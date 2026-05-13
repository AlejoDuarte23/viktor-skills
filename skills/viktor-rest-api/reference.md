# VIKTOR REST API Reference

Sources:

- https://docs.viktor.ai/docs/api/
- https://docs.viktor.ai/docs/api/rest/viktor-api/
- https://docs.viktor.ai/docs/api/rest/workspaces-list/
- https://github.com/AlejoDuarte23/viktor-mcp-template/blob/draft/build-mcp-footing-tools/src/viktor_mcp_server/viktor_api.py

## When to use REST

The REST API is VIKTOR's low-level HTTP interface for platform data exchange and automation. It is language-agnostic. If the task is in Python and the SDK API supports the operation, prefer the SDK API because it handles platform-specific details for you.

## Authentication

REST API calls require a Personal Access Token. The token grants the same rights as its owner, so never hard-code it or print it. Store it in an environment variable or another secret store.

Use the token in the `Authorization` header:

```text
Authorization: Bearer <TOKEN>
```

Common environment variable names:

- `TOKEN_VK_APP`: used by app-adjacent tooling in the source helper.
- `VIKTOR_TOKEN`: useful for standalone scripts.

Strip whitespace and fail fast if the value is empty.

## Base URL handling

Build the API base from either a full API URL or an environment slug:

```text
https://<environment>.viktor.ai/api/workspaces/
```

Recommended behavior:

- Accept `VIKTOR_API_BASE` when callers already know the full base, for example `https://cloud.viktor.ai/api`.
- Accept `VIKTOR_ENVIRONMENT` when callers provide the VIKTOR environment, for example `cloud`, `cloud.us1`, `my-company`, `my-company.viktor.ai`, or `https://my-company.viktor.ai`.
- Strip trailing slashes.
- Ensure the normalized API base is an absolute HTTPS URL and ends in `/api`.
- Derive UI URLs by removing the trailing `/api` from the API base.

Example editor URL pattern:

```text
https://<environment>.viktor.ai/workspaces/<workspace_id>/app/editor/<entity_id>
```

## Client/helper shape

Use a small helper class for non-trivial scripts and tools:

- Keep `api_base`, `token`, `connect_timeout`, `read_timeout`, and auth headers on the client.
- Use `timeout=(connect_timeout, read_timeout)` with `requests`.
- Keep separate header helpers for auth-only requests and JSON body requests.
- Put all response checking in one `_request_json` or `_raise_for_status` helper.
- Use typed models for response shapes that the rest of the code depends on. The source helper uses Pydantic v2 `BaseModel` and `model_validate`.
- Allow extra keys in dynamic result payloads because VIKTOR result types can vary by app method.

## Request and error handling

Preferred request behavior:

- Pass query parameters through `params=...`.
- Pass JSON request bodies through `json=...`.
- Call the API only after all required IDs and method names are known.
- Truncate response-body snippets in exceptions, for example to 500 characters.
- Do not include request headers in exception messages because they contain the bearer token.

Common response meanings:

- `400`: validation error. Surface field messages or `non_field_errors` when present.
- `401`: missing, malformed, expired, or unauthorized token.
- `403`: permission failure or operation not allowed for this caller.
- `404`: missing resource. For optional parent lookups, returning `None` can be better than raising.
- `429`: rate limiting. Retry only if the workflow is idempotent and the API provides a safe retry signal.
- `5xx`: VIKTOR or upstream service failure. Report the status and a short body snippet.

## Pagination

Paginated endpoints use:

- `count`: total number of objects in the result set.
- `next`: URL for the next page, if available.
- `previous`: URL for the previous page, if available.
- `results`: array of objects.

Follow `next` until it is empty. When using the returned `next` URL, do not resend the original `params`; the URL already contains the pagination query. For repeated filters such as `visibility`, `app`, and `label`, pass Python lists through the HTTP client instead of manually encoding repeated query keys.

## Workspace operations

Endpoint:

```text
GET /api/workspaces/
```

Purpose: list workspaces for the current user, depending on that user's role and access.

Workspace query parameters:

- `limit` (`integer`): number of results per page.
- `offset` (`integer`): initial result index.
- `detail_level` (`string`): `minimal`, `basic`, or `full`; default is `full`.
- `include_development` (`boolean`): include individual development workspaces; requires org admin permission.
- `include_archived` (`boolean`): include archived workspaces; requires org admin permission.
- `visibility` (`string[]`): filter by `INTERNAL`, `PRIVATE`, `DEVELOPMENT`, or `PUBLIC`.
- `is_dev` (`boolean`): fetch only development workspaces when `true`.
- `archived` (`boolean`): fetch only archived workspaces when `true`.
- `app` (`integer[]`): filter by app ID.
- `label` (`integer[]`): filter by label ID.
- `project` (`integer`): filter by project ID; value must be at least `1`.
- `sort` (`string`): one of `name`, `created_at`, `views`, `views_last_30_days`, or `user_last_visit`, optionally suffixed with `:asc` or `:desc`.
- `search` (`string`): non-empty fuzzy match against name or description.

Workspace object fields commonly include:

- Identity and metadata: `id`, `name`, `slug`, `description`, `created_at`, `updated_at`.
- Classification: `visibility`, `type`, `is_dev`, `is_archived`, `is_active`, `is_initialized`.
- App/version details: `app`, `app_builder`, `app_version`, `errors`, `image`.
- Organization context: `owner`, `labels`, `project`, `default_group`, `start_entity_id`.
- Usage and targets: `user_last_visit`, `nr_views`, `nr_views_last_30_days`, `target_total_users`, `target_monthly_active_users`, `target_daily_active_users_per_month`.

Use `detail_level` to reduce response payloads when full nested objects are not needed.

## Entity operations

The source helper uses these entity endpoints:

- `GET /api/workspaces/{workspace_id}/entities/{entity_id}/`
  - Query flags: `properties`, `clean_params`, `param_types`.
  - Encode booleans as lowercase strings: `true` or `false`.
- `GET /api/workspaces/{workspace_id}/entities/{entity_id}/parent/`
  - Return `None` for `404`.
  - The source helper also treats a `403` mentioning tree access as no parent available.
- `POST /api/workspaces/{workspace_id}/entities/`
  - Body: `entity_type`, `name`, `properties`.
- `POST /api/workspaces/{workspace_id}/entities/{parent_entity_id}/entities/`
  - Body: `entity_type`, `name`, `properties`.
  - Some responses may be a list; validate it is non-empty before using the first entity.
- `PUT /api/workspaces/{workspace_id}/entities/{entity_id}/`
  - Body: `name`, `properties`, `message`.
  - Include a clear audit message because this mutates workspace data.
- `POST /api/workspaces/{workspace_id}/entities/{entity_id}/session/`
  - Returns an `editor_session` UUID that can be used by job calls that need an editor context.

Common entity response fields:

- `id`
- `name`
- `properties`
- `entity_type`
- `entity_type_name`
- `parent_count`
- `path`

## Job operations

The source helper models VIKTOR method execution as a job created under an entity.

Create job endpoint:

```text
POST /api/workspaces/{workspace_id}/entities/{entity_id}/jobs/
```

Request body:

- `method_name` (`string`, required): app method to call.
- `params` (`object`, optional): method parameters.
- `poll_result` (`boolean`): set to `false` when the client will poll the returned job URL.
- `method_type` (`string`, optional).
- `editor_session` (`UUID`, optional).
- `events` (`string[]`, optional).
- `timeout` (`integer`, optional): source helper validates `1` to `86400` seconds.

Create job response handling:

- If the response has `url`, poll it with `GET`.
- If it has immediate `status == "success"` and `content`, validate the content as the result payload.
- Otherwise, raise an unexpected-response error with the sanitized response object.

Job statuses in the source helper:

```text
success, cancelled, failed, running, error, error_user,
error_app_reloading, error_timeout, expired, stopped, message
```

Treat these as failed states for normal automation:

```text
failed, cancelled, error, error_user, error_timeout
```

Polling pattern:

- Use a monotonic deadline, not wall-clock time.
- Start around `0.8` seconds between polls.
- Increase by a small multiplier, for example `1.5`.
- Cap sleep at about `5` seconds.
- Stop after `max_poll_seconds` and raise `TimeoutError`.

Result payload keys vary by app method. The source helper permits:

```text
web, ifc, pdf, geojson, data, image, plotly, geometry,
table, download, optimization, set_params
```

When `result.download.url` exists, fetch it separately. Use `response.json()` for JSON artifacts and `response.text` for HTML/text artifacts.

## Implementation notes

- Ask for the environment host and required permission level when they are not known.
- Ask before writing to entities if the user has not explicitly requested mutation.
- Prefer typed helpers when later code depends on fields such as `id`, `properties`, job `status`, or `download.url`.
- Keep examples safe: list/read operations can run directly; create/update examples should require explicit IDs and properties from the user.
