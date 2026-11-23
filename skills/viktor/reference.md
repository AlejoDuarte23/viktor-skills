# VIKTOR Skill Routing Reference

Start every VIKTOR app task with:

1. `viktor-core`
2. `viktor-parametrization`
3. `viktor-styling`

Then add specialized skills only when the task needs them.

| User intent | Load this skill |
| --- | --- |
| Build a normal VIKTOR engineering app | `viktor-core`, `viktor-parametrization`, `viktor-styling` |
| Add or fix input fields | `viktor-parametrization` |
| Improve labels, descriptions, equations, or input guidance | `viktor-styling` |
| Return a 3D model | `viktor-geometry-view` |
| Return tables or key result cards | `viktor-table-data-view` |
| Cache a slow calculation, store a run, or fill fields from a stored result | `viktor-storage`, with `viktor-parametrization` for buttons and hidden fields |
| Read an uploaded Excel file | `viktor-upload-excel` |
| Upload or download general files | `viktor-file-management` |
| Generate downloadable Word reports from Markdown | `viktor-reporting-pandoc`, `viktor-file-management`, `viktor-cli-config` |
| Query Autodesk ACC model data | `viktor-aec-data-model` |
| Run STAAD.Pro outside the VIKTOR cloud runtime | `viktor-staad-pro-worker` |
| Create and run a SCIA Engineer model through the VIKTOR SCIA worker | `viktor-scia-worker` |
| Draw or read an open AutoCAD drawing | `viktor-autocad-connect` |
| Run ETABS with a worker-side Python script | `viktor-etabs-worker` |
| Prefer direct ETABS access through `vkt.etabs.connect()` or `attach()` | `viktor-etabs-connect` |
| Run SAP2000 with a worker-side Python script | `viktor-sap2000-worker` |
| Prefer direct SAP2000 access through `vkt.sap2000.connect()` or `attach()` | `viktor-sap2000-connect` |
| Call VIKTOR platform REST endpoints | `viktor-rest-api` |
| Use the VIKTOR Python SDK API | `viktor-sdk-api` |
| Configure, install, or run a VIKTOR app locally | `viktor-cli-config` |
| Add, fix, run, or mock automated tests | `viktor-testing`, usually with `viktor-core` and `viktor-cli-config` |
| Add built-in VIKTOR LLM features | `viktor-llm` |
| Build custom interactive HTML output | `viktor-webview` |
| Build a Three.js scene with orbit controls, model picking, or a geometry input panel | `threejs-dynamic-ui` |
| Apply edits from a WebView to VIKTOR inputs | `interactive-viktor-webview` |
| Render LaTeX equations in WebView HTML | `viktor-webview`, `viktor-webview-mathjax` |

Do not load every specialized skill by default. The core trio is enough for most application structure work.
