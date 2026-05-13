
# STAAD.PRO - Viktor integration
The VIKTOR worker (from viktor.external.python import PythonAnalysis) takes `the run_staad_model.py`and send it to the users computer server and executes the model there. it uses a json as inputs and retrieves back a json to the application for later visualization.

# Basic Example Example
This example creates a parametric 3D frame assign

```plaintext
my-app
├── app.py
├── run_staad_model.py    # Script to run the STAAD.Pro model
├── requirements.txt
└── viktor.config.toml
```

```python
import json
import viktor as vkt

from viktor.external.python import PythonAnalysis
from io import BytesIO
from pathlib import Path
from viktor.core import File


def create_frame_data(length, height, cross_section="IPE400"):
    nodes = {
        1: {"node_id": 1, "x": 0, "z": 0, "y": 0},
        2: {"node_id": 2, "x": 0, "z": length, "y": 0},
        3: {"node_id": 3, "x": 0, "z": 0, "y": height},
        4: {"node_id": 4, "x": 0, "z": length, "y": height},
        5: {"node_id": 5, "x": length, "z": 0, "y": 0},
        6: {"node_id": 6, "x": length, "z": length, "y": 0},
        7: {"node_id": 7, "x": length, "z": 0, "y": height},
        8: {"node_id": 8, "x": length, "z": length, "y": height},
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
        9: {"line_id": 9, "node_i": 1, "node_j": 4},
        10: {"line_id": 10, "node_i": 5, "node_j": 8},
    }

    with open("inputs.json", "w") as jsonfile:
        json.dump([nodes, lines, cross_section], jsonfile)

    return nodes, lines


class Parametrization(vkt.Parametrization):
    intro = vkt.Text("# STAAD - Member End Forces App")
    inputs_title = vkt.Text("""## Frame Geometry 
    Please fill in the following parameters to create the steel structure:""")
    frame_length = vkt.NumberField("Frame Length", min=0.3, default=8, suffix="sm")
    frame_height = vkt.NumberField("Frame Height", min=1, default=6, suffix="m")
    line_break = vkt.LineBreak()
    section_title = vkt.Text("""## Frame Cross-Section 
    Please select a cross section for the frame's elements:""")
    cross_sect = vkt.OptionField(
        "Cross-Section", options=["IPE400", "IPE200"], default="IPE400"
    )


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.GeometryView("3D Model", duration_guess=1, x_axis_to_right=True)
    def create_render(self, params, **kwargs):
        nodes, lines = create_frame_data(
            length=params.frame_length, height=params.frame_height
        )
        sections_group = []

        for line_id, dict_vals in lines.items():
            node_id_i = dict_vals["node_i"]
            node_id_j = dict_vals["node_j"]

            node_i = nodes[node_id_i]
            node_j = nodes[node_id_j]
            # IMPORTANT in the parametric model "y" is the vertical dimension in the geometry view z is the vertical dimension
            point_i = vkt.Point(node_i["x"], node_i["z"], node_i["y"])
            point_j = vkt.Point(node_j["x"], node_j["z"], node_j["y"])

            line_k = vkt.Line(point_i, point_j)
            cs_size = float(params.cross_sect[3:]) / 1000
            section_k = vkt.RectangularExtrusion(
                cs_size, cs_size, line_k, identifier=str(line_id)
            )
            sections_group.append(section_k)
        return vkt.GeometryResult(geometry=sections_group)

    @vkt.TableView(
        "Member End Forces", duration_guess=10, update_label="Run STAAD Analysis"
    )
    def run_staad(self, params, **kwargs):
        nodes, lines = create_frame_data(
            length=params.frame_length, height=params.frame_height
        )
        cross_section = params.cross_sect
        input_json = json.dumps([nodes, lines, cross_section])
        script_path = Path(__file__).parent / "run_staad_model.py"
        script = File.from_path(script_path)

        files = [
            ("inputs.json", BytesIO(bytes(input_json, "utf8"))),
        ]

        staad_analysis = PythonAnalysis(
            script=script, files=files, output_filenames=["output.json"]
        )
        staad_analysis.execute(timeout=300)
        output_file = staad_analysis.get_output_file("output.json")
        output_file = json.loads(output_file.getvalue())

        forces = [[round(force, 2) for force in row] for row in output_file["forces"]]

        return vkt.TableResult(
            forces,
            row_headers=output_file["headers"],
            column_headers=[
                "FX [kN]",
                "FY [kN]",
                "FZ [kN] ",
                "MX [kN m]",
                "MY [kN m]",
                "MZ [kN m]",
            ],
        )
```
### run_staad_model.py
```python
import subprocess
import time
import json 
import comtypes.client

from pythoncom import CoInitialize, CoUninitialize
from datetime import datetime
from pathlib import Path
from openstaad import Output

# Staad Vertical dimension is Y
def run_staad():
    CoInitialize()
    # Replace with your version and file path.
    staad_path = r"C:\Program Files\Bentley\Engineering\STAAD.Pro 2024\STAAD\Bentley.Staad.exe" 
    # Launch STAAD.Pro
    staad_process  = subprocess.Popen([staad_path])
    print("Launching STAAD.Pro...")
    time.sleep(15)
    # Connect to OpenSTAAD.
    openstaad = comtypes.client.GetActiveObject("StaadPro.OpenSTAAD")

    # Create a new STAAD file.
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    std_file_path = Path.cwd() / f"Structure_{timestamp}.std" 
    length_unit = 4  # Meter.
    force_unit = 5  # Kilo Newton.
    openstaad.NewSTAADFile(str(std_file_path), length_unit, force_unit)
    
    # Important to add sleeps after creating new file to let staad load the interface
    # Important Wait to load interface
    time.sleep(5)

    # Load lines and nodes 
    # Create joints
    input_json = Path.cwd() / "inputs.json"
    with open(input_json) as jsonfile:
        data = json.load(jsonfile)

    nodes, lines,section_name = data[:]



    # Set Material and Beam Section
    staad_property = openstaad.Property
    staad_property._FlagAsMethod("SetMaterialName")
    staad_property._FlagAsMethod("CreateBeamPropertyFromTable")
    material_name = "STEEL"
    staad_property.SetMaterialName(material_name)

    country_code = 7  # European database.
    # section_name = "IPE400"  # Selected profile.
    type_spec = 0  # ST (Single Section from Table).
    add_spec_1 = 0.0  # Not used for single sections
    add_spec_2 = 0.0  # Must be 0.0.

    # Create the beam property.
    property_no = staad_property.CreateBeamPropertyFromTable(
        country_code, section_name, type_spec, add_spec_1, add_spec_2
    )

    # Create Members.
    geometry = openstaad.Geometry
    geometry._FlagAsMethod("CreateNode")
    geometry._FlagAsMethod("CreateBeam")
    staad_property._FlagAsMethod("AssignBeamProperty")
    
    create_nodes = set()
    for line_id, vals in lines.items():
        node_i_id = str(vals["node_i"])
        node_i_cords = nodes[node_i_id]

        node_j_id = str(vals["node_j"])
        node_j_cords = nodes[node_j_id]

        if node_i_id not in create_nodes:
            geometry.CreateNode(
                int(node_i_id), node_i_cords["x"], node_i_cords["y"], node_i_cords["z"]
            )
        if node_j_id not in create_nodes:
            geometry.CreateNode(
                int(node_j_id), node_j_cords["x"], node_j_cords["y"], node_j_cords["z"]
            )
        geometry.CreateBeam(int(line_id), node_i_id, node_j_id)
        
        # Assign beam property to beam ids.
        _ = staad_property.AssignBeamProperty(int(line_id),property_no)
    
    # Create supports.
    support = openstaad.Support
    support._FlagAsMethod("CreateSupportFixed")
    support._FlagAsMethod("AssignSupportToNode")

    varnSupportNo  = support.CreateSupportFixed()
    # This one can be node when y = 0 so iterate the nodes.
    nodes_with_support = [1,2,5,6]
    for node in nodes_with_support:
        _  =  support.AssignSupportToNode(node,varnSupportNo)
    
    # Create Load cases and add self weight.
    load = openstaad.Load
    load._FlagAsMethod("SetLoadActive")
    load._FlagAsMethod("CreateNewPrimaryLoad")
    load._FlagAsMethod("AddSelfWeightInXYZ")

    case_num = load.CreateNewPrimaryLoad("Self Weight")
    ret = load.SetLoadActive(case_num) # Load Case 1
    ret = load.AddSelfWeightInXYZ(2, -1.0) # Load factor
    
    # Run analysis in silent mode.
    command = openstaad.Command
    command._FlagAsMethod("PerformAnalysis")
    openstaad._FlagAsMethod("SetSilentMode")
    openstaad._FlagAsMethod("Analyze")
    openstaad._FlagAsMethod("isAnalyzing")
    command.PerformAnalysis(6)
    openstaad.SaveModel(1)
    time.sleep(3)
    openstaad.SetSilentMode(1)

    openstaad.Analyze()
    while openstaad.isAnalyzing():
        print("...Analyzing")
        time.sleep(2)

    time.sleep(5)
    # Process Outputs.
    output = Output()
    #  GetMemberEndForces returns -> FX, FY, FZ, MX, MY and MZ (in order).
    end_forces = [list(output.GetMemberEndForces(beam=int(bid), start=False, lc=1)) for bid in lines]
    end_headers = [f"Beam:{lines[bid]['line_id']}/Node:{lines[bid]['node_j']}" for bid in lines]

    # Retrieve start forces and headers
    start_forces = [list(output.GetMemberEndForces(beam=int(bid), start=True, lc=1)) for bid in lines]
    start_headers = [f"Beam:{lines[bid]['line_id']}/Node:{lines[bid]['node_i']}" for bid in lines]

    # Combine forces and headers into lists of lists
    forces = end_forces + start_forces
    headers = end_headers + start_headers

    # Save to JSON file
    json_path = Path.cwd() / "output.json"
    with open(json_path, "w") as jsonfile:
        json.dump({"forces": forces, "headers": headers}, jsonfile)

    openstaad = None
    CoUninitialize()

    staad_process.terminate()
    return ret

if __name__ == "__main__":
    openstaad = run_staad()
```

## Create, Modify and Extend [Important]
You can generate python helpers in the app.py that creates, nodes, lines in the same dict format as the sample `run_staad_model.py`

and you can use this helpers to get:
- Node displacements
- Reaction Loads

```python
def get_displacements(output: OpenSTAADOutput, node_i: int, lc: int = 1) -> dict[str, dict[str, float]]:
    """Retrieves node displacements (converted to mm)."""
    safe_n1 = make_safe_array_double(6)
    x = make_variant_vt_ref(safe_n1, automation.VT_ARRAY | automation.VT_R8)
    output.GetNodeDisplacements(node_i, lc, x)
    return {str(node_i): {"x": x.value[0][0] * 25.4, "y": x.value[0][1] * 25.4, "z": x.value[0][2] * 25.4}}


def get_reaction_loads(output: OpenSTAADOutput, node_id: int, lc: int = 1) -> dict[str, dict[str, float]]:
    """Retrieves support reactions for a node."""
    safe_n1 = make_safe_array_double(6)
    x = make_variant_vt_ref(safe_n1,  automation.VT_ARRAY |  automation.VT_R8)
    output.GetSupportReactions(int(node_id),lc,x)
    Fx, Fy, Fz, *_  = x.value[0]
    return {str(node_id): {"Fx [kN]": round(Fx, 4), "Fy [kN]": round(Fy, 2), "Fz [kN]": round(Fz, 2)}}


def get_all_reactions(output: OpenSTAADOutput, nodes_w_constraints: list[int], lc: int = 1) -> dict[str, dict[str, float]]:
    reactions_dict: dict[str,dict[str,float]] = {}
    for bolt in nodes_w_constraints[:-1]:
        reactions_dict.update(get_reaction_loads(output=output, node_id=bolt, lc=lc))
    return reactions_dict


def get_axial_loads(output, member_id: int, lc: int):
    """
    dMin: Minimun axial Force
    dMinPos: Location where the min load is located
    dMax: Maximun axial force
    dMaxPos: Location of the Max axial force
    """

    # Create a helper function to create a by-reference VARIANT.
    def make_variant_vt_ref(obj, var_type):
        var = automation.VARIANT()
        var._.c_void_p = ctypes.addressof(obj)
        var.vt = var_type | automation.VT_BYREF
        return var

    # Create c_double objects for the output values
    min_val = ctypes.c_double()
    min_pos = ctypes.c_double()
    max_val = ctypes.c_double()
    max_pos = ctypes.c_double()

    # Create VARIANT references for the outputs
    dMin = make_variant_vt_ref(min_val, VT_R8)
    dMinPos = make_variant_vt_ref(min_pos, VT_R8)
    dMax = make_variant_vt_ref(max_val, VT_R8)
    dMaxPos = make_variant_vt_ref(max_pos, VT_R8)

    output._FlagAsMethod("GetMinMaxAxialForce")

    output.GetMinMaxAxialForce(member_id, lc, dMin, dMinPos, dMax, dMaxPos)
    return min_val.value, min_pos.value, max_val.value, max_pos.value


def get_all_max_min_axial_loads(output, load_combos: dict[str, dict], lines: dict[str, dict]):
    member_results = {}
    for memberid in lines:
        combo_vs_load = {}
        for combo_name, combo_args in load_combos.items():
            combo_id = combo_args["lc_num"]
            # member id is an int bcs as required by STAAD.
            dMin, _, dMax, _ = get_axial_loads(output=output, member_id=int(memberid), lc=combo_id)
            max_axial = dMin if abs(dMin) > abs(dMax) else dMax
            combo_vs_load[combo_name] = max_axial

        member_results[memberid] = combo_vs_load

    return member_results
```

Don't worry about sections use IPE200 as a default like the example!
And also remember adding the sleep time in the change of interface like when creating NewSTAADFile