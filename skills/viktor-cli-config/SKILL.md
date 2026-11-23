---
name: viktor-cli-config
description: Use when creating, configuring, running, debugging, testing, or publishing a VIKTOR app with viktor-cli. Covers registered app names, dependencies, development sessions, logs, workspace resets, and publication.
---

# VIKTOR CLI Config

Use this skill for VIKTOR local development, configuration, CLI commands, and dependency setup.

## Workflow

1. Check `app.py` or `app/__init__.py`, `requirements.txt`, and `viktor.config.toml`. Read `app_type` and `registered_name`; check the configured account and `viktor-cli apps` when needed.
2. If the platform app does not exist and creation is part of the task, run `viktor-cli create-app "<App Name>" --registered-name <registered-name>`. Use `--init --app-type <editor|simple|tree>` only when starter files are needed. Check the actual returned registered name; a collision may add a suffix. Align the config with the intended app.
3. Check CLI availability and credentials without printing tokens. If setup is missing, guide the user through `viktor-cli configure` and `viktor-cli check-system`.
4. For an existing installation, try `viktor-cli start`. If dependencies are missing or changed, run `viktor-cli install` and then `viktor-cli start`. Diagnose the error before retrying.
5. `clean-start` includes `clear`, which deletes entities and entity types from the development workspace. Use it for a confirmed new, empty workspace; otherwise ask before clearing existing or unknown data. Do not use it as an automatic fallback after a failed start.
6. Keep `start` running in a terminal session whose output the agent can read. Report the development URL, reproduce the action in the browser or ask the user to do it, and inspect new terminal output. A session must remain alive for the app to stay connected. Check VIKTOR Desktop separately for worker logs.
7. Run appropriate tests and fix observed issues. When ready, ask the user before `viktor-cli publish` unless publication was already authorized. Confirm the app, version target, and whether committed files or `--use-filesystem` will be published.

Use `requirements.txt` for Python packages and `packages` in `viktor.config.toml` for Linux system dependencies. `python_version` controls published builds; local venv Python is configured by the CLI.

## Load when needed

- Read [reference.md](reference.md) for configuration, commands, logging, workspace data, and publishing.
- Read [examples.md](examples.md) for setup, development, and publish examples.
