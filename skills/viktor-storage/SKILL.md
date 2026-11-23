---
name: viktor-storage
description: Cache slow VIKTOR calculations with memoize or store results across jobs with vkt.Storage. Use for storage scopes, files, cross-entity access, or filling fields and WebViews from stored results.
---

# VIKTOR Storage

Use this skill when a VIKTOR app needs results or intermediate files to survive beyond one job, be shared between views/buttons, or avoid rerunning expensive computations.

## Workflow

1. Load `../viktor-core/SKILL.md` first for controller, view, job, and stateless-app conventions.
2. Choose `vkt.Storage` when the data should be explicitly stored under a key as a `vkt.File`.
3. Choose `vkt.memoize` only for temporary caching of a pure, serializable function call.
4. Always pass an explicit `scope`: `entity`, `workspace`, or `session`.
5. Prefer `scope="entity"` for results tied to one saved entity, long-running analysis outputs, parsed files, or workflow state.
6. Use `scope="workspace"` only for app-wide shared state, shared templates, shared reference data, or durable caches where overwriting by another entity is acceptable.
7. Use `scope="session"` for editor-session state, temporary previews, or per-user ephemeral state. This scope requires VIKTOR SDK `>=14.28.0`.
8. Store structured payloads as JSON with `vkt.File.from_data(json.dumps(...))`; read them with `getvalue_binary().decode("utf-8")`.
9. Catch `FileNotFoundError` for optional cached data and return a recoverable response, empty result, or user-facing instruction to run the producer job first.
10. Use `viktor.testing.mock_Storage` when local tests execute storage reads or writes.

## Related Skills

- Load `../viktor-testing/SKILL.md` when adding or fixing tests for storage-backed code.
- Load `../storage-tool/SKILL.md` only for agentic workflow handoffs, graph state, optimization studies, or storage-controlled WebViews.
- Load `../viktor-sdk-api/SKILL.md` when cross-entity storage access requires resolving a target entity through `vkt.api_v1.API`.

## Load When Needed

- Read [reference.md](reference.md) for storage operations, scope selection, JSON helpers, cross-entity access, memoize rules, and testing notes.
- Read [long-running-results.md](long-running-results.md) to choose a cache or storage pattern, fill params from a stored run, and reuse results in views and WebViews.
- Read [examples.md](examples.md) for compact copyable storage, visibility, and test snippets.
