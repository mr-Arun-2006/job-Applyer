from dataclasses import dataclass

@dataclass
class ApplicationResult:
    submitted: bool
    url: str
    message: str

class ApplicationEngine:
    """Application automation boundary.

    A site-specific Playwright adapter should be implemented only for permitted
    application flows. CAPTCHA, MFA and anti-bot challenges are human steps.
    """
    def prepare(self, job, resume_text: str):
        if not job.get("application_url"):
            raise ValueError("Job has no application URL")
        return {"url": job["application_url"], "resume": resume_text}

    def submit(self, prepared_application):
        raise NotImplementedError("Use a site-specific permitted adapter for submission")
