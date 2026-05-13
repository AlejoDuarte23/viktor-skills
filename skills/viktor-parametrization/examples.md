# VIKTOR Parametrization Examples

## Basic Engineering Inputs

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    geometry = vkt.Section("Geometry")
    geometry.width = vkt.NumberField("Width", default=2.0, min=0, suffix="m")
    geometry.length = vkt.NumberField("Length", default=3.0, min=0, suffix="m")
    geometry.material = vkt.OptionField(
        "Material",
        options=["Concrete", "Steel", "Timber"],
        default="Concrete",
    )
```

## Slider for Bounded Numeric Choice

```python
class Parametrization(vkt.Parametrization):
    load_factor = vkt.NumberField(
        "Load factor",
        default=1.2,
        min=0.8,
        max=2.0,
        step=0.05,
        variant="slider",
    )
```

## Step with Inputs and View

```python
class Parametrization(vkt.Parametrization):
    step_1 = vkt.Step("Inputs", views=["summary"])
    step_1.inputs = vkt.Section("Design values")
    step_1.inputs.width = vkt.NumberField("Width", default=1.0, min=0, suffix="m")
    step_1.inputs.height = vkt.NumberField("Height", default=0.4, min=0, suffix="m")
```

Use `params.step_1.inputs.width` and `params.step_1.inputs.height` in controller methods.
