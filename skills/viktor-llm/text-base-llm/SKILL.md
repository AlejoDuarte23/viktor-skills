---
name: viktor-llm-text-base-llm
description: "Use for text-based VIKTOR built-in LLM work: `vkt.Chat`, `vkt.ChatResult`, text model defaults, Chat Completions, Responses API tool use, OpenAI Agents SDK with `Runner.run_sync`, and model-visible JSON tool errors."
---

# VIKTOR Text-Based LLM

Use this subskill when a VIKTOR app needs text chat, tool use, or an Agents SDK agent backed by VIKTOR's built-in LLM.

## Sources

- VIKTOR docs: https://docs.viktor.ai/docs/create-apps/viktor-llm/
- VIKTOR docs: https://docs.viktor.ai/docs/create-apps/viktor-llm/tool-use/
- VIKTOR docs: https://docs.viktor.ai/docs/create-apps/user-input/llm-chat/
- OpenAI Agents SDK docs: https://openai.github.io/openai-agents-python/running_agents/
- OpenAI Agents SDK docs: https://openai.github.io/openai-agents-python/config/
- OpenAI Agents SDK docs: https://openai.github.io/openai-agents-python/tools/
- OpenAI Agents SDK docs: https://openai.github.io/openai-agents-python/models/
- OpenAI Agents SDK docs: https://openai.github.io/openai-agents-python/ref/model_settings/
- OpenAI gpt-oss cookbook: https://developers.openai.com/cookbook/articles/gpt-oss/run-colab#specify-reasoning-effort

## Defaults

- Use `vkt.ViktorOpenAI`; do not require `OPENAI_API_KEY`.
- Use text model `openai.gpt-oss-120b` unless the user asks for another supported built-in model.
- For manual Responses API calls with `openai.gpt-oss-120b`, pass `reasoning={"effort": "medium"}` on every `client.responses.create(...)` call in the tool loop.
- For `openai.gpt-oss-120b` Agents SDK agents, set thinking effort in the agent's `model_settings` with `ModelSettings(reasoning=Reasoning(effort="medium"))`.
- Use gpt-oss thinking effort values `low`, `medium`, or `high`; keep `medium` as the default unless the task needs faster or deeper reasoning.
- Include `viktor` and `openai` in `requirements.txt`.
- Add `openai-agents` and `pydantic` only when using the Agents SDK.
- The built-in VIKTOR LLM service is documented as new in SDK v14.29.0.
- `vkt.Chat` is documented as new in SDK v14.21.0.
- `vkt.ChatResult` can return a complete string or an iterable of strings. Its response size limit is 75,000 characters.

## VIKTOR OpenAI Wrapper

```python
from openai import OpenAI
import viktor as vkt

client = OpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)
```

For the Agents SDK, configure the default async client with the same VIKTOR wrapper:

```python
import viktor as vkt
from agents import set_default_openai_client, set_tracing_disabled
from openai import AsyncOpenAI

viktor_llm_client = AsyncOpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)
set_default_openai_client(viktor_llm_client, use_for_tracing=False)
set_tracing_disabled(True)
```

Disable tracing unless the app explicitly configures tracing credentials.

## Chat Input

Use `vkt.Chat` in a `Parametrization`. The `method` argument names the controller method called when the user sends a message.

```python
class Parametrization(vkt.Parametrization):
    chat = vkt.Chat("Chatbot", method="call_llm")
```

The controller receives a `ChatConversation` object through `params.chat`. Call `conversation.get_messages()` to retrieve the full user and assistant history:

```python
[
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "How can I help?"},
]
```

`ChatConversation` stores only `user` and `assistant` turns. For normal Chat Completions calls, prepend a `system` message manually before sending the request. For Agents SDK calls, put system behavior in the `Agent.instructions` instead.

Useful `vkt.Chat` arguments:

- `method`: required controller method name.
- `first_message`: optional first message shown at the top of an empty conversation.
- `placeholder`: optional prompt placeholder.
- `flex`: optional width value from 0 to 100, defaulting to 33.
- `visible`: optional conditional visibility.

## Plain Text Chat Example

```python
import openai
import viktor as vkt
from openai import OpenAI


client = OpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)


class Parametrization(vkt.Parametrization):
    chat = vkt.Chat("Chat", method="call_llm", placeholder="Ask a question")


class Controller(vkt.Controller):
    parametrization = Parametrization

    def call_llm(self, params, **kwargs):
        conversation = params.chat
        if not conversation:
            return None

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            *conversation.get_messages(),
        ]

        try:
            response = client.chat.completions.create(
                model="openai.gpt-oss-120b",
                messages=messages,
            )
        except openai.RateLimitError:
            raise vkt.UserError("Fair usage limit reached. Please try again later.")

        return vkt.ChatResult(conversation, response.choices[0].message.content or "")
```

## Responses API Tool Use

Use the Responses API when the app needs a manual tool loop without the Agents SDK. Define OpenAI function schemas, inspect `response.output`, execute matching Python functions, and send tool outputs back as `function_call_output` items with the original `call_id`.

For `openai.gpt-oss-120b`, keep the thinking effort explicit on every Responses API call in the loop:

```python
import json
from typing import Any

import openai
import viktor as vkt
from openai import OpenAI


MODEL_NAME = "openai.gpt-oss-120b"
REASONING_EFFORT = "medium"

client = OpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)

ADD_NUMBERS_TOOL = {
    "type": "function",
    "name": "add_numbers",
    "description": "Add two numbers.",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
        },
        "required": ["a", "b"],
    },
}


def tool_ok(data: Any = None, message: str = "ok") -> str:
    payload: dict[str, Any] = {"status": "ok", "message": message}
    if data is not None:
        payload["data"] = data
    return json.dumps(payload, default=str)


def tool_error(error_type: str, message: str) -> str:
    return json.dumps(
        {"status": "error", "error_type": error_type, "message": message},
        default=str,
    )


def run_add_numbers(arguments: str) -> str:
    try:
        args = json.loads(arguments)
        return tool_ok({"sum": float(args["a"]) + float(args["b"])}, "Numbers added.")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return tool_error(type(exc).__name__, "Tool arguments were invalid.")


class Parametrization(vkt.Parametrization):
    chat = vkt.Chat("Chat", method="call_llm", placeholder="Ask a question")


class Controller(vkt.Controller):
    parametrization = Parametrization

    def call_llm(self, params, **kwargs):
        conversation = params.chat
        if not conversation:
            return None

        try:
            response = client.responses.create(
                model=MODEL_NAME,
                input=conversation.get_messages(),
                tools=[ADD_NUMBERS_TOOL],
                reasoning={"effort": REASONING_EFFORT},
            )

            while any(item.type == "function_call" for item in response.output):
                tool_outputs = []
                for item in response.output:
                    if item.type != "function_call":
                        continue
                    if item.name == "add_numbers":
                        output = run_add_numbers(item.arguments)
                    else:
                        output = tool_error("UnknownTool", f"Unknown tool: {item.name}")
                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": output,
                        }
                    )

                response = client.responses.create(
                    model=MODEL_NAME,
                    input=tool_outputs,
                    previous_response_id=response.id,
                    tools=[ADD_NUMBERS_TOOL],
                    reasoning={"effort": REASONING_EFFORT},
                )
        except openai.RateLimitError:
            raise vkt.UserError("Fair usage limit reached. Please try again later.")
        except openai.APIConnectionError as exc:
            raise vkt.UserError(f"Network error while calling the LLM: {exc}")
        except openai.APIStatusError as exc:
            raise vkt.UserError(f"LLM API error {exc.status_code}: {exc.message}")

        return vkt.ChatResult(conversation, response.output_text)
```

Expected tool failures should be sent back to the model as tool output:

```json
{
  "status": "error",
  "error_type": "MissingPrerequisite",
  "message": "Required data is missing.",
  "retry_action": {
    "tool": "create_required_data",
    "reason": "Generate the missing input before retrying."
  }
}
```

Use `previous_response_id` to chain tool output calls. Do not resend the whole chat history for each tool output step. Catch `openai.APIStatusError` and `openai.APIConnectionError` around Responses API calls and raise `vkt.UserError` with a clear user-facing message.

## Agents SDK Tool Use

Use the OpenAI Agents SDK when the app should let the SDK manage the agent loop, tool calls, and final answer.

Rules:

- Import `Reasoning` from `openai.types.shared` and `ModelSettings` from `agents`.
- Configure `AsyncOpenAI` with `vkt.ViktorOpenAI.get_base_url(version="v1")` and `get_api_key()`.
- Call `set_default_openai_client(viktor_llm_client, use_for_tracing=False)`.
- Disable tracing unless it is explicitly configured.
- Put the gpt-oss thinking effort on the agent with `model_settings=ModelSettings(reasoning=Reasoning(effort="medium"))`.
- Define tools with `@function_tool`.
- Add `RunContextWrapper[YourContext]` as the first argument when a tool needs app context.
- Run from VIKTOR's synchronous controller method with `Runner.run_sync(...)`.
- Always pass `max_turns` to prevent infinite tool loops.
- Return `vkt.ChatResult(conversation, str(result.final_output))`.
- Return JSON strings for expected tool errors so the model can recover. Do not raise expected tool errors.
- Use `failure_error_function` as a last-resort JSON fallback for unexpected crashes.

Compact example:

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Annotated, Any

import openai
import viktor as vkt
from agents import (
    Agent,
    ModelSettings,
    RunContextWrapper,
    Runner,
    function_tool,
    set_default_openai_client,
    set_tracing_disabled,
)
from openai import AsyncOpenAI
from openai.types.shared import Reasoning
from pydantic import Field


MODEL_NAME = "openai.gpt-oss-120b"
REASONING_EFFORT = "medium"
MAX_AGENT_TURNS = 8


@dataclass
class AgentContext:
    entity_id: int | None = None
    workspace_id: int | None = None


def tool_ok(data: Any = None, message: str = "ok") -> str:
    payload: dict[str, Any] = {"status": "ok", "message": message}
    if data is not None:
        payload["data"] = data
    return json.dumps(payload, default=str)


def tool_error(
    error_type: str,
    message: str,
    retry_action: dict[str, Any] | None = None,
) -> str:
    payload: dict[str, Any] = {
        "status": "error",
        "error_type": error_type,
        "message": message,
    }
    if retry_action:
        payload["retry_action"] = retry_action
    return json.dumps(payload, default=str)


def unexpected_tool_error(ctx: RunContextWrapper[AgentContext], exc: Exception) -> str:
    return tool_error(type(exc).__name__, str(exc))


viktor_llm_client = AsyncOpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)
set_default_openai_client(viktor_llm_client, use_for_tracing=False)
set_tracing_disabled(True)


@function_tool(failure_error_function=unexpected_tool_error)
def add_numbers(
    ctx: RunContextWrapper[AgentContext],
    a: Annotated[float, Field(description="First number")],
    b: Annotated[float, Field(description="Second number")],
) -> str:
    """Add two numbers."""
    return tool_ok({"sum": a + b}, "Numbers added.")


agent = Agent[AgentContext](
    name="VIKTOR Assistant",
    model=MODEL_NAME,
    model_settings=ModelSettings(
        reasoning=Reasoning(effort=REASONING_EFFORT),
    ),
    instructions=(
        "You are an assistant inside a VIKTOR app. Tool outputs are JSON strings. "
        "If a tool returns status=ok, use the data field. If a tool returns "
        "status=error, read error_type, message, and retry_action, then retry once "
        "when the correction is clear. If the retry fails, explain the failing tool "
        "and the next action."
    ),
    tools=[add_numbers],
)


class Parametrization(vkt.Parametrization):
    chat = vkt.Chat("Agent chat", method="call_llm", placeholder="Ask the agent")


class Controller(vkt.Controller):
    parametrization = Parametrization

    def call_llm(self, params, entity_id=None, workspace_id=None, **kwargs):
        conversation = params.chat
        if not conversation:
            return None

        chat_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in conversation.get_messages()
        ]

        try:
            result = Runner.run_sync(
                agent,
                input=chat_history,
                context=AgentContext(entity_id=entity_id, workspace_id=workspace_id),
                max_turns=MAX_AGENT_TURNS,
            )
        except openai.RateLimitError:
            raise vkt.UserError("Fair usage limit reached. Please try again later.")
        except openai.APIConnectionError as exc:
            raise vkt.UserError(f"Network error while calling the LLM: {exc}")
        except openai.APIStatusError as exc:
            raise vkt.UserError(f"LLM API error {exc.status_code}: {exc.message}")

        return vkt.ChatResult(conversation, str(result.final_output))
```

## External Provider Notes

External Anthropic, OpenAI, or Gemini examples require their own packages and API keys. Use those only when the user explicitly asks for an external provider. For built-in VIKTOR LLM work, use `vkt.ViktorOpenAI`.
