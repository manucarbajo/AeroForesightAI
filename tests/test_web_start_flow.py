"""Der geführte Start-Ablauf (P1.1).

Zwei Zusagen tragen dieses Paket, und beide sind hier mechanisch geprüft statt
nach Augenschein: **höchstens drei Entscheidungen** bis zum Start, und **kein
Feld steht doppelt** — der geführte Block und der aktive Tab liegen gleichzeitig
im DOM, dieselbe Feld-ID zweimal ist für Dash ein Fehler.

Beide Prüfungen laufen über den gerenderten Komponentenbaum, nicht über eine
gepflegte Liste von Feldnamen. Eine Liste fängt einen Rückfall an bekannter
Stelle; ein Baumdurchlauf fängt auch das Feld, an das niemand gedacht hat.
"""

from __future__ import annotations

import pytest
from dash import html

from dashboard.config_catalog import list_sweep_presets
from dashboard.web import components as ui
from dashboard.web.config_editor import TABS, controls, start_flow, tab_layout
from dashboard.web.state import initial_draft_dict

#: Was der geführte Ablauf höchstens fragen darf, bevor jemand «Start» drückt.
#: Die Zahl steht so im Projektplan (P1.1, «messbar gemacht am 2026-08-26»).
MAX_ENTSCHEIDUNGEN = 3

_FELD_TYPEN = {controls.CFG, controls.CFG_BOOL}


def _walk(node, *, skip_details: bool):
    """Komponentenbaum durchlaufen; auf Wunsch ohne die zugeklappten Teile."""

    if skip_details and isinstance(node, html.Details):
        return
    yield node
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            yield from _walk(child, skip_details=skip_details)
    elif children is not None:
        yield from _walk(children, skip_details=skip_details)


def _fields(node, *, skip_details: bool = False) -> set[str]:
    found: set[str] = set()
    for item in _walk(node, skip_details=skip_details):
        identifier = getattr(item, "id", None)
        if isinstance(identifier, dict) and identifier.get("type") in _FELD_TYPEN:
            found.add(str(identifier.get("field")))
    return found


@pytest.fixture
def draft() -> dict:
    return initial_draft_dict()


# --- Die drei Entscheidungen -----------------------------------------------


class TestDreiEntscheidungen:
    """Das Abnahmekriterium von P1.1, als Zusicherung statt als Absichtserklärung."""

    def test_the_guided_flow_asks_at_most_three_things(self, draft):
        sichtbar = _fields(start_flow.layout(draft), skip_details=True)

        assert len(sichtbar) <= MAX_ENTSCHEIDUNGEN, (
            "Der geführte Ablauf fragt mehr als drei Dinge ab: "
            f"{sorted(sichtbar)}. Was nicht zu den drei Entscheidungen gehört, "
            "gehört hinter «Feinabstimmung» oder in die Tabs."
        )

    def test_the_three_are_scenario_scope_and_mode(self, draft):
        """Nicht *irgendwelche* drei — diese drei."""

        assert _fields(start_flow.layout(draft), skip_details=True) == {
            start_flow.FIELD,
            "rounds",
            "compute_mode",
        }

    def test_the_fine_print_is_reachable_but_folded_away(self, draft):
        """Wiederholungen und Zufallsstartwert bleiben erreichbar — nur nicht vorn."""

        alle = _fields(start_flow.layout(draft))
        sichtbar = _fields(start_flow.layout(draft), skip_details=True)

        assert {"run_count", "run_all_sweeps", "use_seed", "seed"} <= alle - sichtbar

    def test_the_counting_would_notice_a_fourth_field(self, draft):
        """Kontrolle: Der Zähler zählt wirklich, statt immer drei zu finden."""

        block = html.Div([start_flow.layout(draft), controls.number("base_price", 100.0)])

        assert len(_fields(block, skip_details=True)) == MAX_ENTSCHEIDUNGEN + 1


# --- Kein Feld steht doppelt -----------------------------------------------


class TestKeinFeldStehtDoppelt:
    """Der geführte Block und der aktive Tab liegen gleichzeitig im DOM.

    Dash quittiert eine doppelt vergebene ID im Browser mit einem Fehler — und
    zwar zur Laufzeit, nicht beim Bauen. Ohne diesen Test fiele es erst
    demjenigen auf, der die Seite öffnet.
    """

    @pytest.mark.parametrize("tab", [value for _, value in TABS])
    def test_no_field_appears_in_both_the_guided_block_and_a_tab(self, tab, draft):
        doppelt = _fields(start_flow.layout(draft)) & _fields(tab_layout(tab, draft))

        assert not doppelt, f"Feld(er) doppelt in «{tab}»: {sorted(doppelt)}"

    @pytest.mark.parametrize("mode", ["basis", "sweep", "custom"])
    def test_that_holds_in_every_scenario_mode(self, mode, draft):
        draft["scenario_mode"] = mode
        if mode == "sweep":
            presets = list_sweep_presets()
            if not presets:
                pytest.skip("Keine Sweep-Presets unter configs/sweeps/ vorhanden.")
            draft["sweep_id"] = presets[0].id

        gefuehrt = _fields(start_flow.layout(draft))
        for _, tab in TABS:
            assert not (gefuehrt & _fields(tab_layout(tab, draft))), tab


# --- Auswahl ⇄ Entwurf -----------------------------------------------------


class TestDieSzenarioAuswahl:
    """Eine Entscheidung, aus der zwei Draft-Felder folgen."""

    def test_the_default_draft_starts_at_the_standard_baseline(self, draft):
        assert start_flow.of(draft) == start_flow.STANDARD

    def test_choosing_a_preset_sets_both_fields(self, draft):
        presets = list_sweep_presets()
        if not presets:
            pytest.skip("Keine Sweep-Presets unter configs/sweeps/ vorhanden.")

        draft[start_flow.FIELD] = presets[0].id
        result = start_flow.normalise(draft)

        assert result["scenario_mode"] == "sweep"
        assert result["sweep_id"] == presets[0].id
        assert start_flow.FIELD not in result, "die Auswahl selbst ist kein Draft-Feld"

    def test_choosing_a_preset_leaves_the_length_alone(self, draft):
        """Die Länge gehört dem Feld, nicht der Auswahl.

        Sie hier mitzusetzen hieße, dieselbe Zahl an zwei Stellen zu führen:
        `normalise` läuft bei **jeder** Änderung, das Eingabefeld schriebe seinen
        alten Wert beim nächsten Abgleich zurück, und im Fenster stünde eine
        andere Zahl als im Lauf. Am laufenden System nachgestellt und deshalb
        hier festgehalten.
        """

        preset = next((s for s in list_sweep_presets() if s.max_ticks != draft["rounds"]), None)
        if preset is None:
            pytest.skip("Kein Preset mit abweichender Länge vorhanden.")
        vorher = draft["rounds"]
        draft[start_flow.FIELD] = preset.id

        assert start_flow.normalise(draft)["rounds"] == vorher

    def test_the_preset_length_is_at_least_said_out_loud(self, draft):
        """Wenn sie nicht gesetzt wird, muss sie wenigstens dastehen."""

        preset = next((s for s in list_sweep_presets() if s.max_ticks != draft["rounds"]), None)
        if preset is None:
            pytest.skip("Kein Preset mit abweichender Länge vorhanden.")
        draft["scenario_mode"] = "sweep"
        draft["sweep_id"] = preset.id

        assert f"{preset.max_ticks} Ticks" in str(start_flow.scenario_details(draft))

    def test_own_settings_are_their_own_choice(self, draft):
        draft[start_flow.FIELD] = start_flow.CUSTOM
        result = start_flow.normalise(draft)

        assert result["scenario_mode"] == "custom"
        assert result["apply_custom_overrides"] is True
        assert start_flow.of(result) == start_flow.CUSTOM

    def test_every_preset_is_offered(self):
        values = {option["value"] for option in start_flow.choice_options()}

        assert {preset.id for preset in list_sweep_presets()} <= values
        assert {start_flow.STANDARD, start_flow.CUSTOM} <= values


# --- Befunde am Feld -------------------------------------------------------


class TestBefundeStehenAmFeld:
    """P1.1: «Fehlermeldungen aus P0.3 direkt am Feld» — nicht nur gesammelt."""

    def test_every_input_carries_a_slot_for_its_findings(self, draft):
        slots = {
            (item.id or {}).get("field")
            for item in _walk(start_flow.layout(draft), skip_details=False)
            if isinstance(getattr(item, "id", None), dict) and item.id.get("type") == controls.ERROR
        }

        assert {"rounds", "seed"} <= slots

    def test_a_negative_seed_is_reported_at_the_seed_field(self, draft):
        draft["use_seed"] = True
        draft["seed"] = -1

        _slots, by_field = start_flow.live_state(draft)

        assert "seed" in by_field, f"kein Feldbezug, nur: {by_field}"
        assert any("seed" in message for message in by_field["seed"])
        assert str(ui.field_errors(by_field["seed"]))

    def test_a_healthy_draft_marks_no_field(self, draft):
        _slots, by_field = start_flow.live_state(draft)

        assert by_field == {}

    def test_the_preflight_points_at_the_marked_field(self, draft):
        draft["use_seed"] = True
        draft["seed"] = -1

        rendered = str(start_flow.preflight(draft, start_flow.errors_for(draft)))

        assert "kann so nicht starten" in rendered
        assert "am betroffenen Feld" in rendered


# --- Was der Callback nachfüllt --------------------------------------------


def test_live_state_fills_every_slot_the_layout_declares(draft):
    """Ein Slot ohne Inhalt bliebe nach der ersten Änderung leer stehen.

    Seit P1.6 liegen die Slots in **zwei** Bäumen: die Szenario-Beschreibung im
    Bereich «Einrichten», der Preflight im Bedienfeld links. `_live` füllt beide
    über dieselbe Pattern-ID — der Test muss deshalb beide abgehen. Nur einen zu
    prüfen hieße, den anderen leer stehen zu lassen und es nicht zu merken.
    """

    from dashboard.web.pages import launch as launch_page

    erklaert = {
        (item.id or {}).get("slot")
        for baum in (start_flow.layout(draft), launch_page.rail(draft))
        for item in _walk(baum, skip_details=False)
        if isinstance(getattr(item, "id", None), dict) and item.id.get("type") == start_flow.SLOT
    }
    slots, _by_field = start_flow.live_state(draft)

    assert erklaert == set(slots)


def _groesse(klassen: set[str]) -> str | None:
    """Welche Schriftgröße für ein Element mit diesen Klassen gewinnt.

    **Nachgerechnet mit dem Kaskaden-Nachrechner aus `test_web_drawers`**, und
    das ist wichtiger, als es aussieht — zwei Näherungen davor haben nicht
    getragen:

    * Der erste Anlauf las **Klassennamen** und hielt jede Klasse mit
      `af-md--`-Präfix für eine Größe. Er schlug damit bei `af-md--these` an,
      das nur Farbe und Gewicht setzt.
    * Der zweite suchte die Klasse **im Stylesheet** und fand für `af-md` die
      Regel `.af-md.af-md--caption`, weil deren Selektor die Zeichenfolge
      enthält — gemeldet wurde damit 12 px für einen 15-px-Text.

    Hier gewinnt die Regel, die auch im Browser gewinnt: höchste Spezifität,
    bei Gleichstand die spätere in der Datei.
    """

    from tests.test_web_drawers import _sieger

    try:
        _, wert = _sieger(klassen, "font-size")
    except (AssertionError, StopIteration, ValueError):
        return None
    return wert.strip() or None


class TestDieBegruendungStoertDieEntscheidungNicht:
    """**D3, entschieden am 2026-09-12.** Sichtbar sind These und zwei Sätze.

    Vorher stand die ganze Begründung offen: je Szenario 1163 bis 2429 Zeichen
    zusammen mit der These, beim Standardrahmen 2261 allein aus Begründung und
    Vorbehalt. Das Audit nennt das die Tonlage eines Projektplans. **Die
    Ehrlichkeit bleibt vollständig erreichbar** — der Rest steht einen Klick
    tiefer, hinter «Begründung und Quellen».

    **Und D3 ist die Voraussetzung von U1.2.** Der erste Anlauf der Breiten ist
    daran gescheitert, dass dieser Block zwei Textgrößen mischte: Ein Deckel in
    Pixeln kann die Zusage «höchstens 75 Zeichen je Zeile» nicht für zwei
    Größen halten — 608 px tragen bei 15 px 66 Zeichen und bei 12 px 106. Die
    Regel, die daraus folgt, steht hier als Zusage: **ein Leseblock hat eine
    Textgröße.**
    """

    @staticmethod
    def _rahmen():
        from dashboard.config_catalog import list_sweep_presets
        from src.config_loader import load_properties_config

        rahmen = [("Standard-Ausgangslage", load_properties_config().kohaerenz)]
        rahmen += [(p.name, p.kohaerenz) for p in list_sweep_presets() if p.kohaerenz]
        return [(name, k) for name, k in rahmen if k is not None]

    def test_the_visible_layer_carries_one_text_size(self):
        """Die tragende Zusage — sie macht U1.2 überhaupt möglich.

        **Gemessen wird die Größe, nicht der Klassenname.** Der erste Anlauf
        dieses Wächters meldete jede Klasse mit `af-md--`-Präfix und schlug
        damit auch bei `af-md--these` an — einer Betonung, die Farbe und
        Gewicht setzt und die Größe gerade **nicht** anfasst. Nachgeschlagen
        wird deshalb im Stylesheet, welche Klasse eine `font-size` trägt.
        """

        for name, kohaerenz in self._rahmen():
            block = start_flow._kohaerenz_block(kohaerenz)
            sichtbar = [kind for kind in block.children if not isinstance(kind, html.Details)]
            groessen = {
                _groesse(set(str(getattr(kind, "className", "")).split()))
                for kind in sichtbar
                if _groesse(set(str(getattr(kind, "className", "")).split()))
            }

            assert len(groessen) <= 1, (
                f"«{name}»: Die sichtbare Ebene trägt {len(groessen)} Textgrößen "
                f"({sorted(groessen)}). Ein Leseblock hat eine Textgröße — sonst kann "
                "kein Pixeldeckel die Zusage «höchstens 75 Zeichen je Zeile» halten: "
                "608 px tragen bei 15 px 66 Zeichen und bei 12 px 106."
            )

    def test_only_two_sentences_of_the_reasoning_are_open(self):
        for name, kohaerenz in self._rahmen():
            offen, _ = start_flow.satzanfang(kohaerenz.begruendung)
            saetze = len(start_flow._SATZENDE.split(offen))

            assert saetze <= start_flow.SAETZE_OFFEN, (
                f"«{name}»: {saetze} Sätze stehen offen, erlaubt sind "
                f"{start_flow.SAETZE_OFFEN}."
            )
            assert len(offen) < len(kohaerenz.begruendung), (
                f"«{name}»: Die ganze Begründung steht offen ({len(offen)} Zeichen) — "
                "dann ist D3 nicht umgesetzt, sondern nur umbenannt."
            )

    def test_nothing_is_lost_behind_the_disclosure(self):
        """**Weggeklappt ist nicht weggelassen.** Der Text bleibt vollständig.

        Ohne diese Zusage wäre D3 ein Textverlust: Ein Satzschnitt, der den
        Rest wegwirft, nimmt der Variante C ihre einzige Absicherung.
        """

        for name, kohaerenz in self._rahmen():
            offen, rest = start_flow.satzanfang(kohaerenz.begruendung)
            zusammen = " ".join(teil for teil in (offen, rest) if teil)

            assert zusammen == " ".join(kohaerenz.begruendung.split()), (
                f"«{name}»: Der Satzschnitt verliert Text. Offen plus Rest muss die "
                "ganze Begründung sein."
            )

    def test_the_sentence_split_holds_on_every_shipped_reasoning(self):
        """**Die Machbarkeit ist gemessen, nicht angenommen.**

        Ein Satzschnitt am Punkt ist fragil, sobald eine Abkürzung oder eine
        Dezimalzahl im Text steht — «z. B.» würde nach «z.» trennen und einen
        halben Satz zeigen. Am 2026-09-12 enthielt keine der fünf
        Begründungen so etwas; wer eine schreibt, die es tut, bekommt hier
        Bescheid, bevor ein Leser den Bruch sieht.
        """

        import re

        stolpersteine = {
            "Abkürzung": r"\b(?:z\.\s?B\.|bzw\.|ca\.|vgl\.|Nr\.|S\.\s?\d|u\.\s?a\.|d\.\s?h\.)",
            "Dezimalzahl": r"\d\.\d",
        }
        befunde = []
        for name, kohaerenz in self._rahmen():
            for art, muster in stolpersteine.items():
                treffer = re.findall(muster, kohaerenz.begruendung)
                if treffer:
                    befunde.append(f"«{name}»: {art} {treffer}")

        assert not befunde, (
            "Diese Begründungen enthalten etwas, woran der Satzschnitt scheitert:\n  "
            + "\n  ".join(befunde)
            + "\n\nEntweder umformulieren, oder D3 braucht ein eigenes Feld für die "
            "sichtbare Kurzfassung (die dritte Variante der Entscheidung)."
        )

    def test_the_disclosure_names_what_it_holds(self):
        for name, kohaerenz in self._rahmen():
            block = start_flow._kohaerenz_block(kohaerenz)
            klappen = [kind for kind in block.children if isinstance(kind, html.Details)]

            assert len(klappen) == 1, (
                f"«{name}»: {len(klappen)} Klappen im Block. D3 hat **eine** entschieden — "
                "zwei übereinander lesen sich als Formular (U1.4)."
            )
            assert "Begründung und Quellen" in str(klappen[0]), (
                f"«{name}»: Die Klappe sagt nicht, dass die Begründung darin steckt. "
                "Sie hieß bis D3 «Quellen und was davon nicht belegt ist» und trug nur "
                "zwei der vier Texte."
            )
