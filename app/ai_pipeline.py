from app.llm import LLMRouter


class JobAIPipeline:
    def __init__(self, router: LLMRouter | None = None):
        self.router = router or LLMRouter()

    def extract(self, raw_job_text: str) -> str:
        return self.router.complete(
            "extract",
            "Extract job data. Return valid JSON only. Never invent missing facts.",
            raw_job_text,
        )

    def analyze(self, job_json: str) -> str:
        return self.router.complete(
            "analyze",
            "Analyze the role. Return JSON with role_summary, responsibilities, requirements, skills and suitability_factors.",
            job_json,
        )

    def match(self, job_json: str, profile_json: str) -> str:
        return self.router.complete(
            "match",
            "Match the job to the candidate. Never infer qualifications. Return JSON with score_0_100, matched_skills, missing_skills and decision.",
            f"JOB:\n{job_json}\n\nPROFILE:\n{profile_json}",
        )

    def customize_resume(self, job_json: str, profile_json: str, master_resume: str) -> str:
        return self.router.complete(
            "resume",
            "Customize the resume truthfully. Never fabricate experience, education, projects, certifications, dates, metrics or skills. Return resume text only.",
            f"JOB:\n{job_json}\n\nPROFILE:\n{profile_json}\n\nMASTER RESUME:\n{master_resume}",
            temperature=0.1,
        )

    def map_form(self, form_fields_json: str, profile_json: str, resume_text: str) -> str:
        return self.router.complete(
            "form",
            "Map fields to truthful candidate answers. Return JSON. Unknown or sensitive fields must be NEEDS_HUMAN_INPUT.",
            f"FIELDS:\n{form_fields_json}\n\nPROFILE:\n{profile_json}\n\nRESUME:\n{resume_text}",
            temperature=0.0,
        )
