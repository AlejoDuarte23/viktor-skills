# VIKTOR SAP2000 Worker Reference

## Scope

Use this reference when a VIKTOR app needs to run SAP2000 on a Windows machine through a VIKTOR worker.

The intended architecture is:

1. The VIKTOR app runs in the cloud or in a local development workspace.
2. The controller serializes params and model data to one or more files.
3. The controller starts a `SAP2000Analysis` worker job.
4. The worker runs a Python script on a Windows machine with SAP2000 installed.
5. The script automates SAP2000 through the CSI OAPI using `comtypes`.
6. The script writes declared output files.
7. The controller reads returned files and builds VIKTOR views, tables, or downloads.

Important distinction:

- Use `vkt.sap2000.SAP2000Analysis` for SAP2000 worker calls.
- Use `vkt.etabs.ETABSAnalysis` for ETABS worker calls.
- Use `viktor.external.python.PythonAnalysis` only for a deliberately generic worker setup.
- Do not automate SAP2000 directly from app-side controller code. COM automation belongs in the worker script.

## App Layout

Minimal layout:

```text
my-sap2000-app/
+-- app.py
+-- run_sap2000_model.py
+-- csi_comtypes_helpers.py
+-- csi_output_types.py
+-- requirements.txt
+-- viktor.config.toml
```

Larger app layout:

```text
my-sap2000-app/
+-- app/
|   +-- __init__.py
|   +-- controller.py
|   +-- sap_worker/
|       +-- run_sap2000_model.py
|       +-- csi_comtypes_helpers.py
|       +-- csi_output_types.py
+-- requirements.txt
+-- viktor.config.toml
```

Runtime files such as `inputs.json`, `output.json`, `.sdb`, and debug exports should be created in the worker working directory.

## Configuration

`viktor.config.toml` must expose the SAP2000 worker integration:

```toml
app_type = "simple"
python_version = "3.12"

worker_integrations = [
    "sap2000",
]
```

For apps that support both CSI products:

```toml
worker_integrations = [
    "etabs",
    "sap2000",
]
```

## Requirements

App-side `requirements.txt`:

```text
viktor>=14.17.0
```

Use a VIKTOR SDK version that supports `SAP2000Analysis`. The SDK reference marks `SAP2000Analysis` as available from VIKTOR SDK 14.17.0. In real apps, pin this to an available release from your environment once the app installs cleanly.

Worker-side requirements:

- Windows machine or Windows server where the VIKTOR worker is installed.
- SAP2000 installed on that same machine with a valid license.
- Python executable selected during worker installation.
- `comtypes` installed into that exact Python environment.
- SAP2000 CSI OAPI available for the installed SAP2000 version.
- Matching bitness: use 64-bit Python with 64-bit SAP2000.
- Matching permissions: if SAP2000 runs elevated, run the worker/Python elevated too.

Install worker Python dependencies with the Python executable selected during worker setup:

```powershell
C:\Path\To\python.exe -m pip install comtypes
```

Project standard:

- Prefer `comtypes` for SAP2000 and ETABS worker scripts.
- Do not use `win32com.client`, `VARIANT`, or `EnsureDispatch` in new worker code.
- Install `pywin32` only when an existing project still imports `pythoncom` or `win32com`; do not make it part of the new default pattern.

## COM Initialization

Initialize COM on the worker thread before creating or attaching to CSI objects, and uninitialize it in a `finally` block.

```python
import comtypes

comtypes.CoInitialize()
try:
    ...
finally:
    comtypes.CoUninitialize()
```

Each successful COM initialization on a thread must be balanced by a matching uninitialize call. This matters for worker scripts, background threads, and long-running agent tools.

## SAP2000 Helper Methods

SAP2000 OAPI access starts with the helper object:

```python
import comtypes.client

helper = comtypes.client.CreateObject("SAP2000v1.Helper")
```

### Attach To Active SAP2000

Use this when the user already opened SAP2000 and selected `Tools -> Set as active instance for API`.

```python
sap_object = helper.GetObject("CSI.SAP2000.API.SapObject")
sap_model = sap_object.SapModel
```

Requirements:

- SAP2000 is running.
- A model is open.
- The user has set the active API instance.
- SAP2000 and Python run at the same permission level.

### Launch By Program Path

Use this when the worker script owns the SAP2000 process and the installed version path is known.

```python
program_path = r"C:\Program Files\Computers and Structures\SAP2000 26\SAP2000.exe"
sap_object = helper.CreateObject(program_path)
sap_object.ApplicationStart()
sap_model = sap_object.SapModel
```

Prefer a configurable path when the app may run on different worker machines.

### Launch By ProgID

Use this when the registered SAP2000 COM server should choose the installed version.

```python
sap_object = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
sap_object.ApplicationStart()
sap_model = sap_object.SapModel
```

This avoids hardcoding an executable path, but it depends on COM registration being correct.

## ETABS Equivalent Helper Methods

Use the same `comtypes` pattern for ETABS:

```python
helper = comtypes.client.CreateObject("ETABSv1.Helper")

etabs_object = helper.GetObject("CSI.ETABS.API.ETABSObject")
etabs_object = helper.CreateObject(r"C:\Program Files\Computers and Structures\ETABS 22\ETABS.exe")
etabs_object = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")

etabs_object.ApplicationStart()
sap_model = etabs_object.SapModel
```

CSI names the model API object `SapModel` in both ETABS and SAP2000.

## Session Ownership

Track whether the worker started the CSI process.

- If the script launched SAP2000, close it with `ApplicationExit(False)` in `finally`.
- If the script attached to a user's active instance, normally do not close it.
- Always clear local references before `CoUninitialize`.

Recommended session helper:

```python
from csi_comtypes_helpers import CsiComSession

with CsiComSession(product="sap2000", attach_to_active=False, program_path=PROGRAM_PATH) as csi:
    model = csi.model
```

## Controller Responsibilities

The VIKTOR controller should:

- Define the UI and collect user parameters.
- Build a JSON-serializable input contract for the worker.
- Keep units explicit in parameter labels, JSON keys, and output headers.
- Locate the worker script with `Path(__file__).parent / "run_sap2000_model.py"` or an equivalent package path.
- Send files as `BytesIO` or `vkt.File` objects.
- Declare every expected output file in `output_filenames`.
- Call `execute(timeout=...)` with a realistic timeout.
- Fetch output with `get_output_file("output.json")`.
- Decode JSON and validate required keys before building VIKTOR results.
- Convert worker failures to `vkt.UserError` messages.
- Avoid importing `comtypes` or CSI COM modules in app-side controller code.

## Worker Script Responsibilities

The SAP2000 worker script should:

- Read input files from `Path.cwd()`.
- Use `comtypes.CoInitialize()` and `comtypes.CoUninitialize()` through `CsiComSession` or an equivalent balanced pattern.
- Start or attach to SAP2000 through `SAP2000v1.Helper`.
- Open an existing model or create a new one when requested.
- Set units explicitly before creating geometry, assigning loads, or reading results.
- Run `SapModel.Analyze.RunAnalysis()` when needed.
- Select output cases or combinations before result extraction.
- Extract result arrays through CSI OAPI calls.
- Normalize results into JSON-serializable dictionaries and lists.
- Write declared output files to `Path.cwd()`.
- Close SAP2000 only if the script launched the instance.

Keep the worker script runnable from a Windows terminal:

```powershell
C:\Path\To\python.exe run_sap2000_model.py
```

## JSON Contracts

For extraction-only workers that attach to an active model:

```json
{
  "attach_to_active": true,
  "program_path": "",
  "model_path": "",
  "save_model_path": "",
  "run_analysis": false,
  "result_names": ["DEAD", "ULS1", "ULS2"],
  "modal_result_names": ["MODAL"],
  "extract": {
    "model_lists": true,
    "support_nodes": true,
    "joint_reactions": true,
    "joint_displacements": true,
    "frame_forces": true,
    "base_reactions": true,
    "modal_periods": true
  },
  "units": {
    "length": "m",
    "force": "kN",
    "moment": "kN m"
  }
}
```

Recommended output:

```json
{
  "status": "ok",
  "units": {
    "length": "m",
    "force": "kN",
    "moment": "kN m"
  },
  "model_lists": {
    "points": ["1", "2"],
    "frames": ["F1"],
    "load_cases": ["DEAD"],
    "load_combinations": ["ULS1"]
  },
  "support_nodes": [
    {
      "joint": "1",
      "x": 0.0,
      "y": 0.0,
      "z": 0.0,
      "restraint": {"u1": 1, "u2": 1, "u3": 1, "r1": 1, "r2": 1, "r3": 1}
    }
  ],
  "joint_reactions": {
    "1": {
      "ULS1": [
        {
          "joint": "1",
          "object": "1",
          "element": "1",
          "requested_result": "ULS1",
          "result_type": "combo",
          "load_case": "ULS1",
          "step_type": "",
          "step_num": 0.0,
          "f1": 12.3,
          "f2": 0.0,
          "f3": -225.0,
          "m1": 0.0,
          "m2": 4.5,
          "m3": 0.0
        }
      ]
    }
  },
  "joint_displacements": [],
  "frame_forces": [],
  "base_reactions": [],
  "modal_periods": [],
  "warnings": []
}
```

If the worker catches an error and writes JSON:

```json
{
  "status": "error",
  "message": "Could not attach to SAP2000. Open SAP2000 and set it as active instance for API.",
  "warnings": []
}
```

The controller must check `status` before displaying results.

## Output Schema Style

Use `Annotated[...]` fields for output schemas. Do not assign defaults in schema definitions.

Do not write:

```python
frame_forces: list[FrameForceOut] = []
```

Write:

```python
frame_forces: Annotated[list[FrameForceOut], "Frame internal force rows"]
```

Defaults belong in output builder functions, not in `TypedDict` schema definitions. Use `scripts/csi_output_types.py` for a complete contract.

## Main Results Extraction Toolset

Use this section when the worker needs common SAP2000 analysis results.

The controller should request outputs through `inputs.json`. The worker decides which helper functions to call based on the `extract` flags.

### Main Result Families

| Result | CSI method | Output key | Notes |
|---|---|---|---|
| Point names | `PointObj.GetNameList` | `model_lists.points` | Used before supports, joint reactions, and displacements. |
| Frame names | `FrameObj.GetNameList` | `model_lists.frames` | Used before frame/internal forces. |
| Load cases | `LoadCases.GetNameList` | `model_lists.load_cases` | Used to choose output cases. |
| Load combinations | `RespCombo.GetNameList` | `model_lists.load_combinations` | Used to choose output combinations. |
| Support nodes | `PointObj.GetRestraint` + `PointObj.GetCoordCartesian` | `support_nodes` | Returns restrained joints and coordinates. |
| Joint reactions | `Results.JointReact` | `joint_reactions` | Returns `F1`, `F2`, `F3`, `M1`, `M2`, `M3`. |
| Joint displacements | `Results.JointDispl` or `Results.JointDisplAbs` | `joint_displacements` | Returns `U1`, `U2`, `U3`, `R1`, `R2`, `R3`. |
| Frame internal forces | `Results.FrameForce` | `frame_forces` | Returns `P`, `V2`, `V3`, `T`, `M2`, `M3` along frame stations. |
| Base reactions | `Results.BaseReact` | `base_reactions` | Returns total base `FX`, `FY`, `FZ`, `MX`, `MY`, `MZ`. |
| Modal periods | `Results.ModalPeriod` | `modal_periods` | Returns period, frequency, circular frequency, and eigenvalue. |
| Database display tables | `DatabaseTables.GetTableForDisplayArray` | `database_tables` | Additive table-export tool for CSI display tables. |
| Shell forces | `Results.AreaForceShell` | `shell_forces` | Optional; add only when shell/plate results are needed. |
| Shell stresses | `Results.AreaStressShell` | `shell_stresses` | Optional; add only when stress recovery is needed. |
| Link forces | `Results.LinkForce` | `link_forces` | Optional; add for link/support-element models. |

### Required Result Extraction Flow

1. Start or attach to SAP2000 with `CsiComSession`.
2. Set units before extracting values when the app controls units.
3. Run analysis when `run_analysis` is true.
4. Build model lists if requested.
5. Select one result case or combination at a time.
6. Call the requested result helper.
7. Normalize tuple/list outputs into dictionaries/lists.
8. Write one `output.json`.
9. Include `status`, `units`, and `warnings`.

Do not silently drop multi-row results. Joint reactions, frame forces, displacements, base reactions, and modal periods can return many rows per object, station, step, or output case. Store them as lists.

### Comtypes Method Contracts

Ground every direct CSI call in a small input/output contract. With `comtypes`, the same SAP2000 method can return tuples or lists, and generated wrappers may include or omit the return code. The helper functions in `csi_comtypes_helpers.py` normalize these shapes.

| Helper | Comtypes call and inputs | Accepted raw output shapes | Normalized output |
|---|---|---|---|
| `get_name_list(...)` | `api_object.GetNameList(0, [])`, fallback `api_object.GetNameList()` | `[NumberNames, Names]`, `(NumberNames, Names, ret)`, `(ret, NumberNames, Names)` | `list[str]` |
| `get_point_coords(...)` | `SapModel.PointObj.GetCoordCartesian(point_name, 0, 0, 0)` | `[x, y, z]`, `[x, y, z, ret]`, `[ret, x, y, z]` | `(float(x), float(y), float(z))` |
| `get_point_restraint(...)` | `SapModel.PointObj.GetRestraint(point_name, [0, 0, 0, 0, 0, 0])`, fallback `GetRestraint(point_name)` | `[u1, u2, u3, r1, r2, r3]`, `[u1, u2, u3, r1, r2, r3, ret]`, `[ret, u1, u2, u3, r1, r2, r3]`, `([u1, u2, u3, r1, r2, r3], ret)` | `list[int]` with six restraint flags |
| `get_frame_points(...)` | `SapModel.FrameObj.GetPoints(frame_name, "", "")` | `[point_i, point_j]`, `[point_i, point_j, ret]`, `[ret, point_i, point_j]` | `(str(point_i), str(point_j))` |
| `call_joint_react(...)` | `SapModel.Results.JointReact(joint_name, 0, 0, [], [], [], [], [], [], [], [], [], [], [])`, fallback `JointReact(joint_name, 0)` | `[NumberResults, Obj, Elm, LoadCase, StepType, StepNum, F1, F2, F3, M1, M2, M3]`, plus `ret` first or last | one row dict per reaction result with `f1`, `f2`, `f3`, `m1`, `m2`, `m3` |
| `call_joint_displ(...)` | `SapModel.Results.JointDispl(point_name, 0, 0, [], [], [], [], [], [], [], [], [], [], [])`, fallback `JointDispl(point_name, 0)` | `[NumberResults, Obj, Elm, LoadCase, StepType, StepNum, U1, U2, U3, R1, R2, R3]`, plus `ret` first or last | one row dict per result with `u1`, `u2`, `u3`, `r1`, `r2`, `r3` |
| `call_frame_force(...)` | `SapModel.Results.FrameForce(frame_name, 0, 0, [], [], [], [], [], [], [], [], [], [], [], [], [])`, fallback `FrameForce(frame_name, 0)` | `[NumberResults, Obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, P, V2, V3, T, M2, M3]`, plus `ret` first or last | one row dict per station with `p`, `v2`, `v3`, `t`, `m2`, `m3` |
| `call_base_react(...)` | `SapModel.Results.BaseReact(0, [], [], [], [], [], [], [], [], [], 0.0, 0.0, 0.0)`, fallback `BaseReact()` | `[NumberResults, LoadCase, StepType, StepNum, FX, FY, FZ, MX, MY, MZ, GX, GY, GZ]`, plus `ret` first or last | one row dict per result with base reactions and global point |
| `call_modal_period(...)` | `SapModel.Results.ModalPeriod(0, [], [], [], [], [], [], [])`, fallback `ModalPeriod()` | `[NumberResults, LoadCase, StepType, StepNum, Period, Frequency, CircFreq, EigenValue]`, plus `ret` first or last | one row dict per mode |
| `get_available_database_tables(...)` | `SapModel.DatabaseTables.GetAvailableTables()` | tuple/list containing one or more string arrays | `list[str]` table keys |
| `parse_table_for_display_array_result(...)` | `SapModel.DatabaseTables.GetTableForDisplayArray(TableKey=..., GroupName=...)`, fallback positional call | tuple/list containing field keys, record count, flat table data, and optional return code | `(columns, rows)` and downstream `records` |

Rules for adding a new CSI method:

1. Write down the exact `comtypes` call inputs before coding the parser.
2. Capture at least one raw return from the target worker machine.
3. Add a parser fixture for that raw return shape.
4. Normalize to JSON-safe values before returning from the worker.
5. Validate result-array lengths against `NumberResults`; do not truncate arrays with `min(...)`.

## Database Table Export Tool

Use `scripts/csi_database_tables.py` when the app should retrieve CSI display tables as generic table data instead of calling one direct `Results.*` method per result family.

This follows the same idea as the public `viktor-platform/etabs-sap-wrapper` table helper: use `SapModel.DatabaseTables`, select display cases or combinations, retrieve a named table with `GetTableForDisplayArray`, and normalize the flat table data into rows and records. Keep it as an additive tool. Do not replace direct result helpers when the app needs precise typed extraction.

Good use cases:

- The user asks for a table by name.
- The result family is already exposed as a CSI database display table.
- The app needs broad, configurable result export.
- The output will become a VIKTOR table, JSON download, CSV, or debug payload.

Prefer direct `Results.*` helpers when:

- The app needs a stable typed contract for calculations.
- You need exact control over stations, object/element item type, or result semantics.
- You are using a result that is not reliably available as a database table in both SAP2000 and ETABS.

Worker input pattern:

```json
{
  "extract": {
    "database_tables": true
  },
  "database_tables": [
    {
      "name": "frame_forces",
      "load_cases": ["DEAD"],
      "load_combinations": ["ULS1"],
      "group_name": ""
    },
    {
      "table_key": "Joint Displacements",
      "load_cases": ["DEAD"],
      "group_name": ""
    }
  ]
}
```

Friendly names in `csi_database_tables.py`:

| Friendly name | CSI table key |
|---|---|
| `frame_forces` | `Element Forces - Frames` |
| `beam_forces` | `Element Forces - Beams` |
| `joint_displacements` | `Joint Displacements` |
| `base_reactions` | `Base Reactions` |

Output shape:

```json
{
  "database_tables": [
    {
      "table_key": "Element Forces - Frames",
      "group_name": "",
      "columns": ["Frame", "OutputCase", "StepType", "P", "V2", "V3", "T", "M2", "M3"],
      "rows": [["1", "DEAD", "", "10.0", "0.0", "0.0", "0.0", "5.0", "0.0"]],
      "records": [
        {
          "Frame": "1",
          "OutputCase": "DEAD",
          "StepType": "",
          "P": 10.0,
          "V2": 0.0,
          "V3": 0.0,
          "T": 0.0,
          "M2": 5.0,
          "M3": 0.0
        }
      ]
    }
  ]
}
```

Implementation notes:

- Include `csi_database_tables.py` in the worker files sent by `SAP2000Analysis` or `ETABSAnalysis`.
- Keep it independent from pandas and numpy so the worker does not need extra dependencies.
- If a project already uses pandas, converting `records` to a DataFrame is fine in project code.
- Table availability depends on the model, product, analysis state, selected cases, and CSI version.
- Use `get_available_database_tables(model)` to inspect keys before requesting a table.
- Numeric coercion is intentionally column-based. Add project-specific numeric columns in the request when needed.

## CSI OAPI Return Parsing

CSI OAPI methods often return tuples or lists with output arguments and a return code. The order can differ between examples, `comtypes`, generated type-library wrappers, and CSI versions. Some generated wrappers return compact output-only lists without an explicit return code.

Rules:

- Always check the return code.
- Prefer helper functions that parse by shape when wrappers differ.
- For name-list calls, find the longest list/tuple as the name list and an integer return code.
- Treat compact name-list outputs such as `[NumberNames, Names]` as successful when `NumberNames` matches `len(Names)`.
- For scalar output calls such as `PointObj.GetCoordCartesian`, accept `[x, y, z]`, `[x, y, z, ret]`, and `[ret, x, y, z]`.
- For two-name output calls such as `FrameObj.GetPoints`, accept `[point_i, point_j]`, `[point_i, point_j, ret]`, and `[ret, point_i, point_j]`.
- For restraint calls, accept nested or flat six-value restraint lists, with or without an explicit return code.
- For result calls, parse expected arrays by position only after validating tuple length.
- Keep debug failures explicit: include method name and the raw returned value in the exception.

Useful calls:

```python
SapModel.PointObj.GetNameList(0, [])
SapModel.FrameObj.GetNameList(0, [])
SapModel.RespCombo.GetNameList(0, [])
SapModel.LoadCases.GetNameList(0, [])
SapModel.PointObj.GetCoordCartesian(point_name, 0, 0, 0)
SapModel.PointObj.GetRestraint(point_name, [0, 0, 0, 0, 0, 0])
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput(name)
SapModel.Results.Setup.SetComboSelectedForOutput(name)
SapModel.Results.JointReact(joint_name, 0, 0, [], [], [], [], [], [], [], [], [], [], [])
SapModel.Results.JointDispl(point_name, 0, 0, [], [], [], [], [], [], [], [], [], [], [])
SapModel.Results.FrameForce(frame_name, 0, 0, [], [], [], [], [], [], [], [], [], [], [], [], [])
SapModel.Results.BaseReact(0, [], [], [], [], [], [], [], [], [], 0.0, 0.0, 0.0)
SapModel.Results.ModalPeriod(0, [], [], [], [], [], [], [])
SapModel.DatabaseTables.GetAvailableTables()
SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(["DEAD"])
SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(["ULS1"])
SapModel.DatabaseTables.GetTableForDisplayArray(TableKey="Element Forces - Frames", GroupName="")
```

## Coordinate Order

When migrating older SAP2000 helper code to `comtypes`, re-check coordinate tuple order before preserving any manual coordinate rotation.

Before using coordinates for geometry, supports, or footing placement:

1. Open a small SAP2000 model with one support at a known coordinate.
2. Call `PointObj.GetCoordCartesian(point_name, 0, 0, 0)`.
3. Print the raw tuple.
4. Confirm whether the installed SAP2000/comtypes combination returns `x, y, z, ret`.
5. Only add a remap in the project worker if the raw tuple proves it is needed.

## Error Handling

Controller-side handling:

- Catch `viktor.errors.LicenseError` and explain that no SAP2000 worker license is available or the worker is unavailable.
- Catch `viktor.errors.ExecutionError` and include concise worker failure context.
- Check that `get_output_file("output.json")` returned a file.
- Catch `json.JSONDecodeError` and report malformed worker output.
- Check `status == "ok"` when the worker uses a status envelope.
- Validate required keys such as `units` and the requested output keys.

Worker-side handling:

- Validate `inputs.json` before starting SAP2000 when possible.
- Fail clearly when SAP2000 cannot attach or launch.
- Include the active-instance instruction in attach failures: `Tools -> Set as active instance for API`.
- Wrap SAP2000 lifecycle in `try/finally` or use `CsiComSession`.
- Write useful progress messages with `print`; these help diagnose worker logs.
- Prefer structured `output.json` errors for expected user-fixable issues.

Common failures:

- `comtypes` is not installed in the worker-selected Python environment.
- SAP2000 is not installed or the program path is wrong.
- SAP2000 license is unavailable.
- SAP2000 is not set as active API instance when using attach mode.
- Worker and SAP2000 permissions differ.
- Python and SAP2000 bitness differ.
- Modal dialogs block automation.
- Analysis timeout is too short.
- Output filename is not listed in `output_filenames`.
- Output is written somewhere other than `Path.cwd()`.

## Testing

Do not run SAP2000 in automated CI tests. Mock worker execution.

Use `viktor.testing.mock_SAP2000Analysis` for controller tests:

```python
@mock_SAP2000Analysis(get_output_file={
    "output.json": vkt.File.from_data(
        b'{"status": "ok", "units": {"length": "m", "force": "kN", "moment": "kN m"}, "warnings": []}'
    )
})
def test_controller_view(self):
    result = Controller().run_sap2000(params)
    self.assertIsNotNone(result)
```

Recommended boundaries:

- Unit test input payload builders.
- Unit test output parsing and schema validation.
- Unit test COM tuple parsers with fixture tuples.
- Mock `SAP2000Analysis` in VIKTOR controller tests.
- Manually test the worker script on the Windows SAP2000 machine.

## Review Checklist

Before finishing a SAP2000 worker app, verify:

- `viktor.config.toml` includes `worker_integrations = ["sap2000"]`.
- App `requirements.txt` uses a VIKTOR SDK that supports `SAP2000Analysis`.
- Worker Python has `comtypes` installed.
- SAP2000 path, version, and launch mode are documented.
- Controller uses `vkt.sap2000.SAP2000Analysis`, not direct COM automation.
- Worker script uses `comtypes`, not `win32com`.
- Worker script reads from `Path.cwd()` and writes declared outputs to `Path.cwd()`.
- Input and output JSON contracts have units and stable keys.
- COM initialization and uninitialization are balanced.
- SAP2000 is closed only when the script started it.
- Controller errors are user-facing and actionable.
- Tests mock SAP2000 execution.
