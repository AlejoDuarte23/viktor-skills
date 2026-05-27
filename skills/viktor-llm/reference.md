# VIKTOR LLM Routing Reference

The detailed LLM guidance lives in two subskills under this folder.

| User intent | Load this subskill |
| --- | --- |
| Text chat with `vkt.Chat` and `vkt.ChatResult` | `text-base-llm/SKILL.md` |
| Built-in text model defaults and `vkt.ViktorOpenAI` wrapper | `text-base-llm/SKILL.md` |
| Responses API tool use without the Agents SDK | `text-base-llm/SKILL.md` |
| OpenAI Agents SDK tool use with `Runner.run_sync(...)` | `text-base-llm/SKILL.md` |
| Model-visible JSON tool errors | `text-base-llm/SKILL.md` |
| Image upload and image analysis | `vision-llm/SKILL.md` |
| Built-in VIKTOR vision model defaults | `vision-llm/SKILL.md` |
| Base64 image data URIs and MIME handling | `vision-llm/SKILL.md` |

Load both subskills when an app combines normal chat or agentic tools with image analysis.

Keep provider-specific guidance out of this router. For built-in VIKTOR LLM features, both subskills use `vkt.ViktorOpenAI` and do not require `OPENAI_API_KEY`.

No router-level `examples.md` is needed. Keep implementation examples inside the focused subskill files.
