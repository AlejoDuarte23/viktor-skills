# VIKTOR File Management Examples

## CSV Upload and Preview

```python
import pandas as pd
import viktor as vkt


class Parametrization(vkt.Parametrization):
    csv_file = vkt.FileField(
        "CSV file",
        file_types=[".csv"],
        description="Upload a comma-separated file with headers in the first row.",
    )


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Preview")
    def preview(self, params, **kwargs):
        if not params.csv_file:
            return vkt.TableResult([], column_headers=["Message"])

        file_resource = params.csv_file
        with file_resource.file.open() as r:
            df = pd.read_csv(r)

        return vkt.TableResult(
            df.head(20).values.tolist(),
            column_headers=list(df.columns),
        )
```

## Upload Size and Type Restrictions

```python
class Parametrization(vkt.Parametrization):
    image = vkt.FileField(
        "Image",
        file_types=[".png", ".jpg", ".jpeg"],
        max_size=100_000_000,
    )
```

## File-Like Entity Parser

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    number_of_entries = vkt.NumberField("Number of entries")
    project_name = vkt.TextField("Project")


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.ParamsFromFile(file_types=[".txt"])
    def process_file(self, file: vkt.File, **kwargs):
        number_of_entries = 0
        project_name = ""

        with file.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f):
                line = line.strip()
                if lineno == 0 and "=" in line:
                    _, project_name = line.split("=", maxsplit=1)
                elif line.startswith("Entry"):
                    number_of_entries += 1

        return {
            "number_of_entries": number_of_entries,
            "project_name": project_name,
        }
```

## Download Generated Text

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    download = vkt.DownloadButton("Download report", method="download_report")


class Controller(vkt.Controller):
    parametrization = Parametrization

    def download_report(self, params, **kwargs):
        content = "Result,Value\nStatus,OK\n"
        return vkt.DownloadResult(content, "report.csv")
```

## Download Generated JSON

```python
import json
import viktor as vkt


class Parametrization(vkt.Parametrization):
    download = vkt.DownloadButton("Download JSON", method="download_json")


class Controller(vkt.Controller):
    parametrization = Parametrization

    def download_json(self, params, **kwargs):
        payload = {"status": "ok", "values": [1, 2, 3]}
        return vkt.DownloadResult(json.dumps(payload, indent=2), "results.json")
```

## Download Multiple Files as Zip

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    download = vkt.DownloadButton("Download files", method="download_files")


class Controller(vkt.Controller):
    parametrization = Parametrization

    def download_files(self, params, **kwargs):
        return vkt.DownloadResult(
            zipped_files={
                "summary.txt": "Status: OK\n",
                "values.csv": "name,value\nA,1\nB,2\n",
            },
            file_name="results.zip",
        )
```

## Download a VIKTOR `File`

Use this shape when another VIKTOR helper or an external analysis returns a `File`.

```python
class Controller(vkt.Controller):
    parametrization = Parametrization

    def download_spreadsheet(self, params, **kwargs):
        filled_spreadsheet = vkt.spreadsheet.render_spreadsheet(...)
        return vkt.DownloadResult(filled_spreadsheet, "filled_spreadsheet.xlsx")
```
