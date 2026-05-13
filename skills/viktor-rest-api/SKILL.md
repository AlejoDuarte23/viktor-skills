---
name: viktor-rest-api
description: Use when the user needs code or guidance for calling the VIKTOR REST API directly, including base URL setup, Personal Access Token handling, workspace/entity/job operations, pagination, and small typed Python REST clients.
---

# VIKTOR REST API

Use this skill when direct HTTP calls to VIKTOR are needed. Prefer `../viktor-sdk-api/SKILL.md` when the Python SDK covers the same operation.

## Workflow

1. Confirm the VIKTOR host, token source, endpoint, operation type, and required permissions.
2. Normalize the base URL once. Accept either a full API base such as `https://cloud.viktor.ai/api` or an environment slug such as `cloud` or `cloud.us1`.
3. Read the token from an environment variable or secret store. Common names are `TOKEN_VK_APP` in app-adjacent tooling and `VIKTOR_TOKEN` in standalone scripts. Strip whitespace, reject empty values, and never log the token.
4. Use a small client/helper instead of repeating raw `requests` calls. Centralize headers, timeouts, JSON parsing, error messages, pagination, and polling.
5. Send query parameters with the HTTP client and request bodies through `json=...`; do not concatenate query strings by hand.
6. For list endpoints, handle the paginated shape: `count`, `next`, `previous`, and `results`.
7. For long-running entity method calls, create the job, poll the returned job URL with a bounded timeout/backoff, then read `result.download.url` when the result is a downloadable artifact.
8. Raise clear errors for validation, authentication, permission, missing-resource, and remote-service failures. Redact secrets and cap response-body snippets.

## Load When Needed

- Read [reference.md](reference.md) for base URL/token conventions, helper design, endpoint shapes, pagination, entity operations, job polling, and error handling.
- Read [examples.md](examples.md) for safe Python `requests` and Pydantic patterns that can be copied into scripts or MCP-style tools.
