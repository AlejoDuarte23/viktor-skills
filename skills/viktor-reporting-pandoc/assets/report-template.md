# {{ project_name }} Calculation Report

## Summary

This report summarizes the inputs, governing checks, and calculated results for {{ project_name }}. It is intended to document the calculation path and provide traceable values for review.

| Item | Value |
| --- | --- |
| Report date | {{ report_date }} |
| Model status | {{ status }} |

## Inputs

The following table lists the report inputs used by the calculation. Symbols match the notation used in the equations, and units are shown in the final column.

| Parameter | Symbol | Value | Unit |
| --- | --- | ---: | --- |
{% for item in inputs %}
| {{ item.label }} | ${{ item.symbol }}$ | {{ item.value }} | {{ item.unit }} |
{% endfor %}

## Equations

This section records the governing expressions used to produce the reported values. Equations are rendered with Pandoc math so they remain readable in the generated Word document.

Inline equations use `$...$`, for example $L_{trib} = \frac{L_{joist}}{2}$.

Display equations use `$$...$$`:

$$
P = w L_{trib}
$$

Use roman text for units:

$$
P = {{ load_value }}\ \mathrm{kip}
$$

## Results

The results table summarizes the calculated checks. Values are rounded for reporting, and the status column indicates whether each check satisfies the selected criterion.

| Check | Equation | Value | Unit | Status |
| --- | --- | ---: | --- | --- |
{% for row in result_rows %}
| {{ row.name }} | ${{ row.equation }}$ | {{ row.value }} | {{ row.unit }} | {{ row.status }} |
{% endfor %}

## Image

The figure below provides visual context for the calculation or load path described in the report.

![Load path diagram](images/load-path.png){width=5in}

## Notes

- Keep Markdown tables simple for reliable Word output.
- Keep Jinja-generated tables uninterrupted: header row, separator row, data rows, then one blank line after the table.
- Keep headers short and put units below wide tables.
- Keep image paths relative to the directory passed to Pandoc with `--resource-path`.
- Escape backslashes in Python strings or use raw strings for LaTeX equations.
