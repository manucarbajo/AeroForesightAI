"""Woraus ein Lauf entstanden ist: Seed, Rechenmodus, Config-Fingerabdruck, Codestand (P0.6).

`run_metadata.json` belegte den Reproduzierbarkeits-Claim bisher nicht: Modell,
`base_url`, Temperatur und Tick-Zahlen standen drin, aber weder der Seed noch,
ob überhaupt ein Sprachmodell beteiligt war. Aus den Artefakten allein ließ sich
ein Lauf nicht nachstellen.

**Der Fingerabdruck beschreibt, was gelaufen ist — nicht, was auf der Platte
liegt.** Gehasht werden die Konfigurationsobjekte aus dem `SimulationState`,
nicht die Dateien unter `configs/`. Der Unterschied ist wesentlich: Ein Lauf aus
dem Dashboard arbeitet mit einem Entwurf, der die Dateien gar nicht anfasst. Ein
Dateihash würde dort eine Gleichheit behaupten, die es nicht gibt.

**Und er wird beim Start genommen, nicht am Ende.** `config_fingerprint` ist
eine Momentaufnahme des Zustands, in dem sie aufgerufen wird — richtig ist
deshalb allein der Aufrufzeitpunkt. `SimulationRunner.run` nimmt sie vor dem
ersten Tick und legt sie im State ab; `save_run_metadata` liest sie von dort.
Am Ende genommen hätte sie den Lauf mitgehasht: `factors` trägt den Zustand
jedes Deskriptors, und den verschiebt der Lauf. Zwei Läufe derselben
Konfiguration mit verschiedenen Seeds bekamen so verschiedene Abdrücke.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from src.models.run_models import RunArgs
from src.models.state_models import ConfigFingerprint

REPO_ROOT = Path(__file__).resolve().parents[3]

#: Schlüssel, die ein Lauf **in** die CIB-Matrix schreibt. Sie beschreiben das
#: Ergebnis, nicht die Eingabe, und gehören deshalb nicht in den
#: Fingerabdruck — sonst trügen zwei Läufe derselben Konfiguration
#: verschiedene Fingerabdrücke, und die Frage, für die er da ist, bliebe
#: unbeantwortet.
#:
#: Diese Liste ist eine Aufzählung, und Aufzählungen laufen dem Code davon.
#: `tests/test_run_provenance.py` liest deshalb alle Schreibzugriffe auf
#: ``cib_matrix.metadata[...]`` aus `src/` und vergleicht sie hiermit: Wer einen
#: neuen Schlüssel einführt, bekommt einen roten Test statt eines still
#: wandernden Fingerabdrucks.
RUN_PRODUCED_MATRIX_METADATA: frozenset[str] = frozenset(
    {
        "consistency_score",
        # **Zwei Schlüssel seit P1.3**, die sich nicht um ein Wort
        # unterscheiden. Vorher waren es vier: `scenarios` (das LLM-Narrativ),
        # `scenario_candidates` (die gerechneten Kandidaten),
        # `scenario_consistency` und `scenario_llm_payload` — zwei davon
        # Doppelungen des jeweils anderen.
        "gerechnete_szenarien",
        "erzaehlte_szenarien",
    }
)


def _digest(payload: Any) -> str:
    """Stabiler Hash über eine JSON-serialisierbare Struktur."""

    text = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _dump(model: Any) -> Any:
    if model is None:
        return None
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model


def config_fingerprint(state) -> ConfigFingerprint:
    """Momentaufnahme der Eingaben — **im Zustand des Aufrufzeitpunkts**.

    Aufzurufen ist sie vor dem ersten Tick; siehe Modul-Docstring. Der ``seed``
    ist aus dem Simulations-Config-Hash ausgenommen: Er unterscheidet zwei Läufe
    **derselben** Konfiguration, und der Fingerabdruck soll genau diese
    Gleichheit sichtbar machen. Er steht als eigenes Feld daneben.
    """

    simulation_config = _dump(getattr(state, "config", None)) or {}
    if isinstance(simulation_config, dict):
        simulation_config = {
            key: value for key, value in simulation_config.items() if key != "seed"
        }

    factors = {
        factor_id: _dump(factor)
        for factor_id, factor in getattr(getattr(state, "environment", None), "factors", {}).items()
    }
    agent_profiles = {
        agent.id: _dump(agent.profile) for agent in getattr(state, "agents", []) or []
    }

    cib_matrix = _dump(getattr(state, "cib_matrix", None))
    if isinstance(cib_matrix, dict):
        metadata = {
            key: value
            for key, value in (cib_matrix.get("metadata") or {}).items()
            if key not in RUN_PRODUCED_MATRIX_METADATA
        }
        cib_matrix = {**cib_matrix, "metadata": metadata}

    return ConfigFingerprint(
        simulation_config=_digest(simulation_config),
        properties=_digest(_dump(getattr(state, "properties", None))),
        factors=_digest(factors),
        agent_profiles=_digest(agent_profiles),
        cib_matrix=_digest(cib_matrix) if cib_matrix is not None else None,
    )


def recorded_fingerprint(state) -> ConfigFingerprint:
    """Der beim Start abgelegte Abdruck — sonst einer von jetzt.

    Der Rückfall gilt Aufrufern, die ohne `SimulationRunner` an
    `save_run_metadata` kommen (Tests, Skripte). Er beschreibt dann den
    Zustand beim Schreiben, nicht beim Starten; für einen echten Lauf greift
    er nie, weil der Runner das Feld setzt.
    """

    recorded = getattr(state, "config_fingerprint", None)
    if isinstance(recorded, ConfigFingerprint):
        return recorded
    return config_fingerprint(state)


def code_version() -> dict[str, Any] | None:
    """Git-Commit und ob der Arbeitsbaum dabei sauber war — oder ``None``.

    Ohne Git (installiertes Paket, Container ohne Repo) ist das schlicht nicht
    feststellbar. Dann steht ``null`` in der Datei, statt eine Herkunft zu
    behaupten, die niemand prüfen kann.

    Bewusst **nicht** zwischengespeichert: Das Dashboard läuft als ein Prozess
    über Stunden. Ein `lru_cache` hätte Commit und `dirty` beim Prozessstart
    eingefroren, und jeder spätere Lauf trüge den Codestand von damals — die
    Sorte Angabe, die stimmt, bis sie gebraucht wird. Drei `git`-Aufrufe pro
    Lauf sind neben der Simulation nicht messbar.
    """

    def _git(*args: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        return result.stdout.strip()

    commit = _git("rev-parse", "HEAD")
    if not commit:
        return None

    status = _git("status", "--porcelain")
    return {
        "commit": commit,
        "dirty": bool(status),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD") or None,
    }


def compute_mode(args: RunArgs) -> str:
    """Wie gerechnet wurde — in derselben Sprache wie das Dashboard.

    Die ersten drei Modi entsprechen den Auswahlmöglichkeiten unter
    «Rechenmodus»: Ein Lauf ohne Sprachmodell darf nicht wie ein vollwertiger
    aussehen.

    Der vierte hat keinen Schalter, weil ihn nur der Sweep-Pfad erzeugt: Der
    rechnet seine Ticks deterministisch, lässt den Abschlusstext am Ende aber
    vom Modell schreiben (`prefer_llm=True`). Beide vorhandenen Modi hätten
    dort etwas Falsches behauptet — `deterministic_only`, es sei kein Modell
    beteiligt gewesen, `llm`, die Zahlen kämen aus einem Dialog mit ihm. Ein
    eigener Modus ist billiger als eine gebeugte Angabe.
    """

    deterministic = args.deterministic_only
    llm_narrative = args.llm_narrative

    if deterministic and llm_narrative:
        return "deterministic_with_llm_narrative"
    if deterministic:
        return "deterministic_only"
    if args.mock_llm:
        return "mock_llm"
    return "llm"


COMPUTE_MODE_LABELS = {
    "llm": "Mit Sprachmodell",
    "mock_llm": "Ohne Sprachmodell (Mock)",
    "deterministic_only": "Nur Zahlen (deterministisch)",
    "deterministic_with_llm_narrative": "Nur Zahlen, Abschlusstext vom Modell",
}

#: Modi, in denen kein Sprachmodell an den **Zahlen** beteiligt war. Der Hybrid
#: steht hier mit drin: Seine Ticks sind so deterministisch wie die eines
#: reinen Zahlenlaufs, befragt wird das Modell erst danach.
MODES_WITHOUT_LLM_TICKS = frozenset(
    {"mock_llm", "deterministic_only", "deterministic_with_llm_narrative"}
)

#: Modi, in denen überhaupt kein Sprachmodell befragt wurde. Nur hier ist die
#: Angabe eines Modellnamens sinnlos.
MODES_WITHOUT_ANY_LLM = frozenset({"mock_llm", "deterministic_only"})
