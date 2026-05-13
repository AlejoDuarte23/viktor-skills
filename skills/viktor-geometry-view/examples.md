# VIKTOR Geometry View Examples

## Simple Beam

```python
import viktor as vkt
from viktor.geometry import Group, Line, Material, Point, RectangularExtrusion


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.GeometryView("Beam")
    def beam(self, params, **kwargs):
        material = Material(color=(80, 130, 180), opacity=1.0)
        line = Line(Point(0, 0, 0), Point(params.length, 0, 0))
        beam = RectangularExtrusion(
            width=params.width,
            height=params.height,
            line=line,
            material=material,
            identifier="main-beam",
        )
        return vkt.GeometryResult(Group([beam], identifier="structure"))
```

## Footing Block With Column

```python
from viktor.geometry import Line, Material, Point, RectangularExtrusion, Group


def footing_geometry(width: float, length: float, thickness: float, column_size: float):
    concrete = Material(color=(185, 185, 185), opacity=1.0)
    footing = RectangularExtrusion(
        width=width,
        height=length,
        line=Line(Point(0, 0, 0), Point(0, 0, thickness)),
        material=concrete,
        identifier="footing",
    )
    column = RectangularExtrusion(
        width=column_size,
        height=column_size,
        line=Line(Point(0, 0, thickness), Point(0, 0, thickness + 2.0)),
        material=Material(color=(120, 120, 120)),
        identifier="column",
    )
    return Group([footing, column], identifier="foundation")
```

## Deformed Shape Pattern

For structural analysis output, keep original and deformed geometry in separate groups. Scale displacements for visibility, use a distinct material for the deformed shape, and document the scale factor in a `DataView` or nearby text.
