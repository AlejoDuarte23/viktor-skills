---
name: viktor-etabs-worker
description: Use when the user wants a VIKTOR app to run ETABS through a VIKTOR worker on a Windows machine or server. VIKTOR cloud apps cannot directly automate local CSI desktop software, so this skill covers `vkt.etabs.ETABSAnalysis`, the inherited `PythonAnalysis` worker pattern, ETABS local execution assumptions, JSON input and output files, CSI OAPI automation with `comtypes`, launching or attaching to ETABS, result extraction, error handling, requirements, and testing.
---

# VIKTOR ETABS Worker

Use this skill only when ETABS automation through a VIKTOR worker is required.

Do not use this skill for STAAD.Pro. Use `../viktor-staad-pro-worker/SKILL.md` for STAAD/OpenSTAAD work. Use `../viktor-sap2000-worker/SKILL.md` for SAP2000-specific worker code.

## Workflow

1. Load the VIKTOR core trio first: `../viktor-core/SKILL.md`, `../viktor-parametrization/SKILL.md`, and `../viktor-styling/SKILL.md`.
2. Load `../viktor-geometry-view/SKILL.md` when the app previews the ETABS model geometry.
3. Load `../viktor-table-data-view/SKILL.md` when the app returns base reactions, joint reactions, frame forces, or summary tables.
4. Configure `viktor.config.toml` with `worker_integrations = ["etabs"]`.
5. Use `vkt.etabs.ETABSAnalysis` from the controller for ETABS worker execution. It follows the `PythonAnalysis` script-and-file transfer pattern, but is the ETABS-specific integration.
6. Serialize user inputs and generated model data to JSON, usually as `inputs.json`.
7. Send `run_etabs_model.py` plus input files to the worker with explicit `output_filenames`, usually `["output.json"]`.
8. In the worker script, read files from `Path.cwd()`, start or attach to ETABS with the CSI OAPI through `comtypes`, build or update the model, run the analysis, extract results, and write JSON output.
9. In the controller, read the worker output, validate its schema, and return `TableResult`, `DataResult`, `GeometryResult`, or files for download.
10. Convert worker, license, timeout, missing-file, and malformed-output failures into clear user-facing errors.

## Load When Needed

- Read [reference.md](reference.md) for the full ETABS worker integration reference.
- Read [examples.md](examples.md) for controller, worker, output-contract, and test examples.
For shared SAP2000/ETABS `comtypes` helpers, see `../viktor-sap2000-worker/scripts/csi_comtypes_helpers.py`.
