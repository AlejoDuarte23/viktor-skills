# ETABS Connect Examples

## Start a fresh model

```python
import viktor as vkt


def check(ret, operation):
    if ret != 0:
        raise vkt.UserError(f"ETABS failed: {operation} ({ret})")


def create_member():
    with vkt.etabs.connect(timeout=60) as sap:
        check(sap.InitializeNewModel(vkt.etabs.eUnits.kN_m_C), "InitializeNewModel")
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
        with vkt.etabs.attach(timeout=60) as sap:
            point_i, point_j, ret = sap.FrameObj.GetPoints(frame_name, "", "")
            if ret != 0:
                raise vkt.UserError(f"ETABS could not read frame {frame_name} ({ret}).")
            return point_i, point_j
    except vkt.errors.WorkerSessionAttachError as error:
        raise vkt.UserError("Open the ETABS model and start its personal worker, then try again.") from error
```

For a beam and column design app, read frame geometry and results in the attached session, preserve load-case and unit labels, then calculate or draw details in separate steps. Do not assume the attached model is blank.
