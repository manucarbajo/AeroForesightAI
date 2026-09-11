"""Shared Studio helpers for LangGraph Studio and the CLI entrypoint."""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from getpass import getpass
from pathlib import Path
from typing import Iterable, Protocol

import requests

from src.llm import defaults

logger = logging.getLogger(__name__)


class LLMCallable(Protocol):
    """Was ein Sprachmodell für diese Engine können muss: einen Prompt beantworten.

    **Die eine Definition** (P5.1, 2026-09-11). Bis dahin stand dasselbe Protokoll
    in sieben Modulen — strukturell gleich und deshalb ohne Laufzeitfehler, aber
    eine Signatur, die an einer Stelle geändert wird, wäre an sechs anderen still
    stehen geblieben. Gehalten von `tests/test_ein_name_eine_klasse.py`.
    """

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
        # **Die Env-Übersetzung liegt seit P3.4 in `OllamaConfig`**, nicht mehr
        # hier. Sie war der Grund, warum `OLLAMA_BASE_URL` für jeden Aufrufer
        # wirkungslos blieb, der seinen Client direkt baut — der Sweep-Pfad tut
        # genau das. Was hier bleibt, ist der Unterschied zum allgemeinen Fall:
        # Diese Klasse **verlangt** ein Modell, weil `get_llm()` sie nur wählt,
        # wenn eines genannt ist. Ein Vorgabewert wäre hier eine Anmaßung.
        model_name = model or os.environ.get("OLLAMA_MODEL", "").strip()
        if not model_name:
            raise RuntimeError("OLLAMA_MODEL nicht gesetzt")
        self.model = model_name

        self.base_url = (base_url or defaults.env_base_url()).rstrip("/")
        self.url = self.base_url + "/api/generate"
        self.temperature = defaults.env_temperature()
        self.max_tokens = defaults.env_max_tokens()
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
                # `OLLAMA_TIMEOUT_SECONDS` ist die Timeout-Quelle dieser Klasse.
                # Ohne diese Zeile läse `__init__` sie weiter aus und niemand
                # benutzte sie — ein totes Attribut und eine still wirkungslose
                # Umgebungsvariable.
                read_timeout=self.request_timeout,
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


#: Die Umgebungsvariable, mit der man den Mock **anfordert** (P3.4).
#:
#: Nötig, weil `get_llm()` keine Argumente durchreichen kann: Seine Aufrufer
#: sind der Studio-Graph und die Szenario-CLI, und beide bauen ihn ohne
#: Parameter. Ein Schalter im Aufruf hätte also niemanden erreicht.
MOCK_ENV = "AEROFORESIGHT_MOCK_LLM"


def get_llm(*, mock: bool = False) -> LLMCallable:
    """Das Backend für Studio- und Playground-Läufe — **und es sagt, welches** (P3.4).

    **Der Griff zum Mock war der letzte Zweig einer `if`-Kette.** War weder
    ``OLLAMA_MODEL`` noch ``LLAMA_HTTP_URL`` noch ``LLAMA_TRANSFORMERS_MODEL``
    gesetzt, gab diese Funktion kommentarlos ein ``MockLLM()`` zurück. Wer Studio
    ohne gesetzte Umgebung startete, bekam **erfundene Agenten-Antworten, ohne
    sie angefordert zu haben** — kein `--mock-llm`, kein Hinweis, und nach der
    Definition aus Invariante 1 auch kein «Ausfall», weil nie ein Aufruf
    gescheitert ist. P0.1 hat den stillen Mock *bei Fehlern* beseitigt; die
    Auswahl davor blieb.

    **Was jetzt gilt:** Der Mock kommt nur auf ausdrückliche Ansage — über
    ``mock=True`` oder :data:`MOCK_ENV`. Ohne Ansage und ohne konfiguriertes
    Backend wird nichts erfunden, sondern gescheitert. Und jede Wahl steht im
    Log: Ein Lauf, dessen Backend man nicht mehr feststellen kann, ist genau der
    Zustand, den Invariante 1 verhindern soll.

    Der bewusste Mock ist davon unberührt und richtig so: ``--mock-llm`` auf der
    CLI und «Ohne Sprachmodell» im Dashboard bauen ``MockLLM()`` direkt und gehen
    an dieser Auswahl vorbei.
    """

    if mock or os.environ.get(MOCK_ENV, "").strip().lower() in {"1", "true", "yes", "on"}:
        logger.info("LLM-Backend: MockLLM (ausdrücklich angefordert)")
        return MockLLM()

    omodel = os.environ.get("OLLAMA_MODEL")
    if omodel:
        logger.info("LLM-Backend: Ollama, Modell %s", omodel)
        return LocalOllama(model=omodel, base_url=os.environ.get("OLLAMA_BASE_URL"))

    http_url = os.environ.get("LLAMA_HTTP_URL")
    if http_url:
        logger.info("LLM-Backend: HTTP-Endpunkt %s", http_url)
        return LocalLlamaHTTP(http_url)

    tmodel = os.environ.get("LLAMA_TRANSFORMERS_MODEL")
    if tmodel:
        logger.info("LLM-Backend: transformers, Modell %s", tmodel)
        return LocalLlamaTransformers(tmodel)

    raise RuntimeError(
        "Kein Sprachmodell konfiguriert. Eine dieser Variablen setzen: "
        f"OLLAMA_MODEL, LLAMA_HTTP_URL, LLAMA_TRANSFORMERS_MODEL — oder {MOCK_ENV}=1, "
        "um ausdrücklich mit erfundenen Antworten zu rechnen. "
        "Bis P3.4 wurde hier stillschweigend der Mock gewählt: Ein Lauf sah "
        "vollwertig aus und war es nicht."
    )
