# VIKTOR File Management Reference

Official sources:

- <https://docs.viktor.ai/docs/create-apps/managing-files/uploading-files/>
- <https://docs.viktor.ai/docs/create-apps/managing-files/downloading-files/>

## Upload Choices

VIKTOR has two main upload patterns:

- `FileField` or `MultiFileField`: attach a file directly to a field in the current entity. This is the encouraged default because the user can stay inside the current entity, and the file is available in `params`.
- File-like entity type: create an entity type that opens an upload modal when the user creates that entity. This takes more navigation, but it can isolate a file with its own views.

For Autodesk cloud files, use `AutodeskFileField` to reference the cloud file directly instead of downloading and uploading it through VIKTOR.

## Upload With `FileField`

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    csv_file = vkt.FileField("CSV file")
```

`FileField` and `MultiFileField` appear as dropdown fields with upload support. After the user selects a file, the value in `params` is a `FileResource`.

Use:

- `params.csv_file.file` to retrieve the VIKTOR `File`.
- `params.csv_file.filename` to retrieve the selected filename.

`FileResource` objects from `FileField` and `MultiFileField` are memoizable.

## Reading Uploaded Content

Use the `File` object with `.open()`:

```python
csv_file = params.csv_file.file
with csv_file.open() as r:
    df = pd.read_csv(r)
```

For text parsing, pass an encoding:

```python
with file.open(encoding="utf-8") as f:
    for line in f:
        ...
```

Avoid reading complete large files into memory. When large files are required, increase the upload limit and read in chunks.

## Temporary Files

The upload docs mention temporary files as possible but not recommended. A temporary file is created securely and removed after closing, and a `NamedTemporaryFile` returns a file-like object that can be used in a `with` statement.

## File-Like Entity Type

Use `@vkt.ParamsFromFile` on a controller method to process the uploaded file when a file-like entity is created.

```python
import viktor as vkt


class Controller(vkt.Controller):
    @vkt.ParamsFromFile()
    def process_file(self, file: vkt.File, **kwargs):
        return {}
```

The method can parse file content and return a dictionary with values to store on fields defined in the entity parametrization.

```python
class Parametrization(vkt.Parametrization):
    number_of_entries = vkt.NumberField("Number of entries")
    project_name = vkt.TextField("Project")


class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.ParamsFromFile()
    def process_file(self, file: vkt.File, **kwargs):
        number_of_entries = 0
        project_name = ""
        with file.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f):
                if lineno == 0:
                    _, project_name = line.split("=")
                elif line.startswith("Entry"):
                    number_of_entries += 1
        return {
            "number_of_entries": number_of_entries,
            "project_name": project_name,
        }
```

For nested parametrization structures, return a nested dictionary that matches the field structure.

```python
return {
    "tab": {
        "section": {
            "number_of_entries": number_of_entries,
            "project_name": project_name,
        }
    }
}
```

Do not store complete large file content in fields. Store parsed values only. The file content can be retrieved later through the API if needed.

## Upload Restrictions

Use `max_size` for larger allowed uploads:

```python
file = vkt.FileField("CPT file", max_size=100_000_000)  # 100 MB

@vkt.ParamsFromFile(max_size=100_000_000)
def process_file(self, file: vkt.File, **kwargs):
    ...
```

Use `file_types` to restrict allowed extensions:

```python
file = vkt.FileField("Image", file_types=[".png", ".jpg", ".jpeg"])

@vkt.ParamsFromFile(file_types=[".png", ".jpg", ".jpeg"])
def process_file(self, file: vkt.File, **kwargs):
    ...
```

## Excel vs CSV

The VIKTOR docs recommend CSV over Excel when possible. CSV is plain text, imports special characters more predictably, and can be compared in version control. A multi-sheet Excel workbook needs one CSV per sheet because CSV has no sheet concept.

Use the existing `../viktor-upload-excel/SKILL.md` when the task specifically requires `.xlsx`.

## Download With `DownloadButton`

Add a `DownloadButton` in the parametrization and implement the linked controller method.

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    download = vkt.DownloadButton("Download", method="download_file")


class Controller(vkt.Controller):
    def download_file(self, params, **kwargs):
        return vkt.DownloadResult("file content", "filename.txt")
```

## Downloading `File` Objects

`DownloadResult` can directly accept a VIKTOR `File`. This is useful for files returned by document conversions, spreadsheet rendering, or external analyses.

```python
return vkt.DownloadResult(filled_spreadsheet, "filled_spreadsheet.xlsx")
return vkt.DownloadResult(word_file, "word_file.docx")
return vkt.DownloadResult(result_file, "scia_result.xml")
```

## Downloading Text, Bytes, and JSON

For formats such as `.txt`, `.xml`, `.json`, and other custom files, pass file content as `str` or `bytes` and provide a filename.

```python
return vkt.DownloadResult(json_text, "results.json")
```

## Downloading Multiple Files

Use `zipped_files` to bundle multiple generated files:

```python
return vkt.DownloadResult(
    zipped_files={
        "my_file_1.txt": my_file_1,
        "my_file_2.txt": my_file_2,
    },
    file_name="my_file.zip",
)
```

Alternatively, create a zip manually with Python's standard `zipfile` module and return the resulting `File`.
