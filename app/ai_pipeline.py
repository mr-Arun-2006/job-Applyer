from __future__ import annotations

import json

from app.llm import LLMRouter


class JobAIPipeline:
    def __init__(self, router: LLMRouter | None = None):
        self.router = router or LLMRouter()

    def extract_job(self, raw_job_text: str, official_url: str = "") -> dict:
        return self.router.complete_json(
            "extract",
            """Extract only facts explicitly present in the source.
Return JSON with company, title, location, employment_type, description,
skills, official_url, application_url and posted_at.
Never invent missing values.""",
            f"OFFICIAL URL: {official_url}\n\nSOURCE TEXT:\n{raw_job_text}",
            temperature=0.0,
        )

    def analyze_job(self, job: dict) -> dict:
        return self.router.complete_json(
            "analyze",
            """Analyze the job for a candidate.
Return JSON with role_summary, responsibilities, requirements, skills,
must_have_skills, nice_to_have_skills and suitability_factors.
Do not invent requirements.""",
            json.dumps(job, ensure_ascii=False),
            temperature=0.1,
        )

    def match_job(self, job: dict, profile_json: str) -> dict:
        return self.router.complete_json(
            "match",
            """Match the job against the candidate profile.
Return JSON with score_0_100, matched_skills, missing_skills,
eligibility_risks, decision and rationale.
Never infer a qualification the profile does not state.""",
            f"JOB:\n{json.dumps(job, ensure_ascii=False)}\n\nPROFILE:\n{profile_json}",
            temperature=0.0,
        )

    def customize_resume_json(self, job: dict, profile_json: str, master_resume: str) -> str:
        return self.router.complete(
            "resume",
            """Create a truthful, job-specific resume from the supplied master resume.
You may reorder and rewrite existing facts for relevance.
Never fabricate skills, experience, education, certifications, dates, employers,
projects, achievements or metrics. Return resume text only.""",
            f"JOB:\n{json.dumps(job, ensure_ascii=False)}\n\nPROFILE:\n{profile_json}\n\nMASTER RESUME:\n{master_resume}",
            temperature=0.1,
            max_tokens=6000,
        )

    def generate_cover_letter(self, job: dict, profile_json: str, resume_text: str) -> str:
        return self.router.complete(
            "cover_letter",
            """Write a concise, truthful cover letter for this job.
Use only facts present in the profile and resume. Never invent qualifications,
experience or achievements. Return the letter only.""",
            f"JOB:\n{json.dumps(job, ensure_ascii=False)}\n\nPROFILE:\n{profile_json}\n\nRESUME:\n{resume_text}",
            temperature=0.2,
            max_tokens=1800,
        )

    def map_form(self, form_fields_json: str, profile_json: str, resume_text: str) -> dict:
        return self.router.complete_json(
            "form",
            """Map application fields to truthful candidate answers.
Return a JSON object mapping each field name to its value.
Unknown, ambiguous, sensitive, CAPTCHA, OTP/MFA and legal declarations
must be NEEDS_HUMAN_INPUT.""",
            f"FIELDS:\n{form_fields_json}\n\nPROFILE:\n{profile_json}\n\nRESUME:\n{resume_text}",
            temperature=0.0,
        )
