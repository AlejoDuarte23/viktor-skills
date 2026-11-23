---
name: viktor-parametrization
description: Build or fix VIKTOR app inputs, including fields, tables, pages, validation, and params paths. Use for SetParamsButton updates and HiddenField state.
---

# VIKTOR Parametrization

Use this skill whenever a VIKTOR task touches user inputs.

## Workflow

1. Start from the app structure in `../viktor-core/SKILL.md`.
2. Choose the narrowest input type that matches the user intent.
3. Add defaults, min/max values, units, suffixes, descriptions, and variants where they improve correctness.
4. Use `vkt.Section`, `vkt.Step`, `vkt.Page`, `vkt.Tab`, and `vkt.Table` only when the workflow needs that structure.
5. Keep field names stable and readable because they become `params` paths.
6. Load `../viktor-styling/SKILL.md` before writing long descriptions, Markdown, or equations.

## Load When Needed

- Read [reference.md](reference.md) for input field signatures and options.
- Read [examples.md](examples.md) for common input layouts and validation patterns.
- Read `../viktor-storage/long-running-results.md` when a `SetParamsButton` must fill fields from stored data or keep a result ID in a `HiddenField`.
