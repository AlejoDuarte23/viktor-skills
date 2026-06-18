# VIKTOR Storage Tool Reference

## Scope

Use this reference when a VIKTOR-backed Agents SDK app needs entity-scoped Storage for workflow state, app-to-app handoffs, optimization studies, or storage-controlled view visibility.

Storage is best for payloads that should persist outside chat:

- upstream tool results
- downstream handoff payloads
- heavy WebView data
- visibility flags
- workflow graph state
- optimization study records

Do not store secrets in VIKTOR Storage.

## Storage Rules

- Use `scope="entity"` for workflow-local state.
- Store JSON with `vkt.File.from_data(json.dumps(payload, indent=2))`.
- Read JSON with `getvalue_binary().decode("utf-8")`.
- Store simple flags as `"show"` or `"hide"` and read them with `.getvalue()`.
- Keep data keys and visibility keys separate.
- Use stable, app-specific key constants.

## Handoff Pattern

Producer tools should:

1. Resolve the active workflow entity.
2. Read saved params if user inputs matter.
3. Compute the VIKTOR method.
4. Select a useful result key.
5. Write the selected payload to storage.
6. Return a compact status, summary, and storage key.

Consumer tools should:

1. Read required upstream storage.
2. Return `needs_prerequisite` if upstream storage is missing.
3. Map only necessary upstream values into downstream params.
4. Compute the downstream method.
5. Store downstream output.
6. Return a short summary and storage key.

## View Visibility Pattern

- Store view data under a data key.
- Store visibility under a separate `show_*` key.
- A show action should verify the data key exists before setting visibility.
- A hide action should usually leave the data in place.
- `visible=` callbacks should catch exceptions and return `False`.
- WebView methods should render a safe fallback page instead of raising when storage is missing.

## Reset Rules

Reset tools should require explicit confirmation:

```json
{
  "status": "confirmation_required",
  "message": "Set confirm=true to clear the active study."
}
```

Delete both data and visibility keys only when resetting the whole feature. Do not delete data for a simple hide action.

## Validation

Run checks appropriate to the target app:

```bash
python3 -m py_compile $(rg --files . -g '*.py')
xmllint --noout agent/system_prompt.xml
git diff --check
```
