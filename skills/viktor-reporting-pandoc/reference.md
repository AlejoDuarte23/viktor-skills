# VIKTOR Reporting With Pandoc Reference

Official sources:

- <https://docs.viktor.ai/docs/create-apps/references/viktor-config-toml/>
- <https://docs.viktor.ai/docs/create-apps/development-tools-and-tips/system-dependencies/>
- <https://pandoc.org/installing.html>
- <https://pandoc.org/MANUAL.html#extension-pipe_tables>
- <https://pandoc.org/MANUAL.html#option--reference-doc>
- <https://github.com/pandoc-ext/pagebreak>
- <https://jinja.palletsprojects.com/en/stable/templates/#whitespace-control>
- <https://github.com/microsoft/winget-pkgs/tree/master/manifests/j/JohnMacFarlane/Pandoc>

## VIKTOR Config

Add Pandoc as a system package in `viktor.config.toml`:

```toml
app_type = "simple"
python_version = "3.12"
registered_name = "my-reporting-app"
packages = ["pandoc"]
```

`packages` installs Linux `apt-get` compatible packages for published VIKTOR apps. For local testing, Pandoc still needs to be available on the machine or in the selected local isolation environment.

Do not add `pandoc` to `requirements.txt` unless the app imports a Python wrapper. A normal `subprocess.run(["pandoc", ...])` export only needs the Pandoc executable.

If the Markdown template is rendered with Jinja:

```text
viktor==X.X.X
jinja2==3.1.4
```

## Local Windows Install

Use `winget` from PowerShell:

```powershell
winget install --source winget --exact --id JohnMacFarlane.Pandoc --accept-source-agreements --accept-package-agreements
```

Then open a new terminal and verify:

```powershell
pandoc --version
```

If the skill script is available in the project:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-pandoc-windows.ps1
```

For WSL2 VIKTOR development, install Pandoc inside WSL:

```bash
sudo apt-get update
sudo apt-get install -y pandoc
pandoc --version
```

## Pandoc Command

Use this shape from Python:

```python
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
subprocess.run(command, check=True, cwd=resource_dir)
```

Use `--resource-path` when Markdown references local images. Set `cwd` to the template or output directory so relative paths resolve consistently.

Optional Word controls:

```python
if reference_docx is not None:
    command.extend(["--reference-doc", str(reference_docx)])
if pagebreak_filter is not None:
    command.extend(["--lua-filter", str(pagebreak_filter)])
```

Use `--reference-doc` for Word styles, page size, margins, and the default table style. Use a pagebreak Lua filter when Markdown contains standalone `\newpage` paragraphs that must become DOCX page breaks.

## Markdown Syntax For Word Reports

### Headings

```markdown
# Calculation Report
## Inputs
## Results
```

### Equations

Inline:

```markdown
The tributary length is $L_{trib} = \frac{L_{joist}}{2}$.
```

Display:

```markdown
$$
q_z = 0.00256 K_z K_{zt} K_d V^2
$$
```

Units:

```markdown
$P = 4.25\ \mathrm{kip}$
```

Use `\mathrm{}` for units so Pandoc converts them as equation text instead of variables.

### Section Narrative

Write each Markdown section as a report section, not only as a heading followed by a table. Add one short paragraph between the heading and the transformed content.

For each section, include:

- What the section contains.
- How to read the table, figure, or equation.
- Which units, sign conventions, filters, or governing assumptions apply.
- What empty data means when a section has no rows.

Good pattern:

```markdown
## Reaction Loads

This section summarizes the support reactions recovered from the selected SAP2000 load combinations. Positive forces follow the global SAP2000 axes, and moments are reported about the corresponding global axes. Use these values to check support demand and foundation load transfer.

{% if joint_reactions %}
| Joint | Combination | F1 | F2 | F3 | M1 | M2 | M3 |
|:------|:------------|---:|---:|---:|---:|---:|---:|
...
{% else %}
No reaction results were available for the selected combinations. Check that the model was analyzed and that the requested combinations are selected for output.
{% endif %}
```

Avoid:

```markdown
## Reaction Loads

| Joint | Combination | F1 | F2 | F3 |
|:------|:------------|---:|---:|---:|
...
```

The second version converts to Word, but it reads like exported data rather than an engineering report.

### Tables

```markdown
| Check | Expression | Value | Unit |
| --- | --- | ---: | --- |
| Dead load | $w_D L_{trib}$ | 1.25 | klf |
| Wind load | $q_z GC_p$ | -0.032 | ksf |
```

Keep tables simple. Pipe tables are reliable for short, single-line cells. They are weak for wide engineering tables, fixed Word column widths, merged cells, or long packed text.

Rules for Word-friendly pipe tables:

- Render the Jinja template to a debug `.md` file before Pandoc and inspect that file when the DOCX table is wrong.
- Keep each table uninterrupted: header row, separator row, data rows, then one blank line after the table.
- Do not leave blank lines inside the table from `{% if %}`, `{% for %}`, or `{% endfor %}` tags.
- Use `trim_blocks=True` and `lstrip_blocks=True` in the Jinja environment.
- Use Jinja whitespace control only where needed. `{%-` and `-%}` can remove required newlines if used aggressively.
- Keep headers short. Move units to a note below the table when units make columns too wide.
- Split dense text cells into separate columns. For restraints, prefer `U1 | U2 | U3 | R1 | R2 | R3` over one long cell.
- Escape pipe characters in data values before rendering table cells.

Good support table pattern:

```markdown
{% if support_nodes %}
The following table lists the restrained joints used for support reaction extraction. Coordinates are reported in the model length unit, and each restraint flag uses `1` for fixed and `0` for free.

| Joint | X | Y | Z | U1 | U2 | U3 | R1 | R2 | R3 |
|:------|---:|---:|---:|:--:|:--:|:--:|:--:|:--:|:--:|
{% for support in support_nodes -%}
| {{ support.joint }} | {{ "%.2f"|format(support.x) }} | {{ "%.2f"|format(support.y) }} | {{ "%.2f"|format(support.z) }} | {{ support.restraint.u1 }} | {{ support.restraint.u2 }} | {{ support.restraint.u3 }} | {{ support.restraint.r1 }} | {{ support.restraint.r2 }} | {{ support.restraint.r3 }} |
{% endfor %}

**Coordinates in {{ units.length }}; restraints: 1=fixed, 0=free**
{% else %}
No support nodes were found. Confirm that restraints are assigned in SAP2000 before using this report for support reactions.
{% endif %}
```

If Word still squeezes columns, create a reference `.docx` with the desired `Table` style and pass it with `--reference-doc`. If exact cell widths, merged headers, repeated headers, or strict layout are required, generate the DOCX tables with `python-docx` instead of Markdown.

### Page Breaks

For DOCX output, do not assume a bare `\newpage` will always become a Word page break. Prefer a Pandoc pagebreak Lua filter. Keep the marker as its own paragraph:

```markdown
Paragraph before page break

\newpage

Paragraph after page break
```

### Images

```markdown
![Load path diagram](images/load-path.png){width=5in}
```

Images must exist on disk when Pandoc runs. Use a temporary directory and copy generated images there, or point `--resource-path` at the app assets/report directory.

## Failure Handling

Raise a clear user-facing error when Pandoc is missing:

```python
if shutil.which("pandoc") is None:
    raise vkt.UserError(
        "Pandoc is not installed. Install it locally for testing and add packages = [\"pandoc\"] before publishing."
    )
```

Catch `subprocess.CalledProcessError` and show a short message. During development, inspect the failed Markdown file and run the printed Pandoc command manually.

For table failures, keep the rendered Markdown file and test it directly:

```powershell
pandoc calculation-report.md --from=markdown+tex_math_dollars+pipe_tables --to=docx --standalone --output calculation-report.docx
```
