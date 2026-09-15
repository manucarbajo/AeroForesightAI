"""Der Einstieg und die Schrittfolge des Einrichtens (P1.7-C).

Sechs Zusagen, und die meisten sind schon einmal gebrochen worden — mehrere am
laufenden System, bevor sie hier festgehalten wurden:

1. **Drei Entscheidungen genügen bis zum Start** (P1.1). Eine Schrittfolge, die
   acht Stationen erzwingt, wäre ein Rückschritt. Ab dem dritten Schritt führt
   deshalb ein Weg direkt zum Schluss.
2. **Nur der offene Schritt steht im DOM.** Sonst stünden Felder doppelt, und
   eine doppelte Dash-ID ist ein Laufzeitfehler im Browser.
3. **Die Navigationsknöpfe stehen immer im DOM.** Dash führt einen Callback gar
   nicht erst aus, wenn auch nur *ein* Eingang fehlt. Am laufenden System kostete
   das die ganze Navigation: Auf Schritt 1 gab es «Direkt zum Start» nicht, also
   tat auch «Weiter» nichts, und der Zähler blieb bei «Schritt 1 von 8».
4. **Zwei Auslöser, ein Startpfad.** Der Knopf im Bedienfeld und der am Ende der
   Schrittfolge hängen am selben Callback — eine Prüfung, ein `runner.start`.
5. **Der Einstieg steht vor dem ersten Schritt.** Ohne ihn war «alle Szenarien
   nacheinander» eine Ankreuzoption hinter der Feinabstimmung des zweiten
   Schritts — vorhanden, aber unauffindbar. Seine drei Wege sind Knöpfe wie
   «Weiter» und unterliegen derselben Regel: immer im DOM, nur ausgeblendet.
6. **Jeder Weg sagt genau eine Sache — und schreibt auch nur je eine.** «Neuen
   Lauf einrichten» heißt *ein* Lauf, «Szenario-Vergleich» heißt *alle*,
   «Weiterverwenden» fasst den Entwurf nicht an. Ohne das erste Schreiben bliebe
   ein einmal gewählter Vergleich still aktiv, und man startete acht Läufe, wo
   man einen wollte.
"""

from __future__ import annotations

import dataclasses

import pytest

#: Der Modell-Bereich wird seit P3.12 erst beim Aufsuchen gebaut — diese
#: Wächter meinen seinen **Rumpf**, nicht den leeren Rahmen. Ohne den Pfad
#: lieferte `rumpf_fuer` eine leere Liste, und die Zusagen wären lautlos
#: hohl: Der Regel-1-Test verglich dann eine leere Feldmenge mit der
#: Schrittfolge und wäre für immer grün.
from dashboard.web import routing
from dashboard.web.config_editor import controls, wizard
from dashboard.web.pages.model_editor import ROUTE as _MODELL_ROUTE
from dashboard.web.state import initial_draft_dict

_MODELL_PFAD = routing.url(_MODELL_ROUTE)


@pytest.fixture
def draft() -> dict:
    return initial_draft_dict()


def _walk(node):
    yield node
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            yield from _walk(child)
    elif children is not None:
        yield from _walk(children)


def _ids(node) -> list:
    return [item.id for item in _walk(node) if getattr(item, "id", None) not in (None, "", [])]


def _fields(node) -> set[str]:
    return {
        str(item.id.get("field"))
        for item in _walk(node)
        if isinstance(getattr(item, "id", None), dict)
        and item.id.get("type") in {controls.CFG, controls.CFG_BOOL}
    }


# --- Drei Entscheidungen genuegen ------------------------------------------


class TestDreiEntscheidungenGenuegenWeiterhin:
    def test_the_shortcut_appears_once_the_three_decisions_are_made(self, draft):
        """Ab Schritt 3 führt ein Weg direkt zum Schluss."""

        versteckt = {"display": "none"}

        for schritt in range(wizard.LAST_REQUIRED):
            knopf = _knopf(wizard.navigation(schritt), wizard.SKIP)
            assert knopf.style == versteckt, f"Abkürzung schon auf Schritt {schritt + 1}"

        knopf = _knopf(wizard.navigation(wizard.LAST_REQUIRED), wizard.SKIP)
        assert knopf.style is None, "Nach den drei Entscheidungen fehlt die Abkürzung"

    def test_the_three_decisions_come_first(self):
        """Die Reihenfolge ist eine Aussage: erst entscheiden, dann feinjustieren.

        **Seit P7.13-U13.1 steht ein optionaler Schritt zwischen ihnen** —
        «Verläufe» direkt nach der Wahl des Szenarios, von Haiko entschieden am
        2026-09-15, weil die Verläufe das gewählte Szenario zeigen. Die Aussage
        bleibt: Nach der dritten Entscheidung ist nichts mehr Pflicht, und die
        erste steht vorn.
        """

        pflicht = [step.required for step in wizard.STEPS]

        assert pflicht[0] is True
        assert sum(pflicht[: wizard.LAST_REQUIRED + 1]) == 3
        assert not any(pflicht[wizard.LAST_REQUIRED + 1 : wizard.FINAL])

    def test_the_optional_steps_say_so(self):
        """«optional» steht dran — sonst wirken sie wie Pflicht."""

        gerendert = str(wizard.rail(0))

        assert gerendert.count("optional") == sum(1 for s in wizard.STEPS if not s.required)


class TestModellUndExperimentSindZweiOrte:
    """W3.1 — der Schnitt zwischen Assistent und Modell-Editor.

    Bis hierher lagen beide in derselben Schrittfolge. Die Schritte 4 und 5
    trugen zusammen **168 Bedienelemente** und brauchten 3,0 bzw. 4,0
    Bildschirme, während die drei Entscheidungsschritte davor mit drei, fünf und
    zehn Feldern auskamen. «Schritt 5 von 8» war damit keine Ortsangabe: Der
    fünfte Schritt war das Vielfache aller anderen zusammen.

    Der wichtigste Test hier ist der zweite. Beide Bereiche liegen **gleichzeitig
    im DOM** — `app.py` blendet nur um. Stünde ein Feld in beiden, wäre das eine
    doppelte Dash-ID und damit ein Laufzeitfehler im Browser, den keine
    Testsuite ohne diesen Abgleich bemerkt.
    """

    def test_the_dense_areas_left_the_step_sequence(self, draft):
        """Die **Formularwaende** sind weg — und seit P2.0-C auch die Ausgangslage.

        W3.1 hat 168 Bedienelemente in den Modell-Editor verschoben, W3.3 die
        Faktorlage als *eine* Frage zurückgeholt. P2.0-C nimmt diese Frage
        wieder heraus, aber aus einem anderen Grund: nicht weil sie zu groß
        wäre, sondern weil sie **keine Wirkung hatte**.
        """

        schluessel = [s.key for s in wizard.STEPS]

        assert "rahmen" not in schluessel
        assert "nachfrage" not in schluessel
        assert "faktorlage" not in schluessel
        assert schluessel == [
            "szenario",
            # P7.13-U13.1: die zeitlichen Verläufe, optional, direkt nach dem
            # Szenario — keine Formularwand, sondern eine Liste mit Kurve.
            "verlaeufe",
            # P7.13-U13.5: Preisbildung, Sättigung, Bevölkerung für diesen Lauf.
            "modellannahmen",
            "umfang",
            "modus",
            "ablage",
            "technik",
            "start",
        ]

    def test_no_field_is_rendered_in_both_places(self, draft):
        """Beide Bereiche liegen gleichzeitig im DOM — ein Feld darf nur in einem stehen."""

        from dashboard.web.pages import model_editor

        im_modell = _fields(model_editor.rumpf_fuer(_MODELL_PFAD, draft))
        in_schritten = set()
        for index in range(len(wizard.STEPS)):
            in_schritten |= _fields(wizard.content(draft, index))

        doppelt = im_modell & in_schritten
        assert not doppelt, (
            f"Diese Felder stehen im Modell-Editor **und** in der Schrittfolge: "
            f"{sorted(doppelt)}\nEine doppelt vergebene Dash-ID ist ein "
            "Laufzeitfehler im Browser."
        )

    def test_the_model_area_carries_the_model(self, draft):
        """Systemgrößen, Bevölkerung, Preisbildung — das Modell, und nur das."""

        from dashboard.web.pages import model_editor

        felder = _fields(model_editor.rumpf_fuer(_MODELL_PFAD, draft))

        assert any(f.startswith("property_edits.") for f in felder), "Die Systemgrößen fehlen"
        assert any(f.startswith("population_edits.") for f in felder), "Die Bevölkerung fehlt"
        assert any(f.startswith("market_feedback_edit.") for f in felder), "Die Preisbildung fehlt"
        assert not any(f.startswith("factor_states.") for f in felder), (
            "Die Faktorlage steht wieder im Modell — sie ist seit P2.0-C gar keine "
            "Eingabe mehr, weder hier noch im Assistenten."
        )

    def test_die_faktorlage_ist_nirgends_mehr_eine_eingabe(self, draft):
        """P2.0-C kehrt W3.3 um — und das ist der Kern der Umdrehung.

        W3.3 hatte die Faktorlage in den Assistenten geholt, weil sie zum
        Experiment gehört und nicht zum Modell. Das war richtig, solange sie
        überhaupt eine Eingabe war. Gemessen ist sie es nicht: Vier der sieben
        Faktoren sind nach *einem* Tick überschrieben, und in allen vier Presets
        mit Vorgabe landeten alle sieben auf denselben Zuständen wie ohne sie
        (`test_faktoren_abgeleitet.py`).

        Ein Rahmenszenario setzt die exogenen Verläufe — die Faktorlage entsteht
        daraus im Lauf.
        """

        from dashboard.web.pages import model_editor

        ueberall = _fields(model_editor.rumpf_fuer(_MODELL_PFAD, draft))
        for index in range(len(wizard.STEPS)):
            ueberall |= _fields(wizard.content(draft, index))

        faktoren = {f for f in ueberall if f.startswith("factor_states")}
        assert not faktoren, (
            f"Die Faktorlage ist wieder ein Eingabefeld: {sorted(faktoren)}. "
            "Damit stünde die Antwort wieder vor der Rechnung."
        )

    def test_der_schalter_ist_mit_umgezogen(self, draft):
        """Er entschied über die Wirkung der Faktorauswahl und steuert heute die
        Systemgrößen — er gehört dorthin, wo der Ausgangspunkt gewählt wird."""

        in_schritten = set()
        for index in range(len(wizard.STEPS)):
            in_schritten |= _fields(wizard.content(draft, index))

        assert "apply_custom_overrides" in in_schritten, (
            "Der Schalter «Eigene Werte anwenden» ist mit dem Schritt «Ausgangslage» "
            "verschwunden, statt umzuziehen — dann wirken Änderungen am Modell "
            "stillschweigend oder stillschweigend nicht."
        )

    def test_the_model_area_survives_a_broken_config(self, draft):
        """Eine kaputte Config ist ein Befund, kein leerer Bereich."""

        from dashboard.web.pages import model_editor

        kaputt = dict(draft)
        kaputt["properties_file"] = "gibt-es-nicht.json"

        gerendert = str(model_editor.rumpf_fuer(_MODELL_PFAD, kaputt))

        assert gerendert
        assert "Traceback" not in gerendert


class TestJederWegSiehtDenNamen:
    """W4.1 — kein Lauf trägt den Vorgabenamen, ohne dass jemand ihn gesehen hat.

    Der Name lag im optionalen Schritt «Lauf & Ablage». Drei von vier Wegen
    führen daran vorbei: «Szenario-Vergleich», «Weiterverwenden» und «Direkt zum
    Start» landen unmittelbar auf «Prüfen & Starten». Alle Läufe hießen deshalb
    gleich — und genau das sagt der Text neben dem Feld voraus: «Ohne sie sind
    mehrere Läufe später kaum auseinanderzuhalten.»
    """

    def test_the_name_lives_on_the_step_every_path_reaches(self, draft):
        """Der letzte Schritt ist der einzige, den **jeder** Weg passiert."""

        felder = _fields(wizard.content(draft, wizard.FINAL))

        assert "simulation_name" in felder, (
            "Der Name steht nicht auf «Prüfen & Starten» — dann sehen ihn die "
            "Wege, die direkt dorthin springen, nie."
        )

    def test_it_is_not_rendered_twice(self, draft):
        """Und nirgends sonst — dieselbe Feld-ID zweimal ist ein Laufzeitfehler."""

        orte = [
            index
            for index in range(len(wizard.STEPS))
            if "simulation_name" in _fields(wizard.content(draft, index))
        ]

        assert orte == [wizard.FINAL], f"«simulation_name» steht in den Schritten {orte}"

    def test_the_finding_points_at_that_step(self, draft):
        """Und ein Befund am Namen führt dorthin, wo er zu beheben ist."""

        assert wizard.FELD_SCHRITT["simulation_name"] == wizard.FINAL

    def test_the_suggestion_is_an_action_not_a_fallback(self, draft):
        """**Ein Vorschlag ist eine Handlung.**

        Den Namen beim Rendern vorzubelegen wäre der Fehler aus Befund A7: Der
        Wert käme aus dem Quelltext statt aus einer Entscheidung, und
        `touched()` meldete danach Einstellungen, die niemand vorgenommen hat.
        """

        from dashboard.web import config_editor
        from dashboard.web.config_editor import controls as c

        vorher = dict(draft)
        gerendert = str(wizard.content(vorher, wizard.FINAL))
        assert vorher == draft, "Das Zeichnen hat den Entwurf verändert"

        neu, meldung, _ = config_editor._handle_action(c.action_id("suggest-name"), dict(draft), [])

        assert neu["simulation_name"] != draft["simulation_name"]
        assert "Ticks" in neu["simulation_name"], neu["simulation_name"]
        assert meldung
        assert "suggest-name" in gerendert, "Der Knopf fehlt auf dem Schritt"

    def test_the_suggestion_names_the_comparison_as_one(self, draft):
        """Ein Vergleich hat keine eine Länge — der Name behauptet auch keine."""

        from dashboard.web import config_editor

        vergleich = {**draft, "run_all_sweeps": True}
        name = config_editor._namensvorschlag(vergleich)

        assert "Szenario-Vergleich" in name
        assert "Ticks" not in name, f"Der Vergleich nennt eine Länge: {name}"


class TestWasAbweichtStehtVorDemStart:
    """W4.2 — «Was habe ich geändert?» wird beantwortet, bevor gerechnet wird.

    Der Prüfschritt zeigte einen Satz und sechs Kacheln. Bei über hundert
    Feldern über sieben Schritte und einen Modell-Bereich war «was weicht ab»
    die einzige Frage ohne Antwort — und der einzige Umkehrmechanismus war «Auf
    Standard zurücksetzen», das alles verwirft.
    """

    def test_an_untouched_draft_reports_nothing(self, draft):
        from dashboard.web.config_editor import delta

        assert delta.unterschiede(draft) == []

    def test_a_change_shows_up_with_both_values(self, draft):
        from dashboard.web.config_editor import delta

        geaendert = {**draft, "rounds": 99}
        (abweichung,) = delta.unterschiede(geaendert)

        assert abweichung.feld == "rounds"
        assert abweichung.vorher == "40"
        assert abweichung.jetzt == "99"

    def test_nested_structures_are_counted_not_listed(self, draft):
        """Dreizehn Systemgrößen ergäben Dutzende Zeilen und keinen Überblick."""

        from dashboard.web.config_editor import delta

        groessen = {
            pid: {**wert, "baseline": float(wert["baseline"]) + 1.0}
            for pid, wert in list(draft["property_edits"].items())[:2]
        }
        (abweichung,) = delta.unterschiede(
            {**draft, "property_edits": {**draft["property_edits"], **groessen}}
        )

        assert abweichung.feld == "property_edits"
        assert "2" in abweichung.jetzt, abweichung.jetzt

    def test_the_path_choice_is_not_a_deviation(self, draft):
        """«Sie haben den Vergleich gewählt» ist der Satz darüber, keine Abweichung."""

        from dashboard.web.config_editor import delta

        assert delta.unterschiede({**draft, "run_all_sweeps": True}) == []

    def test_a_single_change_can_be_taken_back(self, draft):
        """Der Gegenentwurf zu «alles zurücksetzen»."""

        from dashboard.web.config_editor import delta

        geaendert = {**draft, "rounds": 99, "mock_llm": False}
        zurueck = delta.zuruecknehmen(dict(geaendert), "rounds")

        assert zurueck["rounds"] == draft["rounds"]
        assert zurueck["mock_llm"] is False, "Die zweite Änderung darf nicht mit verschwinden"

    def test_it_stands_on_the_step_every_path_reaches(self, draft):
        from dashboard.web.config_editor import delta

        gerendert = str(wizard.content({**draft, "rounds": 99}, wizard.FINAL))

        assert delta.REVERT in gerendert, "Die Abweichungsliste fehlt auf «Prüfen & Starten»"


class TestDieHerkunftStehtVorDemStart:
    """W4.4 — was das Artefakt hinterher festhält, steht vorher auf dem Schirm.

    P0.6 hat dafür gesorgt, dass ein Lauf mitschreibt, wie er entstanden ist.
    Das half beim Vergleichen aber erst **danach**: Wer zwei Läufe
    nebeneinanderlegen will, muss vorher wissen, ob Codestand und
    Konfigurationsdateien dieselben sind — besser vor der halben Stunde
    Rechenzeit als danach.
    """

    def test_it_names_the_code_version_and_the_config(self, draft):
        from dashboard.web.config_editor import start_flow

        gerendert = str(start_flow.herkunft(draft))

        assert "Codestand" in gerendert
        assert "Konfiguration" in gerendert

    def test_it_comes_from_the_same_source_as_the_artifact(self, draft):
        """**Eine Quelle, nicht zwei.** Sonst stünde vorher etwas anderes als hinterher."""

        from dashboard.web.config_editor import start_flow
        from src.reporting.output_writer.provenance import config_fingerprint

        erwartet = config_fingerprint(start_flow._zustand(draft))
        gerendert = str(start_flow.herkunft(draft))

        assert erwartet.simulation_config in gerendert
        assert erwartet.properties in gerendert

    def test_a_broken_config_does_not_break_the_preflight(self, draft):
        """Eine unlesbare Datei meldet der Preflight — hier gibt es keinen zweiten Absturz."""

        from dashboard.web.config_editor import start_flow

        kaputt = {**draft, "properties_file": "gibt-es-nicht.json"}

        gerendert = str(start_flow.herkunft(kaputt))
        assert "Codestand" in gerendert
        assert "Traceback" not in gerendert

    def test_the_rail_stays_compact(self, draft):
        """Im Bedienfeld nicht: Dort sind drei Kacheln der ganze Platz."""

        from dashboard.web.config_editor import start_flow

        schmal = str(start_flow.preflight(draft, [], slot="rail", compact=True))

        assert "Codestand" not in schmal


class TestDieDauerWirdGemessenNichtGeraten:
    """W4.3 — und der Befund, der das Paket auf eine andere Grundlage stellt.

    Das Paket sah eine Schätzung «aus `run_metadata.json` vergangener Läufe»
    vor. **Die Daten gab es nicht:** Das Artefakt hielt einen Zeitstempel fest
    (*wann* die Metadaten geschrieben wurden), aber keine Dauer. Es war also
    nichts zu schätzen, sondern zuerst etwas zu messen.
    """

    def test_nothing_is_shown_without_measurements(self, draft, tmp_path):
        """**Keine Zahl ist besser als eine erfundene.**

        Eine Schätzung vor einem Lauf, die auf nichts beruht, ist genau das, was
        Invariante 1 verbietet — und das Handbuch nennt seine groben Angaben
        ausdrücklich «geschätzt».
        """

        from dashboard.web.config_editor import dauer

        assert dauer.schaetzung(draft, wurzel=tmp_path) is None
        assert dauer.hinweis(draft, wurzel=tmp_path) is None

    def test_a_single_run_is_not_an_estimate(self, draft, tmp_path):
        """Aus einer Einzelmessung eine Erwartung zu machen wäre eine Behauptung."""

        from dashboard.web.config_editor import dauer

        self._lauf(tmp_path, "a", sekunden=12.0, ticks=40)

        assert dauer.schaetzung(draft, wurzel=tmp_path) is None

    def test_it_reports_a_range_and_its_source(self, draft, tmp_path):
        from dashboard.web.config_editor import dauer

        self._lauf(tmp_path, "a", sekunden=12.0, ticks=40)
        self._lauf(tmp_path, "b", sekunden=20.0, ticks=40)

        satz = dauer.schaetzung(draft, wurzel=tmp_path)

        assert satz and "bis" in satz, satz
        assert "2 vergleichbaren Läufen" in satz, satz

    def test_only_comparable_runs_count(self, draft, tmp_path):
        """Ein Lauf «Mit Sprachmodell» sagt nichts über einen «Ohne».

        Sie zu mitteln ergäbe eine Zahl, die für keinen von beiden stimmt — die
        beiden Modi unterscheiden sich um Größenordnungen.
        """

        from dashboard.web.config_editor import dauer

        self._lauf(tmp_path, "a", sekunden=12.0, ticks=40)
        self._lauf(tmp_path, "b", sekunden=900.0, ticks=40, mock=False)

        assert (
            dauer.schaetzung(draft, wurzel=tmp_path) is None
        ), "Der Lauf mit Sprachmodell wurde mitgezählt"

    def test_only_the_youngest_runs_count(self, draft, tmp_path):
        """Das Fenster ist `FENSTER` Läufe breit — und es sind die jüngsten.

        «Mehr macht die Schätzung nicht besser, aber das Einlesen langsamer»,
        sagt der Docstring von `FENSTER`, «und ältere Läufe stammen eher von
        einem anderen Codestand». Ohne einen Wächter ist das eine Absicht: Wer
        die Auswahl anfasst, merkt nicht, wenn sie plötzlich alles einliest
        oder die ältesten nimmt.
        """

        from dashboard.web.config_editor import dauer

        # Ein einzelner uralter Ausreißer, der die Spanne sprengen würde.
        self._lauf(tmp_path, "0000_uralt", sekunden=9000.0, ticks=40)
        for nummer in range(dauer.FENSTER):
            self._lauf(tmp_path, f"9{nummer:03d}_jung", sekunden=12.0, ticks=40)

        satz = dauer.schaetzung(draft, wurzel=tmp_path)

        assert satz and "9000" not in satz, satz
        assert f"{dauer.FENSTER} vergleichbaren Läufen" in satz, satz

    def test_a_folder_without_metadata_does_not_use_up_the_window(self, draft, tmp_path):
        """Ein Ordner ohne Artefakt zählt nicht mit — sonst wäre das Fenster leer.

        **Der Fall ist der Normalfall und nicht der Rand:** Ein abgebrochener
        Lauf, ein Ordner aus einem Sichtprüfungslauf, ein halb geschriebenes
        Verzeichnis — von 698 Ordnern unter `outputs/` trugen am 2026-09-12
        genau 137 Metadaten. Würde die Auswahl die jüngsten `FENSTER`
        **Ordner** nehmen statt der jüngsten `FENSTER` **Läufe**, verschwände
        die Schätzung, sobald oben etwas Leeres liegt.
        """

        from dashboard.web.config_editor import dauer

        for nummer in range(dauer.FENSTER + 5):
            (tmp_path / f"z{nummer:03d}_leer").mkdir()
        self._lauf(tmp_path, "a", sekunden=12.0, ticks=40)
        self._lauf(tmp_path, "b", sekunden=20.0, ticks=40)

        satz = dauer.schaetzung(draft, wurzel=tmp_path)

        assert satz and "2 vergleichbaren Läufen" in satz, satz

    def test_the_runner_records_the_duration(self):
        """Ohne diese Zeile gäbe es nie Messwerte."""

        from src.models.state_models import SimulationState

        assert "elapsed_seconds" in SimulationState.model_fields

    def test_the_artifact_keeps_it(self):
        """Und das Artefakt hält sie fest, statt sie neu zu berechnen."""

        from pathlib import Path

        quelle = Path("src/reporting/output_writer/metadata.py").read_text(encoding="utf-8")

        assert '"elapsed_seconds": getattr(state, "elapsed_seconds", None)' in quelle, (
            "Die Dauer wird nicht aus dem Zustand gelesen — dann misst sie die "
            "falsche Spanne, wie der Config-Fingerabdruck vor P0.6."
        )

    @staticmethod
    def _lauf(wurzel, name, *, sekunden, ticks, mock=True):
        import json

        ordner = wurzel / f"run_{name}"
        ordner.mkdir()
        (ordner / "run_metadata.json").write_text(
            json.dumps(
                {
                    "elapsed_seconds": sekunden,
                    "ticks_completed": ticks,
                    "mock_llm": mock,
                    "deterministic_only": False,
                }
            ),
            encoding="utf-8",
        )


class _SchreibVersuch(Exception):
    """Eine Aktion hat versucht, in `configs/` zu schreiben."""


#: Was das **Modell** dauerhaft verändert. Diese Funktionen werden im Test
#: ersetzt, damit ein Schreibversuch auffällt, statt Dateien anzufassen.
MODELL_SCHREIBER = (
    "add_custom_property",
    "delete_custom_property",
    "save_market_feedback_to_file",
    "save_population_edits_to_file",
    "save_saturation_to_file",
)

#: `save_custom_sweep_preset` steht **nicht** darin, und das ist eine
#: Entscheidung: «Als Szenario sichern» legt unter `configs/sweeps/` ab, und
#: das ist die Ablage des Experiments, nicht das Modell. Es darf deshalb zum
#: Einrichten gehören — seit P7.4-U4.5 als der eine Dialog aus der Kopfzeile
#: (`config_editor.sichern`), nicht mehr als Knopf in einem Schritt.
EXPERIMENT_SCHREIBER = ("save_custom_sweep_preset",)


def _freie_werte():
    """Plausible Eingaben für die Aktionen, die welche brauchen.

    Ohne sie brechen «Größe anlegen» und «Segment anlegen» **vor** dem Schreiben
    mit einer Meldung ab — und der Test schlösse daraus fälschlich, sie
    schrieben nicht.
    """

    from dashboard.web.config_editor import controls as c

    return [
        {"id": {"type": c.FREE, "name": "new-prop-id"}, "value": "probe_groesse"},
        {"id": {"type": c.FREE, "name": "new-prop-label"}, "value": "Probe"},
        {"id": {"type": c.FREE, "name": "new-prop-category"}, "value": "none"},
        {"id": {"type": c.FREE, "name": "new-segment-id"}, "value": "probe_segment"},
    ]


def _aktionen(baum) -> list[dict]:
    """Alle auslösbaren Aktions-IDs eines Komponentenbaums."""

    from dashboard.web.config_editor import controls as c
    from dashboard.web.config_editor import macro, micro

    typen = {c.ACTION, c.WRITE, macro.PROP_DELETE, micro.SEGMENT_DELETE}
    return [
        item.id
        for item in _walk(baum)
        if isinstance(getattr(item, "id", None), dict) and item.id.get("type") in typen
    ]


def _schreibt(monkeypatch, trigger: dict, draft: dict) -> bool:
    """Ob diese Aktion das Modell dauerhaft verändern würde.

    **Geprüft wird die Wirkung, nicht der Name.** Eine Liste verbotener
    Aktionsnamen wäre in dem Moment falsch, in dem jemand eine neue Aktion
    hinzufügt und sie nicht einträgt — genau die Sorte Wächter, die aus dem
    falschen Grund grün ist.
    """

    from dashboard.web import config_editor

    for name in MODELL_SCHREIBER:

        def _versuch(*_a, __name=name, **_k):
            raise _SchreibVersuch(__name)

        monkeypatch.setattr(config_editor, name, _versuch)

    # **Auch die erlaubten Schreiber werden stillgelegt.** Sie sind hier nicht
    # der Gegenstand, und bis P7.4-U4.5 stand `save-preset` in Schritt 4 und
    # legte beim Durchgehen aller Aktionen wirklich eine Datei unter
    # `configs/sweeps/` an. Beim ersten Lauf ist genau das passiert — ein Test,
    # der das Repo verändert, ist ein Fehler im Test. Die Sperre bleibt, falls
    # ein Schritt je wieder sichert.
    from dashboard.web.config_editor import sichern

    for name in EXPERIMENT_SCHREIBER:
        # Seit P7.4-U4.5 ruft nur `sichern` den Schreiber; auf `config_editor` bleibt
        # die Sperre für den Fall, dass ein Schritt je wieder sichert.
        for modul in (config_editor, sichern):
            monkeypatch.setattr(modul, name, lambda *_a, **_k: "pfad", raising=False)

    try:
        config_editor._handle_action(trigger, dict(draft), _freie_werte())
    except _SchreibVersuch:
        return True
    except Exception:  # noqa: BLE001 - jeder andere Fehler ist hier kein Befund
        return False
    return False


class TestNurDasModellSchreibtInsModell:
    """W3.2 — der kritische Audit-Befund A6.

    Fünf Bedienelemente in als *optional* gekennzeichneten Schritten schrieben
    sofort und ohne Rückfrage in `configs/properties.json`: «Entfernen» an einem
    Segment löschte es aus der ausgelieferten Datei. Kein Dialog, kein Undo,
    keine Sicherung. Die Wirkung reichte über den Lauf, die Sitzung und den
    Nutzer hinaus — die nächste Person arbeitete mit einem veränderten Modell,
    ohne es zu erfahren.

    Das war kein Bedienfehler, sondern ein Kategorienfehler. W3.1 hat die
    Trennung gebaut, dieses Paket macht sie mechanisch nachprüfbar.
    """

    def test_no_step_of_the_wizard_can_change_the_model(self, monkeypatch, draft):
        """Der Kern der Zusage — und er prüft die Wirkung, nicht die Namen."""

        schuldige = []
        for index in range(len(wizard.STEPS)):
            for trigger in _aktionen(wizard.content(draft, index)):
                if _schreibt(monkeypatch, trigger, draft):
                    schuldige.append(f"  Schritt {index + 1}: {trigger}")

        assert not schuldige, (
            "Diese Aktionen im Assistenten verändern das Modell dauerhaft:\n"
            + "\n".join(schuldige)
            + "\n\nEin Assistent, der einen Lauf einrichtet, darf das Modell nicht "
            "ändern. Der Ort dafür ist der Bereich «Modell»."
        )

    def test_the_experiment_may_still_save_itself(self, monkeypatch, draft):
        """«Als Szenario sichern» bleibt — es legt kein Modell an, sondern ein Experiment.

        Die Zusage lautet «kein Schreibpfad **ins Modell**», nicht «kein
        Schreibpfad». Ein Szenario unter `configs/sweeps/` abzulegen ist die
        Ablage des Experiments. Seit P7.4-U4.5 geschieht es im Dialog aus der
        Kopfzeile; der Test ruft dessen Callback und prüft, dass er das Experiment
        schreibt und sonst nichts.
        """

        from pathlib import Path

        from dashboard.web.config_editor import sichern

        class _Mitschrift:
            def __init__(self):
                self.callbacks = {}

            def callback(self, *_a, **_k):
                def _dekorator(funktion):
                    self.callbacks[funktion.__name__] = funktion
                    return funktion

                return _dekorator

            def clientside_callback(self, *_a, **_k):
                return None

        gerufen = []
        for name in EXPERIMENT_SCHREIBER:
            monkeypatch.setattr(
                sichern, name, lambda *a, __n=name, **k: gerufen.append(__n) or Path("probe.json")
            )
        for name in MODELL_SCHREIBER:
            monkeypatch.setattr(
                sichern, name, lambda *a, __n=name, **k: gerufen.append(__n), raising=False
            )
        mitschrift = _Mitschrift()
        sichern.register_callbacks(mitschrift)

        mitschrift.callbacks["_sichern"](1, "probe", None, dict(draft))

        assert gerufen == list(EXPERIMENT_SCHREIBER)

    def test_every_writing_control_asks_first(self, monkeypatch, draft):
        """Jede schreibende Schaltfläche im Modell steht hinter einer Rückfrage.

        Auch das über die Wirkung: Erst wird ermittelt, welche Aktionen des
        Bereichs schreiben, dann wird geprüft, dass genau diese in einer
        Rückfrage stecken — als Bestätigung im Dialog von `controls.write_action`.
        Eine neue schreibende Aktion ohne
        Rückfrage fällt damit auf, ohne dass jemand eine Liste pflegt.
        """

        from dash import html

        from dashboard.web.pages import model_editor

        baum = model_editor.rumpf_fuer(_MODELL_PFAD, draft)
        mit_rueckfrage = {
            str(knopf.id)
            for dialog in _walk(baum)
            if isinstance(dialog, html.Dialog)
            for knopf in _walk(dialog)
            if isinstance(getattr(knopf, "id", None), dict)
        }

        ohne = [
            trigger
            for trigger in _aktionen(baum)
            if _schreibt(monkeypatch, trigger, draft) and str(trigger) not in mit_rueckfrage
        ]

        assert not ohne, (
            f"Diese Schaltflächen im Modell schreiben ohne Rückfrage: {ohne}\n"
            "`controls.write_action` verpackt sie samt Reichweite."
        )

    def test_the_reach_is_named_at_every_one_of_them(self, draft):
        """Und die Reichweite steht dran — im Hinweis wie in der Rückfrage.

        Eine Rückfrage, die nur «Fortfahren?» sagt, klickt man weg. Sie muss
        sagen, wie weit die Änderung reicht.
        """

        from dash import html

        from dashboard.web.config_editor import controls as c
        from dashboard.web.pages import model_editor

        dialoge = [
            item
            for item in _walk(model_editor.rumpf_fuer(_MODELL_PFAD, draft))
            if isinstance(item, html.Dialog)
        ]

        assert dialoge, "Keine einzige Rückfrage im Modell-Bereich"
        for dialog in dialoge:
            text = " ".join(k for k in _walk(dialog) if isinstance(k, str))
            assert c.REICHWEITE in text, f"Eine Rückfrage nennt die Reichweite nicht: {text[:80]!r}"

    def test_the_reach_is_worded_once(self):
        """Ein Satz, eine Quelle — sonst laufen Hinweis und Rückfrage auseinander."""

        from pathlib import Path

        for datei in ("macro.py", "micro.py"):
            quelle = Path("dashboard/web/config_editor") / datei
            text = quelle.read_text(encoding="utf-8")
            assert "für alle künftigen Läufe" not in text, (
                f"{datei} formuliert die Reichweite selbst — sie gehört in "
                "`controls.REICHWEITE` und nur dorthin."
            )


# --- Nur der offene Schritt steht im DOM -----------------------------------


class TestNurEinSchrittStehtImDom:
    def test_a_step_shows_only_its_own_fields(self, draft):
        """Zwei Schritte gleichzeitig hieße dieselbe Feld-ID zweimal."""

        for index in range(len(wizard.STEPS)):
            for anderer in range(len(wizard.STEPS)):
                if index == anderer:
                    continue
                gemeinsam = _fields(wizard.content(draft, index)) & _fields(
                    wizard.content(draft, anderer)
                )
                assert not gemeinsam, (
                    f"Schritt {index + 1} und {anderer + 1} zeigen dieselben Felder: "
                    f"{sorted(gemeinsam)}"
                )

    def test_no_step_renders_a_duplicate_id(self, draft):
        for index in range(len(wizard.STEPS)):
            ids = [str(i) for i in _ids(wizard.content(draft, index))]
            doppelt = {i for i in ids if ids.count(i) > 1}
            assert not doppelt, f"Schritt {index + 1} vergibt eine ID doppelt: {doppelt}"


# --- Die Knoepfe bleiben im DOM --------------------------------------------


def _knopf(baum, kennung):
    for item in _walk(baum):
        if getattr(item, "id", None) == kennung:
            return item
    raise AssertionError(f"Knopf «{kennung}» fehlt im DOM")


class TestJederKnopfBleibtImDom:
    """Dash führt einen Callback nicht aus, wenn ein Eingang fehlt.

    Deshalb werden die Knöpfe **ausgeblendet**, nicht weggelassen — dasselbe
    Muster wie bei den vier Viewport-Bereichen in `app.py`.
    """

    @pytest.mark.parametrize("kennung", [wizard.BACK, wizard.NEXT, wizard.SKIP, wizard.START])
    def test_it_exists_on_every_step(self, kennung):
        for schritt in range(len(wizard.STEPS)):
            _knopf(wizard.navigation(schritt), kennung)

    def test_start_shows_up_only_at_the_end(self):
        for schritt in range(wizard.FINAL):
            assert _knopf(wizard.navigation(schritt), wizard.START).style == {"display": "none"}

        assert _knopf(wizard.navigation(wizard.FINAL), wizard.START).style is None

    def test_next_steps_aside_at_the_end(self):
        assert _knopf(wizard.navigation(wizard.FINAL), wizard.NEXT).style == {"display": "none"}
        assert _knopf(wizard.navigation(0), wizard.NEXT).style is None


# --- Der Schritt bleibt in seinen Grenzen ----------------------------------


class TestDerSchrittBleibtInSeinenGrenzen:
    @pytest.mark.parametrize(
        ("eingabe", "erwartet"), [(-5, 0), (0, 0), (3, 3), (99, wizard.FINAL), (None, 0), ("x", 0)]
    )
    def test_clamp(self, eingabe, erwartet):
        assert wizard.clamp(eingabe) == erwartet


# --- Zwei Ausloeser, ein Startpfad -----------------------------------------


def test_the_start_button_shares_the_callback_with_the_rail():
    """Ein zweiter Knopf ist kein zweiter Startpfad.

    Der Einwand aus P1.6 galt einer zweiten Prüfung und einer zweiten
    `runner.start`-Stelle. Hier hängen beide Knöpfe am selben Callback — es gibt
    weiterhin genau eine Prüfung und genau einen Start.
    """

    from dashboard.web.pages import launch as launch_page

    class _App:
        def __init__(self):
            self.eingaenge: list[list] = []

        def callback(self, *outputs, **kwargs):
            ids = [
                getattr(dep, "component_id", None)
                for dep in outputs
                if hasattr(dep, "component_id")
            ]

            def decorator(fn):
                if fn.__name__ == "_start":
                    self.eingaenge.append(ids)
                return fn

            return decorator

        def clientside_callback(self, *args, **kwargs):
            """Läuft im Browser — hier nur entgegenzunehmen."""

    app = _App()
    launch_page.register_callbacks(app)

    assert len(app.eingaenge) == 1, "Es darf genau einen Start-Callback geben"


def test_a_step_change_scrolls_back_to_the_top():
    """Nach «Weiter» steht man am Anfang der neuen Frage, nicht mittendrin.

    Die Bildlaufhöhe des vorigen Schritts bleibt sonst erhalten: Am laufenden
    System gemessen setzte ein «Zurück» aus dem 2237 px hohen vierten Schritt
    einen bei Bildlaufhöhe 1200 ab — weit unterhalb der Überschrift des
    Schritts, auf dem man gelandet war.

    Geprüft wird die **Verdrahtung**, nicht das Scrollen selbst: Das läuft im
    Browser, und ohne Browser lässt sich nur festhalten, dass der Callback
    angemeldet ist und am richtigen Eingang hängt.

    **Und der richtige Eingang ist der Inhalt, nicht der Schritt-Store**
    (P1.9-W5.3). Bis dahin hing der Callback am Store — der ändert sich in dem
    Moment, in dem jemand klickt, während der neue Inhalt erst mit der Antwort
    des Servers kommt. Fürs Scrollen fiel das nicht auf; für den Fokus, der
    seit W5.3 danebensteht, schon: Am laufenden System griff er ins Leere und
    der Fokus blieb auf `BODY`. Der Wirt des Inhalts ändert sich genau dann,
    wenn es etwas zu fokussieren gibt.
    """

    class _App:
        def __init__(self):
            self.clientside: list[tuple] = []

        def callback(self, *outputs, **kwargs):
            def decorator(fn):
                return fn

            return decorator

        def clientside_callback(self, code, *deps, **kwargs):
            self.clientside.append((code, deps))

    app = _App()
    wizard.register_callbacks(app)

    assert app.clientside, "Kein clientseitiger Callback angemeldet"
    code, deps = app.clientside[0]
    assert "scrollTo" in code
    assert any(
        getattr(d, "component_id", None) == wizard.CONTENT_HOST for d in deps
    ), "Der Callback hängt nicht am Inhalt — dann läuft er, bevor es ihn gibt."
    assert not any(
        getattr(d, "component_id", None) == wizard.STEP_STORE for d in deps
    ), "Am Schritt-Store hängend feuert er zu früh (siehe Docstring)."


# --- Der Einstieg ----------------------------------------------------------


class TestDerEinstiegStehtVorDemErstenSchritt:
    """Drei Wege statt einer Bildlaufstrecke — und keiner davon versteckt.

    Bis P1.7-C landete man unmittelbar auf Schritt 1. Damit lag der
    Szenario-Vergleich als Kästchen hinter «Feinabstimmung» im zweiten Schritt;
    er war da, aber niemand fand ihn.
    """

    def test_the_setup_area_opens_on_the_entry(self, draft):
        from dashboard.web.pages import setup as setup_page

        baum = setup_page.layout(draft)

        assert _style(baum, wizard.ENTRY_HOST) == {}, "Der Einstieg ist nicht zu sehen"
        assert _style(baum, wizard.CONTENT_HOST) == {"display": "none"}
        assert _style(baum, wizard.RAIL) == {"display": "none"}

    def test_a_step_hides_the_entry_instead_of_dropping_it(self, draft):
        """Regel 6: Ein fehlender Eingang legt den ganzen Callback lahm.

        Die drei Wege hängen am selben Callback wie «Weiter» und «Zurück». Einen
        davon auf Schritt 3 wegzulassen nähme die ganze Navigation mit — genau
        das ist in P1.7 schon einmal passiert.
        """

        for schritt in [wizard.ENTRY, *range(len(wizard.STEPS))]:
            baum = wizard.layout(draft, schritt)
            for weg in (wizard.WAY_NEW, wizard.WAY_SWEEP, wizard.WAY_RESUME):
                _knopf(baum, weg)
            sichtbar = _style(baum, wizard.ENTRY_HOST) == {}
            assert sichtbar is (schritt is wizard.ENTRY), f"Einstieg falsch sichtbar bei {schritt}"

    def test_the_entry_offers_exactly_three_ways(self, draft):
        assert len(_wege(wizard.entry(draft))) == 3

    def test_exactly_one_way_carries_the_weight(self, draft):
        """Drei gleich betonte Karten stellen drei Fragen (P1.9-W5.6).

        Zu beantworten ist eine. Welche hervorgehoben wird, ist ein Fachurteil
        und steht als solches in `_hauptweg` — geprüft wird hier nur, dass es
        **genau eine** ist.
        """

        for entwurf in (draft, {}):
            betont = [w for w in _wege(wizard.entry(entwurf)) if "af-way--haupt" in w.className]
            assert len(betont) == 1, f"{len(betont)} hervorgehobene Wege statt einem"

    def test_the_weight_follows_the_only_signal_there_is(self, draft):
        """Gibt es etwas fortzusetzen, ist Fortsetzen der naheliegende Weg.

        Häufigkeit lässt sich ohne Nutzungsdaten nicht messen — **ob es einen
        Entwurf gibt**, sehr wohl. Danach richtet sich die Hervorhebung; alles
        andere wäre geraten.
        """

        assert wizard._hauptweg(weiter=True) == wizard.WAY_RESUME
        assert wizard._hauptweg(weiter=False) == wizard.WAY_NEW

    def test_no_locked_way_is_ever_the_highlighted_one(self, draft):
        """Eine betonte Karte, die nicht reagiert, ist schlimmer als eine matte."""

        for entwurf in (draft, {}):
            for weg in _wege(wizard.entry(entwurf)):
                if "af-way--haupt" in weg.className:
                    assert not getattr(
                        weg, "disabled", False
                    ), "Der hervorgehobene Weg ist gesperrt"

    def test_the_entry_renders_no_input_field(self, draft):
        """Der Einstieg ist eine Weiche, kein Formular.

        Ein Feld hier stünde zusätzlich zu dem im Schritt — und dieselbe Dash-ID
        zweimal ist ein Laufzeitfehler im Browser.
        """

        assert not _fields(wizard.entry(draft))

    def test_no_duplicate_id_with_the_entry_in_the_tree(self, draft):
        for schritt in [wizard.ENTRY, 0, wizard.FINAL]:
            ids = [str(i) for i in _ids(wizard.layout(draft, schritt))]
            doppelt = {i for i in ids if ids.count(i) > 1}
            assert not doppelt, f"Doppelte ID bei Schritt {schritt}: {doppelt}"

    def test_resume_stays_shut_until_something_was_changed(self, draft):
        """«Letzte Einstellungen» darf nicht anbieten, was es nicht gibt.

        Ausgegraut statt weggelassen — der Knopf bleibt Eingang seines
        Callbacks.
        """

        assert not wizard.touched(draft)
        assert _knopf(wizard.entry(draft), wizard.WAY_RESUME).disabled

        geaendert = {**draft, "rounds": int(draft.get("rounds") or 40) + 1}

        assert wizard.touched(geaendert)
        assert not _knopf(wizard.entry(geaendert), wizard.WAY_RESUME).disabled


def _style(baum, kennung) -> dict:
    for item in _walk(baum):
        if getattr(item, "id", None) == kennung:
            return getattr(item, "style", None) or {}
    raise AssertionError(f"«{kennung}» fehlt im DOM")


# --- Jeder Weg sagt genau eine Sache ---------------------------------------


def _navigate_callback(monkeypatch, ausgeloest: str):
    """Den Navigations-Callback holen und einen Knopfdruck vortäuschen."""

    class _Ctx:
        triggered_id = ausgeloest
        triggered = [{"prop_id": f"{ausgeloest}.n_clicks", "value": 1}]

    gefangen: dict = {}

    class _App:
        def callback(self, *outputs, **kwargs):
            def decorator(fn):
                gefangen.setdefault(fn.__name__, fn)
                return fn

            return decorator

        def clientside_callback(self, *args, **kwargs):
            """Läuft im Browser."""

    wizard.register_callbacks(_App())
    monkeypatch.setattr(wizard, "ctx", _Ctx)
    return gefangen["_navigate"]


class TestDieSchrittlisteBehauptetNichts:
    """W2.1 — ein Haken nur für Schritte, die wirklich offen waren.

    Der gemessene Ausgangspunkt: Ein Klick auf «Szenario-Vergleich starten»
    führt auf Schritt 8, und die Liste zeigte danach

        ["done","done","done","done","done","done","done","current"]

    also sieben Häkchen für sieben Schritte, die nie auf dem Schirm standen.
    Der Zustand hing allein an der Position. Ein Fortschrittsanzeiger, der
    Übersprungenes als Erledigt ausweist, ist schlechter als keiner: Er nimmt
    genau die Information weg, für die er da ist.
    """

    def _zustaende(self, current, besucht):
        baum = wizard.rail(current, set(besucht))
        return [
            item.className.replace("af-step af-step--", "")
            for item in _walk(baum)
            if isinstance(getattr(item, "id", None), dict) and item.id.get("type") == wizard.JUMP
        ]

    def test_a_jump_to_the_end_marks_nothing_as_done(self):
        """Der Befund selbst, als Zeile."""

        zustaende = self._zustaende(wizard.FINAL, {wizard.FINAL})

        assert (
            "besucht" not in zustaende
        ), f"Nach einem Sprung ans Ende gilt etwas als besucht: {zustaende}"
        assert zustaende[wizard.FINAL] == "current"
        assert set(zustaende[: wizard.FINAL]) == {"uebersprungen"}

    def test_walking_through_leaves_real_marks(self):
        """Wer die Schritte durchgeht, sieht seinen Weg."""

        zustaende = self._zustaende(3, {0, 1, 2, 3})

        assert zustaende[:3] == ["besucht"] * 3
        assert zustaende[3] == "current"
        assert set(zustaende[4:]) == {"offen"}

    def test_skipped_and_upcoming_are_told_apart(self):
        """«Noch nicht dran» und «übergangen» sehen verschieden aus.

        Beides als «offen» zu zeigen wäre nicht falsch, aber es beantwortet die
        Frage nicht, die man auf Schritt 8 hat: *Habe ich etwas übergangen?*
        """

        # Bewusst nicht der letzte Schritt: Danach muss noch etwas kommen,
        # sonst prueft der Fall nur die Haelfte. Die Zahl ist deshalb aus
        # `STEPS` abgeleitet und nicht hingeschrieben -- W3.1 hat die
        # Schrittfolge schon einmal von acht auf sechs gekuerzt.
        offen = wizard.FINAL - 1
        zustaende = self._zustaende(offen, {0, offen})

        assert zustaende[0] == "besucht"
        assert zustaende[1:offen] == ["uebersprungen"] * (offen - 1)
        assert zustaende[offen] == "current"
        assert set(zustaende[offen + 1 :]) == {"offen"}

    def test_the_open_step_counts_as_seen_without_being_recorded(self):
        """Der offene Schritt braucht keinen Eintrag im Speicher.

        Sonst müsste jeder Schreiber daran denken, und ein vergessener Fall
        hieße, dass ein gerade betrachteter Schritt als übersprungen dasteht.
        """

        assert wizard._besucht_aus([], 4) == {4}
        assert wizard._besucht_aus([1, 2], 4) == {1, 2, 4}
        assert wizard._besucht_aus(None, None) == set()

    def test_the_rail_says_how_many_were_skipped(self):
        """Und die Zahl steht darunter, wenn es etwas zu sagen gibt."""

        text = str(wizard.rail(wizard.FINAL, {wizard.FINAL}))
        assert f"{wizard.FINAL} übersprungen" in text

        sauber = str(wizard.rail(0, {0}))
        assert "übersprungen" not in sauber, (
            "Ohne übersprungene Schritte gehört die Zeile weg — sonst liest sie "
            "nach dem zweiten Mal niemand mehr."
        )

    def test_the_current_step_is_marked_for_screen_readers(self):
        """`aria-current="step"` — bisher steckte der Zustand nur in der Farbe.

        Ein Vorgriff auf W5.3, aber er gehört hierher: Diese Funktion vergibt
        gerade die Zustände, und ihn später nachzurüsten hieße, dieselbe Stelle
        ein zweites Mal aufzuschlagen.
        """

        aria = [
            item.to_plotly_json()["props"].get("aria-current")
            for item in _walk(wizard.rail(2, {0, 1, 2}))
            if isinstance(getattr(item, "id", None), dict) and item.id.get("type") == wizard.JUMP
        ]

        assert aria.count("step") == 1, f"Genau ein Schritt ist der offene: {aria}"
        assert aria[2] == "step", f"Markiert ist der falsche Schritt: {aria}"


class TestDasTorHaeltWasEsZusagt:
    """W2.2 — «Weiter» garantiert wieder etwas.

    Bis hierher prüfte die Navigation nichts: «Weiter» war nie gesperrt, «Lauf
    starten» nur während eines laufenden Laufs, und die Fehler wurden zwar
    angezeigt, hielten aber nichts auf. Man konnte durch acht Schritte laufen und
    erst beim Start erfahren, dass Schritt 2 ungültig war.

    Ein Wizard unterscheidet sich von einer Reiterleiste dadurch, dass «Weiter»
    etwas garantiert. Ohne Tor war diese Schrittfolge eine Reiterleiste mit
    zusätzlichen Klicks — und die Reiterleiste hatte P1.7 gerade abgeschafft.
    """

    def _kaputt(self, draft):
        entwurf = dict(draft)
        entwurf["rounds"] = 0  # `max_ticks muss mindestens 1 sein`, Feld `rounds`
        return entwurf

    def test_a_clean_draft_blocks_nothing(self, draft):
        weiter, start, meldung = wizard.gate(draft, 1)

        assert (weiter, start) == (False, False)
        assert meldung is None, "Ohne Befund gehört keine Meldung in die Leiste"

    def test_it_blocks_next_where_the_finding_can_be_fixed(self, draft):
        weiter, start, meldung = wizard.gate(self._kaputt(draft), wizard.FELD_SCHRITT["rounds"])

        assert weiter is True
        assert start is True
        assert meldung is not None

    def test_it_does_not_block_next_elsewhere(self, draft):
        """Sonst wäre es eine Sackgasse, keine Führung.

        Auf Schritt 1 kann man die Lauflänge nicht einstellen. «Weiter» dort zu
        sperren hieße, jemanden für einen Fehler festzuhalten, den er an dieser
        Stelle gar nicht beheben kann.
        """

        weiter, start, meldung = wizard.gate(self._kaputt(draft), 0)

        assert weiter is False, "«Weiter» sperrt in einem Schritt ohne den Befund"
        assert start is True, "«Lauf starten» muss trotzdem sperren"
        wohin = f"Schritt {wizard.FELD_SCHRITT['rounds'] + 1}"
        assert wohin in str(meldung), "Die Meldung sagt nicht, wohin"

    def test_start_is_blocked_by_any_finding(self, draft):
        """Von «Prüfen & Starten» geht es nicht weiter, sondern los."""

        for schritt in range(len(wizard.STEPS)):
            _, start, _ = wizard.gate(self._kaputt(draft), schritt)
            assert start is True, f"Start ist auf Schritt {schritt + 1} offen"

    def test_the_entry_is_not_a_step(self, draft):
        """Am Einstieg gibt es weder «Weiter» noch «Starten» — also nichts zu sperren."""

        assert wizard.gate(self._kaputt(draft), wizard.ENTRY) == (False, False, None)

    def test_a_finding_without_a_field_lands_at_the_end(self):
        """Etwa eine unlesbare Konfigurationsdatei — sie hat keinen anderen Ort."""

        verteilt = wizard.blocker_je_schritt(["Konfiguration konnte nicht geladen werden: kaputt"])

        assert list(verteilt) == [wizard.SCHRITT_OHNE_FELD]

    def test_the_field_to_step_table_matches_what_the_steps_render(self, draft):
        """**Die Tabelle wird nicht geglaubt, sondern geprüft.**

        `FELD_SCHRITT` sagt, in welchem Schritt ein beanstandetes Feld
        eingestellt wird. Eine handgepflegte Zuordnung ist genau die Sorte
        Tabelle, die P1.1 im Dashboard abgelehnt hat — sie bricht still, sobald
        jemand ein Feld in einen anderen Schritt verschiebt.

        Hier wird sie gegen die Wirklichkeit gehalten: Jeder Schritt wird
        gerendert, seine Felder ausgelesen, und die Zeile muss stimmen.
        """

        tatsaechlich = {
            index: _fields(wizard.content(draft, index)) for index in range(len(wizard.STEPS))
        }

        falsch = []
        for feld, schritt in sorted(wizard.FELD_SCHRITT.items()):
            wo = [i for i, felder in tatsaechlich.items() if feld in felder]
            if wo != [schritt]:
                falsch.append(
                    f"  `{feld}`: Tabelle sagt Schritt {schritt + 1}, gerendert in "
                    f"{[i + 1 for i in wo] or 'keinem Schritt'}"
                )

        assert not falsch, (
            "`FELD_SCHRITT` stimmt nicht mehr mit den Schritten überein:\n"
            + "\n".join(falsch)
            + "\n\nSolange sie falsch ist, sperrt «Weiter» im falschen Schritt — "
            "oder gar nicht."
        )

    def test_every_field_validation_can_flag_is_in_the_table(self):
        """Und umgekehrt: kein Befund, der keinen Schritt findet.

        Ein Feld, das die Prüfung beanstanden kann und das die Tabelle nicht
        kennt, landet stillschweigend auf «Prüfen & Starten». Das ist der
        richtige Notnagel für Befunde **ohne** Feld — für eines **mit** Feld ist
        es eine verpasste Führung.
        """

        import re
        from pathlib import Path

        quelle = Path("src/validation.py").read_text(encoding="utf-8")
        vergeben = set(re.findall(r'issue\(\s*(?:f?"[^"]*"\s*)+,\s*"([a-z_.]+)"', quelle))
        vergeben |= set(re.findall(r'^\s*"([a-z_.]+)",\s*$', quelle, re.M))

        # `tick_unit` und Konsorten sind Konstanten im Modul, keine Feldnamen —
        # gezählt wird nur, was auch ein Draft-Feld ist.
        from dashboard.config_catalog import ConfigDraft

        felder = {f.name for f in dataclasses.fields(ConfigDraft)}
        beanstandbar = {name for name in vergeben if name in felder}

        fehlend = sorted(beanstandbar - set(wizard.FELD_SCHRITT))
        assert not fehlend, (
            f"Diese Felder kann die Prüfung beanstanden, aber `FELD_SCHRITT` kennt "
            f"sie nicht: {fehlend}. Ihr Befund landet dann auf «Prüfen & Starten», "
            "statt in dem Schritt, in dem man ihn beheben kann."
        )


class TestZurueckFuehrtDorthinWoManWar:
    """W2.3 — «Zurück» folgt einem Verlauf statt einer Subtraktion.

    `aktuell - 1` stimmt für den geraden Weg durch die Schritte und für keinen
    anderen. Wer über «Szenario-Vergleich starten» auf Schritt 8 kam, landete
    mit einem Klick in Schritt 7 «Technik» — in Feineinstellungen zum
    Sprachmodell, die er nie sehen wollte und die auf seinem Pfad ohnehin nicht
    gelten. Wer über die Liste von Schritt 1 auf 7 sprang, landete auf 6.
    """

    def _navigate(self, monkeypatch, ausgeloest):
        return _navigate_callback(monkeypatch, ausgeloest)

    def test_the_comparison_leads_back_to_the_entry(self, monkeypatch, draft):
        """Der Befund selbst: Schritt 8, betreten über den Einstieg."""

        navigate = self._navigate(monkeypatch, wizard.BACK)

        schritt, _e, _b, verlauf = navigate(
            *[None] * 6, None, None, wizard.FINAL, draft, [], [wizard.ENTRY]
        )

        assert schritt is wizard.ENTRY, "«Zurück» führt in einen Schritt, in dem man nie war"
        assert verlauf == []

    def test_a_jump_is_undone_by_back(self, monkeypatch, draft):
        """Von 1 auf 7 gesprungen, «Zurück» führt auf 1 — nicht auf 6."""

        navigate = self._navigate(monkeypatch, wizard.BACK)

        schritt, _e, _b, verlauf = navigate(
            *[None] * 6, None, None, 6, draft, [], [wizard.ENTRY, 0]
        )

        assert schritt == 0
        assert verlauf == [wizard.ENTRY]

    def test_the_straight_path_is_unchanged(self, monkeypatch, draft):
        """Wer der Reihe nach geht, merkt von alldem nichts.

        Der Verlauf darf den Normalfall nicht verbiegen: 1 → 2 → 3 und zurück
        muss weiterhin 2 ergeben.
        """

        weiter = self._navigate(monkeypatch, wizard.NEXT)
        schritt, _e, _b, verlauf = weiter(*[None] * 6, None, None, 1, draft, [], [wizard.ENTRY, 0])
        assert (schritt, verlauf) == (2, [wizard.ENTRY, 0, 1])

        zurueck = self._navigate(monkeypatch, wizard.BACK)
        schritt, _e, _b, verlauf = zurueck(*[None] * 6, None, None, 2, draft, [], verlauf)
        assert schritt == 1
        assert verlauf == [wizard.ENTRY, 0]

    def test_an_empty_history_lands_at_the_entry(self, monkeypatch, draft):
        """Wer keinen Weg hinter sich hat, steht am Anfang.

        Keine Notlösung, sondern die richtige Antwort — und vor allem keine
        Sackgasse: Ohne sie käme man aus einem Schritt ohne Verlauf gar nicht
        mehr heraus.
        """

        navigate = self._navigate(monkeypatch, wizard.BACK)

        schritt, _e, _b, verlauf = navigate(*[None] * 6, None, None, 4, draft, [], [])

        assert schritt is wizard.ENTRY
        assert verlauf == []

    def test_the_ways_start_a_fresh_history(self, monkeypatch, draft):
        """Sonst führte «Zurück» in einen Weg, den es nicht mehr gibt."""

        for weg in (wizard.WAY_NEW, wizard.WAY_SWEEP, wizard.WAY_RESUME):
            navigate = self._navigate(monkeypatch, weg)
            _s, _e, besucht, verlauf = navigate(
                *[None] * 6, None, None, 5, draft, [1, 2, 3], [wizard.ENTRY, 1, 2]
            )
            assert verlauf == [wizard.ENTRY], f"{weg} erbt einen alten Verlauf"
            assert besucht == [], f"{weg} erbt alte Häkchen"


class TestJederWegSagtGenauEineSache:
    def test_a_new_run_is_one_run(self, monkeypatch, draft):
        navigate = _navigate_callback(monkeypatch, wizard.WAY_NEW)

        schritt, entwurf, _besucht, _verlauf = navigate(
            *[None] * 6, None, None, wizard.ENTRY, {**draft, "run_all_sweeps": True}, [], []
        )

        assert schritt == 0
        assert entwurf["run_all_sweeps"] is False

    def test_the_comparison_says_all_of_them(self, monkeypatch, draft):
        navigate = _navigate_callback(monkeypatch, wizard.WAY_SWEEP)

        schritt, entwurf, _besucht, _verlauf = navigate(
            *[None] * 6, None, None, wizard.ENTRY, draft, [], []
        )

        assert schritt == wizard.FINAL, "Der Vergleich führt direkt zu «Prüfen & Starten»"
        assert entwurf["run_all_sweeps"] is True

    def test_carrying_on_touches_nothing(self, monkeypatch, draft):
        """«Weiterverwenden» heißt: nicht anfassen.

        Ein Schreiben hier wäre der Fehler, den P1.1 bei der Lauflänge gemacht
        hat — dieselbe Zahl an zwei Stellen.
        """

        from dash import no_update

        navigate = _navigate_callback(monkeypatch, wizard.WAY_RESUME)

        schritt, entwurf, _besucht, _verlauf = navigate(
            *[None] * 6, None, None, wizard.ENTRY, draft, [], []
        )

        assert schritt == wizard.FINAL
        assert entwurf is no_update

    def test_back_from_the_first_step_reaches_the_entry_again(self, monkeypatch, draft):
        """Sonst wäre die Schrittfolge eine Sackgasse.

        Vor der Korrektur war «Zurück» auf Schritt 1 abgeschaltet und
        unsichtbar; man kam nur über einen Neuladen zurück zum Einstieg.
        """

        navigate = _navigate_callback(monkeypatch, wizard.BACK)

        schritt, _entwurf, _besucht, _verlauf = navigate(
            *[None] * 6, None, None, 0, draft, [], [wizard.ENTRY]
        )

        assert schritt is wizard.ENTRY
        assert not getattr(_knopf(wizard.navigation(0), wizard.BACK), "disabled", False)


def _wege(baum) -> list:
    """Die drei Karten des Einstiegs — an der Klasse, nicht am exakten Wortlaut.

    Die erste Fassung verglich `className` auf Gleichheit mit `"af-way"`. Mit
    dem Gewicht aus W5.6 heißt sie `"af-way af-way--haupt"`, und der Test fand
    **null** Wege statt dreier.
    """

    return [
        node for node in _walk(baum) if "af-way" in (getattr(node, "className", None) or "").split()
    ]


class TestEinUnveraenderterEntwurfWirdNichtGeschrieben:
    """P3.9 (2026-09-05) — der Kern der gekürzten Kette, ohne Browser geprüft.

    `_sync` feuert nicht nur beim Tippen: Sobald ein Schritt gezeichnet wird,
    melden seine Eingabefelder ihren **unveränderten** Wert. Bis P3.9 schrieb
    `_sync` daraufhin einen neuen Entwurf in den Store, und ein neues Dict ist
    für Dash eine Änderung — ein Klick, der keine Einstellung anfasst, zog
    Preflight, Feldfehler, Tor, Zusammenfassungen und Laufübersicht nach.

    **Der Browser-Wächter (Teil 9 von `test_web_overflow.py`) misst die Wirkung**
    — 8–11 auf 6–7 Aufrufe je Klick. Hier steht die Regel selbst, damit sie auch
    ohne Playwright rot wird: Der Browser-Test ist opt-in, die CI läuft ohne ihn.
    """

    @staticmethod
    def _sync_nachbau(vorher: dict, nachher: dict):
        """Was `_sync` am Ende tut — dieselbe Entscheidung, ohne Dash-Kontext.

        Nachgebaut und nicht gerufen: `_sync` liest `ctx.inputs_list`, und das
        gibt es nur in einem laufenden Callback. Der **Vergleich** ist die
        Zusage, nicht der Weg dorthin — und er steht hier so, wie er dort steht.
        """

        from dash import no_update

        return no_update if vorher is not None and nachher == vorher else nachher

    def test_gleicher_entwurf_schreibt_nicht(self):
        from dash import no_update

        entwurf = {"rounds": 20, "seed": 42, "mock_llm": True}

        assert self._sync_nachbau(entwurf, dict(entwurf)) is no_update

    def test_ein_geaenderter_wert_schreibt(self):
        """Sonst käme keine Eingabe mehr an — die Zusage muss in beide Richtungen halten."""

        from dash import no_update

        vorher = {"rounds": 20, "seed": 42}
        nachher = {"rounds": 21, "seed": 42}

        assert self._sync_nachbau(vorher, nachher) is not no_update
        assert self._sync_nachbau(vorher, nachher) == nachher

    def test_der_erste_entwurf_schreibt(self):
        """Ohne gespeicherten Stand gibt es nichts zu vergleichen."""

        from dash import no_update

        assert self._sync_nachbau(None, {"rounds": 20}) is not no_update

    def test_die_regel_steht_wirklich_im_callback(self):
        """Der Nachbau oben wäre wertlos, wenn `_sync` etwas anderes täte.

        Geprüft wird der Syntaxbaum des echten Callbacks: Er muss einen Vergleich
        gegen den gespeicherten Entwurf enthalten und daraufhin `no_update`
        zurückgeben. Ein Test, der nur seinen eigenen Nachbau prüft, bewacht sich
        selbst.
        """

        import ast
        from pathlib import Path

        import dashboard.web.config_editor as editor

        quelle = Path(editor.__file__).read_text(encoding="utf-8")
        sync = next(
            k
            for k in ast.walk(ast.parse(quelle))
            if isinstance(k, ast.FunctionDef) and k.name == "_sync"
        )
        rueckgaben = [k for k in ast.walk(sync) if isinstance(k, ast.Return)]
        namen = {k.id for r in rueckgaben for k in ast.walk(r) if isinstance(k, ast.Name)}
        vergleiche = [k for k in ast.walk(sync) if isinstance(k, ast.Compare)]

        assert "no_update" in namen, (
            "`_sync` gibt nirgends `no_update` zurück — dann schreibt jedes "
            "Zeichnen wieder in den Store, und die Kette ist zurück."
        )
        assert any(
            isinstance(op, ast.Eq) for v in vergleiche for op in v.ops
        ), "`_sync` vergleicht nichts auf Gleichheit"
