# VIKTOR SCIA Worker Examples

## App File Layout

```text
my-scia-app/
+-- app.py
+-- model.esa
+-- requirements.txt
+-- viktor.config.toml
```

`model.esa` is a user-created SCIA template file. It must use the same SCIA version as the worker and contain an XML I/O document named `output`.

## Minimal Configuration

```toml
app_type = "simple"
python_version = "3.12"

worker_integrations = [
    "scia",
]
```

```text
viktor
```

Pin the `viktor` package version to the version available in the target environment when the app is installed.

If the app uses the foundation slab example below exactly, no extra package is required. If the implementation follows the official tutorial's `numpy.linspace` style, add `numpy` to `requirements.txt`.

## Minimal Controller Flow

```python
from pathlib import Path

import viktor as vkt


class Controller(vkt.Controller):
    @vkt.GeometryAndDataView("SCIA result", duration_guess=60, x_axis_to_right=True)
    def run_scia(self, params, **kwargs):
        model = vkt.scia.Model()

        material = vkt.scia.Material(455, "test_material")
        cross_section = model.create_rectangular_cross_section(
            "rectangular_section",
            material,
            0.1,
            0.1,
        )
        n1 = model.create_node("n1", 0, 0, 0)
        n2 = model.create_node("n2", 1, 0, 0)
        model.create_beam(n1, n2, cross_section, name="test_beam")

        input_xml, input_def = model.generate_xml_input()
        input_esa = vkt.File.from_path(Path(__file__).parent / "model.esa")

        analysis = vkt.scia.SciaAnalysis(input_xml, input_def, input_esa)
        analysis.execute(300)

        analysis.get_xml_output_file()
        data_result = vkt.DataGroup(
            vkt.DataItem("SCIA analysis", "Completed")
        )
        return vkt.GeometryAndDataResult([], data_result)
```

## Result Parsing

```python
result = vkt.scia.OutputFileParser.get_result(
    scia_result,
    "Reactions",
    parent="Combinations - C1",
)

reactions = result["Nodal reactions"]
max_rz = float(max(reactions["R_z"]))
```

Make the `table_name` and `parent` values match the XML I/O document in the `.esa` template.

## Tutorial Model Flow

The official tutorial builds a foundation slab with piles. Use this sequence as the implementation checklist:

1. Create slab corner nodes from input geometry.
2. Create pile top and bottom nodes.
3. Create circular pile cross-sections and pile beams.
4. Create a concrete slab plane from the corner nodes.
5. Add point supports at pile bottoms.
6. Add line supports along piles or slab edges when needed.
7. Create a load group, load case, and load combination.
8. Add a surface load to the slab.
9. Generate XML and `.def` files and optionally expose downloads for manual SCIA verification.
10. Run `vkt.scia.SciaAnalysis` with `model.esa`.
11. Parse output XML with `vkt.scia.OutputFileParser.get_result(...)`.

Source: [Tutorial - Creating and analyzing a SCIA model](https://docs.viktor.ai/docs/tutorials/integrate-scia/).

## Foundation Slab With Piles

This is a compact, app-ready pattern adapted from the official tutorial. It uses the current `vkt.scia.Model` API and keeps unit conversions in one place.

Assumed parameters:

- `params.geometry.slab.width_x`: slab width in X direction, in mm.
- `params.geometry.slab.width_y`: slab width in Y direction, in mm.
- `params.geometry.slab.thickness`: slab thickness, in mm.
- `params.geometry.piles.length`: pile length, in m.
- `params.geometry.piles.diameter`: pile diameter, in mm.
- `params.loads.input.uniform_load`: surface load, in kN.

The `.esa` template must contain matching concrete materials and an XML I/O document named `output`.

Matching parametrization:

```python
class Parametrization(vkt.Parametrization):
    geometry = vkt.Tab("Geometry")
    geometry.slab = vkt.Section("Slab")
    geometry.slab.width_x = vkt.NumberField("Slab width X", default=6000, min=1000, suffix="mm")
    geometry.slab.width_y = vkt.NumberField("Slab width Y", default=4500, min=1000, suffix="mm")
    geometry.slab.thickness = vkt.NumberField(
        "Slab thickness",
        default=350,
        min=100,
        suffix="mm",
    )

    geometry.piles = vkt.Section("Piles")
    geometry.piles.length = vkt.NumberField("Pile length", default=8.0, min=1.0, suffix="m")
    geometry.piles.diameter = vkt.NumberField("Pile diameter", default=450, min=100, suffix="mm")

    loads = vkt.Tab("Loads")
    loads.input = vkt.Section("Input")
    loads.input.uniform_load = vkt.NumberField("Uniform surface load", default=10.0, suffix="kN")
```

```python
from pathlib import Path

import viktor as vkt


MM_TO_M = 1e-3
KN_TO_N = 1e3


class Foundation(vkt.Controller):
    parametrization = Parametrization

    def get_scia_input_esa(self) -> vkt.File:
        return vkt.File.from_path(Path(__file__).parent / "model.esa")

    @staticmethod
    def pile_grid(width_x, width_y, count_x=4, count_y=3, edge_offset=0.3):
        if count_x < 2 or count_y < 2:
            raise vkt.UserError("Use at least two piles in each direction.")

        usable_x = width_x - 2 * edge_offset
        usable_y = width_y - 2 * edge_offset
        if usable_x <= 0 or usable_y <= 0:
            raise vkt.UserError("The slab is too small for the selected pile edge offset.")

        step_x = usable_x / (count_x - 1)
        step_y = usable_y / (count_y - 1)
        return [
            (edge_offset + i * step_x, edge_offset + j * step_y)
            for i in range(count_x)
            for j in range(count_y)
        ]

    def create_scia_model(self, params) -> vkt.scia.Model:
        model = vkt.scia.Model()

        width_x = params.geometry.slab.width_x * MM_TO_M
        width_y = params.geometry.slab.width_y * MM_TO_M
        slab_thickness = params.geometry.slab.thickness * MM_TO_M
        pile_length = params.geometry.piles.length
        pile_diameter = params.geometry.piles.diameter * MM_TO_M

        concrete = vkt.scia.Material(0, "C30/37")

        n1 = model.create_node("slab_n1", 0, 0, 0)
        n2 = model.create_node("slab_n2", 0, width_y, 0)
        n3 = model.create_node("slab_n3", width_x, width_y, 0)
        n4 = model.create_node("slab_n4", width_x, 0, 0)
        slab = model.create_plane(
            [n1, n2, n3, n4],
            slab_thickness,
            name="foundation_slab",
            material=concrete,
        )

        pile_section = model.create_circular_cross_section(
            "pile_section",
            concrete,
            pile_diameter,
        )

        pile_beams = []
        for pile_id, (x_coord, y_coord) in enumerate(self.pile_grid(width_x, width_y), 1):
            top_node = model.create_node(f"pile_{pile_id}_top", x_coord, y_coord, 0)
            bottom_node = model.create_node(
                f"pile_{pile_id}_bottom",
                x_coord,
                y_coord,
                -pile_length,
            )
            pile_beams.append(
                model.create_beam(
                    top_node,
                    bottom_node,
                    pile_section,
                    name=f"pile_{pile_id}",
                )
            )

        vertical_freedom = (
            vkt.scia.PointSupport.Freedom.FREE,
            vkt.scia.PointSupport.Freedom.FREE,
            vkt.scia.PointSupport.Freedom.FLEXIBLE,
            vkt.scia.PointSupport.Freedom.FREE,
            vkt.scia.PointSupport.Freedom.FREE,
            vkt.scia.PointSupport.Freedom.FREE,
        )
        vertical_stiffness = (0, 0, 400e6, 0, 0, 0)
        horizontal_stiffness = 10e6

        for pile_id, pile_beam in enumerate(pile_beams, 1):
            model.create_point_support(
                f"pile_{pile_id}_toe_support",
                pile_beam.end_node,
                vkt.scia.PointSupport.Type.STANDARD,
                vertical_freedom,
                vertical_stiffness,
                vkt.scia.PointSupport.CSys.GLOBAL,
            )
            model.create_line_support_on_beam(
                pile_beam,
                x=vkt.scia.LineSupport.Freedom.FLEXIBLE,
                stiffness_x=horizontal_stiffness,
                y=vkt.scia.LineSupport.Freedom.FLEXIBLE,
                stiffness_y=horizontal_stiffness,
                z=vkt.scia.LineSupport.Freedom.FREE,
                rx=vkt.scia.LineSupport.Freedom.FREE,
                ry=vkt.scia.LineSupport.Freedom.FREE,
                rz=vkt.scia.LineSupport.Freedom.FREE,
                c_sys=vkt.scia.LineSupport.CSys.GLOBAL,
            )

        edge_stiffness = 50e6
        for edge in (1, 3):
            model.create_line_support_on_plane(
                (slab, edge),
                x=vkt.scia.LineSupport.Freedom.FLEXIBLE,
                stiffness_x=edge_stiffness,
                y=vkt.scia.LineSupport.Freedom.FREE,
                z=vkt.scia.LineSupport.Freedom.FREE,
                rx=vkt.scia.LineSupport.Freedom.FREE,
                ry=vkt.scia.LineSupport.Freedom.FREE,
                rz=vkt.scia.LineSupport.Freedom.FREE,
            )
        for edge in (2, 4):
            model.create_line_support_on_plane(
                (slab, edge),
                x=vkt.scia.LineSupport.Freedom.FREE,
                y=vkt.scia.LineSupport.Freedom.FLEXIBLE,
                stiffness_y=edge_stiffness,
                z=vkt.scia.LineSupport.Freedom.FREE,
                rx=vkt.scia.LineSupport.Freedom.FREE,
                ry=vkt.scia.LineSupport.Freedom.FREE,
                rz=vkt.scia.LineSupport.Freedom.FREE,
            )

        load_group = model.create_load_group(
            "LG1",
            vkt.scia.LoadGroup.LoadOption.VARIABLE,
            vkt.scia.LoadGroup.RelationOption.STANDARD,
            vkt.scia.LoadGroup.LoadTypeOption.CAT_G,
        )
        load_case = model.create_variable_load_case(
            "LC1",
            "foundation surface load",
            load_group,
            vkt.scia.LoadCase.VariableLoadType.STATIC,
            vkt.scia.LoadCase.Specification.STANDARD,
            vkt.scia.LoadCase.Duration.SHORT,
        )
        model.create_load_combination(
            "C1",
            vkt.scia.LoadCombination.Type.ENVELOPE_SERVICEABILITY,
            {load_case: 1.0},
        )

        load_value = -params.loads.input.uniform_load * KN_TO_N
        model.create_surface_load(
            "surface_load",
            load_case,
            slab,
            vkt.scia.SurfaceLoad.Direction.Z,
            vkt.scia.SurfaceLoad.Type.FORCE,
            load_value,
            vkt.scia.SurfaceLoad.CSys.GLOBAL,
            vkt.scia.SurfaceLoad.Location.LENGTH,
        )

        return model
```

## Foundation Visualization Helper

Use VIKTOR geometry to preview the SCIA input before running the worker. This catches most unit and orientation mistakes before SCIA is involved.

```python
class Foundation(vkt.Controller):
    def create_visualization_geometries(self, params, scia_model):
        geometries = []

        node_radius = max(params.geometry.slab.width_x, params.geometry.slab.width_y) * 1e-5
        for node in scia_model.nodes:
            sphere = vkt.Sphere(vkt.Point(node.x, node.y, node.z), node_radius)
            sphere.material = vkt.Material("node", color=vkt.Color(0, 180, 90))
            geometries.append(sphere)

        pile_diameter = params.geometry.piles.diameter * MM_TO_M
        for beam in scia_model.beams:
            top = vkt.Point(beam.begin_node.x, beam.begin_node.y, beam.begin_node.z)
            bottom = vkt.Point(beam.end_node.x, beam.end_node.y, beam.end_node.z)
            pile = vkt.CircularExtrusion(pile_diameter, vkt.Line(top, bottom))
            pile.material = vkt.Material("pile", opacity=0.35, roughness=1)
            geometries.append(pile)

        slab_nodes = scia_model.nodes[:4]
        slab_points = [vkt.Point(node.x, node.y, node.z) for node in slab_nodes]
        slab_points.append(slab_points[0])
        slab_thickness = params.geometry.slab.thickness * MM_TO_M
        slab = vkt.Extrusion(
            slab_points,
            vkt.Line(
                vkt.Point(0, 0, -slab_thickness / 2),
                vkt.Point(0, 0, slab_thickness / 2),
            ),
        )
        slab.material = vkt.Material("slab", opacity=0.25, roughness=1)
        geometries.append(slab)

        return geometries
```

## Run SCIA And Parse Reactions

The output XML must contain a table named `Reactions` below `Combinations - C1`. Configure that in the `.esa` XML I/O document.

```python
class Foundation(vkt.Controller):
    @vkt.GeometryAndDataView("SCIA result", duration_guess=60, x_axis_to_right=True)
    def run_scia(self, params, **kwargs):
        scia_model = self.create_scia_model(params)

        input_xml, input_def = scia_model.generate_xml_input()
        analysis = vkt.scia.SciaAnalysis(input_xml, input_def, self.get_scia_input_esa())
        analysis.execute(300)

        scia_result = analysis.get_xml_output_file()
        result = vkt.scia.OutputFileParser.get_result(
            scia_result,
            "Reactions",
            parent="Combinations - C1",
        )
        nodal_reactions = result["Nodal reactions"]
        max_vertical_reaction = float(max(nodal_reactions["R_z"]))

        data_result = vkt.DataGroup(
            vkt.DataItem(
                "SCIA results",
                "",
                subgroup=vkt.DataGroup(
                    vkt.DataItem(
                        "Maximum pile reaction",
                        max_vertical_reaction,
                        suffix="N",
                        number_of_decimals=2,
                    )
                ),
            )
        )
        geometries = self.create_visualization_geometries(params, scia_model)
        return vkt.GeometryAndDataResult(geometries, data_result)
```

## Download Generated SCIA Input

```python
class Foundation(vkt.Controller):
    def download_scia_input_xml(self, params, **kwargs):
        model = self.create_scia_model(params)
        input_xml, _ = model.generate_xml_input()
        return vkt.DownloadResult(input_xml, "input.xml")

    def download_scia_input_def(self, params, **kwargs):
        model = vkt.scia.Model()
        _, input_def = model.generate_xml_input()
        return vkt.DownloadResult(input_def, "viktor.xml.def")

    def download_scia_input_esa(self, params, **kwargs):
        return vkt.DownloadResult(self.get_scia_input_esa(), "model.esa")
```

For manual SCIA verification, keep the generated `.xml` and `.def` files in the same folder.

## Testing With mock_SciaAnalysis

```python
import unittest

from viktor import File
from viktor.testing import mock_SciaAnalysis

from app import Controller


class TestController(unittest.TestCase):
    @mock_SciaAnalysis(
        get_xml_output_file=File.from_path("tests/fixtures/output.xml"),
        get_updated_esa_model=File.from_path("tests/fixtures/model.esa"),
        get_engineering_report=File.from_path("tests/fixtures/report.pdf"),
    )
    def test_run_scia(self):
        result = Controller().run_scia(params={})
        self.assertIsNotNone(result)
```

`mock_SciaAnalysis` can return a single object repeatedly, a sequence of objects one call at a time, or default empty file-like content when a method is configured as `None`.
