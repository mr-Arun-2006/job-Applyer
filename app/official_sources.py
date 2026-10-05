from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class OfficialSource:
    company: str
    career_url: str
    allowed_domains: tuple[str, ...]


def load_official_sources(path: str = "./config/company_sources.json") -> list[OfficialSource]:
    file = Path(path)
    if not file.exists():
        return []
    raw = json.loads(file.read_text(encoding="utf-8"))
    sources = []
    for item in raw:
        company = str(item["company"]).strip()
        career_url = str(item["career_url"]).strip()
        allowed = tuple(str(x).lower().strip() for x in item.get("allowed_domains", []))
        if not allowed:
            allowed = (urlparse(career_url).hostname or "").lower(),
        sources.append(OfficialSource(company, career_url, allowed))
    return sources


def is_official_url(url: str, allowed_domains: tuple[str, ...]) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    if not host or urlparse(url).scheme not in {"http", "https"}:
        return False

    for allowed in allowed_domains:
        domain = allowed.lstrip(".")
        if host == domain or host.endswith("." + domain):
            return True
    return False
