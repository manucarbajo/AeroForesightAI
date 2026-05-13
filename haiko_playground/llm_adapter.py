"""LLM-Adapter für LangGraph-Projekt.

Reihenfolge:
1) Ollama (OLLAMA_MODEL, optional OLLAMA_BASE_URL)
2) Generic HTTP-API (LLAMA_HTTP_URL)
3) transformers pipeline (LLAMA_TRANSFORMERS_MODEL)
4) Mock
"""
from __future__ import annotations

import os
import json
from typing import Protocol

import requests


class LLMCallable(Protocol):
    def call(self, prompt: str) -> str:
        ...


class LocalOllama:
    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        self.model = model or os.environ.get("OLLAMA_MODEL")
        if not self.model:
            raise RuntimeError("OLLAMA_MODEL nicht gesetzt")

        base = base_url or os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
        self.url = base.rstrip("/") + "/api/generate"

    def call(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        resp = requests.post(self.url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        # Ollama returns response in `response` for non-streaming generate.
        return str(data.get("response") or data.get("text") or data.get("output") or json.dumps(data))


class LocalLlamaHTTP:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or os.environ.get("LLAMA_HTTP_URL")
        if not self.url:
            raise RuntimeError("LLAMA_HTTP_URL nicht gesetzt")

    def call(self, prompt: str) -> str:
        payload = {"prompt": prompt}
        resp = requests.post(self.url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # akzeptiere sowohl {"text": "..."} als auch {"output": "..."}
        return str(data.get("text") or data.get("output") or json.dumps(data))


class LocalLlamaTransformers:
    def __init__(self, model_name: str | None = None) -> None:
        try:
            from transformers import pipeline
        except Exception as e:
            raise RuntimeError("transformers nicht installiert") from e
        model_name = model_name or os.environ.get("LLAMA_TRANSFORMERS_MODEL")
        if not model_name:
            raise RuntimeError("LLAMA_TRANSFORMERS_MODEL nicht gesetzt")
        self._pipe = pipeline("text-generation", model=model_name)

    def call(self, prompt: str) -> str:
        out = self._pipe(prompt, max_new_tokens=512)
        if isinstance(out, list) and out:
            return out[0].get("generated_text", "")
        return str(out)


class MockLLM:
    def call(self, prompt: str) -> str:
        # Sehr einfacher Mock für Tests
        return json.dumps({
            "reasoning": "mock",
            "actions": ["NO_OP"],
            "state_changes": [],
            "events": [],
            "segment_analysis": {},
        })


def get_llm() -> LLMCallable:
    # Bevorzugt Ollama, dann HTTP, dann transformers, sonst Mock
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
