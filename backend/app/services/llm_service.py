import logging
from typing import Optional

import httpx

from app.config import Settings


logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, settings: Settings):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    async def generate(self, prompt: str) -> Optional[str]:
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

            data = response.json()
            answer = data.get("response", "").strip()

            return answer or None
        except Exception:
            logger.warning(
                "Ollama is not available at %s using model %s.",
                self.base_url,
                self.model,
            )
            return None