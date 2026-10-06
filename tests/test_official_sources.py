from __future__ import annotations

import json

from app.official_sources import is_official_url, load_official_sources


def test_official_url_requires_exact_domain_or_subdomain():
    allowed = ("example.com",)
    assert is_official_url("https://example.com/jobs/1", allowed)
    assert is_official_url("https://careers.example.com/jobs/1", allowed)
    assert not is_official_url("https://example.com.evil.test/jobs/1", allowed)
    assert not is_official_url("ftp://example.com/jobs/1", allowed)


def test_load_official_sources(tmp_path):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps(
            [
                {
                    "company": "Example",
                    "career_url": "https://careers.example.com/jobs",
                    "allowed_domains": ["careers.example.com"],
                }
            ]
        ),
        encoding="utf-8",
    )

    sources = load_official_sources(str(path))

    assert len(sources) == 1
    assert sources[0].company == "Example"
    assert sources[0].allowed_domains == ("careers.example.com",)
