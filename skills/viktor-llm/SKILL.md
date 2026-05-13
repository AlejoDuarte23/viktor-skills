---
name: viktor-llm
description: Use when the user wants to add, fix, or review AI chat, tool calling, or image analysis in a VIKTOR app. VIKTOR is a Python platform for engineering web apps; this skill covers the built-in Viktor LLM service, `vkt.Chat`, `vkt.ChatResult`, OpenAI-compatible chat completions, Responses API tool use, and vision prompts without external API keys.
---

# VIKTOR LLM

Use this skill when a VIKTOR app needs built-in LLM chat, tool use, or image analysis.

## Workflow

1. Load `../viktor-core/SKILL.md` first if the app structure, controller, views, or errors are unclear.
2. Load `../viktor-parametrization/SKILL.md` before adding or changing `vkt.Chat` or upload fields.
3. Prefer Viktor LLM through `vkt.ViktorOpenAI` unless the user explicitly asks for another provider.
4. For text chat, call `conversation.get_messages()`, prepend any `system` message manually, and return `vkt.ChatResult`.
5. For tool use, use the Responses API with function schemas, `previous_response_id`, tool outputs, and a final streamed response.
6. For vision, use Chat Completions only and send base64 data URIs for uploaded images.
7. Convert fair-usage and API failures into clear `vkt.UserError` messages.

## Load When Needed

- Read [reference.md](reference.md) for the detailed chat, tool use, vision, limits, and API notes.
- Read [examples.md](examples.md) for compact app patterns.
