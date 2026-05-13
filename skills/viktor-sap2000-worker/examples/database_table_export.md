# Example: Export CSI Database Tables

Use this when a worker should retrieve display tables such as frame forces, joint displacements, or base reactions without writing a dedicated `Results.*` parser for each table.

This is additive. Keep direct helpers such as `get_frame_forces` for typed calculation contracts, and use database tables for configurable exports or user-requested tables.

```python
from csi_comtypes_helpers import CsiComSession, run_analysis
from csi_database_tables import get_database_tables


requests = [
    {
        "name": "frame_forces",
        "load_cases": ["DEAD"],
        "load_combinations": ["ULS1"],
        "group_name": "",
    },
    {
        "table_key": "Joint Displacements",
        "load_cases": ["DEAD"],
        "group_name": "",
        "numeric_columns": ["U1", "U2", "U3", "R1", "R2", "R3"],
    },
]

with CsiComSession(product="sap2000", attach_to_active=True) as csi:
    run_analysis(csi.model)
    tables = get_database_tables(csi.model, requests)

output = {
    "status": "ok",
    "database_tables": tables,
    "warnings": [],
}
```

The same helper can be used with ETABS:

```python
with CsiComSession(product="etabs", attach_to_active=True) as csi:
    tables = get_database_tables(
        csi.model,
        [{"name": "base_reactions", "load_combinations": ["COMB1"]}],
    )
```

Each table contains:

```json
{
  "table_key": "Element Forces - Frames",
  "group_name": "",
  "columns": ["Frame", "OutputCase", "StepType", "P", "V2", "V3", "T", "M2", "M3"],
  "rows": [["1", "DEAD", "", "10.0", "0.0", "0.0", "0.0", "5.0", "0.0"]],
  "records": [
    {
      "Frame": "1",
      "OutputCase": "DEAD",
      "StepType": "",
      "P": 10.0,
      "V2": 0.0,
      "V3": 0.0,
      "T": 0.0,
      "M2": 5.0,
      "M3": 0.0
    }
  ]
}
```
