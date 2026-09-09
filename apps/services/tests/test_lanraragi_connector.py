"""LANraragi connector tests.

AI-written 2026-09-09 (user granted the suite). Explain out loud:
timeout vs empty, no JWT retry, search wraps rows in data, category archives filter.

No live VPS — respx intercepts httpx.
"""

import base64

import httpx
import pytest
import respx

from apps.services.connectors.base import (
    ServiceAuthFailed,
    ServiceBadResponse,
    ServiceUnavailable,
)
from apps.services.connectors.lanraragi import LanraragiConnector

BASE = "http://lrr.test"
KEY = "fake-key"


def _connector() -> LanraragiConnector:
    return LanraragiConnector(BASE, api_key=KEY)


def _categories(*rows: dict) -> None:
    respx.get(f"{BASE}/api/categories").mock(
        return_value=httpx.Response(200, json=list(rows))
    )


@respx.mock
def test_health_timeout_raises_unavailable():
    respx.get(f"{BASE}/api/shinobu").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    with pytest.raises(ServiceUnavailable):
        _connector().health()


@respx.mock
def test_health_401_raises_auth_failed_without_retry():
    respx.get(f"{BASE}/api/shinobu").mock(return_value=httpx.Response(401))
    with pytest.raises(ServiceAuthFailed):
        _connector().health()
    assert respx.calls.call_count == 1


@respx.mock
def test_health_sends_base64_bearer_key():
    respx.get(f"{BASE}/api/shinobu").mock(return_value=httpx.Response(200, json={}))
    assert _connector().health().ok is True
    encoded = base64.b64encode(KEY.encode("utf-8")).decode("ascii")
    assert respx.calls.last.request.headers["Authorization"] == f"Bearer {encoded}"


@respx.mock
def test_categories_html_raises_bad_response():
    respx.get(f"{BASE}/api/categories").mock(
        return_value=httpx.Response(
            200,
            text="<html>nope</html>",
            headers={"Content-Type": "text/html"},
        )
    )
    with pytest.raises(ServiceBadResponse):
        _connector().list_libraries()


@respx.mock
def test_empty_categories_returns_empty_list():
    _categories()
    assert _connector().list_libraries() == []


@respx.mock
def test_list_libraries_maps_id_and_name():
    _categories({"id": "cat1", "name": "Comics"})
    libraries = _connector().list_libraries()
    assert len(libraries) == 1
    assert libraries[0].id == "cat1"
    assert libraries[0].name == "Comics"


@respx.mock
def test_search_timeout_raises_unavailable_not_empty():
    _categories({"id": "cat1", "name": "Comics", "archives": ["a1"]})
    respx.get(url__regex=rf"{BASE}/api/search.*").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    with pytest.raises(ServiceUnavailable):
        list(_connector().list_series("cat1"))


@respx.mock
def test_search_list_instead_of_object_raises_bad_response():
    _categories({"id": "cat1", "name": "Comics", "archives": ["a1"]})
    respx.get(url__regex=rf"{BASE}/api/search.*").mock(
        return_value=httpx.Response(200, json=[])
    )
    with pytest.raises(ServiceBadResponse):
        list(_connector().list_series("cat1"))


@respx.mock
def test_unknown_category_raises_bad_response():
    _categories({"id": "other", "name": "Nope", "archives": ["a1"]})
    with pytest.raises(ServiceBadResponse):
        list(_connector().list_series("cat1"))


@respx.mock
def test_series_filters_by_category_archive_ids():
    _categories({"id": "cat1", "name": "Comics", "archives": ["keep"]})
    respx.get(url__regex=rf"{BASE}/api/search.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "recordsFiltered": 2,
                "data": [
                    {"arcid": "keep", "title": "Keep"},
                    {"arcid": "drop", "title": "Drop"},
                ],
            },
        )
    )
    series = list(_connector().list_series("cat1"))
    assert [s.id for s in series] == ["keep"]
    assert series[0].name == "Keep"
    assert series[0].library_id == "cat1"


@respx.mock
def test_empty_search_data_yields_nothing():
    _categories({"id": "cat1", "name": "Comics", "archives": ["a1"]})
    respx.get(url__regex=rf"{BASE}/api/search.*").mock(
        return_value=httpx.Response(
            200,
            json={"recordsFiltered": 0, "data": []},
        )
    )
    assert list(_connector().list_series("cat1")) == []


@respx.mock
def test_dynamic_category_without_archives_yields_all_search_hits():
    _categories({"id": "cat1", "name": "Dynamic"})
    respx.get(url__regex=rf"{BASE}/api/search.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "recordsFiltered": 1,
                "data": [{"arcid": "only", "title": "Only"}],
            },
        )
    )
    series = list(_connector().list_series("cat1"))
    assert [s.id for s in series] == ["only"]
