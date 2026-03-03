from llm_guard_api.app.app import _get_output_scanners_function
from llm_guard_api.app.config import AppConfig, Config, ScannerConfig


class DummyLoadedScanner:
    pass


class DummyURLHausScanner:
    pass


class DummyVault:
    pass


def _make_config(scanner_type: str) -> Config:
    return Config(
        input_scanners=[],
        output_scanners=[ScannerConfig(type=scanner_type, params={})],
        app=AppConfig(lazy_load=True),
    )


def test_output_scanners_are_reloaded_when_config_changes(monkeypatch):
    initial_config = _make_config("MaliciousURLs")
    updated_config = _make_config("MaliciousURLs_URLHaus")

    config_reads = iter([initial_config, updated_config])
    monkeypatch.setattr("llm_guard_api.app.app.get_config", lambda _path: next(config_reads))

    loaded_scanner_types: list[str] = []

    def fake_get_output_scanners(scanners, _vault):
        scanner_type = scanners[0].type
        loaded_scanner_types.append(scanner_type)
        if scanner_type == "MaliciousURLs_URLHaus":
            return [DummyURLHausScanner()]
        return [DummyLoadedScanner()]

    monkeypatch.setattr("llm_guard_api.app.app.get_output_scanners", fake_get_output_scanners)

    get_scanners = _get_output_scanners_function(initial_config, DummyVault(), "fake-config.yml")

    first_loaded = get_scanners()
    second_loaded = get_scanners()

    assert type(first_loaded[0]).__name__ == "DummyLoadedScanner"
    assert type(second_loaded[0]).__name__ == "DummyURLHausScanner"
    assert loaded_scanner_types == ["MaliciousURLs", "MaliciousURLs_URLHaus"]
