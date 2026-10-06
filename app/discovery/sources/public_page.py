from __future__ import annotations

from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup


@dataclass
class PublicPageConfig:
    url: str
    source: str
    job_selector: str
    title_selector: str
    company_selector: str
    location_selector: str
    description_selector: str
    application_link_selector: str = "a[href]"


class PublicPageSource:
    """Configurable parser for a permitted public job page.

    Site-specific selectors must be supplied by the user. This adapter does not
    bypass authentication, CAPTCHA, robots restrictions, or anti-bot controls.
    """

    def __init__(self, config: PublicPageConfig):
        self.config = config

    @staticmethod
    def _text(card, selector: str) -> str | None:
        node = card.select_one(selector)
        return node.get_text(" ", strip=True) if node else None

    def discover(self) -> list[dict]:
        response = httpx.get(self.config.url, timeout=20, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        jobs: list[dict] = []

        for card in soup.select(self.config.job_selector):
            link = card.select_one(self.config.application_link_selector)
            jobs.append(
                {
                    "source": self.config.source,
                    "source_job_id": None,
                    "company": self._text(card, self.config.company_selector) or "",
                    "title": self._text(card, self.config.title_selector) or "",
                    "location": self._text(card, self.config.location_selector),
                    "employment_type": None,
                    "description": self._text(card, self.config.description_selector) or "",
                    "skills": None,
                    "official_url": None,
                    "application_url": link.get("href") if link else None,
                    "posted_at": None,
                }
            )

        return jobs
