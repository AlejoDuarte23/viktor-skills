# Example: Launch SAP2000, Create A New Blank Model, And Save

Use launch mode when the worker owns the SAP2000 process.

```python
from __future__ import annotations

import json
from pathlib import Path

from csi_comtypes_helpers import CsiComSession, initialize_new_blank_model, save_model_file


OUTPUT_PATH = Path.cwd() / "output.json"
SAVE_PATH = Path.cwd() / "created_model.sdb"
PROGRAM_PATH = r"C:\Program Files\Computers and Structures\SAP2000 26\SAP2000.exe"


with CsiComSession(
    product="sap2000",
    attach_to_active=False,
    program_path=PROGRAM_PATH,
) as csi:
    model = csi.model
    initialize_new_blank_model(model)
    save_model_file(model, SAVE_PATH)

output = {
    "status": "ok",
    "units": {"length": "m", "force": "kN", "moment": "kN m"},
    "saved_model_path": str(SAVE_PATH),
    "warnings": [],
}

with OUTPUT_PATH.open("w", encoding="utf-8") as jsonfile:
    json.dump(output, jsonfile, indent=2)
```

Launch by registered ProgID instead of program path:

```python
with CsiComSession(product="sap2000", attach_to_active=False) as csi:
    model = csi.model
    initialize_new_blank_model(model)
    save_model_file(model, Path.cwd() / "created_model.sdb")
```
