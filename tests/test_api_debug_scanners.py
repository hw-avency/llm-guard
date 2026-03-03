from llm_guard_api.app.app import _merge_configured_with_loaded_scanners


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
