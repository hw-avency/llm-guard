from types import SimpleNamespace

import pytest

from llm_guard_api.app.scanner import _get_output_scanner


class DummyVault:
    pass


class DummyURLHausScanner:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_get_output_scanner_constructs_urlhaus_directly_when_available(monkeypatch):
    monkeypatch.setattr(
        "llm_guard_api.app.scanner.import_module",
        lambda _name: SimpleNamespace(MaliciousURLs_URLHaus=DummyURLHausScanner),
    )

    scanner = _get_output_scanner(
        "MaliciousURLs_URLHaus",
        {"api_base_url": "https://example.local", "threshold": 0.9},
        vault=DummyVault(),
    )

    assert isinstance(scanner, DummyURLHausScanner)
    assert scanner.kwargs == {"api_base_url": "https://example.local", "threshold": 0.9}


def test_get_output_scanner_raises_error_when_urlhaus_not_importable(monkeypatch):
    monkeypatch.setattr(
        "llm_guard_api.app.scanner.import_module",
        lambda _name: (_ for _ in ()).throw(ImportError("not installed")),
    )

    with pytest.raises(ValueError, match="MaliciousURLs_URLHaus"):
        _get_output_scanner(
            "MaliciousURLs_URLHaus",
            {
                "threshold": 0.8,
                "api_base_url": "https://urlhaus.example",
                "timeout": 3,
            },
            vault=DummyVault(),
        )
