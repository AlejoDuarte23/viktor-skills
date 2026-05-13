# VIKTOR Table And Data View Examples

## Table Result

```python
import viktor as vkt


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Design checks")
    def design_checks(self, params, **kwargs):
        rows = [
            ["Bearing pressure", 120, 180, "OK"],
            ["Sliding", 0.72, 1.00, "OK"],
        ]
        return vkt.TableResult(
            rows,
            column_headers=["Check", "Demand", "Capacity", "Status"],
        )
```

## Data Result

```python
class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.DataView("Summary")
    def summary(self, params, **kwargs):
        data = vkt.DataGroup(
            vkt.DataItem("Utilization", 0.72, suffix="-"),
            vkt.DataItem("Status", "OK"),
        )
        return vkt.DataResult(data)
```

## Dynamic Data Items

```python
items = [vkt.DataItem(name, value, suffix=unit) for name, value, unit in calculated_values]
return vkt.DataResult(vkt.DataGroup(*items))
```
