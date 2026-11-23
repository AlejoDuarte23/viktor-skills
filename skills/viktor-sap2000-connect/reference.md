# SAP2000 Connect Reference

Source: <https://docs.viktor.ai/docs/create-apps/software-integrations/etabs-and-sap2000/>

## Configuration

```toml
worker_integrations = ["sap2000connect"]
```

`connect()` requires VIKTOR SDK 14.32.0 or later. `attach()` requires 14.33.0 or later. Both use a
`sap2000connect` worker on a Windows machine with SAP2000.

## Sessions

Use `connect()` when the app creates a model for the current calculation. Use `attach()` when the
app works with the model an engineer already has open. The context manager owns the session boundary.

```python
with vkt.sap2000.connect(timeout=60) as sap:
    # Build and query a fresh model.
    pass

with vkt.sap2000.attach(timeout=60) as sap:
    # Query or update the model currently open in SAP2000.
    pass
```

## Calling CSI methods

SAP2000 API signatures are VB6. Translate them directly:

- An `As Long` return is a CSI status code: `0` is success.
- Each `ByRef` parameter is supplied as a placeholder and returned before the status code.
- `Optional` arguments are positional; trailing values may be omitted.
- CSI arrays use Python lists, and SDK enums are available under `vkt.sap2000`.

```python
def check(ret, operation):
    if ret != 0:
        raise vkt.UserError(f"SAP2000 failed: {operation} ({ret})")

[frame_name, ret] = sap.FrameObj.AddByCoord(
    0, 0, 0, 6, 0, 0, "", "Default", "Beam", "Global"
)
check(ret, "FrameObj.AddByCoord")
```

`sap` is the CSI model object, so use its normal OAPI paths: `sap.PointObj`, `sap.FrameObj`,
`sap.Analyze`, and `sap.Results`.

## Attached models, performance, and testing

`attach()` leaves the engineer's instance open when the session closes. Keep one SAP2000 instance open; the API does not let the app select among several. Avoid clearing, initializing, or overwriting the open model. Check the model state and units before a write; partial edits can remain after an error. Catch `vkt.errors.WorkerSessionAttachError` before `vkt.errors.WorkerSessionError` and report how to reconnect.

Each OAPI call is a worker round trip. Prefer supported bulk operations and avoid per-element loops where possible. The box culvert sample uses a seed object and database table arrays for bulk model creation, then checks import errors and reads back the geometry. Validate table fields and supported versions; do not assume table schemas are identical across CSI releases. `timeout` applies to individual calls and attach, not the entire session. File paths must be relative to the temporary session directory; the current API cannot return a model file to the app. Extract needed data before the session ends.

Use `vkt.testing.mock_SAP2000Connection` for both modes. Mock expected OAPI return shapes, status failures, and attach failures; a mock does not verify an actual CSI model.
