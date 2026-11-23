# Params Tool Templates

Use these snippets as templates. Rename modules, node ids, and field paths to match the target VIKTOR workflow.

## Table Of Contents

- Module layout
- Response helpers
- Environment and SDK compute
- Workflow node models
- REST entity client
- Workflow entity storage
- Param read/write service
- Tool functions
- Registry snippets
- System prompt snippets
- Propagation snippets
- Things to consider

## Module Layout

```text
agent/
  tools/
    registry.py
    viktor_tools/
      responses.py
      sdk_compute.py
      workflow_entities.py
      workflow_node_params.py
      wind_workflow_tools.py
```

Keep the generic workflow files separate from app-specific compute tools. App-specific tools can import `resolve_workflow_entity`, `read_last_saved_params`, `set_last_saved_params`, `deep_merge_params`, and storage helpers.

## Response Helpers

```python
import json
from typing import Any

from pydantic import ValidationError


def tool_response(status: str, **payload: Any) -> str:
    return json.dumps({"status": status, **payload}, indent=2)


def validation_error_response(
    *,
    tool: str,
    message: str,
    error: Exception,
    retry_tool: str | None = None,
    retry_reason: str | None = None,
) -> str:
    if isinstance(error, ValidationError):
        details: Any = error.errors()
    else:
        details = str(error)

    payload: dict[str, Any] = {
        "tool": tool,
        "message": message,
        "details": details,
    }
    if retry_tool:
        payload["retry_action"] = {
            "tool": retry_tool,
            "reason": retry_reason or "Correct the arguments and retry.",
        }
    return tool_response("validation_error", **payload)


def needs_prerequisite_response(
    *,
    tool: str,
    message: str,
    missing_storage_key: str,
    retry_tool: str,
    retry_reason: str,
) -> str:
    return tool_response(
        "needs_prerequisite",
        tool=tool,
        message=message,
        missing_storage_key=missing_storage_key,
        retry_action={"tool": retry_tool, "reason": retry_reason},
    )


def needs_workflow_run_response(*, tool: str, node_id: str) -> str:
    return tool_response(
        "needs_workflow_run",
        tool=tool,
        node_id=node_id,
        message=(
            "No active workflow entity directory includes this node. "
            "Create or select a workflow run first."
        ),
        retry_action={
            "tool": "create_workflow_entity_directory",
            "reason": "Create or load workflow entities before reading or setting params.",
        },
    )


def execution_error_response(*, tool: str, message: str, error: Exception) -> str:
    return tool_response(
        "execution_error",
        tool=tool,
        message=message,
        error_type=type(error).__name__,
        details=str(error),
    )
```

## Environment And SDK Compute

```python
import os
from typing import Any

import viktor as vkt
from dotenv import load_dotenv


load_dotenv()


def get_required_token() -> str:
    token = os.getenv("TOKEN_VK_APP") or os.getenv("VIKTOR_TOKEN")
    if not token or not token.strip():
        raise ValueError("Missing VIKTOR token. Set TOKEN_VK_APP or VIKTOR_TOKEN.")
    return token.strip()


def normalize_sdk_environment(value: str) -> str:
    environment = value.strip().rstrip("/").lower()
    if not environment:
        raise ValueError("Missing VIKTOR environment.")
    if environment.startswith(("http://", "https://")) or "/" in environment:
        raise ValueError("VIKTOR_ENVIRONMENT must be host-only, for example demo.viktor.ai.")
    if "." not in environment:
        environment = f"{environment}.viktor.ai"
    if not environment.endswith(".viktor.ai"):
        raise ValueError("VIKTOR_ENVIRONMENT must end with .viktor.ai.")
    return environment


def get_optional_environment() -> str | None:
    environment = os.getenv("VIKTOR_ENVIRONMENT")
    if environment and environment.strip():
        return normalize_sdk_environment(environment)
    return None


class ViktorSdkComputeClient:
    def __init__(self, *, token: str | None = None, environment: str | None = None) -> None:
        resolved_token = (token or get_required_token()).strip()
        resolved_environment = (
            normalize_sdk_environment(environment)
            if environment and environment.strip()
            else get_optional_environment()
        )
        if resolved_environment:
            self.api = vkt.api_v1.API(token=resolved_token, environment=resolved_environment)
        else:
            self.api = vkt.api_v1.API(token=resolved_token)

    def compute_method(
        self,
        *,
        workspace_id: int,
        entity_id: int,
        method_name: str,
        params: dict[str, Any],
        timeout: int | None = None,
    ) -> dict[str, Any]:
        workspace = self.api.get_workspace(workspace_id)
        entity = workspace.get_entity(entity_id)
        result = entity.compute(method_name, params=params, timeout=timeout)
        if not isinstance(result, dict):
            raise RuntimeError(f"VIKTOR SDK compute did not return a JSON object: {result}")
        return result


def select_result_key(result: dict[str, Any], result_key: str) -> Any:
    if result_key not in result:
        keys = ", ".join(sorted(result.keys())) or "<none>"
        raise KeyError(f"Result does not contain key '{result_key}'. Available keys: {keys}.")
    return result[result_key]
```

## Workflow Node Models

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


WorkflowNodeId = Literal[
    "wind_turbine_selector",
    "foundation_analysis",
    "cpt_pile_bearing",
    "reinforcement",
    "cost_analysis",
    "allplan_model",
]


class WorkflowAppTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: WorkflowNodeId
    app_name: str
    label: str
    workspace_id: int
    sibling_entity_id: int
    method_name: str
    result_key: str
    storage_key: str
    icon: str
    icon_bg: str
    depends_on: list[WorkflowNodeId] = Field(default_factory=list)


class WorkflowRunEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: WorkflowNodeId
    app_name: str
    label: str
    workspace_id: int
    sibling_entity_id: int
    entity_id: int
    entity_name: str
    url: str
    method_name: str
    result_key: str
    storage_key: str
    icon: str
    icon_bg: str
    depends_on: list[WorkflowNodeId] = Field(default_factory=list)


class WorkflowEntityDirectory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_name: str
    created_at: str
    storage_key: str = "workflow_entity_directory"
    entities: dict[WorkflowNodeId, WorkflowRunEntity]
```

## REST Entity Client

```python
import os
from typing import Any

import requests
from pydantic import BaseModel, ConfigDict


class RestEntityResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    entity_type: int | str
    entity_type_name: str | None = None
    properties: dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    last_saved_params: dict[str, Any] | None = None


class ViktorRestEntityClient:
    def __init__(self, *, token: str | None = None, api_base: str | None = None) -> None:
        self.api_base = (api_base or self.normalize_api_base()).strip().rstrip("/")
        self.auth_headers = {"Authorization": f"Bearer {(token or get_required_token()).strip()}"}
        self.timeout = (5.0, 30.0)

    @staticmethod
    def normalize_api_base() -> str:
        configured_base = os.getenv("VIKTOR_API_BASE")
        if configured_base and configured_base.strip():
            base = configured_base.strip().rstrip("/")
            if not base.startswith("https://"):
                raise ValueError("VIKTOR_API_BASE must be an absolute HTTPS URL.")
            return base if base.endswith("/api") else f"{base}/api"

        environment = get_optional_environment() or "demo.viktor.ai"
        host = environment.strip().rstrip("/")
        if host.startswith("https://"):
            host = host.removeprefix("https://")
        if "/" in host:
            raise ValueError("VIKTOR_ENVIRONMENT must be host-only.")
        return f"https://{host}/api"

    @property
    def ui_base(self) -> str:
        return self.api_base[:-4] if self.api_base.endswith("/api") else self.api_base

    def editor_url(self, *, workspace_id: int, entity_id: int) -> str:
        return f"{self.ui_base}/workspaces/{workspace_id}/app/editor/{entity_id}"

    def get_entity(
        self,
        *,
        workspace_id: int,
        entity_id: int,
        properties: bool = False,
        clean_params: bool = False,
        param_types: bool = False,
    ) -> RestEntityResponse:
        payload = self._request_json(
            "GET",
            f"workspaces/{workspace_id}/entities/{entity_id}/",
            params={
                "properties": str(properties).lower(),
                "clean_params": str(clean_params).lower(),
                "param_types": str(param_types).lower(),
            },
            action="Get entity",
        )
        return RestEntityResponse.model_validate(payload)

    def set_entity_params(
        self,
        *,
        workspace_id: int,
        entity_id: int,
        params: dict[str, Any],
        message: str,
    ) -> None:
        entity = self.get_entity(workspace_id=workspace_id, entity_id=entity_id)
        self._request_json(
            "PUT",
            f"workspaces/{workspace_id}/entities/{entity_id}/",
            json_body={"name": entity.name, "properties": params, "message": message},
            action="Set entity params",
        )

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        action: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        response = requests.request(
            method,
            f"{self.api_base}/{path.lstrip('/')}",
            headers={
                **self.auth_headers,
                **({"Content-Type": "application/json"} if json_body is not None else {}),
            },
            params=params,
            json=json_body,
            timeout=self.timeout,
        )
        if response.ok:
            return response.json() if response.text.strip() else {}
        raise RuntimeError(f"{action} failed (status={response.status_code}): {response.text[:500]}")
```

## Workflow Entity Storage

```python
import copy
from datetime import datetime
from typing import Any

import viktor as vkt


WORKFLOW_ENTITY_DIRECTORY_KEY = "workflow_entity_directory"


class WorkflowEntityStore:
    def __init__(self, *, storage_key: str = WORKFLOW_ENTITY_DIRECTORY_KEY) -> None:
        self.storage_key = storage_key

    def save(self, directory: WorkflowEntityDirectory) -> None:
        vkt.Storage().set(
            self.storage_key,
            data=vkt.File.from_data(directory.model_dump_json(indent=2)),
            scope="entity",
        )

    def try_load(self) -> WorkflowEntityDirectory | None:
        try:
            stored_file = vkt.Storage().get(self.storage_key, scope="entity")
            raw = stored_file.getvalue_binary().decode("utf-8")
            return WorkflowEntityDirectory.model_validate_json(raw)
        except Exception:
            return None

    def load(self) -> WorkflowEntityDirectory:
        directory = self.try_load()
        if directory is None:
            raise FileNotFoundError(f"Missing VIKTOR Storage key '{self.storage_key}'.")
        return directory

    def delete(self) -> None:
        try:
            vkt.Storage().delete(self.storage_key, scope="entity")
        except Exception:
            pass


class WorkflowEntityService:
    def __init__(
        self,
        *,
        store: WorkflowEntityStore | None = None,
        client: ViktorRestEntityClient | None = None,
    ) -> None:
        self.store = store or WorkflowEntityStore()
        self.client = client

    def load_directory(self) -> WorkflowEntityDirectory:
        return self.store.load()

    def resolve_entity(self, node_id: WorkflowNodeId) -> WorkflowRunEntity:
        directory = self.load_directory()
        try:
            return directory.entities[node_id]
        except KeyError as exc:
            raise KeyError(f"Workflow run does not include node '{node_id}'.") from exc

    def read_last_saved_params(self, target: WorkflowRunEntity) -> dict[str, Any]:
        entity = (self.client or ViktorRestEntityClient()).get_entity(
            workspace_id=target.workspace_id,
            entity_id=target.entity_id,
            properties=True,
            clean_params=True,
            param_types=True,
        )
        for value in (entity.properties, entity.params, entity.last_saved_params):
            if isinstance(value, dict) and value:
                return value
        return {}

    def set_last_saved_params(
        self,
        target: WorkflowRunEntity,
        params: dict[str, Any],
        *,
        message: str,
    ) -> None:
        (self.client or ViktorRestEntityClient()).set_entity_params(
            workspace_id=target.workspace_id,
            entity_id=target.entity_id,
            params=params,
            message=message,
        )

    @staticmethod
    def deep_merge(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
        merged = copy.deepcopy(base)
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = WorkflowEntityService.deep_merge(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged


def get_workflow_entity_service() -> WorkflowEntityService:
    return WorkflowEntityService()


def resolve_workflow_entity(node_id: WorkflowNodeId) -> WorkflowRunEntity:
    return get_workflow_entity_service().resolve_entity(node_id)


def read_last_saved_params(target: WorkflowRunEntity) -> dict[str, Any]:
    return get_workflow_entity_service().read_last_saved_params(target)


def set_last_saved_params(target: WorkflowRunEntity, params: dict[str, Any], *, message: str) -> None:
    get_workflow_entity_service().set_last_saved_params(target, params, message=message)


def deep_merge_params(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    return WorkflowEntityService.deep_merge(base, updates)
```

## Param Read/Write Service

```python
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError


class SetParamsInNodeArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: WorkflowNodeId = Field(..., description="Known workflow node id.")
    params: dict[str, JsonValue] = Field(
        ...,
        min_length=1,
        description="JSON-safe saved-param object to write into the node.",
    )
    merge: bool = Field(default=True, description="Deep merge into current saved params.")


class GetParamsInNodeArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: WorkflowNodeId = Field(..., description="Known workflow node id.")


class WorkflowNodeParamService:
    def __init__(self) -> None:
        self.entity_service = get_workflow_entity_service()

    def get_params(self, payload: GetParamsInNodeArgs) -> dict[str, Any]:
        target = self.entity_service.resolve_entity(payload.node_id)
        params = self.entity_service.read_last_saved_params(target)
        return {
            "node_id": payload.node_id,
            "entity_id": target.entity_id,
            "url": target.url,
            "top_level_keys": sorted(params),
            "params": params,
        }

    def set_params(self, payload: SetParamsInNodeArgs) -> dict[str, Any]:
        target = self.entity_service.resolve_entity(payload.node_id)
        updates = dict(payload.params)
        next_params = updates
        if payload.merge:
            current_params = self.entity_service.read_last_saved_params(target)
            next_params = self.entity_service.deep_merge(current_params, updates)

        self.entity_service.set_last_saved_params(
            target,
            next_params,
            message="Agent updated workflow node params.",
        )
        return {
            "node_id": payload.node_id,
            "entity_id": target.entity_id,
            "url": target.url,
            "merge": payload.merge,
            "updated_top_level_keys": sorted(updates),
        }
```

## Tool Functions

```python
async def get_params_in_node_func(context: Any, args: str) -> str:
    try:
        payload = GetParamsInNodeArgs.model_validate_json(args or "{}")
    except ValidationError as exc:
        return validation_error_response(
            tool="get_params_in_node",
            message="Invalid workflow node params arguments.",
            error=exc,
            retry_tool="get_params_in_node",
            retry_reason="Retry with node_id.",
        )

    try:
        result = WorkflowNodeParamService().get_params(payload)
    except (FileNotFoundError, KeyError):
        return needs_workflow_run_response(tool="get_params_in_node", node_id=payload.node_id)
    except Exception as exc:
        return execution_error_response(
            tool="get_params_in_node",
            message="Could not read workflow node saved params.",
            error=exc,
        )

    return tool_response("completed", message="Read workflow node saved params.", **result)


async def set_params_in_node_func(context: Any, args: str) -> str:
    try:
        payload = SetParamsInNodeArgs.model_validate_json(args or "{}")
    except ValidationError as exc:
        return validation_error_response(
            tool="set_params_in_node",
            message="Invalid workflow node params arguments.",
            error=exc,
            retry_tool="set_params_in_node",
            retry_reason="Retry with node_id and a JSON-safe params object.",
        )

    try:
        result = WorkflowNodeParamService().set_params(payload)
    except (FileNotFoundError, KeyError):
        return needs_workflow_run_response(tool="set_params_in_node", node_id=payload.node_id)
    except Exception as exc:
        return execution_error_response(
            tool="set_params_in_node",
            message="Could not update workflow node saved params.",
            error=exc,
        )

    return tool_response("completed", message="Updated workflow node saved params.", **result)
```

## Registry Snippets

```python
from typing import Any

from agents import FunctionTool
from pydantic import BaseModel


TOOL_DISPLAY_NAMES = {
    "get_params_in_node": "Get Params in Node",
    "set_params_in_node": "Set Params in Node",
}


def function_tool(
    name: str,
    description: str,
    schema: type[BaseModel],
    func: Any,
    *,
    strict_json_schema: bool = True,
) -> FunctionTool:
    return FunctionTool(
        name=name,
        description=description,
        params_json_schema=schema.model_json_schema(),
        on_invoke_tool=func,
        strict_json_schema=strict_json_schema,
    )


def get_tools() -> list[Any]:
    return [
        function_tool(
            "get_params_in_node",
            "Read the last saved JSON params from an active workflow node.",
            GetParamsInNodeArgs,
            get_params_in_node_func,
        ),
        function_tool(
            "set_params_in_node",
            "Deep-merge or replace a JSON params object into an active workflow node.",
            SetParamsInNodeArgs,
            set_params_in_node_func,
            strict_json_schema=False,
        ),
    ]
```

## System Prompt Snippets

```xml
<workflow_rules>
  <rule>When the user says they filled or saved inputs manually in a VIKTOR app, call get_params_in_node for that node before running or patching it.</rule>
  <rule>When transferring values into another app, call set_params_in_node explicitly. Do not assume compute tools silently propagate linked params.</rule>
  <rule>For critical handoffs, call get_params_in_node after set_params_in_node and verify saved target values match the producer output before reporting success.</rule>
  <rule>When a dependency is missing, read retry_action.tool and call the prerequisite tool before retrying once.</rule>
</workflow_rules>
```

```xml
<tool name="get_params_in_node">
  <description>Reads the last saved params from an active workflow node.</description>
  <inputs>node_id</inputs>
  <dependencies>create_workflow_entity_directory must complete first.</dependencies>
</tool>
<tool name="set_params_in_node">
  <description>Deep merges or replaces a JSON params object into an active workflow node.</description>
  <inputs>node_id, params, optional merge</inputs>
  <dependencies>create_workflow_entity_directory must complete first.</dependencies>
</tool>
```

## Propagation Snippets

Selector output to foundation mast inputs:

```json
{
  "node_id": "foundation_analysis",
  "merge": true,
  "params": {
    "step_geo": {
      "sec_mast": {
        "mast_diameter": 5.0,
        "mast_vertical_load": 4000.0,
        "mast_horizontal_load": 1500.0,
        "mast_moment": 150000.0
      }
    }
  }
}
```

Foundation reactions to CPT required-depth sizing:

```json
{
  "node_id": "cpt_pile_bearing",
  "merge": true,
  "params": {
    "step2": {
      "sec_load": {"design_load": 5120.5},
      "sec_pile": {"pile_diameter": 500}
    }
  }
}
```

Foundation moments to reinforcement load combinations:

```json
{
  "node_id": "reinforcement",
  "merge": true,
  "params": {
    "tab_geometry": {"height": 4500},
    "tab_loading": {
      "combinations": [
        {"label": "Min m_xD+", "M_Ed": -650.0, "N_Ed": 0},
        {"label": "Max m_xD-", "M_Ed": 720.0, "N_Ed": 0}
      ]
    }
  }
}
```

Compute tool output with a follow-up patch:

```python
return tool_response(
    "completed",
    message="Computed required pile length. Patch foundation params next.",
    storage_key="cpt_pile_bearing_data",
    required_pile_length_m=required_length,
    next_param_update={
        "tool": "set_params_in_node",
        "node_id": "foundation_analysis",
        "merge": True,
        "params": {
            "step_geo": {
                "sec_piles": {
                    "pile_length": required_length,
                    "pile_diameter": pile_diameter,
                }
            }
        },
    },
)
```

## Things To Consider

- Use `Literal[...]` for known node ids when the workflow is fixed.
- Use `str` node ids only when the app genuinely supports arbitrary user-defined graph nodes.
- Keep VIKTOR saved params and VIKTOR result storage separate.
- Deep merge nested params; replace only on explicit user request.
- Preserve table/list structures exactly.
- Do not flatten VIKTOR params unless the target app expects flattened fields.
- Return compact output from tools, but include `entity_url` when it helps the user inspect the app.
- Add readback checks for values that affect engineering safety, sizing, or cost.
- Keep low-level REST details out of the system prompt; put them in code.
