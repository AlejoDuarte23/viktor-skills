---
name: viktor-staad-pro-worker
description: Use when the user wants a VIKTOR app to run STAAD.Pro or OpenSTAAD on a user's Windows machine. VIKTOR cloud apps cannot directly automate local desktop engineering software, so this skill covers `PythonAnalysis`, worker scripts, JSON input and output files, STAAD model generation, analysis execution, and result return to VIKTOR.
---

# VIKTOR STAAD.Pro Worker

Use this skill only when STAAD.Pro or OpenSTAAD automation is required.

## Workflow

1. Load the VIKTOR core trio first.
2. Use `viktor.external.python.PythonAnalysis` from the controller to run a worker script.
3. Serialize user inputs and model data to JSON.
4. Let the worker script create or modify the STAAD model on the user's computer.
5. Run analysis, extract results, and write a JSON output file.
6. Read the worker output in VIKTOR and return `TableResult`, `DataResult`, or `GeometryResult`.
7. Keep STAAD axis conventions explicit; STAAD commonly uses Y as vertical, while VIKTOR geometry defaults to Z as vertical.

## Load When Needed

- Read [reference.md](reference.md) for the full worker and OpenSTAAD reference.
- Read [examples.md](examples.md) for practical worker flow examples.
