# VIKTOR Core Examples

## Minimal App

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    intro = vkt.Text("# Simple VIKTOR app")
    length = vkt.NumberField("Length", default=5, min=0, suffix="m")


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.DataView("Summary")
    def summary(self, params, **kwargs):
        data = vkt.DataGroup(
            vkt.DataItem("Length", params.length, suffix="m"),
        )
        return vkt.DataResult(data)
```

## User-Correctable Validation

```python
import viktor as vkt


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Checks")
    def checks(self, params, **kwargs):
        if params.width <= 0:
            raise vkt.UserError("Width must be larger than zero.")
        return vkt.TableResult([[params.width]], column_headers=["Width"])
```

## View Selection

Use `DataView` for a small set of key values, `TableView` for rows and columns, `GeometryView` for a 3D model, `PlotlyView` for charts, and `PDFView` for a generated report.
