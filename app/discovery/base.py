from dataclasses import dataclass
from typing import Protocol

@dataclass
class DiscoveredJob:
    source: str
    source_job_id: str | None
    company: str
    title: str
    location: str | None
    employment_type: str | None
    description: str
    skills: str | None
    official_url: str | None
    application_url: str | None
    posted_at: str | None = None

class JobSource(Protocol):
    def discover(self) -> list[DiscoveredJob]: ...
