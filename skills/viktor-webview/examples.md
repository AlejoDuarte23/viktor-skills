# VIKTOR WebView Examples

## 1. Minimal Static HTML File

Use this when the page is fixed and does not need `params`.

`app.py`

```python
from pathlib import Path

import viktor as vkt


class Controller(vkt.Controller):
    @vkt.WebView("Method note")
    def method_note(self, params, **kwargs):
        return vkt.WebResult.from_path(Path(__file__).parent / "method-note.html")
```

`method-note.html`

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; line-height: 1.5; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #d4d7dd; padding: 8px; text-align: left; }
  </style>
</head>
<body>
  <h1>Calculation Method</h1>
  <p>This page is packaged with the app and rendered as static HTML.</p>
  <table>
    <tr><th>Step</th><th>Description</th></tr>
    <tr><td>1</td><td>Read input parameters.</td></tr>
    <tr><td>2</td><td>Run the design check.</td></tr>
  </table>
</body>
</html>
```

## 2. Dynamic Summary With Escaped Text

Use `html.escape` for text and format numbers in Python.

```python
import html
import viktor as vkt


class Parametrization(vkt.Parametrization):
    project_name = vkt.TextField("Project name", default="Demo project")
    demand = vkt.NumberField("Demand", default=120)
    capacity = vkt.NumberField("Capacity", default=180)


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Summary")
    def summary(self, params, **kwargs):
        ratio = params.demand / params.capacity if params.capacity else 0
        status = "OK" if ratio <= 1 else "NG"

        page = f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: Arial, sans-serif; margin: 28px; }}
            .metric {{ font-size: 48px; font-weight: 700; }}
            .ok {{ color: #147a4b; }}
            .ng {{ color: #b42318; }}
          </style>
        </head>
        <body>
          <h1>{html.escape(params.project_name or "Untitled")}</h1>
          <div class="metric {status.lower()}">{ratio:.2f}</div>
          <p>Status: {status}</p>
        </body>
        </html>
        """
        return vkt.WebResult(html=page)
```

## MathJax Equation Reports

Load `../viktor-webview-mathjax/SKILL.md` when a WebView HTML template renders calculation equations with MathJax, especially in sandboxed VIKTOR WebView output.

## 3. Send A Button Selection Back To VIKTOR

Use the JavaScript SDK when a user action in the WebView should fill parametrization fields.

`app.py`

```python
import os
from pathlib import Path

import viktor as vkt


class Parametrization(vkt.Parametrization):
    selected_option = vkt.TextField("Selected option")
    multiplier = vkt.NumberField("Multiplier", default=1)


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Selector")
    def selector(self, params, **kwargs):
        html_text = (Path(__file__).parent / "selector.html").read_text()
        html_text = html_text.replace(
            "VIKTOR_JS_SDK",
            os.environ["VIKTOR_JS_SDK_PATH"] + "v1.js",
        )
        return vkt.WebResult(html=html_text)
```

`selector.html`

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="VIKTOR_JS_SDK"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    button { margin-right: 8px; padding: 8px 12px; }
  </style>
  <script>
    function choose(option, multiplier) {
      viktorSdk.sendParams({
        selected_option: option,
        multiplier: multiplier
      });
    }
  </script>
</head>
<body>
  <button onclick="choose('Light', 0.8)">Light</button>
  <button onclick="choose('Normal', 1.0)">Normal</button>
  <button onclick="choose('Heavy', 1.3)">Heavy</button>
</body>
</html>
```

## 4. Plotly Point Click To Populate Fields

Use `PlotlyView` for ordinary Plotly charts. Use `WebView` when browser events need to call `viktorSdk.sendParams`.

```python
import os
from pathlib import Path

import viktor as vkt


class Parametrization(vkt.Parametrization):
    selected_x = vkt.NumberField("Selected x")
    selected_y = vkt.NumberField("Selected y")


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Pick a point")
    def pick_point(self, params, **kwargs):
        html_text = (Path(__file__).parent / "pick-point.html").read_text()
        html_text = html_text.replace(
            "VIKTOR_JS_SDK",
            os.environ["VIKTOR_JS_SDK_PATH"] + "v1.js",
        )
        return vkt.WebResult(html=html_text)
```

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <script src="VIKTOR_JS_SDK"></script>
</head>
<body>
  <div id="plot" style="height: 480px;"></div>
  <script>
    const data = [{
      x: [1, 2, 3, 4],
      y: [10, 14, 12, 18],
      mode: "markers",
      type: "scatter"
    }];

    Plotly.newPlot("plot", data, { hovermode: "closest" }).then(() => {
      document.getElementById("plot").on("plotly_click", (event) => {
        const point = event.points[0];
        viktorSdk.sendParams({
          selected_x: point.x,
          selected_y: point.y
        });
      });
    });
  </script>
</body>
</html>
```

## 5. Pass Existing Table Rows Into A Canvas Editor

Use JSON plus base64 for structured state that the HTML will edit and send back to a VIKTOR `Table`.

`app.py`

```python
import base64
import json
import os
from pathlib import Path

import viktor as vkt


class Parametrization(vkt.Parametrization):
    rectangles = vkt.Table("Rectangles")
    rectangles.x = vkt.IntegerField("X")
    rectangles.y = vkt.IntegerField("Y")
    rectangles.width = vkt.IntegerField("Width")
    rectangles.height = vkt.IntegerField("Height")


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Layout editor")
    def layout_editor(self, params, **kwargs):
        rows = list(params.rectangles or [])
        encoded_rows = base64.b64encode(json.dumps(rows).encode("utf-8")).decode("ascii")

        html_text = (Path(__file__).parent / "layout-editor.html").read_text()
        html_text = html_text.replace("RECTANGLES_BASE64", encoded_rows)
        html_text = html_text.replace(
            "VIKTOR_JS_SDK",
            os.environ["VIKTOR_JS_SDK_PATH"] + "v1.js",
        )
        return vkt.WebResult(html=html_text)
```

`layout-editor.html`

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="VIKTOR_JS_SDK"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    #grid { display: grid; grid-template-columns: repeat(8, 32px); gap: 4px; }
    .cell { width: 32px; height: 32px; border: 1px solid #c8ced8; }
    .filled { background: #2f80ed; }
  </style>
</head>
<body>
  <div id="grid"></div>
  <button id="apply">Apply</button>

  <script>
    const rectangles = JSON.parse(atob("RECTANGLES_BASE64"));
    const selected = new Set(rectangles.map((row) => `${row.x},${row.y}`));
    const grid = document.getElementById("grid");

    for (let y = 0; y < 8; y += 1) {
      for (let x = 0; x < 8; x += 1) {
        const cell = document.createElement("button");
        cell.className = selected.has(`${x},${y}`) ? "cell filled" : "cell";
        cell.type = "button";
        cell.dataset.x = x;
        cell.dataset.y = y;
        cell.addEventListener("click", () => {
          const key = `${x},${y}`;
          selected.has(key) ? selected.delete(key) : selected.add(key);
          cell.classList.toggle("filled");
        });
        grid.appendChild(cell);
      }
    }

    document.getElementById("apply").addEventListener("click", () => {
      const rows = Array.from(selected).map((key) => {
        const [x, y] = key.split(",").map(Number);
        return { x, y, width: 1, height: 1 };
      });
      viktorSdk.sendParams({ rectangles: rows });
    });
  </script>
</body>
</html>
```

## 6. Plotly Parallel Coordinates Filter To VIKTOR Table

This pattern matches the public VIKTOR example repository: browser-side filtering produces a list of row objects and sends them to a `Table` field.

```python
import os
from pathlib import Path

import viktor as vkt


class Parametrization(vkt.Parametrization):
    filtered_results = vkt.Table("Filtered results")
    filtered_results.case = vkt.TextField("Case")
    filtered_results.length = vkt.NumberField("Length [m]")
    filtered_results.capacity = vkt.NumberField("Capacity [kN]")


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Filter cases")
    def filter_cases(self, params, **kwargs):
        html_text = (Path(__file__).parent / "filter-cases.html").read_text()
        html_text = html_text.replace(
            "VIKTOR_JS_SDK",
            os.environ["VIKTOR_JS_SDK_PATH"] + "v1.js",
        )
        return vkt.WebResult(html=html_text)
```

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <script src="VIKTOR_JS_SDK"></script>
</head>
<body>
  <div id="plot" style="height: 520px;"></div>
  <button id="send">Send visible cases</button>

  <script>
    const rows = [
      { case: "A", length: 10, capacity: 900 },
      { case: "B", length: 14, capacity: 1250 },
      { case: "C", length: 18, capacity: 1600 },
      { case: "D", length: 22, capacity: 1850 }
    ];

    const trace = {
      type: "parcoords",
      dimensions: [
        { label: "Length [m]", values: rows.map((row) => row.length) },
        { label: "Capacity [kN]", values: rows.map((row) => row.capacity) }
      ]
    };

    Plotly.newPlot("plot", [trace]);

    document.getElementById("send").addEventListener("click", () => {
      const dimensions = document.getElementById("plot").data[0].dimensions;
      const visibleRows = rows.filter((row) => {
        return dimensions.every((dimension) => {
          const range = dimension.constraintrange;
          if (!range) return true;
          const value = dimension.label.startsWith("Length") ? row.length : row.capacity;
          return value >= range[0] && value <= range[1];
        });
      });
      viktorSdk.sendParams({ filtered_results: visibleRows });
    });
  </script>
</body>
</html>
```

## 7. WebView Combined With Data

Use `WebAndDataView` when the custom HTML needs a VIKTOR data panel beside it.

```python
import viktor as vkt


class Controller(vkt.Controller):
    @vkt.WebAndDataView("Interactive summary")
    def interactive_summary(self, params, **kwargs):
        utilization = 0.72
        html_text = """
        <!doctype html>
        <html lang="en">
        <head><meta charset="utf-8"></head>
        <body>
          <div style="font-family: Arial; margin: 24px;">
            <h1>Design envelope</h1>
            <p>The companion data panel carries the auditable values.</p>
          </div>
        </body>
        </html>
        """
        data = vkt.DataGroup(
            vkt.DataItem("Utilization", utilization, suffix="-"),
            vkt.DataItem("Status", "OK"),
        )
        return vkt.WebAndDataResult(html=html_text, data=data)
```

## 8. Test A WebView Method

Patch `VIKTOR_JS_SDK_PATH` when the view injects the JavaScript SDK.

```python
import unittest
from unittest.mock import patch

from viktor.testing import mock_View

from app import Controller


class TestController(unittest.TestCase):
    @mock_View(Controller)
    @patch.dict("os.environ", {"VIKTOR_JS_SDK_PATH": "/sdk/"})
    def test_selector_view(self):
        result = Controller().selector(params=None)
        self.assertIn('/sdk/v1.js', result.html)
        self.assertIn("viktorSdk.sendParams", result.html)
```
