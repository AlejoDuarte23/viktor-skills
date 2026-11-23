---
name: set-and-get-viktor-app-params-tool
description: Implement Agents SDK tools for VIKTOR workflow apps that read saved params from active workflow node entities, deep-merge or replace saved params, verify propagation, and pass values between apps. Use when adding get_params_in_node, set_params_in_node, workflow node param propagation, manual VIKTOR app input readback, or downstream handoffs between VIKTOR apps.
---

# Set And Get VIKTOR App Params Tool

Use this skill when an agentic VIKTOR app needs tools that read, set, or propagate saved params across multiple VIKTOR app entities.

This skill is self-contained. Read `reference.md` for implementation notes and `examples.md` for copyable templates before writing code.

## Components

Implement these components in the target app:

- `responses.py`: JSON tool response helpers for validation, prerequisite, workflow-run, and execution failures.
- `sdk_compute.py`: VIKTOR SDK compute client and environment normalization.
- `workflow_entities.py`: active workflow entity directory, REST client, node registry, graph publishing hook, and deep merge helper.
- `workflow_node_params.py`: `get_params_in_node` and `set_params_in_node` tool args, service, and tool functions.
- `registry.py`: Agents SDK `FunctionTool` registrations and display names.
- `system_prompt.xml`: high-level agent rules for manual input readback and explicit propagation.

Keep generated app compute tools separate from these generic param tools. Generated compute tools should have explicit Pydantic models. The generic `set_params_in_node` is the exception because VIKTOR saved params are intentionally JSON-shaped.

## Runtime Flow

1. Create an active workflow entity directory before touching params.
2. Resolve `node_id` to `workspace_id`, `entity_id`, URL, method name, result key, and storage key.
3. Read saved params with REST using `properties=true`, `clean_params=true`, and `param_types=true`.
4. Deep-merge patches into saved params by default.
5. Write saved params back with REST `PUT`.
6. For critical propagation, read back the target node and verify the values match the producer output.
7. Return short JSON output with status, message, node metadata, updated top-level keys, and retry actions when recoverable.

## Tool Contracts

Use these tool names unless the target app already has different conventions:

- `create_workflow_entity_directory`: creates or records fresh workflow node entities.
- `get_workflow_entity_directory`: reads the active node directory.
- `get_params_in_node`: reads saved params for one node.
- `set_params_in_node`: deep-merges or replaces saved params for one node.

Minimum arg models:

```python
class GetParamsInNodeArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: WorkflowNodeId


class SetParamsInNodeArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: WorkflowNodeId
    params: dict[str, JsonValue] = Field(..., min_length=1)
    merge: bool = True
```

## Propagation Rules

Treat producer outputs as the source of truth. Do not use target app defaults, stale chat values, or downstream saved values when an upstream tool produced concrete values.

Use this sequence for each handoff:

1. Read or run the producer.
2. Build the exact nested target params patch.
3. Call `set_params_in_node`.
4. Call `get_params_in_node` for important engineering values.
5. Compare saved values to producer values.
6. Report success only after readback matches.

For tool-generated patches, return a `next_param_update` object so the agent can call `set_params_in_node` directly:

```json
{
  "next_param_update": {
    "tool": "set_params_in_node",
    "node_id": "foundation_analysis",
    "merge": true,
    "params": {
      "step_geo": {
        "sec_piles": {
          "pile_length": 20.0,
          "pile_diameter": 500
        }
      }
    }
  }
}
```

## Failure Contract

Return recoverable problems as JSON tool output, not hard exceptions:

- `validation_error`: malformed tool args or malformed stored data.
- `needs_workflow_run`: no active workflow entity directory or node missing.
- `needs_prerequisite`: required upstream storage key missing.
- `execution_error`: REST, SDK, auth, or unexpected runtime failure.
- `needs_scia_template`: engineering worker/template is missing for SCIA-style compute.

Include `retry_action.tool` when the agent can recover by calling another tool.

## Gotchas

- `get_params_in_node` reads saved params, not compute output.
- `set_params_in_node` writes saved params, not result storage, unless you intentionally sync a params snapshot to storage.
- Deep merge preserves manual VIKTOR UI inputs; replacement can erase unrelated fields.
- Param patches must use the target app's exact nested field names.
- Table/list inputs must be passed as full JSON-safe structures.
- `VIKTOR_ENVIRONMENT` must be host-only, for example `demo.viktor.ai`; do not include `https://` or `/api`.
- Do not add `OPENAI_API_KEY`; VIKTOR-backed agent apps should use `vkt.ViktorOpenAI`.

## Validation

Run checks appropriate to the target app:

```bash
python3 -m py_compile $(rg --files . -g '*.py')
xmllint --noout agent/system_prompt.xml
git diff --check
```
