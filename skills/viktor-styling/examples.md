# VIKTOR Styling Examples

## App Intro With Equation

```python
import textwrap
import viktor as vkt


class Parametrization(vkt.Parametrization):
    intro = vkt.Text(textwrap.dedent(r"""
    # Bearing pressure check

    This app checks the average bearing pressure under a rectangular footing.

    $$
    q = \frac{N}{B L}
    $$

    where `N` is the vertical load, `B` is the footing width, and `L` is the footing length.
    """))
```

Use a raw string for LaTeX-heavy text so backslashes are not corrupted.

## Text Inside a Section

```python
class Parametrization(vkt.Parametrization):
    design = vkt.Section("Design inputs")
    design.info = vkt.Text("Enter service loads and footing dimensions.")
    design.width = vkt.NumberField("Width", default=2.0, min=0, suffix="m")
```

When using containers, keep text and inputs inside the relevant container instead of mixing orphan fields at the root.

## Better Input Guidance

```python
class Parametrization(vkt.Parametrization):
    concrete_strength = vkt.NumberField(
        "Concrete strength",
        default=30,
        min=10,
        suffix="MPa",
        description="Use the specified compressive strength from the design basis.",
    )
```
