from dataclasses import dataclass, field

@dataclass
class CandidateProfile:
    name: str
    education: str
    skills: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            education=data["education"],
            skills=data.get("skills", []),
            projects=data.get("projects", []),
            certifications=data.get("certifications", []),
            experience=data.get("experience", []),
        )
