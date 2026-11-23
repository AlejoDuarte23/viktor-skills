# Interactive VIKTOR WebView Examples

## Minimal File Layout

```text
my-app/
+-- app.py
+-- templates/
    +-- load_editor.html
+-- requirements.txt
+-- viktor.config.toml
```

## Parametrization

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    span = vkt.NumberField("Span", default=20, min=5, max=100, suffix="ft")
    section_modulus = vkt.NumberField("Section modulus", default=50, min=10, suffix="in3")

    load_cases_json = vkt.TextAreaField(
        "Load cases JSON",
        visible=False,
        default="[]",
    )
```

## Controller And HTML Builder

```python
import json
import os
from pathlib import Path

import viktor as vkt


APP_DIR = Path(__file__).parent
TEMPLATE_DIR = APP_DIR / "templates"


def parse_load_cases(raw_value):
    try:
        parsed = json.loads(raw_value or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return parsed


def safe_js(value) -> str:
    return json.dumps(value).replace("</", "<\\/")


def build_load_editor_html(span, load_cases) -> str:
    html = (TEMPLATE_DIR / "load_editor.html").read_text(encoding="utf-8")
    bootstrap = (
        "<script>\n"
        f"const initialSpan = {float(span)};\n"
        f"const loadCases = {safe_js(load_cases)};\n"
        "</script>"
    )
    html = html.replace("{{ bootstrap_script }}", bootstrap)
    html = html.replace("VIKTOR_JS_SDK", os.environ["VIKTOR_JS_SDK_PATH"] + "v1.js")
    return html


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Load Editor", duration_guess=3)
    def load_editor(self, params, **kwargs):
        load_cases = parse_load_cases(params.load_cases_json)
        return vkt.WebResult(
            html=build_load_editor_html(
                span=params.span,
                load_cases=load_cases,
            )
        )

    @vkt.DataView("Utilization Check", duration_guess=1)
    def utilization_check(self, params, **kwargs):
        load_cases = parse_load_cases(params.load_cases_json)
        total_load = sum(float(case.get("magnitude", 0)) for case in load_cases)

        span = float(params.span)
        section_modulus = float(params.section_modulus)
        moment = total_load * span / 4
        stress = (moment * 12) / section_modulus
        utilization = stress / 50.0

        return vkt.DataResult(
            vkt.DataGroup(
                vkt.DataItem("Total load", total_load, suffix="kip"),
                vkt.DataItem("Moment", moment, suffix="kip-ft"),
                vkt.DataItem("Stress", stress, suffix="ksi"),
                vkt.DataItem("Utilization", utilization, number_of_decimals=3),
                vkt.DataItem("Status", "PASS" if utilization <= 1 else "FAIL"),
            )
        )
```

## HTML Template

Save as `templates/load_editor.html`.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Load Editor</title>
  <script src="VIKTOR_JS_SDK"></script>
  <style>
    body { font-family: sans-serif; padding: 20px; background: #f7f8fa; color: #18212b; }
    h2 { margin-top: 0; }
    table { width: 100%; border-collapse: collapse; background: #fff; }
    th, td { border: 1px solid #d6dbe1; padding: 10px; text-align: left; }
    th { background: #1b2733; color: white; }
    input { width: 100%; box-sizing: border-box; padding: 6px; border: 1px solid #b9c0c8; }
    button { padding: 8px 12px; border: 1px solid #aeb6bf; background: #fff; cursor: pointer; }
    .primary { margin-top: 16px; background: #1b2733; color: #fff; border-color: #1b2733; }
    .status { margin-left: 12px; color: #506070; }
  </style>
</head>
<body>
  <h2>Load Cases (span: <span id="span-display"></span> ft)</h2>

  <table>
    <thead>
      <tr>
        <th>Load name</th>
        <th>Magnitude (kip)</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody id="loads-body"></tbody>
  </table>

  <p>
    <button type="button" onclick="addLoad()">Add load case</button>
  </p>

  <button type="button" class="primary" onclick="sendToViktor()">Apply to VIKTOR</button>
  <span class="status" id="status" role="status">No changes applied yet.</span>

  {{ bootstrap_script }}
  <script>
    document.getElementById("span-display").textContent = initialSpan;

    function setStatus(message) {
      document.getElementById("status").textContent = message;
    }

    function renderLoads() {
      const tbody = document.getElementById("loads-body");
      tbody.innerHTML = "";

      if (loadCases.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 3;
        cell.textContent = "No load cases yet.";
        return;
      }

      loadCases.forEach((load, index) => {
        const row = tbody.insertRow();
        const nameCell = row.insertCell();
        const magnitudeCell = row.insertCell();
        const actionCell = row.insertCell();

        const nameInput = document.createElement("input");
        nameInput.type = "text";
        nameInput.value = load.name || "";
        nameInput.onchange = () => {
          loadCases[index].name = nameInput.value;
          setStatus("Unsaved changes");
        };
        nameCell.appendChild(nameInput);

        const magnitudeInput = document.createElement("input");
        magnitudeInput.type = "number";
        magnitudeInput.step = "0.1";
        magnitudeInput.value = Number(load.magnitude || 0);
        magnitudeInput.onchange = () => {
          loadCases[index].magnitude = Number(magnitudeInput.value || 0);
          setStatus("Unsaved changes");
        };
        magnitudeCell.appendChild(magnitudeInput);

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.textContent = "Delete";
        deleteButton.onclick = () => {
          loadCases.splice(index, 1);
          renderLoads();
          setStatus("Unsaved changes");
        };
        actionCell.appendChild(deleteButton);
      });
    }

    function addLoad() {
      loadCases.push({ name: "New Load", magnitude: 0 });
      renderLoads();
      setStatus("Unsaved changes");
    }

    function sendToViktor() {
      if (typeof window.viktorSdk?.sendParams !== "function") {
        setStatus("Open this view in VIKTOR to apply the values.");
        return;
      }
      window.viktorSdk.sendParams({
        load_cases_json: JSON.stringify(loadCases)
      }, true);
      setStatus("Update requested. Check the VIKTOR editor.");
    }

    renderLoads();
  </script>
</body>
</html>
```

## Nested Param Update

For a field declared under `geometry.loads.selected_case`, send either nested objects:

```javascript
viktorSdk.sendParams({
  geometry: {
    loads: {
      selected_case: "ULS-1"
    }
  }
}, true);
```

Or dotted paths:

```javascript
viktorSdk.sendParams({ "geometry.loads.selected_case": "ULS-1" }, true);
```
