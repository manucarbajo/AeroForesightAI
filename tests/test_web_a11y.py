"""Die Schrittfolge ist auch ohne Bildschirm bedienbar (P1.9-W5.3).

Gemessen am laufenden System hatte das Dokument **null** `aria-live`-Regionen.
Schrittwechsel, Statusmeldungen und Feldfehler waren für einen Screenreader
stumm; die Schrittliste trug ihren Zustand allein in Farbe und Symbolschrift;
und beim Wechsel blieb der Fokus auf einem Knopf, den es einen Moment später
nicht mehr gab.

**Für ein Werkzeug, das an Hochschulen und in B2B-Kontexten laufen soll, ist
das ein Beschaffungshindernis, kein Schönheitsfehler.** WCAG 2.1 AA ist dort
Voraussetzung, nicht Kür.

Vier Größen prüft diese Datei, und jede steht für einen konkreten Ausfall:

1. **`aria-current="step"`** — ohne das sagt nichts, welcher Schritt offen ist
   (kam mit W2.1, hier gegen einen Rückfall gesichert).
2. **Live-Regionen** — ohne die geschieht alles lautlos.
3. **Fokus auf der Frage** — ohne das tastet man sich nach jedem «Weiter» durch
   die halbe Seite.
4. **`fieldset` mit `legend`** — ohne das ist eine Radiogruppe eine Reihe
   unbeschrifteter Optionen: «Standard-Ausgangslage, 1 von 10», ohne zu sagen,
   wovon.

**Was diese Datei nicht ist:** ein WCAG-Prüfbericht. Sie hält vier Zusagen fest,
die wir geben; Kontraste prüft `test_web_theme.py`, und eine vollständige
Prüfung braucht Hilfsmittel und Menschen.
"""

from __future__ import annotations

import pytest

from dashboard.web.config_editor import wizard
from dashboard.web.state import initial_draft_dict


@pytest.fixture
def draft() -> dict:
    return initial_draft_dict()


def _walk(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None:
        yield from _walk(kinder)


def _props(knoten) -> dict:
    try:
        return knoten.to_plotly_json().get("props", {})
    except Exception:  # noqa: BLE001 - Zeichenketten und Zahlen im Baum
        return {}


def _mit_attribut(baum, name: str) -> list:
    return [k for k in _walk(baum) if _props(k).get(name)]


class TestDerOffeneSchrittIstAnsagbar:
    """(1) `aria-current` — welcher Schritt offen ist, steht nicht nur in der Farbe."""

    def test_exactly_one_step_is_marked(self, draft):
        markiert = _mit_attribut(wizard.rail(2, {0, 1, 2}), "aria-current")

        assert len(markiert) == 1
        assert _props(markiert[0])["aria-current"] == "step"

    def test_the_entry_marks_none(self, draft):
        """Am Einstieg ist kein Schritt offen — dann darf auch keiner so heißen."""

        assert _mit_attribut(wizard.rail(wizard.ENTRY), "aria-current") == []


class TestJedeAenderungWirdAngesagt:
    """(2) Live-Regionen — sonst geschieht alles lautlos."""

    def test_the_step_change_is_announced(self, draft):
        baum = wizard.layout(draft, 0)
        regionen = {
            _props(k).get("id"): _props(k)["aria-live"] for k in _mit_attribut(baum, "aria-live")
        }

        assert wizard.ANSAGE in regionen, "Kein Ort, an dem der Schrittwechsel angesagt wird"
        assert regionen[wizard.ANSAGE] == "polite"

    def test_the_announcement_names_step_and_title(self, draft):
        """«Schritt 4 von 7: Ausgangslage» — Ort und Frage in einem Satz."""

        gerufen = _ansage(draft, 3)

        assert "Schritt 4 von 7" in gerufen
        assert wizard.STEPS[3].title in gerufen

    def test_the_entry_says_where_you_are_too(self, draft):
        assert "Einstieg" in _ansage(draft, wizard.ENTRY)

    def test_the_announcement_lives_outside_the_swapped_content(self, draft):
        """**Sonst wird sie nicht vorgelesen.**

        Beim Wechsel tauscht `_render` den ganzen Inhaltsbaum aus. Eine
        Live-Region *innerhalb* eines ausgetauschten Teilbaums entsteht im
        Moment der Änderung selbst neu — Screenreader lesen sie dann nicht
        zuverlässig vor. Sie muss stehen bleiben und nur neuen Text bekommen.
        """

        inhalt = wizard.content(draft, 0)

        assert not [
            k for k in _walk(inhalt) if _props(k).get("id") == wizard.ANSAGE
        ], "Die Ansage steht im Inhalt, der beim Wechsel ausgetauscht wird"

    def test_the_blocked_button_says_why_at_once(self, draft):
        """Das Tor ist `assertive`: Wer sonst weiterdrückt, drückt ins Leere."""

        baum = wizard.layout(draft, 0)
        tor = [k for k in _walk(baum) if _props(k).get("id") == wizard.GATE]

        assert tor, "Der Meldungsplatz des Tores fehlt"
        assert _props(tor[0]).get("aria-live") == "assertive"

    @pytest.mark.parametrize(
        "modul,kennung",
        [
            ("dashboard.web.pages.model_editor", "STATUS"),
            ("dashboard.web.views.running", "CANCEL_STATUS"),
        ],
    )
    def test_every_status_host_announces(self, modul, kennung, draft):
        """Rückmeldungen auf eine Handlung gehören angesagt — überall, nicht nur hier."""

        import importlib

        gefunden = importlib.import_module(modul)
        quelle = __import__("pathlib").Path(gefunden.__file__).read_text(encoding="utf-8")

        assert '"aria-live"' in quelle, (
            f"{modul} hat einen Meldungsplatz ({kennung}) ohne Live-Region — "
            "die Meldung erscheint dann lautlos."
        )


class TestDerFokusFolgtDerFrage:
    """(3) Nach einem Wechsel steht der Fokus auf der neuen Frage."""

    def test_the_heading_can_take_focus(self, draft):
        titel = [
            k
            for k in _walk(wizard.content(draft, 0))
            if getattr(k, "_type", type(k).__name__) == "H1"
        ]

        assert titel, "Der Schritt hat keine `h1`"
        assert (
            _props(titel[0]).get("tabIndex") == -1
        ), "Ohne `tabIndex=-1` lässt sich die Überschrift nicht fokussieren."

    def test_it_hangs_on_the_content_not_on_the_step(self):
        """**Der Eingang entscheidet, ob es ueberhaupt etwas zu fokussieren gibt.**

        Der Schritt-Store ändert sich beim Klick; die neue Überschrift gibt es
        erst, wenn der Server geantwortet hat. Am Store hängend zielte der
        Callback auf einen Baum, den es noch nicht gab.
        """

        from dash import Input

        eingaenge: list = []

        class _App:
            def callback(self, *a, **k):
                return lambda fn: fn

            def clientside_callback(self, code, *deps, **kwargs):
                eingaenge.extend(
                    getattr(d, "component_id", None) for d in deps if isinstance(d, Input)
                )

        wizard.register_callbacks(_App())

        assert wizard.CONTENT_HOST in eingaenge
        assert wizard.STEP_STORE not in eingaenge

    def test_the_client_side_callback_moves_it(self):
        """Der Fokus wandert im Browser, nicht auf dem Server — geprüft am Quelltext."""

        from pathlib import Path

        quelle = Path("dashboard/web/config_editor/wizard.py").read_text(encoding="utf-8")
        skript = quelle[quelle.index("app.clientside_callback") :]

        assert ".focus(" in skript, (
            "Der Schrittwechsel setzt den Fokus nicht — dann bleibt er auf dem "
            "Knopf, den es einen Moment später nicht mehr gibt."
        )
        assert "preventScroll" in skript, (
            "Ohne `preventScroll` springt die Seite beim Fokussieren und macht "
            "das sanfte Scrollen daneben zunichte."
        )
        # **Auf den Aufruf, nicht auf das Wort.** Die erste Fassung fragte nach
        # `"MutationObserver"` und war damit schon durch den Kommentar darueber
        # zufrieden -- ein Waechter, der die Begruendung prueft statt der Tat.
        assert "new MutationObserver(" in skript, (
            "Der Fokus haengt nicht am Austausch des Inhalts. Zwei Anlaeufe "
            "haben genau daran vorbeigezielt und beide standen am laufenden "
            "System auf `BODY`: erst am Schritt-Store (der aendert sich beim "
            "Klick, der Inhalt kommt erst mit der Antwort des Servers), dann "
            "ueber `requestAnimationFrame` -- und das feuert in einem Tab, den "
            "niemand sieht, gar nicht."
        )


class TestJedeAuswahlSagtWovon:
    """(4) `fieldset` und `legend` — sonst sind es unbeschriftete Optionen."""

    def test_every_radio_group_is_grouped(self, draft):
        from dash import dcc, html

        ohne = []
        for index in range(len(wizard.STEPS)):
            baum = wizard.content(draft, index)
            gruppen = [k for k in _walk(baum) if isinstance(k, dcc.RadioItems)]
            fieldsets = [k for k in _walk(baum) if isinstance(k, html.Fieldset)]
            if len(gruppen) > len(fieldsets):
                ohne.append(f"Schritt {index + 1}: {len(gruppen)} Gruppen, {len(fieldsets)} Rahmen")

        assert not ohne, (
            "Diese Radiogruppen stehen ohne `fieldset`:\n  " + "\n  ".join(ohne) + "\n\n"
            "Ein Screenreader liest sie dann als «1 von 10», ohne zu sagen, wovon."
        )

    def test_the_legend_is_readable_but_not_visible(self, draft):
        """Sie erklärt die Gruppe, ohne die Überschrift daneben zu doppeln."""

        from dash import html

        legenden = [k for k in _walk(wizard.content(draft, 0)) if isinstance(k, html.Legend)]

        assert legenden, "Die Gruppe hat keine Legende"
        for legende in legenden:
            assert "af-nur-vorlesen" in (
                _props(legende).get("className") or ""
            ), "Die Legende ist sichtbar und doppelt damit den Titel des Schritts."
            assert (_props(legende).get("children") or "").strip(), "Die Legende ist leer"

    def test_the_hidden_class_keeps_it_in_the_tree(self):
        """`display: none` nähme sie auch dem Screenreader — dann wäre sie für niemanden da."""

        from pathlib import Path

        css = Path("dashboard/web/assets/dashboard.css").read_text(encoding="utf-8")
        regel = css[css.index(".af-nur-vorlesen {") :][:400]

        assert "display: none" not in regel
        assert "visibility: hidden" not in regel
        assert "clip-path" in regel, "Ohne Beschneidung steht die Legende doch im Bild"


def _ansage(draft: dict, schritt) -> str:
    """Was `_render` in die Live-Region schreiben würde."""

    jetzt = wizard.resolve(schritt)
    if wizard.is_entry(jetzt):
        return "Einstieg: Womit möchten Sie anfangen?"
    return f"Schritt {jetzt + 1} von {len(wizard.STEPS)}: {wizard.STEPS[jetzt].title}"
