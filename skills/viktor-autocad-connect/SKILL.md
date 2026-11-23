---
name: viktor-autocad-connect
description: Build or debug VIKTOR apps that read or draw in AutoCAD with vkt.autocad.connect() or attach() through a personal worker and the AutoCAD ActiveX API.
---

# VIKTOR AutoCAD Connect

Use the direct ActiveX integration for AutoCAD drawings, including footing, beam, and reinforcement details. Read [reference.md](reference.md) for API limits and [examples.md](examples.md) for drawing and error-handling patterns.

1. Add `worker_integrations = ["autocad"]` to `viktor.config.toml` and use VIKTOR SDK 14.35.0 or later. The API is beta.
2. Start the AutoCAD personal worker in VIKTOR Desktop on the licensed AutoCAD machine. Use an interactive Windows session, with AutoCAD and the worker under the same user. Clear modal dialogs.
3. Use `vkt.autocad.attach()` to edit the open drawing; use `connect()` for a new session. An attach failure does not start a new drawing. `connect()` is refused if AutoCAD is already open on the worker.
4. Validate dimensions and units before writing. Attached changes affect the live drawing and are not automatically rolled back; use a copy and recognizable layer prefixes. After failure, inspect the drawing before retrying.
5. Navigate from `acad.ActiveDocument.ModelSpace`. Read scalar properties with call syntax, such as `line.Length()`, and write them by assignment, such as `line.Layer = "STRUCTURE"`.
6. Use an ActionButton to draw. Read needed values inside the session. The current integration cannot return a DWG; the user saves an attached drawing in AutoCAD.
7. Reduce worker round trips with polylines and other bulk operations; regenerate once at the end. Mock sessions with `vkt.testing.mock_AutoCADConnection` and verify live behavior on a personal worker when available.
