# Example: Manual Worker Smoke Test

Run this on the Windows worker machine where SAP2000 is installed.

## Files To Copy Into A Temporary Folder

```text
run_sap2000_model.py
csi_comtypes_helpers.py
csi_output_types.py
inputs.json
```

## Install Worker Dependency

Install `comtypes` into the same Python executable selected during worker installation:

```powershell
C:\Path\To\python.exe -m pip install comtypes
```

## Active Instance Test

Open SAP2000, open a model, then use `Tools -> Set as active instance for API`.

Create `inputs.json`:

```json
{
  "attach_to_active": true,
  "program_path": "",
  "model_path": "",
  "save_model_path": "",
  "create_new_model": false,
  "run_analysis": false,
  "result_names": ["DEAD", "ULS1"],
  "modal_result_names": ["MODAL"],
  "extract": {
    "model_lists": true,
    "support_nodes": true,
    "joint_reactions": true,
    "joint_displacements": false,
    "frame_forces": true,
    "base_reactions": false,
    "modal_periods": false
  },
  "units": {
    "length": "m",
    "force": "kN",
    "moment": "kN m"
  }
}
```

Run:

```powershell
C:\Path\To\python.exe run_sap2000_model.py
type output.json
```

## Raw Comtypes Method Probe

Use this when a parser fails or a SAP2000/comtypes version returns a new shape. Run it in the same temporary folder and with the same Python executable as the worker.

```python
import comtypes
import comtypes.client


def first_sequence(raw):
    for value in raw:
        if isinstance(value, (list, tuple)):
            return value
    return []


comtypes.CoInitialize()
try:
    helper = comtypes.client.CreateObject("SAP2000v1.Helper")
    sap_object = helper.GetObject("CSI.SAP2000.API.SapObject")
    model = sap_object.SapModel

    point_names = model.PointObj.GetNameList(0, [])
    print("PointObj.GetNameList(0, []) ->", repr(point_names))

    names = first_sequence(point_names)
    first_point = str(names[0]) if names else "1"
    print("PointObj.GetCoordCartesian(point, 0, 0, 0) ->", repr(
        model.PointObj.GetCoordCartesian(first_point, 0, 0, 0)
    ))
    print("PointObj.GetRestraint(point, [0, 0, 0, 0, 0, 0]) ->", repr(
        model.PointObj.GetRestraint(first_point, [0, 0, 0, 0, 0, 0])
    ))

    frame_names = model.FrameObj.GetNameList(0, [])
    print("FrameObj.GetNameList(0, []) ->", repr(frame_names))
    frames = first_sequence(frame_names)
    if frames:
        first_frame = str(frames[0])
        print("FrameObj.GetPoints(frame, '', '') ->", repr(
            model.FrameObj.GetPoints(first_frame, "", "")
        ))
finally:
    comtypes.CoUninitialize()
```

Paste raw outputs into parser fixtures before changing helper code. Keep the exact method input arguments in the fixture name or test body.

## Launch Test

Create `inputs.json`:

```json
{
  "attach_to_active": false,
  "program_path": "C:\\Program Files\\Computers and Structures\\SAP2000 26\\SAP2000.exe",
  "model_path": "",
  "save_model_path": "created_model.sdb",
  "create_new_model": true,
  "run_analysis": false,
  "result_names": [],
  "modal_result_names": [],
  "extract": {
    "model_lists": true,
    "support_nodes": false,
    "joint_reactions": false,
    "joint_displacements": false,
    "frame_forces": false,
    "base_reactions": false,
    "modal_periods": false
  },
  "units": {
    "length": "m",
    "force": "kN",
    "moment": "kN m"
  }
}
```

Run:

```powershell
C:\Path\To\python.exe run_sap2000_model.py
type output.json
```
