 Upload and Process Excel Files
This example uses **pandas** and **openpyxl** to read the first sheet of an uploaded `.xlsx` file. Column headers must be in the first row.

### requirements.txt

```text
viktor
pandas
openpyxl
```


### controller.py

> **IMPORTANT NOTE! on `vkt.File`**
> The object returned by a `FileField` is a **`vkt.File`**. Obtain its content with `.getvalue()` (text) or `.getvalue_binary()` (bytes). If you need stream access (`.open()`), first use the `.file` property or copy it to a writable file. Calling `.open()` directly on the `FileField` value leads to errors.

```python
from io import BytesIO
from typing import Union

import pandas as pd
import viktor as vkt


def parse_excel(file: vkt.File) -> pd.DataFrame:
    """Convert an uploaded Excel file (first sheet) to a DataFrame.

    Args:
        file: Value returned by the **FileField** (`vkt.File`).

    Returns:
        DataFrame with the sheet content.
    """
    raw: bytes = file.getvalue_binary()
    with BytesIO(raw) as buf:
        return pd.read_excel(buf, engine="openpyxl")


class Parametrization(vkt.Parametrization):
    xlsx = vkt.FileField(
        "Excel file (.xlsx)",
        file_types=[".xlsx"],
        description="Headers must be in the first row",
    )


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Preview", duration_guess=1)
    def preview(self, params: Parametrization, **kwargs) -> vkt.TableResult:
        """Display the uploaded Excel content in a table view."""
        if not params.xlsx:
            return vkt.TableResult(
                [["Upload an Excel file to preview its content"]],
                row_headers=[],
                column_headers=[],
            )

        df: pd.DataFrame = parse_excel(params.xlsx)
        data = df.values.tolist()
        return vkt.TableResult(
            data,
            row_headers=[str(i) for i in df.index],
            column_headers=list(df.columns),
        )
```


