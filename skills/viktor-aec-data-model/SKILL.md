---
name: viktor-aec-data-model
description: Use when the user wants a VIKTOR app to select an Autodesk Construction Cloud model and query Autodesk AEC Data Model information. This skill covers `AutodeskFileField`, OAuth2 access tokens, GraphQL requests, element group IDs, RSQL filters, pagination, properties, categories, families, types, and quantity takeoff style tables.
---

# VIKTOR AEC Data Model

Use this skill only for Autodesk ACC or AEC Data Model work.

## Workflow

1. Load `../viktor-core/SKILL.md`, `../viktor-parametrization/SKILL.md`, and `../viktor-styling/SKILL.md` first.
2. Add an `AutodeskFileField` with the correct OAuth2 integration name.
3. Use `vkt.external.OAuth2Integration` to get the access token.
4. Get the model region and AEC Data Model element group ID from the selected Autodesk file.
5. Build GraphQL queries with variables and RSQL filters instead of string-concatenating user input into query bodies.
6. Return results through `TableView` or `DataView`; load `../viktor-table-data-view/SKILL.md` when formatting output.

## Load When Needed

- Read [reference.md](reference.md) for GraphQL, RSQL, pagination, and property examples.
- Read [examples.md](examples.md) for Autodesk file selection and quantity query patterns.
