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


class KavitaConnector(BaseConnector):
    def __init__(self, url: str, api_key: str) -> None:
        self._api_key = api_key
        # JWT lives only on this instance (RAM). None = not authenticated yet;
        # __init__ must not hit the network.
        self._token: str | None = None
        self._client = httpx.Client(
            base_url=url.rstrip("/"),
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
        )

    def _authenticate(self) -> None:
        try:
            response = self._client.post(
                "/api/Plugin/authenticate",
                params={"apiKey": self._api_key, "pluginName": "ShelfWatch"},
            )
        except httpx.TimeoutException as exc:
            raise ServiceUnavailable("Kavita authenticate timed out") from exc
        except httpx.NetworkError as exc:
            raise ServiceUnavailable("Kavita authenticate unreachable") from exc

        if response.status_code in (401, 403):
            raise ServiceAuthFailed("Kavita rejected the API key")
        if response.status_code >= 400:
            raise ServiceBadResponse(f"Kavita authenticate HTTP {response.status_code}")

        try:
            payload = response.json()
            token = payload["token"]
        except (ValueError, KeyError, TypeError) as exc:
            raise ServiceBadResponse("Kavita authenticate returned no token") from exc

        self._token = token

    def _ensure_token(self) -> None:
        if self._token is None:
            self._authenticate()

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        # json/params default to None so GET callers stay unchanged; series POST
        # must pass them through on BOTH sends (including the 401 retry).
        self._ensure_token()
        response = self._send(method, path, json=json, params=params)

        if response.status_code == 401:
            self._token = None
            self._authenticate()
            response = self._send(method, path, json=json, params=params)
            if response.status_code == 401:
                raise ServiceAuthFailed("Kavita JWT rejected after re-auth")

        if response.status_code in (401, 403):
            raise ServiceAuthFailed("Kavita authorization failed")

        if response.status_code >= 400:
            raise ServiceBadResponse(f"Kavita HTTP {response.status_code}")
        return response

    def _send(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        try:
            return self._client.request(
                method, path, headers=self._auth_headers(), json=json, params=params
            )
        except httpx.TimeoutException as exc:
            raise ServiceUnavailable("Kavita request timed out") from exc
        except httpx.NetworkError as exc:
            raise ServiceUnavailable("Kavita unreachable") from exc

    def health(self) -> HealthResult:
        self._request("GET", "/api/Health")
        return HealthResult(ok=True)

    def list_libraries(self) -> list[RemoteLibrary]:
        # UI route /library/7 is Angular, not this. List all libraries:
        response = self._request("GET", "/api/Library/libraries")
        try:
            payload = response.json()
        except ValueError as exc:
            raise ServiceBadResponse("Kavita libraries not JSON") from exc
        if not isinstance(payload, list):
            raise ServiceBadResponse("Kavita libraries not a list")
        return [
            RemoteLibrary(id=str(item["id"]), name=str(item["name"]))
            for item in payload
        ]

    def list_series(self, library_id: str) -> Iterator[RemoteSeries]:
        page = 1
        page_size = 100

        while True:
            # Kavita's all-v2 ignores libraryId in the body (confirmed quirk).
            # We still send it, then filter client-side so we do not invent an
            # empty library from "other libraries' series" or from a timeout.
            response = self._request(
                "POST",
                "/api/series/all-v2",
                json={"libraryId": int(library_id)},
                params={"PageNumber": page, "PageSize": page_size},
            )

            try:
                payload = response.json()
            except ValueError as exc:
                raise ServiceBadResponse("Kavita series not JSON") from exc
            if not isinstance(payload, list):
                raise ServiceBadResponse("Kavita series not a list")

            for item in payload:
                try:
                    item_library_id = str(item["libraryId"])
                    series_id = str(item["id"])
                    name = str(item["name"])
                except KeyError as exc:
                    raise ServiceBadResponse("Kavita series row missing fields") from exc
                if item_library_id != str(library_id):
                    continue
                yield RemoteSeries(
                    id=series_id,
                    name=name,
                    library_id=item_library_id,
                )

            # Short page => last page. A full page may still be the last; we
            # request one more and stop when it is short or empty.
            if len(payload) < page_size:
                break
            page += 1
