# AutoCAD Connect Reference

Source: <https://docs.viktor.ai/docs/create-apps/software-integrations/autocad/>

## Setup and sessions

```toml
worker_integrations = ["autocad"]
```

Use `viktor>=14.35.0` and a licensed interactive Windows desktop. Start a personal AutoCAD worker in VIKTOR Desktop; it does not need a Python environment. Inspect its logs in VIKTOR Desktop. Use `connect()` for a new instance and `attach()` for the drawing already open on the worker. Keep the correct drawing open and avoid dialogs. Do not fall back from attach to connect without an explicit choice.

Attached changes remain in the live drawing when the context closes. They are not rolled back. Give generated geometry distinctive layer names, make units explicit, and ask the user to save the drawing. A failure may leave partial geometry.

## ActiveX rules

- Navigate down from `acad`; keep the document reference instead of using blocked `Application`, `Document`, or `Parent` back-references.
- A value read uses parentheses; a property assignment does not. Objects returned by methods are session-scoped handles.
- Each call or property access that reads or writes a value is a worker round trip. Prefer polylines, block copies, or bulk operations to per-entity loops. The session has about 65,000 handles.
- `Save`, `Close`, `Quit`, `SendCommand`, macros, interactive prompts, and other restricted members are refused. `SaveAs` accepts a relative session filename, but the session directory is temporary and cannot return a drawing to the app. Use `attach()` when the user must keep the drawn output.
- Catch `vkt.errors.WorkerSessionAttachError` before `vkt.errors.WorkerSessionError`; its reason may identify no instance or a busy instance. Handle unknown reasons and partial edits.
- The AutoCAD ActiveX reference defines method signatures; VIKTOR enums are under `vkt.autocad`.

## Testing

`vkt.testing.mock_AutoCADConnection` supports both connect and attach. Map paths to expected values or handles, and check behavior without changing a real drawing. A live worker check is still needed to verify drawing behavior and AutoCAD version details.
