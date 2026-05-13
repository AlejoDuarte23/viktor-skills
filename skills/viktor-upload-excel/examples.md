# VIKTOR Upload Excel Examples

## Requirements

```text
viktor
pandas
openpyxl
```

## Parser

```python
from io import BytesIO

import pandas as pd
import viktor as vkt


def parse_excel(file: vkt.File) -> pd.DataFrame:
    raw = file.getvalue_binary()
    with BytesIO(raw) as buffer:
        return pd.read_excel(buffer, engine="openpyxl")
```

## Upload Field and Preview

```python
class Parametrization(vkt.Parametrization):
    xlsx = vkt.FileField(
        "Excel file (.xlsx)",
        file_types=[".xlsx"],
        description="Use a workbook with headers in the first row.",
    )


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Preview")
    def preview(self, params, **kwargs):
        if not params.xlsx:
            return vkt.TableResult([], column_headers=["Message"])

        df = parse_excel(params.xlsx)
        return vkt.TableResult(
            df.head(20).values.tolist(),
            column_headers=list(df.columns),
        )
```
