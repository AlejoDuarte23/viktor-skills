---
name: agent-toggle-viktor-view
description: Show or hide a VIKTOR view from a server-side LLM agent tool by writing a flag to `vkt.Storage` and reading it from the view `visible=` callback. Use when a chat agent must reveal or hide a WebView, DataView, TableView, or GeometryView panel as a side effect of a tool call.
---

# Agent Toggle VIKTOR View

Use this skill when a server-side agent tool should make a VIKTOR view appear or disappear.

Do not use this pattern for normal user-driven visibility. If a native field can drive the view, use `visible=vkt.Lookup("field")` or a `visible=` callback that reads `params`. Use this Storage pattern when the trigger is a tool call that runs on the server.

## Workflow

1. Load `../storage-tool/SKILL.md` when the app also needs broader workflow Storage handoffs.
2. Define a stable Storage key for the view visibility flag.
3. Write `"show"` or `"hide"` to `vkt.Storage` from an agent tool.
4. Read the same key and scope in the view's `visible=` callback.
5. Return a plain `bool` from the callback.
6. Catch only expected missing-key errors in the callback; let real type errors surface during development.
7. Reset stale visibility state when the chat/session should start clean.
8. Register the tool in the agent tool registry and describe when the agent should call it.

## Load When Needed

- Read [reference.md](reference.md) for the Storage visibility model, refresh behavior, gotchas, and reset rules.
- Read [examples.md](examples.md) for a copyable visibility callback, VIKTOR view, and Agents SDK tool.
