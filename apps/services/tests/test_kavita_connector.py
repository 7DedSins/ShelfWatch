"""Kavita connector tests.

AI-written 2026-09-07 (user granted implementation of this suite).
You still need to explain each case out loud: empty list vs raise,
one 401 retry, client-side library filter.

No live VPS — respx intercepts httpx.
"""

import httpx
import pytest
import respx

from apps.services.connectors.base import (
    ServiceAuthFailed,
    ServiceBadResponse,
    ServiceUnavailable,
)
from apps.services.connectors.kavita import KavitaConnector

BASE = "http://kavita.test"


def _connector() -> KavitaConnector:
    return KavitaConnector(BASE, api_key="fake-key")


def _mock_authenticate(token: str = "test-jwt") -> None:
    respx.post(url__regex=rf"{BASE}/api/Plugin/authenticate.*").mock(
        return_value=httpx.Response(200, json={"token": token})
    )


@respx.mock
def test_health_timeout_on_authenticate_raises_unavailable():
    respx.post(url__regex=rf"{BASE}/api/Plugin/authenticate.*").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    with pytest.raises(ServiceUnavailable):
        _connector().health()


@respx.mock
def test_authenticate_401_raises_auth_failed():
    respx.post(url__regex=rf"{BASE}/api/Plugin/authenticate.*").mock(
        return_value=httpx.Response(401)
    )
    with pytest.raises(ServiceAuthFailed):
        _connector().health()


@respx.mock
def test_libraries_html_raises_bad_response():
    _mock_authenticate()
    respx.get(f"{BASE}/api/Library/libraries").mock(
        return_value=httpx.Response(
            200,
            text="<html>nope</html>",
            headers={"Content-Type": "text/html"},
        )
    )
    with pytest.raises(ServiceBadResponse):
        _connector().list_libraries()


@respx.mock
def test_empty_libraries_returns_empty_list():
    _mock_authenticate()
    respx.get(f"{BASE}/api/Library/libraries").mock(
        return_value=httpx.Response(200, json=[])
    )
    assert _connector().list_libraries() == []


@respx.mock
def test_libraries_timeout_raises_unavailable_not_empty_list():
    _mock_authenticate()
    respx.get(f"{BASE}/api/Library/libraries").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    connector = _connector()
    with pytest.raises(ServiceUnavailable):
        connector.list_libraries()


@respx.mock
def test_list_libraries_maps_id_and_name():
    _mock_authenticate()
    respx.get(f"{BASE}/api/Library/libraries").mock(
        return_value=httpx.Response(
            200,
            json=[{"id": 7, "name": "Manhwa"}],
        )
    )
    libraries = _connector().list_libraries()
    assert len(libraries) == 1
    assert libraries[0].id == "7"
    assert libraries[0].name == "Manhwa"


@respx.mock
def test_series_filters_client_side_by_library_id():
    _mock_authenticate()
    respx.post(url__regex=rf"{BASE}/api/series/all-v2.*").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"id": 1, "name": "Keep", "libraryId": 7},
                {"id": 2, "name": "Drop", "libraryId": 8},
            ],
        )
    )
    series = list(_connector().list_series("7"))
    assert [s.id for s in series] == ["1"]
    assert series[0].name == "Keep"
    assert series[0].library_id == "7"


@respx.mock
def test_series_timeout_raises_unavailable():
    _mock_authenticate()
    respx.post(url__regex=rf"{BASE}/api/series/all-v2.*").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    with pytest.raises(ServiceUnavailable):
        list(_connector().list_series("7"))


@respx.mock
def test_series_non_int_library_id_raises_bad_response():
    _mock_authenticate()
    with pytest.raises(ServiceBadResponse):
        list(_connector().list_series("not-an-id"))


@respx.mock
def test_health_retries_once_on_401_then_succeeds():
    _mock_authenticate()
    respx.get(f"{BASE}/api/Health").mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200),
        ]
    )
    result = _connector().health()
    assert result.ok is True
    assert respx.calls.call_count >= 3  # auth + GET 401 + re-auth + GET 200
