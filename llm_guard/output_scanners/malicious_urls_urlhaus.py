from __future__ import annotations

import requests

from llm_guard.util import extract_urls, get_logger

from .base import Scanner

LOGGER = get_logger()


class MaliciousURLs_URLHaus(Scanner):
    """Scanner that checks output URLs against URLHaus-style threat intelligence API."""

    def __init__(
        self,
        *,
        api_base_url: str = "https://threatintel-813066616888.europe-west3.run.app",
        timeout: int = 5,
    ) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._timeout = timeout

    def is_malicious(self, url: str) -> bool:
        """Return whether the URL is reported by the threat intel API."""
        try:
            response = requests.get(
                f"{self._api_base_url}/api/check",
                params={"url": url},
                timeout=self._timeout,
            )
            response.raise_for_status()
            payload = response.json()
            return bool(payload.get("found", False))
        except (requests.RequestException, ValueError) as error:
            LOGGER.warning("Failed to validate URL via URLHaus API", url=url, error=str(error))
            return False

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        if output.strip() == "":
            return output, True, -1.0

        urls = extract_urls(output)
        if len(urls) == 0:
            return output, True, -1.0

        LOGGER.debug("Found URLs in the output", len=len(urls))

        for url in urls:
            if self.is_malicious(url):
                LOGGER.warning("Detected malicious URL via URLHaus API", url=url)
                return output, False, 1.0

        return output, True, -1.0
