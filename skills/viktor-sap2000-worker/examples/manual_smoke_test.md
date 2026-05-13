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
