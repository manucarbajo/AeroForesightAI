"""Grounded chat exploration over completed simulation runs."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from src.llm import LLMCallable, OllamaClient, OllamaConfig, auf_deutsch
from src.logging_setup import stdio_auf_utf8
from src.orchestration.checkpoint_manager import CheckpointManager
from src.reporting.aussagen_pruefung import faktenblatt_saetze, laufzeilen, pruefe
from src.reporting.output_writer import OUTPUT_DIR
from src.reporting.run_scenario_generator.factors import _load_factor_catalog, faktor_namen

EXPLORER_INSTRUCTIONS = """You are an expert data analyst and simulation explorer for an aviation foresight scenario.
Your task is to answer the user's question comprehensively and helpfully using ONLY the GROUND TRUTH DATA block below.

Rules for your answers:
1. Be Detailed: Explain the 'why' and 'how' based on the data. Do not just give 1-sentence answers if the data allows for a deeper explanation.
2. Grounding: Never invent numbers, ticks, prices, booking rates, or events. Only use what is in the data.
3. Missing Data: If the answer cannot be deduced from the data at all, reply: "Das ist nicht in den Run-Daten enthalten."
4. Structure: Use bullet points or short paragraphs for readability.
5. Citations: Always cite the specific tick numbers (e.g. "Ab Tick 15...") when you reference metrics or events.
6. Language: Answer in German (unless the user explicitly asks in another language).
"""


def parse_tick_hint(text: str) -> int | None:
    """Optional tick number from a natural-language question (e.g. 'bei Tick 15')."""

    match = re.search(r"(?:tick|periode)\s*(\d+)", text, flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


@dataclass(frozen=True)
class RunExplorerContext:
    run_id: str
    run_dir: Path
    tick_mechanics: dict[str, Any]
    event_log: list[dict[str, Any]]
    price_history: list[dict[str, Any]]
    factors_timeseries: list[dict[str, Any]]
    metadata: dict[str, Any]
    run_scenario: dict[str, Any] | None
    focus_tick: int | None
    checkpoint_tick: int | None
    checkpoint_snapshot: dict[str, Any] | None


def resolve_run_dir(run_id: str, *, outputs_root: Path | str | None = None) -> Path:
    root = Path(outputs_root or OUTPUT_DIR)
    run_dir = root / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    return run_dir


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _checkpoint_path(run_dir: Path, run_id: str, tick: int) -> Path | None:
    manager = CheckpointManager(checkpoint_dir=run_dir / "checkpoints")
    candidates = [
        manager.checkpoint_dir / run_id / f"tick_{tick:04d}.json",
        manager.checkpoint_dir / f"tick_{tick:04d}.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _summarize_checkpoint(state: dict[str, Any]) -> dict[str, Any]:
    clock = state.get("clock", {})
    market_metrics = state.get("market_metrics", {})
    return {
        "current_tick": clock.get("current_tick"),
        "max_ticks": clock.get("max_ticks"),
        "market_metrics": market_metrics,
        "factor_states": {
            factor_id: factor.get("current_state")
            for factor_id, factor in (state.get("environment", {}).get("factors") or {}).items()
        },
        "event_count": len(state.get("event_log") or []),
        "population_size": len(state.get("population_individuals") or []),
    }


def _load_factors_timeseries(run_dir: Path) -> list[dict[str, Any]]:
    """Load factor rows from JSON (legacy) or ``timeseries/factors.csv`` (standard)."""

    json_path = run_dir / "factors_timeseries.json"
    if json_path.is_file():
        payload = _load_json(json_path, [])
        if isinstance(payload, list):
            return payload

    csv_path = run_dir / "timeseries" / "factors.csv"
    if not csv_path.is_file():
        return []

    import csv

    rows: list[dict[str, Any]] = []
    with csv_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            parsed: dict[str, Any] = dict(row)
            tick_raw = parsed.get("tick")
            if tick_raw not in (None, ""):
                try:
                    parsed["tick"] = int(tick_raw)
                except ValueError:
                    pass
            rows.append(parsed)
    return rows


def load_run_context(
    run_id: str,
    *,
    focus_tick: int | None = None,
    outputs_root: Path | str | None = None,
) -> RunExplorerContext:
    run_dir = resolve_run_dir(run_id, outputs_root=outputs_root)
    tick_mechanics = _load_json(run_dir / "tick_mechanics.json", {"ticks": []})
    event_log = _load_json(run_dir / "event_log.json", [])
    price_history = _load_json(run_dir / "price_history.json", [])
    factors_timeseries = _load_factors_timeseries(run_dir)
    metadata = _load_json(run_dir / "run_metadata.json", {})
    run_scenario_raw = _load_json(run_dir / "run_scenario.json", None)
    run_scenario = run_scenario_raw if isinstance(run_scenario_raw, dict) else None

    checkpoint_snapshot = None
    checkpoint_tick = None
    if focus_tick is not None and focus_tick >= 1:
        checkpoint_tick = focus_tick
        ck_path = _checkpoint_path(run_dir, run_id, focus_tick)
        if ck_path is not None:
            payload = json.loads(ck_path.read_text(encoding="utf-8"))
            checkpoint_snapshot = _summarize_checkpoint(payload.get("state", {}))

    return RunExplorerContext(
        run_id=run_id,
        run_dir=run_dir,
        tick_mechanics=tick_mechanics,
        event_log=event_log,
        price_history=price_history,
        factors_timeseries=factors_timeseries,
        metadata=metadata,
        run_scenario=run_scenario,
        focus_tick=focus_tick,
        checkpoint_tick=checkpoint_tick,
        checkpoint_snapshot=checkpoint_snapshot,
    )


def _select_ticks(context: RunExplorerContext, limit: int = 8) -> list[dict[str, Any]]:
    ticks = list(context.tick_mechanics.get("ticks") or [])
    if not ticks:
        return []
    if context.focus_tick is not None:
        selected = [row for row in ticks if int(row.get("tick", -1)) == context.focus_tick]
        if selected:
            return selected
        nearby = sorted(ticks, key=lambda row: abs(int(row.get("tick", 0)) - context.focus_tick))
        return nearby[:limit]
    if len(ticks) <= limit:
        return ticks
    # Gesamtlauf: Anfang, Ende und gleichmäßige Stichprobe
    if limit >= len(ticks):
        return ticks
    head = ticks[:3]
    tail = ticks[-max(3, limit // 2) :]
    middle_budget = max(0, limit - len(head) - len(tail))
    if middle_budget <= 0:
        return head + tail
    step = max(1, (len(ticks) - len(head) - len(tail)) // middle_budget)
    middle = ticks[len(head) : len(ticks) - len(tail) : step][:middle_budget]
    return head + middle + tail


def _build_run_summary(context: RunExplorerContext) -> dict[str, Any]:
    ticks = list(context.tick_mechanics.get("ticks") or [])
    prices = list(context.price_history)
    if not ticks and not prices:
        return {"note": "Keine Zeitreihen im Run."}

    summary: dict[str, Any] = {
        "ticks_recorded": len(ticks),
        "events_total": len(context.event_log),
    }
    if ticks:
        booking = [
            float(row["booking_rate"]) for row in ticks if row.get("booking_rate") is not None
        ]
        if booking:
            summary["booking_rate_start"] = booking[0]
            summary["booking_rate_end"] = booking[-1]
            summary["booking_rate_min"] = min(booking)
            summary["booking_rate_max"] = max(booking)
    if prices:
        price_vals = [float(row["price"]) for row in prices if row.get("price") is not None]
        if price_vals:
            summary["ticket_price_start"] = price_vals[0]
            summary["ticket_price_end"] = price_vals[-1]
            summary["ticket_price_min"] = min(price_vals)
            summary["ticket_price_max"] = max(price_vals)
    if context.metadata:
        summary["ticks_completed"] = context.metadata.get("ticks_completed")
        summary["ticks_max"] = context.metadata.get("ticks_max")
        summary["model"] = context.metadata.get("model")
    return summary


def _select_events(context: RunExplorerContext, limit: int = 20) -> list[dict[str, Any]]:
    events = list(context.event_log)
    if context.focus_tick is not None:
        tick_events = [event for event in events if event.get("round_number") == context.focus_tick]
        if tick_events:
            return tick_events
    delta_events = [event for event in events if "[delta:" in str(event.get("description", ""))]
    if delta_events:
        return delta_events[-limit:]
    return events[-limit:]


def _context_tick_limit(context: RunExplorerContext) -> int:
    return 8 if context.focus_tick is not None else 24


def build_grounded_context_block(context: RunExplorerContext) -> str:
    lines = [
        f"run_id={context.run_id}",
        f"simulation={context.metadata.get('simulation_name', context.metadata.get('name', 'unknown'))}",
    ]
    # Die Richtung jeder Kerngröße als Satz, vor den Rohdaten (P8-V3). Am
    # 2026-09-29 antwortete `llama3.2` auf «Ist die Buchungsrate gestiegen oder
    # gesunken?» mit «gestiegen», während sie fiel — aus Zahlenreihen gedeutet.
    # Eine Frage zu einem einzelnen Tick bekommt es ebenso: Es beschreibt den Lauf.
    faktenblatt = faktenblatt_saetze(
        context.run_dir, context.factors_timeseries, faktor_namen(_load_factor_catalog())
    )
    if faktenblatt:
        lines.append("faktenblatt (Verlauf über den ganzen Lauf, von Python gerechnet):")
        lines.extend(f"- {satz}" for satz in faktenblatt)
    if context.tick_mechanics.get("reading_guide"):
        lines.append(f"reading_guide: {context.tick_mechanics['reading_guide']}")

    lines.append("run_summary:")
    lines.append(json.dumps(_build_run_summary(context), ensure_ascii=False, indent=2))

    selected_ticks = _select_ticks(context, limit=_context_tick_limit(context))
    if selected_ticks:
        lines.append("tick_mechanics:")
        lines.append(json.dumps(selected_ticks, ensure_ascii=False, indent=2))
    else:
        lines.append("tick_mechanics: []")

    selected_events = _select_events(context)
    if selected_events:
        lines.append("event_log:")
        lines.append(json.dumps(selected_events, ensure_ascii=False, indent=2))
    else:
        lines.append("event_log: []")

    if context.price_history:
        if context.focus_tick is not None:
            price_rows = [
                row
                for row in context.price_history
                if row.get("round_number") == context.focus_tick
            ]
        else:
            price_rows = context.price_history[-min(24, len(context.price_history)) :]
        lines.append("price_history:")
        lines.append(json.dumps(price_rows, ensure_ascii=False, indent=2))

    if context.factors_timeseries:
        if context.focus_tick is not None:
            factor_rows = [
                row for row in context.factors_timeseries if row.get("tick") == context.focus_tick
            ]
        else:
            factor_rows = context.factors_timeseries[-min(24, len(context.factors_timeseries)) :]
        if factor_rows:
            lines.append("factors_timeseries:")
            lines.append(json.dumps(factor_rows, ensure_ascii=False, indent=2))

    if context.run_scenario:
        scenario_excerpt = {
            "title": context.run_scenario.get("title"),
            "summary": context.run_scenario.get("summary"),
            "run_narrative": context.run_scenario.get("run_narrative")
            or (context.run_scenario.get("narrative") or {}).get("run_narrative"),
            "factor_profile": context.run_scenario.get("factor_profile")
            or (context.run_scenario.get("narrative") or {}).get("factor_profile"),
            "agent_digest": context.run_scenario.get("agent_digest")
            or (context.run_scenario.get("narrative") or {}).get("agent_digest"),
            "scenario_alignment": context.run_scenario.get("scenario_alignment"),
            "scenarios": context.run_scenario.get("scenarios")
            or (context.run_scenario.get("narrative") or {}).get("scenarios"),
            "ground_truth": context.run_scenario.get("ground_truth"),
        }
        lines.append("run_scenario:")
        lines.append(json.dumps(scenario_excerpt, ensure_ascii=False, indent=2))

    if context.checkpoint_snapshot is not None:
        lines.append(f"checkpoint_tick_{context.checkpoint_tick}:")
        lines.append(json.dumps(context.checkpoint_snapshot, ensure_ascii=False, indent=2))

    return "\n".join(lines)


#: Eine Zahl in einem Text — mit Tausendertrennung und beiden Dezimalzeichen.
#:
#: Bewusst **ohne** Vorzeichen: «-5 %» und «5 %» sollen dieselbe Zahl finden,
#: sonst gälte ein Minuszeichen im Fließtext als eigene Behauptung.
#:
#: **Der abschließende Lookahead ist kein Schmuck.** Ohne ihn frisst die
#: Tausender-Alternative die Nachkommastellen: `0.4818` wurde als `0.481`
#: erkannt und zu **481** normalisiert — eine Buchungsrate von 48 % galt damit
#: als unbelegt, obwohl sie in den Daten stand. Mit `(?!\d)` scheitert der
#: Tausender-Zweig an der vierten Nachkommastelle und der einfache greift.
_ZAHL = re.compile(r"(?:\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?|\d+(?:[.,]\d+)?)(?!\d)")

#: Zahlen, die keine Aussage über den Lauf sind: Jahreszahlen wären es fast,
#: aber ein Tick hat keine Kalenderbedeutung (Invariante 5) — was hier steht,
#: sind Größen, die in **jedem** Text vorkommen und nichts behaupten.
_HARMLOS = frozenset({"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "100"})


#: Ob direkt hinter einer Zahl ein Prozentzeichen steht.
_PROZENT = re.compile(r"\s*(%|prozent)", re.IGNORECASE)


def _zerlegen(roh: str) -> tuple[float, int]:
    """Eine gefundene Zahl in (Wert, Nachkommastellen) zerlegen.

    **Die Trennzeichen sind mehrdeutig, und das ist der Kern der Arbeit hier.**
    Im Deutschen trennt das Komma die Nachkommastellen und der Punkt die
    Tausender, im Englischen umgekehrt — und eine Antwort des Sprachmodells
    kann beides enthalten. Entschieden wird deshalb nach der **Stellenzahl**,
    nicht nach dem Zeichen:

    - mehrere Trennzeichen → das letzte trennt die Nachkommastellen
    - genau eines mit **drei** Ziffern dahinter → Tausendertrennung (`1.080`)
    - genau eines mit anderer Stellenzahl → Nachkommastellen (`0.4818`, `140,38`)

    Der zweite Fall bleibt echt mehrdeutig — `1.080` kann tausendachtzig oder
    ein Komma-null-acht sein. Die Tausenderlesart ist die häufigere in einem
    Text über Bevölkerungszahlen, und der Fehler wäre in beide Richtungen
    gleich groß.

    **Der erste Anlauf las `0.4818` als 4818**, weil er nur ein- und
    zweistellige Nachkommateile kannte. Eine Buchungsrate von 48 % galt damit
    als unbelegt, obwohl sie in den Daten stand.
    """

    stellen = [i for i, zeichen in enumerate(roh) if zeichen in ".,"]
    if not stellen:
        return float(roh), 0

    letzte = stellen[-1]
    nachkomma = len(roh) - letzte - 1
    ist_tausender = len(stellen) == 1 and nachkomma == 3

    if ist_tausender:
        return float(roh.replace(".", "").replace(",", "")), 0

    ganz = roh[:letzte].replace(".", "").replace(",", "")
    return float(f"{ganz}.{roh[letzte + 1 :]}"), nachkomma


def _zahlen(text: str) -> list[tuple[str, float, int, bool]]:
    """Alle Zahlen eines Textes als (Schreibweise, Wert, Nachkommastellen, Prozent).

    **Die Genauigkeit wird mitgeführt**, weil die Prüfung sie braucht: «140» ist
    mit anderer Genauigkeit behauptet als «140,38», und danach richtet sich, wie
    streng verglichen wird.

    **Und das Prozentzeichen**, weil es eine Einheit ist und keine andere Zahl:
    Die Buchungsrate steht in den Daten als `0.4818`; «48,18 Prozent» ist
    dieselbe Aussage. Das als unbelegt zu markieren wäre ein Fehlalarm — und
    Fehlalarme sind hier teuer, weil sie den Leser darauf trainieren, die
    Markierung zu überlesen.
    """

    gefunden: list[tuple[str, float, int, bool]] = []
    for treffer in _ZAHL.finditer(text):
        roh = treffer.group(0)
        prozent = bool(_PROZENT.match(text[treffer.end() : treffer.end() + 10]))
        try:
            wert, stellen = _zerlegen(roh)
        except ValueError:
            continue
        gefunden.append((roh, wert, stellen, prozent))
    return gefunden


def _zahlwort(anzahl: int) -> str:
    return "1 Zahl" if anzahl == 1 else f"{anzahl} Zahlen"


@dataclass(frozen=True)
class Antwort:
    """Was der Explorer zurückgibt — **samt Prüfung** (P2.5).

    `ask` gab bis P2.5 eine Zeichenkette zurück, die niemand gegen die Daten
    hielt. Das Glossar nannte es «grounded Q&A ohne erfundene Zahlen»; im Code
    war es eine Bitte im Prompt.
    """

    text: str
    #: Zahlen der Antwort, die sich im Kontextblock **nicht** wiederfinden.
    unbelegt: tuple[str, ...] = ()
    #: Wie viele Zahlen überhaupt geprüft wurden. Ohne diese Angabe sähe eine
    #: Antwort ohne Zahlen genauso «sauber» aus wie eine vollständig belegte.
    geprueft: int = 0
    #: Wie viele **verschiedene** Zahlen im Kontextblock standen (B7c, 2026-09-03).
    #:
    #: **Das ist die Trennschärfe der Prüfung, und sie war unsichtbar.** Geprüft
    #: wird «steht diese Zahl irgendwo in den Laufdaten» — ohne Bezug zur Größe.
    #: Je mehr Zahlen im Block stehen, desto eher findet sich für eine erfundene
    #: zufällig eine Entsprechung. Ein «belegt» aus einem Block mit dreißig Zahlen
    #: wiegt anders als eines aus einem mit dreihundert, und wer die Antwort liest,
    #: konnte das bisher nicht wissen.
    kontextzahlen: int = 0
    #: Stellen, an denen die Antwort der Rechnung widerspricht (P8-V3) — eine
    #: Richtung gegen das Faktenblatt, ein Kalenderdatum, englischer Text. Je
    #: Befund die Zeile, die der Leser sieht (`aussagen_pruefung.Befund.zeile`).
    widersprueche: tuple[str, ...] = ()

    @property
    def belegt(self) -> bool:
        return not self.unbelegt

    def __str__(self) -> str:
        """Antwort mit angehängtem Vorbehalt — **immer**, nicht nur bei einem Befund.

        Damit bleibt jeder Aufrufer, der die Antwort als Text behandelt,
        richtig — und bekommt die Warnung mit, statt sie zu verlieren.

        **Bis P8-V3 stand die Auskunft nur unter einer markierten Antwort** (Rest
        von N10). Eine Antwort ohne unbelegte Zahl — oder ganz ohne Zahl — sah
        damit genauso aus wie eine ungeprüfte, und gerade die Antwort, deren
        falsche Prozentangabe durchgerutscht war, trug keinen Hinweis. Die
        Abwägung aus B7c («sonst geht die Markierung in einer Fußnote unter»)
        gilt weiter für die **Form**: Der Hinweis unter einer belegten Antwort ist
        ein Satz, die Warnung unter einer unbelegten bleibt ein Block.
        """

        widerspruch = ""
        if self.widersprueche:
            zeilen = "\n".join(f"- {zeile}" for zeile in self.widersprueche)
            widerspruch = (
                f"⚠️ **Widerspricht der Rechnung:**\n\n{zeilen}\n\n"
                "Den gerechneten Verlauf nennt das Faktenblatt am Anfang der Laufdaten."
            )

        if self.belegt:
            if widerspruch:
                return f"{self.text}\n\n{widerspruch}"
            if self.geprueft == 0:
                hinweis = (
                    "Prüfung: Diese Antwort enthält keine Zahl, die sich gegen die "
                    "Laufdaten halten ließe."
                )
            else:
                hinweis = (
                    f"Prüfung: {_zahlwort(self.geprueft)} der Antwort, gehalten gegen "
                    f"{self.kontextzahlen} verschiedene Zahlen der Laufdaten — jede kommt "
                    "dort vor. Ob an der richtigen Stelle, prüft das nicht."
                )
            return f"{self.text}\n\n_{hinweis}_"
        zahlen = ", ".join(self.unbelegt)
        return (
            f"{self.text}\n\n"
            f"⚠️ **Nicht in den Laufdaten belegt:** {zahlen}\n\n"
            "Diese Zahlen stehen so in keiner Datei dieses Laufs. Das kann eine "
            "eigene Rechnung des Sprachmodells sein (etwa eine Differenz) oder "
            "eine Erfindung — die Prüfung unterscheidet das nicht.\n\n"
            f"Geprüft wurden {self.geprueft} Zahlen der Antwort gegen "
            f"{self.kontextzahlen} verschiedene Zahlen der Laufdaten. Die Prüfung "
            "fragt, **ob** eine Zahl dort vorkommt — nicht, ob sie an der richtigen "
            "Stelle steht."
        ) + (f"\n\n{widerspruch}" if widerspruch else "")


def pruefe_gegen_kontext(antwort: str, kontext: str) -> Antwort:
    """Jede Zahl der Antwort gegen die Zahlen des Kontextblocks halten.

    **Was diese Prüfung beantwortet:** «Steht diese Zahl in den Laufdaten?» —
    **nicht** «ist diese Zahl richtig». Der Unterschied ist keine Spitzfindigkeit:
    Eine korrekt ausgerechnete Differenz («der Preis stieg um 12 Euro») steht
    nirgends in den Daten und wird deshalb als unbelegt markiert. Das ist
    **gewollt**. Ein Prüfer soll sehen, welche Zahl abgelesen und welche
    gerechnet ist; ob die Rechnung stimmt, kann diese Funktion nicht wissen.

    **Markieren statt zurückweisen**, und das ist die Produktentscheidung, die
    das Paket offengelassen hatte. Zurückweisen wäre die härtere Zusage, aber
    die falsche: Eine Antwort mit einer gerechneten Prozentangabe wäre damit
    unbrauchbar, obwohl sie stimmt. Eine markierte Antwort lässt den Leser
    entscheiden — und sie **verschweigt nichts**, was die Zurückweisung auch
    nicht täte.

    **Die Genauigkeit der Antwort bestimmt die Strenge.** «140» gilt als belegt,
    wenn irgendeine Kontextzahl auf 140 rundet; «140,38» muss auf zwei Stellen
    getroffen werden. Sonst wäre jede gerundete Angabe unbelegt, und die
    Markierung würde zum Rauschen, das niemand mehr liest.
    """

    kontextzahlen = _zahlen(kontext)
    im_kontext = [wert for _, wert, _, _ in kontextzahlen]
    # Auf Prozent gebracht: ein Anteil mal hundert, eine Prozentangabe wie sie ist.
    # **Ein Anteil hat Nachkommastellen** — im JSON trägt jede Gleitkommazahl
    # welche (`1.0`). Eine ganze Zahl ist ein Tick oder eine Personenzahl, und
    # «200 %» traf sonst Tick 2.
    als_prozent = [
        wert if prozent else wert * 100.0
        for _, wert, stellen, prozent in kontextzahlen
        if prozent or stellen > 0
    ]
    # Auf die Skala einer schlichten Zahl: eine Prozentangabe des Kontexts durch hundert.
    als_zahl = [wert / 100.0 if prozent else wert for _, wert, _, prozent in kontextzahlen]
    unbelegt: list[str] = []
    geprueft = 0

    for schreibweise, wert, stellen, prozent in _zahlen(antwort):
        if schreibweise.strip("0.,") == "" or schreibweise in _HARMLOS:
            continue
        geprueft += 1

        # Eine Prozentangabe wird gegen die Kontextzahlen **als Prozent** gehalten
        # — ein Anteil mal hundert, eine Prozentangabe wie sie ist — und nicht
        # gegen jede Zahl (N10, P8-V3). Bis dahin wurde «49 %» zu 0,49
        # verkleinert und auf null Stellen gerundet: 0,0, und jede Kontextzahl
        # unter 0,5 ebenfalls. Gegen einen echten Lauf galten damit 250 von 250
        # ganzzahligen Prozentangaben als belegt; nach der Skalenkorrektur allein
        # noch 137, weil «140 %» den Ticketpreis von 140 EUR traf.
        vergleich = als_prozent if prozent else als_zahl
        ziel = round(wert, stellen)
        if any(round(im_daten, stellen) == ziel for im_daten in vergleich):
            continue
        if schreibweise not in unbelegt:
            unbelegt.append(schreibweise)

    return Antwort(
        text=antwort,
        unbelegt=tuple(unbelegt),
        geprueft=geprueft,
        kontextzahlen=len(set(im_kontext)),
    )


class StateExplorer:
    def __init__(
        self,
        context: RunExplorerContext,
        llm: LLMCallable | None = None,
    ) -> None:
        self.context = context
        self.llm = llm or OllamaClient(OllamaConfig(temperature=0.2))

    def build_prompt(self, question: str) -> str:
        """Der Prompt einer Frage — die Sprachanweisung vor «ANSWER:» (P8-V2)."""

        grounded = build_grounded_context_block(self.context)
        return auf_deutsch(
            f"{EXPLORER_INSTRUCTIONS}\n\n"
            f"GROUND TRUTH DATA:\n{grounded}\n\n"
            f"USER QUESTION:\n{question.strip()}",
            schluss="\n\nANSWER:",
        )

    def ask(self, question: str) -> Antwort:
        """Fragen — und die Antwort **gegen die Daten halten** (P2.5).

        Der Rückgabewert ist seit P2.5 ein `Antwort`-Objekt statt einer
        Zeichenkette. Es verhält sich in `str()` wie vorher, trägt den Vorbehalt
        aber im Text mit; wer die einzelnen Befunde braucht, liest `unbelegt`.
        """

        # Ein Prompt, eine Stelle: Bis P8-V2 stand er hier ein zweites Mal wörtlich
        # neben `build_prompt`, und die Sprachanweisung hätte an beiden gefehlt.
        grounded = build_grounded_context_block(self.context)
        antwort = pruefe_gegen_kontext(self.llm.call(self.build_prompt(question)), grounded)
        # Und was sie behauptet, gegen den Verlauf gehalten (P8-V3). Eine Frage zu
        # einem einzelnen Tick darf etwas anderes über die Richtung sagen als der
        # ganze Lauf — dort gilt die Richtungsprüfung nicht.
        befunde = pruefe(antwort.text, laufzeilen(self.context.run_dir))
        if self.context.focus_tick is not None:
            befunde = [befund for befund in befunde if befund.art != "richtung"]
        return replace(antwort, widersprueche=tuple(befund.zeile for befund in befunde))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Grounded state explorer for simulation runs (M9)."
    )
    parser.add_argument(
        "--run-id", required=True, help="Run id under outputs/ (e.g. run_20260614T111705Z)."
    )
    parser.add_argument(
        "--tick",
        type=int,
        default=None,
        help="Focus on a specific tick (loads checkpoint if present).",
    )
    parser.add_argument(
        "--question", type=str, default=None, help="Single question; omit for interactive mode."
    )
    parser.add_argument(
        "--outputs-root", type=str, default=None, help="Override outputs directory."
    )
    parser.add_argument(
        "--mock-llm", action="store_true", help="Echo grounded context without calling Ollama."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    # **Diese CLI ist der schlimmste Fall von P3.10.** Der Vorbehalt einer
    # geprüften Antwort beginnt mit `⚠️` (P2.5), und `Antwort.__str__` hängt ihn
    # an — bei umgeleiteter Ausgabe warf `print` damit einen
    # `UnicodeEncodeError` statt zu warnen: ausgerechnet die Marke, die vor
    # unbelegten Zahlen schützt, riss den Aufruf ab. Dazu kommen die Antworten
    # des Modells selbst, die jedes Zeichen enthalten können.
    stdio_auf_utf8()
    args = _build_parser().parse_args(argv)
    context = load_run_context(
        args.run_id,
        focus_tick=args.tick,
        outputs_root=args.outputs_root,
    )

    if args.mock_llm:

        class _EchoLLM:
            def call(self, prompt: str) -> str:
                return (
                    "Mock explorer response (grounded context attached in prompt).\n"
                    "Use without --mock-llm and a running Ollama instance for real answers."
                )

        llm: LLMCallable = _EchoLLM()
    else:
        llm = OllamaClient(OllamaConfig(temperature=0.2))

    explorer = StateExplorer(context, llm=llm)

    if args.question:
        print(explorer.ask(args.question))
        return 0

    print(f"State explorer for {args.run_id} (tick focus={args.tick}). Type 'exit' to quit.")
    while True:
        try:
            question = input("\nFrage> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question or question.lower() in {"exit", "quit", "q"}:
            break
        print(explorer.ask(question))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
