# VIKTOR Testing Examples

## Minimal Calculation Test

Use plain unit tests for engineering logic that does not need VIKTOR context.

```python
# tests/test_calculations.py
import unittest

from app import bearing_pressure


class TestCalculations(unittest.TestCase):

    def test_bearing_pressure(self):
        self.assertAlmostEqual(
            bearing_pressure(force=1200, area=6),
            200,
        )
```

Run:

```bash
viktor-cli test
```

## Manual View Test

This calls the view function as local Python code.

```python
# tests/test_views.py
import unittest

import viktor as vkt
from munch import munchify

from app import Controller


class TestViews(unittest.TestCase):

    def test_geometry_view(self):
        controller = Controller()

        params = munchify({
            "width": 10,
            "height": 5,
            "length": 20,
        })

        result = controller.geometry_view(params=params)

        self.assertIsInstance(result, vkt.GeometryResult)
        self.assertGreater(len(result.geometry), 0)
```

## Manual View Smoke Test

Use this for broad coverage when the exact result type varies.

```python
# tests/test_view_smoke.py
import unittest

import viktor as vkt
from munch import munchify

from app import Controller


class TestViewSmoke(unittest.TestCase):

    def test_view_returns_viktor_result_or_user_error(self):
        controller = Controller()
        params = munchify({"width": 10, "height": 5})

        try:
            result = controller.geometry_view(params=params)
        except vkt.UserError:
            return

        self.assertIsInstance(result, vkt.views._ViewResult)
```

## Button Method With API Side Effect

```python
# tests/test_buttons.py
import unittest

from munch import munchify
from viktor.testing import MockedEntity, mock_API

from app import Controller


class TestButtons(unittest.TestCase):

    @mock_API(
        get_entity=MockedEntity(entity_id=1, name="Parent"),
        create_child_entity=MockedEntity(entity_id=2, name="Generated case"),
    )
    def test_create_child_button(self):
        controller = Controller()

        controller.create_child_case(
            params=munchify({"case_name": "Generated case"}),
            entity_id=1,
        )
```

## `mock_API` With Entity Navigation

```python
# tests/test_api_navigation.py
import unittest

from munch import munchify
from viktor.testing import MockedEntity, MockedEntityRevision, MockedEntityType, mock_API

from app import Controller


class TestApiNavigation(unittest.TestCase):

    @mock_API(
        get_entity=MockedEntity(
            entity_id=10,
            name="Design",
            entity_type=MockedEntityType(name="Foundation"),
            last_saved_params=munchify({"width": 12}),
            parent=MockedEntity(entity_id=1, name="Project"),
            children=[
                MockedEntity(entity_id=11, name="Load case A"),
                MockedEntity(entity_id=12, name="Load case B"),
            ],
            siblings=[
                MockedEntity(entity_id=13, name="Sibling design"),
            ],
            revisions=[
                MockedEntityRevision(params=munchify({"width": 10})),
                MockedEntityRevision(params=munchify({"width": 12})),
            ],
        )
    )
    def test_summary_reads_related_entities(self):
        controller = Controller()
        result = controller.summary(params=munchify({}), entity_id=10)

        self.assertIsNotNone(result)
```

## `mock_API` With Current User

```python
# tests/test_current_user.py
import unittest

from munch import munchify
from viktor.testing import MockedUser, mock_API

from app import Controller


class TestCurrentUser(unittest.TestCase):

    @mock_API(get_current_user=MockedUser(user_id=5, first_name="Ada", last_name="Lovelace", email="ada@example.com"))
    def test_user_specific_view(self):
        result = Controller().user_view(params=munchify({}))
        self.assertIsNotNone(result)
```

## `mock_params` For Entity And File Fields

Use this when raw params contain serialized VIKTOR references.

```python
# tests/test_deserialized_params.py
import unittest

import viktor as vkt
from viktor.testing import MockedEntity, MockedFileResource, mock_params

from app import Controller, Parametrization


class TestDeserializedParams(unittest.TestCase):

    def test_file_and_entity_params(self):
        params = mock_params(
            {
                "selected_entity": 42,
                "input_file": 7,
            },
            Parametrization,
            entities={
                42: MockedEntity(entity_id=42, name="Reference entity"),
            },
            file_resources={
                7: MockedFileResource(
                    filename="loads.csv",
                    file=vkt.File.from_data(b"load,value\nwind,12\n"),
                ),
            },
        )

        result = Controller().table_view(params=params)
        self.assertIsNotNone(result)
```

## `mock_params` From A Fixture File

```python
# tests/test_fixture_params.py
import json
import unittest
from pathlib import Path

from viktor.testing import mock_params

from app import Controller, Parametrization


class TestFixtureParams(unittest.TestCase):

    def test_saved_design_case(self):
        raw_params = json.loads(Path("tests/params/design_case.json").read_text())
        params = mock_params(raw_params, Parametrization)

        result = Controller().geometry_view(params=params)
        self.assertIsNotNone(result)
```

## `mock_ParamsFromFile`

```python
# tests/test_params_from_file.py
import unittest

import viktor as vkt
from viktor.testing import mock_ParamsFromFile

from app import Controller


class TestParamsFromFile(unittest.TestCase):

    @mock_ParamsFromFile(Controller)
    def test_process_upload(self):
        controller = Controller()

        params = controller.process_uploaded_file(
            file=vkt.File.from_data(b"fake spreadsheet bytes"),
        )

        self.assertIn("width", params)
```

## `mock_View`

```python
# tests/test_mock_view.py
import unittest

import viktor as vkt
from munch import munchify
from viktor.testing import mock_View

from app import Controller


class TestMockView(unittest.TestCase):

    @mock_View(Controller)
    def test_geometry_view(self):
        result = Controller().geometry_view(params=munchify({"width": 10}))
        self.assertIsInstance(result, vkt.GeometryResult)
```

## `mock_Storage`

```python
# tests/test_storage.py
import unittest

import viktor as vkt
from munch import munchify
from viktor.testing import mock_Storage

from app import Controller


class TestStorage(unittest.TestCase):

    @mock_Storage(get=[vkt.File.from_data(b"cached data")])
    def test_download_cached_file(self):
        result = Controller().download_cached_file(params=munchify({}))
        self.assertIsNotNone(result)
```

## External Worker Mock: PythonAnalysis

```python
# tests/test_python_worker.py
import unittest

import viktor as vkt
from munch import munchify
from viktor.testing import mock_PythonAnalysis

from app import Controller


class TestPythonWorker(unittest.TestCase):

    @mock_PythonAnalysis(get_output_file={
        "results.json": vkt.File.from_data(b'{"utilization": 0.82}'),
    })
    def test_worker_result_view(self):
        result = Controller().worker_result_view(params=munchify({}))
        self.assertIsNotNone(result)
```

## External Worker Mock: ETABSAnalysis

```python
# tests/test_etabs_worker.py
import unittest

import viktor as vkt
from munch import munchify
from viktor.testing import mock_ETABSAnalysis

from app import Controller


class TestEtabsWorker(unittest.TestCase):

    @mock_ETABSAnalysis(get_output_file={
        "base_reactions.csv": vkt.File.from_data(b"case,Fx,Fy,Fz\nEQX,1,2,3\n"),
    })
    def test_etabs_view(self):
        result = Controller().base_reactions_view(params=munchify({}))
        self.assertIsNotNone(result)
```

## External Worker Mock Catalog

Use the exact decorator for the integration used by the app. The output file names should match the production code.

```python
# tests/test_worker_catalog.py
import unittest

import viktor as vkt
from munch import munchify
from viktor.testing import (
    mock_AxisVMAnalysis,
    mock_DFoundationsAnalysis,
    mock_DGeoStabilityAnalysis,
    mock_DSettlementAnalysis,
    mock_DSheetPilingAnalysis,
    mock_DStabilityAnalysis,
    mock_DynamoAnalysis,
    mock_Excel,
    mock_GenericAnalysis,
    mock_GRLWeapAnalysis,
    mock_IdeaRcsAnalysis,
    mock_MatlabAnalysis,
    mock_PlaxisAnalysis,
    mock_RFEMAnalysis,
    mock_RevitAnalysis,
    mock_RobotAnalysis,
    mock_SAP2000Analysis,
    mock_SciaAnalysis,
    mock_TeklaAnalysis,
)

from app import Controller


class TestWorkerCatalog(unittest.TestCase):

    @mock_AxisVMAnalysis(
        get_model_file=vkt.File.from_data(b"axisvm model"),
        get_result_file=vkt.File.from_data(b"axisvm result file"),
        get_results={"forces": {"beam_1": 12.3}},
    )
    def test_axisvm(self):
        self.assertIsNotNone(Controller().axisvm_view(params=munchify({})))

    @mock_DFoundationsAnalysis(get_output_file={"dfoundations.out": vkt.File.from_data(b"dfoundations")})
    def test_dfoundations(self):
        self.assertIsNotNone(Controller().dfoundations_view(params=munchify({})))

    @mock_DGeoStabilityAnalysis(get_output_file={"dgeostability.out": vkt.File.from_data(b"dgeostability")})
    def test_dgeostability(self):
        self.assertIsNotNone(Controller().dgeostability_view(params=munchify({})))

    @mock_DSettlementAnalysis(
        get_output_file={".slo": vkt.File.from_data(b"dsettlement output")},
        get_sld_file=vkt.File.from_data(b"dsettlement sld"),
    )
    def test_dsettlement(self):
        self.assertIsNotNone(Controller().dsettlement_view(params=munchify({})))

    @mock_DSheetPilingAnalysis(get_output_file={"dsheetpiling.out": vkt.File.from_data(b"dsheetpiling")})
    def test_dsheetpiling(self):
        self.assertIsNotNone(Controller().dsheetpiling_view(params=munchify({})))

    @mock_DStabilityAnalysis(get_output_file={"dstability.out": vkt.File.from_data(b"dstability")})
    def test_dstability(self):
        self.assertIsNotNone(Controller().dstability_view(params=munchify({})))

    @mock_DynamoAnalysis(get_output_file={"dynamo.json": vkt.File.from_data(b"{}")})
    def test_dynamo(self):
        self.assertIsNotNone(Controller().dynamo_view(params=munchify({})))

    @mock_Excel(
        get_filled_template=vkt.File.from_data(b"excel bytes"),
        get_named_cell_result={"utilization": 0.82},
        get_direct_cell_result={("Sheet1", "A", 1): "ok"},
    )
    def test_excel_worker(self):
        self.assertIsNotNone(Controller().excel_worker_view(params=munchify({})))

    @mock_GenericAnalysis(get_output_file={"result.txt": vkt.File.from_data(b"generic")})
    def test_generic(self):
        self.assertIsNotNone(Controller().generic_worker_view(params=munchify({})))

    @mock_GRLWeapAnalysis(get_output_file=vkt.File.from_data(b"grlweap"))
    def test_grlweap(self):
        self.assertIsNotNone(Controller().grlweap_view(params=munchify({})))

    @mock_IdeaRcsAnalysis(
        get_output_file=vkt.File.from_data(b"<result />"),
        get_idea_rcs_file=vkt.File.from_data(b"idea rcs"),
    )
    def test_idea_rcs(self):
        self.assertIsNotNone(Controller().idea_rcs_view(params=munchify({})))

    @mock_MatlabAnalysis(get_output_file={"matlab.mat": vkt.File.from_data(b"matlab")})
    def test_matlab(self):
        self.assertIsNotNone(Controller().matlab_view(params=munchify({})))

    @mock_PlaxisAnalysis(get_output_file={"plaxis.out": vkt.File.from_data(b"plaxis")})
    def test_plaxis(self):
        self.assertIsNotNone(Controller().plaxis_view(params=munchify({})))

    @mock_RFEMAnalysis(
        get_model=vkt.File.from_data(b"rfem model"),
        get_result={1: vkt.File.from_data(b"rfem result")},
    )
    def test_rfem(self):
        self.assertIsNotNone(Controller().rfem_view(params=munchify({})))

    @mock_RevitAnalysis(get_output_file={"model.ifc": vkt.File.from_data(b"ifc")})
    def test_revit(self):
        self.assertIsNotNone(Controller().revit_view(params=munchify({})))

    @mock_RobotAnalysis(
        get_model_file=vkt.File.from_data(b"robot model"),
        get_results={"bar_forces": {"bar_1": 10.0}},
    )
    def test_robot(self):
        self.assertIsNotNone(Controller().robot_view(params=munchify({})))

    @mock_SAP2000Analysis(get_output_file={"sap2000.csv": vkt.File.from_data(b"sap2000")})
    def test_sap2000(self):
        self.assertIsNotNone(Controller().sap2000_view(params=munchify({})))

    @mock_SciaAnalysis(
        get_engineering_report=vkt.File.from_data(b"pdf report"),
        get_updated_esa_model=vkt.File.from_data(b"esa model"),
        get_xml_output_file=vkt.File.from_data(b"<scia />"),
    )
    def test_scia(self):
        self.assertIsNotNone(Controller().scia_view(params=munchify({})))

    @mock_TeklaAnalysis(get_output_file={"tekla.ifc": vkt.File.from_data(b"tekla")})
    def test_tekla(self):
        self.assertIsNotNone(Controller().tekla_view(params=munchify({})))
```

## External Server Function Patches

Patch the exact path that the app uses. The examples below patch the VIKTOR module path.

```python
# tests/test_external_services.py
import unittest
from unittest import mock

import viktor as vkt
from munch import munchify

from app import Controller


class TestExternalServices(unittest.TestCase):

    @mock.patch(
        "viktor.external.spreadsheet.SpreadsheetCalculation.evaluate",
        return_value={"Sheet1!A1": 42},
    )
    def test_spreadsheet_calculation(self, _evaluate):
        result = Controller().spreadsheet_view(params=munchify({}))
        self.assertIsNotNone(result)

    @mock.patch(
        "viktor.external.spreadsheet.SpreadsheetTemplate.render",
        return_value=vkt.File.from_data(b"xlsx bytes"),
    )
    def test_spreadsheet_template(self, _render):
        result = Controller().download_spreadsheet(params=munchify({}))
        self.assertIsNotNone(result)

    @mock.patch(
        "viktor.external.spreadsheet.render_spreadsheet",
        return_value=vkt.File.from_data(b"xlsx bytes"),
    )
    def test_render_spreadsheet_function(self, _render):
        result = Controller().download_rendered_spreadsheet(params=munchify({}))
        self.assertIsNotNone(result)

    @mock.patch(
        "viktor.external.word.WordFileTemplate.render",
        return_value=vkt.File.from_data(b"docx bytes"),
    )
    def test_word_template(self, _render):
        result = Controller().download_word_report(params=munchify({}))
        self.assertIsNotNone(result)

    @mock.patch(
        "viktor.external.word.render_word_file",
        return_value=vkt.File.from_data(b"docx bytes"),
    )
    def test_render_word_file_function(self, _render):
        result = Controller().download_word_file(params=munchify({}))
        self.assertIsNotNone(result)
```

## Full External Server Patch List

Use this as a checklist. Replace the return values with whatever the app expects.

```python
from unittest import mock

import viktor as vkt


patches = [
    mock.patch("viktor.external.dfoundations.BearingPilesModel.generate_input_file", return_value=vkt.File.from_data(b"bearing piles input")),
    mock.patch("viktor.external.dfoundations.TensionPilesModel.generate_input_file", return_value=vkt.File.from_data(b"tension piles input")),
    mock.patch("viktor.external.dsettlement.Model1D.generate_input_file", return_value=vkt.File.from_data(b"model 1d input")),
    mock.patch("viktor.external.dsettlement.Model2D.generate_input_file", return_value=vkt.File.from_data(b"model 2d input")),
    mock.patch("viktor.external.idea_rcs.Model.generate_xml_input", return_value="<idea-model />"),
    mock.patch("viktor.external.idea_rcs.OpenModel.generate_xml_input", return_value="<idea-open-model />"),
    mock.patch("viktor.external.scia.Model.generate_xml_input", return_value="<scia-model />"),
    mock.patch("viktor.external.spreadsheet.SpreadsheetCalculation.evaluate", return_value={}),
    mock.patch("viktor.external.spreadsheet.SpreadsheetTemplate.render", return_value=vkt.File.from_data(b"xlsx")),
    mock.patch("viktor.external.spreadsheet.render_spreadsheet", return_value=vkt.File.from_data(b"xlsx")),
    mock.patch("viktor.external.word.WordFileTemplate.render", return_value=vkt.File.from_data(b"docx")),
    mock.patch("viktor.external.word.render_word_file", return_value=vkt.File.from_data(b"docx")),
    mock.patch("viktor.geo.GEFData.classify", return_value={}),
    mock.patch("viktor.geo.GEFFile.parse", return_value={}),
    mock.patch("viktor.utils.convert_excel_to_pdf", return_value=vkt.File.from_data(b"pdf")),
    mock.patch("viktor.utils.convert_svg_to_pdf", return_value=vkt.File.from_data(b"pdf")),
    mock.patch("viktor.utils.convert_word_to_pdf", return_value=vkt.File.from_data(b"pdf")),
    mock.patch("viktor.utils.merge_pdf_files", return_value=vkt.File.from_data(b"pdf")),
    mock.patch("viktor.utils.render_jinja_template", return_value="rendered text"),
]
```

Context manager pattern:

```python
class TestEverythingMocked(unittest.TestCase):

    def test_report_generation(self):
        active = [patch.start() for patch in patches]
        self.addCleanup(lambda: [patch.stop() for patch in patches])

        result = Controller().report_view(params=munchify({}))
        self.assertIsNotNone(result)
```

## Hypothesis View Smoke Test

This is a simplified version of the `test-views` idea. Keep it small and adapt field handling to the app.

```python
# tests/test_hypothesis_views.py
import inspect
import unittest

import viktor as vkt
from hypothesis import given, settings
from hypothesis import strategies as st
from munch import munchify

from app import Controller


def params_strategy():
    return st.fixed_dictionaries({
        "width": st.floats(min_value=0.1, max_value=50, allow_nan=False, allow_infinity=False),
        "height": st.floats(min_value=0.1, max_value=50, allow_nan=False, allow_infinity=False),
        "length": st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False),
    }).map(munchify)


class TestGeneratedViewInputs(unittest.TestCase):

    def setUp(self):
        self.controller = Controller()

    @given(params_strategy())
    @settings(deadline=None, max_examples=25)
    def test_geometry_view_handles_generated_params(self, params):
        try:
            result = self.controller.geometry_view(params=params)
        except vkt.UserError:
            return

        self.assertIsInstance(result, vkt.views._ViewResult)

    def test_expected_view_methods_exist(self):
        methods = {
            name
            for name, _method in inspect.getmembers(self.controller, predicate=inspect.ismethod)
        }

        self.assertIn("geometry_view", methods)
```

Add `hypothesis` to `requirements.txt` if the test suite depends on it:

```text
hypothesis==6.103.1
```

## `.viktorignore` For Tests

Exclude tests from published app bundles unless they are intentionally required at runtime.

```text
tests/
test_*.py
*_test.py
```
