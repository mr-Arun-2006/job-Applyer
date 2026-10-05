import re


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9+#.]+", text.lower()))


def match_job_to_profile(job, profile):
    job_text = " ".join([
        job.get("title", ""),
        job.get("description", ""),
        job.get("skills", "") or "",
    ])
    job_tokens = _tokens(job_text)
    candidate_tokens = _tokens(" ".join(profile.skills + profile.projects + profile.certifications + profile.experience))
    matched = sorted(job_tokens & candidate_tokens)
    score = round((len(matched) / max(len(_tokens(" ".join(profile.skills))), 1)) * 100, 2)
    return {"score": min(score, 100), "matched_keywords": matched}
