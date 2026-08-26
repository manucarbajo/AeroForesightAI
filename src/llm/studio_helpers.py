"""Shared Studio helpers for LangGraph Studio and the CLI entrypoint."""

from __future__ import annotations

import json
import os
import re
import sys
from getpass import getpass
from pathlib import Path
from typing import Iterable, Protocol

import requests


class LLMCallable(Protocol):
    def call(self, prompt: str) -> str: ...


def _load_dotenv(path: Path) -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=str(path), override=True)
        return
    except Exception:
        try:
            with path.open("r", encoding="utf-8") as file_handle:
                for line in file_handle:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if value:
                        os.environ[key] = value
        except FileNotFoundError:
            return


STUDIO_DIR = Path(__file__).resolve().parents[2] / "langgraph_studio"


def load_env(env_path: str | None = None, prompt_keys: Iterable[str] | None = None) -> None:
    """Load .env file and prompt for missing secrets when needed."""

    env_file = Path(env_path) if env_path else STUDIO_DIR / ".env"

    if env_file.exists():
        _load_dotenv(env_file)

    tracing_enabled = os.environ.get("LANGCHAIN_TRACING_V2", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    default_keys = ["LANGSMITH_API_KEY"] if tracing_enabled else []
    keys = list(prompt_keys if prompt_keys is not None else default_keys)
    if not keys or not sys.stdin.isatty():
        return

    for key in keys:
        value = os.environ.get(key)
        if value is not None and str(value).strip() != "":
            continue
        try:
            if key.endswith("API_KEY") or key.endswith("SECRET"):
                entered = getpass(f"Enter value for {key} (hidden): ")
            else:
                entered = input(f"Enter value for {key} (leave empty to skip): ")
        except (EOFError, KeyboardInterrupt):
            entered = ""
        if entered:
            os.environ[key] = entered


def _build_mock_response(prompt: str) -> str:
    if "Zu bewertende Paare" in prompt and "→" in prompt:
        pairs: list[tuple[str, str]] = []
        for line in prompt.splitlines():
            line = line.strip()
            if not line.startswith("- "):
                continue
            match = re.match(r"^-\s*(F\d+\.\d+)\s*→\s*(F\d+\.\d+)\s*$", line)
            if match:
                pairs.append((match.group(1), match.group(2)))

        return json.dumps(
            [
                {
                    "source": source,
                    "target": target,
                    "influence": 0,
                    "reasoning": "mock-neutral",
                }
                for source, target in pairs
            ],
            ensure_ascii=False,
        )

    return json.dumps(
        {
            "reasoning": "mock",
            "actions": ["NO_OP"],
            "state_changes": [],
            "events": [],
            "segment_analysis": {},
        }
    )


class LocalOllama:
    """Ollama-Backend, konfiguriert über Umgebungsvariablen.

    Seit P0.1 nur noch die Env-Übersetzung: gerechnet wird in `OllamaClient`.
    Vorher hatte diese Klasse eine eigene HTTP-Schleife, die bei jedem
    Netzwerkfehler still `_build_mock_response` zurückgab — eine erfundene
    Antwort, die im Output von einer echten nicht zu unterscheiden war. Genau
    dieser Zweig ist entfallen; ein Ausfall wirft jetzt, wie überall sonst.
    """

    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        model_name = model or os.environ.get("OLLAMA_MODEL")
        if not model_name:
            raise RuntimeError("OLLAMA_MODEL nicht gesetzt")
        self.model = model_name

        base = base_url or os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
        self.base_url = base.rstrip("/")
        self.url = self.base_url + "/api/generate"
        try:
            self.temperature = float(os.environ.get("OLLAMA_TEMPERATURE", "0.7"))
        except ValueError:
            self.temperature = 0.7
        try:
            self.max_tokens = int(os.environ.get("OLLAMA_MAX_TOKENS", "2048"))
        except ValueError:
            self.max_tokens = 2048
        self.system_prompt = os.environ.get("OLLAMA_SYSTEM_PROMPT")
        try:
            self.request_timeout = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "180"))
        except ValueError:
            self.request_timeout = 180.0

    def call(self, prompt: str) -> str:
        from src.llm.llm_client import OllamaClient, OllamaConfig

        client = OllamaClient(
            OllamaConfig(
                base_url=self.base_url,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        )
        return client.call(prompt, system_prompt=self.system_prompt)


class LocalLlamaHTTP:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or os.environ.get("LLAMA_HTTP_URL")
        if not self.url:
            raise RuntimeError("LLAMA_HTTP_URL nicht gesetzt")

    def call(self, prompt: str) -> str:
        response = requests.post(self.url, json={"prompt": prompt}, timeout=30)
        response.raise_for_status()
        data = response.json()
        return str(data.get("text") or data.get("output") or json.dumps(data))


class LocalLlamaTransformers:
    def __init__(self, model_name: str | None = None) -> None:
        try:
            from transformers import pipeline
        except Exception as exc:
            raise RuntimeError("transformers nicht installiert") from exc

        model_name = model_name or os.environ.get("LLAMA_TRANSFORMERS_MODEL")
        if not model_name:
            raise RuntimeError("LLAMA_TRANSFORMERS_MODEL nicht gesetzt")
        self._pipe = pipeline("text-generation", model=model_name)

    def call(self, prompt: str) -> str:
        output = self._pipe(prompt, max_new_tokens=512)
        if isinstance(output, list) and output:
            return output[0].get("generated_text", "")
        return str(output)


class MockLLM:
    def call(self, prompt: str) -> str:
        return _build_mock_response(prompt)


def get_llm() -> LLMCallable:
    """Select the best available LLM backend for Studio and playground runs."""

    omodel = os.environ.get("OLLAMA_MODEL")
    if omodel:
        return LocalOllama(model=omodel, base_url=os.environ.get("OLLAMA_BASE_URL"))

    http_url = os.environ.get("LLAMA_HTTP_URL")
    if http_url:
        return LocalLlamaHTTP(http_url)

    tmodel = os.environ.get("LLAMA_TRANSFORMERS_MODEL")
    if tmodel:
        return LocalLlamaTransformers(tmodel)

    return MockLLM()
