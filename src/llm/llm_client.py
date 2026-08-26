"""Der eine HTTP-Client für Ollama.

Seit P0.1 gibt es genau diesen. Vorher lag daneben ein zweiter
(`studio_helpers.LocalOllama`) mit gegenteiliger Fehlerphilosophie: derselbe
Ausfall verhielt sich je nach aktivem Client einmal laut und einmal leise.
Verbindlich ist die laute Variante — Retry mit Backoff, danach `RuntimeError`.
Wer bewusst ohne Sprachmodell rechnen will, nimmt `MockLLM`.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str = "http://127.0.0.1:11434"
    model: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int = 2048


class OllamaClient:
    def __init__(self, config: OllamaConfig | None = None) -> None:
        self.config = config or OllamaConfig()

    def call(self, prompt: str, *, system_prompt: str | None = None) -> str:
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
        if system_prompt:
            payload["system"] = system_prompt

        # Configurable timeouts/retries. Use env vars to tune behaviour if needed.
        try:
            read_timeout_base = float(os.environ.get("OLLAMA_READ_TIMEOUT", "120"))
        except ValueError:
            read_timeout_base = 120.0
        try:
            retries = int(os.environ.get("OLLAMA_RETRIES", "3"))
        except ValueError:
            retries = 3

        connect_timeout = 5.0
        resp = None
        last_exc: Exception | None = None
        for attempt in range(max(1, retries)):
            # exponential backoff for read timeout
            read_timeout = read_timeout_base * (2**attempt)
            timeout_tuple = (connect_timeout, read_timeout)
            try:
                resp = requests.post(url, json=payload, timeout=timeout_tuple)
                resp.raise_for_status()
                break
            except requests.exceptions.ReadTimeout as exc:
                last_exc = exc
                wait = min(5 * (attempt + 1), 30)
                logger.warning(
                    "LLM request read timed out after %ss (attempt %s/%s), retrying in %ss...",
                    read_timeout,
                    attempt + 1,
                    retries,
                    wait,
                )
                time.sleep(wait)
                continue
            except requests.exceptions.RequestException as exc:
                # For other request errors, fail fast with a clear message
                raise RuntimeError(
                    f"LLM request to {self.config.base_url} failed: {exc}. "
                    "Ensure Ollama is running, model is available, or configure --base-url."
                ) from exc

        if resp is None:
            raise RuntimeError(
                f"LLM request to {self.config.base_url} failed after {retries} attempts: {last_exc}. "
                "Ensure Ollama is running and model is ready, or increase OLLAMA_READ_TIMEOUT/OLLAMA_RETRIES."
            )

        data = resp.json()
        if isinstance(data, dict) and isinstance(data.get("response"), str):
            return data["response"]
        return json.dumps(data, ensure_ascii=True)
