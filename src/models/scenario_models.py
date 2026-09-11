"""Szenarien: **gerechnet** und **erzählt** — zwei Strukturen, nicht zwei Schlüssel.

Bis zum 2026-08-30 lagen beide im selben untypisierten Dict
(`cib_matrix.metadata`), unter Namen, die sich um ein Wort unterschieden:
`scenario_candidates` für die deterministisch abgeleiteten Kandidaten,
`scenarios` für das LLM-Narrativ. Erschwerend gab die Funktion, die die
**gerechneten** Kandidaten baut, ihren Teil selbst unter dem Schlüssel
`"scenarios"` zurück — derselbe Name für beide Seiten der Grenze, einmal innen,
einmal außen.

**Das Narrativ trägt Zahlen**, und darin liegt der eigentliche Befund: Seine
`key_relationships` nennen Einflusswerte zwischen Deskriptoren. Die sind
geklemmt, aber **erfunden** — sie stammen aus dem Sprachmodell, nicht aus der
CIB-Matrix. Nebeneinander in einem Dict sahen sie aus wie deren Zellenwerte.
Die Grenze stand nur in einem Kommentar.

Sie steht jetzt im Schema, an drei Stellen:

1. **Getrennte Typen** mit Namen, die man nicht verwechselt.
2. **`behaupteter_einfluss`** statt `influence` — das Feld sagt selbst, woher es
   kommt. Wer es in einen Bericht übernimmt, hat es gelesen.
3. **`herkunft`** als Feld auf jeder Sammlung, damit auch ein Konsument, der nur
   das JSON sieht, es beantworten kann, ohne den Schlüssel zu kennen, unter dem
   es lag.

Invariante 1 des Projekts sagt: Zahlen kommen aus Python, nie vom LLM. Diese
Werte sind die eine geduldete Ausnahme — sie sind Teil einer *Erzählung* und
werden nirgends weitergerechnet. Genau deshalb müssen sie als solche erkennbar
sein.
"""

from __future__ import annotations

from typing import Final, Literal

from pydantic import BaseModel, Field

#: Was eine Sammlung von Szenarien hervorgebracht hat. Steht als Feld im
#: Artefakt, damit die Herkunft auch ohne Kenntnis des Schlüssels lesbar ist.
#: `Final`, damit ein Typprüfer den Wert als `Literal` liest und nicht als `str`
#: — die Felder `herkunft` unten sind auf genau diesen Wert festgelegt (P4.4).
GERECHNET: Final = "gerechnet"
ERZAEHLT: Final = "erzaehlt_vom_sprachmodell"


class GerechnetesSzenario(BaseModel):
    """Eine Faktorkonstellation samt ihrer **gerechneten** Bewertung.

    Jede Zahl hier entsteht in `scenario_consistency.py` aus der eingefrorenen
    Matrix — nachvollziehbar und wiederholbar.
    """

    factor_states: dict[str, str] = Field(default_factory=dict)
    consistency_score: float = 0.0
    stability_index: float = 0.0
    reasoning: str = ""


class GerechneteSzenarien(BaseModel):
    """Die deterministisch abgeleiteten Kandidaten eines Laufs."""

    herkunft: Literal["gerechnet"] = GERECHNET
    matrix_round: int | None = None
    total_evaluated: int = 0
    consistent_count: int = 0
    szenarien: list[GerechnetesSzenario] = Field(default_factory=list)


class ErzaehlteBeziehung(BaseModel):
    """Eine vom Sprachmodell **behauptete** Wirkbeziehung.

    Der Feldname ist die Ansage: `behaupteter_einfluss` ist kein Matrixwert. Er
    hieß `influence` und stand damit im selben Vokabular wie `CIBCell.influence`
    — zwei Zahlen, ein Name, verschiedene Herkunft.
    """

    source: str = ""
    target: str = ""
    behaupteter_einfluss: int = 0
    why: str = ""


class ErzaehltesSzenario(BaseModel):
    """Ein Szenario, wie das Sprachmodell es erzählt."""

    id: str = ""
    title: str = ""
    narrative: str = ""
    selected_descriptors: list[str] = Field(default_factory=list)
    key_relationships: list[ErzaehlteBeziehung] = Field(default_factory=list)
    implications: list[str] = Field(default_factory=list)


class ErzaehlteSzenarien(BaseModel):
    """Die Narrative eines Laufs — Sprache, und darin eingebettet Behauptungen."""

    herkunft: Literal["erzaehlt_vom_sprachmodell"] = ERZAEHLT
    szenarien: list[ErzaehltesSzenario] = Field(default_factory=list)
