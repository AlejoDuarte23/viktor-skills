# VIKTOR WebView Reference

## Sources

- VIKTOR docs, HTML web content: https://docs.viktor.ai/docs/create-apps/results-and-visualizations/html/
- VIKTOR SDK reference, views: https://docs.viktor.ai/sdk/api/views/
- VIKTOR Plotly docs: https://docs.viktor.ai/docs/create-apps/results-and-visualizations/plots-charts-graphs/
- VIKTOR blog, upgraded WebView: https://www.viktor.ai/blog/189/create-interactive-outputs-with-the-upgraded-web-view
- VIKTOR WebView examples repository: https://github.com/viktor-platform/WebView-examples

## When To Use WebView

Use `WebView` when the output must be a standalone HTML page with custom JavaScript, CSS, canvas, browser events, third-party JS libraries, or interactions that update the VIKTOR parametrization.

Do not default to `WebView` for normal charts. The VIKTOR docs recommend `PlotlyView` for standard Plotly visualizations. Use `WebView` with Plotly only when the app needs behavior that lives in the browser, such as clicking a point to populate fields, brushing/filtering data and sending rows to a VIKTOR `Table`, or custom UI controls around the chart.

The public WebView examples cover three useful patterns: drawing/editing canvas geometry and sending table rows back to VIKTOR, clicking a Plotly point to fill scalar fields, and filtering a Plotly parallel-coordinates chart to populate a VIKTOR table.

## Core Classes

```python
import viktor as vkt


class Controller(vkt.Controller):
    @vkt.WebView("Interactive output")
    def web_view(self, params, **kwargs):
        return vkt.WebResult(html="<html><body>Hello</body></html>")
```

### `WebView`

`WebView(label, duration_guess=None, *, description=None, update_label=None, visible=True, **kwargs)`

- `label`: tab label shown in the VIKTOR interface.
- `duration_guess`: optional in current SDK versions. Larger values add a manual refresh button for longer-running views.
- `description`: tooltip text, max 200 characters.
- `update_label`: label for the update button, max 30 characters.
- `visible`: boolean or callback.

### `WebResult`

`WebResult(*, html=None, url=None)`

- `html`: HTML formatted content as `str`, `StringIO`, or `vkt.File`.
- `url`: direct URL. Do not combine with `html`; URL takes precedence if both are defined.
- `WebResult.from_path(file_path)`: construct a result from a static local HTML file.

### `WebAndDataView`

Use `WebAndDataView` and `WebAndDataResult` when a custom HTML pane should appear with a VIKTOR data pane.

```python
@vkt.WebAndDataView("Dashboard")
def dashboard(self, params, **kwargs):
    data = vkt.DataGroup(
        vkt.DataItem("Utilization", 0.84, suffix="-"),
        vkt.DataItem("Status", "OK"),
    )
    return vkt.WebAndDataResult(html=build_html(params), data=data)
```

`WebAndDataResult(*, html=None, url=None, data=None)` follows the same `html` or `url` rule and adds `data`, a `DataGroup`.

## HTML Delivery Patterns

### External URL

Use when the page is already hosted and can be shown directly.

```python
@vkt.WebView("Reference")
def reference(self, params, **kwargs):
    return vkt.WebResult(url="https://example.com/viewer")
```

### Static Local HTML

Use when the HTML never changes per run.

```python
from pathlib import Path


@vkt.WebView("Guide")
def guide(self, params, **kwargs):
    html_path = Path(__file__).parent / "guide.html"
    return vkt.WebResult.from_path(html_path)
```

### Dynamic HTML

Use when the HTML depends on `params`, calculated results, or generated assets.

```python
import html
import viktor as vkt


def page(title: str, value: float) -> str:
    return f"""
    <!doctype html>
    <html lang="en">
      <head><meta charset="utf-8"><title>{html.escape(title)}</title></head>
      <body><strong>{value:.2f}</strong></body>
    </html>
    """


@vkt.WebView("Summary")
def summary(self, params, **kwargs):
    return vkt.WebResult(html=page("Design summary", params.force))
```

Prefer templating with placeholder replacement or a real template engine over large f-strings once the page has meaningful CSS or JavaScript.

## VIKTOR JavaScript SDK

The documented browser-to-VIKTOR communication path is `viktorSdk.sendParams`. It sends serialized values to parametrization fields. Import the SDK in the HTML and replace the placeholder from Python with `os.environ["VIKTOR_JS_SDK_PATH"] + "v1.js"`. The `VIKTOR_JS_SDK_PATH` environment variable is automatically available in app logic, so do not ask users to configure it manually with the CLI or app settings.

Do not invent additional WebView-to-VIKTOR browser APIs unless they are documented. Use normal VIKTOR view recomputation to pass Python results into the HTML, and use `sendParams` for browser actions that should update parametrization values.

`template.html`

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="VIKTOR_JS_SDK"></script>
  <script>
    function applySelection() {
      viktorSdk.sendParams({ selected_case: "A-12" });
    }
  </script>
</head>
<body>
  <button onclick="applySelection()">Apply</button>
</body>
</html>
```

`app.py`

```python
import os
from pathlib import Path

import viktor as vkt


@vkt.WebView("Selection")
def selection(self, params, **kwargs):
    html_text = (Path(__file__).parent / "template.html").read_text()
    html_text = html_text.replace(
        "VIKTOR_JS_SDK",
        os.environ["VIKTOR_JS_SDK_PATH"] + "v1.js",
    )
    return vkt.WebResult(html=html_text)
```

By default, VIKTOR shows a confirmation pop-up before applying sent parameters. Use the second argument `true` only when immediate field updates are the intended UX:

```javascript
viktorSdk.sendParams({ selected_case: "A-12" }, true);
```

### Serialized Values

`sendParams` accepts serialized field values. Common shapes:

```javascript
viktorSdk.sendParams({
  number_field: 12.3,
  integer_field: 12,
  text_field: "abc",
  bool_field: true,
  select_field: "Green",
  multiselect_field: ["Red", "Green"],
  table_field: [{ c1: 1, c2: 2 }, { c1: 3, c2: 4 }],
  geopoint_field: { lat: 25.7617, lon: -80.1918 },
  color_field: { r: 30, g: 144, b: 255 },
});
```

For fields nested under `Page`, `Step`, `Tab`, or `Section`, send either nested objects or dotted paths:

```javascript
viktorSdk.sendParams({
  "tab.section.hello": "VIKTOR",
});
```

## Passing Data Into HTML

Use JSON serialization. For simple `<script type="application/json">` blocks, escape HTML-sensitive characters. For placeholder injection in a JavaScript string, base64 is a robust option.

```python
import base64
import json
from pathlib import Path


def inject_json_template(path: Path, marker: str, value) -> str:
    encoded = base64.b64encode(json.dumps(value).encode("utf-8")).decode("ascii")
    return path.read_text().replace(marker, encoded)
```

```html
<script>
  const rows = JSON.parse(atob("ROWS_BASE64"));
</script>
```

This mirrors the public VIKTOR WebView examples repository, where table/canvas state is JSON-serialized in Python and decoded by JavaScript.

## JavaScript Libraries And Assets

### CDN Libraries

Use a CDN only when the target VIKTOR environment can access it and the dependency is acceptable for the project.

```html
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
```

CDNs are convenient for prototypes, but production apps should consider version-pinned URLs or local bundled assets for reproducibility.

### Local Assets

For static HTML, CSS, or JS files that live next to `app.py`, read them with `Path(__file__).parent`. For larger frontend assets, use a consistent app folder such as `assets/` if the app configuration exposes that folder, or inline the final generated CSS/JS into the HTML passed to `WebResult`.

Practical file patterns:

- Keep `viewer.html`, `viewer.css`, and `viewer.js` as source files during development.
- Inline CSS and JS into the HTML returned by `WebResult` if relative asset URLs are not resolving in the VIKTOR iframe.
- Use `WebResult.from_path(...)` for static single-file HTML.
- Use `WebResult(html=...)` after injecting JSON data, the VIKTOR SDK path, or generated chart specs.
- Use `vkt.File` or `StringIO` for generated HTML when that fits an existing file-generation pipeline.

## Security And Sanitization Caveats

The official WebView docs describe how to render HTML and how to send serialized values to parametrization fields. They do not describe WebView as a general secure templating system, so apply conservative browser security practices:

- Never place raw user text directly into HTML. Use `html.escape` for text nodes and attributes.
- Never place raw user text directly into JavaScript. Serialize with `json.dumps` and decode in JS.
- Avoid accepting arbitrary HTML, SVG, or script content from end users.
- Avoid `innerHTML` for dynamic text. Prefer `textContent` or DOM APIs.
- Do not embed secrets, API tokens, private URLs, or environment variables in WebView HTML. Browser code is visible to users.
- Validate values received through `sendParams` in Python just like ordinary user input.
- Be cautious with `sendParams(..., true)` because it bypasses the confirmation step.
- Use version-pinned third-party scripts where possible. Review CDN and license constraints before relying on external scripts.
- Keep interactive payloads reasonably small. Large base64 blobs or huge inline libraries can make the view slow to refresh.

## Testing

Decorated view methods should be called under `viktor.testing.mock_View` in automated tests.

```python
import unittest
from unittest.mock import patch

from viktor.testing import mock_View

from app import Controller


class TestWebView(unittest.TestCase):
    @mock_View(Controller)
    @patch.dict("os.environ", {"VIKTOR_JS_SDK_PATH": "/sdk/"})
    def test_web_view_contains_sdk(self):
        result = Controller().web_view(params=...)
        self.assertIn('/sdk/v1.js', result.html)
```
