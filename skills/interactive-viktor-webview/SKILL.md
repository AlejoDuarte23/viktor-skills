---
name: interactive-viktor-webview
description: Build VIKTOR WebViews where users edit values in HTML or JavaScript and send those values back into VIKTOR params with the VIKTOR JavaScript SDK. Use for editable tables, form builders, canvas editors, parameter grids, and other client-side editing UIs that standard VIKTOR parametrization fields cannot express.
---

# Interactive VIKTOR WebView

Use this skill when a VIKTOR WebView needs browser-side editing that round-trips back into app params with `viktorSdk.sendParams(...)`.

This is the user-driven complement to agent-driven Storage toggles. Use this when the browser writes params. Use a Storage-based pattern when a server-side agent tool should show, hide, or update a view without browser input.

## Workflow

1. Load `../viktor-webview/SKILL.md` first when the general `WebView`, `WebResult`, or WebView asset pattern is unclear.
2. Prefer native parametrization fields such as `NumberField`, `OptionField`, and `Table` when they can express the UI.
3. Add hidden receiving fields to `Parametrization`, usually `TextField(visible=False)` for scalar values and `TextAreaField(visible=False)` for JSON blobs.
4. In the controller, read the hidden fields from `params`, parse and validate them, and inject the current state into the HTML as escaped JSON.
5. In the HTML, load the VIKTOR JavaScript SDK from `VIKTOR_JS_SDK_PATH + "v1.js"`.
6. Send edited values back with `viktorSdk.sendParams(values, true)` when immediate saves are desired, or omit `true` when the user should confirm.
7. Handle the returned JavaScript `Promise` with `.then(...)` and `.catch(...)` so the user sees save status.
8. Re-read the hidden params in normal VIKTOR views or compute methods and convert the JSON/string values back into typed Python data.
9. Keep all dynamic HTML injection safe: use `json.dumps`, escape `</`, and do not interpolate user-provided HTML.

## Load When Needed

- Read [reference.md](reference.md) for architecture, field-path rules, serialization, SDK loading, sandbox constraints, and gotchas.
- Read [examples.md](examples.md) for a copyable editable load-table WebView with hidden JSON params and a downstream `DataView`.
