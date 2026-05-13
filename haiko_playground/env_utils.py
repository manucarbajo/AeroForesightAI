"""Environment helpers: load .env and prompt for missing secrets at runtime.

Behavior:
- Loads environment variables from `haiko_playground/.env` if present (uses python-dotenv when available).
- For a small set of secret keys (e.g. `LANGSMITH_API_KEY`) if the variable is missing/empty, prompts the user via getpass and sets it in `os.environ` for the running process only.

This keeps secrets out of source control and avoids writing back to the .env file.
"""
from __future__ import annotations

import os
from pathlib import Path
from getpass import getpass
from typing import Iterable


def _load_dotenv(path: Path) -> None:
    try:
        from dotenv import load_dotenv

        # override=True ensures values from .env replace empty inherited env vars
        load_dotenv(dotenv_path=str(path), override=True)
        return
    except Exception:
        # fallback: simple parse
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if v:
                        os.environ[k] = v
        except FileNotFoundError:
            return


def load_env(env_path: str | None = None, prompt_keys: Iterable[str] | None = None) -> None:
    """Load .env file and interactively prompt for missing secret keys.

    - `env_path`: path to .env file (defaults to `haiko_playground/.env`).
    - `prompt_keys`: iterable of env var names to prompt for if missing/empty.
    """
    root = Path(__file__).resolve().parent
    env_file = Path(env_path) if env_path else root / ".env"

    if env_file.exists():
        _load_dotenv(env_file)

    # Default: only prompt for LANGSMITH_API_KEY (a secret).
    # LLM config (LLAMA_HTTP_URL, LLAMA_TRANSFORMERS_MODEL) should come from .env, not prompts.
    keys = list(prompt_keys or ["LANGSMITH_API_KEY"])
    for key in keys:
        val = os.environ.get(key)
        if val is None or str(val).strip() == "":
            try:
                # Use getpass for API keys to hide input.
                if key.endswith("API_KEY") or key.endswith("SECRET"):
                    entered = getpass(f"Enter value for {key} (hidden): ")
                else:
                    entered = input(f"Enter value for {key} (leave empty to skip): ")
            except (EOFError, KeyboardInterrupt):
                entered = ""
            if entered:
                os.environ[key] = entered
