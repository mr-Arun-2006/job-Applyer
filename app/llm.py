from __future__ import annotations

import json
import os
import time

import httpx

from app.config import model_for_stage, nvidia_api_key


class LLMRouter:
    """NVIDIA hosted-model router using one NVIDIA API key."""

    def __init__(self, timeout: float = 90.0, retries: int = 2):
        self.timeout = timeout
        self.retries = retries
        self.base_url = os.getenv(
            "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
        ).rstrip("/")

    def model_for(self, stage: str) -> str:
        return model_for_stage(stage)

    def complete(
        self,
        stage: str,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        payload = {
            "model": self.model_for(stage),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = httpx.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {nvidia_api_key()}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                if not isinstance(content, str) or not content.strip():
                    raise RuntimeError("NVIDIA returned an empty model response.")
                return content.strip()
            except (httpx.HTTPError, KeyError, TypeError, RuntimeError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(1.5 * (attempt + 1))

        raise RuntimeError(
            f"NVIDIA model request failed after retries: {last_error}"
        ) from last_error

    def complete_json(
        self,
        stage: str,
        system: str,
        user: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> dict:
        raw = self.complete(
            stage,
            system,
            user,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        cleaned = raw.strip()
        fence = chr(96) * 3
        if cleaned.startswith(fence):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith(fence):
                lines = lines[1:]
            if lines and lines[-1].strip() == fence:
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            value = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Model returned invalid JSON for stage '{stage}'."
            ) from exc

        if not isinstance(value, dict):
            raise TypeError(
                f"Model returned non-object JSON for stage '{stage}'."
            )
        return value
