---
name: viktor-table-data-view
description: Use when the user wants a VIKTOR app to display tabular results or compact result cards. VIKTOR uses `TableView` with `TableResult` for rows and columns, and `DataView` with `DataResult`, `DataGroup`, and `DataItem` for key values, checks, statuses, and summaries.
---

# VIKTOR Table And Data Views

Use this skill for result outputs that are not primarily 3D geometry, charts, maps, or files.

## Workflow

1. Use `TableView` when users need rows, columns, sorting, filtering, or CSV download.
2. Use `DataView` when users need a short summary of engineering values, utilization ratios, statuses, or messages.
3. Add units in headers, suffixes, or `DataItem` suffixes.
4. Return empty but valid results when user input is missing, or raise `vkt.UserError` when the user must fix input.
5. Keep result labels stable and readable.

## Load When Needed

- Read [reference.md](reference.md) for signatures, parameters, formatting, and common mistakes.
- Read [examples.md](examples.md) for table and data result patterns.
