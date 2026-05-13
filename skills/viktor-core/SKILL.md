---
name: viktor-core
description: Use when the user wants to create, fix, or understand the base structure of a VIKTOR app. VIKTOR is a Python platform for engineering web apps, so this skill covers the app folder, `Parametrization`, `Controller`, views, results, validation errors, and the minimum code shape needed before adding domain-specific features.
---

# VIKTOR Core

Use this skill before writing or reviewing any VIKTOR app code.

## Workflow

1. Confirm the app has the VIKTOR basics: `app.py`, `requirements.txt`, and `viktor.config.toml`.
2. Define a `Parametrization` class for user inputs.
3. Define a `Controller` class and set `parametrization = Parametrization`.
4. Choose view decorators and result classes that match the requested output.
5. Use `vkt.UserError` for user-correctable input problems.
6. Load specialized skills only after the core structure is clear.

## Load When Needed

- Read [reference.md](reference.md) for controller patterns, view decorators, layout containers, and result classes.
- Read [examples.md](examples.md) for minimal app, view, and validation examples.

For input details, load `../viktor-parametrization/SKILL.md`.
For app text and equations, load `../viktor-styling/SKILL.md`.
