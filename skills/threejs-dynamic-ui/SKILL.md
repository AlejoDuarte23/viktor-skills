---
name: threejs-dynamic-ui
description: Build and debug Three.js scenes in a VIKTOR WebView. Use for custom 3D engineering views with OrbitControls, model picking, camera presets, or a geometry input panel that updates VIKTOR params.
---

# Three.js Dynamic UI

## Workflow

1. Keep load combinations in a native `vkt.Table` when it fits the task. When users edit dimensions beside the model, put the controls in a right-side WebView panel and use hidden typed VIKTOR fields to keep the applied values. Read `params` in Python and return a validated geometry payload in `vkt.WebResult(html=...)`.
2. Load Three.js and its addons from the same pinned release. For a CDN build, map both `three` and `three/addons/` before the module script. Use a bundled build if the target browser or network blocks CDN modules.
3. Convert units once at the scene boundary. Document the engineering axes and map them to the scene axes. Keep camera controls, visibility, and temporary selections in the browser.
4. Calculate from native params in Python. Use a `DataView` for the summary. A fast calculation can run when VIKTOR updates the DataView. For an explicit or slow run, use a button and reuse the completed result. Read [the stored result guide](../viktor-storage/long-running-results.md).
5. Test orbit, zoom, resize, and one parameter change inside the target VIKTOR iframe. Check the browser console for module or WebGL errors. Check the running CLI log for Python errors.

## Load When Needed

- Load [VIKTOR WebView](../viktor-webview/SKILL.md) for the HTML result and asset patterns.
- Load [Interactive VIKTOR WebView](../interactive-viktor-webview/SKILL.md) when users must apply edits or a selection from the 3D view to VIKTOR fields. Orbiting and inspecting objects can stay in the browser.
- Load [VIKTOR Table and Data View](../viktor-table-data-view/SKILL.md) to display result summaries with native VIKTOR views.
- Load [VIKTOR Geometry View](../viktor-geometry-view/SKILL.md) when the standard geometry viewer meets the app requirements.

- Read [examples.md](examples.md) for a base plate app with the model on the left, dimension controls on the right, a native load table, and a Results DataView.
- Read [reference.md](reference.md) for CDN and bundled options, the WebView data flow, and browser checks.
