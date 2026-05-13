---
name: viktor-cli-config
description: Use when the user needs to create, set up, run, test, publish, or configure a VIKTOR app from the command line. VIKTOR apps are Python apps that rely on `viktor-cli`, `viktor.config.toml`, and `requirements.txt`, so this skill helps choose app type, registered app name, dependency pins, Python and system packages, local isolation mode, create-app, clean-start, install, start, test, run, and publish commands.
---

# VIKTOR CLI Config

Use this skill when a task touches VIKTOR local development, CLI commands, app configuration, or dependency setup.

## Workflow

1. If the app does not exist yet, either scaffold it with `viktor-cli create-app "<App Name>" --init --registered-name <registered-name> --app-type <editor|simple|tree>` or manually create the local files first.
2. Confirm the app has `app.py` or `app/__init__.py`, `requirements.txt`, and `viktor.config.toml`.
3. When creating manually from scratch, write `viktor.config.toml` with `app_type`, `python_version`, and `registered_name`, create the platform app with `viktor-cli create-app "<App Name>" --registered-name <registered-name>`, then run `viktor-cli install` or `viktor-cli clean-start`.
4. Choose `app_type` deliberately: `editor` for one unsaved session, `simple` for one shared entity type, or `tree` for a hierarchy of entity types.
5. Keep `registered_name` in `viktor.config.toml` aligned with the registered app name used by `create-app`, `start`, and `publish`.
6. Put Python dependencies in `requirements.txt` and pin versions when stability matters.
7. Put non-Python Linux system dependencies in `packages` inside `viktor.config.toml`.
8. Use `viktor-cli clean-start` for the first clean local install and launch of an app.
9. Re-run `viktor-cli install` after changing `requirements.txt` or adding Python packages.
10. Use `viktor-cli start`, `run`, `test`, and `publish` according to the development stage. Prefer relying on `registered_name` from the config, or pass the same name with `--registered-name` when being explicit.

### First-Run Example

When local files already exist but the platform app has not been registered yet, do this before `start`:

```bash
viktor-cli create-app "SAP2000 Model Reader" --registered-name sap2000-reader-app
```

Confirm `viktor.config.toml` contains the same registered name:

```toml
registered_name = "sap2000-reader-app"
```

Then launch with a clean install and give the user the app URL printed by the CLI:

```bash
viktor-cli clean-start
```

## Load When Needed

- Read [reference.md](reference.md) for config keys, app types, registered app names, dependency rules, CLI commands, and publishing notes.
- Read [examples.md](examples.md) for app creation, `viktor.config.toml`, `requirements.txt`, local development, and publish command patterns.
