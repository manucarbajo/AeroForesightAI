"""Der Vorlauf: historische Außenwelt rein, Ticketpreis raus, gegen `CP0733` gehalten.

Aufruf:

    python -m src.backtest.vorlauf

Er rechnet **ohne Sprachmodell** — für den Preispfad trägt es nichts bei, und
`compute_mode` sagt das im Artefakt. Ein Lauf über 120 Ticks braucht damit
wenige Sekunden.
"""

from __future__ import annotations

import json
import sys

from src.backtest.auswertung import bewerten
from src.backtest.rahmen import ZUORDNUNG, historischer_rahmen
from src.backtest.reihen import REPO_ROOT, laden, monat_je_tick
from src.config_loader import build_initial_state
from src.llm.studio_helpers import MockLLM
from src.logging_setup import stdio_auf_utf8
from src.models.state_models import Rahmenszenario
from src.orchestration.scenario_sweeps import apply_sweep_overrides
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

#: Was gegen was gehalten wird. Zwei Seiten, dieselbe Rechnung: indexiert auf
#: 2015 = 100, verglichen auf Jahresmitteln, 2020/21 mitgerechnet und nicht
#: bewertet.
#:
#: Die **Preisseite** war der Vorlauf; die **Nachfrageseite** kam dazu, nachdem
#: er getragen hat. Die Reihenfolge war Absicht: Träfe schon der Preispfad die
#: Größenordnung nicht, sagte die Nachfrage nichts mehr dazu — sie hängt am Preis.
ZIELREIHEN = {
    "Preis": ("ticket_price", "hicp_flugreisen"),
    "Nachfrage": ("booking_rate", "fluggaeste"),
}
BERICHT = REPO_ROOT / "docs" / "backtest_vorlauf.md"


def modellpfade(*, seed: int = 42, mit_kapazitaet: bool = True) -> dict[str, dict[str, float]]:
    """Ticketpreis **und** Buchungsrate je Monat, aus **einem** Lauf.

    Beide Seiten kommen aus demselben Lauf — sonst verglichen sie zwei
    verschiedene Welten, und die Nachfrage antwortete auf einen anderen Preis
    als den, der geprüft wird.

    *mit_kapazitaet* ist die **Gegenprobe zu B4** (2026-09-03) und der Grund
    steht in `auswertung.py`: Eingang und Nachfrage-Zielreihe stammen aus
    derselben Eurostat-Tabelle. Ohne die Kapazitätsreihe gerechnet zeigt sich,
    wie viel der Übereinstimmung daran hängt — und die Antwort war nicht die
    erwartete.
    """

    reihen = {name: laden(name) for name in ZUORDNUNG}
    sweep = historischer_rahmen(reihen)
    if not mit_kapazitaet:
        sweep = sweep.model_copy(
            update={
                "property_overrides": [
                    o for o in sweep.property_overrides if o.property_id != "kapazitaet_index"
                ]
            }
        )

    state = apply_sweep_overrides(build_initial_state(), sweep)
    state.clock.max_ticks = sweep.max_ticks
    state.config.seed = seed
    state.rahmen = Rahmenszenario(id=sweep.id, name=sweep.name, quelle="preset")

    runner = SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(
            enable_market=True,
            enable_cib=True,
            deterministic_only=True,
            checkpoint_interval=0,
            verbose_ticks=False,
            # Den Personenverlauf liest der Backtest nicht; geschrieben landete er
            # im Vorführbestand unter `outputs/` (2026-10-02).
            personenverlauf=False,
        ),
    )
    ende = runner.run(
        state,
        seed=seed,
        run_id="backtest_vorlauf" if mit_kapazitaet else "backtest_ohne_kapazitaet",
    )

    monate = monat_je_tick()
    pfade: dict[str, dict[str, float]] = {"ticket_price": {}, "booking_rate": {}}
    for eintrag in ende.price_history:
        monat = monate.get(eintrag.round_number)
        if monat is None:
            continue
        pfade["ticket_price"][monat] = eintrag.price
        # `booking_rate` ist optional; ein fehlender Wert fällt heraus, statt als
        # 0 in ein Jahresmittel einzugehen.
        if eintrag.booking_rate is not None:
            pfade["booking_rate"][monat] = eintrag.booking_rate
    return pfade


def main() -> int:
    print("Backtest-Vorlauf 2015–2024 …")
    pfade = modellpfade()
    # **Die Gegenprobe zu B4 läuft immer mit**, nicht auf Zuruf: Ein Vorbehalt,
    # den man erst nachrechnen muss, liest niemand nach.
    ohne = modellpfade(mit_kapazitaet=False)
    ergebnisse: dict[str, object] = {}
    gegenprobe: dict[str, object] = {}

    for titel, (modellgroesse, zielname) in ZIELREIHEN.items():
        ziel = laden(zielname)
        ergebnis = bewerten(pfade[modellgroesse], ziel.werte)
        ergebnisse[titel] = (ergebnis, ziel)
        gegenprobe[titel] = bewerten(ohne[modellgroesse], ziel.werte)

        print()
        print(f"  === {titel}: {modellgroesse} gegen {zielname} ===")
        print("  Jahr   Modell    Ziel   Abstand")
        for jahr in sorted(ergebnis.modell_je_jahr):
            marke = _marke(ergebnis, jahr)
            m, z = ergebnis.modell_je_jahr[jahr], ergebnis.ziel_je_jahr[jahr]
            print(
                f"  {jahr}  {m:7.2f} {z:7.2f}   {m - z:+7.2f}{'  (' + marke + ')' if marke else ''}"
            )
        vor = [j for j in ergebnis.bewertete_jahre if j < "2020"]
        nach = [j for j in ergebnis.bewertete_jahre if j > "2021"]
        print(
            f"  Abstand gesamt {ergebnis.mittlerer_abstand:>7.2f}  |  "
            f"{vor[0]}–{vor[-1]}: {ergebnis.abstand_ueber(vor):.2f}  |  "
            f"{nach[0]}–{nach[-1]}: {ergebnis.abstand_ueber(nach):.2f}"
        )
        print(f"  Richtung getroffen {ergebnis.richtungstreffer}")

    BERICHT.write_text(_bericht(ergebnisse, gegenprobe), encoding="utf-8", newline="")
    print(f"\nBericht: {BERICHT.relative_to(REPO_ROOT)}")
    return 0


def _marke(ergebnis, jahr: str) -> str:
    """Warum ein Jahr in der Tabelle steht, aber nicht in der Kennzahl.

    **Zwei Gründe, und sie sind verschieden.** 2020/21 sind ungewertet, weil das
    Modell keine Reisebeschränkung kennt — eine Aussage über das Modell. Das
    Basisjahr ist ausgenommen, weil beide Reihen darauf indexiert sind und sein
    Abstand *per Konstruktion* null ist — eine Aussage über die Messung. Sie mit
    demselben Wort zu markieren hätte den zweiten Fall als Modellschwäche
    gelesen.
    """

    if jahr == ergebnis.basisjahr:
        return "Basis, Abstand per Konstruktion 0"
    if jahr in ergebnis.unbewertete_jahre:
        return "ungewertet"
    return ""


def _gegenprobe_abschnitt(
    ergebnisse: dict[str, object], gegenprobe: dict[str, object]
) -> list[str]:
    """Wie viel der Übereinstimmung hängt am Kapazitätseingang? (B4, 2026-09-03)

    **Der Anlass ist eine Zirkularitätssorge, und sie ist berechtigt:** Der
    Eingang `kapazitaet_index` kommt aus Eurostat `avia_paoc`/`CAF_PAS` (Flüge),
    die Nachfrage-Zielreihe aus `avia_paoc`/`PAS_CRD` (Passagiere) — dieselbe
    Tabelle, und mechanisch verbunden über Sitze und Auslastung. Ein Modell, das
    einen nahen Verwandten seiner Zielgröße als Eingabe bekommt, kann gut
    aussehen, ohne etwas zu können.

    **Deshalb steht die Gegenprobe im Bericht und nicht in einer Fußnote:** Ein
    Vorbehalt, den man erst nachrechnen muss, liest niemand nach. Gerechnet wird
    derselbe Lauf ohne die Kapazitätsreihe, mit sonst unverändertem Verfahren.
    """

    zeilen = [
        "## Gegenprobe: was hängt am Kapazitätseingang?",
        "",
        "Der Eingang `kapazitaet_index` (Eurostat `avia_paoc`, `CAF_PAS` — Flüge) und "
        "die Nachfrage-Zielreihe (`avia_paoc`, `PAS_CRD` — Passagiere) stammen aus "
        "**derselben Tabelle** und hängen mechanisch zusammen. Unten steht deshalb "
        "derselbe Lauf ohne die Kapazitätsreihe, mit sonst unverändertem Verfahren.",
        "",
        "| Seite | Kennzahl | mit Kapazität | ohne |",
        "| --- | --- | ---: | ---: |",
    ]
    for titel, paket in ergebnisse.items():
        mit = paket[0]  # type: ignore[index]
        oh = gegenprobe[titel]
        vor = [j for j in mit.bewertete_jahre if j < "2020"]
        nach = [j for j in mit.bewertete_jahre if j > "2021"]
        zeilen += [
            f"| {titel} | Abstand gesamt | {mit.mittlerer_abstand:.2f} | "
            f"{oh.mittlerer_abstand:.2f} |",
            f"| {titel} | davon {vor[0]}–{vor[-1]} | {mit.abstand_ueber(vor):.2f} | "
            f"{oh.abstand_ueber(vor):.2f} |",
            f"| {titel} | davon {nach[0]}–{nach[-1]} | {mit.abstand_ueber(nach):.2f} | "
            f"{oh.abstand_ueber(nach):.2f} |",
            f"| {titel} | Richtung getroffen | {mit.richtungstreffer} | "
            f"{oh.richtungstreffer} |",
        ]

    zeilen += [
        "",
        "**Wie das zu lesen ist:** Würde der Eingang die Übereinstimmung nur "
        "widerhallen, müsste der **Abstand** mit ihm kleiner sein. Auf der "
        "Nachfrageseite ist er größer — das Modell folgt den *Flügen* und verfehlt "
        "damit die *Passagiere*, die stärker gewachsen sind. Was er beiträgt, zeigt "
        "sich an der **Richtung** und an der **Preisseite**, deren Zielreihe aus einer "
        "ganz anderen Quelle stammt (Eurostat `prc_hicp_midx`) und deshalb nicht "
        "zirkulär sein kann.",
        "",
        "Der Vorbehalt bleibt trotzdem stehen: Eine Kapazitätsreihe, die Sitze zählt "
        "statt Flüge, gibt es bei Eurostat auf dieser Ebene nicht. Das ist eine "
        "**Datenfrage**, keine Parameterfrage.",
        "",
    ]
    return zeilen


def _bericht(ergebnisse: dict[str, object], gegenprobe: dict[str, object]) -> str:
    quellen = json.loads((REPO_ROOT / "configs" / "backtest" / "quellen.json").read_text("utf-8"))
    zeilen = [
        "# Backtest-Vorlauf 2015–2024",
        "",
        "> Erzeugt von `python -m src.backtest.vorlauf`. **Diese Datei wird "
        "überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.",
        "",
    ]

    for titel, paket in ergebnisse.items():
        ergebnis, ziel = paket  # type: ignore[misc]
        modellgroesse, zielname = ZIELREIHEN[titel]
        vor = [j for j in ergebnis.bewertete_jahre if j < "2020"]
        nach = [j for j in ergebnis.bewertete_jahre if j > "2021"]

        zeilen += [
            f"## {titel}: `{modellgroesse}` gegen `{zielname}`",
            "",
            "| Jahr | Modell | Zielreihe | Abstand | |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
        for jahr in sorted(ergebnis.modell_je_jahr):
            m, z = ergebnis.modell_je_jahr[jahr], ergebnis.ziel_je_jahr[jahr]
            zeilen.append(
                f"| {jahr} | {m:.2f} | {z:.2f} | {m - z:+.2f} | {_marke(ergebnis, jahr)} |"
            )

        zeilen += [
            "",
            "| Kennzahl | Wert |",
            "| --- | ---: |",
            f"| Mittlerer Abstand, bewertete Jahre | {ergebnis.mittlerer_abstand:.2f} |",
            f"| Größter Abstand | {ergebnis.groesster_abstand:.2f} "
            f"({ergebnis.groesster_abstand_jahr}) |",
        ]
        if vor:
            zeilen.append(f"| davon {vor[0]}–{vor[-1]} | {ergebnis.abstand_ueber(vor):.2f} |")
        if nach:
            zeilen.append(f"| davon {nach[0]}–{nach[-1]} | {ergebnis.abstand_ueber(nach):.2f} |")
        zeilen += [
            f"| Richtung der Jahresveränderung getroffen | {ergebnis.richtungstreffer} |",
            f"| Saisonschwankung Modell / Ziel | {ergebnis.saison_modell:.1f} / "
            f"{ergebnis.saison_ziel:.1f} |",
            "",
        ]
        zeilen += [f"- {h}" for h in ergebnis.hinweise]
        zeilen.append("")

    zeilen += _gegenprobe_abschnitt(ergebnisse, gegenprobe)
    zeilen += [
        "## Datenquellen",
        "",
        "| Reihe | Monate | Abgerufen | Herkunft |",
        "| --- | ---: | --- | --- |",
    ]
    for eintrag in quellen["reihen"]:
        zeilen.append(
            f"| `{eintrag['datei']}` | {eintrag['zeilen']} | {eintrag['abgerufen']} | "
            f"{str(eintrag['hinweis']).split('.')[0]}. |"
        )
    zeilen += [
        "",
        f"Fenster: {quellen['fenster']['von']} bis {quellen['fenster']['bis']}. "
        f"Nicht bewertet: {', '.join(quellen['unbewertet'])}.",
        "",
        f"> {quellen['unbewertet_grund']}",
        "",
    ]
    return "\n".join(zeilen)


if __name__ == "__main__":
    # Der Prozess sichert seine Ausgabe, bevor er das erste Zeichen schreibt
    # (P3.10): Umgeleitet spricht `sys.stdout` unter Windows cp1252, und dann
    # wirft jede Meldung mit `→`, `≥` oder `₂` statt zu erscheinen.
    stdio_auf_utf8()
    sys.exit(main())
