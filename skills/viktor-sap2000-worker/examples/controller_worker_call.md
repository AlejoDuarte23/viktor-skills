# Example: VIKTOR Controller Worker Call

This example shows only app-side orchestration. The controller builds `inputs.json`, sends worker files, runs `SAP2000Analysis`, and validates `output.json`. It does not import `comtypes`.

```python
import json
from io import BytesIO
from pathlib import Path

import viktor as vkt
from viktor.errors import ExecutionError, LicenseError


def build_worker_payload(params):
    return {
        "attach_to_active": bool(params.attach_to_active),
        "program_path": params.sap2000_path or "",
        "model_path": params.model_path or "",
        "save_model_path": "",
        "run_analysis": bool(params.run_analysis),
        "result_names": [name.strip() for name in params.result_names.split(",") if name.strip()],
        "modal_result_names": [name.strip() for name in params.modal_result_names.split(",") if name.strip()],
        "extract": {
            "model_lists": bool(params.extract_model_lists),
            "support_nodes": bool(params.extract_support_nodes),
            "joint_reactions": bool(params.extract_joint_reactions),
            "joint_displacements": bool(params.extract_joint_displacements),
            "frame_forces": bool(params.extract_frame_forces),
            "base_reactions": bool(params.extract_base_reactions),
            "modal_periods": bool(params.extract_modal_periods),
        },
        "units": {
            "length": "m",
            "force": "kN",
            "moment": "kN m",
        },
    }


def parse_worker_output(result_file):
    if result_file is None:
        raise vkt.UserError("SAP2000 did not return output.json.")

    try:
        output = json.loads(result_file.getvalue_binary().decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise vkt.UserError("SAP2000 returned malformed JSON output.") from exc

    if output.get("status") != "ok":
        message = output.get("message") or "SAP2000 worker failed."
        raise vkt.UserError(message)

    if "units" not in output:
        raise vkt.UserError("SAP2000 output is missing units.")

    if "warnings" not in output:
        output["warnings"] = []

    return output


class Parametrization(vkt.Parametrization):
    intro = vkt.Text("# SAP2000 Main Results")
    attach_to_active = vkt.BooleanField("Attach to active SAP2000 instance", default=True)
    sap2000_path = vkt.TextField(
        "SAP2000 executable path",
        default=r"C:\Program Files\Computers and Structures\SAP2000 26\SAP2000.exe",
    )
    model_path = vkt.TextField("Optional model path on worker", default="")
    run_analysis = vkt.BooleanField("Run analysis before extracting results", default=True)
    result_names = vkt.TextField("Cases or combinations", default="DEAD, ULS1")
    modal_result_names = vkt.TextField("Modal cases", default="MODAL")
    extract_model_lists = vkt.BooleanField("Get model lists", default=True)
    extract_support_nodes = vkt.BooleanField("Get supports", default=True)
    extract_joint_reactions = vkt.BooleanField("Get joint reactions", default=True)
    extract_joint_displacements = vkt.BooleanField("Get joint displacements", default=False)
    extract_frame_forces = vkt.BooleanField("Get frame forces", default=True)
    extract_base_reactions = vkt.BooleanField("Get base reactions", default=False)
    extract_modal_periods = vkt.BooleanField("Get modal periods", default=False)


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Frame Forces", duration_guess=30, update_label="Run SAP2000")
    def run_sap2000(self, params, **kwargs):
        payload = build_worker_payload(params)
        base_path = Path(__file__).parent
        script_path = base_path / "run_sap2000_model.py"
        helper_path = base_path / "csi_comtypes_helpers.py"
        types_path = base_path / "csi_output_types.py"

        analysis = vkt.sap2000.SAP2000Analysis(
            script=vkt.File.from_path(script_path),
            files=[
                ("inputs.json", BytesIO(json.dumps(payload).encode("utf-8"))),
                ("csi_comtypes_helpers.py", vkt.File.from_path(helper_path)),
                ("csi_output_types.py", vkt.File.from_path(types_path)),
            ],
            output_filenames=["output.json"],
        )

        try:
            analysis.execute(timeout=900)
        except LicenseError as exc:
            raise vkt.UserError("No SAP2000 worker license is available. Check the worker connection.") from exc
        except ExecutionError as exc:
            raise vkt.UserError(f"SAP2000 worker execution failed: {exc}") from exc

        output = parse_worker_output(analysis.get_output_file("output.json"))
        frame_forces = output.get("frame_forces", [])

        rows = []
        for force in frame_forces:
            rows.append([
                force.get("frame", ""),
                force.get("requested_result", ""),
                round(float(force.get("object_station", 0.0)), 3),
                round(float(force.get("p", 0.0)), 3),
                round(float(force.get("v2", 0.0)), 3),
                round(float(force.get("v3", 0.0)), 3),
                round(float(force.get("t", 0.0)), 3),
                round(float(force.get("m2", 0.0)), 3),
                round(float(force.get("m3", 0.0)), 3),
            ])

        return vkt.TableResult(
            rows,
            column_headers=[
                "Frame",
                "Case/Combo",
                "Station",
                "P [kN]",
                "V2 [kN]",
                "V3 [kN]",
                "T [kN m]",
                "M2 [kN m]",
                "M3 [kN m]",
            ],
        )
```
