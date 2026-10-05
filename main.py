from __future__ import annotations

import argparse
from pathlib import Path

from app.ai_pipeline import JobAIPipeline
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

    sources = load_official_sources(args.sources)
    if not sources:
        raise SystemExit(
            f"No official sources configured. Copy the source template to "
            f"{args.sources} and add your target companies."
        )

    ai = JobAIPipeline()
    all_jobs: list[dict] = []
    for source in sources:
        all_jobs.extend(discover_official_source(source, ai))

    inserted = save_jobs(all_jobs)
    print(f"Discovered {len(all_jobs)} jobs; stored {inserted} new jobs.")

    if args.command == "discover":
        return

    profile = load_profile()
    runner = JobRunner(ai)
    eligible = runner.eligible_jobs(all_jobs, profile)
    print(f"Eligible jobs: {len(eligible)}")

    resume = load_resume()
    for index, job in enumerate(eligible, start=1):
        prepared = runner.prepare_application(job, profile, resume)
        runner.record_result(job, prepared, "READY_FOR_HUMAN_REVIEW")
        print(
            f"[{index}/{len(eligible)}] {job.get('company')} | "
            f"{job.get('title')} | score={job.get('match_score')} | "
            f"resume={prepared['resume_path']}"
        )

    print(f"Prepared files under {OUTPUT_DIR}.")
    print(
        "No automatic submission is performed by prepare. "
        "CAPTCHA/MFA/OTP/human-only steps remain manual."
    )


if __name__ == "__main__":
    main()
