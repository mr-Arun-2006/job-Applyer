from __future__ import annotations

import argparse
from pathlib import Path

from app.ai_pipeline import JobAIPipeline
from app.application_agent import ApplicationAgent
from app.config import (
    MASTER_RESUME_PATH,
    OFFICIAL_SOURCES_PATH,
    OUTPUT_DIR,
    PROFILE_PATH,
    available_models,
    validate_local_config,
)
from app.database import init_db, save_jobs
from app.discovery_engine import discover_official_source, scrape_public_job_page
from app.job_runner import JobRunner
from app.official_sources import load_official_sources


def load_profile() -> str:
    return Path(PROFILE_PATH).read_text(encoding="utf-8")


def load_resume() -> str:
    return Path(MASTER_RESUME_PATH).read_text(encoding="utf-8")


def discover_jobs(sources_path: str, ai: JobAIPipeline) -> list[dict]:
    sources = load_official_sources(sources_path)
    if not sources:
        raise SystemExit(
            f"No official sources configured. Copy the source template to "
            f"{sources_path} and add your target companies."
        )

    all_jobs: list[dict] = []
    for source in sources:
        all_jobs.extend(discover_official_source(source, ai))
    save_jobs(all_jobs)
    return all_jobs


def prepare_jobs(jobs: list[dict], ai: JobAIPipeline) -> list[dict]:
    profile = load_profile()
    resume = load_resume()
    runner = JobRunner(ai)
    eligible = runner.eligible_jobs(jobs, profile)

    print(f"Eligible jobs: {len(eligible)}")
    for index, job in enumerate(eligible, start=1):
        prepared = runner.prepare_application(job, profile, resume)
        job["resume_path"] = prepared["resume_path"]
        job["cover_letter_path"] = prepared["cover_letter_path"]
        runner.record_result(job, prepared, "READY_FOR_HUMAN_REVIEW")
        print(
            f"[{index}/{len(eligible)}] {job.get('company')} | "
            f"{job.get('title')} | score={job.get('match_score')} | "
            f"resume={prepared['resume_path']}"
        )
    return eligible


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Personal official-company Job-Applyer"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db")
    sub.add_parser("models")

    scrape = sub.add_parser("scrape")
    scrape.add_argument("url")

    discover = sub.add_parser("discover")
    discover.add_argument("--sources", default=OFFICIAL_SOURCES_PATH)

    prepare = sub.add_parser("prepare")
    prepare.add_argument("--sources", default=OFFICIAL_SOURCES_PATH)

    apply = sub.add_parser("apply")
    apply.add_argument("--sources", default=OFFICIAL_SOURCES_PATH)

    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
        print("Database initialized.")
        return

    if args.command == "models":
        for stage, model in available_models().items():
            print(f"{stage}: {model}")
        return

    if args.command == "scrape":
        result = scrape_public_job_page(args.url)
        print(result["text"])
        return

    validate_local_config()
    init_db()

    ai = JobAIPipeline()
    jobs = discover_jobs(args.sources, ai)
    print(f"Discovered {len(jobs)} jobs from configured official sources.")

    if args.command == "discover":
        return

    eligible = prepare_jobs(jobs, ai)
    print(f"Prepared files under {OUTPUT_DIR}.")

    if args.command == "prepare":
        print("No application submission performed.")
        return

    profile = load_profile()
    agent = ApplicationAgent(ai)
    results = agent.run_all(
        eligible,
        profile,
    )

    runner = JobRunner(ai)
    for job, status in results:
        prepared = {
            "resume_path": job.get("resume_path"),
            "cover_letter_path": job.get("cover_letter_path"),
        }
        mapped_status = "SUBMITTED" if status == "SUBMITTED" else status
        runner.record_result(job, prepared, mapped_status, None if status == "SUBMITTED" else status)
        print(f"{job.get('company')} | {job.get('title')} | {status}")

    print("Application run completed.")
    print("CAPTCHA/MFA/OTP/human-only controls are never bypassed.")


if __name__ == "__main__":
    main()
