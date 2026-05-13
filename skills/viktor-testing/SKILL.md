---
name: viktor-testing
description: Use when the user explicitly wants to add, fix, run, or explain automated tests for a VIKTOR app, including `viktor-cli test`, unittest test layout, direct controller/view/button tests, Hypothesis view smoke tests, `viktor.testing` mocks, API/entity/file/user mocks, `ParamsFromFile`, deserialized params, external workers, external server calls, or failing VIKTOR test output. Do not use for every generic VIKTOR runtime error unless the user asks for tests/mocking or the error comes from a test run.
---

# VIKTOR Testing

Use this skill for automated testing and mocking in VIKTOR apps.

## Trigger Boundaries

- Use this skill when the work is about tests, test failures, `viktor-cli test`, mocked VIKTOR context, or mocked external calls.
- Use this skill when a runtime problem is being turned into a regression test.
- Do not use this skill for every normal app error. First debug generic runtime failures with the relevant app feature skill unless the user specifically asks for tests or the failure came from a test command.
- Do not confuse local tests with SDK entity computation. `entity.compute(...)` calls the platform API; VIKTOR tests usually import local Python code and call controller methods directly.

## Workflow

1. Load `../viktor-core/SKILL.md` first when the tests touch a VIKTOR controller, parametrization, view, button, or result.
2. Load `../viktor-cli-config/SKILL.md` when creating the test command, checking app config, or using `viktor-cli test`.
3. Put tests in a folder named `tests` and write them with Python `unittest` unless the existing app already uses another runner inside the CLI.
4. Prefer direct Python calls for local controller tests:
   - instantiate `Controller()`
   - build realistic `params`
   - call `controller.some_view(params=params)` or a button method directly
5. Use `viktor.testing.mock_params` for params containing deserialized VIKTOR objects such as file resources, entity selections, dates, and geo fields.
6. Use `mock_API`, `MockedEntity`, `MockedEntityRevision`, `MockedFileResource`, and `MockedUser` when app code calls `vkt.api_v1.API()`.
7. Use `mock_View`, `mock_ParamsFromFile`, `mock_Storage`, and the external analysis decorators when tests hit platform context, file parsing hooks, storage, workers, or VIKTOR-hosted services.
8. Patch the documented external-server functions before running tests that call spreadsheet, Word, GEF, PDF conversion, Jinja rendering, D-Foundations, D-Settlement, IDEA RCS, or SCIA helper functions.
9. Run `viktor-cli test` from the app root for the normal VIKTOR test path.

## Load When Needed

- Read [reference.md](reference.md) for the testing model, CLI behavior, mock catalog, and all external-server functions that require mocking.
- Read [examples.md](examples.md) for ready-to-adapt `unittest` files, controller view tests, `mock_API`, `mock_params`, `mock_ParamsFromFile`, external worker mocks, and external-server patch examples.
