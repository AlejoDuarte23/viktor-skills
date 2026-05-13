---
name: viktor-cli-config
description: Use when the user needs to set up, run, test, publish, or configure a VIKTOR app from the command line. VIKTOR apps are Python apps that rely on `viktor-cli`, `viktor.config.toml`, and `requirements.txt`, so this skill helps choose app type, dependency pins, Python and system packages, local isolation mode, and safe CLI commands.
---

# VIKTOR CLI Config

Use this skill when a task touches VIKTOR local development, CLI commands, app configuration, or dependency setup.

## Workflow

1. Confirm the app has `app.py` or `app/__init__.py`, `requirements.txt`, and `viktor.config.toml`.
2. Choose `app_type` deliberately: `editor` for one unsaved session, `simple` for one shared entity type, or `tree` for a hierarchy of entity types.
3. Put Python dependencies in `requirements.txt` and pin versions when stability matters.
4. Put non-Python Linux system dependencies in `packages` inside `viktor.config.toml`.
5. Use `viktor-cli configure`, `check-system`, `install`, `start`, `run`, `test`, and `publish` according to the development stage.
6. Re-run `viktor-cli install` after changing `requirements.txt`.

## Load When Needed

- Read [reference.md](reference.md) for config keys, app types, dependency rules, CLI commands, and publishing notes.
- Read [examples.md](examples.md) for `viktor.config.toml`, `requirements.txt`, local development, and publish command patterns.
