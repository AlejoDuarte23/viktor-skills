# Three.js Dynamic UI Examples

## Base Plate With a Right-Side Panel

Use this example when the editor needs a native load table and the geometry controls belong beside the model.

| Location | Component | Behavior |
| --- | --- | --- |
| VIKTOR input panel | `vkt.Table` | Edit load combinations. The table is the only visible input. |
| Geometry tab | `vkt.WebView` | Orbit and inspect the model on the left. Edit width, depth, and thickness in the panel on the right. |
| Results tab | `vkt.DataView` | Read the current load table and show the largest axial load magnitude, resultant shear, and resultant bending. |

## App File Layout

```text
base-plate-app/
+-- app.py
+-- plate.html
+-- requirements.txt
+-- viktor.config.toml
```

Copy [app.py](examples/base-plate/app.py) and [plate.html](examples/base-plate/plate.html) into the same app directory.

Use `viktor==14.36.1` in `requirements.txt` to match the tested SDK. For a new app, use Python 3.12 and set `app_type = "editor"` in `viktor.config.toml`. Create and start the development app with the [VIKTOR CLI skill](../viktor-cli-config/SKILL.md).

## Geometry Update

1. Python reads the three hidden `IntegerField` values, validates them, and adds them to the HTML as JSON.
2. In the browser, a change to a valid dimension updates the preview. An out-of-range dimension disables **Apply to VIKTOR**.
3. **Apply to VIKTOR** sends the width, depth, and thickness to the three declared fields. When VIKTOR loads the view again, the controller uses the returned dimensions.
4. The Results DataView reads the native table. With the sample rows, it shows 240 kN axial magnitude for LC-02, 51 kN resultant shear for LC-03, and 35 kN·m resultant bending for LC-01. These are applied loads.

## Check the App

- Change the plate to 420 × 310 × 28 mm and confirm that the model preview changes. Apply the dimensions, switch to Results, and return to Geometry. Confirm that the dimensions are still 420 × 310 × 28 mm.
- Change Vx in LC-01 from 18 kN to 60 kN. Open Results and confirm that LC-01 now gives the largest resultant shear at about 64.62 kN.
- Narrow the VIKTOR split pane. Confirm that the fields stay in the right panel and the canvas resizes.
