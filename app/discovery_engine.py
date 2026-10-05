from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup


def scrape_public_job_page(url: str) -> dict:
    """Fetch a public job page without bypassing access controls."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; PersonalJobApplyer/1.0)"}
    with httpx.Client(timeout=30, follow_redirects=True, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = soup.get_text("\n", strip=True)
    links = [urljoin(str(response.url), a.get("href")) for a in soup.find_all("a", href=True)]
    return {"url": str(response.url), "title": title, "text": text, "links": links}
