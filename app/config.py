import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MASTER_RESUME_PATH = os.getenv("MASTER_RESUME_PATH", "./private/master_resume.txt")
PROFILE_PATH = os.getenv("PROFILE_PATH", "./private/profile.json")
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "provider_01")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")


def available_providers(max_slots: int = 52) -> list[str]:
    return [f"provider_{i:02d}" for i in range(1, max_slots + 1) if os.getenv(f"PROVIDER_{i:02d}_BASE_URL") and os.getenv(f"PROVIDER_{i:02d}_API_KEY") and os.getenv(f"PROVIDER_{i:02d}_MODEL")]


def provider_config(name: str) -> dict[str, str]:
    key = name.upper().replace("-", "_")
    base_url = os.getenv(f"{key}_BASE_URL", "").rstrip("/")
    api_key = os.getenv(f"{key}_API_KEY", "")
    model = os.getenv(f"{key}_MODEL", "")
    if not base_url or not api_key or not model:
        raise RuntimeError(
            f"Incomplete configuration for {name}: expected {key}_BASE_URL, "
            f"{key}_API_KEY and {key}_MODEL"
        )
    return {"base_url": base_url, "api_key": api_key, "model": model}


STAGE_PROVIDERS = {
    "extract": os.getenv("MODEL_EXTRACT", DEFAULT_LLM_PROVIDER),
    "analyze": os.getenv("MODEL_ANALYZE", DEFAULT_LLM_PROVIDER),
    "match": os.getenv("MODEL_MATCH", DEFAULT_LLM_PROVIDER),
    "resume": os.getenv("MODEL_RESUME", DEFAULT_LLM_PROVIDER),
    "form": os.getenv("MODEL_FORM", DEFAULT_LLM_PROVIDER),
}
