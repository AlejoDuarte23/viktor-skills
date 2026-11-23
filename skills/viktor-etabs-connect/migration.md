# Migrate an ETABS Worker Script to Connect

Use this guide when an existing VIKTOR app sends a Python script to `ETABSAnalysis`, and that script uses `comtypes` to control ETABS. Preserve the app's inputs, units, outputs, and engineering behavior. The APIs are beta; check the installed SDK and worker versions.

Sources: [VIKTOR ETABS integration](https://docs.viktor.ai/docs/create-apps/software-integrations/etabs-and-sap2000/) and [ETABS SDK reference](https://docs.viktor.ai/sdk/api/external/etabs/).

## 1. Inventory the existing behavior

- Identify the `ETABSAnalysis` call, input files, worker script, output files, parsed JSON, and views that consume the results.
- Record whether the script starts ETABS or attaches to an existing model, whether it initializes or clears a model, and whether the engineer must keep the model open.
- Record units, geometry, materials, loads, combinations, analysis steps, result rows, and error messages. Save representative inputs and expected outputs for comparison.
- Identify model files, external files, worker-only packages, and operations that require the ETABS instance or session files to survive the job. Direct sessions cannot currently return the worker's model file. Keep the script integration if a required workflow cannot be reproduced.

## 2. Select the session and configure the worker

| Existing intent | Direct session | Behavior |
| --- | --- | --- |
| Start a fresh app-owned model | `vkt.etabs.connect()` | Opens a new empty instance for the session. |
| Work on an engineer's open model | `vkt.etabs.attach()` | Attaches to an existing instance; fails if none is running and leaves it open after detach. |

Do not silently switch between modes. For attach, use a personal worker on the engineer's machine, open the intended model, and keep only one ETABS instance open. Never call `InitializeNewModel`, `File.NewBlank`, or other clearing operations on the attached model unless the user explicitly intends that change. A failed write can leave partial changes; inspect the model before retrying.

Use SDK 14.31.0 or later for `connect()` and 14.33.0 or later for `attach()`. Add `"etabsconnect"` to `worker_integrations` in `viktor.config.toml`; keep other required entries. Start the ETABS personal worker in VIKTOR Desktop on a licensed, interactive Windows session. Direct sessions do not require `comtypes` or Python on the worker. Keep the legacy `"etabs"` integration while a script path still needs it; remove it only after migration and verification.

## 3. Move the OAPI work into the app

Before, the controller sends the script and files to a worker and reads `output.json`:

```python
analysis = vkt.etabs.ETABSAnalysis(
    script=worker_script,
    files=[("inputs.json", input_file)],
    output_filenames=["output.json"],
)
analysis.execute(timeout=300)
output_file = analysis.get_output_file("output.json")
```

After, put pure input preparation and result formatting in app-side functions. Put ETABS calls inside a session. The model returned by the context manager is the ETABS `SapModel`; do not call `CreateObject`, `ApplicationStart`, `ApplicationExit`, `CoInitialize`, or `CoUninitialize` for this session.

This small example reads a named frame from the open model. It replaces only that read operation; it is not a complete structural analysis or a replacement for existing reaction results.

```python
import viktor as vkt


def read_frame_points(frame_name: str) -> dict[str, str]:
    try:
        with vkt.etabs.attach(timeout=60) as sap:
            point_i, point_j, status = sap.FrameObj.GetPoints(frame_name, "", "")
            if status != 0:
                raise vkt.UserError(f"ETABS could not read frame {frame_name} (status {status}).")
            return {"frame": frame_name, "point_i": point_i, "point_j": point_j}
    except vkt.errors.WorkerSessionAttachError as error:
        raise vkt.UserError("Open the ETABS model and start its personal worker, then try again.") from error
    except vkt.errors.WorkerSessionError as error:
        raise vkt.UserError("The ETABS session was lost. Inspect the open model before retrying.") from error
```

For a new model, use `with vkt.etabs.connect(timeout=60) as sap:` and initialize that new model with the appropriate product-specific unit enum. Reuse model-building and extraction functions after adapting each call and result shape. Copy all needed values into ordinary Python data while the session is open; return data in the same schema the views expect. Replace JSON serialization only when no consumer needs that contract.

## 4. Translate calls and validate outputs

- Compare each call to the installed ETABS OAPI signature. Direct calls return a status code or output parameters followed by a status code; supply required `ref` and `out` placeholders. Do not assume a legacy `comtypes` tuple has the same order or shape. Check every returned status.
- Use `vkt.etabs` enums and explicit units. Preserve load case and combination labels, object and station IDs, step information, and every result row. Validate `NumberResults` and array lengths before building output records.
- When supported by the installed SDK, deferred calls can be batched. In SDK 14.37.0 and later, `defer=True` is the default: values are read when used, and errors can surface at that point. `defer=False` sends each call immediately. Do not use `is None` to inspect a deferred value. Check SDK-version support before passing `defer`.
- `timeout` bounds an individual call or batch and the attach operation, not the whole analysis. Use realistic values, report failures, and keep partial-result handling explicit.
- Use relative filenames for supported session file arguments. Session files are temporary; the connected app cannot currently download an ETABS model from the session. An attached engineer saves the model in ETABS.

## 5. Test and complete the migration

Replace `mock_ETABSAnalysis` tests with `vkt.testing.mock_ETABSConnection` for the new calls. Cover successful results, nonzero status, missing or mismatched result arrays, attach failure, lost sessions, and the absence of model-clearing calls in attach mode. Check output keys and units against the legacy fixtures.

Use an interactive Windows worker for a live comparison on a known disposable model. Compare geometry, loads, combinations, analysis completion, all relevant results, and tolerances. The box culvert sample builds a model and extracts results inside one `connect()` session; the beam and column sample reads an open model with `attach()`. Neither example proves that another project's engineering results are correct.

Remove the old script, input/output file handoff, `comtypes` dependency, or legacy worker configuration only after confirming that no other app path needs it. Report any feature that remains on the legacy integration.
