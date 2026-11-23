# AutoCAD Connect Examples

## Draw a footing outline in the open drawing

Set `worker_integrations = ["autocad"]` in `viktor.config.toml` and use `viktor>=14.35.0` in `requirements.txt`. Start the personal worker and open a copy of a drawing that uses millimetres. This complete `app.py` draws an outline only; it does not calculate a footing design.

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    intro = vkt.Text("# AutoCAD footing outline\nDraw in an open drawing that uses millimetres.")
    width = vkt.NumberField("Width", default=2000, min=1, suffix="mm")
    length = vkt.NumberField("Length", default=2500, min=1, suffix="mm")
    draw = vkt.ActionButton("Draw in AutoCAD", method="draw_footing", longpoll=True)


class Controller(vkt.Controller):
    parametrization = Parametrization

    def draw_footing(self, params, **kwargs):
        if params.width <= 0 or params.length <= 0:
            raise vkt.UserError("The footing dimensions must be greater than zero.")
        try:
            with vkt.autocad.attach(timeout=120) as acad:
                document = acad.ActiveDocument
                try:
                    layer = document.Layers.Item("VKT-FOOTING")
                except vkt.errors.ExecutionError:
                    layer = document.Layers.Add("VKT-FOOTING")
                outline = document.ModelSpace.AddLightWeightPolyline([
                    0.0, 0.0, params.width, 0.0,
                    params.width, params.length, 0.0, params.length,
                ])
                outline.Closed = True
                outline.Layer = "VKT-FOOTING"
                document.Regen(vkt.autocad.AcRegenType.acAllViewports)
        except vkt.errors.WorkerSessionAttachError as error:
            raise vkt.UserError("Open the drawing and start the AutoCAD personal worker, then try again.") from error
        except vkt.errors.WorkerSessionError as error:
            raise vkt.UserError("The connection was lost. Inspect the drawing for partial edits before retrying.") from error
```

The action adds geometry each time it runs. The user reviews and saves the result in AutoCAD. If drawing units are unknown, determine them before using this example; the app does not change the drawing's unit settings.

## Read a line length

This action uses the drawing's existing units. Validate the input units before calling it and test in a copy of the drawing.

```python
import viktor as vkt


def draw_line(length: float) -> float:
    if length <= 0:
        raise vkt.UserError("The length must be greater than zero.")
    try:
        with vkt.autocad.attach(timeout=120) as acad:
            document = acad.ActiveDocument
            line = document.ModelSpace.AddLine([0, 0, 0], [length, 0, 0])
            result = line.Length()
            document.Regen(vkt.autocad.AcRegenType.acAllViewports)
            return result
    except vkt.errors.WorkerSessionAttachError as error:
        raise vkt.UserError("Open the drawing and start the AutoCAD personal worker, then try again.") from error
```

The line is a real edit. The user saves it in AutoCAD. If a later call fails, the line can remain in the drawing.

## Footing and rebar detail

The footing sample builds a validated design first, converts metres to drawing units, creates or reuses prefixed layers, draws closed `AddLightWeightPolyline` outlines and reinforcement, then regenerates. Separate the calculation from the drawing operation so that a design check does not accidentally edit the open drawing.
