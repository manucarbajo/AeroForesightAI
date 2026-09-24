"""Das Bedienfeld bleibt ein Bedienfeld (P1.6).

P1.1 hat gezählt, wie viele Entscheidungen bis zum Start nötig sind — drei, und
das stimmt bis heute. P1.5 hat geprüft, dass fünf Zonen den Bildschirm füllen
und keine Seite scrollt — stimmt auch. Trotzdem war die linke Spalte danach
**10,7 Bildschirme** hoch, trug 752 Wörter und 122 Eingabefelder, und der
Start-Knopf lag 6,1 Bildschirme tief.

Der Grund: **Ein Kriterium, das die Anzahl misst, sagt nichts über die
Erreichbarkeit.** In einer 1400 px breiten Seite fielen beide zusammen, in einer
336-px-Spalte liefen sie auseinander.

Dieser Wächter misst deshalb das, was schiefging: **Umfang**. Er kann keine
Pixel zählen — dafür bräuchte er einen Browser —, aber er zählt die Größen, aus
denen die Pixel entstehen: Eingabefelder, Wörter, Textblöcke. Wer den Editor
wieder in die Spalte schiebt, bekommt einen roten Test statt einer Seite, die
erst beim Öffnen auffällt.
"""

from __future__ import annotations

import pytest
from dash import html

from dashboard.web.config_editor import TABS, controls, start_flow, tab_layout
from dashboard.web.pages import launch as launch_page
from dashboard.web.pages import setup as setup_page
from dashboard.web.state import initial_draft_dict

#: Was das Bedienfeld höchstens tragen darf. Die Zahlen sind aus dem gemessenen
#: Ziel abgeleitet — die Spalte soll auf **einen** Bildschirm passen — und
#: bewusst mit Luft gesetzt: Der Wächter soll den Rückfall fangen, nicht jede
#: zusätzliche Zeile verbieten.
MAX_WOERTER = 160
MAX_TEXTBLOECKE = 30

_FELD_TYPEN = {controls.CFG, controls.CFG_BOOL}


def _walk(node):
    yield node
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            yield from _walk(child)
    elif children is not None:
        yield from _walk(children)


def _fields(node) -> set[str]:
    found: set[str] = set()
    for item in _walk(node):
        identifier = getattr(item, "id", None)
        if isinstance(identifier, dict) and identifier.get("type") in _FELD_TYPEN:
            found.add(str(identifier.get("field")))
    return found


def _words(node) -> int:
    return sum(len(item.split()) for item in _walk(node) if isinstance(item, str) and item.strip())


def _text_blocks(node) -> int:
    return sum(1 for item in _walk(node) if isinstance(item, str) and item.strip())


@pytest.fixture
def draft() -> dict:
    return initial_draft_dict()


# --- Kein Formular ---------------------------------------------------------


class TestDasBedienfeldIstKeinFormular:
    """Die tragende Zusage von P1.6."""

    def test_it_renders_no_input_field(self, draft):
        felder = _fields(launch_page.rail(draft))

        assert not felder, (
            f"Das Bedienfeld rendert Eingabefelder: {sorted(felder)}. "
            "Eingestellt wird im Bereich «Einrichten» — hier steht nur, was "
            "eingestellt ist."
        )

    def test_it_shares_no_field_id_with_the_setup_area(self, draft):
        """Beide liegen gleichzeitig im DOM; eine doppelte ID ist ein Laufzeitfehler."""

        doppelt = _fields(launch_page.rail(draft)) & _fields(setup_page.layout(draft))

        assert not doppelt, f"Feld(er) doppelt: {sorted(doppelt)}"

    @pytest.mark.parametrize("tab", [value for _, value in TABS])
    def test_it_shares_no_field_id_with_any_editor_tab(self, tab, draft):
        doppelt = _fields(launch_page.rail(draft)) & _fields(tab_layout(tab, draft))

        assert not doppelt, f"Feld(er) doppelt in «{tab}»: {sorted(doppelt)}"


# --- Und es bleibt schlank -------------------------------------------------


class TestDasBedienfeldBleibtSchlank:
    """Umfang statt Anzahl — das Maß, das P1.1 und P1.5 gefehlt hat."""

    def test_it_stays_short(self, draft):
        woerter = _words(launch_page.rail(draft))

        assert woerter <= MAX_WOERTER, (
            f"Das Bedienfeld trägt {woerter} Wörter (erlaubt: {MAX_WOERTER}). "
            "Vor P1.6 waren es 752, und die Spalte war zehn Bildschirme hoch."
        )

    def test_it_stays_flat(self, draft):
        bloecke = _text_blocks(launch_page.rail(draft))

        assert bloecke <= MAX_TEXTBLOECKE, f"{bloecke} Textblöcke im Bedienfeld"

    def test_the_counting_would_notice_the_editor_coming_back(self, draft):
        """Kontrolle: Der Zähler zählt wirklich, statt immer klein zu sein.

        Der Rückfall wird mit den Editor-Bereichen nachgestellt, die seit P1.7
        Schritte der Schrittfolge sind — vorher waren sie Reiter unter
        `config_editor.layout`, die es so nicht mehr gibt.
        """

        rueckfall = html.Div(
            [launch_page.rail(draft)] + [tab_layout(tab, draft) for _, tab in TABS]
        )

        assert _words(rueckfall) > MAX_WOERTER
        assert _fields(rueckfall)


# --- Hinweise werden gezählt, nicht aufgezählt (P7.5-U5.1) ------------------


class TestDieHinweiseWerdenGezaehlt:
    """Von Haiko entschieden am 2026-09-15: ein Satz und ein Zähler, ausführlich im Prüfschritt."""

    def _mit_zwei_hinweisen(self, draft) -> dict:
        return {**draft, "run_count": 2, "use_seed": False, "no_scenarios": True}

    def test_two_notes_become_one_counter_that_names_the_place(self, draft):
        entwurf = self._mit_zwei_hinweisen(draft)
        ausfuehrlich = start_flow._warnings(entwurf, [])
        assert len(ausfuehrlich) >= 2, "Vorbedingung: Der Entwurf trägt mehrere Hinweise"

        text = str(start_flow.preflight(entwurf, [], slot="rail", compact=True))

        assert f"{len(ausfuehrlich)} Hinweise" in text
        assert "«Prüfen & Starten»" in text
        assert "Mehrere Wiederholungen ohne festen Zufallsstartwert" not in text

    def test_no_notes_no_counter(self, draft):
        """Zehn Ticks: Kein ausgelieferter Verlauf endet davor, also keine Horizontlücke."""

        entwurf = {
            **draft,
            "rounds": 10,
            "run_count": 1,
            "no_scenarios": False,
            "apply_custom_overrides": True,
        }
        assert start_flow._warnings(entwurf, []) == [], "Vorbedingung: ein Entwurf ohne Hinweis"

        assert "Vor dem Start" not in str(
            start_flow.preflight(entwurf, [], slot="rail", compact=True)
        )

    def test_a_blocking_finding_stays_an_error(self, draft):
        text = str(
            start_flow.preflight(draft, ["Seed darf nicht negativ sein"], slot="rail", compact=True)
        )

        assert "Der Lauf kann so nicht starten" in text
        assert "af-alert--error" in text, "Ein Befund, der den Start verhindert, ist kein Ratschlag"
        assert "«Prüfen & Starten»" in text


# --- Was es dafür tragen muss ----------------------------------------------


class TestWasDasBedienfeldTraegt:
    def test_the_start_button_is_there(self, draft):
        assert "run-start" in str(launch_page.rail(draft))

    def test_the_preflight_slot_is_there(self, draft):
        slots = {
            (item.id or {}).get("slot")
            for item in _walk(launch_page.rail(draft))
            if isinstance(getattr(item, "id", None), dict)
            and item.id.get("type") == start_flow.SLOT
        }

        assert "preflight" in slots

    def test_the_three_rows_say_what_is_set(self, draft):
        gerendert = str(launch_page.summary_rows(draft))

        assert "Szenario" in gerendert
        assert "Länge" in gerendert
        assert "Rechenmodus" in gerendert

    def test_the_rows_name_the_chosen_preset(self, draft):
        from dashboard.config_catalog import list_sweep_presets

        presets = list_sweep_presets()
        if not presets:
            pytest.skip("Keine Sweep-Presets unter configs/sweeps/ vorhanden.")

        draft["scenario_mode"] = "sweep"
        draft["sweep_id"] = presets[0].id

        assert presets[0].name in str(launch_page.summary_rows(draft))

    def test_the_rows_are_links_into_the_setup_area(self, draft):
        """Geändert wird dort, wo die Felder stehen — nicht hier.

        Die Adresse wird aus `shell.ROUTES` abgeleitet statt hingeschrieben:
        Sie ist mit P1.7 schon einmal umgezogen, und ein Test, der den alten
        Pfad festnagelt, hätte den Umzug als Fehler gemeldet statt ihn zu
        sichern.
        """

        from dashboard.web import routing, shell

        einrichten = next(route for route, label in shell.ROUTES if label == "Einrichten")
        assert f"href='{routing.url(einrichten)}'" in str(launch_page.summary_rows(draft))

    def test_the_heading_says_it_is_the_next_run(self, draft):
        """P7.5-U5.1: Daneben steht die Szene eines fertigen Laufs — «Lauf» ließ offen, welcher."""

        ueberschriften = [
            k.children for k in _walk(launch_page.rail(draft)) if isinstance(k, html.H1)
        ]

        assert ueberschriften == [launch_page.UEBERSCHRIFT] == ["Nächster Lauf"]

    def test_the_footer_carries_only_the_start(self, draft):
        """P7.5-U5.1: Unter dem Start-Knopf stand eine Zeile, die die Stand-Zeilen wiederholte
        und das Szenario mit seiner Kennung nannte («Szenario: basis»)."""

        fuss = next(
            k
            for k in _walk(launch_page.rail(draft))
            if "af-rail-footer" in str(getattr(k, "className", "") or "")
        )

        assert "run-start" in str(fuss)
        # Gezählt wird ein Textabsatz, nicht Wörter: Der Knopf trägt neben «Start»
        # den Symbolnamen `play_arrow` als Text.
        assert not [
            k for k in _walk(fuss) if isinstance(k, html.P)
        ], f"Unter dem Start-Knopf steht wieder eine Zeile: {fuss}"

    def test_the_mode_is_named_in_two_words(self, draft):
        """Der volle Optionstext ist ein Satz und passt hier nicht hin."""

        from dashboard.web.config_editor import compute_mode

        kurz = compute_mode.short_label(draft)

        assert kurz and len(kurz.split()) <= 3
        assert kurz in {label for label in compute_mode.SHORT_LABELS.values()}
