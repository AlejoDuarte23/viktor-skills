---
name: storage-tool
description: Implement VIKTOR Storage patterns for agentic workflow handoffs, graph state, optimization studies, and storage-controlled WebView visibility. Use when storing large VIKTOR tool outputs, reading prerequisites from entity-scoped storage, showing or hiding views with storage flags, or debugging VIKTOR Storage gotchas.
---

# VIKTOR Storage Tool

Use this skill when a VIKTOR-backed Agents SDK app needs storage-backed handoffs, persistent workflow state, optimization study state, or show/hide WebViews controlled by VIKTOR Storage.

This skill is self-contained. Read `reference.md` for implementation notes and `examples.md` for copyable templates before writing code.

## Components

Implement these components in the target app:

- `storage_helpers.py`: JSON read/write helpers, result-key selection, and compact data extraction helpers.
- `responses.py`: `needs_prerequisite`, `validation_error`, and `execution_error` JSON responses.
- producer tools: compute a VIKTOR method and store the useful result payload.
- consumer tools: read upstream storage, patch downstream params, compute, and store the next payload.
- view producer tools: store heavy view data and set a separate visibility flag.
- show/hide tools: write `show` or `hide` flags after validating required view data exists.
- `app.py`: `visible=` callbacks and WebViews that render from storage.
- optional graph state module: persist workflow graph state and visible checklist progress.

## Storage Rules

Use entity-scoped VIKTOR Storage for workflow-local state:

```python
vkt.Storage().set(
    key,
    data=vkt.File.from_data(json.dumps(payload, indent=2)),
    scope="entity",
)
```

Read JSON payloads with bytes decode:

```python
stored_file = vkt.Storage().get(key, scope="entity")
payload = json.loads(stored_file.getvalue_binary().decode("utf-8"))
```

Read simple flags with `.getvalue()`:

```python
visible = vkt.Storage().get(SHOW_KEY, scope="entity").getvalue() == "show"
```

## Handoff Pattern

Producer tools:

1. resolve the active workflow entity
2. call the live VIKTOR method
3. select the useful result key
4. write the selected payload to storage
5. return a compact summary and `storage_key`

Consumer tools:

1. expose only missing user inputs
2. read required upstream keys from storage
3. map only needed values into downstream params
4. call the downstream method
5. store the downstream payload
6. return a compact summary

If storage is missing, return `needs_prerequisite` with `missing_storage_key` and `retry_action.tool`.

## Show/Hide View Pattern

Keep heavy view payload and view visibility separate:

- data key: `foundation_moment_contours_plotly`
- visibility key: `show_foundation_moment_contours`

Producer view tool:

```python
write_json_to_storage(DATA_KEY, payload)
vkt.Storage().set(SHOW_KEY, data=vkt.File.from_data("show"), scope="entity")
```

Show/hide tool:

```python
class ShowHideViewArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["show", "hide"]
```

When `action=="show"`, verify the data key exists before setting the visibility flag. Hiding should usually keep the data.

## WebView Visibility

Use a defensive `visible=` callback:

- return `False` when chat/input state is empty
- optionally delete visibility state when chat is empty
- return `True` only when the visibility flag equals `show`
- verify the data payload exists when the view depends on it
- catch exceptions and return `False`

The WebView body should also catch exceptions and render an empty/fallback HTML page instead of raising.

## Workflow Graph State

Use storage for graph state when the graph should persist across chat turns:

- graph state key: `workflow_graph_state`
- graph state contains workflow nodes, edges, plan/todos, and optional hidden progress payload
- visible checklist progress should live in `WorkflowPlan.todos[*].status`
- update visible progress with plan update tools, not hidden progress payloads

If an app also writes pre-rendered HTML, make sure the controller actually reads that HTML. A stored HTML key does not matter if the WebView renders from graph state.

## Reset Rules

Reset tools should require explicit confirmation:

```json
{
  "status": "confirmation_required",
  "message": "Set confirm=true to clear the active study."
}
```

When confirmed, delete both data and visibility keys only when the reset is meant to clear the whole feature. A hide action should not delete data.

## Gotchas

- Always pass `scope="entity"` for workflow-local handoffs and UI state.
- Do not use storage for secrets.
- Store JSON with `vkt.File.from_data(...)`; read JSON with `getvalue_binary().decode("utf-8")`.
- Store simple visibility flags as `"show"` or `"hide"` and read with `.getvalue()`.
- A visibility flag is not the payload; validate both before showing.
- WebView visibility callbacks must not raise.
- Sequential optimization overwrites latest workflow outputs; record candidate snapshots before moving on.
- Tool outputs should be short; include storage keys, not full large payloads.
- Missing upstream storage is recoverable and should return `needs_prerequisite`.
- Clear visibility when chat state is empty if the view should reset with chat.

## Validation

Run checks appropriate to the target app:

```bash
python3 -m py_compile $(rg --files . -g '*.py')
xmllint --noout agent/system_prompt.xml
git diff --check
```
