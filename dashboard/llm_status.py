"""Ist Ollama erreichbar, und welche Modelle liegen dort?

Die Oberfläche bietet an, mit einem Sprachmodell zu rechnen. Ob das im Moment
überhaupt geht, konnte man bisher erst daran merken, dass ein Lauf nach
Minuten abbrach. Diese Abfrage beantwortet die Frage vorher.

Bewusst ohne Oberflächen-Bezug — wie die übrigen Module unter `dashboard/`.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

#: Wie lange eine Antwort auf sich warten lassen darf.
#:
#: Nicht zu knapp: Unter Windows loest `localhost` zuerst auf `::1` auf. Lauscht
#: Ollama nur auf IPv4, laeuft dieser Versuch erst in einen Timeout — gemessen
#: rund zwei Sekunden, bevor ueberhaupt die richtige Adresse probiert wird. Ein
#: kuerzerer Wert meldet einen laufenden Dienst faelschlich als tot.
TIMEOUT_SECONDS = 5.0

#: Wie lange eine Auskunft wiederverwendet wird. Ollama startet und stoppt
#: nicht im Sekundentakt; öfter zu fragen kostet nur Zeit.
CACHE_SECONDS = 30.0


@dataclass(frozen=True)
class OllamaStatus:
    base_url: str
    reachable: bool
    models: tuple[str, ...] = field(default_factory=tuple)
    detail: str = ""

    def has_model(self, name: str) -> bool:
        """Ollama führt Modelle als `llama3.2:latest`; angegeben wird `llama3.2`."""

        if not name:
            return False
        wanted = name.split(":")[0]
        return any(model.split(":")[0] == wanted for model in self.models)


_cache: dict[str, tuple[float, OllamaStatus]] = {}


def check(base_url: str, *, force: bool = False) -> OllamaStatus:
    """Erreichbarkeit abfragen, höchstens alle `CACHE_SECONDS` erneut."""

    url = (base_url or "").rstrip("/")
    if not url:
        return OllamaStatus(base_url="", reachable=False, detail="Keine Adresse angegeben.")

    now = time.monotonic()
    cached = _cache.get(url)
    if cached and not force and now - cached[0] < CACHE_SECONDS:
        return cached[1]

    status = _query(url)
    _cache[url] = (now, status)
    return status


def _query(url: str) -> OllamaStatus:
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read())
    except urllib.error.URLError as exc:
        return OllamaStatus(base_url=url, reachable=False, detail=f"Nicht erreichbar: {exc.reason}")
    except Exception as exc:  # noqa: BLE001 - jede Störung heißt hier schlicht «geht nicht»
        return OllamaStatus(base_url=url, reachable=False, detail=str(exc))

    models = tuple(
        str(item.get("name"))
        for item in (payload.get("models") or [])
        if isinstance(item, dict) and item.get("name")
    )
    return OllamaStatus(base_url=url, reachable=True, models=models)


def reset_cache() -> None:
    """Zwischenspeicher leeren — für Tests und nach einer Adressänderung."""

    _cache.clear()
