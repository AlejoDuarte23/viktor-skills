# VIKTOR SDK API Examples

## Read parent params inside a view

```python
import viktor as vkt


class Controller(vkt.Controller):
    @vkt.DataView("Data")
    def calculate_view(self, params, entity_id, entity_name, workspace_id, **kwargs):
        api = vkt.api_v1.API()
        current_entity = api.get_entity(entity_id)
        parent_params = current_entity.parent().last_saved_params

        data = vkt.DataGroup(
            vkt.DataItem("Parent name", parent_params.get("name", "-")),
        )
        return vkt.DataResult(data)
```

## Build option values from a parent entity

```python
import viktor as vkt


def get_options(params, entity_id, entity_name, workspace_id, **kwargs):
    current_entity = vkt.api_v1.API().get_entity(entity_id)
    parent_params = current_entity.parent().last_saved_params
    return parent_params.get("available_options", [])


class Parametrization(vkt.Parametrization):
    field = vkt.OptionField("Option", options=get_options)
```

## Cross-workspace entity read

```python
import os

import viktor as vkt


api = vkt.api_v1.API(token=os.environ["TOKEN"])
workspace = api.get_workspace(4)
entity = workspace.get_entity(1)
params = entity.last_saved_params
summary = entity.last_saved_summary
```

## Read children without params for faster navigation

```python
api = vkt.api_v1.API()
entity = api.get_entity(entity_id)

gef_children = entity.children(
    entity_type_names=["GEF"],
    include_params=False,
)

child_names = [child.name for child in gef_children]
```

## Update an entity's params

```python
api = vkt.api_v1.API(token=os.environ["TOKEN"])
entity = api.get_workspace(workspace_id).get_entity(entity_id)

new_params = dict(entity.last_saved_params)
new_params["status"] = "Reviewed"
entity.set_entity_params(new_params)
```

## Run a remote view computation

```python
import os

import viktor as vkt


class Controller(vkt.Controller):
    @vkt.GeometryView("Geometry", duration_guess=5)
    def geometry_view_from_other_entity(self, params, **kwargs):
        api = vkt.api_v1.API(token=os.environ["TOKEN"])
        entity = api.get_workspace(other_workspace_id).get_entity(other_entity_id)
        result = entity.compute(
            "geometry_view",
            params=entity.last_saved_params,
        )
        return vkt.GeometryResult(**result["geometry"])
```
