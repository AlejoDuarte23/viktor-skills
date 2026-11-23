# Three.js in a VIKTOR WebView

## Choose how to load Three.js

- **CDN** for a small prototype. Declare an import map before the module code. Point `three` and `three/addons/` to the same exact release on the same CDN. `OrbitControls.js` imports the bare specifier `three`, even if the app imports the addon by a full URL. A single full URL to the addon does not resolve that import.
- **Bundle** when the app must work in a network that blocks the CDN. Resolve Three.js and its addons from one dependency version at build time. For a small, self-contained `WebResult(html=...)`, generate one browser bundle and inline it in the trusted HTML template. Preserve the dependency license notices. For a larger app, verify the URL and delivery method for each emitted chunk and asset in the VIKTOR iframe. The runtime uses the built files and does not need the JavaScript build tool.

The CDN configuration in the example uses jsDelivr and Three.js 0.185.1. This combination rendered with OrbitControls in one VIKTOR development workspace. Test the target tenant and browser because local render tests cannot check iframe or network policy.

[Three.js installation and CDN guidance](https://threejs.org/manual/pages/installation.html) · [OrbitControls](https://threejs.org/docs/pages/OrbitControls.html) · [VIKTOR WebView](https://docs.viktor.ai/docs/create-apps/results-and-visualizations/html/)

## Send geometry and results to the view

- Validate inputs in Python. Inject numeric data, IDs, and labels with `json.dumps(..., allow_nan=False)`. Escape `<` as `\\u003c` before embedding JSON in a script element. Read it with `JSON.parse` and display labels with `textContent`.
- Map axes explicitly. For a Y-up scene of a base plate, X is width, Y is height, and Z is depth. Convert millimeters to meters when building the scene. Add units to the on-screen dimensions.
- Size the canvas from its container. When the container changes size, set the camera aspect, call `updateProjectionMatrix()`, then resize the renderer. Call `controls.update()` after a camera preset. Call it in the animation loop if damping or auto-rotation is enabled.
- Use stable object IDs for picking. Keep hover, highlights, and camera presets local. If a pick changes a calculation input, send the declared field value from an explicit button. Use the [Interactive VIKTOR WebView skill](../interactive-viktor-webview/SKILL.md) for the SDK setup and parameter paths.
- If the 3D view needs overlays, send the result from the same Python run used by the Summary DataView. Use a run ID for a stored result and check that its inputs still match. Send the display data needed by the scene.

## Edit Dimensions in the Right Panel

1. Put the canvas and view buttons in the left column. Put the dimension fields and **Apply to VIKTOR** in the right column. Let the canvas resize with the VIKTOR split pane.
2. Declare one hidden `IntegerField` or `NumberField` for each editable dimension. Use the same field paths in the JSON payload and the SDK call.
3. Update the preview from valid edits in the browser. Dispose of the old mesh geometries when you build replacements.
4. Load the VIKTOR JavaScript SDK in the HTML head. Call `viktorSdk.sendParams` from the Apply button. Read the applied values in the controller on the next view load. See [Interactive VIKTOR WebView](../interactive-viktor-webview/SKILL.md).
5. Keep the load table in the native VIKTOR input panel and read it in the Results DataView. The base plate example shows this flow. See [examples.md](examples.md).

## Verify in the target app

1. Start the app with `viktor-cli start`. Open the development URL and switch to the WebView.
2. Confirm the model is visible. Orbit and zoom. Resize the split pane and check that the model keeps its proportions.
3. Change a dimension. Confirm the updated geometry and dimension label. For editable WebViews, apply the value and reopen the view to check that VIKTOR retained it. Change a load row and check Results. If the app uses a run button, check before and after the run.
4. For a blank view, check the iframe console and network panel. An unresolved `three` specifier points to the import map. A failed fetch can indicate a blocked origin, missing module, or CORS error. If imports succeed and the renderer fails, check WebGL on the client. Use the CLI log to diagnose Python jobs.

[VIKTOR CLI](https://docs.viktor.ai/docs/create-apps/references/cli/) · [VIKTOR DataView](https://docs.viktor.ai/docs/create-apps/results-and-visualizations/data-and-tables/)
