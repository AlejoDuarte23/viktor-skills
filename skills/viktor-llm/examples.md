# VIKTOR LLM Examples

## Requirements

```text
viktor
openai
```

## Streaming Chat With Built-In Viktor LLM

```python
import openai
import viktor as vkt
from openai import OpenAI


client = OpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)


class Parametrization(vkt.Parametrization):
    chat = vkt.Chat(
        "Chat",
        method="call_llm",
        placeholder="Ask a question",
        first_message="How can I help you?",
    )


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
            stream = client.chat.completions.create(
                model="openai.gpt-oss-120b",
                messages=messages,
                stream=True,
            )
        except openai.RateLimitError:
            raise vkt.UserError("Fair usage limit reached. Please try again later.")

        text_stream = (
            chunk.choices[0].delta.content
            for chunk in stream
            if chunk.choices[0].delta.content is not None
        )
        return vkt.ChatResult(conversation, text_stream)
```

## Tool Use With The Responses API

```python
import json

import openai
import viktor as vkt
from openai import OpenAI


WEATHER_TOOL = {
    "type": "function",
    "name": "get_weather",
    "description": "Retrieve the current temperature for a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city_name": {
                "type": "string",
                "description": "The city to get the weather for.",
            },
            "unit": {
                "type": "string",
                "enum": ["Celsius", "Fahrenheit", "Kelvin"],
                "description": "The temperature unit.",
            },
        },
        "required": ["city_name", "unit"],
    },
}


def call_weather_tool(city_name: str, unit: str) -> str:
    return f"22 {unit}s"


class Parametrization(vkt.Parametrization):
    chat = vkt.Chat("Chat", method="submit_responses")


class Controller(vkt.Controller):
    parametrization = Parametrization

    def submit_responses(self, params, **kwargs):
        client = OpenAI(
            base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
            api_key=vkt.ViktorOpenAI.get_api_key(),
        )
        conversation = params.chat
        previous_response_id = None

        try:
            response = client.responses.create(
                model="openai.gpt-oss-120b",
                input=conversation.get_messages(),
                tools=[WEATHER_TOOL],
                max_output_tokens=96000,
            )
            previous_response_id = response.id

            while any(item.type == "function_call" for item in response.output):
                tool_inputs = []
                for output_item in response.output:
                    if output_item.type != "function_call":
                        continue

                    args = json.loads(output_item.arguments)
                    if output_item.name == "get_weather":
                        result = call_weather_tool(
                            city_name=args["city_name"],
                            unit=args["unit"],
                        )
                        tool_inputs.append(
                            {
                                "type": "function_call_output",
                                "call_id": output_item.call_id,
                                "output": result,
                            }
                        )

                if not tool_inputs:
                    break

                response = client.responses.create(
                    model="openai.gpt-oss-120b",
                    input=tool_inputs,
                    previous_response_id=previous_response_id,
                    tools=[WEATHER_TOOL],
                    max_output_tokens=96000,
                )
                previous_response_id = response.id
        except openai.APIStatusError as exc:
            raise vkt.UserError(f"API error {exc.status_code}: {exc.message}")
        except openai.APIConnectionError as exc:
            raise vkt.UserError(f"Network error while calling the API: {exc}")

        def response_generator():
            with client.responses.create(
                model="openai.gpt-oss-120b",
                input=[],
                previous_response_id=previous_response_id,
                tools=[WEATHER_TOOL],
                max_output_tokens=96000,
                stream=True,
            ) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        yield event.delta

        return vkt.ChatResult(conversation, response_generator())
```

## Vision Image Analysis

```python
import base64

import viktor as vkt
from openai import OpenAI


client = OpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)


class Parametrization(vkt.Parametrization):
    image_file = vkt.FileField(
        "Upload image",
        file_types=[".jpg", ".jpeg"],
        description="Upload a JPG image to analyze.",
    )


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Image analysis")
    def analyze_image(self, params, **kwargs):
        if not params.image_file:
            return vkt.WebResult(html="<p>Please upload an image to get started.</p>")

        image_bytes = params.image_file.file.getvalue_binary()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:image/jpeg;base64,{base64_image}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe what is shown in this image."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]
        response = client.chat.completions.create(
            model="mistral.ministral-3-14b-instruct",
            messages=messages,
        )
        result_text = response.choices[0].message.content
        return vkt.WebResult(html=f"<p>{result_text}</p>")
```
