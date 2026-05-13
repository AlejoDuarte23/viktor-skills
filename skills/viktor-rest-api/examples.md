# VIKTOR REST API Examples

## Minimal environment handling

```python
import os


def get_token() -> str:
    token = os.environ.get("TOKEN_VK_APP") or os.environ.get("VIKTOR_TOKEN")
    if not token or not token.strip():
        raise ValueError("Missing VIKTOR token. Set TOKEN_VK_APP or VIKTOR_TOKEN.")
    return token.strip()


def get_api_base() -> str:
    api_base = os.environ.get("VIKTOR_API_BASE")
    if api_base:
        base = api_base.strip().rstrip("/")
        return base if base.endswith("/api") else f"{base}/api"

    environment = os.environ.get("VIKTOR_ENVIRONMENT", "cloud").strip().rstrip("/")
    if not environment:
        raise ValueError("Missing VIKTOR_ENVIRONMENT.")
    if environment.startswith("http"):
        base = environment
    elif environment.endswith(".viktor.ai"):
        base = f"https://{environment}"
    else:
        base = f"https://{environment}.viktor.ai"
    return base if base.endswith("/api") else f"{base}/api"
```

## Small typed REST client

```python
import time
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

import requests
from pydantic import BaseModel, Field


JobStatus = Literal[
    "success",
    "cancelled",
    "failed",
    "running",
    "error",
    "error_user",
    "error_app_reloading",
    "error_timeout",
    "expired",
    "stopped",
    "message",
]


class EntityResponse(BaseModel):
    id: int
    name: str
    properties: dict[str, Any] | None = None
    entity_type: int
    entity_type_name: str | None = None
    parent_count: int = 0
    path: list[int] = Field(default_factory=list)


class EditorSessionResponse(BaseModel):
    editor_session: UUID


class DownloadResult(BaseModel):
    url: str


class JobResultPayload(BaseModel):
    model_config = {"extra": "allow"}

    download: DownloadResult | None = None
    data: dict[str, Any] | None = None
    geometry: dict[str, Any] | None = None
    table: dict[str, Any] | None = None
    web: dict[str, Any] | None = None

    @property
    def download_url(self) -> str | None:
        return self.download.url if self.download else None


class JobStatusResponse(BaseModel):
    uid: int
    kind: str
    status: JobStatus
    completed_at: datetime | None = None
    result: JobResultPayload | None = None
    error: dict[str, Any] | None = None
    log_download_url: str | None = None

    def is_success(self) -> bool:
        return self.status == "success"

    def is_failed(self) -> bool:
        return self.status in {"failed", "cancelled", "error", "error_user", "error_timeout"}

    @property
    def download_url(self) -> str | None:
        return self.result.download_url if self.result else None


class ViktorRestClient:
    def __init__(
        self,
        *,
        api_base: str,
        token: str,
        connect_timeout: float = 5.0,
        read_timeout: float = 30.0,
        max_poll_seconds: int = 300,
    ) -> None:
        token = token.strip()
        if not token:
            raise ValueError("Missing VIKTOR token.")

        base = api_base.strip().rstrip("/")
        self.api_base = base if base.endswith("/api") else f"{base}/api"
        self.max_poll_seconds = max_poll_seconds
        self.timeout = (connect_timeout, read_timeout)
        self.auth_headers = {"Authorization": f"Bearer {token}"}
        self.json_headers = {**self.auth_headers, "Content-Type": "application/json"}

    def _url(self, path: str) -> str:
        return f"{self.api_base}/{path.lstrip('/')}"

    def _check(self, response: requests.Response, *, action: str) -> None:
        if response.ok:
            return
        body = response.text[:500]
        raise RuntimeError(f"{action} failed (status={response.status_code}): {body}")

    def get_json(
        self,
        path_or_url: str,
        *,
        params: dict[str, Any] | None = None,
        action: str = "GET request",
    ) -> Any:
        url = path_or_url if path_or_url.startswith("http") else self._url(path_or_url)
        response = requests.get(url, headers=self.auth_headers, params=params, timeout=self.timeout)
        self._check(response, action=action)
        return response.json()

    def post_json(
        self,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        action: str = "POST request",
    ) -> Any:
        response = requests.post(
            self._url(path),
            headers=self.json_headers,
            json=payload or {},
            timeout=self.timeout,
        )
        self._check(response, action=action)
        return response.json()

    def put_json(self, path: str, *, payload: dict[str, Any], action: str = "PUT request") -> Any:
        response = requests.put(
            self._url(path),
            headers=self.json_headers,
            json=payload,
            timeout=self.timeout,
        )
        self._check(response, action=action)
        return response.json()

    def paginate(self, path: str, *, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        url: str | None = self._url(path)
        page_params = params
        results: list[dict[str, Any]] = []

        while url:
            payload = self.get_json(url, params=page_params, action=f"List {path}")
            results.extend(payload.get("results", []))
            url = payload.get("next")
            page_params = None

        return results

    def get_entity(
        self,
        *,
        workspace_id: int,
        entity_id: int,
        properties: bool = False,
        clean_params: bool = False,
        param_types: bool = False,
    ) -> EntityResponse:
        payload = self.get_json(
            f"workspaces/{workspace_id}/entities/{entity_id}/",
            params={
                "properties": str(properties).lower(),
                "clean_params": str(clean_params).lower(),
                "param_types": str(param_types).lower(),
            },
            action="Get entity",
        )
        return EntityResponse.model_validate(payload)

    def create_editor_session(self, *, workspace_id: int, entity_id: int) -> EditorSessionResponse:
        payload = self.post_json(
            f"workspaces/{workspace_id}/entities/{entity_id}/session/",
            action="Create editor session",
        )
        return EditorSessionResponse.model_validate(payload)

    def create_child_entity(
        self,
        *,
        workspace_id: int,
        parent_entity_id: int,
        entity_type: int,
        name: str,
        properties: dict[str, Any],
    ) -> EntityResponse:
        payload = self.post_json(
            f"workspaces/{workspace_id}/entities/{parent_entity_id}/entities/",
            payload={"entity_type": entity_type, "name": name, "properties": properties},
            action="Create child entity",
        )
        if isinstance(payload, list):
            if not payload:
                raise RuntimeError("Create child entity returned an empty list.")
            payload = payload[0]
        return EntityResponse.model_validate(payload)

    def update_entity(
        self,
        *,
        workspace_id: int,
        entity_id: int,
        name: str,
        properties: dict[str, Any],
        message: str,
    ) -> EntityResponse:
        payload = self.put_json(
            f"workspaces/{workspace_id}/entities/{entity_id}/",
            payload={"name": name, "properties": properties, "message": message},
            action="Update entity",
        )
        return EntityResponse.model_validate(payload)

    def create_job(
        self,
        *,
        workspace_id: int,
        entity_id: int,
        method_name: str,
        params: dict[str, Any] | None = None,
        editor_session: UUID | None = None,
    ) -> JobStatusResponse:
        payload = {
            "method_name": method_name,
            "params": params or {},
            "poll_result": False,
        }
        if editor_session:
            payload["editor_session"] = str(editor_session)

        response_payload = self.post_json(
            f"workspaces/{workspace_id}/entities/{entity_id}/jobs/",
            payload=payload,
            action="Create job",
        )
        if response_payload.get("url"):
            return self.poll_job(response_payload["url"])
        if response_payload.get("status") == "success":
            return JobStatusResponse(
                uid=response_payload.get("uid") or 0,
                kind=response_payload.get("kind") or "result",
                status="success",
                result=JobResultPayload.model_validate(response_payload.get("content") or {}),
            )
        raise RuntimeError(f"Unexpected job response: {response_payload}")

    def poll_job(self, job_url: str) -> JobStatusResponse:
        deadline = time.monotonic() + self.max_poll_seconds
        sleep_s = 0.8

        while time.monotonic() < deadline:
            payload = self.get_json(job_url, action="Poll job")
            job = JobStatusResponse.model_validate(payload)
            if job.is_success():
                return job
            if job.is_failed():
                raise RuntimeError(f"Job failed with status={job.status}: {job.error}")

            time.sleep(sleep_s)
            sleep_s = min(sleep_s * 1.5, 5.0)

        raise TimeoutError(f"Job did not finish within {self.max_poll_seconds} seconds.")

    def download_json(self, download_url: str) -> Any:
        response = requests.get(download_url, timeout=self.timeout)
        self._check(response, action="Download result")
        return response.json()

    def build_entity_editor_url(self, *, workspace_id: int, entity_id: int) -> str:
        ui_base = self.api_base[:-4] if self.api_base.endswith("/api") else self.api_base
        return f"{ui_base}/workspaces/{workspace_id}/app/editor/{entity_id}"
```

## List all workspaces

```python
client = ViktorRestClient(api_base=get_api_base(), token=get_token())

workspaces = client.paginate(
    "workspaces/",
    params={
        "detail_level": "basic",
        "limit": 100,
        "sort": "name:asc",
    },
)

for workspace in workspaces:
    print(workspace["id"], workspace["name"])
```

## Filter workspaces by visibility and search text

```python
matching_workspaces = client.paginate(
    "workspaces/",
    params={
        "visibility": ["INTERNAL", "PRIVATE"],
        "search": "foundation",
        "detail_level": "basic",
        "limit": 100,
    },
)
```

## Read an entity and build its editor URL

```python
workspace_id = int(os.environ["VIKTOR_WORKSPACE_ID"])
entity_id = int(os.environ["VIKTOR_ENTITY_ID"])

entity = client.get_entity(
    workspace_id=workspace_id,
    entity_id=entity_id,
    properties=True,
    clean_params=True,
)
print(entity.id, entity.name)
print(client.build_entity_editor_url(workspace_id=workspace_id, entity_id=entity.id))
```

## Explicit write helper

```python
# Only call this after the user explicitly asks to create a child entity.
new_entity = client.create_child_entity(
    workspace_id=workspace_id,
    parent_entity_id=entity_id,
    entity_type=int(os.environ["VIKTOR_ENTITY_TYPE_ID"]),
    name="Generated alternative",
    properties={"input": {"value": 42}},
)
print(new_entity.id)
```

## Run an app method and download JSON result

```python
job = client.create_job(
    workspace_id=workspace_id,
    entity_id=entity_id,
    method_name=os.environ["VIKTOR_METHOD_NAME"],
    params={},
)

if job.download_url:
    result = client.download_json(job.download_url)
    print(result)
else:
    print(job.model_dump(exclude_none=True))
```
