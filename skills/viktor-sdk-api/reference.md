# VIKTOR SDK API Reference

Sources:

- https://docs.viktor.ai/docs/api/
- https://docs.viktor.ai/docs/api/sdk/
- https://docs.viktor.ai/docs/api/sdk/handling-entity-data/
- https://docs.viktor.ai/docs/api/sdk/running-entity-computation/

## What the SDK API is

The SDK API is available through `vkt.api_v1` and is built on top of the REST API. Use it from Python when possible because it handles pagination, filtering by reference, and object serialization.

Available resource areas documented on the SDK API page:

- Workspaces
- Entity types
- Entities
- Revisions
- Current user

## Access modes

Inside the current workspace:

```python
api = vkt.api_v1.API()
entity = api.get_entity(1)
```

Cross-workspace from a VIKTOR app:

```python
api = vkt.api_v1.API(token=os.environ["TOKEN"])
workspace = api.get_workspace(4)
entity = workspace.get_entity(1)
```

External Python script or notebook:

```python
api = vkt.api_v1.API(
    token=os.environ["TOKEN"],
    environment="cloud.us1.viktor.ai",
)
workspace = api.get_workspace(3)
entity = workspace.get_entity(1)
```

Install `viktor` first when using the SDK API outside an app:

```shell
pip install viktor
```

## Current workspace and entity context

VIKTOR passes `workspace_id`, `entity_id`, and `entity_name` into view methods and callback functions. Use those values to construct the current entity and navigate to related data.

```python
current_entity = vkt.api_v1.API().get_entity(entity_id)
parent = current_entity.parent()
parent_params = parent.last_saved_params
```

Within one job, repeated API calls are memoized temporarily. This is useful in option callbacks that repeatedly read the same parent or related entity.

## Privileged access

Some API calls are limited by the access rights of the current user. The `privileged=True` flag can bypass those restrictions for selected calls, but only after enabling the privileged API in `viktor.config.toml`:

```toml
enable_privileged_api = true
```

Use it narrowly:

```python
settings_entity = api.get_root_entities(
    entity_type_names=["Settings"],
    privileged=True,
)[0]
```

Review privileged usage carefully because confidential data can leak through views, summaries, downloads, or other outputs.

## Navigating entities

Ways to obtain entity objects:

```python
entity = api.get_workspace(workspace_id).get_entity(entity_id)
children = api.get_entity_children(entity_id)
siblings = api.get_entity_siblings(entity_id)
parent = api.get_entity_parent(entity_id)
entities = api.get_workspace(workspace_id).get_entities_by_type("MyType")
roots = api.get_workspace(workspace_id).get_root_entities()
entity = params.entity_field
```

Inside the current workspace, the workspace part can be omitted:

```python
entity = api.get_entity(entity_id)
```

Navigate relatives from an `Entity`:

```python
parent = entity.parent()
children = entity.children()
siblings = entity.siblings()
grand_parent = entity.parent().parent()
gef_children = entity.children(entity_type_names=["GEF"])
```

## Excluding params

By default, entity params are included when entity data is fetched. Use `include_params=False` when only identity, name, or type data is required:

```python
gef_children = entity.children(
    entity_type_names=["GEF"],
    include_params=False,
)
```

## Reading entity data

Get historical revisions:

```python
revisions = api.get_entity_revisions(entity_id)
revisions = entity.get_revisions()
params = revisions[0].params
```

Read the most common current data directly from the entity:

```python
params = entity.last_saved_params
summary = entity.last_saved_summary
```

For file-type entities:

```python
file = api.get_entity_file(entity_id)
file = entity.get_file()
```

## Modifying entity data

API-level methods:

```python
api.rename_entity(entity_id, new_name)
api.delete_entity(entity_id)
api.set_entity_params(entity_id, new_params)
api.create_child_entity(parent_entity_id, entity_type_name, new_entity_name)
```

Entity-level methods:

```python
entity.rename(new_name)
entity.delete()
entity.set_entity_params(new_params)
entity.create_child(entity_type_name, new_entity_name)
```

Use explicit confirmation for destructive changes such as delete operations when working interactively.

## List objects

Some methods return list objects such as `EntityList`, not plain `list[Entity]`. Normal operations like length checks, positive/negative indexing, and iteration are supported:

```python
children = entity.children()
len(children)
children[0]
children[-1]
for child in children:
    ...
```

Slicing list objects is not supported:

```python
children[0:5]  # not supported
```

## Running entity computations

The SDK API can run supported methods on an entity:

```python
api.entity_compute(
    workspace_id=1,
    entity_id=2,
    method_name="my_calculation",
    params={...},
)

workspace = api.get_workspace(1)
workspace.entity_compute(
    entity_id=2,
    method_name="my_calculation",
    params={...},
)

entity = api.get_entity(2)
entity.compute(method_name="my_calculation", params={...})
```

Rules:

- Only view methods and button methods are supported for compute calls.
- `compute` cannot be used on an entity in the caller's own development workspace; it returns a `TimeoutError`.
- The running-entity-computation docs mark this feature as new in VIKTOR v14.12.0.
