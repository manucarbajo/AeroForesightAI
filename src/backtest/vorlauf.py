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
from src.models.state_models import Rahmenszenario
from src.orchestration.scenario_sweeps import apply_sweep_overrides
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

ZIELREIHE = "hicp_flugreisen"
BERICHT = REPO_ROOT / "docs" / "backtest_vorlauf.md"


def modellpfad(*, seed: int = 42) -> dict[str, float]:
    """Den Ticketpreis je Monat aus einem Lauf unter der historischen Außenwelt."""

    reihen = {name: laden(name) for name in ZUORDNUNG}
    sweep = historischer_rahmen(reihen)

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
        ),
    )
    ende = runner.run(state, seed=seed, run_id="backtest_vorlauf")

    monate = monat_je_tick()
    return {
        monate[eintrag.round_number]: eintrag.price
        for eintrag in ende.price_history
        if eintrag.round_number in monate
    }


def main() -> int:
    print("Backtest-Vorlauf 2015–2024 …")
    ziel = laden(ZIELREIHE)
    pfad = modellpfad()
    print(f"  Modellpfad: {len(pfad)} Monate")
    print(f"  Zielreihe : {len(ziel.werte)} Monate ({ziel.quelle['url'][:60]}…)")

    ergebnis = bewerten(pfad, ziel.werte)

    print()
    print("  Jahr   Modell    Ziel   Abstand")
    for jahr in sorted(ergebnis.modell_je_jahr):
        marke = "  (ungewertet)" if jahr in ergebnis.unbewertete_jahre else ""
        m, z = ergebnis.modell_je_jahr[jahr], ergebnis.ziel_je_jahr[jahr]
        print(f"  {jahr}  {m:7.2f} {z:7.2f}   {m - z:+7.2f}{marke}")
    print()
    print(f"  Mittlerer Abstand   {ergebnis.mittlerer_abstand:>7.2f} Indexpunkte")
    print(
        f"  Größter Abstand     {ergebnis.groesster_abstand:>7.2f} "
        f"({ergebnis.groesster_abstand_jahr})"
    )
    print(f"  Richtung getroffen  {ergebnis.richtungstreffer:>7s} Jahresschritte")
    print(f"  Saison Modell/Ziel  {ergebnis.saison_modell:>7.1f} / {ergebnis.saison_ziel:.1f}")

    BERICHT.write_text(_bericht(ergebnis, ziel, pfad), encoding="utf-8", newline="")
    print(f"\nBericht: {BERICHT.relative_to(REPO_ROOT)}")
    return 0


def _bericht(ergebnis, ziel, pfad: dict[str, float]) -> str:
    quellen = json.loads((REPO_ROOT / "configs" / "backtest" / "quellen.json").read_text("utf-8"))
    zeilen = [
        "# Backtest-Vorlauf 2015–2024",
        "",
        "> Erzeugt von `python -m src.backtest.vorlauf`. **Diese Datei wird "
        "überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.",
        "",
        "## Ergebnis",
        "",
        "| Jahr | Modell | Zielreihe | Abstand | |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for jahr in sorted(ergebnis.modell_je_jahr):
        m, z = ergebnis.modell_je_jahr[jahr], ergebnis.ziel_je_jahr[jahr]
        marke = "ungewertet" if jahr in ergebnis.unbewertete_jahre else ""
        zeilen.append(f"| {jahr} | {m:.2f} | {z:.2f} | {m - z:+.2f} | {marke} |")

    vor = [j for j in ergebnis.bewertete_jahre if j < "2020"]
    nach = [j for j in ergebnis.bewertete_jahre if j > "2021"]
    zeilen += [
        "",
        "| Kennzahl | Wert |",
        "| --- | ---: |",
        f"| Mittlerer Abstand, bewertete Jahre | {ergebnis.mittlerer_abstand:.2f} |",
        f"| Größter Abstand | {ergebnis.groesster_abstand:.2f} ({ergebnis.groesster_abstand_jahr}) |",
    ]
    # Die beiden Teilfenster stehen getrennt, weil genau dort die Aussage liegt:
    # vor der Pandemie und danach sind zwei verschiedene Ergebnisse.
    if vor:
        zeilen.append(f"| davon {vor[0]}–{vor[-1]} | {ergebnis.abstand_ueber(vor):.2f} |")
    if nach:
        zeilen.append(f"| davon {nach[0]}–{nach[-1]} | {ergebnis.abstand_ueber(nach):.2f} |")
    zeilen += [
        f"| Richtung der Jahresveränderung getroffen | {ergebnis.richtungstreffer} |",
        f"| Saisonschwankung Modell / Ziel | {ergebnis.saison_modell:.1f} / "
        f"{ergebnis.saison_ziel:.1f} |",
        "",
        "## Was das heißt",
        "",
    ]
    zeilen += [f"- {h}" for h in ergebnis.hinweise]
    zeilen += [
        "",
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
    sys.exit(main())
