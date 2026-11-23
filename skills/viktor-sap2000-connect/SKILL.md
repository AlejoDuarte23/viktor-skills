---
name: viktor-sap2000-connect
description: Use when a VIKTOR app drives SAP2000 directly with `vkt.sap2000.connect()` or `vkt.sap2000.attach()` through a `sap2000connect` worker. Covers concise OAPI session and call patterns, not Python scripts or comtypes automation.
---

# VIKTOR SAP2000 Connect

Prefer this skill for new SAP2000 integrations. Use `../viktor-sap2000-worker/SKILL.md` for an existing or explicitly requested worker-side Python script.

## Setup

- Declare `worker_integrations = ["sap2000connect"]` in `viktor.config.toml`.
- Use VIKTOR SDK 14.32.0 or later; `attach()` needs 14.33.0 or later.
- The connected Windows worker needs SAP2000 installed and ready for interactive use.
- Use a logged-in Windows session with an activated licence. Start the personal worker in VIKTOR Desktop and inspect its logs there. No Python environment is needed on the worker for direct calls.

## Session choice

- `vkt.sap2000.connect()` starts a fresh SAP2000 model for the session.
- `vkt.sap2000.attach()` binds to the SAP2000 model already open on the worker.
- Use a `with` block and read the data needed by the VIKTOR view before it closes.
- Keep one SAP2000 instance open for `attach()`; it does not select between multiple instances or fall back to a new one. Never initialize or clear an attached model without an explicit requirement.
- Live edits can remain after a failure. Read the results before the session ends; session files cannot currently be returned to the app. The engineer saves their attached model.

## OAPI calls

- `sap` is the SAP2000 model: call paths look like `sap.FrameObj.AddByCoord(...)`.
- Use the SDK enums, such as `vkt.sap2000.eUnits.kN_m_C`.
- Check every CSI status code and use the return shape documented by the CSI signature.
- Use `vkt.testing.mock_SAP2000Connection` for both session modes. Verify the actual model and worker behavior separately when available.

## Load when needed

- Read [reference.md](reference.md) for configuration, session, and VB6-signature rules.
- Read [examples.md](examples.md) for compact `connect()` and `attach()` blocks.
