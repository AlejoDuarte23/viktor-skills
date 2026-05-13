# VIKTOR STAAD.Pro Worker Examples

## App File Layout

```text
my-app
├── app.py
├── run_staad_model.py
├── requirements.txt
└── viktor.config.toml
```

## Controller Worker Call

```python
import json
from io import BytesIO

import viktor as vkt
from viktor.core import File
from viktor.external.python import PythonAnalysis


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Member forces", duration_guess=20, update_label="Run STAAD")
    def member_forces(self, params, **kwargs):
        model_input = {
            "length": params.length,
            "height": params.height,
            "cross_section": params.cross_section,
        }
        input_file = File.from_data(json.dumps(model_input).encode("utf-8"))

        analysis = PythonAnalysis(
            "run_staad_model.py",
            files=[("input.json", input_file)],
            output_filenames=["results.json"],
        )
        analysis.execute(timeout=120)

        result_file = analysis.get_output_file("results.json")
        results = json.loads(result_file.getvalue())
        rows = results.get("member_forces", [])
        return vkt.TableResult(rows, column_headers=["Member", "Fx", "Fy", "Fz", "Mx", "My", "Mz"])
```

## Worker Output Contract

```json
{
  "member_forces": [
    [1, 12.4, 0.0, -8.1, 0.0, 3.2, 0.0]
  ],
  "warnings": []
}
```

Keep the worker contract small and explicit. The VIKTOR controller should not depend on STAAD COM objects directly; it should depend on the JSON output from the worker.
