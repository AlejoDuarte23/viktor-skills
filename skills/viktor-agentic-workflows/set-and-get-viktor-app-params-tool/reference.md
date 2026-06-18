# Set And Get VIKTOR App Params Tool Reference

## Scope

Use this reference when a VIKTOR-backed Agents SDK app needs to read, update, and verify saved params on workflow node entities.

The goal is explicit app-to-app handoff:

1. Resolve the active workflow node entity.
2. Read its saved params.
3. Build an exact nested params patch from upstream output.
4. Deep-merge or replace saved params.
5. Write params back through the VIKTOR REST API.
6. Read back important values before reporting success.

## Expected Modules

- `responses.py`: compact JSON response helpers for recoverable tool states.
- `sdk_compute.py`: VIKTOR SDK compute client and environment normalization.
- `workflow_entities.py`: workflow node registry, active entity directory, REST client, and deep merge helper.
- `workflow_node_params.py`: `get_params_in_node` and `set_params_in_node` args, service, and tools.
- `registry.py`: Agents SDK `FunctionTool` registrations.
- `system_prompt.xml`: rules for readback, propagation, and user-facing recovery.

## Tool Contracts

Use these generic tools unless the target app already has names:

- `create_workflow_entity_directory`
- `get_workflow_entity_directory`
- `get_params_in_node`
- `set_params_in_node`

`get_params_in_node` reads saved params, not compute output. `set_params_in_node` writes saved params, not result storage.

## Propagation Rules

- Treat upstream tool output as the source of truth.
- Patch downstream params with exact target field paths.
- Use deep merge by default so manual VIKTOR UI values are preserved.
- Replace params only when the app explicitly owns the full params payload.
- Verify critical engineering values by reading saved params after writing.
- Return a `next_param_update` object when a producer tool can hand off values to `set_params_in_node`.

## Failure Contract

Return recoverable problems as JSON tool output:

- `validation_error`: malformed tool args or stored params.
- `needs_workflow_run`: no active entity directory or node mapping.
- `needs_prerequisite`: required upstream data is missing.
- `execution_error`: REST, SDK, auth, or unexpected runtime failure.
- `needs_scia_template`: SCIA compute cannot run because the worker/template is missing.

Include `retry_action.tool` when the agent can recover by calling another tool.

## Validation

Run checks appropriate to the target app:

```bash
python3 -m py_compile $(rg --files . -g '*.py')
xmllint --noout agent/system_prompt.xml
git diff --check
```
