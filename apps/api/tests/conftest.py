"""Shared API test helpers. AI-written [!]."""


def results(response):
    """List body after pagination: ``{count, next, previous, results}``."""
    body = response.json()
    assert isinstance(body, dict), body
    assert "results" in body, body
    return body["results"]
