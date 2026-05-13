---
name: viktor-geometry-view
description: Use when the user wants a VIKTOR app to display a 3D model or structural shape. VIKTOR geometry views return `GeometryResult` objects made from geometry primitives such as points, lines, extrusions, materials, and groups, so this skill helps create visible, well-organized engineering geometry.
---

# VIKTOR Geometry View

Use this skill for 3D outputs.

## Workflow

1. Load the VIKTOR core trio first: core, parametrization, and styling.
2. Choose a `GeometryView` when the output is a 3D model.
3. Build geometry from `Point`, `Line`, `RectangularExtrusion`, `Extrusion`, `Material`, and `Group`.
4. Use identifiers and groups for model parts that need selection, labeling, or later styling.
5. Remember that VIKTOR geometry uses Z as the default vertical axis.
6. For structural tools that receive STAAD coordinates, map axes deliberately because STAAD commonly uses Y as vertical.

## Load When Needed

- Read [reference.md](reference.md) for geometry classes and result patterns.
- Read [examples.md](examples.md) for practical 3D model and deformation examples.
