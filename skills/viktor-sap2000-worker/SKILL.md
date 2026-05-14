---
name: viktor-sap2000-worker
description: Use when a VIKTOR app needs SAP2000 automation through a Windows VIKTOR worker using CSI OAPI with comtypes. Covers SAP2000Analysis worker orchestration, JSON input/output contracts, attach or launch flows, reusable comtypes helper functions, DatabaseTables exports, and examples for retrieving main SAP2000 results or creating/opening models.
---

# VIKTOR SAP2000 Worker

Use this skill when a VIKTOR app needs SAP2000 automation through a VIKTOR worker.

Do not automate SAP2000 directly from VIKTOR controller code. The controller starts the worker job, sends files, and reads outputs. The worker script uses `comtypes` to attach to or launch SAP2000.

## Core Rules

- Use `vkt.sap2000.SAP2000Analysis` for SAP2000 worker jobs.
- Keep CSI COM automation inside worker scripts.
- Use `comtypes`; do not use `win32com`, `VARIANT`, or `EnsureDispatch` for new code.
- Read worker inputs from `Path.cwd()`.
- Write declared outputs, usually `output.json`, to `Path.cwd()`.
- Use explicit JSON contracts for inputs and outputs.
- Keep units explicit in params, payloads, and result headers.
- Check CSI return codes.
- Parse CSI tuple/list outputs defensively because return order and compact return shapes can differ across wrappers and versions.
- Ground every direct `comtypes` call with its input arguments, accepted raw output shapes, and normalized helper output.
- Preserve multi-row CSI results as lists and validate result-array lengths against `NumberResults`; never collapse reactions or time-step results to the first row.
- Close SAP2000 only when the worker launched it.
- Mock worker execution in tests; manually test SAP2000 on the Windows worker.

## Load Order

1. Read `reference.md` for architecture, JSON contracts, attach/launch patterns, error handling, result families, and CSI return parsing.
2. Reuse `scripts/csi_comtypes_helpers.py` when a worker needs SAP2000 or ETABS session helpers and result helpers.
3. Use `scripts/csi_database_tables.py` when a worker should export CSI display tables through `SapModel.DatabaseTables`.
4. Use `scripts/csi_output_types.py` for typed output contracts with `Annotated[...]` fields and no default assignments.
5. Read only the examples needed for the task:
   - `examples/controller_worker_call.md`
   - `examples/full_worker_extract_main_results.md`
   - `examples/attach_to_active_extract_results.md`
   - `examples/launch_new_model.md`
   - `examples/manual_smoke_test.md`

## Worker Pattern

The controller or harness should orchestrate:

1. Build `inputs.json`.
2. Send the worker script and helper files.
3. Run `SAP2000Analysis`.
4. Fetch `output.json`.
5. Validate `status`.
6. Convert output data into VIKTOR views, downloads, or tables.

The worker script should perform SAP2000 tasks:

1. Attach to an active model or launch SAP2000.
2. Optionally open or create a model.
3. Optionally run analysis.
4. Retrieve requested data.
5. Write normalized JSON output.

## Preferred Helper

Use `CsiComSession` from `scripts/csi_comtypes_helpers.py`:

```python
from csi_comtypes_helpers import CsiComSession

with CsiComSession(
    product="sap2000",
    attach_to_active=True,
    program_path=None,
) as csi:
    model = csi.model
```

Use helper functions for common operations:

```python
get_point_names(model)
get_frame_names(model)
get_point_coords(model, point_name)
get_support_nodes(model)
get_load_case_names(model)
get_load_combo_names(model)
run_analysis(model)
get_support_reactions(model, supports, result_names)
get_joint_displacements(model, point_names, result_names)
get_frame_forces(model, frame_names, result_names)
get_base_reactions(model, result_names)
get_modal_periods(model, modal_result_names)
get_database_tables(model, table_requests)
```

## Example Tasks This Skill Supports

- Attach to an already running SAP2000 model.
- Launch a new SAP2000 instance by executable path.
- Launch SAP2000 by registered ProgID.
- Open an existing `.sdb` model.
- Create a new blank model.
- Get node coordinates.
- Get frame names and connectivity.
- Get supports.
- Get load cases.
- Get load combinations.
- Get joint reactions.
- Get joint displacements.
- Get frame internal forces: `P`, `V2`, `V3`, `T`, `M2`, `M3`.
- Get base reactions.
- Get modal periods.
- Export CSI database display tables such as frame forces, joint displacements, and base reactions.
- Run analysis before extraction.
- Return results to a VIKTOR table, JSON file, or downloadable file.
