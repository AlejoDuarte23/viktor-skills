---
name: viktor-llm-vision-llm
description: Use for VIKTOR built-in vision LLM work: image upload fields, base64 data URI inputs, MIME type handling, the `mistral.ministral-3-14b-instruct` vision model, and image-analysis outputs without external API keys.
---

# VIKTOR Vision LLM

Use this subskill when a VIKTOR app needs to analyze an uploaded image with VIKTOR's built-in vision model.

## Sources

- VIKTOR docs: https://docs.viktor.ai/docs/create-apps/viktor-llm/
- VIKTOR docs: https://docs.viktor.ai/docs/create-apps/viktor-llm/vision/

## Defaults

- Use `vkt.ViktorOpenAI`; do not require `OPENAI_API_KEY`.
- Use vision model `mistral.ministral-3-14b-instruct`.
- Use the Chat Completions API for vision.
- Do not use the Responses API for the built-in vision model.
- Include `viktor` and `openai` in `requirements.txt`.
- Read uploaded images with `params.<field>.file.getvalue_binary()`.
- Send images as base64 data URIs.

## VIKTOR OpenAI Wrapper

```python
from openai import OpenAI
import viktor as vkt

client = OpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)
```

## Image Input Rules

Supported MIME mappings:

- JPG or JPEG: `image/jpeg`
- PNG: `image/png`
- WEBP: `image/webp`

Limitations:

- Only base64-encoded data URIs are supported for images.
- HTTP image URLs are not supported.
- The optional `detail` field in `image_url` is not supported.
- Fair-usage limits can raise `openai.RateLimitError`.

Make the `FileField.file_types` match the image formats the app accepts.

## Base64 Data URI

```python
import base64


def image_data_uri(image_bytes: bytes, extension: str) -> str:
    mime_by_extension = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime_type = mime_by_extension.get(extension.lower(), "image/jpeg")
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"
```

## Vision Example

```python
import base64
from pathlib import Path

import openai
import viktor as vkt
from openai import OpenAI


client = OpenAI(
    base_url=vkt.ViktorOpenAI.get_base_url(version="v1"),
    api_key=vkt.ViktorOpenAI.get_api_key(),
)


def image_data_uri(image_bytes: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    mime_by_extension = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime_type = mime_by_extension.get(suffix, "image/jpeg")
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


class Parametrization(vkt.Parametrization):
    image_file = vkt.FileField(
        "Upload image",
        file_types=[".jpg", ".jpeg", ".png", ".webp"],
        description="Upload an image to analyze.",
    )


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.WebView("Image analysis")
    def analyze_image(self, params, **kwargs):
        if not params.image_file:
            return vkt.WebResult(html="<p>Please upload an image to get started.</p>")

        image = params.image_file.file
        image_url = image_data_uri(
            image.getvalue_binary(),
            params.image_file.filename or "image.jpg",
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe what is shown in this image."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]

        try:
            response = client.chat.completions.create(
                model="mistral.ministral-3-14b-instruct",
                messages=messages,
            )
        except openai.RateLimitError:
            raise vkt.UserError("Fair usage limit reached. Please try again later.")

        result_text = response.choices[0].message.content or ""
        return vkt.WebResult(html=f"<p>{result_text}</p>")
```
