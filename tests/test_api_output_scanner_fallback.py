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


def test_get_output_scanner_raises_original_error_when_urlhaus_not_importable(monkeypatch):
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

    with pytest.raises(ValueError, match="Unknown scanner name: MaliciousURLs_URLHaus!"):
        _get_output_scanner("MaliciousURLs_URLHaus", {}, vault=DummyVault())
