# SAP2000 Worker Helper Scripts

These files are agent reference material and reusable worker-side helpers for VIKTOR SAP2000 and ETABS integrations.

## Runtime Boundary

- Run these helpers on the Windows worker machine where SAP2000 or ETABS is installed.
- Do not import `comtypes` from VIKTOR app-side controller code unless the app server itself is a compatible Windows machine.
- App-side code should call `vkt.sap2000.SAP2000Analysis` or `vkt.etabs.ETABSAnalysis`, send files, and read declared outputs.
- Worker-side scripts should read inputs from `Path.cwd()` and write declared outputs, usually `output.json`, to `Path.cwd()`.

## Files

- `csi_comtypes_helpers.py`: launch or attach to CSI products, parse common OAPI return shapes, and extract common results.
- `csi_database_tables.py`: export generic `SapModel.DatabaseTables` display tables.
- `csi_output_types.py`: typed JSON output contracts for worker results.

## Use As Reference, Not Full CSI Documentation

These helpers cover common SAP2000/ETABS workflows, but they are not the full CSI API. Before adding a new result family:

1. Write down the exact `comtypes` method inputs.
2. Capture the raw return value from the target worker machine.
3. Add a small parser fixture for ret-code-first, ret-code-last, no-ret-code, zero-row, and multi-row shapes when applicable.
4. Validate result-array lengths against `NumberResults`.
5. Normalize output to JSON-safe dictionaries and lists before returning it to VIKTOR.

Do not silently truncate result arrays. If CSI returns inconsistent output lengths, raise a clear worker error so the model, result selection, or parser can be inspected.
