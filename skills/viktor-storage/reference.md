# VIKTOR Storage Reference

Official sources:

- <https://docs.viktor.ai/docs/create-apps/results-and-visualizations/storing-results/>
- <https://docs.viktor.ai/sdk/api/core/#storage>
- <https://docs.viktor.ai/sdk/api/utils/#memoize>

## Mental Model

VIKTOR app jobs are stateless. A view, button, or other controller method runs, returns a result, and finishes. Use `params` for saved user input. Use `vkt.Storage` when app code needs to persist a file-like result under a key and read it in a later job.

Storage data is represented as `vkt.File`. Text and bytes can be stored directly with `vkt.File.from_data(...)`; structured data should be serialized first.

```python
import json
import viktor as vkt


def write_json_to_storage(key: str, payload: dict, *, scope: str = "entity") -> None:
    vkt.Storage().set(
        key,
        data=vkt.File.from_data(json.dumps(payload, indent=2)),
        scope=scope,
    )


def read_json_from_storage(key: str, *, scope: str = "entity") -> dict:
    stored_file = vkt.Storage().get(key, scope=scope)
    return json.loads(stored_file.getvalue_binary().decode("utf-8"))
```

## Supported Operations

Use one `vkt.Storage()` object or instantiate inline. Always pass `scope`.

```python
import viktor as vkt

storage = vkt.Storage()

storage.set("analysis/result.json", data=vkt.File.from_data(b'{"ok": true}'), scope="entity")
result_file = storage.get("analysis/result.json", scope="entity")

all_files = storage.list(scope="entity")
analysis_files = storage.list(prefix="analysis/", scope="entity")

storage.delete("analysis/result.json", scope="entity")
```

| Operation | Use | Notes |
| --- | --- | --- |
| `set(key, data, *, scope, entity=None)` | Store a `vkt.File` under a key. | `key` is a unique string and supports up to 256 characters in SDK `>=14.28.0`. Existing data at the same key and scope is overwritten. |
| `get(key, *, scope, entity=None)` | Retrieve a stored `vkt.File`. | Raises `FileNotFoundError` when the key does not exist in the selected scope. |
| `list(*, prefix=None, scope, entity=None)` | Return stored files for a scope. | Prefer `prefix` when many files may exist. It is faster and avoids scanning unrelated keys. |
| `delete(key, *, scope, entity=None)` | Delete one stored key. | Raises `FileNotFoundError` when deleting a missing key. |

## Scope Selection

| Scope | Use when | App types | Lifetime and sharing |
| --- | --- | --- | --- |
| `entity` | Data belongs to one entity: analysis output, parsed input, generated report source, cached view data, workflow-local state. | `simple`, `tree` | Persistent. Same key in another entity points to another storage zone. |
| `workspace` | Data is shared workspace-wide: reference datasets, shared settings, app-wide expensive cache. | `simple`, `tree` | Persistent. All entities see the same key, so later writes overwrite earlier writes. |
| `session` | Data belongs to one user editor session: temporary editor state, unsaved previews, per-tab intermediate data. | all app types | Deleted when the session ends. Not shared between users. Requires SDK `>=14.28.0`. |

Default to `entity` unless there is a clear reason not to.

## Entity Scope

Entity-scoped storage is assigned to the current entity by default.

```python
vkt.Storage().set(
    "entity_data",
    data=vkt.File.from_data("content set by this entity"),
    scope="entity",
)

current_entity_file = vkt.Storage().get("entity_data", scope="entity")
```

The same key can be reused in a different entity without overwriting the first entity's data. Reading a key from an entity where it was never written raises `FileNotFoundError`.

To read or write another entity's storage, resolve the target `Entity` and pass it with `entity=...`.

```python
target_entity = ...  # for example, from vkt.api_v1.API().get_entity(...)
target_file = vkt.Storage().get("entity_data", scope="entity", entity=target_entity)
```

Use this cross-entity pattern only when the app has a clear relationship between the active entity and the target entity. Otherwise it is easy to couple unrelated entities through hidden state.

## Workspace Scope

Workspace-scoped storage is shared across all entities in the workspace.

```python
vkt.Storage().set(
    "shared/reference_data.json",
    data=vkt.File.from_data(b'{"version": 1}'),
    scope="workspace",
)

reference_file = vkt.Storage().get("shared/reference_data.json", scope="workspace")
```

Any entity can overwrite the same workspace key. Namespace workspace keys by feature, version, or content hash when accidental overwrite would be harmful:

```python
key = f"soil_database/v2/{dataset_id}.json"
```

Use `workspace` as a durable alternative to cache shared by multiple entities. Do not use it for user-specific or entity-specific results.

## Session Scope

Session-scoped storage is available inside the current editor session and is removed when that session closes.

```python
vkt.Storage().set(
    "preview_mesh",
    data=vkt.File.from_data(mesh_json),
    scope="session",
)

preview_file = vkt.Storage().get("preview_mesh", scope="session")
```

Use it for temporary UI state, unsaved previews, editor-only intermediate data, or app types where entity/workspace scope is unavailable. A different user, browser session, or tab should not be expected to see this data.

## Key Naming

Use stable, namespaced keys:

```text
analysis/latest.json
analysis/by-input-hash/<hash>.json
views/moment_contours.json
reports/latest_inputs.json
shared/reference/v2/materials.json
```

Good keys make `list(prefix=...)` useful and prevent unrelated features from overwriting each other.

Avoid storing secrets in VIKTOR Storage. Use environment variables or a dedicated secret store for credentials.

## File Content

Read text payloads with `.getvalue()`.

```python
text = vkt.Storage().get("summary.txt", scope="entity").getvalue()
```

Read binary or JSON payloads with `.getvalue_binary()`.

```python
payload = json.loads(
    vkt.Storage().get("result.json", scope="entity").getvalue_binary().decode("utf-8")
)
```

For large files, use `.open()` or `.open_binary()` and stream content instead of loading everything into memory.

## Missing Storage

Treat missing storage as an expected state when the storage is produced by another job.

```python
try:
    payload = read_json_from_storage("analysis/latest.json")
except FileNotFoundError:
    raise vkt.UserError("Run the analysis first before opening these results.")
```

For agent tool outputs, return a compact recoverable response instead of dumping a traceback:

```python
return {
    "status": "needs_prerequisite",
    "missing_storage_key": "analysis/latest.json",
    "retry_action": {"tool": "run_analysis"},
}
```

## Memoize

Use `@vkt.memoize` for temporary caching of expensive pure functions when inputs and outputs are small compared to compute time.

```python
import viktor as vkt


@vkt.memoize
def run_expensive_calculation(*, width, height, material):
    return calculate(width=width, height=height, material=material)


class Controller(vkt.Controller):

    @vkt.DataView("Results", duration_guess=30)
    def get_data_view(self, params, **kwargs):
        result = run_expensive_calculation(
            width=params.width,
            height=params.height,
            material=params.material,
        )
        return vkt.DataResult(...)
```

Memoize rules:

- The function must be pure: same input gives same output.
- Avoid side effects inside the memoized function. Side effects are skipped on cache hits.
- Prefer keyword-only arguments because positional/keyword differences can produce different cache keys.
- Inputs and outputs must be serializable.
- Keep function names unique within the Python file.
- If multiple decorators are used, put `@vkt.memoize` last.
- Cached results live for at most 24 hours.
- In local development, the cache is local and limited to 50 calls with first-in, first-out cleanup.
- In production, the memoize cache is not limited by the same 50-call development cap.

Use `vkt.Storage` when results must be retrieved by key, retained beyond the cache lifetime, listed, deleted, or inspected. Both mechanisms can reuse work across jobs. Read [long-running-results.md](long-running-results.md) for choosing between them and connecting the result to params or a view.

## Testing

Load `../viktor-testing/SKILL.md` for complete test conventions. Use `mock_Storage` around tests that call `vkt.Storage()`.

```python
import unittest

import viktor as vkt
from munch import munchify
from viktor.testing import mock_Storage

from app import Controller


class TestStorage(unittest.TestCase):

    @mock_Storage(get=[vkt.File.from_data(b'{"status": "ok"}')])
    def test_reads_cached_result(self):
        result = Controller().stored_result_view(params=munchify({}))
        self.assertIsNotNone(result)
```

Prefer assertions on the user-visible result or returned payload. Do not only assert that no exception was raised.
