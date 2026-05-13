"""Reusable comtypes helpers for CSI SAP2000 and ETABS worker scripts.

Copy this file next to the worker script that VIKTOR sends to the worker.
It is intentionally independent from VIKTOR imports so it can be run locally
on a Windows worker machine for debugging.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import comtypes
import comtypes.client


@dataclass(frozen=True)
class CsiProductConfig:
    helper_progid: str
    api_progid: str
    default_exe_name: str


CSI_PRODUCTS: Dict[str, CsiProductConfig] = {
    "sap2000": CsiProductConfig(
        helper_progid="SAP2000v1.Helper",
        api_progid="CSI.SAP2000.API.SapObject",
        default_exe_name="SAP2000.exe",
    ),
    "etabs": CsiProductConfig(
        helper_progid="ETABSv1.Helper",
        api_progid="CSI.ETABS.API.ETABSObject",
        default_exe_name="ETABS.exe",
    ),
}


class CsiComSession:
    """Context manager for launching or attaching to SAP2000/ETABS with comtypes."""

    def __init__(
        self,
        product: str,
        *,
        attach_to_active: bool = False,
        program_path: Optional[Union[str, Path]] = None,
        start_application: bool = True,
        close_on_exit: Optional[bool] = None,
    ) -> None:
        key = product.lower()
        if key not in CSI_PRODUCTS:
            raise ValueError(f"Unsupported CSI product: {product!r}")

        self.product = key
        self.config = CSI_PRODUCTS[key]
        self.attach_to_active = attach_to_active
        self.program_path = Path(program_path) if program_path else None
        self.start_application = start_application
        self.close_on_exit = (not attach_to_active) if close_on_exit is None else close_on_exit
        self.helper = None
        self.application = None
        self.model = None

    def __enter__(self) -> "CsiComSession":
        comtypes.CoInitialize()
        try:
            self.helper = comtypes.client.CreateObject(self.config.helper_progid)
            self.application = self._get_or_create_application()
            if self.start_application and not self.attach_to_active:
                ret = self.application.ApplicationStart()
                if ret not in (None, 0):
                    raise RuntimeError(f"{self.product} ApplicationStart failed (ret={ret})")

            self.model = self.application.SapModel
            if self.model is None:
                raise RuntimeError(f"{self.product} application returned SapModel=None")
            return self
        except Exception:
            self._release()
            comtypes.CoUninitialize()
            raise

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if self.close_on_exit and self.application is not None:
                try:
                    self.application.ApplicationExit(False)
                except Exception:
                    pass
        finally:
            self._release()
            comtypes.CoUninitialize()

    def _get_or_create_application(self):
        if self.attach_to_active:
            app = self.helper.GetObject(self.config.api_progid)
            if app is None:
                raise RuntimeError(
                    f"Could not attach to active {self.product}. "
                    "Open the CSI application, open a model, set it as active instance for API, "
                    "and run Python with the same privilege level."
                )
            return app

        if self.program_path:
            if not self.program_path.exists():
                raise RuntimeError(f"CSI executable does not exist: {self.program_path}")
            return self.helper.CreateObject(str(self.program_path))

        return self.helper.CreateObjectProgID(self.config.api_progid)

    def _release(self) -> None:
        self.model = None
        self.application = None
        self.helper = None


def require_ret_zero(ret: Any, method_name: str) -> None:
    if ret not in (None, 0):
        raise RuntimeError(f"{method_name} failed (ret={ret})")


def _is_sequence(value: Any) -> bool:
    return isinstance(value, (list, tuple))


def _to_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    try:
        return list(value)
    except TypeError:
        return [value]


def _split_result_fields(result: Any, method_name: str, field_count: int) -> Tuple[Any, ...]:
    """Return output fields from a CSI result tuple and validate the return code.

    Accepts common comtypes wrapper shapes:
    - (ret, field1, field2, ...)
    - (field1, field2, ..., ret)
    - (extra, field1, field2, ..., ret)
    """
    if not isinstance(result, tuple):
        raise RuntimeError(f"{method_name} returned non-tuple: {type(result)} {result!r}")

    candidates: List[Tuple[int, Tuple[Any, ...]]] = []

    if len(result) == field_count + 1:
        if isinstance(result[0], int):
            candidates.append((int(result[0]), tuple(result[1:])))
        if isinstance(result[-1], int):
            candidates.append((int(result[-1]), tuple(result[:-1])))

    if len(result) == field_count + 2:
        if isinstance(result[-1], int):
            candidates.append((int(result[-1]), tuple(result[1:-1])))
        if isinstance(result[0], int):
            candidates.append((int(result[0]), tuple(result[1 : 1 + field_count])))

    if not candidates:
        raise RuntimeError(
            f"Could not parse {method_name} return. "
            f"Expected {field_count + 1} or {field_count + 2} values, got {len(result)}: {result!r}"
        )

    for ret, fields in candidates:
        if ret == 0:
            if len(fields) != field_count:
                raise RuntimeError(
                    f"Could not parse {method_name} return. Expected {field_count} fields, "
                    f"got {len(fields)}: {result!r}"
                )
            return fields

    ret, fields = candidates[0]
    require_ret_zero(ret, method_name)
    return fields


def parse_name_list_result(result: Any, method_name: str) -> Tuple[List[str], int]:
    """Parse common CSI GetNameList return shapes."""
    if not isinstance(result, tuple):
        raise RuntimeError(f"{method_name} returned non-tuple: {type(result)} {result!r}")

    ints = [value for value in result if isinstance(value, int)]
    sequences = [value for value in result if _is_sequence(value)]
    if not ints or not sequences:
        raise RuntimeError(f"Could not parse {method_name} return: {result!r}")

    ret = 0 if 0 in ints else int(ints[-1])
    names = max(sequences, key=len)
    return [str(name) for name in names], ret


def get_name_list(api_object: Any, method_name: str) -> List[str]:
    """Call a CSI GetNameList-like method and return names."""
    method = getattr(api_object, method_name)
    try:
        result = method(0, [])
    except Exception:
        result = method()

    names, ret = parse_name_list_result(result, f"{api_object}.{method_name}")
    require_ret_zero(ret, method_name)
    return names


def get_point_names(model: Any) -> List[str]:
    return get_name_list(model.PointObj, "GetNameList")


def get_frame_names(model: Any) -> List[str]:
    return get_name_list(model.FrameObj, "GetNameList")


def get_load_combo_names(model: Any) -> List[str]:
    return get_name_list(model.RespCombo, "GetNameList")


def get_load_case_names(model: Any) -> List[str]:
    return get_name_list(model.LoadCases, "GetNameList")


def get_load_pattern_names(model: Any) -> List[str]:
    return get_name_list(model.LoadPatterns, "GetNameList")


def parse_restraint_result(result: Any, point_name: str) -> List[int]:
    if not isinstance(result, tuple):
        raise RuntimeError(f"PointObj.GetRestraint returned non-tuple for {point_name}: {result!r}")

    restraint = None
    ret = None
    for value in result:
        if isinstance(value, int):
            ret = value
        elif _is_sequence(value) and len(value) == 6:
            restraint = value

    if restraint is None or ret is None:
        raise RuntimeError(f"Could not parse PointObj.GetRestraint({point_name}) return: {result!r}")
    require_ret_zero(ret, f"PointObj.GetRestraint({point_name})")
    return [int(value) for value in restraint]


def get_point_restraint(model: Any, point_name: str) -> List[int]:
    try:
        result = model.PointObj.GetRestraint(str(point_name), [0, 0, 0, 0, 0, 0])
    except Exception:
        result = model.PointObj.GetRestraint(str(point_name))
    return parse_restraint_result(result, str(point_name))


def get_point_coords(model: Any, point_name: str) -> Tuple[float, float, float]:
    result = model.PointObj.GetCoordCartesian(str(point_name), 0, 0, 0)
    if not isinstance(result, tuple) or len(result) < 4:
        raise RuntimeError(f"PointObj.GetCoordCartesian({point_name}) returned unexpected value: {result!r}")

    *coords, ret = result
    require_ret_zero(ret, f"PointObj.GetCoordCartesian({point_name})")
    if len(coords) != 3:
        raise RuntimeError(f"PointObj.GetCoordCartesian({point_name}) returned unexpected coords: {result!r}")
    return float(coords[0]), float(coords[1]), float(coords[2])


def get_frame_points(model: Any, frame_name: str) -> Tuple[str, str]:
    result = model.FrameObj.GetPoints(str(frame_name), "", "")
    if not isinstance(result, tuple) or len(result) < 3:
        raise RuntimeError(f"FrameObj.GetPoints({frame_name}) returned unexpected value: {result!r}")

    if isinstance(result[0], int):
        ret, point_i, point_j = result[0], result[1], result[2]
    else:
        point_i, point_j, ret = result[-3], result[-2], result[-1]

    require_ret_zero(ret, f"FrameObj.GetPoints({frame_name})")
    return str(point_i), str(point_j)


def get_frame_connectivity(model: Any, frame_names: Iterable[str]) -> List[Dict[str, str]]:
    frames: List[Dict[str, str]] = []
    for frame_name in frame_names:
        point_i, point_j = get_frame_points(model, str(frame_name))
        frames.append({"frame": str(frame_name), "point_i": point_i, "point_j": point_j})
    return frames


def get_support_nodes(model: Any) -> List[Dict[str, Any]]:
    supports: List[Dict[str, Any]] = []
    for point_name in get_point_names(model):
        restraint = get_point_restraint(model, point_name)
        if any(restraint):
            x, y, z = get_point_coords(model, point_name)
            supports.append(
                {
                    "joint": str(point_name),
                    "x": x,
                    "y": y,
                    "z": z,
                    "restraint": {
                        "u1": restraint[0],
                        "u2": restraint[1],
                        "u3": restraint[2],
                        "r1": restraint[3],
                        "r2": restraint[4],
                        "r3": restraint[5],
                    },
                }
            )
    return supports


def run_analysis(model: Any) -> None:
    ret = model.Analyze.RunAnalysis()
    require_ret_zero(ret, "Analyze.RunAnalysis")


def initialize_new_blank_model(model: Any) -> None:
    ret = model.InitializeNewModel()
    require_ret_zero(ret, "InitializeNewModel")
    ret = model.File.NewBlank()
    require_ret_zero(ret, "File.NewBlank")


def open_model_file(model: Any, model_path: Union[str, Path]) -> None:
    path = Path(model_path)
    if not path.exists():
        raise RuntimeError(f"SAP2000 model file does not exist: {path}")
    ret = model.File.OpenFile(str(path))
    require_ret_zero(ret, f"File.OpenFile({path})")


def save_model_file(model: Any, model_path: Union[str, Path]) -> None:
    path = Path(model_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ret = model.File.Save(str(path))
    require_ret_zero(ret, f"File.Save({path})")


def select_results_output(model: Any, name: str) -> str:
    ret = model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    require_ret_zero(ret, "Results.Setup.DeselectAllCasesAndCombosForOutput")

    ret_case = model.Results.Setup.SetCaseSelectedForOutput(str(name))
    if ret_case == 0:
        return "case"

    ret_combo = model.Results.Setup.SetComboSelectedForOutput(str(name))
    if ret_combo == 0:
        return "combo"

    raise RuntimeError(
        f"Could not select {name!r} as case (ret={ret_case}) or combo (ret={ret_combo})."
    )


def call_joint_react(model: Any, joint_name: str) -> Any:
    """Call Results.JointReact with a comtypes-friendly explicit OUT-arg shape."""
    try:
        return model.Results.JointReact(
            str(joint_name),
            0,
            0,
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
    except TypeError:
        return model.Results.JointReact(str(joint_name), 0)


def parse_joint_react_first_row(result: Any, joint_name: str) -> Dict[str, Any]:
    if not isinstance(result, tuple):
        raise RuntimeError(f"Results.JointReact({joint_name}) returned non-tuple: {result!r}")

    if len(result) == 13:
        if isinstance(result[0], int):
            ret, number_results, obj, elm, load_case, step_type, step_num, f1, f2, f3, m1, m2, m3 = result
        else:
            number_results, obj, elm, load_case, step_type, step_num, f1, f2, f3, m1, m2, m3, ret = result
    elif len(result) == 14:
        number_results, obj, elm, load_case, step_type, step_num, f1, f2, f3, m1, m2, m3, ret = result[1:]
    else:
        raise RuntimeError(f"Results.JointReact({joint_name}) returned unexpected length: {result!r}")

    require_ret_zero(ret, f"Results.JointReact({joint_name})")
    if int(number_results or 0) <= 0 or not load_case:
        return {
            "result_name": "",
            "step_type": "",
            "step_num": 0.0,
            "f1": 0.0,
            "f2": 0.0,
            "f3": 0.0,
            "m1": 0.0,
            "m2": 0.0,
            "m3": 0.0,
        }

    index = 0
    return {
        "result_name": str(load_case[index]),
        "step_type": str(step_type[index]),
        "step_num": float(step_num[index]),
        "f1": float(f1[index]),
        "f2": float(f2[index]),
        "f3": float(f3[index]),
        "m1": float(m1[index]),
        "m2": float(m2[index]),
        "m3": float(m3[index]),
    }


def get_support_reactions(
    model: Any,
    supports: Sequence[Dict[str, Any]],
    result_names: Iterable[str],
) -> Dict[str, Dict[str, Any]]:
    reactions: Dict[str, Dict[str, Any]] = {support["joint"]: {} for support in supports}

    for result_name in result_names:
        result_type = select_results_output(model, str(result_name))
        for support in supports:
            joint_name = support["joint"]
            reaction = parse_joint_react_first_row(call_joint_react(model, joint_name), joint_name)
            reactions[joint_name][str(result_name)] = {
                "type": result_type,
                "step_type": reaction["step_type"],
                "step_num": reaction["step_num"],
                "f1": reaction["f1"],
                "f2": reaction["f2"],
                "f3": reaction["f3"],
                "m1": reaction["m1"],
                "m2": reaction["m2"],
                "m3": reaction["m3"],
            }

    return reactions


def call_frame_force(model: Any, frame_name: str, item_type: int = 0) -> Any:
    try:
        return model.Results.FrameForce(
            str(frame_name),
            int(item_type),
            0,
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
    except TypeError:
        return model.Results.FrameForce(str(frame_name), int(item_type))


def parse_frame_force_rows(result: Any, frame_name: str) -> List[Dict[str, Any]]:
    fields = _split_result_fields(result, f"Results.FrameForce({frame_name})", 14)

    (
        number_results,
        obj,
        obj_sta,
        elm,
        elm_sta,
        load_case,
        step_type,
        step_num,
        p,
        v2,
        v3,
        torsion,
        m2,
        m3,
    ) = fields

    lists = {
        "object": _to_list(obj),
        "object_station": _to_list(obj_sta),
        "element": _to_list(elm),
        "element_station": _to_list(elm_sta),
        "load_case": _to_list(load_case),
        "step_type": _to_list(step_type),
        "step_num": _to_list(step_num),
        "p": _to_list(p),
        "v2": _to_list(v2),
        "v3": _to_list(v3),
        "t": _to_list(torsion),
        "m2": _to_list(m2),
        "m3": _to_list(m3),
    }

    row_count = min(int(number_results or 0), *(len(values) for values in lists.values()))

    rows: List[Dict[str, Any]] = []
    for index in range(row_count):
        rows.append(
            {
                "frame": str(frame_name),
                "object": str(lists["object"][index]),
                "object_station": float(lists["object_station"][index]),
                "element": str(lists["element"][index]),
                "element_station": float(lists["element_station"][index]),
                "load_case": str(lists["load_case"][index]),
                "step_type": str(lists["step_type"][index]),
                "step_num": float(lists["step_num"][index]),
                "p": float(lists["p"][index]),
                "v2": float(lists["v2"][index]),
                "v3": float(lists["v3"][index]),
                "t": float(lists["t"][index]),
                "m2": float(lists["m2"][index]),
                "m3": float(lists["m3"][index]),
            }
        )

    return rows


def get_frame_forces(
    model: Any,
    frame_names: Iterable[str],
    result_names: Iterable[str],
    item_type: int = 0,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for result_name in result_names:
        result_type = select_results_output(model, str(result_name))

        for frame_name in frame_names:
            frame_rows = parse_frame_force_rows(
                call_frame_force(model, str(frame_name), item_type=item_type),
                str(frame_name),
            )

            for row in frame_rows:
                row["requested_result"] = str(result_name)
                row["result_type"] = result_type
                rows.append(row)

    return rows


def call_joint_displ(model: Any, point_name: str, item_type: int = 0, absolute: bool = False) -> Any:
    method = model.Results.JointDisplAbs if absolute else model.Results.JointDispl

    try:
        return method(
            str(point_name),
            int(item_type),
            0,
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
    except TypeError:
        return method(str(point_name), int(item_type))


def parse_joint_displ_rows(result: Any, point_name: str, absolute: bool = False) -> List[Dict[str, Any]]:
    method_name = "JointDisplAbs" if absolute else "JointDispl"
    fields = _split_result_fields(result, f"Results.{method_name}({point_name})", 12)

    (
        number_results,
        obj,
        elm,
        load_case,
        step_type,
        step_num,
        u1,
        u2,
        u3,
        r1,
        r2,
        r3,
    ) = fields

    lists = {
        "object": _to_list(obj),
        "element": _to_list(elm),
        "load_case": _to_list(load_case),
        "step_type": _to_list(step_type),
        "step_num": _to_list(step_num),
        "u1": _to_list(u1),
        "u2": _to_list(u2),
        "u3": _to_list(u3),
        "r1": _to_list(r1),
        "r2": _to_list(r2),
        "r3": _to_list(r3),
    }

    row_count = min(int(number_results or 0), *(len(values) for values in lists.values()))

    rows: List[Dict[str, Any]] = []
    for index in range(row_count):
        rows.append(
            {
                "joint": str(point_name),
                "object": str(lists["object"][index]),
                "element": str(lists["element"][index]),
                "load_case": str(lists["load_case"][index]),
                "step_type": str(lists["step_type"][index]),
                "step_num": float(lists["step_num"][index]),
                "absolute": bool(absolute),
                "u1": float(lists["u1"][index]),
                "u2": float(lists["u2"][index]),
                "u3": float(lists["u3"][index]),
                "r1": float(lists["r1"][index]),
                "r2": float(lists["r2"][index]),
                "r3": float(lists["r3"][index]),
            }
        )

    return rows


def get_joint_displacements(
    model: Any,
    point_names: Iterable[str],
    result_names: Iterable[str],
    item_type: int = 0,
    absolute: bool = False,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for result_name in result_names:
        result_type = select_results_output(model, str(result_name))

        for point_name in point_names:
            point_rows = parse_joint_displ_rows(
                call_joint_displ(model, str(point_name), item_type=item_type, absolute=absolute),
                str(point_name),
                absolute=absolute,
            )

            for row in point_rows:
                row["requested_result"] = str(result_name)
                row["result_type"] = result_type
                rows.append(row)

    return rows


def call_base_react(model: Any) -> Any:
    try:
        return model.Results.BaseReact(
            0,
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            0.0,
            0.0,
            0.0,
        )
    except TypeError:
        return model.Results.BaseReact()


def parse_base_react_rows(result: Any) -> List[Dict[str, Any]]:
    fields = _split_result_fields(result, "Results.BaseReact", 13)

    (
        number_results,
        load_case,
        step_type,
        step_num,
        fx,
        fy,
        fz,
        mx,
        my,
        mz,
        gx,
        gy,
        gz,
    ) = fields

    lists = {
        "load_case": _to_list(load_case),
        "step_type": _to_list(step_type),
        "step_num": _to_list(step_num),
        "fx": _to_list(fx),
        "fy": _to_list(fy),
        "fz": _to_list(fz),
        "mx": _to_list(mx),
        "my": _to_list(my),
        "mz": _to_list(mz),
    }

    row_count = min(int(number_results or 0), *(len(values) for values in lists.values()))

    rows: List[Dict[str, Any]] = []
    for index in range(row_count):
        rows.append(
            {
                "load_case": str(lists["load_case"][index]),
                "step_type": str(lists["step_type"][index]),
                "step_num": float(lists["step_num"][index]),
                "fx": float(lists["fx"][index]),
                "fy": float(lists["fy"][index]),
                "fz": float(lists["fz"][index]),
                "mx": float(lists["mx"][index]),
                "my": float(lists["my"][index]),
                "mz": float(lists["mz"][index]),
                "gx": float(gx),
                "gy": float(gy),
                "gz": float(gz),
            }
        )

    return rows


def get_base_reactions(model: Any, result_names: Iterable[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for result_name in result_names:
        result_type = select_results_output(model, str(result_name))
        result_rows = parse_base_react_rows(call_base_react(model))

        for row in result_rows:
            row["requested_result"] = str(result_name)
            row["result_type"] = result_type
            rows.append(row)

    return rows


def call_modal_period(model: Any) -> Any:
    try:
        return model.Results.ModalPeriod(
            0,
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
    except TypeError:
        return model.Results.ModalPeriod()


def parse_modal_period_rows(result: Any) -> List[Dict[str, Any]]:
    fields = _split_result_fields(result, "Results.ModalPeriod", 8)

    (
        number_results,
        load_case,
        step_type,
        step_num,
        period,
        frequency,
        circular_frequency,
        eigenvalue,
    ) = fields

    lists = {
        "load_case": _to_list(load_case),
        "step_type": _to_list(step_type),
        "step_num": _to_list(step_num),
        "period": _to_list(period),
        "frequency": _to_list(frequency),
        "circular_frequency": _to_list(circular_frequency),
        "eigenvalue": _to_list(eigenvalue),
    }

    row_count = min(int(number_results or 0), *(len(values) for values in lists.values()))

    rows: List[Dict[str, Any]] = []
    for index in range(row_count):
        rows.append(
            {
                "load_case": str(lists["load_case"][index]),
                "step_type": str(lists["step_type"][index]),
                "step_num": float(lists["step_num"][index]),
                "period": float(lists["period"][index]),
                "frequency": float(lists["frequency"][index]),
                "circular_frequency": float(lists["circular_frequency"][index]),
                "eigenvalue": float(lists["eigenvalue"][index]),
            }
        )

    return rows


def get_modal_periods(model: Any, modal_result_names: Iterable[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for result_name in modal_result_names:
        result_type = select_results_output(model, str(result_name))
        result_rows = parse_modal_period_rows(call_modal_period(model))

        for row in result_rows:
            row["requested_result"] = str(result_name)
            row["result_type"] = result_type
            rows.append(row)

    return rows


def get_model_lists(model: Any) -> Dict[str, Any]:
    frame_names = get_frame_names(model)
    return {
        "points": get_point_names(model),
        "frames": frame_names,
        "frame_connectivity": get_frame_connectivity(model, frame_names),
        "load_cases": get_load_case_names(model),
        "load_combinations": get_load_combo_names(model),
    }
