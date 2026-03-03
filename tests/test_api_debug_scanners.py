import pytest
from fastapi import HTTPException

from llm_guard_api.app.app import _get_debug_scanners_response, _merge_configured_with_loaded_scanners
from llm_guard_api.app.config import get_config


class DummyScanner:
    pass


class MaliciousURLs_URLHaus:
    pass


def test_merge_configured_with_loaded_scanners_adds_missing_runtime_scanners():
    configured = [
        {"type": "Deanonymize", "params": {"matching_strategy": "exact"}},
        {"type": "MaliciousURLs", "params": {"threshold": 0.75}},
    ]

    merged = _merge_configured_with_loaded_scanners(
        configured,
        [DummyScanner(), MaliciousURLs_URLHaus()],
    )

    assert merged == [
        {"type": "Deanonymize", "params": {"matching_strategy": "exact"}},
        {"type": "MaliciousURLs", "params": {"threshold": 0.75}},
        {"type": "DummyScanner", "params": {}},
        {"type": "MaliciousURLs_URLHaus", "params": {}},
    ]


def test_merge_configured_with_loaded_scanners_keeps_existing_scanner_types_once():
    configured = [{"type": "MaliciousURLs_URLHaus", "params": {}}]

    merged = _merge_configured_with_loaded_scanners(configured, [MaliciousURLs_URLHaus()])

    assert merged == configured


def test_default_api_scanners_config_contains_urlhaus_scanner():
    config = get_config("llm_guard_api/config/scanners.yml")

    assert config is not None
    assert "MaliciousURLs_URLHaus" in [scanner.type for scanner in config.output_scanners]


def test_get_debug_scanners_response_reads_latest_config_file():
    config = get_config("llm_guard_api/config/scanners.yml")

    assert config is not None

    response = _get_debug_scanners_response(config, "llm_guard_api/config/scanners.yml")

    assert "MaliciousURLs_URLHaus" in [scanner["type"] for scanner in response.output_scanners]


def test_get_debug_scanners_response_raises_when_config_cannot_be_loaded(monkeypatch):
    config = get_config("llm_guard_api/config/scanners.yml")

    assert config is not None

    monkeypatch.setattr("llm_guard_api.app.app.get_config", lambda _config_file: None)

    with pytest.raises(HTTPException) as exc:
        _get_debug_scanners_response(config, "llm_guard_api/config/scanners.yml")

    assert exc.value.status_code == 500
