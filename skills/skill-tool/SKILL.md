---
name: skill-tool
description: Implement or adapt local Agent Skills inside a VIKTOR-backed Agents SDK app, especially optimization workflow skills. Use when adding an agent-readable skill folder, exposing list/read skill tools, converting optimization playbooks into runtime guidance, or wiring optimization study tools and prompt rules.
---

# VIKTOR Workflow Skill Tool

Use this skill when a VIKTOR Agents SDK app needs a local skill folder that the runtime agent can read on demand, or when implementing an optimization workflow skill.

This skill is self-contained. Read `reference.md` for implementation notes and `examples.md` for copyable templates before writing code.

## Components

Implement these components in the target VIKTOR agent app:

- `agent/skills/<skill-name>/SKILL.md`: the runtime playbook the agent reads when the user asks for a specialized workflow.
- `agent/skills/<skill-name>/examples.md`: compact examples for tool inputs, candidate records, or workflow-specific patches.
- `agent/tools/skill_tools.py`: safe tools for listing and reading local skill files.
- `agent/tools/optimization_tools/cost_optimization.py`: optional study storage, candidate recording, and result visibility tools.
- `agent/tools/registry.py`: registers skill-reader and optimization tools.
- `agent/system_prompt.xml`: tells the agent when to read the local skill and how to follow its workflow.

Use a local skill folder when the workflow guidance is too detailed for the system prompt but should travel with the VIKTOR app.

## Pattern

Keep long workflow guidance in `agent/skills/<skill-name>/`, not in `system_prompt.xml`.

Expose two small tools:

- `list_skill_files`
- `read_skill_file`

Then add prompt rules that require the agent to call those tools before planning tasks that match the skill, for example optimization, cost minimization, design sweeps, or best-configuration requests.

## Runtime Skill Folder

Use this shape:

```text
agent/
  skills/
    optimization/
      SKILL.md
      examples.md
      parallel_coordinates_schema.json
```

Keep `SKILL.md` procedural and concise. Put longer examples, schemas, and fragile output details in sibling files.

## Skill Reader Tool Requirements

The reader must:

- list only files under the configured skill root
- reject path traversal
- skip hidden path parts
- allow only safe suffixes such as `.md`, `.json`, `.txt`, and `.py`
- cap file content, for example at 30,000 characters
- return JSON strings with `status`, `skill`, `files`, `relative_path`, `content`, and `truncated`

## Optimization Tool Requirements

Use explicit Pydantic models for:

- study variables
- fixed inputs
- study creation args
- candidate recording args
- study read args
- reset args
- show/hide args

Store optimization state in VIKTOR Storage, not in chat. Candidate records should be append-only comparison snapshots because the latest workflow outputs are overwritten during sequential candidate loops.

Core tools:

- `start_cost_optimization_study`
- `record_cost_optimization_candidate`
- `get_cost_optimization_study`
- `reset_cost_optimization_study`
- `show_hide_optimization_results`

## Optimization Loop

For a cost or design optimization request:

1. Create or select the workflow entities before asking for detailed design inputs.
2. Show node URLs and offer chat setup or manual VIKTOR app setup.
3. Call `list_skill_files`.
4. Call `read_skill_file` for `SKILL.md`, and read `examples.md` when candidate setup or recording is needed.
5. Run upstream producer tools.
6. Propagate producer outputs with explicit param patches.
7. Start the optimization study.
8. Evaluate candidates sequentially on the same workflow entities.
9. Record every candidate immediately after it finishes.
10. Read the study and identify the best feasible candidate.
11. Show the results view.
12. Restore/finalize the selected best candidate before any final downstream model/export step.

Do not create a new VIKTOR entity per candidate unless the user explicitly wants parallel isolated runs. Sequential sweeps are simpler and expected to overwrite latest workflow storage.

## Candidate Rules

Keep first sweeps small: usually 3 to 8 candidates.

Record failed and infeasible candidates with a short note. A failed candidate still teaches the optimizer which region to avoid.

Store flat, plot-friendly keys when possible:

```json
{
  "candidate_id": "cand-001",
  "status": "completed",
  "feasible": true,
  "variables": {
    "slab_diameter_m": 20.0,
    "pile_diameter_mm": 500
  },
  "outputs": {
    "max_pile_reaction_kn": 5120.5,
    "required_pile_length_m": 20.0,
    "steel_mass_kg_m3": 72.0,
    "total_cost": 845000.0
  },
  "cost": 845000.0
}
```

Use nested `variables` or `outputs` only when preserving source structure is more valuable than direct charting.

## Prompt Rules

Update the system prompt with high-level behavior only:

- call the local skill reader for matching workflow requests
- follow the skill before planning candidate loops
- run candidates sequentially unless the user asks otherwise
- record candidates immediately
- show results after candidates are recorded
- restore the best/final candidate before downstream finalization

Do not copy the whole skill into the system prompt.

## Failure Contract

Use JSON tool outputs for recoverable states:

- `study_exists`: active study already exists; retry with `replace_existing=true` if the user wants a fresh study.
- `needs_prerequisite`: study or upstream storage is missing.
- `validation_error`: malformed candidate or study payload.
- `execution_error`: storage, runtime, or compute failure.
- `confirmation_required`: destructive reset needs `confirm=true`.

## Gotchas

- Local skill files are runtime guidance, not Python imports.
- Keep path traversal checks in the reader even if the tool is only exposed to the agent.
- Do not leak secrets through `read_skill_file`; restrict suffixes and skill root.
- Candidate storage is the comparison record; latest workflow storage is only the active state.
- Record a candidate before evaluating the next one.
- Show/hide view state is separate from study data.
- If the best candidate is not the latest active state, restore and rerun the final workflow sequence once before final export.

## Validation

Run checks appropriate to the target app:

```bash
python3 -m py_compile $(rg --files . -g '*.py')
xmllint --noout agent/system_prompt.xml
git diff --check
```
