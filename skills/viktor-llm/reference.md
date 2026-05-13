# VIKTOR LLM Reference

## Sources

- VIKTOR docs: https://docs.viktor.ai/docs/create-apps/viktor-llm/
- VIKTOR docs: https://docs.viktor.ai/docs/create-apps/viktor-llm/tool-use/
- VIKTOR docs: https://docs.viktor.ai/docs/create-apps/viktor-llm/vision/
- VIKTOR docs: https://docs.viktor.ai/docs/create-apps/user-input/llm-chat/

## Built-In Viktor LLM

Viktor LLM is VIKTOR's built-in large language model service. It does not require an external API key, third-party account, or application-managed environment variable. It exposes an OpenAI-compatible API, so VIKTOR apps use the standard `openai` Python client with VIKTOR-provided base URL and API key values.

```python
from openai import OpenAI
import viktor as vkt

client = OpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)
```

The VIKTOR docs mark the built-in Viktor LLM service as new in SDK v14.29.0. The LLM chat input itself is marked as new in v14.21.0.

For local development, include `openai` in `requirements.txt` unless the project is running in App Builder, where the VIKTOR docs state that the package is pre-installed.

## Chat Input

Use `vkt.Chat` in a `Parametrization` to place an LLM chat widget in the app editor. The `method` argument is required and names the controller method called when the user sends a message.

```python
class Parametrization(vkt.Parametrization):
    chat = vkt.Chat("Chatbot", method="call_llm")
```

The controller receives a `ChatConversation` object through `params.chat`.

```python
conversation = params.chat
messages = conversation.get_messages()
```

`get_messages()` returns the full conversation history in this shape:

```python
{
    "role": str,      # "user" or "assistant"
    "content": str,
}
```

`ChatConversation` stores `user` and `assistant` turns only. It does not store `system` messages, and the VIKTOR SDK currently supports only those two roles inside the conversation. For OpenAI-compatible chat completions, prepend a `system` message manually before sending the request.

`vkt.ChatResult` returns the LLM answer to the chat. Its response can be a complete string or an iterable of strings for streaming. The maximum `ChatResult` response size is 75,000 characters.

Useful `vkt.Chat` arguments:

- `method`: required controller method name.
- `first_message`: optional first message shown at the top of an empty conversation.
- `placeholder`: optional prompt placeholder.
- `flex`: optional width value from 0 to 100, defaulting to 33.
- `visible`: optional conditional visibility.

## Chat Completions Pattern

LLM chat completions are stateless. Each request must include the full conversation history. In VIKTOR, the `ChatConversation` tracks the user and assistant turns; the controller should call `conversation.get_messages()`, prepend the system message if needed, call the model, and return a `ChatResult`.

The VIKTOR docs use `openai.gpt-oss-120b` for built-in text chat examples.

For streaming, call `client.chat.completions.create(..., stream=True)` and pass an iterable that yields `chunk.choices[0].delta.content` values that are not `None`.

Fair-usage limits can return HTTP 429. The `openai` library raises that as `openai.RateLimitError`; catch it and raise `vkt.UserError` with a user-facing message.

## Tool Use

Tool use lets the LLM call Python functions in the VIKTOR app before composing its final answer. The VIKTOR docs describe tool use through the OpenAI-compatible Responses API, not the chat completions API.

Define tools with the standard OpenAI function schema:

```python
WEATHER_TOOL = {
    "type": "function",
    "name": "get_weather",
    "description": "Retrieve the current temperature for a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city_name": {"type": "string"},
            "unit": {"type": "string", "enum": ["Celsius", "Fahrenheit", "Kelvin"]},
        },
        "required": ["city_name", "unit"],
    },
}
```

Tool-use flow:

1. Start with `input=conversation.get_messages()` and `tools=[...]`.
2. Make a non-streamed `client.responses.create(...)` call so `response.output` can be inspected.
3. Store `response.id` as `previous_response_id`.
4. While `response.output` contains `function_call` items, parse each function call's JSON arguments.
5. Run the matching Python function in the app.
6. Send each tool result back as a `function_call_output` item with the original `call_id`.
7. Chain the next response using `previous_response_id`.
8. After tool calls are resolved, make one final streamed Responses API call with `input=[]` and the last `previous_response_id`.
9. Yield text from `response.output_text.delta` events.

The Responses API maintains context server-side for this flow by chaining calls with `previous_response_id`; do not resend the whole message history for each tool output step.

Catch `openai.APIStatusError` and `openai.APIConnectionError` around Responses API calls and raise `vkt.UserError` with a clear message.

## Vision

VIKTOR includes a built-in vision model for image analysis. It requires no external API key or third-party account.

The built-in vision model is supported through the Chat Completions API only. The Responses API is not supported for this model.

Vision flow:

1. Add a `vkt.FileField` for image upload.
2. Read the uploaded image bytes.
3. Base64-encode the bytes.
4. Wrap the encoded image in a data URI such as `data:image/jpeg;base64,...`.
5. Send a chat completions message whose `content` is a list containing a text prompt and an `image_url` item.
6. Use the model ID `mistral.ministral-3-14b-instruct`.

The VIKTOR docs show JPG upload with:

```python
image_bytes = params.image_file.file.getvalue_binary()
base64_image = base64.b64encode(image_bytes).decode("utf-8")
image_url = f"data:image/jpeg;base64,{base64_image}"
```

Supported MIME mappings:

- JPG or JPEG: `image/jpeg`
- PNG: `image/png`
- WEBP: `image/webp`

Make the `FileField` `file_types` match the image formats the app accepts.

Vision limitations:

- Only base64-encoded data URIs are supported for images.
- HTTP image URLs are not supported.
- The optional `detail` field in `image_url` is not supported.
- Fair-usage limits can raise `openai.RateLimitError`.

## External Provider Notes

The general `vkt.Chat` docs also show Anthropic, OpenAI, and Gemini client examples. Those providers require their own Python package and API key handling. For published VIKTOR applications, API keys and other environment variables are configured from the Apps section in the VIKTOR environment. For local CLI runs, environment variables can be passed with `viktor-cli start --env NAME="value"` or read in code with `os.getenv(...)`.

Use those external-provider patterns only when the user asks for an external provider. For built-in Viktor LLM, use `vkt.ViktorOpenAI` instead.
