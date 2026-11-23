# VIKTOR Workflow Skill Tool Reference

## Scope

Use this reference when a VIKTOR-backed Agents SDK app needs local runtime skills that the agent can list and read on demand.

Use local skill folders when workflow guidance is too detailed for `system_prompt.xml` but should ship with the VIKTOR app.

## Runtime Skill Layout

Use this app-local shape:

```text
agent/
  skills/
    optimization/
      SKILL.md
      examples.md
      parallel_coordinates_schema.json
  tools/
    skill_tools.py
```

Keep `SKILL.md` concise and procedural. Put examples, schemas, and fragile output details in sibling files.

## Skill Reader Tools

Expose two small tools:

- `list_skill_files`
- `read_skill_file`

The reader must:

- list only files under the configured skill root
- reject path traversal
- skip hidden path parts
- allow only safe suffixes such as `.md`, `.json`, `.txt`, and `.py`
- cap returned file content
- return JSON with `status`, `skill`, `files`, `relative_path`, `content`, and `truncated`

## Optimization Workflow Rules

For optimization workflow skills:

1. Create or select workflow entities.
2. Read the local skill before planning the candidate loop.
3. Run upstream producer tools.
4. Propagate exact params to downstream tools.
5. Start an optimization study.
6. Evaluate candidates sequentially unless the user asks for isolated parallel runs.
7. Record every candidate immediately.
8. Read the study and identify the best feasible candidate.
9. Show the results view.
10. Restore the selected best candidate before final export or model generation.

## Failure Contract

Return recoverable states as JSON tool output:

- `study_exists`
- `needs_prerequisite`
- `validation_error`
- `execution_error`
- `confirmation_required`

## Validation

Run checks appropriate to the target app:

```bash
python3 -m py_compile $(rg --files . -g '*.py')
xmllint --noout agent/system_prompt.xml
git diff --check
```
