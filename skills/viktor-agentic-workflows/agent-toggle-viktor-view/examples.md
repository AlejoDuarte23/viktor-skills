# Agent Toggle VIKTOR View Examples

## Visibility Callback

```python
import viktor as vkt


STORAGE_SCOPE = "entity"
SHOW_SURROGATE_KEY = "show_surrogate"


def is_surrogate_view_visible(params, **kwargs) -> bool:
    try:
        content = vkt.Storage().get(SHOW_SURROGATE_KEY, scope=STORAGE_SCOPE).getvalue()
    except FileNotFoundError:
        return False
    return content == "show"
```

## Optional Reset On Fresh Chat

```python
def is_surrogate_view_visible(params, **kwargs) -> bool:
    if not getattr(params, "chat", None):
        try:
            vkt.Storage().delete(SHOW_SURROGATE_KEY, scope=STORAGE_SCOPE)
        except FileNotFoundError:
            pass
        return False

    try:
        content = vkt.Storage().get(SHOW_SURROGATE_KEY, scope=STORAGE_SCOPE).getvalue()
    except FileNotFoundError:
        return False
    return content == "show"
```

## Wire The Callback To A View

```python
class Controller(vkt.Controller):
    @vkt.WebView(
        "Surrogate Inference",
        duration_guess=3,
        visible=is_surrogate_view_visible,
    )
    def surrogate_inference_viewer(self, params, **kwargs):
        return vkt.WebResult(html="<p>Surrogate result is ready.</p>")
```

The same callback shape works for `DataView`, `TableView`, `GeometryView`, and other views that support `visible=`.

## Agents SDK Tool

```python
from typing import Literal

import viktor as vkt
from agents import function_tool


@function_tool
def show_hide_surrogate_view(action: Literal["show", "hide"]) -> str:
    vkt.Storage().set(
        SHOW_SURROGATE_KEY,
        data=vkt.File.from_data(action),
        scope=STORAGE_SCOPE,
    )
    return f"Surrogate Inference view is now set to: {action}."
```

Register this tool in the agent registry and describe it in `system_prompt.xml`:

```xml
<view_visibility>
  Use show_hide_surrogate_view when the user asks to show or hide the surrogate view.
  Pass action="show" to reveal it and action="hide" to hide it.
</view_visibility>
```

## Separate Show And Hide Tools

```python
@function_tool
def show_surrogate_view() -> str:
    vkt.Storage().set(
        SHOW_SURROGATE_KEY,
        data=vkt.File.from_data("show"),
        scope=STORAGE_SCOPE,
    )
    return "Surrogate Inference view is now visible."


@function_tool
def hide_surrogate_view() -> str:
    vkt.Storage().set(
        SHOW_SURROGATE_KEY,
        data=vkt.File.from_data("hide"),
        scope=STORAGE_SCOPE,
    )
    return "Surrogate Inference view is now hidden."
```
