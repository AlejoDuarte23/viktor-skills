# Interactive VIKTOR WebView Reference

## Scope

Use this reference for VIKTOR WebViews where the user edits values in HTML/JavaScript and pushes those values back into VIKTOR parametrization params.

Use this pattern for:

- editable tables with dynamic rows or columns
- form builders
- canvas or geometry editors
- parameter grids
- custom controls that need browser-side interactions before Python recomputes

Do not use this pattern for display-only HTML. A normal `WebView` without the JavaScript SDK bridge is enough when no browser edits need to be saved.

## Data Flow

```text
Python controller
  -> reads hidden fields from params
  -> injects current state into HTML as JSON
  -> returns WebResult(html=...)

WebView iframe
  -> user edits values in the DOM
  -> JavaScript calls viktorSdk.sendParams(...)
  -> VIKTOR receives an update request

VIKTOR params
  -> declared hidden fields receive serialized values
  -> Python reads and casts values on the next view refresh or compute call
```

## Hidden Param Fields

Declare receiving fields in `Parametrization` before sending to them from JavaScript.

Use:

- `IntegerField(visible=False)` or `NumberField(visible=False)` for typed numeric inputs such as plate dimensions.
- `TextField(visible=False)` for one scalar string.
- `TextAreaField(visible=False)` for JSON blobs or larger payloads.

If `viktorSdk.sendParams({field: value})` targets a field that does not exist in the parametrization, the update will not be useful to the app. Keep field names and nesting exact.

## JavaScript SDK Loading

Load the SDK with a script tag in the HTML head so the bridge can receive the parent message during iframe setup.

```html
<script src="VIKTOR_JS_SDK"></script>
```

Replace the placeholder in Python:

```python
sdk_path = os.environ["VIKTOR_JS_SDK_PATH"] + "v1.js"
html = html.replace("VIKTOR_JS_SDK", sdk_path)
```

`VIKTOR_JS_SDK_PATH` is provided by the VIKTOR runtime. If the value is missing, the app is likely running outside the VIKTOR runtime or on an older setup.

## Sending Values Back

Use `viktorSdk.sendParams(values, bypassConfirmation)`.

```javascript
function applyLoads() {
  if (typeof window.viktorSdk?.sendParams !== "function") {
    setStatus("Open this view in VIKTOR to apply the values.");
    return;
  }
  window.viktorSdk.sendParams({ load_cases_json: JSON.stringify(loadCases) });
  setStatus("Update requested. Check the VIKTOR editor.");
}
```

Pass `true` to skip confirmation and apply the values to the editor. Omit it or pass `false` when the user should confirm. Saved entity revisions follow the app's usual save behavior.

Bind the function to a `type="button"` click. The V1 SDK sends the request to the parent and returns no completion value. If the SDK exists and nothing changes, check that it loads early, then check the payload paths and the editor values inside VIKTOR. [VIKTOR WebView guide](https://docs.viktor.ai/docs/create-apps/results-and-visualizations/html/)

## Field Path Syntax

Top-level field:

```javascript
viktorSdk.sendParams({ selected_case: "ULS-1" }, true);
```

Nested field:

```javascript
viktorSdk.sendParams({
  geometry: {
    loads: {
      selected_case: "ULS-1"
    }
  }
}, true);
```

Dotted notation can also be used:

```javascript
viktorSdk.sendParams({ "geometry.loads.selected_case": "ULS-1" }, true);
```

Match the target `Parametrization` structure exactly.

## Serialization

Keep complex values JSON-safe.

- Numbers can be sent as numbers or strings and cast in Python.
- Booleans should be sent as booleans or `"true"` / `"false"` strings and normalized in Python.
- Objects and arrays should be sent as `JSON.stringify(value)` into a hidden text area, then read with `json.loads(...)`.

When injecting JSON into an inline script, escape `</` so JSON content cannot close the script tag:

```python
def safe_js(value) -> str:
    return json.dumps(value).replace("</", "<\\/")
```

## Sandbox Constraints

Treat WebView HTML as sandboxed.

- Do not depend on outbound browser requests for core behavior.
- Avoid loading external scripts or stylesheets dynamically.
- Use a button click to call the SDK. A sandboxed iframe can block normal HTML form submission.
- Inline critical CSS and JavaScript, or load local/static assets according to the base VIKTOR WebView skill.
- Do not interpolate untrusted user-provided HTML.
- The documented browser-to-VIKTOR path is `viktorSdk.sendParams(...)`.

## Related Patterns

- Use `../viktor-webview/SKILL.md` for general WebView rendering, static HTML, dynamic HTML, Plotly-in-WebView, and WebView testing.
- Use [Three.js Dynamic UI](../threejs-dynamic-ui/SKILL.md) for model rendering, orbit controls, and editing geometry in a side panel.
- Use an agent-driven Storage visibility skill when a server-side agent tool should show or hide a panel.
- Use native VIKTOR parametrization fields when the interaction can be expressed without custom HTML.
