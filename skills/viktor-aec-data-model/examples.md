# VIKTOR AEC Data Model Examples

## Autodesk File Selection

```python
import viktor as vkt


class Parametrization(vkt.Parametrization):
    autodesk_file = vkt.AutodeskFileField(
        "Select Autodesk model",
        oauth2_integration="aps-integration-viktor",
    )
```

## Access Token and Element Group ID

```python
class Controller(vkt.Controller):
    parametrization = Parametrization

    @vkt.TableView("Model data")
    def model_data(self, params, **kwargs):
        if not params.autodesk_file:
            raise vkt.UserError("Select an Autodesk model first.")

        integration = vkt.external.OAuth2Integration("aps-integration-viktor")
        token = integration.get_access_token()
        region = params.autodesk_file.get_region()
        element_group_id = params.autodesk_file.get_aec_data_model_element_group_id()

        rows = [[region, element_group_id, bool(token)]]
        return vkt.TableResult(rows, column_headers=["Region", "Element group", "Token available"])
```

## Query Pattern

Keep the HTTP helper separate from the view method. Send `query` and `variables` as JSON, include the `Region` header, and raise a clear error if GraphQL returns `errors`.
