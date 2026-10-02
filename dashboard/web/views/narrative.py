"""Tab «Bericht»: das abschließende Narrativ des Laufs (`final_narrative.md`).

**Jeder Tick ist zugeklappt** (P7.6, 2026-10-01). Der Bericht des Pitch-Falls
stand bis dahin als ein Markdown-Block da, gemessen 63 Bildschirme lang (Befund
16 der Abnahme vom 2026-09-30): vierzig Ticks mit Kennzahlen, Segmenten,
Begründungen und Meldungen untereinander. Jetzt stehen Überblick und Endstand
offen, und je Tick eine Zeile mit seinen Kennzahlen — wer einem Tick nachgeht,
klappt ihn auf. Die Datei selbst bleibt, wie sie ist; gegliedert wird beim
Anzeigen, also auch für Berichte von vor diesem Tag.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from dash import html

from dashboard.run_browser import read_run_file
from dashboard.web import components as ui

#: Die Überschrift des Abschnitts mit den Ticks — «Tick für Tick» seit dem
#: 2026-10-01, davor «Tick-Übersicht».
_TICKS_KOPF = re.compile(r"^## Tick(?: für Tick|-Übersicht)\s*$", re.MULTILINE)

#: Wo im Kopf die Vorgaben des Szenarios beginnen — Zeitplan und Regeln. Sie
#: kommen in eine eigene Klappe: Im Pitch-Fall waren es 1210 px vor dem ersten
#: Tick, bei Berichten von vor dem 2026-10-01 samt Konfigurationsprosa 3478.
_VORGABEN_KOPF = re.compile(
    r"^## (?:Geplante Änderungen der Systemgrößen|Property-Zeitplan \(Config\))\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Tick:
    titel: str
    kennzahlen: str
    rumpf: str
    faktorwechsel: bool


@dataclass(frozen=True)
class Gliederung:
    kopf: str
    ticks: list[Tick]
    schluss: str
    vorgaben: str = ""


def gliedern(text: str) -> Gliederung:
    """Teilt einen Bericht in Kopf, Ticks und Schluss. Ohne Tick-Abschnitt ist alles Kopf."""

    treffer = _TICKS_KOPF.search(text)
    if not treffer:
        return Gliederung(kopf=text, ticks=[], schluss="")

    kopf = text[: treffer.start()]
    vorgaben = ""
    if vorgaben_start := _VORGABEN_KOPF.search(kopf):
        kopf, vorgaben = kopf[: vorgaben_start.start()], kopf[vorgaben_start.end() :]
    rest = text[treffer.end() :]
    schluss_start = re.search(r"^## ", rest, re.MULTILINE)
    abschnitt = rest[: schluss_start.start()] if schluss_start else rest
    schluss = rest[schluss_start.start() :] if schluss_start else ""

    ticks: list[Tick] = []
    for block in re.split(r"^### ", abschnitt, flags=re.MULTILINE)[1:]:
        titel, _, rumpf = block.partition("\n")
        zeilen = [z.strip() for z in rumpf.splitlines() if z.strip()]
        kennzahlen = zeilen[0].replace("**", "") if zeilen else ""
        ticks.append(
            Tick(
                titel=titel.strip(),
                kennzahlen=kennzahlen,
                rumpf=rumpf,
                faktorwechsel="**Faktorwechsel:**" in rumpf,
            )
        )
    return Gliederung(kopf=kopf, ticks=ticks, schluss=schluss, vorgaben=vorgaben)


def _zeile(tick: Tick) -> str:
    """Die Zeile über einem zugeklappten Tick: Titel und die ersten beiden Kennzahlen."""

    teile = [t for t in tick.kennzahlen.split(" · ")[:2] if t]
    return " · ".join([tick.titel, *teile])


def render(run_dir: Path, run_id: str) -> html.Div:
    path = run_dir / "final_narrative.md"
    if not path.is_file():
        return ui.hinweis("`final_narrative.md` fehlt in diesem Lauf.", "warnung")

    gliederung = gliedern(read_run_file(path))
    if not gliederung.ticks:
        return ui.card(ui.markdown(gliederung.kopf))

    teile: list = [ui.card(ui.markdown(gliederung.kopf), class_name="mb-6")]
    if gliederung.vorgaben.strip():
        teile.append(
            html.Div(
                ui.accordion("Vorgaben des Szenarios", ui.markdown(gliederung.vorgaben)),
                className="mb-6",
            )
        )
    teile += [
        html.H2("Tick für Tick", className=f"{ui.H2} mb-2"),
        ui.satz(
            "Jeder Tick ist zugeklappt; die Zeile nennt Buchungsrate und Preis. "
            "Ein Tick mit Faktorwechsel ist markiert.",
            class_name=f"{ui.CAPTION} mb-4",
        ),
    ]
    teile.extend(
        ui.accordion(
            _zeile(tick),
            ui.markdown(tick.rumpf),
            badge="Faktorwechsel" if tick.faktorwechsel else None,
        )
        for tick in gliederung.ticks
    )
    if gliederung.schluss.strip():
        teile.append(ui.card(ui.markdown(gliederung.schluss), class_name="mt-6"))
    return html.Div(teile)
