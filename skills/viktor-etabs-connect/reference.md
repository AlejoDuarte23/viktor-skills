# ETABS Connect Reference

Source: <https://docs.viktor.ai/docs/create-apps/software-integrations/etabs-and-sap2000/>

## Configuration

```toml
worker_integrations = ["etabsconnect"]
```

`connect()` requires VIKTOR SDK 14.31.0 or later. `attach()` requires 14.33.0 or later. Both use an
`etabsconnect` worker on a Windows machine with ETABS.

## Sessions

Use `connect()` when the app creates a model for the current calculation. Use `attach()` when the
app works with the model an engineer already has open. The context manager owns the session boundary.

```python
with vkt.etabs.connect(timeout=60) as sap:
    # Build and query a fresh model.
    pass

with vkt.etabs.attach(timeout=60) as sap:
    # Query or update the model currently open in ETABS.
    pass
```

## Calling CSI methods

ETABS API signatures are C#. Translate them directly:

- An `int` return is a CSI status code: `0` is success.
- Each `ref` or `out` parameter is supplied as a placeholder and returned before the status code.
- C# optional arguments are positional; trailing values may be omitted.
- CSI arrays use Python lists, and SDK enums are available under `vkt.etabs`.

```python
def check(ret, operation):
    if ret != 0:
        raise vkt.UserError(f"ETABS failed: {operation} ({ret})")

[frame_name, ret] = sap.FrameObj.AddByCoord(
    0, 0, 0, 6, 0, 0, "", "Default", "Beam", "Global"
)
check(ret, "FrameObj.AddByCoord")
```

`sap` is the CSI model object, so use its normal OAPI paths: `sap.PointObj`, `sap.FrameObj`,
`sap.Analyze`, and `sap.Results`.

## Attached models, performance, and testing

`attach()` leaves the engineer's instance open when the session closes. Keep one ETABS instance open; the API does not let the app select among several. Avoid clearing, initializing, or overwriting the open model. Check the model state and units before a write; partial edits can remain after an error. Catch `vkt.errors.WorkerSessionAttachError` before `vkt.errors.WorkerSessionError` and report how to reconnect.

Calls go through the worker. In SDK 14.37.0 and later, the default `defer=True` batches calls until their results are read; `defer=False` sends each call immediately. Earlier versions must be checked separately. Prefer supported bulk operations and avoid per-element loops where possible. The timeout applies to calls or batches and attach, not the entire session. File paths must be relative to the temporary session directory; the current API cannot return a model file to the app. Extract needed data before the session ends.

Use `vkt.testing.mock_ETABSConnection` for both modes. Mock expected OAPI return shapes, status failures, and attach failures; a mock does not verify an actual CSI model.
