from dataclasses import dataclass
from bs4 import BeautifulSoup
import httpx

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

    def discover(self):
        response = httpx.get(self.config.url, timeout=20, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        for card in soup.select(self.config.job_selector):
            def text(selector):
                node = card.select_one(selector)
                return node.get_text(" ", strip=True) if node else None
            link = card.select_one(self.config.application_link_selector)
            jobs.append({
                "source": self.config.source,
                "source_job_id": None,
                "company": text(self.config.company_selector) or "",
                "title": text(self.config.title_selector) or "",
                "location": text(self.config.location_selector),
                "employment_type": None,
                "description": text(self.config.description_selector) or "",
                "skills": None,
                "official_url": None,
                "application_url": link.get("href") if link else None,
                "posted_at": None,
            })
        return jobs
