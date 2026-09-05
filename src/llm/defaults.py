"""Die **eine** Quelle für Modellname, Endpunkt, Temperatur und Antwortlänge (P3.4).

Bis zum 2026-09-05 standen diese vier Werte als Literale in **neun**
Produktionsdateien, der Endpunkt zusätzlich in zwei Schreibweisen:
``http://localhost:11434`` in fünf und ``http://127.0.0.1:11434`` in zwei
Dateien. Ein Endpunktwechsel war damit eine Suche über das ganze Repo, und das
Finding wuchs mit jedem neuen Modul weiter — die beim Dash-Umbau *neu*
entstandenen ``config_editor``-Module hatten die Hartkodierung geerbt.

**Der Endpunkt ist jetzt `127.0.0.1` und nicht `localhost`**, und das ist keine
Kosmetik: `localhost` löst auf manchen Windows-Installationen zuerst nach `::1`
auf, während Ollama nur auf IPv4 lauscht — der Aufruf läuft dann in einen
Verbindungsfehler, den niemand dem Namen ansieht. Beide Schreibweisen
gleichzeitig zu führen war ohnehin eine Quelle zu viel.

**Umgebungsvariablen gehören zur Quelle, nicht daneben.** Sie werden in
:class:`~src.llm.llm_client.OllamaConfig` selbst gelesen — vorher saß die
Übersetzung ausschließlich in ``studio_helpers.LocalOllama``, und jeder
Aufrufer, der ``OllamaConfig()`` direkt baute (der Sweep-Pfad tut genau das),
ignorierte ``OLLAMA_BASE_URL`` und die übrigen stillschweigend. Eine Variable zu
setzen und nichts zu bewirken ist dieselbe Klasse von Problem wie die
hartkodierten Werte selbst.

**Was hier nicht steht:** die Timeouts (``OLLAMA_READ_TIMEOUT``,
``OLLAMA_RETRIES``, ``OLLAMA_TIMEOUT_SECONDS``). Sie beschreiben nicht *welches
Modell wie antwortet*, sondern *wie lange der Client wartet* — sie gehören zum
HTTP-Verhalten und werden in ``llm_client`` gelesen, wo dieses Verhalten lebt.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

#: Das Modell, mit dem gerechnet wird, wenn niemand eines nennt.
DEFAULT_MODEL = "llama3.2"

#: Der Endpunkt eines lokal laufenden Ollama. **IPv4 ausdrücklich** — siehe der
#: Absatz zu `localhost` im Modul-Docstring.
DEFAULT_BASE_URL = "http://127.0.0.1:11434"

#: Kreativität. 0 heißt reproduzierbar, 2 ist die Obergrenze, die
#: `validation.validate_llm_settings` durchlässt.
DEFAULT_TEMPERATURE = 0.7

#: Antwortlänge in Tokens.
DEFAULT_MAX_TOKENS = 2048

#: Umgebungsvariable → welchen Wert sie überschreibt. Steht als Daten da, damit
#: die Doku und `tests/test_llm_defaults.py` dieselbe Liste benutzen wie der
#: Code, statt sie nachzuführen.
ENV_KEYS = {
    "OLLAMA_BASE_URL": "base_url",
    "OLLAMA_MODEL": "model",
    "OLLAMA_TEMPERATURE": "temperature",
    "OLLAMA_MAX_TOKENS": "max_tokens",
}


def env_base_url() -> str:
    return _text("OLLAMA_BASE_URL", DEFAULT_BASE_URL)


def env_model() -> str:
    return _text("OLLAMA_MODEL", DEFAULT_MODEL)


def env_temperature() -> float:
    return _zahl("OLLAMA_TEMPERATURE", DEFAULT_TEMPERATURE, float)


def env_max_tokens() -> int:
    return _zahl("OLLAMA_MAX_TOKENS", DEFAULT_MAX_TOKENS, int)


def _text(name: str, rueckfall: str) -> str:
    wert = os.environ.get(name, "").strip()
    return wert or rueckfall


def _zahl(name: str, rueckfall: float | int, typ: type) -> float | int:
    """Eine Zahl aus der Umgebung — und ein **Hinweis**, wenn sie keine ist.

    Bis P3.4 verschluckte `LocalOllama` einen Tippfehler wie
    ``OLLAMA_TEMPERATURE=0,7`` still und rechnete mit 0,7. Das Ergebnis war
    zufällig richtig, die Zusage nicht: Wer ``2,0`` schrieb, bekam ebenso 0,7
    und keinen Hinweis. Der Rückfall bleibt — ein Lauf soll an einer Kommazahl
    nicht scheitern —, aber er sagt es jetzt.
    """

    roh = os.environ.get(name, "").strip()
    if not roh:
        return rueckfall
    try:
        return typ(roh)
    except ValueError:
        logger.warning(
            "%s=%r ist keine Zahl — es gilt der Vorgabewert %s.",
            name,
            roh,
            rueckfall,
        )
        return rueckfall
