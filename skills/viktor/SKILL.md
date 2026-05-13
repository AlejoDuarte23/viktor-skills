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
4. Load only the specialized skills that match the requested feature.
5. Build or review the app against VIKTOR conventions, not generic Python web app conventions.

## Specialized Skills

- `../viktor-geometry-view/SKILL.md`: 3D geometry output, materials, grouping, deformed shape views.
- `../viktor-table-data-view/SKILL.md`: tabular results, summary panels, `TableView`, `DataView`.
- `../viktor-upload-excel/SKILL.md`: Excel upload and parsing with `FileField`, pandas, and openpyxl.
- `../viktor-aec-data-model/SKILL.md`: Autodesk ACC file selection and AEC Data Model GraphQL queries.
- `../viktor-staad-pro-worker/SKILL.md`: STAAD.Pro automation through a VIKTOR worker and `PythonAnalysis`.
- `../viktor-etabs-worker/SKILL.md`: ETABS automation through a VIKTOR worker and `ETABSAnalysis`.
- `../viktor-rest-api/SKILL.md`: VIKTOR REST API calls for platform-level resources such as workspaces.
- `../viktor-sdk-api/SKILL.md`: VIKTOR Python SDK API for entity data and running entity computations.
- `../viktor-cli-config/SKILL.md`: VIKTOR CLI commands, app types, `viktor.config.toml`, Python packages, and system dependencies.
- `../viktor-file-management/SKILL.md`: VIKTOR file upload and download patterns beyond Excel parsing.
- `../viktor-llm/SKILL.md`: VIKTOR built-in LLM, tool use, vision, and LLM chat inputs.
- `../viktor-webview/SKILL.md`: custom HTML, CSS, JavaScript, interactive dashboards, and browser-to-VIKTOR parameter updates.

## References

- Read [reference.md](reference.md) for the routing checklist.
- Read [examples.md](examples.md) for trigger examples.
