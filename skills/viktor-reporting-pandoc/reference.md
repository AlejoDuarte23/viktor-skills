# VIKTOR Reporting With Pandoc Reference

Official sources:

- <https://docs.viktor.ai/docs/create-apps/references/viktor-config-toml/>
- <https://docs.viktor.ai/docs/create-apps/development-tools-and-tips/system-dependencies/>
- <https://pandoc.org/installing.html>
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

### Tables

```markdown
| Check | Expression | Value | Unit |
| --- | --- | ---: | --- |
| Dead load | $w_D L_{trib}$ | 1.25 | klf |
| Wind load | $q_z GC_p$ | -0.032 | ksf |
```

Keep tables simple. For heavily styled tables, generate a reference `.docx` outside the app and pass it with `--reference-doc`, but avoid that until the report needs exact Word branding.

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
