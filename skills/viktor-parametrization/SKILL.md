---
name: viktor-parametrization
description: Use when the user wants to add or fix VIKTOR app inputs. VIKTOR inputs are declared in a Python `Parametrization` class and become the app UI, so this skill helps choose fields, organize sections, pages, tabs, steps, tables, defaults, validators, and `params` access paths correctly.
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
