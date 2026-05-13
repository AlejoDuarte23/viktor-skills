# Geometry View 3D Models
Construct a 3D view using `vkt.GeometryResult` with viktor.geometry elements. The default right-handed axis has Z pointing up.

## Groups
Use `Group(objects: Sequence[TransformableObject], identifier: Optional[str] = None)` to combine multiple `TransformableObject` items or other `Group` instances for hierarchical visuals.

## Key Classes and Input Types

- **Point(x: float, y: float, z: float = 0)**

  - **Inputs**: `x` (float), `y` (float), `z` (float, defaults to 0)
  - **Properties**: `x`, `y`, `z`, `coordinates: numpy.ndarray`
  - **Methods**: `coincides_with(other: Point) -> bool`, `copy() -> Point`, `get_local_coordinates(local_origin: Point, spherical: bool = False) -> ndarray`, `vector_to(point: Union[Point, Tuple[float, float, float]]) -> Vector`

- **Polygon(points: List[Point], surface\_orientation: bool = False, material: Optional[Material] = None, skip\_duplicate\_vertices\_check: bool = False, identifier: Optional[str] = None)**

  - **Inputs**:
    - `points`: list of `Point` (automatically closed loop)
    - `surface_orientation`: bool
    - `material`: `Material`
    - `skip_duplicate_vertices_check`: bool
    - `identifier`: str
  - **Properties**: `centroid: Tuple[float, float]`, `cross_sectional_area: float`, `moment_of_inertia: Tuple[float, float]`, `has_clockwise_circumference() -> bool`
  - **Method**: `extrude(line: Line, profile_rotation: float = 0, material: Optional[Material] = None, identifier: Optional[str] = None) -> Extrusion`

- **Material(name: Optional[str] = None, density: Optional[float] = None, price: Optional[float] = None, threejs\_type: str = 'MeshStandardMaterial', roughness: float = 1.0, metalness: float = 0.5, opacity: float = 1.0, color: Union[str, Tuple[int, int, int], Color] = (221,221,221))**

  - **Inputs**: all optional inputs as annotated above
  - **Defines**: appearance parameters for geometry objects

- **Cone(diameter: float, height: float, origin: Optional[Point] = None, orientation: Optional[Vector] = None, material: Optional[Material] = None, identifier: Optional[str] = None)**

  - **Inputs**: `diameter`, `height`, `origin`, `orientation`, `material`, `identifier`
  - **Creates**: conical `TransformableObject`

- **Extrusion(profile: List[Point], line: Line, profile\_rotation: float = 0, material: Optional[Material] = None, identifier: Optional[str] = None)**

  - **Inputs**: `profile` (list of `Point`), `line`, `profile_rotation`, `material`, `identifier`
  - **Properties**: `cross_sectional_area: float`, `inner_volume: float`

- **RectangularExtrusion(width: float, height: float, line: Line, profile\_rotation: float = 0, material: Optional[Material] = None, identifier: Optional[str] = None)**

  - **Inputs**: `width`, `height`, `line`, `profile_rotation`, `material`, `identifier`

- **Line(start\_point: Union[Point, Tuple[float, float, float]], end\_point: Union[Point, Tuple[float, float, float]], color: Tuple[int, int, int] = (0,0,0), identifier: Optional[str] = None)**

  - **Inputs**: `start_point`, `end_point`, `color`, `identifier`
  - **Methods**: `collinear(point: Point) -> bool`, `direction(normalize: bool = True) -> Vector`, `distance_to_point(point: Point) -> float`, `find_overlap(other: Line, inclusive: bool = False) -> Union[Point, Line, None]`, `project_point(point: Point) -> Point`, `revolve(material: Optional[Material] = None, identifier: Optional[str] = None, **kwargs) -> LineRevolve`
  - **Properties**: `length: float`, `length_vector: numpy.ndarray`, `unit_vector: numpy.ndarray`, `horizontal: bool`, `vertical: bool`

## Example Usage

```python
import viktor as vkt
from viktor.geometry import Point, Line, RectangularExtrusion, Group

# Create a box extrusion and wrap in a group
p1 = Point(1, 2)
line = Line(Point(0, 0, 0), Point(0, 0, 1))
box = RectangularExtrusion(1.0, 1.0, line)
view = vkt.GeometryResult(Group([box]))
```

## Structure Example: Render a 3D Model

```python
import json
import viktor as vkt

def create_frame_data(length: float, height: float):
    nodes = {
        1: {"node_id": 1, "x": 0, "y": 0, "z": 0},
        2: {"node_id": 2, "x": 0, "y": length, "z": 0},
        3: {"node_id": 3, "x": 0, "y": 0, "z": height},
        4: {"node_id": 4, "x": 0, "y": length, "z": height},
        5: {"node_id": 5, "x": length, "y": 0, "z": 0},
        6: {"node_id": 6, "x": length, "y": length, "z": 0},
        7: {"node_id": 7, "x": length, "y": 0, "z": height},
        8: {"node_id": 8, "x": length, "y": length, "z": height},
    }
    lines = {
        1: {"line_id": 1, "node_i": 1, "node_j": 3},
        2: {"line_id": 2, "node_i": 2, "node_j": 4},
        3: {"line_id": 3, "node_i": 3, "node_j": 4},
        4: {"line_id": 4, "node_i": 6, "node_j": 8},
        5: {"line_id": 5, "node_i": 5, "node_j": 7},
        6: {"line_id": 6, "node_i": 3, "node_j": 7},
        7: {"line_id": 7, "node_i": 4, "node_j": 8},
        8: {"line_id": 8, "node_i": 7, "node_j": 8},
    }
    return nodes, lines

class Parametrization(vkt.Parametrization):
    intro = vkt.Text("# Structure 3D Model")
    frame_length = vkt.NumberField("Frame Length", min=100, default=4000, suffix="mm")
    frame_height = vkt.NumberField("Frame Height", min=100, default=4000, suffix="mm")

class Controller(vkt.Controller):
    parametrization = Parametrization
    
    @vkt.GeometryView("3D Model", duration_guess=1, x_axis_to_right=True)
    def create_render(self, params, **kwargs):
        nodes, lines = create_frame_data(length=params.frame_length, height=params.frame_height)
        sections_group = []
        
        for line_id, dict_vals in lines.items():
            node_i = nodes[dict_vals["node_i"]]
            node_j = nodes[dict_vals["node_j"]]

            point_i = vkt.Point(node_i["x"], node_i["y"], node_i["z"])
            point_j = vkt.Point(node_j["x"], node_j["y"], node_j["z"])
            
            line_k = vkt.Line(point_i, point_j)
            section_k = vkt.RectangularExtrusion(300, 300, line_k, identifier=str(line_id))
            sections_group.append(section_k)
            
        return vkt.GeometryResult(geometry=sections_group)
```
## Render 3D models deformations for structural Analysis
To render deformation you need to:
1. Get deformation in either on all x, y ,Z
2. define a sclae factor and add the scale deformation to the model
3. Pick a colormap
4. Color the lines based ont the mean deformation value based on the each node values

See a code snipets that don't have much information about the context but provide a good idea of the process.:

app.py
```python
SF = 20
COLOR_BY = "component"
COLUMN_HEIGHT = 6000
color_dict = {
    "Truss": vkt.Material(color=vkt.Color(r=255, g=105, b=180)),  # Bright Pastel Pink
    "Column": vkt.Material(color=vkt.Color(r=100, g=200, b=250)),  # Bright Pastel Blue
    "Joist": vkt.Material(color=vkt.Color(r=255, g=220, b=130)),  # Bright Pastel Yellow
}
section_dict = {"Truss": 150, "Column": 300, "Joist": 100}
class Controller(vkt.Controller):
    ...
    @vkt.GeometryAndDataView("Deformed model", duration_guess=1, x_axis_to_right=True)
    def run_model(self, params, **kwargs) -> vkt.GeometryResult:
    ...
    for node_id, _ in opt_model["nodes"].items():
                defo = SF * results_data[0]["deformations"][str(node_id)]
                opt_model["nodes"][node_id]["z"] = opt_model["nodes"][node_id]["z"] + defo

            for line_id, dict_vals in opt_model["lines"].items():
                ni = str(dict_vals["nodeI"])
                nj = str(dict_vals["nodeI"])
                defo_ni = results_data[0]["deformations"][str(ni)]
                defo_nj = results_data[0]["deformations"][str(nj)]
                opt_model["lines"][line_id].update({"deformation": 0.5 * (abs(defo_ni) + abs(defo_nj))})

            max_defo = abs(results_data[0]["max_defo"])
            selected_section = sections_db[params.step_1.section]["depth"]
            section_dict = {"Truss":selected_section , "Column": 300, "Joist": selected_section}
            sections_group = render_frame_elements(
                lines=opt_model["lines"],
                nodes=opt_model["nodes"],
                color_dict=color_dict,
                section_dict=section_dict,
                COLOR_BY=COLOR_BY,
                deformation=True,
                max_defo=max_defo,
            )
    return vkt.GeometryResult(geometry=sections_group)

viz_helper_function.py
def render_frame_elements(
    lines: dict,
    nodes: dict,
    color_dict: dict,
    section_dict: dict,
    COLOR_BY: str,
    deformation: bool = False,
    max_defo: float | None = None,
) -> list:
    sections_group = []
    rendered_sphere = set()
    for line_id, dict_vals in lines.items():
        node_id_i = dict_vals["nodeI"]
        node_id_j = dict_vals["nodeJ"]

        node_i = nodes[node_id_i]
        node_j = nodes[node_id_j]

        point_i = vkt.Point(node_i["x"], node_i["y"], node_i["z"])
        point_j = vkt.Point(node_j["x"], node_j["y"], node_j["z"])

        # To Do: This can be simplified
        if not node_id_i in rendered_sphere:
            sphere_k = vkt.Sphere(point_i, radius=NODE_RADIUS, material=None, identifier=str(node_id_i))
            sections_group.append(sphere_k)
            rendered_sphere.add(node_id_i)

        if not node_id_j in rendered_sphere:
            sphere_k = vkt.Sphere(point_j, radius=NODE_RADIUS, material=None, identifier=str(node_id_j))
            sections_group.append(sphere_k)
            rendered_sphere.add(node_id_j)

        line_k = vkt.Line(point_i, point_j)
        material = color_dict[dict_vals[COLOR_BY]]
        sec_size = section_dict[dict_vals[COLOR_BY]]
        if deformation:
            def_val = dict_vals["deformation"]
            r, g, b = get_color_from_displacement(def_val, max_defo)
            material = vkt.Material(color=vkt.Color(r=r, g=g, b=b))
        section_k = vkt.RectangularExtrusion(sec_size, sec_size, line_k, identifier=str(line_id), material=material)
        sections_group.append(section_k)

    return sections_group


def get_color_from_displacement(displacement: float, max_displacement: float, partitions: int = 30):
    # Normalize the displacement value
    normalized_displacement = displacement / max_displacement if max_displacement != 0 else 0
    # Generate a colormap with the specified number of partitions
    base_cmap = plt.get_cmap("jet")
    discrete_cmap = ListedColormap(base_cmap(np.linspace(0, 1, partitions)))
    # Get the RGB color from the discrete colormap
    rgb_color = discrete_cmap(normalized_displacement)[:3]  # Exclude alpha channel
    return tuple(int(x * 255) for x in rgb_color)
```
