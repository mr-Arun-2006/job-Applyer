from __future__ import annotations

import os
from pathlib import Path

from app.ai_pipeline import JobAIPipeline
from app.database import has_application, record_application
from app.resume_engine import ATSResumeEngine


class JobRunner:
    """Personal job workflow: discover, score, customize, prepare, then apply."""

    def __init__(self, ai: JobAIPipeline | None = None):
        self.ai = ai or JobAIPipeline()
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./data/applications"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_match_score = float(os.getenv("MIN_MATCH_SCORE", "50"))
        self.apply_all = os.getenv("APPLY_TO_ALL_ELIGIBLE", "true").lower() == "true"
        self.resume_engine = ATSResumeEngine()

    def eligible_jobs(self, jobs: list[dict], profile_json: str) -> list[dict]:
        selected = []
        for job in jobs:
            if has_application(job):
                continue
            if not job.get("application_url"):
                continue

            analysis = self.ai.analyze_job(job)
            match = self.ai.match_job(job, profile_json)
            job["analysis"] = analysis
            job["match"] = match
            try:
                score = float(match.get("score_0_100", 0))
            except (TypeError, ValueError):
                score = 0.0
            job["match_score"] = score

            decision = str(match.get("decision", "SKIP")).upper()
            if self.apply_all and score >= self.min_match_score and decision == "APPLY":
                selected.append(job)
        return selected

    def prepare_application(
        self, job: dict, profile_json: str, master_resume: str
    ) -> dict:
        resume_text = self.ai.customize_resume_json(job, profile_json, master_resume)

        validation = self.ai.validate_resume(job, master_resume, resume_text)
        if not bool(validation.get("approved", False)):
            retry_prompt = (
                resume_text
                + "\n\nFACT-CHECK FEEDBACK:\n"
                + "\n".join(validation.get("unsupported_claims", []))
                + "\n\nATS FEEDBACK:\n"
                + "\n".join(validation.get("ats_issues", []))
            )
            resume_text = self.ai.router.complete(
                "resume",
                """Correct the supplied resume using the validation feedback.
Preserve only facts supported by the master resume. Keep it ATS-friendly,
single-column in structure, with standard section headings. Return resume text only.""",
                f"JOB:\n{job}\n\nMASTER RESUME:\n{master_resume}\n\nDRAFT:\n{retry_prompt}",
                temperature=0.0,
                max_tokens=6000,
            )
            validation = self.ai.validate_resume(job, master_resume, resume_text)

        if not bool(validation.get("approved", False)):
            raise RuntimeError(
                f"Resume validation failed for {job.get('company')} / "
                f"{job.get('title')}: "
                + "; ".join(validation.get("unsupported_claims", []))
            )

        resume_path = self.resume_engine.render_docx(
            resume_text,
            job.get("company", "company"),
            job.get("title", "role"),
            str(self.output_dir),
        )
        resume_text_path = Path(resume_path).with_suffix(".txt")
        resume_text_path.write_text(resume_text, encoding="utf-8")

        cover_letter = self.ai.generate_cover_letter(job, profile_json, resume_text)
        cover_path = Path(resume_path).with_name(
            Path(resume_path).stem.replace("_resume", "_cover_letter") + ".txt"
        )
        cover_path.write_text(cover_letter, encoding="utf-8")

        return {
            "resume_path": str(resume_path),
            "resume_text_path": str(resume_text_path),
            "cover_letter_path": str(cover_path),
            "resume": resume_text,
            "cover_letter": cover_letter,
            "resume_validation": validation,
        }

    def record_result(
        self,
        job: dict,
        prepared: dict,
        status: str,
        error: str | None = None,
    ) -> None:
        record_application(
            job,
            prepared.get("resume_path"),
            prepared.get("cover_letter_path"),
            status,
            error,
        )
