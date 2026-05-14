"""Typed output contracts for SAP2000 worker JSON files.

Use Annotated[...] for output fields. Do not assign defaults in these schema
classes. Defaults belong in builder functions such as make_ok_output and
make_error_output.
"""

from __future__ import annotations

from typing import Annotated, Literal, NotRequired, TypedDict


class UnitsOut(TypedDict):
    length: Annotated[str, "Length unit label, for example m"]
    force: Annotated[str, "Force unit label, for example kN"]
    moment: Annotated[str, "Moment unit label, for example kN m"]


class RestraintOut(TypedDict):
    u1: Annotated[int, "Translation restraint in local/global 1 direction"]
    u2: Annotated[int, "Translation restraint in local/global 2 direction"]
    u3: Annotated[int, "Translation restraint in local/global 3 direction"]
    r1: Annotated[int, "Rotation restraint about 1 direction"]
    r2: Annotated[int, "Rotation restraint about 2 direction"]
    r3: Annotated[int, "Rotation restraint about 3 direction"]


class SupportNodeOut(TypedDict):
    joint: Annotated[str, "SAP2000 point object name"]
    x: Annotated[float, "X coordinate"]
    y: Annotated[float, "Y coordinate"]
    z: Annotated[float, "Z coordinate"]
    restraint: Annotated[RestraintOut, "Point restraint flags"]


class JointReactionOut(TypedDict):
    joint: Annotated[str, "SAP2000 point object name requested"]
    object: Annotated[str, "CSI object name returned by result call"]
    element: Annotated[str, "CSI element name returned by result call"]
    requested_result: Annotated[str, "Requested case or combination name"]
    result_type: Annotated[Literal["case", "combo"], "Selected output type"]
    load_case: Annotated[str, "Result load case returned by CSI"]
    step_type: Annotated[str, "CSI step type"]
    step_num: Annotated[float, "CSI step number"]
    f1: Annotated[float, "Reaction force in 1 direction"]
    f2: Annotated[float, "Reaction force in 2 direction"]
    f3: Annotated[float, "Reaction force in 3 direction"]
    m1: Annotated[float, "Reaction moment about 1 direction"]
    m2: Annotated[float, "Reaction moment about 2 direction"]
    m3: Annotated[float, "Reaction moment about 3 direction"]


class FrameConnectivityOut(TypedDict):
    frame: Annotated[str, "SAP2000 frame object name"]
    point_i: Annotated[str, "Frame start point object name"]
    point_j: Annotated[str, "Frame end point object name"]


class FrameForceOut(TypedDict):
    frame: Annotated[str, "SAP2000 frame object name requested"]
    object: Annotated[str, "CSI object name returned by result call"]
    object_station: Annotated[float, "Station along object"]
    element: Annotated[str, "CSI element name returned by result call"]
    element_station: Annotated[float, "Station along analysis element"]
    requested_result: Annotated[str, "Requested case or combination name"]
    result_type: Annotated[Literal["case", "combo"], "Selected output type"]
    load_case: Annotated[str, "Result load case returned by CSI"]
    step_type: Annotated[str, "CSI step type"]
    step_num: Annotated[float, "CSI step number"]
    p: Annotated[float, "Axial force"]
    v2: Annotated[float, "Shear force in local 2 direction"]
    v3: Annotated[float, "Shear force in local 3 direction"]
    t: Annotated[float, "Torsion"]
    m2: Annotated[float, "Moment about local 2 axis"]
    m3: Annotated[float, "Moment about local 3 axis"]


class JointDisplacementOut(TypedDict):
    joint: Annotated[str, "SAP2000 point object name requested"]
    object: Annotated[str, "CSI object name returned by result call"]
    element: Annotated[str, "CSI element name returned by result call"]
    requested_result: Annotated[str, "Requested case or combination name"]
    result_type: Annotated[Literal["case", "combo"], "Selected output type"]
    load_case: Annotated[str, "Result load case returned by CSI"]
    step_type: Annotated[str, "CSI step type"]
    step_num: Annotated[float, "CSI step number"]
    absolute: Annotated[bool, "True when result came from JointDisplAbs"]
    u1: Annotated[float, "Translation in 1 direction"]
    u2: Annotated[float, "Translation in 2 direction"]
    u3: Annotated[float, "Translation in 3 direction"]
    r1: Annotated[float, "Rotation about 1 direction"]
    r2: Annotated[float, "Rotation about 2 direction"]
    r3: Annotated[float, "Rotation about 3 direction"]


class BaseReactionOut(TypedDict):
    requested_result: Annotated[str, "Requested case or combination name"]
    result_type: Annotated[Literal["case", "combo"], "Selected output type"]
    load_case: Annotated[str, "Result load case returned by CSI"]
    step_type: Annotated[str, "CSI step type"]
    step_num: Annotated[float, "CSI step number"]
    fx: Annotated[float, "Global base reaction force X"]
    fy: Annotated[float, "Global base reaction force Y"]
    fz: Annotated[float, "Global base reaction force Z"]
    mx: Annotated[float, "Global base reaction moment X"]
    my: Annotated[float, "Global base reaction moment Y"]
    mz: Annotated[float, "Global base reaction moment Z"]
    gx: Annotated[float, "Base reaction point X coordinate"]
    gy: Annotated[float, "Base reaction point Y coordinate"]
    gz: Annotated[float, "Base reaction point Z coordinate"]


class ModalPeriodOut(TypedDict):
    requested_result: Annotated[str, "Requested modal case name"]
    result_type: Annotated[Literal["case", "combo"], "Selected output type"]
    load_case: Annotated[str, "Result load case returned by CSI"]
    step_type: Annotated[str, "CSI step type"]
    step_num: Annotated[float, "Mode number or step number"]
    period: Annotated[float, "Modal period"]
    frequency: Annotated[float, "Modal frequency"]
    circular_frequency: Annotated[float, "Circular frequency"]
    eigenvalue: Annotated[float, "Eigenvalue"]


class DatabaseTableOut(TypedDict):
    table_key: Annotated[str, "CSI database table key"]
    group_name: Annotated[str, "Optional CSI group name used to filter rows"]
    columns: Annotated[list[str], "Column names returned by DatabaseTables.GetTableForDisplayArray"]
    rows: Annotated[list[list[object]], "Raw table rows"]
    records: Annotated[list[dict[str, object]], "Rows converted to dictionaries keyed by column name"]


class ModelListsOut(TypedDict):
    points: Annotated[list[str], "Point object names"]
    frames: Annotated[list[str], "Frame object names"]
    frame_connectivity: Annotated[list[FrameConnectivityOut], "Frame start and end point names"]
    load_cases: Annotated[list[str], "Load case names"]
    load_combinations: Annotated[list[str], "Load combination names"]


class WorkerOkOutput(TypedDict):
    status: Annotated[Literal["ok"], "Successful worker result"]
    units: Annotated[UnitsOut, "Output unit labels"]
    warnings: Annotated[list[str], "Non-fatal worker warnings"]
    model_lists: NotRequired[Annotated[ModelListsOut, "Optional model object and result-name lists"]]
    support_nodes: NotRequired[Annotated[list[SupportNodeOut], "Restrained support points"]]
    joint_reactions: NotRequired[
        Annotated[
            dict[str, dict[str, list[JointReactionOut]]],
            "Joint reactions keyed by joint name and requested result name; each leaf preserves all CSI result rows",
        ]
    ]
    joint_displacements: NotRequired[Annotated[list[JointDisplacementOut], "Joint displacement rows"]]
    frame_forces: NotRequired[Annotated[list[FrameForceOut], "Frame internal force rows"]]
    base_reactions: NotRequired[Annotated[list[BaseReactionOut], "Base reaction rows"]]
    modal_periods: NotRequired[Annotated[list[ModalPeriodOut], "Modal period rows"]]
    database_tables: NotRequired[
        Annotated[
            list[DatabaseTableOut],
            "Optional CSI database display tables exported through SapModel.DatabaseTables",
        ]
    ]


class WorkerErrorOutput(TypedDict):
    status: Annotated[Literal["error"], "Failed worker result"]
    message: Annotated[str, "User-facing error message"]
    warnings: Annotated[list[str], "Non-fatal warnings collected before failure"]
    traceback: NotRequired[Annotated[str, "Debug traceback from the worker"]]


WorkerOutput = WorkerOkOutput | WorkerErrorOutput


def make_ok_output(units: UnitsOut) -> WorkerOkOutput:
    return {
        "status": "ok",
        "units": units,
        "warnings": [],
    }


def make_error_output(message: str, traceback_text: str | None = None) -> WorkerErrorOutput:
    output: WorkerErrorOutput = {
        "status": "error",
        "message": message,
        "warnings": [],
    }

    if traceback_text:
        output["traceback"] = traceback_text

    return output
