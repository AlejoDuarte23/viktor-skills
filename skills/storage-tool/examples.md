# Storage And View Templates

Use these snippets to implement entity-scoped storage handoffs and storage-controlled WebViews.

## Table Of Contents

- Storage key naming
- JSON storage helpers
- Response helpers
- Producer tool template
- Consumer tool template
- Show/hide view tool template
- VIKTOR `visible=` callback
- WebView rendering template
- Workflow graph state template
- Optimization study storage template
- Things to consider

## Storage Key Naming

Use stable constants:

```python
SELECTOR_STORAGE_KEY = "wind_turbine_selector_data"
FOUNDATION_STORAGE_KEY = "wind_turbine_foundation_data"
FOUNDATION_PARAMS_STORAGE_KEY = "wind_turbine_foundation_params"
CPT_STORAGE_KEY = "cpt_pile_bearing_data"
REINFORCEMENT_STORAGE_KEY = "wind_turbine_reinforcement_data"
COST_STORAGE_KEY = "wind_turbine_cost_data"
ALLPLAN_STORAGE_KEY = "allplan_model_schedule"

WORKFLOW_GRAPH_STATE_STORAGE_KEY = "workflow_graph_state"
WORKFLOW_ENTITY_DIRECTORY_KEY = "workflow_entity_directory"

OPTIMIZATION_STUDY_STORAGE_KEY = "wind_turbine_cost_optimization_study"
SHOW_OPTIMIZATION_RESULTS_KEY = "show_optimization_results"

PLOTLY_VIEW_STORAGE_KEY = "foundation_moment_contours_plotly"
SHOW_PLOTLY_VIEW_KEY = "show_foundation_moment_contours"
```

Naming rules:

- use noun phrases for data keys
- prefix visibility keys with `show_`
- avoid user-specific values in keys
- keep keys stable across app versions when old sessions should still load

## JSON Storage Helpers

```python
import json
from typing import Any

import viktor as vkt


def write_json_to_storage(key: str, payload: Any) -> None:
    vkt.Storage().set(
        key,
        data=vkt.File.from_data(json.dumps(payload, indent=2)),
        scope="entity",
    )


def read_json_from_storage(key: str) -> Any:
    stored_file = vkt.Storage().get(key, scope="entity")
    if not stored_file:
        raise FileNotFoundError(f"Missing VIKTOR Storage key '{key}'.")
    return json.loads(stored_file.getvalue_binary().decode("utf-8"))


def delete_storage_key(key: str) -> None:
    try:
        vkt.Storage().delete(key, scope="entity")
    except Exception:
        pass


def set_visibility(key: str, action: str) -> None:
    if action not in {"show", "hide"}:
        raise ValueError("Visibility action must be 'show' or 'hide'.")
    vkt.Storage().set(key, data=vkt.File.from_data(action), scope="entity")


def get_visibility(key: str) -> bool:
    try:
        return vkt.Storage().get(key, scope="entity").getvalue() == "show"
    except Exception:
        return False
```

## Result Selection Helper

```python
def select_result_key(result: dict[str, Any], result_key: str) -> Any:
    if result_key not in result:
        keys = ", ".join(sorted(result.keys())) or "<none>"
        raise KeyError(f"Result does not contain key '{result_key}'. Available keys: {keys}.")
    return result[result_key]


def select_and_store_result(
    *,
    result: dict[str, Any],
    result_key: str,
    storage_key: str,
) -> Any:
    payload = select_result_key(result, result_key)
    write_json_to_storage(storage_key, payload)
    return payload
```

Common result keys:

```python
RESULT_KEY_PRIORITY = [
    "data",
    "table",
    "download",
    "geometry",
    "plotly",
    "geojson",
    "web",
    "pdf",
    "image",
    "ifc",
    "optimization",
    "set_params",
]
```

## Response Helpers

```python
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
```

## Producer Tool Template

```python
async def run_producer_tool_func(context: Any, args: str) -> str:
    try:
        payload = ProducerToolArgs.model_validate_json(args or "{}")
        target = resolve_workflow_entity("producer_node")
        saved_params = read_last_saved_params(target)
        compute_payload = deep_merge_params(saved_params, payload.model_dump(exclude_none=True))
    except (FileNotFoundError, KeyError):
        return needs_workflow_run_response(tool="run_producer_tool", node_id="producer_node")
    except (ValidationError, ValueError) as exc:
        return validation_error_response(
            tool="run_producer_tool",
            message="Invalid producer arguments.",
            error=exc,
            retry_tool="run_producer_tool",
        )

    try:
        result = ViktorSdkComputeClient().compute_method(
            workspace_id=target.workspace_id,
            entity_id=target.entity_id,
            method_name=target.method_name,
            params=compute_payload,
            timeout=300,
        )
        data = select_and_store_result(
            result=result,
            result_key=target.result_key,
            storage_key=target.storage_key,
        )
    except Exception as exc:
        return execution_error_response(
            tool="run_producer_tool",
            message="Producer compute or storage write failed.",
            error=exc,
        )

    return tool_response(
        "completed",
        message="Producer result stored.",
        entity_id=target.entity_id,
        entity_url=target.url,
        storage_key=target.storage_key,
        summary=summarize_producer_data(data),
    )
```

## Consumer Tool Template

```python
async def run_consumer_tool_func(context: Any, args: str) -> str:
    try:
        upstream_data = read_json_from_storage(PRODUCER_STORAGE_KEY)
    except FileNotFoundError:
        return needs_prerequisite_response(
            tool="run_consumer_tool",
            message="Missing producer output in VIKTOR Storage.",
            missing_storage_key=PRODUCER_STORAGE_KEY,
            retry_tool="run_producer_tool",
            retry_reason="Run the producer before the consumer.",
        )

    try:
        payload = ConsumerToolArgs.model_validate_json(args or "{}")
        target = resolve_workflow_entity("consumer_node")
        saved_params = read_last_saved_params(target)
        handoff_patch = build_consumer_patch(upstream_data)
        compute_payload = deep_merge_params(saved_params, handoff_patch)
        compute_payload = deep_merge_params(compute_payload, payload.model_dump(exclude_none=True))
        set_last_saved_params(
            target,
            compute_payload,
            message="Agent patched consumer params from upstream storage.",
        )
    except (ValidationError, KeyError, ValueError) as exc:
        return validation_error_response(
            tool="run_consumer_tool",
            message="Could not build consumer inputs from upstream data.",
            error=exc,
            retry_tool="run_producer_tool",
        )

    try:
        result = ViktorSdkComputeClient().compute_method(
            workspace_id=target.workspace_id,
            entity_id=target.entity_id,
            method_name=target.method_name,
            params=compute_payload,
            timeout=300,
        )
        data = select_and_store_result(
            result=result,
            result_key=target.result_key,
            storage_key=target.storage_key,
        )
    except Exception as exc:
        return execution_error_response(
            tool="run_consumer_tool",
            message="Consumer compute or storage write failed.",
            error=exc,
        )

    return tool_response(
        "completed",
        message="Consumer result stored.",
        storage_key=target.storage_key,
        summary=summarize_consumer_data(data),
    )
```

## Show/Hide View Tool Template

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError


VIEW_DATA_KEY = "view_payload"
SHOW_VIEW_KEY = "show_view_payload"


class ShowHideViewArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["show", "hide"]


async def show_hide_view_func(context: Any, args: str) -> str:
    try:
        payload = ShowHideViewArgs.model_validate_json(args or "{}")
    except ValidationError as exc:
        return validation_error_response(
            tool="show_hide_view",
            message="Invalid view visibility arguments.",
            error=exc,
            retry_tool="show_hide_view",
        )

    if payload.action == "show":
        try:
            vkt.Storage().get(VIEW_DATA_KEY, scope="entity")
        except Exception:
            return tool_response(
                "needs_prerequisite",
                tool="show_hide_view",
                message="No view payload exists to display.",
                missing_storage_key=VIEW_DATA_KEY,
                retry_action={
                    "tool": "run_view_producer",
                    "reason": "Run and store the view payload first.",
                },
            )

    try:
        set_visibility(SHOW_VIEW_KEY, payload.action)
    except Exception as exc:
        return execution_error_response(
            tool="show_hide_view",
            message="Could not update view visibility.",
            error=exc,
        )

    return tool_response(
        "completed",
        message=f"View set to {payload.action}.",
        visibility=payload.action,
        storage_key=SHOW_VIEW_KEY,
    )
```

## VIKTOR `visible=` Callback

```python
def get_view_visibility(params, **kwargs) -> bool:
    if not params.chat:
        delete_storage_key(SHOW_VIEW_KEY)
        return False

    try:
        visible = vkt.Storage().get(SHOW_VIEW_KEY, scope="entity").getvalue() == "show"
        vkt.Storage().get(VIEW_DATA_KEY, scope="entity")
        return visible
    except Exception:
        return False
```

## WebView Rendering Template

```python
def _empty_html(message: str = "") -> str:
    body = ""
    if message:
        body = (
            "<div style='display:grid;place-items:center;min-height:100vh;"
            "font-family:system-ui,sans-serif;color:#64748b;background:#f8fafc;'>"
            f"{message}</div>"
        )
    return (
        "<!doctype html><html><head><style>"
        "body{margin:0;background:#fff;}"
        "</style></head><body>"
        f"{body}"
        "</body></html>"
    )


@vkt.WebView("Stored Results", width=100, visible=get_view_visibility)
def stored_results_view(self, params, **kwargs):
    try:
        raw = read_json_from_storage(VIEW_DATA_KEY)
        html = StoredResultsViewer(raw).write()
        return vkt.WebResult(html=html)
    except Exception:
        return vkt.WebResult(html=_empty_html("No results are available yet."))
```

## Self-Contained HTML Viewer Template

```python
import base64
import json
from typing import Any


class StoredResultsViewer:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def write(self) -> str:
        encoded = base64.b64encode(json.dumps(self.payload).encode("utf-8")).decode("ascii")
        return HTML_TEMPLATE.replace("__DATA__", encoded)


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Stored Results</title>
  <style>
    body { margin: 0; font-family: system-ui, sans-serif; background: #f8fafc; color: #111827; }
    main { width: min(1120px, calc(100vw - 32px)); margin: 0 auto; padding: 24px 0; }
    pre { white-space: pre-wrap; background: #fff; border: 1px solid #d6dee9; border-radius: 8px; padding: 16px; }
  </style>
</head>
<body>
  <main>
    <h1>Stored Results</h1>
    <pre id="payload"></pre>
  </main>
  <script>
    const payload = JSON.parse(atob("__DATA__"));
    document.getElementById("payload").textContent = JSON.stringify(payload, null, 2);
  </script>
</body>
</html>"""
```

## Workflow Graph State Template

```python
import viktor as vkt
from pydantic import BaseModel, Field


WORKFLOW_GRAPH_STATE_STORAGE_KEY = "workflow_graph_state"


class PlanTodo(BaseModel):
    id: str
    label: str
    status: str = "pending"
    description: str | None = None


class WorkflowPlan(BaseModel):
    id: str = "workflow-plan"
    title: str
    description: str | None = None
    todos: list[PlanTodo] = Field(default_factory=list)
    max_visible_todos: int = 6


class WorkflowCanvasState(BaseModel):
    workflow_name: str
    workflow: dict
    plan: WorkflowPlan | None = None
    progress: dict | None = None


def save_canvas_state(state: WorkflowCanvasState) -> None:
    vkt.Storage().set(
        WORKFLOW_GRAPH_STATE_STORAGE_KEY,
        data=vkt.File.from_data(state.model_dump_json()),
        scope="entity",
    )


def load_canvas_state() -> WorkflowCanvasState | None:
    try:
        stored_file = vkt.Storage().get(WORKFLOW_GRAPH_STATE_STORAGE_KEY, scope="entity")
        raw = stored_file.getvalue_binary().decode("utf-8")
        return WorkflowCanvasState.model_validate_json(raw)
    except Exception:
        return None
```

## Optimization Study Storage Template

```python
def save_study(study: CostOptimizationStudy) -> None:
    study.updated_at = now_iso()
    write_json_to_storage(OPTIMIZATION_STUDY_STORAGE_KEY, study.model_dump())


def load_study() -> CostOptimizationStudy:
    raw = read_json_from_storage(OPTIMIZATION_STUDY_STORAGE_KEY)
    return CostOptimizationStudy.model_validate(raw)


async def show_hide_optimization_results_func(context: Any, args: str) -> str:
    payload = ShowHideOptimizationResultsArgs.model_validate_json(args or "{}")
    if payload.action == "show":
        try:
            load_study()
        except Exception:
            return tool_response(
                "needs_prerequisite",
                tool="show_hide_optimization_results",
                message="No active optimization study exists to display.",
                missing_storage_key=OPTIMIZATION_STUDY_STORAGE_KEY,
                retry_action={
                    "tool": "start_cost_optimization_study",
                    "reason": "Start and record candidates before showing results.",
                },
            )
    set_visibility(SHOW_OPTIMIZATION_RESULTS_KEY, payload.action)
    return tool_response(
        "completed",
        message=f"Optimization results view set to {payload.action}.",
        visibility=payload.action,
        storage_key=SHOW_OPTIMIZATION_RESULTS_KEY,
    )
```

## Things To Consider

- Use VIKTOR Storage for large handoffs and UI state, not for secrets.
- Keep visibility keys separate from payload keys.
- Hide does not mean delete.
- Reset means delete, but require confirmation.
- Broad exception catches are acceptable in WebView visibility functions; tool functions should return explicit JSON errors.
- If payload shape is fragile, validate it before writing storage.
- Store summaries in tool output and large payloads in storage.
- Include `storage_key` in tool output so the agent can explain what happened without dumping data.
- Use stable keys so old sessions remain readable after deployment.
