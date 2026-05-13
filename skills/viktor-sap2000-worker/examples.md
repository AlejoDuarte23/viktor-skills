# VIKTOR SAP2000 Worker Examples

## App File Layout

```text
my-sap2000-app/
+-- app.py
+-- run_sap2000_model.py
+-- csi_comtypes_helpers.py
+-- requirements.txt
+-- viktor.config.toml
```

Copy [scripts/csi_comtypes_helpers.py](scripts/csi_comtypes_helpers.py) next to `run_sap2000_model.py` when the worker needs reusable SAP2000 and ETABS session helpers.

## Minimal Configuration

```toml
app_type = "simple"
python_version = "3.12"

worker_integrations = [
    "sap2000",
]
```

```text
viktor==14.27.3
```

Install worker-side dependencies into the Python executable selected during worker installation:

```powershell
C:\Path\To\python.exe -m pip install comtypes
```

## Controller With SAP2000 Worker Call

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
        "run_analysis": bool(params.run_analysis),
        "result_names": [name.strip() for name in params.result_names.split(",") if name.strip()],
        "extract": {
            "support_coordinates": True,
            "joint_reactions": True,
        },
        "units": {
            "length": "m",
            "force": "kN",
            "moment": "kN m",
        },
    }


def parse_sap2000_output(result_file):
    if result_file is None:
        raise vkt.UserError("SAP2000 did not return output.json.")

    try:
        output = json.loads(result_file.getvalue_binary().decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise vkt.UserError("SAP2000 returned malformed JSON output.") from exc

    if output.get("status") != "ok":
        message = output.get("message") or "SAP2000 analysis failed."
        raise vkt.UserError(message)

    if "support_coordinates" not in output:
        raise vkt.UserError("SAP2000 output is missing support_coordinates.")
    if "joint_reactions" not in output:
        raise vkt.UserError("SAP2000 output is missing joint_reactions.")

    return output


class Parametrization(vkt.Parametrization):
    intro = vkt.Text("# SAP2000 Support Reactions")
    attach_to_active = vkt.BooleanField("Attach to active SAP2000 instance", default=True)
    sap2000_path = vkt.TextField(
        "SAP2000 executable path",
        default=r"C:\Program Files\Computers and Structures\SAP2000 26\SAP2000.exe",
    )
    run_analysis = vkt.BooleanField("Run analysis before extracting results", default=True)
    result_names = vkt.TextField("Cases or combinations", default="DEAD, ULS1, ULS2")


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Support Reactions", duration_guess=30, update_label="Run SAP2000")
    def run_sap2000(self, params, **kwargs):
        payload = build_worker_payload(params)
        script_path = Path(__file__).parent / "run_sap2000_model.py"
        helper_path = Path(__file__).parent / "csi_comtypes_helpers.py"

        analysis = vkt.sap2000.SAP2000Analysis(
            script=vkt.File.from_path(script_path),
            files=[
                ("inputs.json", BytesIO(json.dumps(payload).encode("utf-8"))),
                ("csi_comtypes_helpers.py", vkt.File.from_path(helper_path)),
            ],
            output_filenames=["output.json"],
        )

        try:
            analysis.execute(timeout=600)
        except LicenseError as exc:
            raise vkt.UserError("No SAP2000 worker license is available. Check the worker connection.") from exc
        except ExecutionError as exc:
            raise vkt.UserError(f"SAP2000 worker execution failed: {exc}") from exc

        output = parse_sap2000_output(analysis.get_output_file("output.json"))
        reactions = output["joint_reactions"]

        rows = []
        for joint_name, result_map in reactions.items():
            for result_name, reaction in result_map.items():
                rows.append([
                    joint_name,
                    result_name,
                    reaction.get("type", ""),
                    round(float(reaction.get("f1", 0.0)), 2),
                    round(float(reaction.get("f2", 0.0)), 2),
                    round(float(reaction.get("f3", 0.0)), 2),
                    round(float(reaction.get("m1", 0.0)), 2),
                    round(float(reaction.get("m2", 0.0)), 2),
                    round(float(reaction.get("m3", 0.0)), 2),
                ])

        return vkt.TableResult(
            rows,
            column_headers=[
                "Joint",
                "Case/Combo",
                "Type",
                "F1 [kN]",
                "F2 [kN]",
                "F3 [kN]",
                "M1 [kN m]",
                "M2 [kN m]",
                "M3 [kN m]",
            ],
        )
```

## Worker Script With Comtypes

Save this as `run_sap2000_model.py`. Run it only on the Windows worker machine where SAP2000 is installed.

```python
import json
import traceback
from pathlib import Path

from csi_comtypes_helpers import (
    CsiComSession,
    get_load_case_names,
    get_load_combo_names,
    get_support_nodes,
    get_support_reactions,
    run_analysis,
)


INPUT_PATH = Path.cwd() / "inputs.json"
OUTPUT_PATH = Path.cwd() / "output.json"


def read_inputs():
    with INPUT_PATH.open(encoding="utf-8") as jsonfile:
        payload = json.load(jsonfile)

    payload.setdefault("attach_to_active", True)
    payload.setdefault("program_path", "")
    payload.setdefault("run_analysis", True)
    payload.setdefault("result_names", [])
    payload.setdefault("extract", {})
    payload.setdefault("units", {"length": "m", "force": "kN", "moment": "kN m"})
    return payload


def choose_result_names(model, payload):
    requested = [str(name) for name in payload.get("result_names", []) if str(name).strip()]
    if requested:
        return requested

    names = []
    names.extend(get_load_combo_names(model))
    names.extend(get_load_case_names(model))
    return names


def write_output(data):
    with OUTPUT_PATH.open("w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, indent=2)


def main():
    try:
        payload = read_inputs()
        with CsiComSession(
            product="sap2000",
            attach_to_active=bool(payload["attach_to_active"]),
            program_path=payload.get("program_path") or None,
        ) as csi:
            model = csi.model

            if payload.get("run_analysis", True):
                run_analysis(model)

            supports = get_support_nodes(model)
            result_names = choose_result_names(model, payload)
            reactions = get_support_reactions(model, supports, result_names)

        write_output({
            "status": "ok",
            "units": payload.get("units", {}),
            "support_coordinates": supports,
            "joint_reactions": reactions,
            "warnings": [],
        })
    except Exception as exc:
        write_output({
            "status": "error",
            "message": str(exc),
            "traceback": traceback.format_exc(),
            "warnings": [],
        })


if __name__ == "__main__":
    main()
```

## Comtypes Launch And Attach Snippets

SAP2000 attach:

```python
import comtypes
import comtypes.client

comtypes.CoInitialize()
try:
    helper = comtypes.client.CreateObject("SAP2000v1.Helper")
    sap_object = helper.GetObject("CSI.SAP2000.API.SapObject")
    model = sap_object.SapModel
finally:
    comtypes.CoUninitialize()
```

SAP2000 launch by path:

```python
helper = comtypes.client.CreateObject("SAP2000v1.Helper")
sap_object = helper.CreateObject(r"C:\Program Files\Computers and Structures\SAP2000 26\SAP2000.exe")
sap_object.ApplicationStart()
model = sap_object.SapModel
```

SAP2000 launch by ProgID:

```python
helper = comtypes.client.CreateObject("SAP2000v1.Helper")
sap_object = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
sap_object.ApplicationStart()
model = sap_object.SapModel
```

ETABS uses the same pattern with different ProgIDs:

```python
helper = comtypes.client.CreateObject("ETABSv1.Helper")
etabs_object = helper.CreateObject(r"C:\Program Files\Computers and Structures\ETABS 22\ETABS.exe")
etabs_object.ApplicationStart()
model = etabs_object.SapModel
```

## Manual Worker Smoke Test

On the worker machine:

1. Copy `run_sap2000_model.py` and `csi_comtypes_helpers.py` into a temporary folder.
2. Create a small `inputs.json`.
3. Run the same Python executable selected during worker installation.
4. Confirm SAP2000 attaches or starts and writes `output.json`.

```powershell
C:\Path\To\python.exe -m pip install comtypes
C:\Path\To\python.exe run_sap2000_model.py
type output.json
```

Example `inputs.json` for active-instance extraction:

```json
{
  "attach_to_active": true,
  "run_analysis": false,
  "result_names": ["DEAD", "ULS1"],
  "extract": {
    "support_coordinates": true,
    "joint_reactions": true
  },
  "units": {
    "length": "m",
    "force": "kN",
    "moment": "kN m"
  }
}
```

Before using attach mode, open SAP2000, open a model, and run `Tools -> Set as active instance for API`.

## Mocked Controller Test

Use `mock_SAP2000Analysis` in tests. Keep actual SAP2000 execution as a manual worker-machine test.

```python
import json
import unittest
from types import SimpleNamespace

import viktor as vkt
from viktor.testing import mock_SAP2000Analysis

from app import Controller


class TestController(unittest.TestCase):

    @mock_SAP2000Analysis(
        get_output_file={
            "output.json": vkt.File.from_data(
                json.dumps({
                    "status": "ok",
                    "units": {"length": "m", "force": "kN", "moment": "kN m"},
                    "support_coordinates": [],
                    "joint_reactions": {
                        "1": {
                            "ULS1": {
                                "type": "combo",
                                "step_type": "",
                                "step_num": 0.0,
                                "f1": 1.0,
                                "f2": 2.0,
                                "f3": -3.0,
                                "m1": 0.0,
                                "m2": 0.0,
                                "m3": 0.0,
                            }
                        }
                    },
                    "warnings": [],
                }).encode("utf-8")
            )
        }
    )
    def test_run_sap2000_returns_table(self):
        params = SimpleNamespace(
            attach_to_active=True,
            sap2000_path="",
            run_analysis=False,
            result_names="ULS1",
        )
        result = Controller().run_sap2000(params)
        self.assertEqual(result.column_headers[0], "Joint")
```

## Tuple Parser Unit Test

Keep COM tuple parsing testable without SAP2000.

```python
import unittest

from csi_comtypes_helpers import parse_name_list_result


class TestComTupleParsing(unittest.TestCase):

    def test_name_list_parser_accepts_common_order(self):
        names, ret = parse_name_list_result((2, ["ULS1", "ULS2"], 0), "RespCombo.GetNameList")
        self.assertEqual(ret, 0)
        self.assertEqual(names, ["ULS1", "ULS2"])

    def test_name_list_parser_accepts_ret_first(self):
        names, ret = parse_name_list_result((0, 2, ["ULS1", "ULS2"]), "RespCombo.GetNameList")
        self.assertEqual(ret, 0)
        self.assertEqual(names, ["ULS1", "ULS2"])
```
