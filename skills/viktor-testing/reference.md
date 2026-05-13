# VIKTOR Testing Reference

Official sources:

- <https://docs.viktor.ai/docs/create-apps/automated-testing/>
- <https://docs.viktor.ai/docs/create-apps/automated-testing/mocking/>
- <https://docs.viktor.ai/docs/create-apps/references/cli/#test>
- <https://docs.viktor.ai/sdk/api/testing/>
- <https://github.com/viktor-platform/test-views>
- <https://github.com/viktor-platform/test-views/blob/main/test_views.py>

## Mental Model

Most VIKTOR automated tests run local Python code. They do not click the app UI and they do not call `entity.compute(...)`.

The common local test model is:

```python
from app import Controller

controller = Controller()
result = controller.geometry_view(params=params)
```

This is different from:

```python
api = vkt.api_v1.API()
entity = api.get_entity(1)
result = entity.compute(method_name="geometry_view", params={...})
```

`entity.compute(...)` is an SDK API call to the VIKTOR platform. Local tests bypass that API and call the method as Python. This matters because SDK computation can fail in a development workspace while the local view test can still be valid.

## Test Command And Layout

The normal VIKTOR command is:

```bash
viktor-cli test
```

Use this from the application root. Tests must live in a folder named `tests`.

```text
my-viktor-app/
├── app.py
├── requirements.txt
├── viktor.config.toml
└── tests/
    ├── __init__.py
    ├── test_views.py
    ├── test_calculations.py
    └── params/
        └── design_case.json
```

VIKTOR testing is based on Python `unittest`. Keep tests discoverable with filenames such as `test_*.py`.

Useful commands:

```bash
viktor-cli test
viktor-cli run -- python -m unittest discover -s tests
viktor-cli run -- python -m unittest tests.test_views
viktor-cli run -- python -m unittest tests.test_views.TestViews.test_geometry_view
```

Use `viktor-cli run -- ...` when you need a custom Python command inside the VIKTOR-managed environment.

## Choosing The Test Type

| Need | Recommended test |
| --- | --- |
| Pure engineering formula | Unit test the helper function without VIKTOR mocks. |
| View returns a result | Instantiate `Controller`, pass params, assert a result type or payload. |
| View handles many input combinations | Use a Hypothesis strategy built from `Parametrization`, then call view methods directly. |
| Button mutates entities | Use `mock_API` and `MockedEntity`. |
| Method uses entity id, user, or workspace context | Pass those keyword arguments directly if the controller method accepts them, and mock API calls if it creates `vkt.api_v1.API()`. |
| Method uses files from params | Use `mock_params` with `MockedFileResource`. |
| Method uses `ParamsFromFile` | Use `mock_ParamsFromFile`. |
| Method uses VIKTOR storage | Use `mock_Storage`. |
| Method uses external workers | Use the matching worker decorator such as `mock_PythonAnalysis`. |
| Method calls a VIKTOR-hosted helper service | Patch the documented function target with `unittest.mock`. |

## Params

For simple params, use `munch.munchify`:

```python
from munch import munchify

params = munchify({
    "width": 10,
    "height": 5,
    "material": "Concrete",
})
```

For raw params that contain VIKTOR-serialized values, use `viktor.testing.mock_params`:

```python
from viktor.testing import mock_params
from app import Parametrization

params = mock_params(
    {
        "calculation_date": "2026-05-13",
        "selected_entity": 42,
    },
    Parametrization,
    entities={
        42: MockedEntity(entity_id=42, name="Input entity"),
    },
)
```

`mock_params` is important for fields whose runtime value is not the raw JSON value. The documented deserialization targets are:

- `DateField`
- `EntityOptionField`
- `ChildEntityOptionField`
- `SiblingEntityOptionField`
- `EntityMultiSelectField`
- `ChildEntityMultiSelectField`
- `SiblingEntityMultiSelectField`
- `GeoPointField`
- `GeoPolylineField`
- `GeoPolygonField`
- `FileField`
- `MultiFileField`

Use fixture files for realistic saved params:

```python
import json
from pathlib import Path

from viktor.testing import mock_params
from app import Parametrization

raw = json.loads(Path("tests/params/design_case.json").read_text())
params = mock_params(raw, Parametrization)
```

## View And Button Tests

View tests should assert behavior, not just absence of exceptions. For smoke tests over many views, it is acceptable to assert that a valid VIKTOR view result is returned or that the method raises `vkt.UserError` for user-correctable invalid input.

Generic view smoke assertion:

```python
import viktor as vkt

result = controller.geometry_view(params=params)
self.assertIsInstance(result, vkt.views._ViewResult)
```

Specific assertions are better when the result type is known:

```python
result = controller.geometry_view(params=params)
self.assertIsInstance(result, vkt.GeometryResult)
self.assertGreater(len(result.geometry), 0)
```

For button methods, assert side effects through mocks:

```python
created = MockedEntity(entity_id=20, name="Created")

@mock_API(create_child_entity=created)
def test_button_creates_child(self):
    controller = Controller()
    controller.create_child(params=munchify({"name": "Created"}), entity_id=1)
```

## `test-views` Pattern

The `viktor-platform/test-views` repository is a local smoke-test pattern:

1. Import the app's `Controller` and `Parametrization`.
2. Parse the parametrization into strategies.
3. Generate many fake params with Hypothesis.
4. Find controller methods.
5. Call each method directly with generated params.
6. Pass if the method returns a VIKTOR view result or raises `vkt.UserError`.

Use this idea for broad view coverage, but adapt it to the app:

- Filter only actual view methods when the controller has helper methods.
- Add fixtures for required files, entity selections, or option callbacks.
- Use `mock_params` when generated raw params contain fields that need VIKTOR deserialization.
- Limit `max_examples` for slow geometry, worker, or API-heavy views.
- For tree apps, import the controller class for each entity type.

## `viktor.testing` Mock Objects

### `MockedEntity`

Use when code reads or mutates VIKTOR entities through `vkt.api_v1.API()` or entity objects.

Common constructor values:

```python
MockedEntity(
    entity_id=1,
    name="Design A",
    entity_type=MockedEntityType(name="Design"),
    last_saved_params=munchify({"width": 10}),
    last_saved_summary={"status": "ok"},
    get_file=vkt.File.from_data(b"file content"),
    parent=MockedEntity(entity_id=100, name="Parent"),
    children=[MockedEntity(entity_id=2, name="Child")],
    siblings=[MockedEntity(entity_id=3, name="Sibling")],
    revisions=[
        MockedEntityRevision(params=munchify({"width": 8})),
    ],
)
```

Important behavior:

- `.id`, `.name`, `.entity_type`, `.last_saved_params`, and `.last_saved_summary` return the configured values.
- `.parent()`, `.children()`, `.siblings()`, `.revisions()`, and `.get_file()` return configured related objects.
- `.create_child(entity_type_name, name, params=...)` returns a mocked child entity.
- `.rename(name)`, `.set_params(params)`, and `.delete()` simulate mutation methods.
- Set `invalid=True` when a test should simulate failing API calls.

### `MockedEntityList`

API methods that return multiple entities use a mocked list object. It behaves like a list for length checks, indexing, and iteration.

```python
entities = MockedEntityList([
    MockedEntity(entity_id=1, name="A"),
    MockedEntity(entity_id=2, name="B"),
])

self.assertEqual(len(entities), 2)
self.assertEqual(entities[0].name, "A")
```

### `MockedEntityRevision`

Use for revision history:

```python
revision = MockedEntityRevision(
    entity_revision_id=7,
    params=munchify({"width": 9}),
    created_date=datetime(2026, 5, 13),
)
```

### `MockedEntityType`

Use when code branches by entity type name:

```python
entity_type = MockedEntityType(name="Foundation")
entity = MockedEntity(entity_id=1, entity_type=entity_type)
```

### `MockedFileResource`

Use with `mock_params` for `FileField` and `MultiFileField`:

```python
file_resource = MockedFileResource(
    filename="input.csv",
    file=vkt.File.from_data(b"x,y\n1,2\n"),
)
```

### `MockedUser`

Use when code calls `api.get_current_user()`:

```python
user = MockedUser(
    user_id=4,
    first_name="Test",
    last_name="User",
    email="test@example.com",
)
```

## `mock_API`

Use `mock_API` when app code constructs `vkt.api_v1.API()` and calls API methods.

Supported return hooks include:

- `get_entity`
- `create_child_entity`
- `generate_upload_url`
- `get_current_user`
- `get_entities_by_type`
- `get_entity_children`
- `get_entity_siblings`
- `get_root_entities`
- `get_entity_parent`
- `get_entity_revisions`
- `get_entity_file`
- `rename_entity`
- `set_entity_params`

Return values can be:

- a single object, reused for every matching call
- a sequence, consumed one item per matching call
- `None`, which lets the mock provide a default object

Example:

```python
entity = MockedEntity(
    entity_id=1,
    name="Design A",
    children=[
        MockedEntity(entity_id=2, name="Child A"),
        MockedEntity(entity_id=3, name="Child B"),
    ],
)

@mock_API(get_entity=entity)
def test_reads_children(self):
    api_entity = vkt.api_v1.API().get_entity(1)
    self.assertEqual(len(api_entity.children()), 2)
```

## `mock_View`

Use `mock_View` to mock VIKTOR view decorators on a controller class so view methods can be called directly in tests.

```python
@mock_View(Controller)
def test_geometry_view(self):
    controller = Controller()
    result = controller.geometry_view(params=munchify({}))
    self.assertIsInstance(result, vkt.GeometryResult)
```

## `mock_ParamsFromFile`

Use `mock_ParamsFromFile` for tests around a method decorated with `@ParamsFromFile`. Pass the controller class on which the decorator should be mocked.

```python
@mock_ParamsFromFile(Controller)
def test_params_from_file(self):
    controller = Controller()
    result = controller.process_file(file=vkt.File.from_data(b"data"))
    self.assertIn("width", result)
```

## `mock_Storage`

Use `mock_Storage` when app code reads or writes VIKTOR storage.

```python
@mock_Storage(get=[vkt.File.from_data(b"cached")])
def test_reads_storage(self):
    controller = Controller()
    result = controller.download_cached_file(params=munchify({}))
    self.assertIsNotNone(result)
```

## External Worker Mock Decorators

Use these when tests call VIKTOR external analyses. The decorator name matches the integration class.

| Decorator | Integration type commonly mocked | Return controls |
| --- | --- | --- |
| `mock_AxisVMAnalysis` | `vkt.external.axisvm.AxisVMAnalysis` | `get_model_file`, `get_result_file`, `get_results` |
| `mock_DFoundationsAnalysis` | `vkt.external.dfoundations.DFoundationsAnalysis` | output files |
| `mock_DGeoStabilityAnalysis` | `vkt.external.dgeostability.DGeoStabilityAnalysis` | output files |
| `mock_DSettlementAnalysis` | `vkt.external.dsettlement.DSettlementAnalysis` | `get_output_file`, `get_sld_file` |
| `mock_DSheetPilingAnalysis` | `vkt.external.dsheetpiling.DSheetPilingAnalysis` | output files |
| `mock_DStabilityAnalysis` | `vkt.external.dstability.DStabilityAnalysis` | output files |
| `mock_DynamoAnalysis` | Dynamo worker analysis | output files |
| `mock_ETABSAnalysis` | `vkt.external.etabs.ETABSAnalysis` | output files |
| `mock_Excel` | `vkt.external.excel.Excel` | `get_named_cell_result`, `get_direct_cell_result`, `get_filled_template` |
| `mock_GenericAnalysis` | `vkt.external.generic.GenericAnalysis` | output files |
| `mock_GRLWeapAnalysis` | `vkt.external.grlweap.GRLWeapAnalysis` | output files |
| `mock_IdeaRcsAnalysis` | `vkt.external.idea_rcs.IdeaRcsAnalysis` | `get_output_file`, `get_idea_rcs_file` |
| `mock_MatlabAnalysis` | `vkt.external.matlab.MatlabAnalysis` | output files |
| `mock_PlaxisAnalysis` | `vkt.external.plaxis.PlaxisAnalysis` | output files |
| `mock_PythonAnalysis` | `vkt.external.python.PythonAnalysis` | output files |
| `mock_RFEMAnalysis` | `vkt.external.rfem.RFEMAnalysis` | `get_model`, `get_result` |
| `mock_RevitAnalysis` | `vkt.external.revit.RevitAnalysis` | output files |
| `mock_RobotAnalysis` | `vkt.external.robot.RobotAnalysis` | `get_model_file`, `get_results` |
| `mock_SAP2000Analysis` | `vkt.external.sap2000.SAP2000Analysis` | output files |
| `mock_SciaAnalysis` | `vkt.external.scia.SciaAnalysis` | `get_engineering_report`, `get_updated_esa_model`, `get_xml_output_file` |
| `mock_TeklaAnalysis` | `vkt.external.tekla.TeklaAnalysis` | output files |

Pattern:

```python
@mock_PythonAnalysis(get_output_file={
    "results.json": vkt.File.from_data(b'{"ok": true}'),
})
def test_worker_view(self):
    result = Controller().worker_view(params=munchify({}))
    self.assertIsNotNone(result)
```

Use realistic file names and extensions that match the production code, because app code often calls `analysis.get_output_file("some-name.ext")`.

## External Server Functions That Require Mocking

The following VIKTOR functions call external services and must be mocked outside app context:

- `viktor.external.dfoundations.BearingPilesModel.generate_input_file`
- `viktor.external.dfoundations.TensionPilesModel.generate_input_file`
- `viktor.external.dsettlement.Model1D.generate_input_file`
- `viktor.external.dsettlement.Model2D.generate_input_file`
- `viktor.external.idea_rcs.Model.generate_xml_input`
- `viktor.external.idea_rcs.OpenModel.generate_xml_input`
- `viktor.external.scia.Model.generate_xml_input`
- `viktor.external.spreadsheet.SpreadsheetCalculation.evaluate`
- `viktor.external.spreadsheet.SpreadsheetTemplate.render`
- `viktor.external.spreadsheet.render_spreadsheet`
- `viktor.external.word.WordFileTemplate.render`
- `viktor.external.word.render_word_file`
- `viktor.geo.GEFData.classify`
- `viktor.geo.GEFFile.parse`
- `viktor.utils.convert_excel_to_pdf`
- `viktor.utils.convert_svg_to_pdf`
- `viktor.utils.convert_word_to_pdf`
- `viktor.utils.merge_pdf_files`
- `viktor.utils.render_jinja_template`

Patch the import path used by the app code when possible. If the app does `from viktor.utils import convert_word_to_pdf`, patch `app.convert_word_to_pdf`. If it calls `vkt.utils.convert_word_to_pdf`, patch `viktor.utils.convert_word_to_pdf`.

## Common Pitfalls

- Do not use `entity.compute(...)` for local view tests.
- Do not pass raw serialized file/entity/date params directly into controller methods if production receives deserialized objects.
- Do not let external worker or service calls run in unit tests.
- Do not hide `vkt.UserError` failures when the input should be valid. Treat `UserError` as acceptable only for intentionally invalid or broad randomized inputs.
- Do not rely only on smoke tests. Add specific assertions around engineering calculations and generated output.
- Do not publish test fixtures unless the app needs them at runtime; exclude `tests/` in `.viktorignore` when appropriate.
