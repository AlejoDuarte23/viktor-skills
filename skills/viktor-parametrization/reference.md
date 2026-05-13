## NumberField

The first argument, the name of the input field, is required. All other parameters are optional. Example below shows usage with all optional parameters:

```python
number = vkt.NumberField(
    'Insert a Number here',     # required: field label
    default=7.5,                # optional: prefilled value
    description="Tooltip info",# optional: additional information
    flex=50,                    # optional: field width (0–100, default=33)
    min=0,                      # optional: minimum value
    max=10,                     # optional: maximum value
    name="n",                   # optional: param reference (params.n)
    prefix="€",                  # optional: prefix in UI
    suffix="mm",                 # optional: suffix in UI
    step=0.5,                    # optional: increment/decrement step
    variant='slider'             # optional: slider view (requires min and max)
)
```

```python
import viktor as vkt
class Parametrization(vkt.Parametrization):
    number = vkt.NumberField('Insert a Number here')
    slider = vkt.NumberField('Adjust the Number', min=0, max=8, variant='slider')
```

## OptionField

The first argument, the name of the input field, is required. All other parameters are optional. Example below shows usage with all optional parameters:

```python
option = vkt.OptionField(
    'Pick your favorite fruit',         # required: field label
    options=fruits,                     # required: available options (list of strings, numbers, or OptionListElement objects)
    autoselect_single_option=True,       # optional: auto-select if only one option is available
    default="Coconut",                  # optional: prefilled value
    description="Tooltip info",         # optional: additional information
    flex=50,                             # optional: field width (0–100, default=33)
    name="o",                            # optional: param reference (params.o)
    prefix="..",                         # optional: prefix in UI
    suffix="..",                         # optional: suffix in UI
    variant='radio'                      # optional: field style ('radio' or 'radio-inline')
)
```

### OptionField - UI variants
The option list can be display to the user interface as vertical radio elements or in-line (horizontal)
```python
import viktor as vkt

fruits = ['Avocado', 'Banana', 'Coconut']

class Parametrization(vkt.Parametrization):
    option = vkt.OptionField('Pick your favorite fruit', options=fruits)
    radio_v = vkt.OptionField('Pick your favorite fruit', options=fruits, variant='radio')
    radio_h = vkt.OptionField('Pick your favorite fruit', options=fruits, variant='radio-inline')
```

### OptionField - Option Formats
```python
# As list of strings
options=['Avocado', 'Banana', 'Coconut']

# As list of numbers
options=[1, 2, 3]

# As OptionListElement objects
options=[
    OptionListElement(value=1, label="Avocado"),  # params.option will be 1
    OptionListElement(value=2, label="Banana"),
    OptionListElement(value=3, label="Coconut"),
]
```

### OptionField - Using a Function
```python
import viktor as vkt

# Important the inputs should be params and **kwargs
def get_material_options(params, **kwargs):
    if params.material_group == 'Aluminium':
        return ['Aluminium 5083', 'Aluminium 6082']
    elif params.material_group == 'Steel':
        return ['Steel S355', 'Steel S690']
    else:
        return []

class Parametrization(vkt.Parametrization):
    material_group = vkt.OptionField('Material group', options=['Aluminium', 'Steel'])
    material_type = vkt.OptionField('Material', options=get_material_options)
```

## Table

The **vkt.Table** allows users to input structured rows of data. Columns are defined with **dot-notation** using other input fields (e.g., `TextField`, `NumberField`).

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    table = vkt.Table('Input Table')
    table.col_1 = vkt.TextField('Text Column')
    table.col_2 = vkt.NumberField('Number Column')
```

### Options
- **default**: prefill rows
- **description**: tooltip info
- **name**: param reference (`params.t`)
- **visible**: conditional visibility

```python
table = vkt.Table(
    'Input Table',
    default=[{'col_1': 'A', 'col_2': 1}],
    description="Enter rows of values",
    name="t",
    visible=vkt.Lookup("other_field")
)
```

### Data Access
User input is available as a list of dictionaries:
```python
params.table
# Example:
# [{"col_1": "entry1", "col_2": 10}, {"col_1": "entry2", "col_2": 20}]
```



## Important: Orphan `vkt.Table`
Just like `vkt.Text`, a **`vkt.Table`** cannot be orphan when using container fields such as **`vkt.Section`**, **`vkt.Step`**, **`vkt.Tab`**, or **`vkt.Page`**. The table must be attached to a container.

❌ Wrong (orphan `vkt.Table`):
```python
class Parametrization(vkt.Parametrization):
    table = vkt.Table('Input Table')
    table.col_1 = vkt.TextField('Text Column')
    soil = vkt.Section('Soil parameters')
```

✅ Correct (attach `vkt.Table` inside a container):
```python
class Parametrization(vkt.Parametrization):
    soil = vkt.Section('Soil parameters')
    soil.table = vkt.Table('Input Table')
    soil.table.col_1 = vkt.TextField('Text Column')
    soil.table.col_2 = vkt.NumberField('Number Column')
```

The same rule applies to **`vkt.Step`**, **`vkt.Tab`**, and **`vkt.Page`**. Always declare the container first, then assign the `vkt.Table` and its columns as child attributes of that container.


---

## Important: `Table` inside containers and column ownership
If the app uses a container like `vkt.Section`, `vkt.Step`, `vkt.Tab`, or `vkt.Page`, do not leave the `Table` at the top level. The `Table` must be defined inside the container, and each column must be attached to the `Table` object, not to the container, and not at the top level. Otherwise it fails.

❌ Wrong, orphan `Table`, and orphan columns:
```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    app_outline = vkt.Section('Application Description')

    # Wrong, this Table is not inside the Section
    table = vkt.Table('Input Table')

    # Wrong, this column is not attached to the Table object
    col_1 = vkt.TextField('Text Column')
```

✅ Correct, place `Table` inside the container, attach columns to the `Table`:
```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    app_outline = vkt.Section('Application Description')

    # Table belongs to the Section
    app_outline.table = vkt.Table('Input Table')
    # Columns belong to the Table
    app_outline.table.col_1 = vkt.TextField('Text Column')
    app_outline.table.col_2 = vkt.NumberField('Number Column')
```

The same rule applies to `vkt.Step`, `vkt.Tab`, and `vkt.Page`. Declare the container first, then create the `Table` on that container, then attach the column fields on the `Table`.

### Column keys and default rows
- The keys in `params.table` are the column attribute names, unless you set an explicit `name` on the column.
- When you set a `default` with rows, the keys in each row must match the column keys.

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    sec = vkt.Section('Data')

    sec.tbl = vkt.Table(
        'Measurements',
        default=[{'id': 'A1', 'value': 10.0}],  # keys match column names below
        name='tbl'
    )
    # If you set name on a column, that name becomes the key in params
    sec.tbl.id = vkt.TextField('ID')                    # key: 'id'
    sec.tbl.value = vkt.NumberField('Value', name='v')  # key: 'v'

# Result shape
# params.tbl == [{'id': 'A1', 'v': 10.0}]

### Access in Controller
When a `Table` is inside a container, access it through the container name. For example:
```python
# Access values in controller
for row in params.app_outline.table:
    text_value = row['col_1']
    number_value = row['col_2']
```
Here the path is `params.app_outline.table.col_1` and `params.app_outline.table.col_2` depending on how you defined the column keys.
```

## Table Supported and No Supported

Use this note for **Table** only, not DynamicArray.

## NumberField inside a table

* Do not set min or max, VIKTOR ignores them and logs warnings
* Do not use the slider variant

## Input table, unsupported behaviors

* No defaults when adding a new row
* OptionField options cannot use a label
* Users can create rows, not columns
* Any min or max on fields inside the table is ignored

## Input table, supported fields

* TextField, NumberField, IntegerField, BooleanField, OptionField, AutocompleteField

## Input table, not supported fields

* Text, TextAreaField, DateField, OutputField, HiddenField, LineBreak, MultiSelectField, EntityOptionField, ChildEntityOptionField, SiblingEntityOptionField, EntityMultiSelectField, ChildEntityMultiSelectField, SiblingEntityMultiSelectField, FileField, MultiFileField, GeoPointField, GeoPolylineField, GeoPolygonField, ColorField, ActionButton, DownloadButton, OptimizationButton, SetParamsButton


## OutputField Usage

An OutputField can display a textual or numeric value within a parametrization that cannot be modified by the user. The value can be static or dynamic.

**Important:** The value of the OutputField is not included in `params`.

### OutputField - Simple Read Only Values
The OutputField is the simplest way of show a numeric result without generating a view, the output field displays a single numeric or text value directly in the Parametrization so the user can see it. However the output can NOT be accesss in the controler trought params.
```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    output = vkt.OutputField('Output', value=3.1415)
```

### OutputField - Dynamic value with function

For more complex cases, use a callback function. The platform passes `params`, `entity_id`, `entity_name`, and `workspace_id` (>= v14.7.1) to the function.

```python
import viktor as vkt

def sum_x_y(params, **kwargs):
    return params.param_x + params.param_y

class Parametrization(vkt.Parametrization):
    param_x = vkt.NumberField('X')
    param_y = vkt.NumberField('Y')
    output = vkt.OutputField('X + Y', value=sum_x_y)
```

## BooleanField

The BooleanField acts as a toggle button which can be either `True` or `False`.

### BooleanField - Basic usage

```python
import viktor as vkt

class Parametrization(vkt.Parametrization):
    is_true = vkt.BooleanField('False / True')
```

The value can be obtained via `params` and can be:

* `True`: when toggled on
* `False`: when toggled off

### BooleanField - With all optional parameters

The first argument (field label) is required. All other parameters are optional.

```python
is_true = vkt.BooleanField(
    'False / True',              # required: field label
    default=True,                # optional: prefilled value
    description="Tooltip info",  # optional: additional information
    flex=50,                     # optional: field width (0–100, default=33)
    name="b",                    # optional: param reference (params.b)
    visible=True                  # optional: conditional visibility
)
```

