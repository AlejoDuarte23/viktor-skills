# Reuse long-running VIKTOR results

Use this guide when a calculation, worker job, or file import takes time and its output is needed in a later view, button, or report.

| Need | Use |
| --- | --- |
| Run a slow calculation only when the user requests a view update | Set an appropriate `duration_guess` on the view. This controls its update behavior. |
| Reuse the same calculation in a view and a download | Use `@vkt.memoize` on a pure function with compact, serializable inputs and outputs. |
| Run a job once and read its output later | Write the result to `vkt.Storage` from a button. Views and downloads read it by key. |
| Fill fields with values from a stored result | Read and validate the result in a `SetParamsButton` method. Return the fields to change in `vkt.SetParamsResult`. |
| Keep a result reference or small editor state with the params | Use a typed field with `visible=False` for a scalar or `vkt.HiddenField` for small JSON-compatible state. |

[Job execution and long-running results](https://docs.viktor.ai/docs/getting-started/fundamentals/call-flow/#long-running-results) · [Storing results](https://docs.viktor.ai/docs/create-apps/results-and-visualizations/storing-results/) · [Set params using a button](https://docs.viktor.ai/docs/create-apps/user-input/set-params-using-button/) · [HiddenField](https://docs.viktor.ai/docs/create-apps/user-input/other-fields/#hiddenfield---store-json-data)

## Run once, then read or apply the result

1. Take a snapshot of the inputs that determine the result. Include units and, when relevant, the model, file, material data, and solver versions. Use a stable input fingerprint if the snapshot is large.
2. Run the analysis from an explicit button. Use `longpoll=True` for a button that can take longer than the normal request timeout. Return `None` from an `ActionButton` that only writes data. Use a `SetParamsButton` when the same action also selects a completed run or fills fields.
3. Write the completed result before returning its run ID. Use `scope="entity"` for durable per-entity results in simple and tree apps, or `scope="session"` for temporary results in any app type. Use `scope="workspace"` for shared data. Keep large results such as meshes, result tables, and files in Storage.
4. On each read, check for a missing result and verify that its input snapshot matches the current inputs. Give the user a way to rerun or restore the inputs. If the source is a live desktop model that can change outside VIKTOR, require a new import or verify the source revision before reuse.
5. Read the same stored result in views and downloads. A Storage write alone does not guarantee a view update. Read the run ID in the view or tell the user to use the view's Update button.

Choose how long to keep individual runs. If saved params can refer to an older run, retain that result while the reference is valid. A hidden field is part of the params and follows normal app save and revision behavior. Keep credentials and large payloads out of params.

[Action buttons](https://docs.viktor.ai/docs/create-apps/user-input/action-buttons/) · [Storage scopes](https://docs.viktor.ai/docs/create-apps/results-and-visualizations/storing-results/#storage-scopes) · [View updates](https://docs.viktor.ai/docs/getting-started/fundamentals/call-flow/#updating-a-view-manually)

## Example with a WebView and a fill button

Use this example in a simple or tree app with an existing entity. The area calculation keeps the example small. Replace it with the actual analysis. The run button stores the result and returns its ID. The fill button reads the selected result and changes only the target field.

```python
import json
from math import isfinite
from uuid import UUID, uuid4

import viktor as vkt


RESULT_SCOPE = "entity"


def result_key(run_id: str) -> str:
    return f"area/v1/{run_id}.json"


def read_area(run_id: object, length_m: float, width_m: float) -> float:
    try:
        if not isinstance(run_id, str):
            raise ValueError
        key = result_key(UUID(run_id).hex)
    except ValueError as error:
        raise vkt.UserError("Run the calculation first.") from error

    try:
        file = vkt.Storage().get(key, scope=RESULT_SCOPE)
    except FileNotFoundError as error:
        raise vkt.UserError("The stored result is missing. Run the calculation again.") from error

    try:
        result = json.loads(file.getvalue())
        if result["length_m"] != length_m or result["width_m"] != width_m:
            raise vkt.UserError("The dimensions changed. Run the calculation again.")
        area_m2 = float(result["area_m2"])
        if not isfinite(area_m2) or area_m2 <= 0:
            raise ValueError
    except (TypeError, KeyError, ValueError) as error:
        raise vkt.UserError("The stored result is invalid. Run the calculation again.") from error

    return area_m2


class Parametrization(vkt.Parametrization):
    length_m = vkt.NumberField("Length", default=4.0, min=0.1, suffix="m")
    width_m = vkt.NumberField("Width", default=2.0, min=0.1, suffix="m")
    result_id = vkt.HiddenField("Current result")
    run = vkt.SetParamsButton("Run calculation", method="run_calculation", longpoll=True)
    area_to_use = vkt.NumberField("Area to use", min=0, suffix="m²")
    apply = vkt.SetParamsButton("Use stored area", method="apply_area")


class Controller(vkt.Controller):
    parametrization = Parametrization

    def run_calculation(self, params, **kwargs):
        length_m = params.length_m
        width_m = params.width_m
        if any(value is None or not isfinite(value) or value <= 0 for value in (length_m, width_m)):
            raise vkt.UserError("Enter a positive length and width.")
        area_m2 = length_m * width_m
        if not isfinite(area_m2) or area_m2 <= 0:
            raise vkt.UserError("Use dimensions that give a valid area.")
        result = {"length_m": length_m, "width_m": width_m, "area_m2": area_m2}
        run_id = uuid4().hex
        vkt.Storage().set(
            result_key(run_id),
            data=vkt.File.from_data(json.dumps(result, allow_nan=False)),
            scope=RESULT_SCOPE,
        )
        return vkt.SetParamsResult({"result_id": run_id})

    def apply_area(self, params, **kwargs):
        area = read_area(params.result_id, params.length_m, params.width_m)
        return vkt.SetParamsResult({"area_to_use": area})

    @vkt.WebView("Stored area", duration_guess=1)
    def show_area(self, params, **kwargs):
        area = read_area(params.result_id, params.length_m, params.width_m)
        return vkt.WebResult(html=f"<p>Area: {area:.2f} m²</p>")
```

The Python view reads Storage and sends the display value to the browser. An interactive WebView can also send selections or small edits to declared fields with `viktorSdk.sendParams`. For a hidden text area, send a JSON string and parse it in Python. For small structured state, a native `HiddenField` can hold JSON-compatible values in params. Validate browser input in Python and resolve result IDs within the correct Storage scope. See the [WebView communication guide](https://docs.viktor.ai/docs/create-apps/results-and-visualizations/html/).

## Use memoize when recalculation is acceptable

Call the same decorated function with the same keyword arguments from the view and the report button. Pass every input that affects the result, including relevant data versions. Keep Storage writes and model edits outside the decorated function because cache hits skip its body. VIKTOR documents a maximum cache lifetime of 24 hours. Use the stored-run pattern when the result must still be available or when reuse depends on an earlier explicit action.

```python
import viktor as vkt

from analysis import solve  # Your app's deterministic calculation.


@vkt.memoize
def calculate(*, span_m: float, section: str, catalogue_revision: str) -> dict[str, float]:
    return solve(span_m=span_m, section=section, catalogue_revision=catalogue_revision)


# Use the same call in the view and in the report button.
result = calculate(span_m=params.span_m, section=params.section, catalogue_revision=revision)
```

Test that a run can populate the field and display the WebView. Also check missing Storage data, edited inputs, and running twice with the same inputs. Check that reopening a saved entity still resolves the selected run if the app promises that behavior. Use `mock_Storage` for tests that call Storage.
