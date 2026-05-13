---
name: viktor-file-management
description: Use when the user needs a VIKTOR app to upload, parse, validate, generate, or download files. VIKTOR file workflows use `FileField`, `MultiFileField`, `FileResource`, `ParamsFromFile`, `DownloadButton`, and `DownloadResult`, so this skill helps connect user-selected files to controller logic and return generated files from the app.
---

# VIKTOR File Management

Use this skill when a VIKTOR app reads user-uploaded files or offers generated files for download.

## Workflow

1. Load `../viktor-core/SKILL.md` and `../viktor-parametrization/SKILL.md` first.
2. Prefer `FileField` or `MultiFileField` for files attached to the current entity.
3. Use a file-like entity type with `@vkt.ParamsFromFile` only when the file should be its own entity with its own views or parsed fields.
4. Access uploaded field files through the `FileResource`: use `.file` for the `vkt.File` and `.filename` for the selected name.
5. Restrict upload size and extensions with `max_size` and `file_types` when the workflow expects known formats.
6. Add `DownloadButton` plus a controller method returning `DownloadResult` for generated downloads.
7. For multiple generated files, return a zip with `DownloadResult(zipped_files=..., file_name=...)`.

## Load When Needed

- Read [reference.md](reference.md) for upload choices, `FileResource`, `ParamsFromFile`, restrictions, and download behavior.
- Read [examples.md](examples.md) for CSV upload, parsed file entity, single download, and zipped download patterns.
