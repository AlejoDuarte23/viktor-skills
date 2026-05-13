# {{ project_name }} Calculation Report

## Summary

Prepared for {{ project_name }}.

| Item | Value |
| --- | --- |
| Report date | {{ report_date }} |
| Model status | {{ status }} |

## Inputs

| Parameter | Symbol | Value | Unit |
| --- | --- | ---: | --- |
{% for item in inputs %}
| {{ item.label }} | ${{ item.symbol }}$ | {{ item.value }} | {{ item.unit }} |
{% endfor %}

## Equations

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

| Check | Equation | Value | Unit | Status |
| --- | --- | ---: | --- | --- |
{% for row in result_rows %}
| {{ row.name }} | ${{ row.equation }}$ | {{ row.value }} | {{ row.unit }} | {{ row.status }} |
{% endfor %}

## Image

![Load path diagram](images/load-path.png){width=5in}

## Notes

- Keep Markdown tables simple for reliable Word output.
- Keep Jinja-generated tables uninterrupted: header row, separator row, data rows, then one blank line after the table.
- Keep headers short and put units below wide tables.
- Keep image paths relative to the directory passed to Pandoc with `--resource-path`.
- Escape backslashes in Python strings or use raw strings for LaTeX equations.
