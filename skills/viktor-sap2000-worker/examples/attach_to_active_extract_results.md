# Example: Attach To Active SAP2000 And Extract Results

Use attach mode when SAP2000 is already open and the user wants to inspect the running model.

Before running:

1. Open SAP2000.
2. Open the model.
3. Use `Tools -> Set as active instance for API`.
4. Run Python with the same permission level as SAP2000.

```python
from __future__ import annotations

import json
from pathlib import Path

from csi_comtypes_helpers import (
    CsiComSession,
    get_frame_forces,
    get_frame_names,
    get_load_case_names,
    get_load_combo_names,
    get_support_nodes,
    get_support_reactions,
)


OUTPUT_PATH = Path.cwd() / "output.json"


with CsiComSession(product="sap2000", attach_to_active=True) as csi:
    model = csi.model
    supports = get_support_nodes(model)
    result_names = get_load_combo_names(model) or get_load_case_names(model)
    frame_names = get_frame_names(model)

    output = {
        "status": "ok",
        "units": {"length": "m", "force": "kN", "moment": "kN m"},
        "support_nodes": supports,
        "joint_reactions": get_support_reactions(model, supports, result_names),
        "frame_forces": get_frame_forces(model, frame_names, result_names),
        "warnings": [],
    }

with OUTPUT_PATH.open("w", encoding="utf-8") as jsonfile:
    json.dump(output, jsonfile, indent=2)
```
