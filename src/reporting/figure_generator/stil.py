"""Farben und Achsen der Diagramme — **eine** Quelle für PNG und Bildschirm (P1.2).

Bis zum 2026-08-30 traf jede Matplotlib-Figur ihre Farbwahl selbst: `#2563eb`
für die Buchungsrate hier, `#059669` für den Preis dort, `#1f77b4`/`#ff7f0e` aus
der Matplotlib-Standardpalette in der Bevölkerungsgrafik. Das Dashboard färbte
dieselben Größen über `theme.PALETTE` ganz anders ein. Wer eine Figur aus dem
Bericht neben den Bildschirm hielt, sah zweimal dasselbe in verschiedenen
Farben — und musste die Legende zweimal lesen.

**Warum die Werte hier stehen und nicht in `theme.py`:** `src/` ist die Engine
und darf nichts aus `dashboard/` importieren; umgekehrt ist es erlaubt und
üblich. Die Rollen liegen deshalb hier, und `dashboard/web/theme.py` bedient
sich daraus. Die Markenfarben selbst stammen aus
`aeroforesight-ai-landing-page/design/color-tokens.json`; sie sind hier
absichtlich als Konstanten festgehalten und nicht zur Laufzeit gelesen — die
Engine soll keine Datei der Landingpage brauchen, um eine Kurve zu zeichnen.

**Rollen, keine Farbnamen.** Wer `FARBEN["preis"]` schreibt, sagt, *was* er
zeichnet; wer `#0f766e` schreibt, sagt nur, wie es aussieht — und die nächste
Figur sagt etwas anderes.
"""

from __future__ import annotations

#: Die Markenfarbe und ihre Abstufungen, deckungsgleich mit `theme.NAVY`.
NAVY_500 = "#3e76a6"
NAVY_800 = "#1E3A5F"

#: Was welche Größe in einem Diagramm bedeutet. Dieselben Rollen trägt
#: `theme.PALETTE[…]` für die Bildschirmdarstellung.
FARBEN: dict[str, str] = {
    #: Ticketpreis — das Teal der Erlösseite.
    "preis": "#0f766e",
    #: Buchungsrate — die Markenfarbe, weil sie die Kernkennzahl ist.
    "buchung": NAVY_500,
    #: Politische Instrumente (CO₂-Abgabe, Abgaben) — Eingriff, deshalb warnend.
    "politik": "#b45309",
    #: Kosten der Anbieter.
    "kosten": "#7c3aed",
    #: Geschäftsreisende gegen Privatreisende — zwei Gruppen, ein Kontrast.
    "geschaeftlich": NAVY_800,
    "privat": "#b45309",
    #: Alles, was Kontext ist und nicht Aussage: Raster, Hilfslinien, Rahmen.
    "neutral": "#94a3b8",
}

#: Wie viel Deckkraft eine Hilfslinie verträgt, ohne die Kurve zu überstimmen.
HILFSLINIE_ALPHA = 0.35


def achsen_vereinheitlichen(fig) -> None:
    """Jede Achse einer Figur so setzen, wie sie in **jeder** Figur aussieht.

    **Angewandt beim Speichern, nicht in den Plot-Funktionen** — dort ließe es
    sich vergessen, und die nächste Figur sähe wieder nach einem anderen
    Werkzeug aus. Vorher entschied das jede Funktion für sich: mal Raster mit
    `alpha=0.3`, mal mit `0.7`, mal gestrichelt, dazu ein Rahmen auf allen vier
    Seiten. Ein Bericht aus fünf Bildern sah nach fünf Herkünften aus.

    Achsen, die bewusst abgeschaltet sind (die Platzhalter «Keine Daten»),
    bleiben unangetastet — ein Raster über einer Fehlermeldung wäre Dekoration.
    """

    for ax in fig.get_axes():
        if not getattr(ax, "axison", True):
            continue
        ax.grid(True, alpha=HILFSLINIE_ALPHA, linewidth=0.6)
        ax.set_axisbelow(True)
        for kante in ("top", "right"):
            ax.spines[kante].set_visible(False)
        for kante in ("left", "bottom"):
            ax.spines[kante].set_color(FARBEN["neutral"])
