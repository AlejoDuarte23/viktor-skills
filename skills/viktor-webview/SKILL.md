---
name: viktor-webview
description: Use when the user wants a VIKTOR app to render custom HTML, CSS, JavaScript, interactive dashboards, canvas tools, Plotly or browser-library visualizations, or WebView interactions that send values back to the VIKTOR parametrization with `WebView`, `WebResult`, `WebAndDataView`, or the VIKTOR JavaScript SDK.
---

# VIKTOR WebView

Use this skill when a VIKTOR result needs browser-native HTML instead of a standard VIKTOR `PlotlyView`, `TableView`, `GeometryView`, or image/PDF view.

## Workflow

1. Load the VIKTOR core skill first if the app skeleton, `Parametrization`, or `Controller` pattern is unclear.
2. Choose `WebView` with `WebResult` for a full custom web surface.
3. Prefer `PlotlyView` for ordinary Plotly charts; choose `WebView` for Plotly only when JavaScript event handling, custom controls, filtering, or `viktorSdk.sendParams` is needed.
4. Decide the HTML source:
   - `WebResult(url=...)` for an external live page.
   - `WebResult.from_path(path)` for static local HTML.
   - `WebResult(html=html_text)` for generated or templated HTML.
5. Keep complex HTML/CSS/JS in separate `.html` files and inject only sanitized JSON data, asset paths, and the VIKTOR JavaScript SDK URL from Python.
6. Use the documented VIKTOR JavaScript SDK bridge only for sending serialized values back to parametrization fields: `viktorSdk.sendParams(values)` or `viktorSdk.sendParams(values, true)`.
7. Treat all dynamic HTML values as untrusted. Encode data with `json.dumps`, escape text, avoid interpolating user-provided HTML, and be deliberate about CDN dependencies.
8. Test decorated `WebView` and `WebAndDataView` methods with `viktor.testing.mock_View`.

## Load When Needed

- Read [reference.md](reference.md) for API signatures, source notes, asset handling, communication rules, and security caveats.
- Read [examples.md](examples.md) for practical static, dynamic, Plotly, canvas, table-update, and test patterns.

