"""Der Prüfsatz: alles, was das Sprachmodell schreibt, gegen die Rechnung gehalten (P8-V1).

Aufruf (Ollama muss laufen, das Modell aus ``configs/simulation_config.json`` geladen sein):

    python -m src.reporting.pruefsatz_sprachmodell --rechner "Vorführ-Laptop"

Er befragt das Sprachmodell auf den drei Wegen, auf denen es im Produkt schreibt,
und zählt mit `aussagen_pruefung`, wie oft es der Rechnung widerspricht:

1. **Abschlusstexte** der vier Rahmenszenarien (ein Szenario-Vergleich, je 120 Ticks);
2. **Abfragen** an zwei dieser Läufe (fünf feste Fragen je Lauf);
3. **Texte der Agenten** aus einem Lauf über sechs Ticks — und dessen Sekunden je Tick.

Das Ergebnis steht in ``docs/pruefsatz_sprachmodell.md``. **Diese Datei wird bei
jedem Aufruf überschrieben** — wie ``docs/backtest_vorlauf.md``. Sie nennt den
Rechner nur mit der Bezeichnung aus ``--rechner``, keine Hardware: Gemessen wird
das Verhalten des Produkts, nicht die Maschine.

**Warum kein Test daraus wird, der rot und grün kennt:** Die Antworten eines
Sprachmodells streuen von Aufruf zu Aufruf. Ein Deckel auf die Zahl der
Widersprüche wäre an einem Tag grün und am nächsten rot, ohne dass sich etwas
geändert hätte — und ein Wächter, der ohne Anlass rot wird, wird abgeschaltet
statt gelesen (die Lehre aus P7.12). Der Prüfsatz ist deshalb eine **Messung mit
Bericht**; was deterministisch prüfbar ist, hält `tests/test_aussagen_pruefung.py`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from src.llm import OllamaClient, OllamaConfig
from src.logging_setup import stdio_auf_utf8
from src.reporting.aussagen_pruefung import LAUFTEXTE, Befund, laufzeilen, pruefe, pruefe_bis
from src.reporting.output_writer.paths import OUTPUT_DIR

REPO = Path(__file__).resolve().parents[2]
BERICHT = REPO / "docs" / "pruefsatz_sprachmodell.md"

#: Die Fragen an die Abfrage — je eine zu Preis, Buchungsrate, CO₂-Abgabe,
#: Faktorwechseln und Kostendruck. Fest, damit zwei Messungen vergleichbar sind.
FRAGEN = (
    "Wie haben sich Ticketpreis und Buchungsrate über den Lauf entwickelt?",
    "Ist die Buchungsrate im Lauf gestiegen oder gesunken?",
    "Wie hat sich die CO₂-Abgabe über den Lauf entwickelt?",
    "Welche Faktoren haben im Lauf ihren Zustand gewechselt?",
    "Wie hat sich der Kostendruck entwickelt?",
)

#: Die Läufe, an die die Fragen gehen: einer mit flacher CO₂-Abgabe und einer, in
#: dem Preis und Nachfrage auseinanderlaufen — die beiden Fälle vom 2026-09-29.
ABFRAGE_LAEUFE = ("business_as_usual", "transformation_conflict")

AGENTEN_TICKS = 6
AGENTEN_LAUF = "pruefsatz_agenten"


@dataclass
class Text:
    herkunft: str
    inhalt: str
    befunde: list[Befund] = field(default_factory=list)
    unbelegt: tuple[str, ...] = ()
    #: Was das Produkt selbst an diesem Text markiert (P8-V3) — je Befund die
    #: Zeile, die der Leser sieht. ``None``: Dieser Weg markiert nichts.
    markiert: tuple[str, ...] | None = None

    @property
    def unmarkiert(self) -> int:
        """Befunde, die der Leser nicht zu sehen bekommt — das Kriterium von P8-V3."""

        if self.markiert is None:
            return len(self.befunde)
        return sum(befund.zeile not in self.markiert for befund in self.befunde)


def _ticks(run_dir: Path) -> list[dict]:
    """Die Ticks mit allen Größen des Faktenblatts — auch der SAF-Quote (P8-V3)."""

    return laufzeilen(run_dir)


def abschlusstexte() -> tuple[list[Text], dict[str, Path]]:
    """Ein Szenario-Vergleich mit Abschlusstexten, geprüft gegen den je eigenen Lauf."""

    from src.orchestration.scenario_sweeps import rahmenszenarien, run_single_sweep

    texte: list[Text] = []
    ordner: dict[str, Path] = {}
    for sweep in rahmenszenarien():
        run_single_sweep(sweep, verbose=False, llm_narrative=True)
        run_dir = Path(OUTPUT_DIR) / "sweeps" / f"sweep_{sweep.id}"
        ordner[sweep.id] = run_dir
        daten = json.loads((run_dir / "run_scenario.json").read_text(encoding="utf-8"))
        ticks = _ticks(run_dir)
        if daten.get("source") != "llm":
            texte.append(
                Text(
                    f"{sweep.name}: Abschlusstext",
                    "(kein Text vom Sprachmodell — Vorlage verwendet)",
                )
            )
            continue
        # Geprüft wird, was der Text über **diesen** Lauf sagt. Die Geschichten der
        # drei Szenarien beschreiben andere Zukünfte und dürfen anders verlaufen.
        narrativ = daten.get("narrative") or {}
        markiert = tuple(w.get("zeile", "") for w in daten.get("widersprueche") or [])
        for schluessel in LAUFTEXTE:
            inhalt = str(daten.get(schluessel) or narrativ.get(schluessel) or "").strip()
            if inhalt:
                texte.append(
                    Text(
                        f"{sweep.name}: {schluessel}",
                        inhalt,
                        pruefe(inhalt, ticks),
                        markiert=markiert,
                    )
                )
    return texte, ordner


def abfragen(ordner: dict[str, Path]) -> list[Text]:
    """Die festen Fragen an zwei Läufe, samt Zahlenprüfung aus P2.5."""

    from src.reporting.state_explorer import StateExplorer, load_run_context

    texte: list[Text] = []
    llm = OllamaClient(OllamaConfig(temperature=0.2))
    for sweep_id in ABFRAGE_LAEUFE:
        run_dir = ordner.get(sweep_id)
        if run_dir is None:
            continue
        explorer = StateExplorer(load_run_context(f"sweeps/sweep_{sweep_id}"), llm=llm)
        ticks = _ticks(run_dir)
        for frage in FRAGEN:
            antwort = explorer.ask(frage)
            texte.append(
                Text(
                    f"{sweep_id}: {frage}",
                    antwort.text,
                    pruefe(antwort.text, ticks),
                    antwort.unbelegt,
                    markiert=antwort.widersprueche,
                )
            )
    return texte


def agenten() -> tuple[list[Text], float | None]:
    """Ein Lauf mit Agenten über wenige Ticks: ihre Texte und die Sekunden je Tick."""

    beginn = time.perf_counter()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.run_simulation",
            "--rounds",
            str(AGENTEN_TICKS),
            "--run-id",
            AGENTEN_LAUF,
            "--quiet",
        ],
        cwd=REPO,
        check=True,
    )
    wand = time.perf_counter() - beginn
    run_dir = Path(OUTPUT_DIR) / AGENTEN_LAUF
    metadaten = json.loads((run_dir / "run_metadata.json").read_text(encoding="utf-8"))
    gerechnet = metadaten.get("elapsed_seconds") or wand
    ticks = metadaten.get("ticks_completed") or AGENTEN_TICKS
    ereignisse = json.loads((run_dir / "event_log.json").read_text(encoding="utf-8"))
    ereignisse = ereignisse if isinstance(ereignisse, list) else ereignisse.get("events", [])
    lauf_ticks = _ticks(run_dir)
    # **Gegen den Stand bis zu ihrem Tick**, nicht gegen den ganzen Lauf (2026-10-02):
    # Ein Agent spricht über das, was er bis dahin sieht. Bericht und Konsole markieren
    # genau diese Befunde — deshalb ist `markiert` hier ihre eigene Zeilenmenge.
    texte = [
        Text(
            f"Agent, {e.get('event_type')}",
            str(e.get("description")),
            befunde := pruefe_bis(
                str(e.get("description")), lauf_ticks, int(e.get("round_number") or 0)
            ),
            markiert=tuple(b.zeile for b in befunde),
        )
        for e in ereignisse
        # Die Zeilen des Rechenkerns ([delta:…], Marktberichte) schreibt Python, nicht das Modell.
        if e.get("description")
        and not str(e.get("description")).startswith("[delta")
        and e.get("event_type") != "market_event"
    ]
    return texte, (gerechnet / ticks if ticks else None)


def bericht(rechner: str, gruppen: dict[str, list[Text]], sekunden_je_tick: float | None) -> str:
    modell = OllamaConfig().model
    zeilen = [
        "# Prüfsatz Sprachmodell",
        "",
        "> Erzeugt von `python -m src.reporting.pruefsatz_sprachmodell`. **Diese Datei wird überschrieben** — "
        "wer ein Ergebnis festhalten will, kopiert es heraus.",
        "",
        f"Gemessen am {date.today().isoformat()} auf «{rechner}», Modell `{modell}`. "
        "Die Antworten eines Sprachmodells streuen von Aufruf zu Aufruf; eine einzelne Messung ist ein Ausgangswert, kein Urteil.",
        "",
        "| Weg | Texte | englisch | mit Datum | Richtungswiderspruch | davon unmarkiert | unbelegte Zahlen |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, texte in gruppen.items():
        zaehl = lambda art: sum(any(b.art == art for b in t.befunde) for t in texte)  # noqa: E731
        zeilen.append(
            f"| {name} | {len(texte)} | {zaehl('englisch')} | {zaehl('datum')} | {zaehl('richtung')} | "
            f"{sum(t.unmarkiert for t in texte)} | {sum(bool(t.unbelegt) for t in texte)} |"
        )
    zeilen += [
        "",
        "**Sekunden je Tick** im Lauf mit Agenten: "
        + (f"{sekunden_je_tick:.1f}" if sekunden_je_tick is not None else "nicht gemessen"),
        "",
    ]
    zeilen += ["## Befunde im Einzelnen", ""]
    for name, texte in gruppen.items():
        auffaellig = [t for t in texte if t.befunde or t.unbelegt]
        zeilen += [f"### {name}", ""]
        if not auffaellig:
            zeilen += ["Keine.", ""]
            continue
        for t in auffaellig:
            zeilen.append(f"- **{t.herkunft}**")
            for b in t.befunde:
                marke = (
                    "" if t.markiert is not None and b.zeile in t.markiert else " **(unmarkiert)**"
                )
                zeilen.append(f"  - {b.art}{marke}: {b.zeile}")
            if t.unbelegt:
                zeilen.append(f"  - unbelegt: {', '.join(t.unbelegt)}")
        zeilen.append("")
    zeilen += [
        "## Was der Prüfsatz nicht sieht",
        "",
        "Erfundene Dinge ohne falsche Richtung oder Zahl («eine Elektroflotte») erkennt er nicht — "
        "das Faktenblatt sagt dem Modell nur, was es behaupten darf. Eine Richtungsaussage zählt nur, "
        "wenn ihr Satzteil genau eine Größe und genau eine Richtung nennt — alles andere wird übergangen "
        "statt geraten.",
        "",
        "**«davon unmarkiert»** zählt Befunde, die das Produkt dem Leser nicht zeigt. Abschlusstext "
        "und Abfrage markieren seit P8-V3 jeden Befund dieser Prüfung. Die Texte der Agenten werden "
        "seit dem 2026-10-02 gegen den Stand **bis zu ihrem Tick** gehalten statt gegen den ganzen "
        "Lauf, nur ein klarer Gegensatz zählt («steigt» gegen «sinkt»), und Bericht und Konsole "
        "markieren ihn.",
        "",
    ]
    return "\n".join(zeilen)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prüfsatz: Texte des Sprachmodells gegen die Rechnung."
    )
    parser.add_argument(
        "--rechner", default="Entwicklungsrechner", help="Bezeichnung des Rechners im Bericht"
    )
    args = parser.parse_args(argv)

    try:
        OllamaClient(OllamaConfig()).call("Antworte nur mit: ok")
    except Exception as exc:  # noqa: BLE001 - ohne Sprachmodell gibt es nichts zu messen
        print(f"Das Sprachmodell ist nicht erreichbar: {exc}", file=sys.stderr)
        return 2

    texte_schluss, ordner = abschlusstexte()
    texte_abfrage = abfragen(ordner)
    texte_agenten, sekunden = agenten()
    BERICHT.write_text(
        bericht(
            args.rechner,
            {"Abschlusstexte": texte_schluss, "Abfrage": texte_abfrage, "Agenten": texte_agenten},
            sekunden,
        ),
        encoding="utf-8",
    )
    print(f"Bericht: {BERICHT}")
    return 0


if __name__ == "__main__":
    # Wie jeder Einstieg (P3.10): Die Ausgabe ist UTF-8, auch umgeleitet.
    stdio_auf_utf8()
    raise SystemExit(main())
