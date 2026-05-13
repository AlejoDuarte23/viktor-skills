---
name: viktor-sdk-api
description: Use when the user needs VIKTOR Python code that reads, navigates, creates, modifies, or computes with VIKTOR entities through `vkt.api_v1.API`. VIKTOR is a platform for engineering web apps; the SDK API is its Python interface for workspace, entity, revision, file, and computation operations.
---

# VIKTOR SDK API

Use this skill for Python API access to VIKTOR data. Load `../viktor-core/SKILL.md` first when the code lives inside a VIKTOR app.

## Workflow

1. Decide whether the call runs inside the current workspace, cross-workspace, or from an external script.
2. Instantiate `vkt.api_v1.API()` with no token inside the current workspace, or with a Personal Access Token for cross-workspace/external use.
3. Start from a workspace, entity ID, root entities, entity type, or an entity field.
4. Use entity methods such as `parent()`, `children()`, `siblings()`, `get_revisions()`, `get_file()`, and `compute()`.
5. Use `include_params=False` when only entity identity/type data is needed.
6. Enable and use privileged API access only when permissions are intentionally bypassed and the app has been reviewed for data leakage.

## Load When Needed

- Read [reference.md](reference.md) for access modes, navigation, entity data, mutation, list objects, and computation rules.
- Read [examples.md](examples.md) for app callbacks, cross-workspace reads, entity updates, and remote computations.
