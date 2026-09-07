"""Was ein Startpfad den Artefakt-Schreibern mitgibt (P3.11).

**Bis zum 2026-09-05 war das ein Namensraum ohne Form.** `save_run_outputs`,
`build_run_args` und `save_run_metadata` bekamen ein `argparse.Namespace` bzw.
ein `types.SimpleNamespace` und lasen daraus mit ``getattr(args, "feld", False)``.
Kein Modell sagte, was ein Startpfad liefern muss; `dashboard/run_launcher.py`
baute den Namensraum an **zwei** Stellen von Hand mit je fünfzehn Feldern. Ein
vergessenes Feld war damit von einem abgeschalteten nicht zu unterscheiden.

**Der Schaden ist zweimal eingetreten**, und beide Male an derselben Stelle —
dem Rechenmodus, also der Angabe, *wie* ein Lauf gerechnet wurde:

* ``mock_llm`` fehlte im handgebauten Namensraum, `save_run_metadata` fiel auf
  ``False`` zurück, und **jeder Dashboard-Lauf «Ohne Sprachmodell» wurde als
  vollwertiger LLM-Lauf protokolliert** (zweite Gegenprobe zu P0.6).
* ``llm_narrative`` wurde von `build_run_args` **gar nicht mitkopiert**.
  Nachgestellt am 2026-09-05: Aus ``deterministic_with_llm_narrative`` wurde beim
  Durchreichen ``deterministic_only`` — ein Lauf, dessen Abschlusstext das Modell
  geschrieben hat, hätte sich selbst als modellfrei ausgewiesen. Heute erreicht
  kein Pfad diesen Fall; die *nächste* Änderung hätte ihn erreicht.

Beide Male stand die Absicht im Code und die Wirkung nicht — dieselbe Klasse wie
die Prüfungen aus P3.2, P3.3 und P3.4, die nur so aussahen.

**Invariante 4 gilt hier jetzt auch**: Das ist eine Grenze zwischen zwei Paketen
(`dashboard/` reicht sie an `src/reporting/`), und Cross-Boundary-Strukturen sind
typisierte Modelle, keine rohen Dicts oder Namensräume.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RunArgs(BaseModel):
    """Die Lauf-Argumente eines einzelnen Laufs — vollständig und geprüft.

    **Die Aufteilung in Pflicht und Vorgabe ist die eigentliche Entscheidung.**
    Der Projektplan warnt in beide Richtungen: Wer alles zur Pflicht macht,
    erzeugt fünfzehn Felder, die jeder Aufrufer stumpf ausschreibt, und gewinnt
    nichts; wer alles mit einem Vorgabewert versieht, hat den alten Zustand mit
    mehr Zeremonie.

    **Die Trennlinie ist der Rechenmodus.** Pflicht ist, was in
    :func:`~src.reporting.output_writer.provenance.compute_mode` einfließt —
    denn ein falscher Wert *dort* lässt den Lauf im eigenen Artefakt etwas
    Falsches über sich behaupten, und genau das ist zweimal passiert. Alles
    andere beschreibt, was ein Lauf *nebenbei* tut (ein Protokoll schreiben, ein
    Szenario erzeugen), und ein ausgelassenes Feld heißt dort ohne Zweideutigkeit
    «nein».

    Dazu gehören die vier Angaben zum Sprachmodell: `save_run_metadata` liest sie
    ohnehin ohne Rückfall, sie waren also immer schon Pflicht — nur sagte es
    niemand, und ein Aufrufer erfuhr es als `AttributeError` mitten im Schreiben.
    """

    # `extra="forbid"`: Ein Tippfehler im Feldnamen ist ein Fehler und kein
    # stilles Zusatzfeld. Vorher trug der Namensraum, was man hineinschrieb —
    # `deterministic_ony=True` hätte niemand bemerkt.
    model_config = ConfigDict(extra="forbid")

    # --- Pflicht: fließt in den Rechenmodus ---------------------------------
    mock_llm: bool
    deterministic_only: bool
    llm_narrative: bool

    # --- Pflicht: beschreibt das Sprachmodell -------------------------------
    model: str
    base_url: str
    temperature: float
    max_tokens: int

    # --- Vorgabe: was ein Lauf nebenbei tut ---------------------------------
    #: Der Markt-Node ist an, wenn niemand ihn abschaltet.
    no_market: bool = False
    #: Protokoll, Szenarien und Lauf-Szenario entstehen, wenn niemand sie abwählt.
    no_protocol: bool = False
    no_scenarios: bool = False
    no_run_scenario: bool = False
    #: Der Redebedarf-Scheduler ist die Ausnahme, nicht die Voreinstellung.
    redebedarf: bool = False
    #: Ein Lauf redet, solange ihn niemand leise stellt.
    quiet: bool = False

    # --- Vorgabe: wer dieser Lauf ist ---------------------------------------
    #: Der wievielte Lauf einer Folge. Ein einzelner Lauf ist der erste.
    run_index: int = 1
    #: **`None` heißt «keiner genannt», nicht «keiner benutzt».** Welcher Seed
    #: wirklich gezogen hat, steht in `state.config.seed`; `save_run_metadata`
    #: nimmt zuerst den und greift nur hilfsweise hierauf zurück.
    seed: int | None = None
    #: Ohne Namen gilt der aus `simulation_config.json`.
    simulation_name: str | None = None
    simulation_description: str | None = None


def run_args_from(base: object, *, run_index: int, seed: int | None) -> RunArgs:
    """Aus einem beliebigen Träger die Lauf-Argumente eines Teillaufs bauen.

    *base* ist alles, was die Felder als Attribute trägt: das
    `argparse.Namespace` der CLI, ein `RunLaunchConfig`-Abbild des Dashboards
    oder ein fertiges :class:`RunArgs`. **Übernommen wird nur, was das Modell
    kennt** — ein Feld, das niemand liest, kommt gar nicht erst mit, und ein
    unbekanntes fällt auf, statt still mitzureisen.

    **Die Vorgabewerte stehen ausschließlich im Modell.** Diese Funktion setzt
    keinen einzigen: Was *base* nicht trägt, füllt Pydantic — und was Pflicht
    ist und fehlt, meldet Pydantic mit dem Feldnamen, bevor ein Artefakt
    entsteht. Vorher lag beides verstreut in ``getattr(args, "feld", False)``
    über drei Dateien, und jede Stelle hätte einen anderen Rückfall haben
    können.
    """

    vorhanden = {name: getattr(base, name) for name in RunArgs.model_fields if hasattr(base, name)}
    return RunArgs(**{**vorhanden, "run_index": run_index, "seed": seed})
