from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class OfficialSource:
    company: str
    career_url: str
    allowed_domains: tuple[str, ...]


def load_official_sources(
    path: str = "./config/company_sources.json",
) -> list[OfficialSource]:
    file = Path(path)
    if not file.is_file():
        return []

    raw = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise TypeError(f"Official sources file must contain a JSON array: {file}")

    sources: list[OfficialSource] = []

    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise TypeError(f"Official source #{index} must be a JSON object.")

        company = str(item.get("company", "")).strip()
        career_url = str(item.get("career_url", "")).strip()

        if not company:
            raise ValueError(f"Official source #{index} is missing 'company'.")
        if not career_url:
            raise ValueError(f"Official source #{index} is missing 'career_url'.")

        parsed = urlparse(career_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError(
                f"Official source #{index} has an invalid career_url: {career_url}"
            )

        configured_domains = item.get("allowed_domains", [])
        if not isinstance(configured_domains, list):
            raise TypeError(
                f"Official source #{index} 'allowed_domains' must be an array."
            )

        allowed = tuple(
            str(domain).lower().strip().lstrip(".")
            for domain in configured_domains
            if str(domain).strip()
        )
        if not allowed:
            allowed = (parsed.hostname.lower(),)

        sources.append(OfficialSource(company, career_url, allowed))

    return sources


def is_official_url(url: str, allowed_domains: tuple[str, ...]) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    host = (parsed.hostname or "").lower().rstrip(".")
    if not host or parsed.scheme not in {"http", "https"}:
        return False

    for allowed in allowed_domains:
        domain = allowed.lower().strip().lstrip(".").rstrip(".")
        if domain and (host == domain or host.endswith("." + domain)):
            return True

    return False
