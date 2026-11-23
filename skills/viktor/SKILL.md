---
name: viktor
description: Use when the user wants to build, repair, or review a VIKTOR app and may not know which VIKTOR topic applies. VIKTOR is a Python platform for creating engineering web apps with inputs, calculations, visualizations, reports, and integrations. This router skill tells the agent which VIKTOR skills to load first and which specialized skills to load next.
---

# VIKTOR Skill Router

Use this skill as the entry point for VIKTOR app work.

## Workflow

1. Load `../viktor-core/SKILL.md` first to get the app structure, controller pattern, views, and error handling right.
2. Load `../viktor-parametrization/SKILL.md` second before creating or changing user inputs.
3. Load `../viktor-styling/SKILL.md` third before writing app titles, descriptions, equations, or input guidance.
4. Load `../viktor-cli-config/SKILL.md` before creating, installing, starting, testing, or publishing an app.
5. When the task includes running or debugging the app, follow the CLI workflow below and load the CLI skill for details.
6. Load only the specialized skills that match the requested feature.
7. Build or review the app against VIKTOR conventions, not generic Python web app conventions.

## Run the app and inspect logs

1. From the app directory, check `viktor.config.toml`, `requirements.txt`, CLI availability, and the configured platform app. Use `viktor-cli apps` when needed. If the platform app is missing and creating it is part of the task, run `viktor-cli create-app "<App Name>" --registered-name <registered-name>` without `--init` for existing files. Confirm the actual returned name and update the config if needed.
2. For an installed app, start with `viktor-cli start`. For a new app or changed dependencies, run `viktor-cli install`, then `viktor-cli start`. Use `viktor-cli clean-start` only for a confirmed empty development workspace or when the user has authorized clearing it: it deletes workspace entities and entity types.
3. Run the start command in a persistent terminal session the agent can read. Wait for the connection message and development URL; give the user that URL and keep the process running while the app is tested. If the session exits, inspect its error before retrying.
4. Open the development URL and reproduce the relevant view or action, or ask the user to do it. Read new output from the same terminal session and match errors to the action. For integration failures, also check the personal worker logs in VIKTOR Desktop. Do not claim a successful app test based only on startup.
5. If the agent cannot retain or read the terminal session, explain the limitation and ask the user to run `viktor-cli start` and share the relevant output. Run appropriate checks, then ask before publishing unless the user already authorized it.

## Specialized Skills

- `../viktor-geometry-view/SKILL.md`: 3D geometry output, materials, grouping, deformed shape views.
- `../viktor-table-data-view/SKILL.md`: tabular results, summary panels, `TableView`, `DataView`.
- `../viktor-storage/SKILL.md`: reuse long-running results with `vkt.Storage` or `vkt.memoize`, and fill fields or WebViews from a stored run.
- `../viktor-upload-excel/SKILL.md`: Excel upload and parsing with `FileField`, pandas, and openpyxl.
- `../viktor-aec-data-model/SKILL.md`: Autodesk ACC file selection and AEC Data Model GraphQL queries.
- `../viktor-staad-pro-worker/SKILL.md`: STAAD.Pro automation through a VIKTOR worker and `PythonAnalysis`.
- `../viktor-scia-worker/SKILL.md`: SCIA Engineer model creation and analysis through the VIKTOR SCIA worker, `vkt.scia.Model`, `SciaAnalysis`, supported part methods, `.esa` templates, result parsing, and SCIA tests.
- `../viktor-autocad-connect/SKILL.md`: AutoCAD ActiveX access with `connect()` or `attach()`.
- `../viktor-etabs-connect/SKILL.md`: preferred direct ETABS OAPI access with `connect()` or `attach()`.
- `../viktor-sap2000-connect/SKILL.md`: preferred direct SAP2000 OAPI access with `connect()` or `attach()`.
- `../viktor-etabs-worker/SKILL.md`: ETABS worker-side Python scripts and `ETABSAnalysis`.
- `../viktor-sap2000-worker/SKILL.md`: SAP2000 worker-side Python scripts and `SAP2000Analysis`.
- `../viktor-rest-api/SKILL.md`: VIKTOR REST API calls for platform-level resources such as workspaces.
- `../viktor-sdk-api/SKILL.md`: VIKTOR Python SDK API for entity data and running entity computations.
- `../viktor-cli-config/SKILL.md`: VIKTOR CLI commands, app types, `viktor.config.toml`, Python packages, and system dependencies.
- `../viktor-testing/SKILL.md`: VIKTOR automated tests, `viktor-cli test`, local controller/view tests, `viktor.testing` mocks, and external worker/service mocks.
- `../viktor-file-management/SKILL.md`: VIKTOR file upload and download patterns beyond Excel parsing.
- `../viktor-reporting-pandoc/SKILL.md`: Word DOCX reports generated from Markdown with Pandoc and exposed through `DownloadButton`.
- `../viktor-llm/SKILL.md`: VIKTOR built-in LLM, tool use, vision, and LLM chat inputs.
- `../viktor-webview/SKILL.md`: custom HTML, CSS, JavaScript, interactive dashboards, and browser-to-VIKTOR parameter updates.
- `../threejs-dynamic-ui/SKILL.md`: Three.js scenes with OrbitControls, model selection, and a side panel for geometry inputs.
- `../interactive-viktor-webview/SKILL.md`: browser edits and selections that update VIKTOR inputs.
- `../viktor-webview-mathjax/SKILL.md`: MathJax equation rendering inside sandboxed VIKTOR WebView HTML templates.

## References

- Read [reference.md](reference.md) for the routing checklist.
- Read [examples.md](examples.md) for trigger examples.
