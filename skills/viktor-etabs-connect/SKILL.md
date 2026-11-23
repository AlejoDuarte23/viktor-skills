---
name: viktor-etabs-connect
description: Build or migrate a VIKTOR ETABS integration to direct OAPI calls with vkt.etabs.connect() or attach(), including migration from ETABSAnalysis and comtypes worker scripts.
---

# VIKTOR ETABS Connect

Prefer this skill for new ETABS integrations. Use `../viktor-etabs-worker/SKILL.md` for an existing or explicitly requested worker-side Python script.

## Setup

- Declare `worker_integrations = ["etabsconnect"]` in `viktor.config.toml`.
- Use VIKTOR SDK 14.31.0 or later; `attach()` needs 14.33.0 or later.
- The connected Windows worker needs ETABS installed and ready for interactive use.
- Use a logged-in Windows session with an activated licence. Start the personal worker in VIKTOR Desktop and inspect its logs there. No Python environment is needed on the worker for direct calls.

## Session choice

- `vkt.etabs.connect()` starts a fresh ETABS model for the session.
- `vkt.etabs.attach()` binds to the ETABS model already open on the worker.
- Use a `with` block and read the data needed by the VIKTOR view before it closes.
- Keep one ETABS instance open for `attach()`; it does not select between multiple instances or fall back to a new one. Never initialize or clear an attached model without an explicit requirement.
- Live edits can remain after a failure. Read the results before the session ends; session files cannot currently be returned to the app. The engineer saves their attached model.

## OAPI calls

- `sap` is the ETABS model: call paths look like `sap.FrameObj.AddByCoord(...)`.
- Use the SDK enums, such as `vkt.etabs.eUnits.kN_m_C`.
- Check every CSI status code and use the return shape documented by the CSI signature.
- Use `vkt.testing.mock_ETABSConnection` for both session modes. Verify the actual model and worker behavior separately when available.

## Load when needed

- Read [reference.md](reference.md) for configuration, session, and C#-signature rules.
- Read [examples.md](examples.md) for compact `connect()` and `attach()` blocks.
- Read [migration.md](migration.md) when replacing an `ETABSAnalysis` and `comtypes` worker script with direct sessions.
