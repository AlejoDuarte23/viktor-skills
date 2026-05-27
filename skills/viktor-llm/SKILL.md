---
name: viktor-llm
description: Use when the user wants to add, fix, or review VIKTOR built-in LLM features. This is a router skill with two subskills in subfolders: `text-base-llm` for text chat, tool use, and Agents SDK orchestration, and `vision-llm` for image analysis with the built-in vision model.
---

# VIKTOR LLM

Use this skill when a VIKTOR app needs built-in LLM chat, tool use, Agents SDK orchestration, or image analysis. This skill routes to the focused subskill under this folder.

## Workflow

1. Load `../viktor-core/SKILL.md` first if the app structure, controller, views, or errors are unclear.
2. Load `../viktor-parametrization/SKILL.md` before adding or changing `vkt.Chat` or upload fields.
3. Prefer Viktor LLM through `vkt.ViktorOpenAI` unless the user explicitly asks for another provider.
4. For text chat, `vkt.Chat`, `vkt.ChatResult`, text model defaults, Responses API tools, or Agents SDK tools, load `text-base-llm/SKILL.md`.
5. For image upload, vision prompts, base64 data URIs, or the built-in vision model, load `vision-llm/SKILL.md`.
6. If the app combines text agent behavior and image analysis, load both subskills.
7. Convert fair-usage and API failures into clear `vkt.UserError` messages.

## Subskills

- `text-base-llm/SKILL.md`: text-based built-in VIKTOR LLM, `vkt.Chat`, `vkt.ChatResult`, Chat Completions, Responses API tool loops, Agents SDK with `Runner.run_sync(...)`, and model-visible JSON tool errors.
- `vision-llm/SKILL.md`: built-in VIKTOR vision model, image upload fields, base64 data URI inputs, MIME handling, model limitations, and image-analysis examples.

## Load When Needed

- Read [reference.md](reference.md) for routing notes across both subskills.
