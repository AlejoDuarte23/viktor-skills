from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

from csi_comtypes_helpers import (
    CsiComSession,
    get_base_reactions,
    get_frame_forces,
    get_frame_names,
    get_joint_displacements,
    get_model_lists,
    get_modal_periods,
    get_point_names,
    get_support_nodes,
    get_support_reactions,
    initialize_new_blank_model,
    open_model_file,
    run_analysis,
    save_model_file,
)
from csi_database_tables import get_database_tables
from csi_output_types import UnitsOut, make_error_output, make_ok_output


INPUT_PATH = Path.cwd() / "inputs.json"
OUTPUT_PATH = Path.cwd() / "output.json"


def read_inputs() -> dict[str, Any]:
    with INPUT_PATH.open(encoding="utf-8") as jsonfile:
        payload = json.load(jsonfile)

    payload.setdefault("attach_to_active", True)
    payload.setdefault("program_path", "")
    payload.setdefault("model_path", "")
    payload.setdefault("save_model_path", "")
    payload.setdefault("create_new_model", False)
    payload.setdefault("run_analysis", True)
    payload.setdefault("result_names", [])
    payload.setdefault("modal_result_names", [])
    payload.setdefault("database_tables", [])
    payload.setdefault("extract", {})
    payload.setdefault("units", {"length": "m", "force": "kN", "moment": "kN m"})
    return payload


def write_output(data: dict[str, Any]) -> None:
    with OUTPUT_PATH.open("w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, indent=2)


def main() -> None:
    try:
        payload = read_inputs()
        units: UnitsOut = {
            "length": str(payload["units"].get("length", "m")),
            "force": str(payload["units"].get("force", "kN")),
            "moment": str(payload["units"].get("moment", "kN m")),
        }
        output = make_ok_output(units)

        with CsiComSession(
            product="sap2000",
            attach_to_active=bool(payload["attach_to_active"]),
            program_path=payload.get("program_path") or None,
        ) as csi:
            model = csi.model

            if payload.get("create_new_model", False):
                initialize_new_blank_model(model)

            if payload.get("model_path"):
                open_model_file(model, payload["model_path"])

            if payload.get("run_analysis", True):
                run_analysis(model)

            extract = payload.get("extract", {})
            result_names = [str(name) for name in payload.get("result_names", []) if str(name).strip()]
            modal_result_names = [str(name) for name in payload.get("modal_result_names", []) if str(name).strip()]

            if extract.get("model_lists"):
                output["model_lists"] = get_model_lists(model)

            if extract.get("support_nodes"):
                output["support_nodes"] = get_support_nodes(model)

            if extract.get("joint_reactions"):
                supports = output.get("support_nodes") or get_support_nodes(model)
                output["joint_reactions"] = get_support_reactions(model, supports, result_names)

            if extract.get("joint_displacements"):
                point_names = get_point_names(model)
                output["joint_displacements"] = get_joint_displacements(model, point_names, result_names)

            if extract.get("frame_forces"):
                frame_names = get_frame_names(model)
                output["frame_forces"] = get_frame_forces(model, frame_names, result_names)

            if extract.get("base_reactions"):
                output["base_reactions"] = get_base_reactions(model, result_names)

            if extract.get("modal_periods"):
                output["modal_periods"] = get_modal_periods(model, modal_result_names)

            if extract.get("database_tables"):
                output["database_tables"] = get_database_tables(model, payload.get("database_tables", []))

            if payload.get("save_model_path"):
                save_model_file(model, payload["save_model_path"])

        write_output(output)

    except Exception as exc:
        write_output(make_error_output(str(exc), traceback.format_exc()))


if __name__ == "__main__":
    main()
