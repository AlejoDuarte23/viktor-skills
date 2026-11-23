# SAP2000 Connect Examples

## Start a fresh model

```python
import viktor as vkt


def check(ret, operation):
    if ret != 0:
        raise vkt.UserError(f"SAP2000 failed: {operation} ({ret})")


def create_member():
    with vkt.sap2000.connect(timeout=60) as sap:
        check(sap.InitializeNewModel(vkt.sap2000.eUnits.kN_m_C), "InitializeNewModel")
        check(sap.File.NewBlank(), "File.NewBlank")
        [name, ret] = sap.FrameObj.AddByCoord(0, 0, 0, 6, 0, 0, "", "Default", "B1")
        check(ret, "FrameObj.AddByCoord")
        return name
```

## Work with an open model

```python
import viktor as vkt


def read_frame_points(frame_name: str) -> tuple[str, str]:
    try:
        with vkt.sap2000.attach(timeout=60) as sap:
            point_i, point_j, ret = sap.FrameObj.GetPoints(frame_name, "", "")
            if ret != 0:
                raise vkt.UserError(f"SAP2000 could not read frame {frame_name} ({ret}).")
            return point_i, point_j
    except vkt.errors.WorkerSessionAttachError as error:
        raise vkt.UserError("Open the SAP2000 model and start its personal worker, then try again.") from error
```

For a box culvert, build and validate geometry and loads locally first. Use `connect()` for a new app-owned model, or `attach()` only when the engineer explicitly selects an open model. For a blank-model workflow, check all relevant object families and the lock state before writing. If a write fails, report that a partial model can remain and require inspection before retrying. Validate result coverage and units before displaying results.
