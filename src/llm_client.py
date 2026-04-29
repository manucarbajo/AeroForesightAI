from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int = 2048


class OllamaClient:
    def __init__(self, config: OllamaConfig | None = None) -> None:
        self.config = config or OllamaConfig()

    def call(self, prompt: str) -> str:
        url = f"{self.config.base_url}/api/generate"
        payload: dict[str, Any] = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            },
        }

        resp = requests.post(url, json=payload, timeout=300)
        resp.raise_for_status()

        data = resp.json()
        if isinstance(data, dict) and isinstance(data.get("response"), str):
            return data["response"]
        return json.dumps(data, ensure_ascii=True)

