# VIKTOR ETABS Worker Reference

This skill is based on the public VIKTOR sample repository `viktor-platform/etabs-concrete-frame` at commit `6bd046c6c3c332fd33adfb3660a936c5648bffc3`, plus official VIKTOR worker and SDK documentation.

Official sources:

- https://github.com/viktor-platform/etabs-concrete-frame
- https://docs.viktor.ai/docs/create-apps/software-integrations/etabs-and-sap2000/
- https://docs.viktor.ai/docs/tutorials/integrate-etabs-sap2000/
- https://docs.viktor.ai/sdk/api/external/etabs/
- https://docs.viktor.ai/sdk/api/external/python/

## Scope

Use this reference when a VIKTOR app needs to run an ETABS model through the CSI API on a machine outside the VIKTOR cloud runtime.

The public sample app creates a simple 3D concrete frame from frame length and frame height, sends the model topology to a worker as JSON, creates and analyzes the model in ETABS, extracts base reactions from the default `Dead` load case, writes `output.json`, and displays the result in a VIKTOR `TableView`.

## Core Architecture

VIKTOR app code and ETABS execution are separated:

1. The user enters parameters in the VIKTOR UI.
2. The VIKTOR controller builds a data contract, usually `inputs.json`.
3. The controller calls `vkt.etabs.ETABSAnalysis`.
4. VIKTOR transfers the script and files to the ETABS worker.
5. The worker runs the Python script in the Python environment selected during worker installation.
6. The worker script controls ETABS locally through the CSI COM API.
7. The worker script writes declared output files, usually `output.json`.
8. VIKTOR transfers the output files back to the app.
9. The controller parses and validates the output and returns a VIKTOR result.

Important distinction:

- For ETABS, prefer `vkt.etabs.ETABSAnalysis`.
- `ETABSAnalysis` inherits the same concept as `PythonAnalysis`: send a Python script and input files, execute it on third-party infrastructure, then fetch declared output files.
- Use `viktor.external.python.PythonAnalysis` only for a deliberately generic Python worker setup. Do not replace `ETABSAnalysis` with generic `PythonAnalysis` in ETABS apps unless the project has chosen a generic worker architecture.

## App Layout

Typical app layout:

```text
my-etabs-app/
+-- app.py
+-- run_etabs_model.py
+-- requirements.txt
+-- viktor.config.toml
```

Runtime files such as `inputs.json`, `output.json`, and `etabsmodel.edb` should be created in the worker working directory, not committed as source files unless they are fixtures for tests.

## Configuration

`viktor.config.toml` must expose the ETABS worker integration:

```toml
app_type = "simple"
python_version = "3.12"

worker_integrations = [
    "etabs",
]
```

The sample repository uses `app_type = 'simple'`, but the same integration pattern can be used in `editor` and `tree` apps. For tree apps, keep worker calls in the controller responsible for the entity that owns the parameters and results.

## Requirements

App-side `requirements.txt`:

```text
viktor==14.27.3
```

Use a VIKTOR SDK version that supports `vkt.etabs.ETABSAnalysis`. The SDK reference marks `ETABSAnalysis` as available from VIKTOR SDK 14.17.0.

Worker-side requirements:

- Windows machine or Windows server where the VIKTOR worker is installed.
- ETABS installed on that same machine with a valid license.
- Python executable selected during worker installation.
- `pywin32` and `comtypes` installed into that exact Python environment.
- The ETABS CSI COM API available for the installed ETABS version.
- The ETABS program path in `run_etabs_model.py` matches the installed version, for example `C:\Program Files\Computers and Structures\ETABS 22\ETABS.exe`.

Install worker Python dependencies with the Python executable selected during worker setup:

```powershell
C:\Path\To\python.exe -m pip install pywin32 comtypes
```

Use `where python` on Windows to help find Python executables. Installing `comtypes` and `pywin32` into a different environment than the one selected by the worker is a common cause of worker failures.

## Local ETABS Execution Assumptions

The ETABS worker script runs outside the VIKTOR cloud runtime. It assumes:

- ETABS can be started interactively or through COM on the worker machine.
- The worker and ETABS have compatible permissions. If ETABS is run as administrator, the worker may need the same permission level.
- No modal dialogs block automation, such as license prompts, update prompts, recovery prompts, or first-run setup dialogs.
- The worker machine has enough desktop/session access for ETABS automation.
- The script is blocking. It should not return before ETABS has finished analysis and written all declared output files.
- Generated files are written relative to `Path.cwd()`, which is the worker working directory.
- Long analyses need realistic `execute(timeout=...)` values.

## Controller Responsibilities

The VIKTOR controller should:

- Define the UI and collect user parameters.
- Build a clear, JSON-serializable input contract for the worker.
- Keep units explicit in parameter labels, JSON keys, and output headers.
- Use `Path(__file__).parent / "run_etabs_model.py"` to locate the worker script in the app package.
- Send input files as `BytesIO` or `vkt.File` objects.
- Declare every expected output file in `output_filenames`.
- Call `execute(timeout=...)`.
- Fetch the output with `get_output_file("output.json")`.
- Decode JSON and validate required keys before building VIKTOR results.
- Convert known worker failures to `vkt.UserError` messages that tell the user what to fix.
- Avoid importing `comtypes`, `pythoncom`, or CSI API modules in app-side controller code.

The controller should not depend on live ETABS objects. Its contract with the worker is files in, files out.

## Worker Script Responsibilities

The worker script should:

- Read `inputs.json` from `Path.cwd()`.
- Initialize COM before using ETABS through `pythoncom.CoInitialize()`.
- Start ETABS through `comtypes.client.CreateObject("ETABSv1.Helper")`.
- Create or open the ETABS model.
- Set model units explicitly, for example `InitializeNewModel(9)` in the public sample for millimeter units.
- Create points, frames, materials, sections, supports, load cases, and analysis settings.
- Save the ETABS model into the worker working directory.
- Run `Analyze.RunAnalysis()` or the project-specific analysis command.
- Select output cases and combinations before result extraction.
- Extract result arrays from CSI API calls.
- Convert all output values to JSON-serializable types.
- Write `output.json` into `Path.cwd()`.
- Close ETABS with `ApplicationExit(False)` when the script started the ETABS instance.
- Call `pythoncom.CoUninitialize()` in a `finally` block after COM work is complete.

Keep the worker script independent from VIKTOR imports. It should be runnable from a Windows terminal for debugging:

```powershell
python run_etabs_model.py
```

## JSON and File I/O Contract

The public sample sends a list:

```json
[
  {
    "1": {"node_id": 1, "x": 0, "y": 0, "z": 0}
  },
  {
    "1": {"line_id": 1, "node_i": 1, "node_j": 3}
  }
]
```

This works, but for production apps prefer a named top-level object:

```json
{
  "units": {
    "length": "mm",
    "force": "N"
  },
  "nodes": {
    "1": {"x": 0, "y": 0, "z": 0},
    "2": {"x": 0, "y": 4000, "z": 0}
  },
  "frames": {
    "1": {"node_i": "1", "node_j": "3", "section": "300x300 RC"}
  },
  "supports": ["1", "2", "5", "6"],
  "load_case": "Dead"
}
```

Guidelines:

- Use string IDs in JSON. Python integer dictionary keys become strings after JSON serialization.
- Include units in the contract. Do not rely on implicit ETABS model units.
- Include model assumptions such as section names, material names, load case names, and support node IDs.
- Keep the output schema stable and small.
- For large model inputs, consider splitting geometry, loads, and settings into separate files, but keep filenames explicit in `files`.

Recommended output contract:

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

If the worker catches an error and writes JSON instead of raising, use a structured error:

```json
{
  "status": "error",
  "message": "ETABS could not be started. Check the ETABS program path.",
  "warnings": []
}
```

The controller must check `status` before displaying results.

## Analysis Result Extraction

The public sample extracts base reactions with this ETABS flow:

1. Save the model to `etabsmodel.edb`.
2. Run `EtabsObject.Analyze.RunAnalysis()`.
3. Set the active output case with `Results.Setup`.
4. Deselect all cases and combinations for output.
5. Select the `Dead` load case.
6. For each supported node, call `Results.JointReact(str(node), 0, 0)`.
7. Read translational reactions `U1`, `U2`, `U3` and rotational reactions `R1`, `R2`, `R3`.
8. Write a list of dictionaries to JSON.

ETABS result APIs often return arrays. Do not assume there is only one result row unless the selected case, step type, and object produce exactly one row. If there can be multiple steps, combinations, or stations, write one JSON object per returned row with the relevant case, step, object, station, and units.

For frame forces or displacements, keep the same pattern:

- Select output cases explicitly.
- Call the CSI result method for the desired result type.
- Normalize returned arrays into a list of dictionaries.
- Keep output field names lower-case and stable for VIKTOR-side parsing.

## Error Handling

Controller-side handling:

- Catch `viktor.errors.LicenseError` and explain that no ETABS worker license is available or the worker is unavailable.
- Catch `viktor.errors.ExecutionError` and include concise worker failure context.
- Check that `get_output_file("output.json")` returned a file.
- Catch `json.JSONDecodeError` and report malformed worker output.
- Check `status == "ok"` if the worker uses a status envelope.
- Validate required keys such as `base_reactions`, `node`, `load_case`, `u1`, `u2`, and `u3`.
- Raise `vkt.UserError` for user-correctable issues.

Worker-side handling:

- Validate `inputs.json` before starting ETABS when possible.
- Fail early when the ETABS program path is wrong.
- Wrap ETABS lifecycle in `try/finally` so ETABS can be closed.
- Write useful progress messages with `print`; they can help diagnose worker logs.
- Prefer a structured `output.json` with `status: "error"` when you want the controller to show a controlled message.
- Let unexpected errors raise when debugging locally, then decide whether to convert them to structured JSON in production.

Common failures:

- `comtypes` or `pywin32` is not installed in the worker-selected Python environment.
- The worker is installed but not running or not connected to the right VIKTOR environment.
- `worker_integrations = ["etabs"]` is missing from `viktor.config.toml`.
- The ETABS path points to a different version or does not exist.
- ETABS license is unavailable.
- ETABS opens a modal dialog and blocks automation.
- Worker and ETABS permissions differ.
- The analysis timeout is too short.
- Output filename is not listed in `output_filenames`.
- The worker writes output to a path other than `Path.cwd() / "output.json"`.
- JSON keys are converted from integers to strings.

## Testing

Do not run ETABS in automated CI tests. Mock `ETABSAnalysis.execute` and `get_output_file`.

Official VIKTOR docs provide `viktor.testing.mock_ETABSAnalysis` for this integration. Use it to return fixture `vkt.File` objects for `output.json`.

Recommended test boundaries:

- Unit test pure input builders such as `create_frame_data`.
- Unit test output parsing and schema validation.
- Mock worker results in controller tests.
- Manually test the worker script on the Windows ETABS machine before relying on the VIKTOR worker.

## Review Checklist

Before finishing an ETABS worker app, verify:

- `viktor.config.toml` includes `worker_integrations = ["etabs"]`.
- App `requirements.txt` pins a VIKTOR SDK that supports `ETABSAnalysis`.
- Worker Python has `pywin32` and `comtypes`.
- ETABS path and version are documented and configurable.
- Controller uses `vkt.etabs.ETABSAnalysis`, not direct COM automation.
- Worker script reads from `Path.cwd()` and writes declared output files to `Path.cwd()`.
- Input and output JSON contracts have units and stable keys.
- ETABS is closed on success and failure.
- Controller errors are user-facing and actionable.
- Tests mock ETABS execution.
