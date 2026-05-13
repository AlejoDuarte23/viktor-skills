# VIKTOR Reporting With Pandoc Examples

## `viktor.config.toml`

```toml
app_type = "simple"
python_version = "3.12"
registered_name = "my-reporting-app"
packages = ["pandoc"]
```

## Local Windows Install

```powershell
winget install --source winget --exact --id JohnMacFarlane.Pandoc --accept-source-agreements --accept-package-agreements
pandoc --version
```

## Suggested App Files

```text
app
├── controller.py
├── parametrization.py
└── report
    ├── __init__.py
    ├── report_builder.py
    ├── word_export.py
    └── templates
        └── calculation_report.docx.md
```

## Markdown Template

```markdown
# {{ project_name }} Calculation Report

## Summary

Generated for {{ project_name }}.

## Governing Equation

$$
P = w L_{trib}
$$

## Results

| Item | Equation | Value | Unit |
| --- | --- | ---: | --- |
{% for row in result_rows %}
| {{ row.name }} | ${{ row.equation }}$ | {{ "%.3f"|format(row.value) }} | {{ row.unit }} |
{% endfor %}

![Load path](images/load-path.png){width=5in}
```

## Word Export Helper

```python
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class PandocNotInstalledError(RuntimeError):
    """Raised when the pandoc executable is unavailable."""


def export_docx(
    markdown_path: Path,
    output_docx: Path,
    resource_dir: Path | None = None,
    reference_docx: Path | None = None,
    pagebreak_filter: Path | None = None,
) -> Path:
    pandoc_path = shutil.which("pandoc")
    if pandoc_path is None:
        raise PandocNotInstalledError(
            "Pandoc is not installed. Install it locally for testing and add packages = [\"pandoc\"] before publishing."
        )

    markdown_path = markdown_path.resolve()
    output_docx = output_docx.resolve()
    resource_dir = (resource_dir or markdown_path.parent).resolve()
    output_docx.parent.mkdir(parents=True, exist_ok=True)

    command = [
        pandoc_path,
        str(markdown_path),
        "--from=markdown+tex_math_dollars+pipe_tables",
        "--to=docx",
        "--standalone",
        f"--resource-path={resource_dir}",
        "--output",
        str(output_docx),
    ]
    if reference_docx is not None:
        command.extend(["--reference-doc", str(reference_docx.resolve())])
    if pagebreak_filter is not None:
        command.extend(["--lua-filter", str(pagebreak_filter.resolve())])

    subprocess.run(command, check=True, cwd=resource_dir)
    return output_docx
```

## Report Builder

```python
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

REPORT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = REPORT_DIR / "templates"
JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape([]),
    trim_blocks=True,
    lstrip_blocks=True,
)


class CalculationReport:
    def __init__(self, params):
        self.params = params

    def build_context(self) -> dict[str, Any]:
        return {
            "project_name": self.params.project_name,
            "result_rows": [
                {
                    "name": "Line load",
                    "equation": r"P = w L_{trib}",
                    "value": 12.5,
                    "unit": r"\mathrm{kip}",
                }
            ],
        }

    def render_word_markdown(self) -> str:
        template = JINJA_ENV.get_template("calculation_report.docx.md")
        return template.render(**self.build_context())
```

## Download Button

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    report_tab = vkt.Tab("Report")
    report_tab.download_word_file = vkt.DownloadButton(
        "Download Word report",
        method="download_word_file",
        description="Generate a DOCX report for the current inputs.",
    )
```

## Controller Method

```python
import subprocess
import tempfile
from pathlib import Path

import viktor as vkt

from .parametrization import Parametrization
from .report.report_builder import CalculationReport
from .report.word_export import PandocNotInstalledError, export_docx


class Controller(vkt.Controller):
    parametrization = Parametrization

    def download_word_file(self, params, **kwargs):
        try:
            with tempfile.TemporaryDirectory(prefix="report-") as temp_dir:
                output_dir = Path(temp_dir)
                markdown_path = output_dir / "calculation-report.md"
                docx_path = output_dir / "calculation-report.docx"

                markdown_path.write_text(
                    CalculationReport(params).render_word_markdown(),
                    encoding="utf-8",
                )
                # Keep this file during debugging and inspect it before blaming Word.
                export_docx(markdown_path, docx_path)
                return vkt.DownloadResult(
                    file_content=docx_path.read_bytes(),
                    file_name=docx_path.name,
                )
        except PandocNotInstalledError as exc:
            raise vkt.UserError(str(exc)) from exc
        except subprocess.CalledProcessError as exc:
            raise vkt.UserError("Pandoc failed while generating the Word report.") from exc
```

This is the same focused pattern used by the dist-load app: the parametrization owns the `DownloadButton`, the controller owns the download method, and `app/report/word_export.py` owns the Pandoc call.

## Word-Friendly Tables

Keep Jinja block tags from creating blank lines inside Markdown tables. Render the Markdown first and inspect the `.md` file when Word cells look wrong.

```markdown
{% if support_nodes %}
| Joint | X | Y | Z | U1 | U2 | U3 | R1 | R2 | R3 |
|:------|---:|---:|---:|:--:|:--:|:--:|:--:|:--:|:--:|
{% for support in support_nodes -%}
| {{ support.joint }} | {{ "%.2f"|format(support.x) }} | {{ "%.2f"|format(support.y) }} | {{ "%.2f"|format(support.z) }} | {{ support.restraint.u1 }} | {{ support.restraint.u2 }} | {{ support.restraint.u3 }} | {{ support.restraint.r1 }} | {{ support.restraint.r2 }} | {{ support.restraint.r3 }} |
{% endfor %}

**Coordinates in {{ units.length }}; restraints: 1=fixed, 0=free**
{% else %}
*No support nodes found*
{% endif %}
```

Prefer short headers and separate columns over packed cells. If a table needs exact Word widths or merged cells, use `python-docx` for that table instead of Markdown.
