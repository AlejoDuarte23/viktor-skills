---
name: viktor-reporting-pandoc
description: Use when a VIKTOR app needs to generate downloadable Word DOCX reports from Markdown with Pandoc. Covers report templates, LaTeX equations, tables, images, DownloadButton, DownloadResult, Windows local Pandoc installation, and packages = ["pandoc"] in viktor.config.toml for published apps.
---

# VIKTOR Reporting With Pandoc

Use this skill when a VIKTOR app should generate a `.docx` report from Markdown and expose it with a download button.

## Workflow

1. Load `../viktor-core/SKILL.md`, `../viktor-parametrization/SKILL.md`, `../viktor-file-management/SKILL.md`, and `../viktor-cli-config/SKILL.md` first.
2. Add `pandoc` to `packages` in `viktor.config.toml`. This is a Linux system package for the published VIKTOR runtime, not a Python package.
3. For local Windows testing, install Pandoc on the host machine and make sure `pandoc --version` works in a new terminal.
4. Keep the report template in Markdown, normally under `app/report/templates/*.docx.md`.
5. Build report data in a helper class or function. Keep the controller method focused on creating the file and returning `DownloadResult`.
6. Write the rendered Markdown to a temporary directory, run `pandoc`, read the generated `.docx` bytes, and return them from a `DownloadButton` method.
7. Use `shutil.which("pandoc")` and raise `vkt.UserError` when Pandoc is missing so users get a clear message.
8. Use `markdown+tex_math_dollars+pipe_tables` as the Pandoc input format when the report contains equations and Markdown tables.
9. When Word tables render poorly, inspect the rendered Markdown before Pandoc. Fix blank lines, Jinja whitespace, long cells, and wide tables before changing the DOCX step.
10. Use a Pandoc `reference.docx` for Word styling and table style control; use a pagebreak filter for DOCX page breaks instead of relying on bare `\newpage`.

## Markdown Report Rules

- Use `$...$` for inline equations and `$$...$$` for display equations.
- Use LaTeX syntax for equation variables, fractions, superscripts, and units, for example `\frac{L}{2}` and `\mathrm{kip}`.
- Use Markdown pipe tables for simple result tables.
- Keep each pipe table as one uninterrupted Markdown block: header, separator, all rows, then one blank line after the table.
- Do not put Jinja block tags where they create blank lines inside a table. Use `trim_blocks=True`, `lstrip_blocks=True`, and `{%- ... -%}` carefully.
- Keep table headers short. Put units in a note below the table when unit labels make columns too wide.
- Split packed values into separate columns, for example `U1`, `U2`, `U3`, `R1`, `R2`, `R3` instead of one long restraint cell.
- Use image syntax such as `![Load diagram](images/load-path.png){width=5in}` and pass a Pandoc resource path when images are relative files.
- Prefer Markdown headings and plain text over HTML styling for Word output.
- If using template loops or conditionals, add `jinja2` to `requirements.txt` and render Markdown before calling Pandoc.
- If exact Word cell widths, merged cells, or strict branding are required, use `python-docx` or a dedicated DOCX template flow instead of Markdown pipe tables.

## Load When Needed

- Read [reference.md](reference.md) for config, Windows installation, Pandoc command flags, and Markdown syntax notes.
- Read [examples.md](examples.md) for a complete `DownloadButton` DOCX export pattern.
- Copy or adapt [assets/report-template.md](assets/report-template.md) when starting a new Markdown report.
- Use [scripts/install-pandoc-windows.ps1](scripts/install-pandoc-windows.ps1) when the user wants a PowerShell installer script for local Windows testing.
