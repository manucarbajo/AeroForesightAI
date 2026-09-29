"""LLM backend selection and HTTP clients (Ollama, local/mocked fallbacks)."""

from src.llm.llm_client import OllamaClient, OllamaConfig
from src.llm.sprache import AUSGABESPRACHE, auf_deutsch
from src.llm.studio_helpers import (
    STUDIO_DIR,
    LLMCallable,
    LocalLlamaHTTP,
    LocalLlamaTransformers,
    LocalOllama,
    MockLLM,
    get_llm,
    load_env,
)

__all__ = [
    "AUSGABESPRACHE",
    "auf_deutsch",
    "OllamaClient",
    "OllamaConfig",
    "STUDIO_DIR",
    "LLMCallable",
    "LocalLlamaHTTP",
    "LocalLlamaTransformers",
    "LocalOllama",
    "MockLLM",
    "get_llm",
    "load_env",
]
