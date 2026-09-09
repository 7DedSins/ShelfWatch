import base64
from collections.abc import Iterator

import httpx

from .base import (
    BaseConnector,
    HealthResult,
    RemoteLibrary,
    RemoteSeries,
    ServiceAuthFailed,
    ServiceBadResponse,
    ServiceUnavailable,
)


class LanraragiConnector(BaseConnector):
    def __init__(self, url: str, api_key: str) -> None:
        self._api_key = api_key
        self._client = httpx.Client(
            base_url=url.rstrip("/"),
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
        )

    def _auth_headers(self) -> dict[str, str]:
        encoded = base64.b64encode(self._api_key.encode("utf-8")).decode("ascii")
        return {"Authorization": f"Bearer {encoded}"}

    def _request(
        self, method: str, path: str, params: dict | None = None
    ) -> httpx.Response:
        response = self._send(method, path, params=params)
        if response.status_code in (401, 403):
            raise ServiceAuthFailed("LANraragi authorization failed")
        if response.status_code >= 400:
            raise ServiceBadResponse(f"LANraragi HTTP {response.status_code}")
        return response

    def _send(
        self, method: str, path: str, params: dict | None = None
    ) -> httpx.Response:
        try:
            return self._client.request(
                method, path, headers=self._auth_headers(), params=params
            )
        except httpx.TimeoutException as extra:
            raise ServiceUnavailable("LANraragi request timed out") from extra
        except httpx.NetworkError as extra:
            raise ServiceUnavailable("LANraragi unreachable") from extra

    def health(self) -> HealthResult:
        self._request("GET", "/api/shinobu")
        return HealthResult(ok=True)

    def list_libraries(self) -> list[RemoteLibrary]:
        payload = self._json_list(self._request("GET", "/api/categories"), "categories")
        try:
            return [
                RemoteLibrary(id=str(item["id"]), name=str(item["name"]))
                for item in payload
            ]
        except KeyError as extra:
            raise ServiceBadResponse("LANraragi category missing id/name") from extra

    def list_series(self, library_id: str) -> Iterator[RemoteSeries]:
        # Search is instance-wide. Static categories list member arcids on
        # GET /api/categories; filter here (same idea as Kavita all-v2).
        allowed_ids = self._archive_ids_for_category(library_id)

        start = 0
        while True:
            payload = self._json_object(
                self._request("GET", "/api/search", params={"start": start}),
                "search",
            )
            try:
                rows = payload["data"]
                records_filtered = int(payload.get("recordsFiltered", len(rows)))
            except (KeyError, TypeError, ValueError) as extra:
                raise ServiceBadResponse("LANraragi search missing data") from extra
            if not isinstance(rows, list):
                raise ServiceBadResponse("LANraragi search data is not a list")

            for item in rows:
                try:
                    series_id = str(item["arcid"])
                    name = str(item["title"])
                except KeyError as extra:
                    raise ServiceBadResponse(
                        "LANraragi search row missing arcid/title"
                    ) from extra
                if allowed_ids is not None and series_id not in allowed_ids:
                    continue
                yield RemoteSeries(
                    id=series_id,
                    name=name,
                    library_id=str(library_id),
                )

            start += len(rows)
            if len(rows) == 0 or start >= records_filtered:
                break

    def _archive_ids_for_category(self, library_id: str) -> set[str] | None:
        """Member arcids, or None if this category has no static archive list."""
        for item in self._json_list(
            self._request("GET", "/api/categories"), "categories"
        ):
            if str(item.get("id")) != str(library_id):
                continue
            archives = item.get("archives")
            if not archives:
                return None
            return {str(arc_id) for arc_id in archives}
        raise ServiceBadResponse(f"LANraragi category not found: {library_id!r}")

    def _json_list(self, response: httpx.Response, label: str) -> list:
        payload = self._json_object(response, label)
        if not isinstance(payload, list):
            raise ServiceBadResponse(f"LANraragi {label} not a list")
        return payload

    def _json_object(self, response: httpx.Response, label: str):
        try:
            return response.json()
        except ValueError as extra:
            raise ServiceBadResponse(f"LANraragi {label} not JSON") from extra
