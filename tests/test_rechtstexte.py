"""Die Rechtstexte sind ein Gerüst — und sagen das, solange sie eines sind (P1.4).

Impressum, Datenschutzerklärung und AGB stehen strukturell fertig: die
Abschnitte nach § 5 DDG, Art. 13 DSGVO und den üblichen Vertragsteilen, und
**jede Pflichtangabe als benannte Lücke** — `[Straße und Hausnummer]`, nicht
`[…]`. Man sieht, *was* fehlt, nicht nur *dass* etwas fehlt.

**Was hier nicht steht, sind die Texte selbst.** Sie brauchen die Firmendaten
und eine juristische Prüfung; erfundene Rechtstexte wären schlimmer als
erkennbar unfertige.

Drei Zusagen prüft diese Datei:

1. **Der Warnblock bleibt**, solange eine Lücke offen ist. Er ist das Einzige,
   was einen Besucher davor bewahrt, den Entwurf für verbindlich zu halten —
   und genau die Art Element, das bei einem späteren Umbau verschwindet, weil
   es niemandem gehört.
2. **Jede Lücke steht in der Checkliste** (`docs/landingpage.md`). Sonst
   arbeitet man die Liste ab und übersieht, was seither dazugekommen ist.
3. **Die Abschnitte sind vollständig** — eine Seite, der ein Pflichtabschnitt
   fehlt, ist nicht unfertig, sondern falsch.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from dashboard.web.landing_route import LANDING_DIR

CHECKLISTE = Path("docs/landingpage.md")

SEITEN = ("impressum", "datenschutz", "agb")

#: Was in einer eckigen Klammer steht, aber keine Lücke ist: JavaScript im
#: `<script>`-Block der Seite (`[...group.querySelectorAll(...)]`) und
#: Attributnamen. Sie werden vor dem Suchen entfernt, nicht danach gefiltert —
#: eine Filterliste wüchse mit jedem neuen Skript.
_SKRIPT = re.compile(r"<script\b.*?</script>", re.S)
_TAG = re.compile(r"<[^>]+>")

#: Pflichtabschnitte je Seite. Bewusst als Stichwort, nicht als voller
#: Wortlaut: Die Überschrift darf umformuliert werden, der Abschnitt nicht
#: verschwinden.
ABSCHNITTE = {
    "impressum": ("§ 5 DDG", "Vertreten durch", "Kontakt", "Registereintrag", "Streitschlichtung"),
    "datenschutz": ("Verantwortlich", "Rechte", "Aufbewahrung", "Beschwerde"),
    "agb": ("Geltungsbereich", "Vertragsschluss", "Verg", "Laufzeit", "Haftung"),
}


def _worte(text: str) -> str:
    """Nur Buchstaben, Ziffern und einfache Zwischenräume — kein Satzzeichen."""

    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE))


def _text(seite: str) -> str:
    return (LANDING_DIR / f"{seite}.html").read_text(encoding="utf-8")


def _luecken(seite: str) -> set[str]:
    """Jede benannte Lücke der Seite."""

    ohne_skript = _SKRIPT.sub(" ", _text(seite))
    return {
        treffer.strip() for treffer in re.findall(r"\[([^\]\[]{3,})\]", _TAG.sub(" ", ohne_skript))
    }


class TestDerWarnblockBleibt:
    """Er ist das Einzige, was den Entwurf als Entwurf kenntlich macht."""

    @pytest.mark.parametrize("seite", SEITEN)
    def test_the_warning_stays_while_a_gap_remains(self, seite):
        text = _text(seite)

        if not _luecken(seite):
            pytest.skip(f"{seite}: keine Lücken mehr — der Warnblock darf raus")

        assert "Platzhalter" in text or "Ger" in text, (
            f"{seite}.html hat noch offene Lücken, sagt es aber nicht mehr. "
            "Der Warnblock ist das Einzige, was einen Besucher davor bewahrt, "
            "den Entwurf für verbindlich zu halten."
        )
        assert "ersetzt keine Rechtsberatung" in text


class TestJedeLueckeStehtInDerCheckliste:
    """Sonst arbeitet man die Liste ab und übersieht, was dazugekommen ist."""

    @pytest.mark.parametrize("seite", SEITEN)
    def test_no_gap_is_missing_from_the_list(self, seite):
        # **Der Vergleich läuft über Wörter, nicht über Satzzeichen.** Die
        # erste Fassung nahm die ersten drei Wörter wörtlich und scheiterte an
        # einem Komma: «Auflistung eingesetzter Dienstleister,» in der Seite
        # gegen «Auflistung eingesetzter Dienstleister» in der Liste. Der
        # Wächter soll auf eine fehlende Angabe zeigen, nicht auf Zeichensetzung.
        liste = _worte(CHECKLISTE.read_text(encoding="utf-8"))
        fehlend = sorted(
            luecke
            for luecke in _luecken(seite)
            # Die Checkliste darf kürzen, sie darf nur nichts weglassen.
            if " ".join(_worte(luecke).split()[:3]) not in liste
        )

        assert not fehlend, (
            f"Diese Lücken in {seite}.html stehen nicht in der Checkliste:\n  "
            + "\n  ".join(fehlend)
            + f"\n\nNachtragen in {CHECKLISTE}."
        )

    def test_the_list_is_not_empty(self):
        """Ein Wächter über eine leere Liste prüft nichts."""

        gefunden = {seite: len(_luecken(seite)) for seite in SEITEN}

        assert sum(gefunden.values()) >= 15, f"Nur {gefunden} Lücken gefunden — sucht er noch?"


class TestDieAbschnitteSindVollstaendig:
    """Eine Seite ohne Pflichtabschnitt ist nicht unfertig, sondern falsch."""

    @pytest.mark.parametrize("seite", SEITEN)
    def test_every_required_section_is_present(self, seite):
        text = _TAG.sub(" ", _text(seite))
        fehlend = [stichwort for stichwort in ABSCHNITTE[seite] if stichwort not in text]

        assert not fehlend, f"{seite}.html fehlen Abschnitte zu: {fehlend}"
