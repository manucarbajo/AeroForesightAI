"""Ein Schritt zu zeichnen startet keinen Stapel Unterprozesse (P7.11-U11.1).

**Der Anlass ist eine Zusage, die gerissen ist, ohne dass jemand eine Regel
gebrochen hat.** P3.16 deckelt, wie lange ein Klick in der Schrittfolge
braucht, bis der neue Schritt im DOM steht: 500 ms zugesagt, 550 durchgelassen.
Am 2026-09-11 lag «Prüfen & Starten» bei 596 ms (1024 px), und die Ursache lag
nicht in der Oberfläche, sondern hinter ihr: `start_flow.herkunft` baut seine
Herkunftsangabe über `provenance.code_version`, und das startete **drei**
`git`-Prozesse — bei jedem Zeichnen. Gemessen 124 ms, während alle fünf anderen
Schritte zusammen unter 7 ms blieben.

**Warum ein Wächter und nicht nur die behobene Zeile.** Die Begründung im
Docstring von `code_version` stimmte, als sie geschrieben wurde: «Drei
`git`-Aufrufe pro Lauf sind neben der Simulation nicht messbar.» Sie hat nur
aufgehört zu gelten, als ein zweiter Aufrufer dazukam, der nicht ein Lauf ist,
sondern ein Bildschirm. Genau diese Sorte Drift findet keine Codelektüre — sie
entsteht an der Nahtstelle zwischen zwei Modulen, von denen keines falsch ist.

**Er sucht, statt aufzuzählen.** Gemessen wird jeder Schritt der Schrittfolge
und der Einstieg dazu; wer morgen einen siebten baut, der eine Adresse anpingt
oder `git` befragt, bekommt Bescheid, ohne dass ihn jemand hier einträgt.

**Der Deckel ist 1 und nicht 0**, und das ist eine Entscheidung: Der Codestand
gehört in den Prüfschritt (P1.9-W4.4), er ist ohne `git` nicht feststellbar,
und zwischengespeichert werden darf er nicht — das Dashboard läuft als ein
Prozess über Stunden, und ein eingefrorener Commit ist die Sorte Angabe, die
stimmt, bis sie gebraucht wird (`test_run_provenance.TestDerCodestandFriertNichtEin`).
Unter Windows kostet allein das Starten eines Prozesses 30 bis 45 ms; einer ist
bezahlbar, drei sind es nicht.
"""

from __future__ import annotations

import subprocess

import pytest

from dashboard.web.config_editor import wizard
from dashboard.web.state import default_config_draft, draft_to_dict

#: Wie viele Unterprozesse ein einzelnes Zeichnen starten darf. Herleitung im
#: Modul-Docstring — die Zahl ist eine Abwägung, keine Messung.
PROZESSE_MAX = 1


@pytest.fixture
def draft() -> dict:
    return draft_to_dict(default_config_draft())


def _gestartete_prozesse(monkeypatch, bauen) -> list[tuple[str, ...]]:
    """Was `bauen()` an Unterprozessen startet — die echten laufen weiter mit.

    Sie zu unterdrücken wäre bequem und falsch: Der Herkunftsblock kommt ohne
    Antwort von `git` gar nicht zustande, und ein Wächter, der eine leere
    Angabe misst, misst den einfachen Fall.
    """

    gezaehlt: list[tuple[str, ...]] = []
    echt = subprocess.run

    def zaehlend(args, **kwargs):
        gezaehlt.append(tuple(args) if isinstance(args, (list, tuple)) else (str(args),))
        return echt(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", zaehlend)
    bauen()
    return gezaehlt


class TestEinSchrittZuZeichnenStartetKaumProzesse:
    def test_no_step_spawns_more_processes_than_agreed(self, draft, monkeypatch):
        befunde: list[str] = []
        for index, schritt in enumerate(wizard.STEPS):
            gestartet = _gestartete_prozesse(monkeypatch, lambda i=index: wizard.content(draft, i))
            if len(gestartet) > PROZESSE_MAX:
                aufrufe = " · ".join(" ".join(a) for a in gestartet)
                befunde.append(
                    f"Schritt {index + 1} «{schritt.title}»: "
                    f"{len(gestartet)} Unterprozesse — {aufrufe}"
                )

        assert not befunde, (
            f"Diese Schritte starten mehr als {PROZESSE_MAX} Unterprozess je Zeichnen:\n  "
            + "\n  ".join(befunde)
            + "\nUnter Windows kostet ein Prozessstart 30 bis 45 ms, und der Klick-Deckel "
            "aus P3.16 steht auf 550 ms — das ist der Weg, auf dem ihn 2026-09-11 "
            "«Prüfen & Starten» gerissen hat."
        )

    def test_the_entry_spawns_none(self, draft, monkeypatch):
        """Der Einstieg nennt keinen Codestand — er soll auch keinen holen."""

        gestartet = _gestartete_prozesse(monkeypatch, lambda: wizard.entry(draft))

        assert not gestartet, f"Der Einstieg startet Unterprozesse: {gestartet}"

    def test_the_counter_would_notice_a_relapse(self, draft, monkeypatch):
        """**Ein Zähler, der nie etwas sieht, ist nicht grün — er ist blind.**

        Der Prüfschritt startet heute genau einen Prozess. Käme die Herkunft
        ohne aus — weil sie zwischengespeichert wird oder weggefallen ist —,
        wäre dieser Wächter für immer grün, ohne dass noch jemand etwas messen
        würde. Dann gehört er neu begründet oder gelöscht, nicht behalten.

        Bewusst **ohne** den Schritt zu nennen: Gesucht wird, dass die Messung
        überhaupt greift, nicht wo.
        """

        gesehen = [
            len(_gestartete_prozesse(monkeypatch, lambda i=i: wizard.content(draft, i)))
            for i in range(len(wizard.STEPS))
        ]

        assert sum(gesehen) >= 1, (
            "Kein einziger Schritt startet noch einen Unterprozess. Entweder misst "
            "dieser Wächter nichts mehr, oder der Codestand kommt inzwischen aus einer "
            "anderen Quelle — beides gehört begründet, nicht stillschweigend behalten."
        )
