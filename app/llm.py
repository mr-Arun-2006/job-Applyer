import httpx
from app.config import provider_config, STAGE_PROVIDERS


class LLMRouter:
    """Route each stage to its configured OpenAI-compatible provider/model."""

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout

    def provider_for(self, stage: str) -> str:
        return STAGE_PROVIDERS.get(stage, STAGE_PROVIDERS["analyze"])

    def complete(self, stage: str, system: str, user: str, temperature: float = 0.2) -> str:
        provider_name = self.provider_for(stage)
        cfg = provider_config(provider_name)
        response = httpx.post(
            f"{cfg['base_url']}/chat/completions",
            json={
                "model": cfg["model"],
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": temperature,
            },
            headers={"Authorization": f"Bearer {cfg['api_key']}"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
