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
3. Add hidden receiving fields to `Parametrization`. Match each scalar to its field type, such as `IntegerField(visible=False)` for a whole-number dimension. Use `TextAreaField(visible=False)` for JSON strings.
4. In the controller, read the hidden fields from `params`, parse and validate them, and inject the current state into the HTML as escaped JSON.
5. Load the VIKTOR JavaScript SDK from `VIKTOR_JS_SDK_PATH + "v1.js"` with a script tag in the HTML head.
6. Call `viktorSdk.sendParams(values)` from a button click. Pass `true` as the second argument only to skip the confirmation dialog.
7. Treat the call as a request to update the editor. The SDK returns no confirmation. Verify the field values in the VIKTOR editor and in the next calculation.
8. Re-read the hidden params in normal VIKTOR views or compute methods and convert the JSON/string values back into typed Python data.
9. Keep all dynamic HTML injection safe: use `json.dumps`, escape `</`, and do not interpolate user-provided HTML.

## Load When Needed

- Read [reference.md](reference.md) for architecture, field-path rules, serialization, SDK loading, sandbox constraints, and gotchas.
- Read [examples.md](examples.md) for a copyable editable load-table WebView with hidden JSON params and a downstream `DataView`.
- Load [Three.js Dynamic UI](../threejs-dynamic-ui/SKILL.md) for custom 3D scenes, OrbitControls, and a right-side geometry panel that updates hidden numeric fields.
- Read `../viktor-storage/long-running-results.md` when Python stores the result and the browser updates only a selection or other small editor state.
