import pytest

from llm_guard_api.app.app import _collect_scanner_results
from llm_guard_api.app.scanner import InputIsInvalid


def test_collect_scanner_results_collects_all_scores_and_invalid_state():
    results = [
        ("PromptInjection", 0.91),
        InputIsInvalid("Secrets", "AKIAIOSFODNN7EXAMPLE", 1.0),
        ("Toxicity", 0.72),
    ]

    is_valid, scores = _collect_scanner_results(results)

    assert not is_valid
    assert scores == {"PromptInjection": 0.91, "Secrets": 1.0, "Toxicity": 0.72}


def test_collect_scanner_results_raises_unhandled_exception():
    with pytest.raises(RuntimeError):
        _collect_scanner_results([RuntimeError("boom")])
