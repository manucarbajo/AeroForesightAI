"""P0.2: Faktornamen dürfen zwischen Config und Matrix nicht auseinanderlaufen.

Die F7-Drift stand seit dem allerersten Commit im Repo: `configs/factors.json`
führte „Geopolitische Stabilitaet", `configs/cib_frozen.json` war für
„Marktstruktur" bewertet. Beide Dateien für sich waren in sich stimmig, nur
zueinander nicht — und niemand hat es bemerkt, weil nichts sie vergleicht.

Genau das tun diese Tests. Sie prüfen keine Bedeutung, sondern nur, dass beide
Dateien dieselbe Faktorlandschaft beschreiben.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FACTORS_PATH = REPO_ROOT / "configs" / "factors.json"
CIB_PATH = REPO_ROOT / "configs" / "cib_frozen.json"


def _normalise(text: str) -> str:
    """Umlaute und Schreibweise angleichen.

    `factors.json` schreibt „Stabilitaet", die Matrix-Metadaten dürfen
    „Stabilität" schreiben — das ist kein Widerspruch, sondern Kodierung. Der
    Test soll die Drift finden, nicht den Umlaut.
    """

    text = text.lower()
    text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", text)


@pytest.fixture(scope="module")
def factors() -> dict:
    return json.loads(FACTORS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def matrix() -> dict:
    return json.loads(CIB_PATH.read_text(encoding="utf-8"))


def _matrix_names(matrix: dict) -> dict[str, str]:
    """`metadata.factors` sieht aus wie ["F1 Mobilitaetsnachfrage", …]."""

    names = {}
    for entry in matrix["metadata"]["factors"]:
        factor_id, _, name = str(entry).partition(" ")
        names[factor_id] = name
    return names


def test_both_files_describe_the_same_factor_ids(factors, matrix):
    assert set(factors) == set(_matrix_names(matrix))


def test_every_factor_name_matches_between_config_and_matrix(factors, matrix):
    """Der eigentliche Drift-Wächter."""

    names = _matrix_names(matrix)
    abweichungen = [
        f"{fid}: factors.json='{factors[fid]['name']}' vs. cib_frozen.json='{names[fid]}'"
        for fid in sorted(factors)
        if _normalise(factors[fid]["name"]) != _normalise(names[fid])
    ]

    assert not abweichungen, "Faktornamen laufen auseinander:\n" + "\n".join(abweichungen)


def test_f7_is_geopolitical_stability(factors, matrix):
    """Die Entscheidung aus P0.2, festgenagelt.

    Kein Stilkriterium: Solange die Matrix für eine andere Bedeutung bewertet
    ist, sind ihre F7-Zellen nicht belastbar.
    """

    assert _normalise(factors["F7"]["name"]) == _normalise("Geopolitische Stabilitaet")
    assert "marktstruktur" not in _normalise(_matrix_names(matrix)["F7"])


def test_the_matrix_covers_every_descriptor_of_every_factor(factors, matrix):
    """Jeder Zustand aus `factors.json` muss in der Matrix vorkommen."""

    descriptors = {state for factor in factors.values() for state in factor["possible_states"]}
    in_matrix = set()
    for key in matrix["cells"]:
        source, _, target = key.partition("|")
        in_matrix.add(source)
        in_matrix.add(target)

    assert descriptors == in_matrix


def test_every_f7_cell_carries_a_reason(matrix):
    """P0.2 hat P2.3 für diese 48 Zellen vorgezogen — sie dürfen nicht leer sein."""

    ohne_grund = [
        key
        for key, cell in matrix["cells"].items()
        if ("F7." in key) and not str(cell.get("reasoning", "")).strip()
    ]

    assert not ohne_grund, f"F7-Zellen ohne Begründung: {ohne_grund}"


def test_the_provenance_of_the_matrix_is_stated(matrix):
    """Die neu bewerteten Zellen sind modellgeneriert — das muss dranstehen.

    **Die Zusage hat sich am 2026-08-31 verschoben, und dieser Test mit ihr.**
    Bis dahin verlangte er ein `pending_review` im Quellenlabel: Solange die 48
    F7-Zellen nicht fachlich abgenommen sind, sollte die Quelle das sagen.

    Mit [P2.2](../docs/projektplan.md) ist die Abnahme **entfallen** — unter
    Variante C prüft kein Algorithmus mehr die Kohärenz, und die Zellen
    entscheiden nichts. Ein Label, das eine Prüfung ankündigt, die niemand mehr
    vorhat, ist keine Ehrlichkeit, sondern eine Zusage an den nächsten Leser,
    die niemand einlöst (P2.3-Rest).

    **Was der Test weiterhin hält, ist die eigentliche Zusage:** Die Datei sagt,
    was sie ist. Nur heißt das jetzt «Beleg ohne bewertende Rolle» statt
    «Prüfung ausstehend».
    """

    metadata = matrix["metadata"]

    assert metadata["frozen"] is True
    assert "pending_review" not in metadata["source"], (
        "Das Label kündigt wieder eine fachliche Abnahme an. Seit P2.2 ist "
        "keine mehr vorgesehen — sie prüfte Werte, die nichts entscheiden."
    )
    assert metadata["source"] == "beleg_keine_bewertende_rolle"
    assert "modellgeneriert" in metadata["note"], (
        "Dass die 48 F7-Zellen modellgeneriert sind, muss weiterhin dranstehen — "
        "sonst liest sich die Matrix wie geprüfte Expertenarbeit."
    )
