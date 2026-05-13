# VIKTOR ETABS Worker Examples

## App File Layout

```text
my-etabs-app/
+-- app.py
+-- run_etabs_model.py
+-- requirements.txt
+-- viktor.config.toml
```

## Minimal Configuration

```toml
app_type = "simple"
python_version = "3.12"

worker_integrations = [
    "etabs",
]
```

```text
viktor==14.27.3
```

Install worker-side dependencies into the Python executable selected during worker installation:

```powershell
C:\Path\To\python.exe -m pip install comtypes
```

## Controller With Geometry Preview and ETABS Worker Call

```python
import json
from io import BytesIO
from pathlib import Path

import viktor as vkt
from viktor.errors import ExecutionError, LicenseError


def create_frame_data(length_mm: float, height_mm: float):
    nodes = {
        "1": {"x": 0, "y": 0, "z": 0},
        "2": {"x": 0, "y": length_mm, "z": 0},
        "3": {"x": 0, "y": 0, "z": height_mm},
        "4": {"x": 0, "y": length_mm, "z": height_mm},
        "5": {"x": length_mm, "y": 0, "z": 0},
        "6": {"x": length_mm, "y": length_mm, "z": 0},
        "7": {"x": length_mm, "y": 0, "z": height_mm},
        "8": {"x": length_mm, "y": length_mm, "z": height_mm},
    }
    frames = {
        "1": {"node_i": "1", "node_j": "3"},
        "2": {"node_i": "2", "node_j": "4"},
        "3": {"node_i": "3", "node_j": "4"},
        "4": {"node_i": "6", "node_j": "8"},
        "5": {"node_i": "5", "node_j": "7"},
        "6": {"node_i": "3", "node_j": "7"},
        "7": {"node_i": "4", "node_j": "8"},
        "8": {"node_i": "7", "node_j": "8"},
    }
    return nodes, frames


def build_worker_payload(params):
    nodes, frames = create_frame_data(params.frame_length, params.frame_height)
    return {
        "units": {"length": "mm", "force": "N"},
        "nodes": nodes,
        "frames": frames,
        "supports": ["1", "2", "5", "6"],
        "section": {"name": "300x300 RC", "width": 300, "depth": 300},
        "material": {"name": "CONC", "type": "concrete"},
        "load_case": "Dead",
    }


def parse_base_reactions(result_file):
    if result_file is None:
        raise vkt.UserError("ETABS did not return output.json.")

    try:
        result = json.loads(result_file.getvalue())
    except json.JSONDecodeError as exc:
        raise vkt.UserError("ETABS returned malformed JSON output.") from exc

    if result.get("status") != "ok":
        message = result.get("message") or "ETABS analysis failed."
        raise vkt.UserError(message)

    reactions = result.get("base_reactions")
    if not isinstance(reactions, list):
        raise vkt.UserError("ETABS output is missing base_reactions.")

    return reactions


class Parametrization(vkt.Parametrization):
    intro = vkt.Text("# ETABS Base Reaction App")
    frame_length = vkt.NumberField("Frame Length", min=100, default=4000, suffix="mm")
    frame_height = vkt.NumberField("Frame Height", min=100, default=4000, suffix="mm")


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.GeometryView("3D Model", duration_guess=1, x_axis_to_right=True)
    def create_render(self, params, **kwargs):
        nodes, frames = create_frame_data(params.frame_length, params.frame_height)
        geometry = []

        for frame_id, frame in frames.items():
            node_i = nodes[frame["node_i"]]
            node_j = nodes[frame["node_j"]]
            line = vkt.Line(
                vkt.Point(node_i["x"], node_i["y"], node_i["z"]),
                vkt.Point(node_j["x"], node_j["y"], node_j["z"]),
            )
            geometry.append(vkt.RectangularExtrusion(300, 300, line, identifier=frame_id))

        return vkt.GeometryResult(geometry=geometry)

    @vkt.TableView("Base Reactions", duration_guess=10, update_label="Run ETABS analysis")
    def run_etabs(self, params, **kwargs):
        payload = build_worker_payload(params)
        input_file = BytesIO(json.dumps(payload).encode("utf-8"))
        script_path = Path(__file__).parent / "run_etabs_model.py"

        analysis = vkt.etabs.ETABSAnalysis(
            script=vkt.File.from_path(script_path),
            files=[("inputs.json", input_file)],
            output_filenames=["output.json"],
        )

        try:
            analysis.execute(timeout=300)
        except LicenseError as exc:
            raise vkt.UserError("No ETABS worker license is available. Check the worker connection.") from exc
        except ExecutionError as exc:
            raise vkt.UserError(f"ETABS worker execution failed: {exc}") from exc

        reactions = parse_base_reactions(analysis.get_output_file("output.json"))
        rows = [
            [
                reaction["node"],
                reaction["load_case"],
                round(reaction["u1"], 0),
                round(reaction["u2"], 0),
                round(reaction["u3"], 0),
            ]
            for reaction in reactions
        ]

        return vkt.TableResult(
            rows,
            row_headers=[f"Sup {index + 1}" for index in range(len(rows))],
            column_headers=["Node", "Load Case", "U1 [N]", "U2 [N]", "U3 [N]"],
        )
```

## Worker Script With Structured Output

Save this as `run_etabs_model.py`. Run it only on the Windows worker machine where ETABS is installed.

```python
import json
import traceback
from pathlib import Path

import comtypes
import comtypes.client


PROGRAM_PATH = r"C:\Program Files\Computers and Structures\ETABS 22\ETABS.exe"
INPUT_PATH = Path.cwd() / "inputs.json"
OUTPUT_PATH = Path.cwd() / "output.json"


def read_inputs():
    with INPUT_PATH.open(encoding="utf-8") as jsonfile:
        payload = json.load(jsonfile)

    required = ["nodes", "frames", "supports", "load_case"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"inputs.json is missing keys: {', '.join(missing)}")

    payload["nodes"] = {str(key): value for key, value in payload["nodes"].items()}
    payload["frames"] = {str(key): value for key, value in payload["frames"].items()}
    payload["supports"] = [str(node_id) for node_id in payload["supports"]]
    return payload


def start_etabs(program_path):
    helper = comtypes.client.CreateObject("ETABSv1.Helper")
    engine = helper.CreateObject(program_path)
    engine.ApplicationStart()

    model = engine.SapModel
    model.InitializeNewModel(9)  # mm units in the public VIKTOR sample.
    model.File.NewBlank()
    return engine, model


def create_model(model, payload):
    nodes = payload["nodes"]
    frames = payload["frames"]
    section = payload.get("section", {})
    material = payload.get("material", {})

    material_name = material.get("name", "CONC")
    section_name = section.get("name", "300x300 RC")
    width = float(section.get("width", 300))
    depth = float(section.get("depth", 300))

    material_concrete = 2
    model.PropMaterial.SetMaterial(material_name, material_concrete)
    model.PropMaterial.SetMPIsotropic(material_name, 30000, 0.2, 0.0000055)
    model.PropFrame.SetRectangle(section_name, material_name, width, depth)

    for node_id, node in nodes.items():
        model.PointObj.AddCartesian(
            float(node["x"]),
            float(node["y"]),
            float(node["z"]),
            " ",
            str(node_id),
        )

    for frame_id, frame in frames.items():
        model.FrameObj.AddByPoint(
            str(frame["node_i"]),
            str(frame["node_j"]),
            str(frame_id),
            section_name,
            "Global",
        )

    for node_id in payload["supports"]:
        model.PointObj.SetRestraint(str(node_id), [1, 1, 1, 1, 1, 1])

    model.View.RefreshView(0, False)


def run_analysis(model):
    model_path = Path.cwd() / "etabsmodel.edb"
    model.File.Save(str(model_path))
    model.Analyze.RunAnalysis()


def extract_base_reactions(model, payload):
    load_case = payload["load_case"]
    support_nodes = payload["supports"]

    model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    model.Results.Setup.SetCaseSelectedForOutput(load_case)

    reactions = []
    for node_id in support_nodes:
        *_, u1, u2, u3, r1, r2, r3, ret = model.Results.JointReact(str(node_id), 0, 0)
        reactions.append(
            {
                "node": str(node_id),
                "load_case": load_case,
                "u1": float(u1[0]),
                "u2": float(u2[0]),
                "u3": float(u3[0]),
                "r1": float(r1[0]),
                "r2": float(r2[0]),
                "r3": float(r3[0]),
            }
        )

    return reactions


def write_output(data):
    with OUTPUT_PATH.open("w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile)


def main():
    engine = None
    comtypes.CoInitialize()
    try:
        payload = read_inputs()
        engine, model = start_etabs(PROGRAM_PATH)
        create_model(model, payload)
        run_analysis(model)
        reactions = extract_base_reactions(model, payload)
        write_output(
            {
                "status": "ok",
                "units": {"force": "N", "moment": "N mm"},
                "base_reactions": reactions,
                "warnings": [],
            }
        )
    except Exception as exc:
        write_output(
            {
                "status": "error",
                "message": str(exc),
                "traceback": traceback.format_exc(),
                "warnings": [],
            }
        )
    finally:
        if engine is not None:
            try:
                engine.ApplicationExit(False)
            except Exception:
                pass
        comtypes.CoUninitialize()


if __name__ == "__main__":
    main()
```

## Compatibility With the Public Sample Input Shape

The public sample sends `[nodes, lines]` rather than a named object. If you are adapting that sample directly, normalize both shapes at the worker boundary:

```python
def read_inputs():
    with (Path.cwd() / "inputs.json").open(encoding="utf-8") as jsonfile:
        payload = json.load(jsonfile)

    if isinstance(payload, list):
        nodes, frames = payload[:]
        return {
            "nodes": {str(key): value for key, value in nodes.items()},
            "frames": {str(key): value for key, value in frames.items()},
            "supports": ["1", "2", "5", "6"],
            "load_case": "Dead",
            "section": {"name": "300x300 RC", "width": 300, "depth": 300},
            "material": {"name": "CONC"},
        }

    return payload
```

## Output Contract

```json
{
  "status": "ok",
  "units": {
    "force": "N",
    "moment": "N mm"
  },
  "base_reactions": [
    {
      "node": "1",
      "load_case": "Dead",
      "u1": 100.0,
      "u2": 0.0,
      "u3": -250.0,
      "r1": 0.0,
      "r2": 0.0,
      "r3": 0.0
    }
  ],
  "warnings": []
}
```

## Mocked Controller Test

Use `mock_ETABSAnalysis` in tests. Keep actual ETABS execution as a manual worker-machine test.

```python
import json
import unittest
from types import SimpleNamespace

import viktor as vkt
from viktor.testing import mock_ETABSAnalysis

from app import Controller


class TestController(unittest.TestCase):
    @mock_ETABSAnalysis(
        get_output_file={
            "output.json": vkt.File.from_data(
                json.dumps(
                    {
                        "status": "ok",
                        "units": {"force": "N", "moment": "N mm"},
                        "base_reactions": [
                            {
                                "node": "1",
                                "load_case": "Dead",
                                "u1": 1.0,
                                "u2": 2.0,
                                "u3": 3.0,
                                "r1": 0.0,
                                "r2": 0.0,
                                "r3": 0.0,
                            }
                        ],
                        "warnings": [],
                    }
                ).encode("utf-8")
            )
        }
    )
    def test_run_etabs_returns_table(self):
        params = SimpleNamespace(frame_length=4000, frame_height=4000)
        result = Controller().run_etabs(params)
        self.assertEqual(result.column_headers, ["Node", "Load Case", "U1 [N]", "U2 [N]", "U3 [N]"])
```

## Manual Worker Smoke Test

On the worker machine:

1. Create a small `inputs.json` next to `run_etabs_model.py`.
2. Run the same Python executable selected during worker installation.
3. Confirm ETABS starts, analyzes, closes, and writes `output.json`.

```powershell
C:\Path\To\python.exe run_etabs_model.py
type output.json
```

Then run the VIKTOR app and trigger the view:

```bash
viktor-cli install
viktor-cli start
```
