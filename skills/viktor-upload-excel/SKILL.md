---
name: viktor-upload-excel
description: Use when the user wants a VIKTOR app to upload, parse, preview, or calculate from Excel files. VIKTOR `FileField` values are `vkt.File` objects, so this skill covers `getvalue_binary()`, pandas, openpyxl, validation, requirements, and table previews.
---

# VIKTOR Upload Excel

Use this skill when a VIKTOR app reads `.xlsx` files.

## Workflow

1. Load the VIKTOR core trio first.
2. Add a `vkt.FileField` with `file_types=[".xlsx"]`.
3. Add `pandas` and `openpyxl` to `requirements.txt`.
4. Read uploaded Excel bytes with `file.getvalue_binary()`.
5. Parse with `pandas.read_excel(..., engine="openpyxl")`.
6. Validate missing files and invalid sheets with user-facing errors.
7. Use `../viktor-table-data-view/SKILL.md` for preview tables.

## Load When Needed

- Read [reference.md](reference.md) for the full upload and parsing pattern.
- Read [examples.md](examples.md) for a compact parser and preview view.
