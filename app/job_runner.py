from __future__ import annotations

import os
from pathlib import Path

from app.ai_pipeline import JobAIPipeline
from app.database import has_application, init_db, record_application, save_jobs


class JobRunner:
    """Personal job workflow: discover, score, customize, prepare, then apply."""

    def __init__(self, ai: JobAIPipeline | None = None):
        self.ai = ai or JobAIPipeline()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./data/applications"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_match_score = float(os.getenv("MIN_MATCH_SCORE", "50"))
        self.apply_all = os.getenv("APPLY_TO_ALL_ELIGIBLE", "true").lower() == "true"

    def eligible_jobs(self, jobs: list[dict], profile_json: str) -> list[dict]:
        selected = []
        for job in jobs:
            if has_application(job):
                continue
            analysis = self.ai.analyze_job(job)
            match = self.ai.match_job(job, profile_json)
            job["analysis"] = analysis
            job["match"] = match
            score = float(match.get("score_0_100", 0))
            job["match_score"] = score
            if score >= self.min_match_score:
                selected.append(job)
        return selected

    def prepare_application(self, job: dict, profile_json: str, master_resume: str) -> dict:
        resume = self.ai.customize_resume_json(job, profile_json, master_resume)
        cover_letter = self.ai.generate_cover_letter(job, profile_json, resume)
        safe_name = "".join(
            c if c.isalnum() or c in "._-" else "_"
            for c in f"{job.get('company','company')}_{job.get('title','role')}"
        )[:120]
        resume_path = self.output_dir / f"{safe_name}_resume.txt"
        cover_path = self.output_dir / f"{safe_name}_cover_letter.txt"
        resume_path.write_text(resume, encoding="utf-8")
        cover_path.write_text(cover_letter, encoding="utf-8")
        return {
            "resume_path": str(resume_path),
            "cover_letter_path": str(cover_path),
            "resume": resume,
            "cover_letter": cover_letter,
        }

    def record_result(self, job: dict, prepared: dict, status: str, error: str | None = None) -> None:
        record_application(
            job,
            prepared.get("resume_path"),
            prepared.get("cover_letter_path"),
            status,
            error,
        )
