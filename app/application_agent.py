from __future__ import annotations

import json

from playwright.sync_api import BrowserContext, Page, sync_playwright

from app.ai_pipeline import JobAIPipeline
from app.form_agent import FormAgent
from app.resume_engine import ATSResumeEngine


class ApplicationAgent:
    """Fill ordinary application fields and require human confirmation to submit."""

    def __init__(self, ai: JobAIPipeline | None = None):
        self.ai = ai or JobAIPipeline()
        self.form_agent = FormAgent()

    @staticmethod
    def inspect_form(page: Page) -> list[dict]:
        fields = []
        for locator in page.locator("input, textarea, select").all():
            try:
                name = locator.get_attribute("name") or ""
                field_type = locator.get_attribute("type") or "text"
                if field_type.lower() == "hidden" or not name:
                    continue
                label = ""
                field_id = locator.get_attribute("id")
                if field_id:
                    label_locator = page.locator(f'label[for="{field_id}"]')
                    if label_locator.count():
                        label = label_locator.first.inner_text().strip()
                fields.append(
                    {
                        "name": name,
                        "id": field_id,
                        "type": field_type,
                        "label": label,
                    }
                )
            except Exception:
                continue
        return fields

    def run_one(
        self,
        context: BrowserContext,
        job: dict,
        profile_json: str,
        resume_path: str,
    ) -> str:
        application_url = job.get("application_url") or job.get("official_url")
        if not application_url:
            return "SKIPPED_NO_APPLICATION_URL"

        page = context.new_page()
        try:
            page.goto(application_url, wait_until="domcontentloaded", timeout=60000)
            fields = self.inspect_form(page)
            answers = self.ai.map_form(
                json.dumps(fields, ensure_ascii=False),
                profile_json,
                ATSResumeEngine.extract_text(resume_path),
            )

            for field in fields:
                name = field["name"]
                answer = answers.get(name)
                if not isinstance(answer, str) or answer == "NEEDS_HUMAN_INPUT":
                    continue
                if field["type"].lower() in {"file", "submit", "button", "checkbox", "radio"}:
                    if field["type"].lower() == "file" and any(
                        token in name.lower()
                        for token in ("resume", "cv", "curriculum")
                    ):
                        page.locator(f'[name="{name}"]').first.set_input_files(resume_path)
                    continue
                locator = page.locator(f'[name="{name}"]').first
                if locator.count():
                    try:
                        locator.fill(answer)
                    except Exception:
                        pass

            print(f"Ready for human review: {job.get('company')} | {job.get('title')}")
            print(f"Application URL: {application_url}")
            confirmation = input(
                "Type SUBMIT to submit this application, or SKIP to continue: "
            ).strip().upper()
            if confirmation != "SUBMIT":
                return "SKIPPED_BY_HUMAN"

            page.get_by_role("button", name="submit").first.click()
            return "SUBMITTED"
        except Exception as exc:
            return f"ERROR: {exc}"
        finally:
            page.close()

    def run_all(
        self,
        jobs: list[dict],
        profile_json: str,
        browser_profile_dir: str = "./data/browser_profile",
    ) -> list[tuple[dict, str]]:
        results = []
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                browser_profile_dir,
                headless=False,
            )
            try:
                for job in jobs:
                    resume_path = job.get("resume_path")
                    if not resume_path:
                        results.append((job, "SKIPPED_NO_RESUME"))
                        continue
                    result = self.run_one(
                        context,
                        job,
                        profile_json,
                        str(resume_path),
                    )
                    results.append((job, result))
            finally:
                context.close()
        return results
