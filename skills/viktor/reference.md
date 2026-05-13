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
| Read an uploaded Excel file | `viktor-upload-excel` |
| Upload or download general files | `viktor-file-management` |
| Generate downloadable Word reports from Markdown | `viktor-reporting-pandoc`, `viktor-file-management`, `viktor-cli-config` |
| Query Autodesk ACC model data | `viktor-aec-data-model` |
| Run STAAD.Pro outside the VIKTOR cloud runtime | `viktor-staad-pro-worker` |
| Run ETABS outside the VIKTOR cloud runtime | `viktor-etabs-worker` |
| Call VIKTOR platform REST endpoints | `viktor-rest-api` |
| Use the VIKTOR Python SDK API | `viktor-sdk-api` |
| Configure, install, or run a VIKTOR app locally | `viktor-cli-config` |
| Add built-in VIKTOR LLM features | `viktor-llm` |
| Build custom interactive HTML output | `viktor-webview` |

Do not load every specialized skill by default. The core trio is enough for most application structure work.
