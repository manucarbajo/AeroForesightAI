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
from dataclasses import dataclass, field
from typing import Any

import requests

from src.llm import defaults

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OllamaConfig:
    """Was der Client wissen muss — mit den Umgebungsvariablen **darin** (P3.4).

    Die vier Werte kommen aus :mod:`src.llm.defaults`, und die
    ``default_factory`` liest dabei die Umgebung. Das ist der eigentliche Fix:
    Vorher trug diese Klasse reine Literale, und die Env-Übersetzung saß
    ausschließlich in ``studio_helpers.LocalOllama``. Jeder Aufrufer, der
    ``OllamaConfig()`` direkt baute — der Sweep-Pfad tut genau das —, ignorierte
    ``OLLAMA_BASE_URL`` stillschweigend. Beim Nachstellen eines Sweeps gegen
    einen toten Endpunkt (2026-08-27) stand trotz ``OLLAMA_BASE_URL=…:9``
    weiterhin der Vorgabewert da.

    **Gelesen wird beim Bauen, nicht beim Importieren.** Ein Modul-Import darf
    nicht festlegen, was eine Stunde später gilt — und ein Test, der die
    Umgebung setzt, käme sonst zu spät.
    """

    base_url: str = field(default_factory=defaults.env_base_url)
    model: str = field(default_factory=defaults.env_model)
    temperature: float = field(default_factory=defaults.env_temperature)
    max_tokens: int = field(default_factory=defaults.env_max_tokens)
    #: Lesetimeout der ersten Runde in Sekunden. ``None`` heißt: aus
    #: ``OLLAMA_READ_TIMEOUT`` nehmen (Default 120). Explizit gesetzt, damit
    #: Aufrufer mit eigener Timeout-Quelle — `LocalOllama` liest
    #: ``OLLAMA_TIMEOUT_SECONDS`` — sie durchreichen können, statt sie still
    #: verfallen zu lassen.
    read_timeout: float | None = None


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
        if self.config.read_timeout is not None:
            read_timeout_base = float(self.config.read_timeout)
        else:
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
