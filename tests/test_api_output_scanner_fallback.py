from types import SimpleNamespace

import pytest

from llm_guard_api.app.scanner import _get_output_scanner


class DummyVault:
    pass


class DummyURLHausScanner:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_get_output_scanner_constructs_urlhaus_directly_when_util_mapping_missing(monkeypatch):
    def fake_get_scanner_by_name(scanner_name, _scanner_config):
        if scanner_name == "MaliciousURLs_URLHaus":
            raise ValueError("Unknown scanner name: MaliciousURLs_URLHaus!")
        raise AssertionError(f"unexpected scanner {scanner_name}")

    monkeypatch.setattr(
        "llm_guard_api.app.scanner.output_scanners.get_scanner_by_name",
        fake_get_scanner_by_name,
    )
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


class DummyMaliciousURLsScanner:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_get_output_scanner_falls_back_to_malicious_urls_when_urlhaus_not_importable(monkeypatch):
    def fake_get_scanner_by_name(scanner_name, _scanner_config):
        raise ValueError(f"Unknown scanner name: {scanner_name}!")

    monkeypatch.setattr(
        "llm_guard_api.app.scanner.output_scanners.get_scanner_by_name",
        fake_get_scanner_by_name,
    )
    monkeypatch.setattr(
        "llm_guard_api.app.scanner.import_module",
        lambda _name: (_ for _ in ()).throw(ImportError("not installed")),
    )
    monkeypatch.setattr(
        "llm_guard_api.app.scanner.output_scanners.MaliciousURLs",
        DummyMaliciousURLsScanner,
    )

    scanner = _get_output_scanner(
        "MaliciousURLs_URLHaus",
        {
            "threshold": 0.8,
            "api_base_url": "https://urlhaus.example",
            "timeout": 3,
        },
        vault=DummyVault(),
    )

    assert isinstance(scanner, DummyMaliciousURLsScanner)
    assert scanner.kwargs == {"threshold": 0.8}
