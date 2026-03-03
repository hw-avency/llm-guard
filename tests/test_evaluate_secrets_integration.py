from llm_guard import scan_prompt
from llm_guard.input_scanners import Regex, Secrets


def test_scan_prompt_secrets_detected_after_redacting_scanner():
    prompt = "My github token is: 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"  # gitleaks:allow
    scanners = [Regex(patterns=[r"ghp_[A-Za-z0-9]+"], is_blocked=True), Secrets()]

    sanitized_prompt, results_valid, results_score = scan_prompt(
        scanners,
        prompt,
        fail_fast=False,
    )

    assert sanitized_prompt == "My github token is: [REDACTED]"
    assert results_valid == {"Regex": False, "Secrets": False}
    assert results_score == {"Regex": 1.0, "Secrets": 1.0}
