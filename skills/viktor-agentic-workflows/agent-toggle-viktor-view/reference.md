# Agent Toggle VIKTOR View Reference

## Scope

Use this reference when an LLM agent or server-side tool should reveal or hide a VIKTOR view during a chat turn or other job.

This pattern is for server-side triggers:

- a chat agent generates a dashboard and shows a WebView
- a tool completes a calculation and reveals a DataView
- a tool hides a panel after reset

Use native parametrization visibility for user-driven toggles. Use `interactive-viktor-webview` when the browser needs to write params with `viktorSdk.sendParams(...)`.

## Data Flow

```text
Agent tool runs inside a VIKTOR job
  -> writes "show" or "hide" to vkt.Storage(scope="entity")
  -> chat/view/button job returns
  -> VIKTOR re-evaluates visible= callbacks
  -> callback reads the Storage flag
  -> view appears or disappears
```

The tool does not write params. It writes server-side Storage. The VIKTOR job boundary is what causes visibility callbacks to run again.

## Why Storage

Agent tools run on the server. They cannot directly write parametrization fields. Browser JavaScript can write params with `viktorSdk.sendParams(...)`, but a server-side tool needs a server-readable state channel.

`vkt.Storage(scope="entity")` is the usual channel for this because the flag belongs to the active entity.

## Visibility Callback Rules

- Read and write the same key.
- Read and write the same scope.
- Return `False` if the flag does not exist.
- Return `True` only when the stored value is exactly `"show"`.
- Keep callbacks defensive and fast.
- Do not decode text written with `vkt.File.from_data("show")`; use `.getvalue()`.

## Reset Rules

If a stale visible panel should not persist into a fresh chat session, delete the visibility key when the chat input/state is empty.

Prefer this behavior for agent-generated dashboards and one-off result panels. Keep the flag when the view should remain visible across sessions.

## Gotchas

- `File.getvalue()` returns text for data written with `vkt.File.from_data("show")`.
- Use `.getvalue_binary()` only for stored bytes or JSON payloads you decode yourself.
- Catch `FileNotFoundError` for a missing flag. Avoid broad `except Exception` unless the view must never fail.
- A bare `Storage().set()` does not refresh the browser by itself. A VIKTOR job must finish before the view state is re-evaluated.
- Agent tools cannot write params. Use `interactive-viktor-webview` for user-driven browser-to-param updates.
