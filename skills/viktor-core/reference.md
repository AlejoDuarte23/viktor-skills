# VIKTOR Basics

## App structure

```text
my-app
├── app.py
├── requirements.txt
└── viktor.config.toml
```

- **app.py** – controllers & logic
- **requirements.txt** – Python deps incl. viktor‑sdk
- **viktor.config.toml** – app config

## VIKTOR skeleton
```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    intro = vkt.Text("""# Application Title
This is the app description.....
""")
    input_1 = vkt.NumberField('Input 1')

class Controller(vkt.Controller):
    parametrization = Parametrization  # Always add this
    # method and view keep reading
```


Key attributes from Controller: `parametrization`, `summary`, `label`, `children`, view/action methods, `@ParamsFromFile`.

### Parametrization & params

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    # App title and description and title as above
    input_1 = vkt.TextField('Text')
    input_2 = vkt.NumberField('Number')

class Controller(vkt.Controller):
    parametrization = Parametrization # IMPORTANT
```

### Simple view

```python
import viktor as vkt

class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Results")
    def results(self, params, **kwargs):
        data = [[1, 2], [3, 4]]
        return vkt.TableResult(
            data,
            row_headers=["Row 1", "Row 2"],
            column_headers=["Col 1", "Col 2"]
        )
```

Use `params.<field>` inside views to access input.

---

## Execution flow

A **job** starts when:

- Input changes
- View refresh / tab enter
- Action button click
- `on_next` in step editors
- `@ParamsFromFile` upload

Each job: call method → return result → finish. Code is **stateless**; only `params` persist.

### Example (cube)

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    length = vkt.NumberField("L", default=1)
    width  = vkt.NumberField("W", default=1)
    height = vkt.NumberField("H", default=1)

class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Results")
    def results(self, p, **kwargs):
        volume  = p.length * p.width * p.height
        surface = 2*(p.length*p.width + p.length*p.height + p.width*p.height)
        return vkt.TableResult(
            [[volume, "m³"], [surface, "m²"]],
            row_headers=["Volume", "Surface"],
            column_headers=["Value", "Unit"]
        )
```

## A Note about Controller

Do not define a method named **summary** on Controller, it conflicts with VIKTOR internals and overwrites the entity summary

Use another name for helper functions, for example make_summary, build_summary_text, or similar

# VIKTOR  Layout

> Exact index of the **Layout** section. Each item reproduces the example used on the referenced page. No additions.

## Tabs & sections

**Creating tabs**

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    tab_1 = vkt.Tab('Tab 1')
    tab_1.title = vkt.Text('# Tab 1 - title')
    tab_1.input_1 = vkt.TextField('This is a text field')
    tab_1.input_2 = vkt.NumberField('This is a number field')

    tab_2 = vkt.Tab('Tab 2')
    tab_2.input_1 = vkt.TextField('Text field in Tab 2')
    tab_2.input_2 = vkt.NumberField('Number field in Tab 2')
```

**Creating sections**
if there is a vkt.Section, no orphan vkt.Text or any  or input component should exist in the parametrization. The correct way is:
Important: * You can't create a vkt.Section inside of and existing vkt.Section, they should be independent.

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    section_1 = vkt.Section('Section 1')
    section_1.title = vkt.Text('# Section 1')
    section_1.input_1 = vkt.TextField('This is a text field')
    section_1.input_2 = vkt.NumberField('This is a number field')

    section_2 = vkt.Section('Section 2')
    section_2.title = vkt.Section('# Section 2')
    section_2.input_1 = vkt.TextField('Text field in Section 2')
    section_2.input_2 = vkt.NumberField('Number field in Section 2')
```

**Three layers: Tab → Section → Fields**
if there is a vkt.Tab or vkt.Section, no orphan vkt.Text or any  or input component should exist in the parametrization. The correct way is:

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    tab_1 = vkt.Tab('Tab 1')
    tab_1.section_1 = vkt.Section('Section 1')
    tab_1.section_1.title = vkt.Text('# Section 1')
    tab_1.section_1.input_1 = vkt.TextField('This is a text field')
    tab_1.section_1.input_2 = vkt.NumberField('This is a number field')

    tab_1.section_2 = vkt.Section('Section 2')
    ...
    tab_2 = vkt.Tab('Tab 2')
    ...
```

**Hide a Tab / Section**

```python
vkt.Tab("Tab 2", visible=vkt.Lookup("tab_1.param_x"))
```

```python
vkt.Tab("Tab 2", visible=get_visible)
```

**Expand a Section**

```python
vkt.Section("Section", initially_expanded=True)
```

---

## Pages

**Assume an editor with a GeometryView and a DataView**

```python
import viktor as vkt

class Controller(vkt.Controller):

    @vkt.GeometryView(...)
    def geometry_view(...):
        ...

    @vkt.DataView(...)
    def data_view(...):
        ...
```

**Define two Pages, second page shows the views**

if there is a vkt.Page or vkt.Section, no orphan vkt.Text or any  or input component should exist in the parametrization. The correct way is:

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    page_1 = vkt.Page('Page 1 - without views')
    page_1.title = vkt.Text('## This is Page 1')
    page_1.input_1 = vkt.TextField('This is a text field')
    page_1.input_2 = vkt.NumberField('This is a number field')

    page_2 = vkt.Page('Page 2 - with views', views=['geometry_view', 'data_view'])
    page_2.title = vkt.Text('## This is Page 2')    
    page_2.input_1 = vkt.TextField('This is a text field')
    page_2.input_2 = vkt.NumberField('This is a number field')
```

**Hide a Page**

```python
vkt.Page("Page 2", visible=vkt.Lookup("page_1.param_x"))
```

```python
vkt.Page("Page 2", visible=get_visible)
```

---

## Steps

**Create two Steps, second step shows the views**
if there is a vkt.Steps no orphan vkt.Text or any  or input component should exist in the parametrization. The correct way is:

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    step_1 = vkt.Step('Step 1 - without views')
    step_1.title = vkt.Text('# This is Step 1')
    step_1.input_1 = vkt.TextField('This is a text field')
    step_1.input_2 = vkt.NumberField('This is a number field')

    step_2 = vkt.Step('Step 2 - with views', views=['geometry_view', 'data_view'])
    step_1.title = vkt.Text('# This is Step 1')
    step_2.input_1 = vkt.TextField('This is a text field')
    step_2.input_2 = vkt.NumberField('This is a number field')
```


# VIKTOR containers, plain text trees, dot notation

This guide uses the official VIKTOR docs as the source of truth. It shows two independent trees, one for a Pages app, and one for a Steps app. Use dot notation for every path. Choose one navigation model, Pages or Steps, never both.

## Pages app, tree and paths

```text
class Parametrization
page_a
page_a.views #['my_view1', 'my_view2']
page_a.tab_a
page_a.tab_a.inputs              # Section
page_a.tab_a.inputs.title = vkt.Text('Revenue and options')
page_a.tab_a.inputs.table        # Table
page_a.tab_a.inputs.table.month = vkt.TextField('Month')
page_a.tab_a.inputs.table.revenue = vkt.NumberField('Revenue')
page_a.tab_a.inputs.sensitivity = vkt.NumberField('Sensitivity, percent')

page_a.tab_b
page_a.tab_b.options             # Section
page_a.tab_b.options.horizon = vkt.OptionField('Horizon, months', options=[3, 6, 12])

page_b
page_b.views  #['my_view3']
page_b.section_a                 # Section
page_b.section_a.table           # Table
page_b.section_a.table.x = vkt.NumberField('X')
page_b.section_a.table.y = vkt.NumberField('Y')
```

**Runtime param paths**

* First table rows, `params.page_a.tab_a.inputs.table`
* Sensitivity, `params.page_a.tab_a.inputs.sensitivity`
* Horizon, `params.page_a.tab_b.options.horizon`
* Page B table, `params.page_b.section_a.table`

## Steps app, tree and paths

```text
# Parametrization
step1 # Add views
step1.tab1
step1.tab1.section1
step1.tab1.section1.title
step1.tab1.section1.table
step1.tab1.section1.table.col_a
step1.tab1.section1.table.col_b
step1.tab1.section1.target

step2 # Add views
step2.section1
step2.section1.title
step2.section1.input_a
```

**Runtime param paths in Controller**

* First table rows, `params.step1.tab1.section1.table`
* Target, `params.step1.tab1.section1.target`
* Step two input, `params.step2.section1.input_a`

## Rules that prevent breakage

* Bind views on every Page or Step using `views=[...]`, otherwise the views do not render.
* Tabs contain Sections only, Sections contain fields, including Table, and text goes in `section.title = vkt.Text(...)`.
* Place every Table inside a Section. Never attach a Table directly to Page, Tab, or Step.
* Do not mix Pages and Steps in one app. Pick one navigation model.
* Do not create `step1.page1` or any Page inside a Step. That structure is invalid.
* Do not create orphan fields at the top level. Always nest fields inside a Section.
* Use `vkt`, not `vkt`.

# Do not nest `Section` inside another `Section`

A `Section` must sit directly under `Parametrization`, or under a `Step`, a `Page`, or a `Tab`. A `Section` cannot contain another `Section`. Nesting `Section` objects, for example `inputs.loads = vkt.Section(...)` when `inputs` is already a `Section`, breaks the UI schema and the app fails. Use separate top level sections, then attach fields to each section.

---

## Wrong, a section inside a section

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    inputs = vkt.Section('Inputs')

    # Loads
    inputs.loads = vkt.Section('Factored loads')
    inputs.loads.Pu = vkt.NumberField('Axial Pu (compression +)', default=200.0, suffix=' kip')
    inputs.loads.Mx = vkt.NumberField('Moment Mx about x (tension on +y)', default=600.0, suffix=' kip-in')
    inputs.loads.My = vkt.NumberField('Moment My about y (tension on +x)', default=0.0, suffix=' kip-in')
    inputs.loads.Vu = vkt.NumberField('Base shear Vu', default=20.0, suffix=' kip')
    inputs.loads.shear_dir = vkt.OptionField(
        'Shear direction for breakout', options=['x', 'y'], default='x', variant='radio-inline'
    )

    # Pedestal, concrete
    inputs.pedestal = vkt.Section('Pedestal, support')
    inputs.pedestal.fc = vkt.NumberField("Concrete f'c", default=4.0, suffix=' ksi')
    inputs.pedestal.Bp = vkt.NumberField('Pedestal length Bp (x)', default=24.0, suffix=' in')
    inputs.pedestal.Dp = vkt.NumberField('Pedestal width Dp (y)', default=24.0, suffix=' in')
    inputs.pedestal.grout_t = vkt.NumberField('Grout thickness', default=0.5, suffix=' in')
    inputs.pedestal.cracked = vkt.BooleanField('Cracked concrete at anchors? (psi_c=0.7)', default=True)

class Controller(vkt.Controller):
    parametrization = Parametrization
```

---

## Correct, flat sections with fields

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    # Loads, top level section
    loads = vkt.Section('Factored loads')
    loads.Pu = vkt.NumberField('Axial Pu, compression positive', default=200.0, suffix=' kip')
    loads.Mx = vkt.NumberField('Moment Mx about x, tension on positive y', default=600.0, suffix=' kip-in')
    loads.My = vkt.NumberField('Moment My about y, tension on positive x', default=0.0, suffix=' kip-in')
    loads.Vu = vkt.NumberField('Base shear Vu', default=20.0, suffix=' kip')
    loads.shear_dir = vkt.OptionField(
        'Shear direction for breakout', options=['x', 'y'], default='x', variant='radio-inline'
    )

    # Pedestal, top level section
    pedestal = vkt.Section('Pedestal, support')
    pedestal.fc = vkt.NumberField("Concrete f'c", default=4.0, suffix=' ksi')
    pedestal.Bp = vkt.NumberField('Pedestal length Bp, x', default=24.0, suffix=' in')
    pedestal.Dp = vkt.NumberField('Pedestal width Dp, y', default=24.0, suffix=' in')
    pedestal.grout_t = vkt.NumberField('Grout thickness', default=0.5, suffix=' in')
    pedestal.cracked = vkt.BooleanField('Cracked concrete at anchors, psi_c equals 0.7', default=True)

class Controller(vkt.Controller):
    parametrization = Parametrization
```

---

## Allowed containers for a `Section`

* Direct child of `Parametrization`
* Inside a `Step`
* Inside a `Page`
* Inside a `Tab`

---

## One line rule for the agent

Use separate sections, no nested sections. For example, use `pedestal` and `pedestal.fc`, do not write `inputs.pedestal` when `inputs` is a `Section`.


## **Correct Usage of Titles in Parametrization with vkt.Section, vkt.Pages, vkt.Tab, vkt.Step [Important]**

Always place vkt.Text at the **lowest level inside a container**, such as inside a single Section. Never attach vkt.Text directly to Step, Page, or Tab, because the application will fail. The correct approach is to nest vkt.Text inside a Section.


✅ Correct pattern:

```
class Parametrization(vkt.Parametrization):
    step1 = vkt.Step('Step 1', views=['my_view1'])
    step1.inputs = vkt.Section('Inputs')
    step1.inputs.intro = vkt.Text("""
        # Items and Target
        Enter the required data below.
    """)
```

```
class Parametrization(vkt.Parametrization):
    page_a = vkt.Page('Forecast', views=['my_view1', 'my_view2'])
    page_a.tab_a = vkt.Tab('Series')
    page_a.tab_a.series = vkt.Section('Series data')
    page_a.tab_a.series.intro = vkt.Text("""
        ## Series
        Enter the observed series values, one row per period.
    """)
```

⚠️ This is **wrong**. The application will fail if you try to assign vkt.Text directly to a container like Section, Page, Tab, or Step.

### **Wrong examples**

```python
class Parametrization(vkt.Parametrization):
    # Step with bound view
    step1 = vkt.Step('step1', views=['my_view1'])
    step1.title = vkt.Text("""# Items and Target""")  # ❌ WRONG

    # Section under the step
    step1.inputs = vkt.Section('inputs')
```

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    # Page with two views bound
    page_a = vkt.Page('Forecast', views=['my_view1', 'my_view2'])
    page_a.title = vkt.Text('## Forecast')  # ❌ WRONG

    # Tab A: Series input table
    page_a.tab_a = vkt.Tab('Series')
    page_a.tab_a.title = vkt.Text('## Series')  # ❌ WRONG
    page_a.tab_a.series = vkt.Section('Series data')
    page_a.tab_a.series.title = vkt.Text('Enter observed series values, one row per period')
```

## Minimal working templates

### Pages template

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    page_a = vkt.Page('Data', views=['my_view1'])
    page_a.tab_a = vkt.Tab('Input')
    page_a.tab_a.inputs = vkt.Section('Revenue and options')
    page_a.tab_a.inputs.table = vkt.Table('Monthly revenue')
    page_a.tab_a.inputs.table.month = vkt.TextField('Month')
    page_a.tab_a.inputs.table.revenue = vkt.NumberField('Revenue')

class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView('My View 1')
    def my_view1(self, params, **kwargs):
        rows = params.page_a.tab_a.inputs.table or []
        out = [[r.get('month', ''), float(r.get('revenue', 0) or 0)] for r in rows]
        return vkt.TableResult(out, column_headers=['Month', 'Revenue'])
```

### Steps template

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    step1 = vkt.Step('Step one', views=['my_view1'])
    step1.tab1 = vkt.Tab('Input')
    step1.tab1.section1 = vkt.Section('Data entry')
    step1.tab1.section1.table = vkt.Table('Pairs')
    step1.tab1.section1.table.col_a = vkt.TextField('Label')
    step1.tab1.section1.table.col_b = vkt.NumberField('Value')

class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView('My View 1')
    def my_view1(self, params, **kwargs):
        rows = params.step1.tab1.section1.table or []
        out = [[r.get('col_a', ''), float(r.get('col_b', 0) or 0)] for r in rows]
        return vkt.TableResult(out, column_headers=['Label', 'Value'])
```


## Example A, simple Section, with a Section title and a Table

> Standalone example file. Do not combine with other examples.

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    # One top level Section
    inputs = vkt.Section('Input data')
    inputs.title = vkt.Text('Provide monthly revenue, month is optional')

    inputs.table = vkt.Table('Monthly revenue')
    inputs.table.month = vkt.TextField('Month')
    inputs.table.revenue = vkt.NumberField('Revenue', default=0)

    inputs.horizon = vkt.OptionField('Forecast horizon, months', options=[3, 6, 12], default=6)

class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView('My View 1')
    def my_view1(self, params, **kwargs):
        """Show a simple echo of the entered data."""
        rows = []
        for r in params.inputs.table or []:
            month = r.get('month')
            revenue = float(r.get('revenue', 0) or 0)
            rows.append([month or '', revenue])
        headers = ['Month', 'Revenue']
        return vkt.TableResult(rows, column_headers=headers)
```

Notes

* No orphan fields, every field sits under `inputs`, a Section.
* The controller reads `params.inputs.*` and returns a TableResult.

---

## Example B, Step with a Section that contains a Table

> Standalone example file. Do not combine with other examples.

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    step_a = vkt.Step('Step A, input', views=['my_view1'])
    step_a.inputs = vkt.Section('Data entry')
    step_a.inputs.title = vkt.Text('Fill the table, then pick a target')

    step_a.inputs.table = vkt.Table('Data table')
    step_a.inputs.table.label = vkt.TextField('Label')
    step_a.inputs.table.value = vkt.NumberField('Value', default=0)

    step_a.inputs.target = vkt.NumberField('Target sum', default=100)

class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView('My View 1')
    def my_view1(self, params, **kwargs):
        total = 0.0
        rows_in = params.step_a.inputs.table or []
        rows_out = []
        for r in rows_in:
            label = r.get('label') or ''
            val = float(r.get('value', 0) or 0)
            total += val
            rows_out.append([label, val])
        rows_out.append(['Total', total])
        rows_out.append(['Target', float(params.step_a.inputs.target or 0)])
        return vkt.TableResult(rows_out, column_headers=['Item', 'Value'])

```

Notes

* The Step contains a Section, the Section contains the Table and other fields.
* You can't create a vkt.Section inside of and existing vkt.Section, they should be independent
* The controller reads `params.step_a.inputs.*`.

---

## Example C, Page with a Tab, with a Section, with a Table, with two views

> Standalone example file. Do not combine with other examples.

````python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    page_a = vkt.Page('Forecast', views=['my_view1', 'my_view2'])

    # Tab under the Page
    page_a.tab_a = vkt.Tab('Inputs')

    # Section under the Tab
    page_a.tab_a.inputs = vkt.Section('Revenue and options')
    page_a.tab_a.inputs.title = vkt.Text(
        'Paste monthly revenue, then choose horizon and sensitivity'
    )

    # Table under the Section
    page_a.tab_a.inputs.table = vkt.Table('Monthly revenue, one row per month')
    page_a.tab_a.inputs.table.month = vkt.TextField('Month, optional')
    page_a.tab_a.inputs.table.revenue = vkt.NumberField('Revenue', default=0)

    # Extra inputs in the same Section
    page_a.tab_a.inputs.horizon = vkt.OptionField('Horizon, months', options=[3, 6, 12], default=6)
    page_a.tab_a.inputs.sensitivity = vkt.NumberField('Sensitivity, percent', min=-20, max=20, step=1, default=0)

class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView('My View 1')
    def my_view1(self, params, **kwargs):
        rows = params.page_a.tab_a.inputs.table or []
        out = []
        for idx, r in enumerate(rows, start=1):
            out.append([idx, float(r.get('revenue', 0) or 0)])
        return vkt.TableResult(out, column_headers=['Index', 'Revenue'])

    @vkt.TableView('My View 2')
    def my_view2(self, params, **kwargs):
        rows = params.page_a.tab_a.inputs.table or []
        horizon = int(params.page_a.tab_a.inputs.horizon or 0)
        sens = float(params.page_a.tab_a.inputs.sensitivity or 0)

        series = [float(r.get('revenue', 0) or 0) for r in rows]
        if not series:
            return vkt.TableResult([], column_headers=['Step', 'Value'])
        last_val = series[-1]
        adj = last_val * (sens / 100.0)
        base = last_val + adj
        out = [[i, round(base, 2)] for i in range(1, horizon + 1)]
        return vkt.TableResult(out, column_headers=['Step', 'Value'])

````

Notes

* Containers are nested Page, Tab, Section, Table.
* The controller uses full paths, `params.page_a.tab_a.inputs.*`.

---

**Button labels**

```python
vkt.Step('Step 2', previous_label='Go to step 1', next_label='Go to step 3')
```

**Validation of user input (on\_next)**

```python
import viktor as vkt

def validate_step_1(params, **kwargs):
    if params.step_1.width > params.step_1.height:
        raise vkt.UserError("The design is not feasible")

class Parametrization(vkt.Parametrization):
    step_1 = vkt.Step('Step 1', on_next=validate_step_1)
    step_1.width = vkt.NumberField('Width')
    step_1.height = vkt.NumberField('Height')
```

**Signature with explicit kwargs**

```python
def validate_step_1(params, entity_id, entity_name, workspace_id, **kwargs):
    ...
```

**Disable a Step**

```python
vkt.Step("Step 2", enabled=vkt.Lookup("step_1.param_x"))
```

```python
def get_enabled(params, **kwargs):
    return params.step_1.param_y > 5

vkt.Step("Step 2", enabled=get_enabled)
```

```python
_step_enabled = vkt.And(
    vkt.IsFalse(vkt.Lookup('step_1.param_x')),
    vkt.IsEqual(vkt.Lookup('step_1.param_y'), 5)
)

step = vkt.Step("Step 2", enabled=_step_enabled)
```

**Width per Step**

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    step_1 = vkt.Step("Step 1", width=30)
    ...
    step_2 = vkt.Step("Step 2", width=70)
    ...
```

---

## Adjust the parametrization width

```python
class Controller(vkt.Controller):
    parametrization = Parametrization(width=60)
```

```python
class Parametrization(vkt.Parametrization):
    number = vkt.NumberField("Number", flex=100)

class Controller(vkt.Controller):
    parametrization = Parametrization(width=30)
```

---
# View Decorators and Their Result Classes

A concise reference mapping each `vkt` view decorator to its corresponding result class, with minimal runnable examples.

---

## 1. `DataView` → `DataResult`

```python
@vkt.DataView("Data Analysis")
def view_data(self, params, **kwargs):
    data = vkt.DataGroup(
        vkt.DataItem("Value", 123.45, suffix="units")
    )
    return vkt.DataResult(data)
```

## 2. `GeometryView` → `GeometryResult`

```python
@vkt.GeometryView("3D Visualization")
def view_geometry(self, params, **kwargs):
    cube = vkt.RectangularExtrusion(1, 1, vkt.Line(vkt.Point(0, 0, 0), vkt.Point(0, 0, 1)))
    return vkt.GeometryResult(cube)
```

## 3. `GeometryAndDataView` → `GeometryAndDataResult`

```python
@vkt.GeometryAndDataView("3D with Data")
def view_geometry_data(self, params, **kwargs):
    cube = vkt.RectangularExtrusion(1, 1, vkt.Line(vkt.Point(0, 0, 0), vkt.Point(0, 0, 1)))
    data = vkt.DataGroup(vkt.DataItem("Volume", 1.0, suffix="m³"))
    return vkt.GeometryAndDataResult(cube, data)
```

## 4. `MapView` → `MapResult`

```python
@vkt.MapView("Map Visualization")
def view_map(self, params, **kwargs):
    point = vkt.MapPoint(52.0, 4.0, title="Location")
    return vkt.MapResult([point])
```

## 5. `MapAndDataView` → `MapAndDataResult`

```python
@vkt.MapAndDataView("Map with Data")
def view_map_data(self, params, **kwargs):
    point = vkt.MapPoint(52.0, 4.0, title="Location")
    data = vkt.DataGroup(vkt.DataItem("Coordinates", "52.0, 4.0"))
    return vkt.MapAndDataResult([point], data)
```

## 6. `GeoJSONView` → `GeoJSONResult`

```python
@vkt.GeoJSONView("GeoJSON Data")
def view_geojson(self, params, **kwargs):
    geojson = {"type": "Point", "coordinates": [4.0, 52.0]}
    return vkt.GeoJSONResult(geojson)
```

## 7. `GeoJSONAndDataView` → `GeoJSONAndDataResult`

```python
@vkt.GeoJSONAndDataView("GeoJSON with Data")
def view_geojson_data(self, params, **kwargs):
    geojson = {"type": "Point", "coordinates": [4.0, 52.0]}
    data = vkt.DataGroup(vkt.DataItem("Location", "Amsterdam"))
    return vkt.GeoJSONAndDataResult(geojson, data)
```

## 8. `PlotlyView` → `PlotlyResult`

```python
@vkt.PlotlyView("Interactive Plot")
def view_plotly(self, params, **kwargs):
    import plotly.graph_objects as go
    fig = go.Figure(data=go.Bar(x=["A", "B", "C"], y=[1, 3, 2]))
    return vkt.PlotlyResult(fig)
```

## 9. `PlotlyAndDataView` → `PlotlyAndDataResult`

```python
@vkt.PlotlyAndDataView("Plot with Data")
def view_plotly_data(self, params, **kwargs):
    import plotly.graph_objects as go
    fig = go.Figure(data=go.Bar(x=["A", "B", "C"], y=[1, 3, 2]))
    data = vkt.DataGroup(vkt.DataItem("Max Value", 3))
    return vkt.PlotlyAndDataResult(fig, data)
```

## 10. `ImageView` → `ImageResult`

```python
@vkt.ImageView("Image Display")
def view_image(self, params, **kwargs):
    import matplotlib.pyplot as plt
    import io

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 2])
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    return vkt.ImageResult(buffer)
```

## 11. `ImageAndDataView` → `ImageAndDataResult`

```python
@vkt.ImageAndDataView("Image with Data")
def view_image_data(self, params, **kwargs):
    import matplotlib.pyplot as plt
    import io

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 2])
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    data = vkt.DataGroup(vkt.DataItem("Data Points", 3))
    return vkt.ImageAndDataResult(buffer, data)
```

## 12. `WebView` → `WebResult`

```python
@vkt.WebView("Web Content")
def view_web(self, params, **kwargs):
    html = "<h1>Hello World</h1><p>This is HTML content</p>"
    return vkt.WebResult(html=html)
```

## 13. `WebAndDataView` → `WebAndDataResult`

```python
@vkt.WebAndDataView("Web with Data")
def view_web_data(self, params, **kwargs):
    html = "<h1>Report</h1><p>Analysis complete</p>"
    data = vkt.DataGroup(vkt.DataItem("Status", "Complete"))
    return vkt.WebAndDataResult(html=html, data=data)
```

## 14. `PDFView` → `PDFResult`

```python
@vkt.PDFView("PDF Document")
def view_pdf(self, params, **kwargs):
    pdf_file = vkt.File.from_path("report.pdf")
    return vkt.PDFResult(file=pdf_file)
```

## 15. `TableView` → `TableResult`

```python
@vkt.TableView("Data Table")
def view_table(self, params, **kwargs):
    import pandas as pd

    df = pd.DataFrame({
        "Name": ["A", "B", "C"],
        "Value": [1, 2, 3],
    })
    return vkt.TableResult(df)
```

## 16. `IFCView` → `IFCResult`

```python
@vkt.IFCView("IFC Model")
def view_ifc(self, params, **kwargs):
    ifc_file = vkt.File.from_path("model.ifc")
    return vkt.IFCResult(ifc_file)
```

## 17. `IFCAndDataView` → `IFCAndDataResult`

```python
@vkt.IFCAndDataView("IFC with Data")
def view_ifc_data(self, params, **kwargs):
    ifc_file = vkt.File.from_path("model.ifc")
    data = vkt.DataGroup(vkt.DataItem("Elements", 150))
    return vkt.IFCAndDataResult(ifc_file, data)
```

---

## Key Points

* Pair every view decorator with its matching result class.
* Decorators ending with **`AndDataView`** combine a visual result with a `DataResult` style panel.
* Use `duration_guess` to control loading indication for long calculations.
* Apply `visible`, `description`, and other optional arguments for conditional display and documentation.
* Some views, such as `GeometryView`, offer extra parameters (e.g., `view_mode`) to adjust rendering behaviour.

