# VIKTOR WebView MathJax Reference

Official sources:

- VIKTOR HTML WebView docs: <https://docs.viktor.ai/docs/create-apps/results-and-visualizations/html/>
- VIKTOR views SDK reference: <https://docs.viktor.ai/sdk/api/views/>
- MathJax v3.2 getting started: <https://docs.mathjax.org/en/v3.2/web/start.html>
- MathJax v3.2 TeX input options: <https://docs.mathjax.org/en/v3.2/options/input/tex.html>
- MathJax v3.2 dynamic content: <https://docs.mathjax.org/en/v3.2/advanced/typeset.html>

## WebView Sandbox Assumptions

VIKTOR renders `WebView` output as an isolated browser surface. Build the HTML as a self-contained page:

- Include `<!doctype html>`, `<meta charset="utf-8">`, viewport metadata, CSS, and required scripts.
- Do not rely on parent-page CSS, parent-page JavaScript, cookies, local storage, or direct parent-window access.
- Use only documented VIKTOR browser communication, such as the VIKTOR JavaScript SDK from `VIKTOR_JS_SDK_PATH`, when the page needs to send values back to parametrization fields.
- Assume external CDN scripts can fail in restricted environments. If raw TeX appears, first check whether the MathJax script loaded.

## Recommended MathJax Block

Put the config before the script tag:

```html
<script>
  window.MathJax = {
    tex: {
      inlineMath: [['\\(', '\\)']],
      displayMath: [['\\[', '\\]'], ['$$', '$$']],
      processEscapes: true
    },
    options: {
      skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    },
    startup: {
      pageReady: () => MathJax.startup.defaultPageReady().then(() => {
        document.documentElement.classList.add('mathjax-ready');
      })
    }
  };
</script>
<script
  id="MathJax-script"
  async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
</script>
```

Use `tex-chtml.js` for CommonHTML output. If a report depends on more TeX extensions than the combined component provides, test with `tex-chtml-full.js`.

## Equation HTML

Inline generated equations:

```html
<div class="calc-line">\( {{ line }} \)</div>
```

Display equations:

```html
<div class="equation-block">
  \[
  {{ equation }}
  \]
</div>
```

Prefer `\(...\)` over `$...$` for generated reports because normal text can contain dollar signs. If `$...$` is enabled, escape literal currency and cost text carefully.

## Responsive Equation CSS

```css
.calc-line,
.equation-block {
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  overflow-wrap: anywhere;
}

mjx-container {
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
}

.calc-line .MathJax {
  font-size: 1.02em !important;
}
```

Use a single-column layout on small screens. MathJax output can be wider than the source text, so avoid fixed-width panels for calculation sheets.

## Jinja And Escaping

For `.html` templates, use Jinja autoescaping:

```python
from jinja2 import Environment, FileSystemLoader, select_autoescape

JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)
```

Guidelines:

- Escape normal text such as project names, labels, notes, and errors.
- Generate equation strings in Python from trusted calculation code.
- Use raw Python strings or doubled backslashes for LaTeX: `r"\frac{L}{2}"`.
- Avoid user-authored HTML, SVG, or script in equation labels.

## Dynamic Content

Initial MathJax startup is enough when VIKTOR renders the whole report once. If browser JavaScript later injects new equations, re-typeset the changed container:

```javascript
async function renderMath(container) {
  if (window.MathJax && MathJax.typesetPromise) {
    await MathJax.typesetPromise([container]);
  }
}
```

Do not run many `typesetPromise()` calls in parallel. Chain or await them.

## Common Failures

- Raw `\(...\)` text appears: MathJax script did not load, loaded after invalid config, or CDN access is blocked.
- Some inline equations render incorrectly: `$...$` is conflicting with ordinary dollar signs; prefer `\(...\)`.
- Equations disappear after a JavaScript update: call `MathJax.typesetPromise([container])` after inserting content.
- Python strings lose backslashes: use raw strings for equation fragments.
- Long formulas overflow the WebView: add `overflow-x: auto` to `mjx-container` and report line containers.
