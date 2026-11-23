# Optimization Skill Templates

Use these snippets to implement a local runtime skill and the optional optimization study tools.

## Table Of Contents

- Runtime skill folder template
- `SKILL.md` optimization playbook template
- `examples.md` template
- Safe skill-reader tool
- Optimization study models
- Storage helpers
- Study tool functions
- Registry snippets
- System prompt snippets
- Things to consider

## Runtime Skill Folder Template

```text
agent/
  skills/
    optimization/
      SKILL.md
      examples.md
      parallel_coordinates_schema.json
  tools/
    skill_tools.py
    optimization_tools/
      __init__.py
      cost_optimization.py
```

## `SKILL.md` Optimization Playbook Template

```markdown
# Cost Optimization Workflow

Use this skill when the user asks to optimize, minimize cost, compare alternatives, run a design sweep, or find the best feasible configuration.

## Goal

Find the lowest-cost feasible configuration by varying selected design variables while keeping user-defined and upstream parameters fixed.

## Fixed Inputs

Keep these fixed unless the user explicitly asks to vary them:

- upstream loads and geometry produced by previous tools
- location or site selection
- material and cost rates
- worker/template availability
- user constraints such as min/max counts and allowed sizes

## First-Pass Variables

Prefer variables that strongly affect the objective and are cheap to sweep:

- primary geometry size
- member diameter or thickness
- spacing or count, only when allowed

Avoid variables that explode combinations unless the user gives a candidate budget.

## Loop

1. Create or select workflow entities.
2. Run upstream producer tools.
3. Start an optimization study.
4. For each candidate:
   - set candidate params
   - run required compute tools
   - patch downstream params from outputs
   - run cost/objective tool
   - record the candidate immediately
5. Read the study.
6. Show the results view.
7. Restore and finalize the selected best candidate.

## Candidate Budget

Prefer 3 to 8 candidates for the first sweep. Use coarse sweeps first, then refine around the best region.

## Feasibility

Mark a candidate infeasible if compute fails, required output is missing, utilization is unacceptable, or the objective cannot be computed.

## Finalization

When applying the optimum, restore best candidate variables, rerun the required final sequence once, and then run final export/model tools.
```

## `examples.md` Template

````markdown
# Optimization Examples

## Start A Study

```json
{
  "study_name": "Small geometry sweep",
  "candidate_budget": 6,
  "variables": [
    {
      "name": "slab_diameter",
      "path": "step_geo.sec_plate.slab_diameter",
      "unit": "m",
      "values": [18, 20, 22]
    }
  ],
  "fixed_inputs": [
    {
      "name": "turbine_loads",
      "value": "fixed from upstream selector output"
    }
  ],
  "replace_existing": true
}
```

## Record A Candidate

```json
{
  "candidate_id": "cand-001",
  "status": "completed",
  "feasible": true,
  "variables": {
    "slab_diameter_m": 20,
    "pile_diameter_mm": 500
  },
  "outputs": {
    "max_pile_reaction_kn": 5120.5,
    "required_pile_length_m": 20,
    "steel_mass_kg_m3": 72,
    "total_cost": 845000
  },
  "cost": 845000,
  "notes": "All required tools completed."
}
```
````

## Safe Skill-Reader Tool

```python
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ListSkillFilesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReadSkillFileArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relative_path: str = Field(
        default="SKILL.md",
        description="Path relative to the configured local skill folder.",
    )


class SkillTools:
    def __init__(
        self,
        skills_root: Path,
        skill_name: str,
        max_chars: int = 30_000,
        allowed_suffixes: set[str] | None = None,
    ) -> None:
        self.skills_root = Path(skills_root)
        self.skill_name = skill_name
        self.max_chars = max_chars
        self.allowed_suffixes = allowed_suffixes or {".md", ".json", ".txt", ".py"}

    @property
    def root(self) -> Path:
        return self.skills_root / self.skill_name

    def list_skill_files(self) -> str:
        if not self.root.exists():
            return tool_response("error", message=f"Missing skill folder: {self.root}")

        files: list[str] = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in self.allowed_suffixes:
                continue
            relative_path = path.relative_to(self.root)
            if any(part.startswith(".") for part in relative_path.parts):
                continue
            files.append(str(relative_path).replace("\\", "/"))

        return tool_response("ok", skill=self.skill_name, files=files)

    def read_skill_file(self, relative_path: str) -> str:
        path = self.safe_skill_path(relative_path)
        content = path.read_text(encoding="utf-8", errors="replace")
        return tool_response(
            "ok",
            skill=self.skill_name,
            relative_path=relative_path,
            content=content[: self.max_chars],
            truncated=len(content) > self.max_chars,
        )

    def safe_skill_path(self, relative_path: str) -> Path:
        root = self.root.resolve()
        path = (root / relative_path).resolve()
        if root not in (path, *path.parents):
            raise ValueError(f"Skill path escapes the skill folder: {relative_path}")
        if not path.is_file():
            raise FileNotFoundError(f"Skill file not found: {relative_path}")
        if path.suffix.lower() not in self.allowed_suffixes:
            raise ValueError(f"Skill file suffix is not allowed: {relative_path}")
        return path


def get_optimization_skill_tools() -> SkillTools:
    skills_root = Path(__file__).resolve().parents[1] / "skills"
    return SkillTools(skills_root=skills_root, skill_name="optimization")


async def list_skill_files_func(context: Any, args: str) -> str:
    try:
        ListSkillFilesArgs.model_validate_json(args or "{}")
        return get_optimization_skill_tools().list_skill_files()
    except ValidationError as exc:
        return validation_error_response(
            tool="list_skill_files",
            message="Invalid skill listing arguments.",
            error=exc,
            retry_tool="list_skill_files",
        )
    except Exception as exc:
        return execution_error_response(
            tool="list_skill_files",
            message="Could not list local skill files.",
            error=exc,
        )


async def read_skill_file_func(context: Any, args: str) -> str:
    try:
        payload = ReadSkillFileArgs.model_validate_json(args or "{}")
        return get_optimization_skill_tools().read_skill_file(payload.relative_path)
    except ValidationError as exc:
        return validation_error_response(
            tool="read_skill_file",
            message="Invalid skill read arguments.",
            error=exc,
            retry_tool="read_skill_file",
        )
    except Exception as exc:
        return execution_error_response(
            tool="read_skill_file",
            message="Could not read local skill file.",
            error=exc,
        )
```

## Optimization Study Models

```python
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError


COST_OPTIMIZATION_STORAGE_KEY = "cost_optimization_study"
SHOW_OPTIMIZATION_RESULTS_KEY = "show_optimization_results"

CandidateStatus = Literal["pending", "completed", "failed", "infeasible"]
OptimizationObjective = Literal["minimize_total_cost"]
ScalarValue = str | float | int | bool | None


class OptimizationScalar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    value: ScalarValue = None
    unit: str | None = None
    path: str | None = None


class OptimizationVariableRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    path: str
    unit: str | None = None
    values: list[float | int | str] = Field(default_factory=list)
    min_value: float | None = None
    max_value: float | None = None
    step: float | None = None


class StartCostOptimizationStudyArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    study_name: str | None = None
    objective: OptimizationObjective = "minimize_total_cost"
    candidate_budget: int = Field(default=8, ge=1)
    variables: list[OptimizationVariableRange] = Field(default_factory=list)
    fixed_inputs: list[OptimizationScalar] = Field(default_factory=list)
    notes: str | None = None
    replace_existing: bool = False


class RecordCostOptimizationCandidateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    status: CandidateStatus = "completed"
    feasible: bool = True
    variables: dict[str, JsonValue] = Field(default_factory=dict)
    outputs: dict[str, JsonValue] = Field(default_factory=dict)
    cost: float | None = None
    notes: str | None = None
    input_storage_keys: list[str] = Field(default_factory=list)
    output_storage_keys: list[str] = Field(default_factory=list)


class GetCostOptimizationStudyArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    include_candidates: bool = True
    max_candidates: int = Field(default=50, ge=1)


class ResetCostOptimizationStudyArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirm: bool = False


class ShowHideOptimizationResultsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["show", "hide"]


class CostOptimizationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    status: CandidateStatus
    feasible: bool
    variables: dict[str, JsonValue]
    outputs: dict[str, JsonValue]
    objective_value: float | None
    notes: str | None = None
    input_storage_keys: list[str] = Field(default_factory=list)
    output_storage_keys: list[str] = Field(default_factory=list)
    recorded_at: str


class CostOptimizationStudy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    storage_key: str = COST_OPTIMIZATION_STORAGE_KEY
    study_name: str
    objective: OptimizationObjective
    candidate_budget: int
    variables: list[OptimizationVariableRange] = Field(default_factory=list)
    fixed_inputs: list[OptimizationScalar] = Field(default_factory=list)
    notes: str | None = None
    created_at: str
    updated_at: str
    candidates: list[CostOptimizationCandidate] = Field(default_factory=list)
```

## Study Utilities

```python
def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def default_study_name() -> str:
    return f"Cost Optimization - {datetime.now().strftime('%Y-%m-%d %H:%M')}"


def load_study() -> CostOptimizationStudy:
    raw = read_json_from_storage(COST_OPTIMIZATION_STORAGE_KEY)
    return CostOptimizationStudy.model_validate(raw)


def try_load_study() -> CostOptimizationStudy | None:
    try:
        return load_study()
    except Exception:
        return None


def save_study(study: CostOptimizationStudy) -> None:
    study.updated_at = now_iso()
    write_json_to_storage(COST_OPTIMIZATION_STORAGE_KEY, study.model_dump())


def to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def flatten_json(value: Any, *, prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(flatten_json(item, prefix=child_prefix))
        return flattened
    if isinstance(value, list):
        for index, item in enumerate(value):
            flattened.update(flatten_json(item, prefix=f"{prefix}[{index}]"))
        return flattened
    if prefix:
        flattened[prefix] = value
    return flattened


def candidate_row(candidate: CostOptimizationCandidate) -> dict[str, Any]:
    row: dict[str, Any] = {
        "candidate_id": candidate.candidate_id,
        "status": candidate.status,
        "feasible": candidate.feasible,
        "objective_value": candidate.objective_value,
    }
    row.update(flatten_json(candidate.variables))
    for key, value in flatten_json(candidate.outputs).items():
        row[key if key not in row else f"output_{key}"] = value
    return row


def parallel_rows(study: CostOptimizationStudy) -> list[dict[str, Any]]:
    return [candidate_row(candidate) for candidate in study.candidates]


def parallel_dimensions(rows: list[dict[str, Any]]) -> list[str]:
    dimensions: list[str] = []
    for row in rows:
        for key, value in row.items():
            if key in {"candidate_id", "status"}:
                continue
            if isinstance(value, (int, float, bool)) and key not in dimensions:
                dimensions.append(key)
    return dimensions


def best_candidate(study: CostOptimizationStudy) -> CostOptimizationCandidate | None:
    feasible = [
        candidate
        for candidate in study.candidates
        if candidate.status == "completed"
        and candidate.feasible
        and candidate.objective_value is not None
    ]
    return min(feasible, key=lambda item: item.objective_value or float("inf")) if feasible else None
```

## Study Tool Functions

```python
async def start_cost_optimization_study_func(context: Any, args: str) -> str:
    try:
        payload = StartCostOptimizationStudyArgs.model_validate_json(args or "{}")
    except ValidationError as exc:
        return validation_error_response(
            tool="start_cost_optimization_study",
            message="Invalid cost optimization study arguments.",
            error=exc,
            retry_tool="start_cost_optimization_study",
        )

    existing = try_load_study()
    if existing and not payload.replace_existing:
        return tool_response(
            "study_exists",
            message="A cost optimization study already exists.",
            storage_key=COST_OPTIMIZATION_STORAGE_KEY,
            retry_action={
                "tool": "start_cost_optimization_study",
                "reason": "Retry with replace_existing=true to overwrite the active study.",
            },
        )

    timestamp = now_iso()
    study = CostOptimizationStudy(
        study_name=(payload.study_name or default_study_name()).strip() or default_study_name(),
        objective=payload.objective,
        candidate_budget=payload.candidate_budget,
        variables=payload.variables,
        fixed_inputs=payload.fixed_inputs,
        notes=payload.notes,
        created_at=timestamp,
        updated_at=timestamp,
    )
    save_study(study)
    return tool_response(
        "completed",
        message="Started cost optimization study.",
        storage_key=COST_OPTIMIZATION_STORAGE_KEY,
        variable_count=len(study.variables),
        fixed_input_count=len(study.fixed_inputs),
    )


async def record_cost_optimization_candidate_func(context: Any, args: str) -> str:
    try:
        payload = RecordCostOptimizationCandidateArgs.model_validate_json(args or "{}")
        study = load_study()
    except FileNotFoundError:
        return tool_response(
            "needs_prerequisite",
            tool="record_cost_optimization_candidate",
            message="No active cost optimization study exists.",
            missing_storage_key=COST_OPTIMIZATION_STORAGE_KEY,
            retry_action={
                "tool": "start_cost_optimization_study",
                "reason": "Start the study before recording candidates.",
            },
        )
    except ValidationError as exc:
        return validation_error_response(
            tool="record_cost_optimization_candidate",
            message="Invalid optimization candidate arguments.",
            error=exc,
            retry_tool="record_cost_optimization_candidate",
        )

    objective_value = payload.cost if payload.cost is not None else to_float(payload.outputs.get("total_cost"))
    candidate = CostOptimizationCandidate(
        candidate_id=payload.candidate_id,
        status=payload.status,
        feasible=payload.feasible,
        variables=payload.variables,
        outputs=payload.outputs,
        objective_value=objective_value,
        notes=payload.notes,
        input_storage_keys=payload.input_storage_keys,
        output_storage_keys=payload.output_storage_keys,
        recorded_at=now_iso(),
    )

    study.candidates = [
        candidate if item.candidate_id == candidate.candidate_id else item
        for item in study.candidates
    ] if any(item.candidate_id == candidate.candidate_id for item in study.candidates) else [
        *study.candidates,
        candidate,
    ]
    save_study(study)
    rows = parallel_rows(study)
    return tool_response(
        "completed",
        message="Recorded optimization candidate.",
        storage_key=COST_OPTIMIZATION_STORAGE_KEY,
        candidate_id=candidate.candidate_id,
        objective_value=candidate.objective_value,
        parallel_coordinates_row=candidate_row(candidate),
        parallel_coordinates_dimensions=parallel_dimensions(rows),
    )
```

```python
async def get_cost_optimization_study_func(context: Any, args: str) -> str:
    try:
        payload = GetCostOptimizationStudyArgs.model_validate_json(args or "{}")
        study = load_study()
    except FileNotFoundError:
        return tool_response(
            "needs_prerequisite",
            tool="get_cost_optimization_study",
            message="No active cost optimization study exists.",
            missing_storage_key=COST_OPTIMIZATION_STORAGE_KEY,
            retry_action={
                "tool": "start_cost_optimization_study",
                "reason": "Start the study before reading optimization results.",
            },
        )
    except ValidationError as exc:
        return validation_error_response(
            tool="get_cost_optimization_study",
            message="Invalid get optimization study arguments.",
            error=exc,
            retry_tool="get_cost_optimization_study",
        )

    rows = parallel_rows(study)
    best = best_candidate(study)
    candidates = study.candidates[: payload.max_candidates] if payload.include_candidates else []
    return tool_response(
        "completed",
        storage_key=COST_OPTIMIZATION_STORAGE_KEY,
        best_candidate=best.model_dump() if best else None,
        candidates=[candidate.model_dump() for candidate in candidates],
        parallel_coordinates_rows=rows[: payload.max_candidates],
        parallel_coordinates_dimensions=parallel_dimensions(rows),
    )
```

## Registry Snippets

```python
function_tool(
    "list_skill_files",
    "List local workflow skill files available to the agent.",
    ListSkillFilesArgs,
    list_skill_files_func,
)
function_tool(
    "read_skill_file",
    "Read a local workflow skill file before planning specialized workflows.",
    ReadSkillFileArgs,
    read_skill_file_func,
)
function_tool(
    "start_cost_optimization_study",
    "Create or replace append-only storage for an optimization study.",
    StartCostOptimizationStudyArgs,
    start_cost_optimization_study_func,
)
function_tool(
    "record_cost_optimization_candidate",
    "Append or replace one evaluated optimization candidate.",
    RecordCostOptimizationCandidateArgs,
    record_cost_optimization_candidate_func,
    strict_json_schema=False,
)
```

## System Prompt Snippets

```xml
<workflow_rules>
  <rule>For optimization, cost minimization, design sweep, alternatives, or best-configuration requests, call list_skill_files and read_skill_file before planning the loop.</rule>
  <rule>Run candidates sequentially through the same active workflow entities unless the user explicitly asks for isolated parallel entities.</rule>
  <rule>Record each candidate immediately after its objective result is available.</rule>
  <rule>Latest workflow storage is overwritten during sequential sweeps; comparison data comes from record_cost_optimization_candidate.</rule>
  <rule>After candidates are recorded, call show_hide_optimization_results with action="show".</rule>
  <rule>Before final export, restore the selected best candidate and rerun the final required sequence once.</rule>
</workflow_rules>
```

## Things To Consider

- The skill-reader tool gives the runtime agent project-specific procedural memory.
- Do not expose arbitrary filesystem reads.
- Keep expensive or fragile optimization choices in the skill, not in the system prompt.
- Keep candidate loops small at first.
- Record failed candidates with useful notes.
- Store raw large outputs in workflow storage, but record scalar candidate metrics in the optimization study.
- Use stable candidate ids so reruns can replace a candidate cleanly.
- If a chart needs dimensions, only numeric and boolean columns should become dimensions.
