# VIKTOR WebView MathJax Examples

## Controller Pattern

```python
import viktor as vkt

from .parametrization import Parametrization
from .report.report_builder import WindSummaryReport


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Wall Load Summary")
    def view_wind_summary(self, params, **kwargs) -> vkt.WebResult:
        return vkt.WebResult(html=WindSummaryReport(params).render_html())
```

The report builder should render a Jinja `.html` template and pass already-formatted equation strings:

```python
def equation_line(expression: str, unit_name: str) -> str:
    return rf"{expression}\ \mathrm{{{unit_name}}}"
```

## Jinja HTML Template

This mirrors the MathJax pattern used by `app/report/templates/wind_summary.html`.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Calculation Report</title>

  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['\\(', '\\)']],
        displayMath: [['\\[', '\\]'], ['$$', '$$']],
        processEscapes: true
      },
      options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
      }
    };
  </script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

  <style>
    body { margin: 0; padding: 32px 40px 48px; font-family: "Times New Roman", Georgia, serif; }
    .report { max-width: 980px; margin: 0 auto; }
    .sheet-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px 28px; }
    .calc-line { max-width: 100%; overflow-x: auto; overflow-wrap: anywhere; padding: 2px 0; }
    mjx-container { max-width: 100%; overflow-x: auto; overflow-y: hidden; }
    .calc-line .MathJax { font-size: 1.02em !important; }
    @media (max-width: 820px) {
      body { padding: 22px 18px 32px; }
      .sheet-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="report">
    <h1>Calculation Report</h1>
    <p>Items: {{ n_items }}</p>

    {% for item in items %}
    <section>
      <h2>{{ item.title }}</h2>
      <div class="sheet-grid">
        {% for block in item.blocks %}
        <div>
          <h3>{{ block.title }}</h3>
          {% for line in block.lines %}
          <div class="calc-line">\( {{ line }} \)</div>
          {% endfor %}
        </div>
        {% endfor %}
      </div>
    </section>
    {% endfor %}
  </main>
</body>
</html>
```

## Dynamic Re-Typesetting

Use this only when browser JavaScript inserts equations after page load:

```html
<div id="checks"></div>

<script>
  async function replaceChecks(lines) {
    const checks = document.getElementById("checks");
    checks.replaceChildren();

    for (const line of lines) {
      const item = document.createElement("div");
      item.className = "calc-line";
      item.textContent = `\\(${line}\\)`;
      checks.appendChild(item);
    }

    if (window.MathJax && MathJax.typesetPromise) {
      await MathJax.typesetPromise([checks]);
    }
  }
</script>
```

## Local Rendering Smoke Test

When debugging outside VIKTOR, render the template to an `.html` file and open it in a browser. If raw TeX remains visible, check the browser console and network panel for MathJax loading errors before changing the Python report code.
