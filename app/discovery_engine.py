from __future__ import annotations

from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.ai_pipeline import JobAIPipeline
from app.config import MAX_DETAIL_PAGES_PER_SOURCE
from app.official_sources import OfficialSource, is_official_url


def _fetch(url: str) -> tuple[str, str]:
    headers = {
        "User-Agent": "PersonalJobApplyer/1.0 (+personal-use)",
        "Accept": "text/html,application/xhtml+xml",
    }
    with httpx.Client(timeout=30, follow_redirects=True, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
        return str(response.url), response.text


def _candidate_links(
    index_url: str,
    html: str,
    allowed_domains: tuple[str, ...],
) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    keywords = (
        "job",
        "jobs",
        "career",
        "careers",
        "position",
        "opening",
        "requisition",
        "vacancy",
    )

    for anchor in soup.find_all("a", href=True):
        url = urljoin(index_url, anchor["href"])
        label = anchor.get_text(" ", strip=True).lower()
        if (
            is_official_url(url, allowed_domains)
            and any(key in url.lower() or key in label for key in keywords)
            and url not in links
        ):
            links.append(url)
        if len(links) >= MAX_DETAIL_PAGES_PER_SOURCE:
            break

    return links


def discover_official_source(
    source: OfficialSource,
    ai: JobAIPipeline | None = None,
) -> list[dict]:
    ai = ai or JobAIPipeline()
    index_url, index_html = _fetch(source.career_url)
    detail_urls = _candidate_links(index_url, index_html, source.allowed_domains)

    if index_url not in detail_urls:
        detail_urls.insert(0, index_url)

    jobs: list[dict] = []
    for detail_url in detail_urls[:MAX_DETAIL_PAGES_PER_SOURCE]:
        if not is_official_url(detail_url, source.allowed_domains):
            continue
        try:
            final_url, html = _fetch(detail_url)
            soup = BeautifulSoup(html, "html.parser")
            raw_text = soup.get_text("\n", strip=True)
            if len(raw_text) < 250:
                continue

            job = ai.extract_job(raw_text, final_url)
            job.setdefault("company", source.company)
            job["official_url"] = job.get("official_url") or final_url
            application_url = job.get("application_url")
            if application_url and not is_official_url(
                application_url,
                source.allowed_domains,
            ):
                job["application_url"] = None
            job["source"] = source.company

            if job.get("title") and job.get("description"):
                jobs.append(job)
        except (httpx.HTTPError, RuntimeError, ValueError):
            continue

    return jobs


def scrape_public_job_page(url: str) -> dict:
    final_url, html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    return {
        "url": final_url,
        "title": soup.title.get_text(" ", strip=True) if soup.title else "",
        "text": soup.get_text("\n", strip=True),
        "links": [
            urljoin(final_url, a.get("href"))
            for a in soup.find_all("a", href=True)
        ],
    }
