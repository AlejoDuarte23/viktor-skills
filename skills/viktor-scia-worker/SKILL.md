---
name: viktor-scia-worker
description: Use when a VIKTOR app needs to create, run, test, or parse a SCIA Engineer model through the VIKTOR SCIA worker integration. Covers `vkt.scia.Model`, supported SCIA `create_*` part methods, XML and DEF generation, `.esa` template requirements, `vkt.scia.SciaAnalysis`, `OutputFileParser`, worker configuration, supported SCIA versions, and `mock_SciaAnalysis` tests.
---

# VIKTOR SCIA Worker

Use this skill when a VIKTOR app needs SCIA Engineer integration through the VIKTOR worker.

Do not build a custom Windows automation script for SCIA unless the user explicitly asks for one. The standard SCIA flow is app-side model construction with `vkt.scia.Model`, XML/DEF generation, and execution through `vkt.scia.SciaAnalysis` using a user-created `.esa` template.

## Workflow

1. Load the VIKTOR core trio first: `../viktor-core/SKILL.md`, `../viktor-parametrization/SKILL.md`, and `../viktor-styling/SKILL.md`.
2. Load `../viktor-geometry-view/SKILL.md` when the app previews the generated SCIA geometry.
3. Load `../viktor-table-data-view/SKILL.md` when parsed SCIA results are shown as tables or data cards.
4. Configure `viktor.config.toml` with `worker_integrations = ["scia"]`.
5. Create a `vkt.scia.Model()` and fill it with supported parts by calling the relevant `model.create_*` methods.
6. Keep all SCIA units explicit. The SDK methods commonly use meters for geometry, newtons for force loads, newton-meters for moments, and degrees for rotations or angles.
7. Use a user-created `.esa` template with matching SCIA version, matching materials, and an XML I/O document named `output`.
8. Call `model.generate_xml_input()` to produce the XML input and `.def` file.
9. Run `vkt.scia.SciaAnalysis(input_xml, input_def, esa_file)` and call `execute(timeout)`.
10. Read results with `get_xml_output_file()`, `get_updated_esa_model()`, or `get_engineering_report()` as needed.
11. Parse XML output with `vkt.scia.OutputFileParser.get_result(...)` when the app needs tabular values.
12. Mock `Model.generate_xml_input()` and `SciaAnalysis.execute()` in automated tests; use `viktor.testing.mock_SciaAnalysis` for worker output methods.

## Load When Needed

- Read [reference.md](reference.md) for the full SCIA integration reference, supported parts, method stubs, and official links.
- Read [examples.md](examples.md) for app configuration, controller flow, tutorial model flow, result parsing, and testing examples.
