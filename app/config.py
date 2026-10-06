from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MASTER_RESUME_PATH = os.getenv("MASTER_RESUME_PATH", "./private/master_resume.txt")
PROFILE_PATH = os.getenv("PROFILE_PATH", "./private/profile.json")
OFFICIAL_SOURCES_PATH = os.getenv(
    "OFFICIAL_SOURCES_PATH", "./config/company_sources.json"
)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./data/applications")
JOB_APPLIER_DB = os.getenv("JOB_APPLIER_DB", "./data/job_applyer.db")

DEFAULT_MODELS: dict[str, str] = {
    "extract": "openai/gpt-oss-20b",
    "analyze": "nvidia/nemotron-3-super-120b-a12b",
    "match": "openai/gpt-oss-20b",
    "resume": "openai/gpt-oss-120b",
    "cover_letter": "openai/gpt-oss-20b",
    "form": "openai/gpt-oss-20b",
    "resume_validate": "openai/gpt-oss-20b",
    "fallback": "deepseek-ai/deepseek-v4-flash",
}


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        f"Invalid boolean value for {name}: {value!r}. "
        "Use true/false, yes/no, on/off, or 1/0."
    )


def _env_int(name: str, default: int, minimum: int = 0) -> int:
    value = int(os.getenv(name, str(default)))
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value}.")
    return value


def _env_float(name: str, default: float, minimum: float, maximum: float | None = None) -> float:
    value = float(os.getenv(name, str(default)))
    if value < minimum or (maximum is not None and value > maximum):
        limit = f"{minimum}..{maximum}" if maximum is not None else f">={minimum}"
        raise ValueError(f"{name} must be {limit}, got {value}.")
    return value


MIN_MATCH_SCORE = _env_float("MIN_MATCH_SCORE", 50.0, 0.0, 100.0)
APPLY_TO_ALL_ELIGIBLE = _env_bool("APPLY_TO_ALL_ELIGIBLE", True)
MAX_DETAIL_PAGES_PER_SOURCE = _env_int("MAX_DETAIL_PAGES_PER_SOURCE", 200, 1)


def nvidia_api_key() -> str:
    key = os.getenv("NVIDIA_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "NVIDIA_API_KEY is not configured. Put it only in local .env."
        )
    return key


def model_for_stage(stage: str) -> str:
    env_name = f"MODEL_{stage.upper()}"
    return os.getenv(env_name, DEFAULT_MODELS.get(stage, DEFAULT_MODELS["fallback"]))


def available_models() -> dict[str, str]:
    return {
        stage: model_for_stage(stage)
        for stage in DEFAULT_MODELS
        if stage != "fallback"
    }


def validate_local_config() -> None:
    nvidia_api_key()

    for label, raw_path in {
        "master resume": MASTER_RESUME_PATH,
        "profile": PROFILE_PATH,
    }.items():
        path = Path(raw_path)
        if not path.is_file():
            raise RuntimeError(f"{label.title()} not found: {path}")
