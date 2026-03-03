from unittest.mock import Mock

import pytest

from llm_guard.output_scanners.malicious_urls_urlhaus import MaliciousURLs_URLHaus


@pytest.mark.parametrize(
    "output,found,expected_valid,expected_score",
    [
        ("No links in this output.", False, True, -1.0),
        ("Visit https://example.com.", False, True, -1.0),
        ("Visit http://222.134.175.94:48838/i", True, False, 1.0),
    ],
)
def test_scan(output, found, expected_valid, expected_score, monkeypatch):
    scanner = MaliciousURLs_URLHaus()

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"found": found}

    requests_get = Mock(return_value=response)
    monkeypatch.setattr("llm_guard.output_scanners.malicious_urls_urlhaus.requests.get", requests_get)

    sanitized_output, valid, score = scanner.scan("", output)

    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score


def test_get_scanner_by_name_supports_urlhaus_scanner():
    from llm_guard.output_scanners.util import get_scanner_by_name

    scanner = get_scanner_by_name("MaliciousURLs_URLHaus")

    assert isinstance(scanner, MaliciousURLs_URLHaus)
