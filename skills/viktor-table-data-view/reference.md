# TableView

The **TableView** provides a simple way to display tabular data with a CSV download option. It uses a WebView and prioritizes simplicity over styling flexibility.

---

* Display data in a table
* Download as CSV
* Sorting and filtering (enabled if columns are homogeneous)
* Custom headers for rows and columns
* Styling support (per-cell, row, or column)
* Transposing tables
* Pandas DataFrame/Styler integration

### Basic Example

```python
import viktor as vkt
from datetime import date

class Controller(vkt.Controller):
    @vkt.TableView("Student Grades")
    def table_view(self, params, **kwargs):
        data = [
            [128, "John", 6.9, False, date(1994, 6, 3)],
            [129, "Jane", 8.1, True, date(1995, 1, 24)],
            [130, "Mike", 7.5, False, date(1989, 12, 4)],
        ]
        return vkt.TableResult(data)
```

---

## TableResult
```python
class viktor.views.TableResult(
    data,
    *,
    column_headers=None,
    row_headers=None,
    enable_sorting_and_filtering=None
)
```

### Parameters
- **data**: list of lists, DataFrame, or Styler.
- **column_headers**: optional list of column titles or styled headers.
- **row_headers**: optional list of row titles or styled headers.
- **enable_sorting_and_filtering**: toggle sorting/filtering (default auto).

### Usage Examples

**Basic table:**
```python
data = [[1.5, "Square"], [3.1, "Circle"]]
vkt.TableResult(data)
```

**With column headers:**
```python
data = [[1.5, "Square"], [3.1, "Circle"]]
vkt.TableResult(data, column_headers=["Area [m²]", "Shape"])
```

**With styling:**
```python
from viktor import Color, TableCell, TableHeader

data = [
    [1.5, "Square"],
    [TableCell(3.1, text_color=Color.green()),
     TableCell("Circle", background_color=Color(211, 211, 211), text_style='italic')]
]

vkt.TableResult(data, column_headers=[
    TableHeader("Area [m²]", num_decimals=2),
    TableHeader("Shape", align='center')
])
```

**Transposed:**
```python
data = [[1.5, "Square"], [3.1, "Circle"]]
transposed = [list(i) for i in zip(*data)]

vkt.TableResult(
    transposed,
    row_headers=[
        TableHeader("Area [m²]", num_decimals=2),
        TableHeader("Shape", align='center")
    ],
    column_headers=["Object 1", "Object 2"]
)
```


### Syntax and studs
Use the following arguments to use the function
```python
class TableCell:
    value: Incomplete
    text_color: Incomplete
    background_color: Incomplete
    def __init__(self, value: TableCellValue, *, text_color: Color | None = None, background_color: Color | None = None, text_style: Literal['bold', 'italic'] | None = None) -> None: ...

class TableResult(_ViewResult):
    data: Incomplete
    column_headers: Incomplete
    row_headers: Incomplete
    enable_sorting_and_filtering: Incomplete
    def __init__(self, data: Sequence[Sequence[TableCellValue | TableCell]] | pd.DataFrame | Styler, *, column_headers: Sequence[str | TableHeader] | None = None, row_headers: Sequence[str | TableHeader] | None = None, enable_sorting_and_filtering: bool | None = None) -> None: ...
```

# DataView

## Purpose
- Groups results in a tree structure, up to three levels deep.
- Displays flat lists or nested groups.
- Works with `DataResult` to render values.

## Signature
```python
@vkt.DataView("Title")
def method(self, params, **kwargs) -> vkt.DataResult:
    ...
```
- Always return a `DataResult` that wraps a `DataGroup`.

---

## vkt.  DataGroup

### Syntax
```python
class viktor.views.DataGroup(*args, **kwargs)
```

### Arguments
- `*args`: positional `DataItem` objects.
- `**kwargs`: keyworded `DataItem` objects (keys allow use in **Summary**).
- Maximum of 100 `DataItem` objects in total.

### Methods
- `.add(*items)`: Append items to an existing group (since v14.22.0).
- `DataGroup.from_data_groups([group1, group2])`: Combine multiple groups. Keys must be unique.

### ⚠️ Common mistakes
- Do **not** pass `prefix`, `suffix`, `status`, `status_message`, or `number_of_decimals` to `DataGroup`. These belong to `DataItem`.

---

## DataItem

### Syntax
```python
class viktor.views.DataItem(
    label, value=None, subgroup=None,
    *, prefix='', suffix='', number_of_decimals=None,
    status=vkt.DataStatus.INFO, status_message='', explanation_label=''
)
```

### Arguments
- `label (str)`: Description of the value.
- `value (str | float | None)`: Actual data shown.
- `subgroup (DataGroup | None)`: Nested items, depth ≤ 3.
- `prefix (str)`: Text before value (example: €).
- `suffix (str)`: Text after value (example: N).
- `number_of_decimals (int)`: Rounding, numbers only.
- `status (DataStatus)`: INFO, SUCCESS, WARNING, or ERROR.
- `status_message (str)`: Explains why a status applies.
- `explanation_label (str)`: Short note between label and value.

### ⚠️ Common mistakes
- Do **not** use `number_of_decimals` with non-numeric values.
- `subgroup` must be a `DataGroup`, not a list.

---

## Examples

### 1) Minimal
```python
class Controller(vkt.Controller):
    @vkt.DataView("Results")
    def visualize_data(self, params, **kwargs):
        data = vkt.DataGroup(
            vkt.DataItem("Data item 1", 123)
        )
        return vkt.DataResult(data)
```

### 2) Keyworded items with formatting
```python
class Controller(vkt.Controller):
    @vkt.DataView("Results")
    def visualize_data(self, params, **kwargs):
        value_a, value_b = 1.0, 2.0
        total = value_a + value_b

        data = vkt.DataGroup(
            totals=vkt.DataItem(
                "Totals", "",
                subgroup=vkt.DataGroup(
                    value_a=vkt.DataItem("Value A", value_a, prefix="€", number_of_decimals=2),
                    value_b=vkt.DataItem("Value B", value_b, prefix="€", number_of_decimals=2,
                                         explanation_label="= 2 × Value A"),
                    sum=vkt.DataItem("Sum", total, prefix="€", number_of_decimals=2,
                                     status=vkt.DataStatus.SUCCESS)
                )
            )
        )
        return vkt.DataResult(data)
```

### 3) Dynamic group (loop)
```python
class Controller(vkt.Controller):
    @vkt.DataView("Results")
    def visualize_data(self, params, **kwargs):
        entries = {"item 1": 1, "item 2": 2, "item 3": 3}
        items = [vkt.DataItem(label, val) for label, val in entries.items()]
        data = vkt.DataGroup(*items)
        return vkt.DataResult(data)
```

### 4) Status and message
```python
class Controller(vkt.Controller):
    @vkt.DataView("Cost check")
    def visualize_data(self, params, **kwargs):
        prices = {"Apple": 0.20, "Pineapple": 1.80, "Milk": 1.00, "Cheese": 2.50}
        cart_items = [vkt.DataItem(name, price, prefix="€") for name, price in prices.items()]
        total = sum(prices.values())

        status = vkt.DataStatus.SUCCESS if total <= 5 else vkt.DataStatus.WARNING
        msg = "" if total <= 5 else "Budget exceeded"

        data = vkt.DataGroup(
            vkt.DataItem(
                "Shopping cart total", total, prefix="€",
                status=status, status_message=msg,
                subgroup=vkt.DataGroup(*cart_items)
            )
        )
        return vkt.DataResult(data)
```

---

## Key Takeaways
- Only `DataItem` supports formatting arguments.
- `DataGroup` only accepts `DataItem` objects, either positional or keyworded.
- Maximum depth: 3 levels.
- Use keyword arguments in `DataGroup` for **Summary** mapping.
- Always wrap the top-level group in `DataResult`. 
