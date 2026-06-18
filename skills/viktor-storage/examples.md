# VIKTOR Storage Examples

## JSON Storage Helpers

```python
import json

import viktor as vkt


def write_json_to_storage(key: str, payload: dict, *, scope: str = "entity") -> None:
    vkt.Storage().set(
        key,
        data=vkt.File.from_data(json.dumps(payload, indent=2)),
        scope=scope,
    )


def read_json_from_storage(key: str, *, scope: str = "entity") -> dict:
    stored_file = vkt.Storage().get(key, scope=scope)
    return json.loads(stored_file.getvalue_binary().decode("utf-8"))
```

## Store Results From One View And Read Them In Another

```python
class Controller(vkt.Controller):
    @vkt.DataView("Run Analysis", duration_guess=10)
    def run_analysis(self, params, **kwargs):
        payload = {
            "max_moment": 124.5,
            "utilization": 0.82,
        }
        write_json_to_storage("analysis/latest.json", payload)
        return vkt.DataResult(
            vkt.DataGroup(
                vkt.DataItem("Stored result", "analysis/latest.json"),
            )
        )

    @vkt.DataView("Stored Result", duration_guess=1)
    def stored_result(self, params, **kwargs):
        try:
            payload = read_json_from_storage("analysis/latest.json")
        except FileNotFoundError:
            raise vkt.UserError("Run the analysis before opening stored results.")

        return vkt.DataResult(
            vkt.DataGroup(
                vkt.DataItem("Max moment", payload["max_moment"], suffix="kNm"),
                vkt.DataItem("Utilization", payload["utilization"]),
            )
        )
```

## Storage-Controlled View Visibility

```python
SHOW_KEY = "show_detail_view"


def detail_view_visible(params, **kwargs):
    try:
        return vkt.Storage().get(SHOW_KEY, scope="entity").getvalue() == "show"
    except FileNotFoundError:
        return False


class Controller(vkt.Controller):
    @vkt.DataView("Details", visible=detail_view_visible)
    def details(self, params, **kwargs):
        return vkt.DataResult(vkt.DataGroup(vkt.DataItem("Visible", "yes")))

    def show_details(self, params, **kwargs):
        vkt.Storage().set(SHOW_KEY, data=vkt.File.from_data("show"), scope="entity")
```

## Mock Storage In Tests

```python
import unittest

import viktor as vkt
from munch import munchify
from viktor.testing import mock_Storage

from app import Controller


class TestStorage(unittest.TestCase):
    @mock_Storage(get=[vkt.File.from_data(b'{"status": "ok"}')])
    def test_reads_cached_result(self):
        result = Controller().stored_result(params=munchify({}))
        self.assertIsNotNone(result)
```
