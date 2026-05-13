---
name: viktor-styling
description: Use when the user wants a VIKTOR app to read well for engineers and non-programmers. VIKTOR app text is written with `vkt.Text` and input descriptions, so this skill helps add concise titles, Markdown, LaTeX equations, units, assumptions, and UI guidance that make parametrization inputs easier to understand.
---

# VIKTOR Styling

Use this skill before writing VIKTOR app copy, labels, descriptions, or equations.

## Workflow

1. Keep language practical and engineering-focused.
2. Explain formulas in the app when the code uses engineering equations.
3. Use Markdown and LaTeX inside `vkt.Text` where it clarifies the workflow.
4. Put text at the correct level in the parametrization layout.
5. Improve input labels with units, defaults, suffixes, descriptions, and option names.
6. Avoid long prose inside field labels; use `description` or nearby `vkt.Text` instead.

## Load When Needed

- Read [reference.md](reference.md) for Markdown, LaTeX, layout placement, and line break guidance.
- Read [examples.md](examples.md) for title, equation, and input UX patterns.
