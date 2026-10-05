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
MIN_MATCH_SCORE = float(os.getenv("MIN_MATCH_SCORE", "50"))
APPLY_TO_ALL_ELIGIBLE = os.getenv("APPLY_TO_ALL_ELIGIBLE", "true").lower() == "true"
MAX_DETAIL_PAGES_PER_SOURCE = int(os.getenv("MAX_DETAIL_PAGES_PER_SOURCE", "200"))

DEFAULT_MODELS = {
    "extract": "openai/gpt-oss-20b",
    "analyze": "z-ai/glm-5-3-flash",
    "match": "openai/gpt-oss-20b",
    "resume": "z-ai/glm-5-3",
    "cover_letter": "z-ai/glm-5-3-flash",
    "form": "openai/gpt-oss-20b",
    "fallback": "deepseek-ai/deepseek-v4.1-flash",
}


def nvidia_api_key() -> str:
    key = os.getenv("NVIDIA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("NVIDIA_API_KEY is not configured. Put it only in local .env.")
    return key


def model_for_stage(stage: str) -> str:
    env_name = f"MODEL_{stage.upper()}"
    return os.getenv(env_name, DEFAULT_MODELS.get(stage, DEFAULT_MODELS["fallback"]))


def available_models() -> dict[str, str]:
    return {stage: model_for_stage(stage) for stage in DEFAULT_MODELS if stage != "fallback"}


def validate_local_config() -> None:
    nvidia_api_key()
    if not Path(MASTER_RESUME_PATH).exists():
        raise RuntimeError(f"Master resume not found: {MASTER_RESUME_PATH}")
    if not Path(PROFILE_PATH).exists():
        raise RuntimeError(f"Profile file not found: {PROFILE_PATH}")
