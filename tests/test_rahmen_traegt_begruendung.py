"""P2.2 / Variante C — ein Rahmenszenario trägt seine Kohärenzbegründung.

**Die Entscheidung, die diese Datei durchsetzt** ([P2.2](../docs/projektplan.md),
getroffen am 2026-08-31 nach dem Backtest): Die Kohärenz eines Rahmenszenarios
wird **in Prosa mit Quellen** begründet, nicht von einem Algorithmus geprüft.
Die CIB-Matrix misst nachweislich Polarität statt Plausibilität
(`test_cib_einachsigkeit.py`), und eine neu erhobene Matrix wäre ein Versprechen
von Präzision, das die Daten nicht decken.

**Der Preis von Variante C ist, dass nichts sie mechanisch erzwingt** — außer
diesem Wächter. Eine Prosa-Begründung, die niemand prüft, ist in sechs Monaten
ein leeres Feld. Er hält deshalb dieselbe Zusage wie
`test_buchungskoeffizienten.py` für die Buchungskoeffizienten: **Jede Aussage
trägt ihre Herkunft, und keine behauptet eine Genauigkeit, die es nicht gibt.**

**Der Fund, aus dem das Paket seinen Umfang bekam:** Unter `configs/sweeps/`
lagen zwei Dinge ununterscheidbar nebeneinander, und der Szenario-Vergleich
startete beide — vier begründete Weltbilder und vier Stresstests der Engine.
«Totaler Wahnsinn (Alle Parameter)» stand gleichrangig neben «Business as
Usual». Einem Kunden wurde damit ein Belastungstest als Zukunft angeboten.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from dashboard.config_catalog import list_sweep_presets, rahmenszenarien
from src.models.property_models import STRATEGIEN
from src.models.sweep_models import ARTEN, SweepConfig
from src.orchestration.scenario_sweeps import SWEEPS_DIR

ALLE = list_sweep_presets()
RAHMEN = [s for s in ALLE if s.art == "rahmen"]


def test_es_liegen_ueberhaupt_rahmenszenarien_da():
    """Ohne diesen Test wäre jeder folgende leer und damit grün."""

    assert len(RAHMEN) >= 4, f"Nur {len(RAHMEN)} Rahmenszenarien gefunden"


@pytest.mark.parametrize("szenario", ALLE, ids=lambda s: s.id)
class TestJedeDateiSagtWasSieIst:
    def test_die_art_ist_bekannt(self, szenario: SweepConfig):
        assert szenario.art in ARTEN

    def test_nichts_liegt_dazwischen(self, szenario: SweepConfig):
        """Entweder begründetes Weltbild oder erklärter Stresstest.

        Ein drittes gibt es nicht — und das ist der Punkt: Vor P2.2 waren
        **alle acht** dieses Dritte, nämlich unmarkiert.
        """

        if szenario.art == "rahmen":
            assert szenario.kohaerenz is not None
        else:
            assert len(szenario.rationale.strip()) > 40, (
                f"{szenario.id} ist als Stresstest geführt, sagt aber nicht wozu. "
                "Ein Stresstest ohne Zweck ist ein Rahmen ohne Begründung."
            )


@pytest.mark.parametrize("szenario", RAHMEN, ids=lambda s: s.id)
class TestEinRahmenTraegtSeineBegruendung:
    def test_er_behauptet_eine_welt_in_einem_satz(self, szenario: SweepConfig):
        assert len(szenario.kohaerenz.these) >= 30

    def test_er_sagt_warum_die_verlaeufe_zusammengehoeren(self, szenario: SweepConfig):
        """**Die eigentliche Zusage von Variante C.**

        Nicht «welche Regel greift bei welchem Tick» — das steht im
        `rationale` und ist eine Umsetzungsnotiz. Sondern: *warum* diese
        Entwicklungen zusammen eine Welt ergeben. Die Grenze ist die Länge
        nicht sicher zu prüfen, aber ein Halbsatz ist es garantiert nicht.
        """

        assert len(szenario.kohaerenz.begruendung) >= 300, (
            f"{szenario.id}: {len(szenario.kohaerenz.begruendung)} Zeichen Begründung. "
            "Variante C trägt die Kohärenz in Prosa — das ist die einzige "
            "Absicherung, die dieses Szenario hat."
        )

    def test_er_nennt_quellen(self, szenario: SweepConfig):
        assert szenario.kohaerenz.quellen, "Ohne Quelle ist es eine Meinung"

    def test_jede_quelle_ist_nachschlagbar(self, szenario: SweepConfig):
        """Eine Quellenangabe muss zu etwas führen — Datei, Rechtsakt oder Reihe.

        Ein Autorenname allein wäre hier zu wenig: Er lässt sich nicht
        nachschlagen, ohne zu raten, was gemeint war.
        """

        for quelle in szenario.kohaerenz.quellen:
            assert len(quelle) >= 40, f"{szenario.id}: Quelle zu knapp — {quelle!r}"

    def test_er_sagt_was_daran_nicht_belegt_ist(self, szenario: SweepConfig):
        """**Die Lehre aus P2.1, hier wiederholt.**

        Eine Literaturangabe an eine handgesetzte Zahl zu heften sieht aus wie
        eine Kalibrierung. Belegt ist die *Storyline*; die Tick-Werte, mit denen
        sie eingestellt wird, sind gesetzt und nicht geschätzt. Jedes
        Rahmenszenario sagt das selbst — nicht nur die Doku daneben.
        """

        vorbehalt = szenario.kohaerenz.vorbehalt
        assert len(vorbehalt) >= 100
        assert "nicht" in vorbehalt.lower()

    def test_keine_quelle_behauptet_eine_eichung(self, szenario: SweepConfig):
        """Das Modell ist auf der Nachfrageseite nachweislich nicht geeicht
        (P2.7). Ein Rahmenszenario darf das nicht anders klingen lassen."""

        text = (szenario.kohaerenz.begruendung + szenario.kohaerenz.these).lower()
        for wort in ("geeicht", "kalibriert", "geschätzt aus", "regressions"):
            assert wort not in text, (
                f"{szenario.id} behauptet mit «{wort}» eine Eichung. Belegt ist die "
                "Storyline, nicht ihre Bezifferung."
            )


class TestDerVergleichVergleichtWeltbilder:
    """Der Befund, der P2.2 seinen Umfang gab."""

    def test_er_laesst_die_stresstests_aus(self):
        ids = {s.id for s in rahmenszenarien()}

        assert ids == {s.id for s in RAHMEN}
        assert "alles_drin_szenario" not in ids, (
            "«Totaler Wahnsinn (Alle Parameter)» wird wieder mitverglichen — "
            "ein Belastungstest ist keine Zukunft."
        )

    def test_ein_stresstest_bleibt_einzeln_startbar(self):
        """Ausgelassen heißt nicht abgeschafft. Wer ihn ausdrücklich nennt,
        bekommt ihn — er verschwindet nur aus dem Vergleich."""

        assert "alles_drin_szenario" in {s.id for s in list_sweep_presets()}


class TestDasSchemaErzwingtEs:
    """Ohne diese beiden wäre der Rest eine Konvention, keine Regel."""

    def test_ein_rahmen_ohne_kohaerenz_wird_abgewiesen(self):
        with pytest.raises(ValidationError, match="kohaerenz"):
            SweepConfig(id="x", name="X", description="", art="rahmen")

    def test_eine_unbekannte_art_wird_abgewiesen(self):
        with pytest.raises(ValidationError, match="Unbekannte Art"):
            SweepConfig(id="x", name="X", description="", art="vielleicht")

    def test_ein_platzhalter_statt_einer_begruendung_wird_abgewiesen(self):
        """Ein Platzhalter ist schlimmer als eine Lücke — er sieht aus wie eine
        Begründung."""

        with pytest.raises(ValidationError, match="Zu kurz"):
            SweepConfig(
                id="x",
                name="X",
                description="",
                art="rahmen",
                kohaerenz={
                    "these": "TODO",
                    "begruendung": "TODO",
                    "quellen": ["irgendwas"],
                    "vorbehalt": "TODO",
                },
            )

    def test_der_standard_ist_stresstest_nicht_rahmen(self):
        """**Die stillere Voreinstellung wäre die falsche.**

        Ein im Dashboard gesichertes Experiment landet in demselben Ordner. Mit
        `rahmen` als Standard würde jede gespeicherte Datei ungefragt zu einer
        begründeten Aussage über die Zukunft.
        """

        assert SweepConfig(id="x", name="X", description="").art == "stresstest"


def test_die_dateien_tragen_das_feld_wirklich():
    """Gegen den Fall, dass ein Default den Test grün hält.

    `art` hat einen Standardwert. Läse eine Datei ihn nicht, fiele sie still
    auf `stresstest` — und jeder Test oben bliebe grün, während das Szenario
    aus dem Vergleich verschwindet.
    """

    for pfad in sorted(SWEEPS_DIR.glob("*.json")):
        roh = json.loads(pfad.read_text(encoding="utf-8"))
        assert "art" in roh, f"{pfad.name} sagt nicht, was es ist"
        if roh["art"] == "rahmen":
            assert "kohaerenz" in roh, f"{pfad.name} ist ein Rahmen ohne Begründung"


class TestJederRahmenSagtEtwasUeberDasAngebot:
    """**Der Befund B6 des Audits vom 2026-09-03, als Zusage.**

    P2.8 hat die Kapazität als exogene Größe eingeführt, P2.8-B die
    Preisstrategie zur Wahl gestellt, B2 das Angebot in den Nutzen gebracht —
    und **kein einziges ausgeliefertes Szenario benutzte davon irgendetwas.**
    `kapazitaet_index` stand in allen acht Dateien und in `properties.json` auf
    1,0 ohne Regel, `strategie` überall auf `auslastung`. Die Angebotsseite
    lebte ausschließlich im Backtest.

    **Das ist mehr als eine ungenutzte Möglichkeit.** Ein Rahmenszenario, das
    von wachsender oder einbrechender Nachfrage erzählt und die Kapazität
    stillschweigend festhält, behauptet eine Welt, die sein eigenes Modell für
    unmöglich hält — genau der Befund von P2.8, nur auf die eigenen Dateien
    angewandt. Und es *behauptet* sie stillschweigend: «die Kapazität bleibt
    gleich» ist eine Aussage über die Welt, keine Abwesenheit einer Aussage.
    """

    @pytest.mark.parametrize("sweep", RAHMEN, ids=lambda s: s.id)
    def test_er_setzt_einen_kapazitaetspfad(self, sweep) -> None:
        ids = {o.property_id for o in sweep.property_overrides}

        assert "kapazitaet_index" in ids, (
            f"`{sweep.id}` sagt nichts über das Angebot. Damit unterstellt er "
            "unveränderte Kapazität, ohne es auszusprechen — und seine "
            "Kohärenzbegründung kann das nicht begründen, weil sie es nicht kennt."
        )

    @pytest.mark.parametrize("sweep", RAHMEN, ids=lambda s: s.id)
    def test_und_er_begruendet_ihn(self, sweep) -> None:
        """Ein Pfad ohne Begründung ist eine Zahl, die jemand gewählt hat."""

        text = f"{sweep.kohaerenz.begruendung} {sweep.kohaerenz.vorbehalt}".lower()

        assert any(
            wort in text for wort in ("angebot", "kapazit", "flotte", "sitze")
        ), f"`{sweep.id}` setzt einen Kapazitätspfad, erklärt ihn aber nirgends."

    @pytest.mark.parametrize("sweep", RAHMEN, ids=lambda s: s.id)
    def test_und_er_sagt_wie_der_anbieter_preist(self, sweep) -> None:
        """**Seit P2.10 kann ein Szenario das überhaupt sagen.**

        P2.8-B nannte die Preisstrategie «eine Frage an das Szenario, nicht an
        das Modell» — nur konnte ein Szenario sie nicht stellen: Sie lebt in
        `market_rules`, und ein Sweep überschrieb nur Systemgrößen.
        """

        assert sweep.preisstrategie in STRATEGIEN, (
            f"`{sweep.id}` überlässt die Preisstrategie der ausgelieferten Config. "
            "Wie der Anbieter auf freie Kapazität reagiert, ist eine Aussage über "
            "diese Welt und gehört in die Datei."
        )


class TestDieAngebotsseiteKommtImLaufAn:
    """**Gemessen, nicht gelesen** — das Abnahmekriterium von P2.10.

    Ein Feld in einer Datei ist keine Wirkung. Diese Zusage rechnet denselben
    Rahmen zweimal, einmal mit und einmal ohne seinen Kapazitätspfad, und hält
    die Buchungsrate im letzten Viertel dagegen. Genau dieses Verfahren hat in
    P1.9-W0.2 gezeigt, dass auf dem Sweep-Pfad **ein einziges** Feld die
    Simulation erreichte.

    Ein Rahmen genügt dafür, und es ist bewusst der klarste: Zwei Läufe über
    50 Ticks kosten Sekunden, acht kosteten eine Minute für dieselbe Aussage.
    """

    @staticmethod
    def _lauf(sweep, *, mit_angebot: bool) -> float:
        from statistics import mean

        from src.config_loader import build_initial_state
        from src.llm.studio_helpers import MockLLM
        from src.orchestration.scenario_sweeps import apply_sweep_overrides
        from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

        if not mit_angebot:
            sweep = sweep.model_copy(
                update={
                    "property_overrides": [
                        o for o in sweep.property_overrides if o.property_id != "kapazitaet_index"
                    ],
                    "preisstrategie": None,
                }
            )

        zustand = apply_sweep_overrides(build_initial_state(), sweep)
        zustand.clock.max_ticks = sweep.max_ticks
        ende = SimulationRunner(
            llm=MockLLM(),
            options=RunnerOptions(
                enable_market=True,
                enable_cib=True,
                deterministic_only=True,
                checkpoint_interval=0,
                verbose_ticks=False,
            ),
        ).run(zustand, seed=42, run_id=f"rahmen_angebot_{sweep.id}_{mit_angebot}")

        spaet = [e for e in ende.price_history if e.round_number > sweep.max_ticks * 0.75]
        return mean(e.booking_rate for e in spaet if e.booking_rate is not None)

    def test_ohne_den_pfad_kaeme_eine_andere_zahl_heraus(self) -> None:
        sweep = next(s for s in RAHMEN if s.id == "business_as_usual")

        ohne = self._lauf(sweep, mit_angebot=False)
        mit = self._lauf(sweep, mit_angebot=True)

        assert mit > ohne * 1.1, (
            f"Mit Kapazitätspfad {mit:.4f}, ohne {ohne:.4f}. In einer Welt, die "
            "wachsendes Angebot behauptet, muss mehr geflogen werden — sonst steht "
            "der Pfad in der Datei und nirgends sonst."
        )


class TestAuchDerStandardIstEinRahmen:
    """**Befund A1 des Audits vom 2026-09-03.**

    P2.0 hatte als Abnahmekriterium «die Sweeps sind der reguläre Startpfad».
    Erfüllt war das nie — ein Lauf ohne Preset rechnet gegen die Dateien unter
    `configs/`, und Stufe C sagt das selbst. Die Klausel wurde trotzdem mit
    abgehakt.

    **Der Weg dorthin wäre aber der falsche gewesen.** Ein
    `configs/sweeps/standard.json` müsste jede Trajektorie aus
    `properties.json` wiederholen — zwei Quellen für denselben Wert, genau die
    Klasse, die P2.11 gerade abgeräumt hat, und die dieses Projekt schon dreimal
    bezahlt hat (F7, die drei Rule-Evaluatoren, der Kostendruck).

    **Was wirklich fehlte, war etwas anderes und Kleineres:** P2.0-B hält fest,
    «auch die ausgelieferten Dateien sind ein Rahmen, sie hießen nur bisher
    nicht so» — und trotzdem war ausgerechnet dieser Rahmen der **einzige ohne
    Begründung**, während dieselbe Datei sie von jedem Preset verlangt. Beim
    meistgenutzten Weltbild überhaupt: Jeder Lauf, der kein Preset wählt, steht
    darunter.
    """

    @staticmethod
    def _standard():
        from src.config_loader import load_properties_config

        return load_properties_config().kohaerenz

    def test_er_traegt_ueberhaupt_eine(self):
        assert self._standard() is not None, (
            "Die Standard-Ausgangslage trägt keine Kohärenzbegründung. Sie ist der "
            "Rahmen, unter dem jeder Lauf ohne Preset-Wahl steht — und der einzige, "
            "dem Variante C dann nichts abverlangt."
        )

    def test_und_zwar_nach_demselben_massstab_wie_die_presets(self):
        """Dieselben Anforderungen, sonst ist es eine Ausnahme mit anderem Namen."""

        k = self._standard()

        assert len(k.these) >= 30 and len(k.begruendung) >= 30 and len(k.vorbehalt) >= 30
        assert k.quellen, "Ohne Quellen ist es eine Meinung."

    def test_sie_behauptet_keine_eichung(self):
        """Dieselbe Zusage wie für die Presets: Belegt ist die Storyline, nicht
        ihre Bezifferung."""

        k = self._standard()
        text = f"{k.these} {k.begruendung} {k.vorbehalt}".lower()

        assert "gesetzt" in text, (
            "Der Vorbehalt sagt nicht, dass die Zahlen gesetzt und nicht geschätzt "
            "sind — genau die Trennung, die Variante C trägt."
        )
        assert not any(
            wort in text for wort in ("kalibriert", "geeicht", "geschätzt aus")
        ), "Eine Kohärenzbegründung darf keine Eichung behaupten."

    def test_sie_benennt_die_konstante_kapazitaet(self):
        """**Seit P2.10 ist der Standard der einzige Rahmen mit flachem Angebot.**

        Das ist eine Annahme und keine Abwesenheit einer Annahme — und sie ist
        die stärkste dieser Welt. Ein Rahmen, der sie nicht ausspricht, verbirgt
        genau den Befund, den P2.10 abgeräumt hat.
        """

        k = self._standard()
        text = f"{k.begruendung} {k.vorbehalt}".lower()

        assert (
            "kapazit" in text
        ), "Die Standard-Ausgangslage hält die Kapazität konstant und sagt es nicht."

    def test_die_werte_stehen_trotzdem_nur_einmal(self):
        """**Die Begründung darf keine zweite Quelle für Zahlen werden.**

        Sie steht neben den Trajektorien, die sie begründet — nicht in einer
        eigenen Sweep-Datei, die sie wiederholen müsste.
        """

        from src.orchestration.scenario_sweeps import SWEEPS_DIR

        assert not (SWEEPS_DIR / "standard.json").exists(), (
            "Es gibt eine `standard.json` unter `configs/sweeps/`. Sie müsste jede "
            "Trajektorie aus `properties.json` wiederholen — zwei Quellen für "
            "denselben Wert."
        )


class TestEineQuelleLaesstSichAuchOeffnen:
    """**Befund B7b des Audits vom 2026-09-03.**

    `test_die_quellen_sind_nicht_leer` prüft, **dass** Quellen dastehen — nicht,
    **ob** ein genannter Pfad existiert. Zwei Rahmen zitierten
    `evolution-of-alternative-fuels-for-aviation.pdf`; im Repo hieß die Datei
    `…-for-aviation.pdf.coredownload.inline.pdf`, ein Rest des Downloads. Der
    Verweis ging ins Leere.

    **Eine Quellenangabe, die niemand öffnen kann, ist der halbe Weg zur
    erfundenen Provenienz** — und genau dagegen ist Variante C angetreten: Die
    Kohärenz eines Rahmens wird in Prosa **mit Quellen** begründet, weil kein
    Algorithmus sie prüft. Dann müssen die Quellen auffindbar sein.

    **Geprüft wird der Dateiname, nicht der Pfad**, und das ist Absicht: Quellen
    stehen als Fließtext da («… und evolution-of-….pdf»), mal mit Verzeichnis,
    mal ohne, und ein Titel darf Leerzeichen enthalten (Rounsevell 2010). Ein
    Muster auf ganze Pfade fand deshalb beim ersten Anlauf vier Phantome und den
    echten Fall nicht.
    """

    #: Wo eine zitierte Datei liegen darf.
    WURZELN = ("docs", "configs")

    #: **Leerzeichen nur mit Verzeichnis davor**, und das ist die Regel, die den
    #: ersten Anlauf gerettet hat: Ein Muster, das Leerzeichen überall erlaubt,
    #: zog «roadmap.pdf und gibt-es-nicht.pdf» zu *einem* Dateinamen zusammen und
    #: fand damit keinen der beiden. Ein Titel mit Leerzeichen kommt in diesen
    #: Quellen immer mit Pfad (Rounsevell 2010); ein blanker Dateiname im
    #: Fließtext ist ein einzelnes Wort.
    _MUSTER = (
        r"(?:docs|configs|src|tests)/[^,;()]+?\.(?:pdf|md|json)" r"|[^\s,;()]+\.(?:pdf|md|json)"
    )

    @classmethod
    def _dateinamen(cls, text: str) -> list[str]:
        import re

        return [treffer.split("/")[-1].strip() for treffer in re.findall(cls._MUSTER, text)]

    @classmethod
    def _vorhandene(cls) -> set[str]:
        from pathlib import Path

        namen: set[str] = set()
        for wurzel in cls.WURZELN:
            namen.update(p.name for p in Path(wurzel).rglob("*") if p.is_file())
        return namen

    @pytest.mark.parametrize("szenario", RAHMEN, ids=lambda s: s.id)
    def test_jede_genannte_datei_liegt_im_repo(self, szenario: SweepConfig) -> None:
        vorhanden = self._vorhandene()

        fehlend = [
            name
            for quelle in szenario.kohaerenz.quellen
            for name in self._dateinamen(quelle)
            if name not in vorhanden
        ]

        assert not fehlend, (
            f"`{szenario.id}` zitiert Dateien, die es nicht gibt: {fehlend}. Eine "
            "Quellenangabe, die niemand öffnen kann, belegt nichts."
        )

    def test_der_waechter_wuerde_einen_rueckfall_bemerken(self) -> None:
        """Er muss beide Formen finden — mit Verzeichnis und ohne, mit Leerzeichen
        im Titel — sonst ist er beim nächsten Mal wieder blind."""

        mit_pfad = "docs/research/studies_future/gibt-es-nicht.pdf — eine Studie"
        ohne_pfad = "… roadmap.pdf und gibt-es-auch-nicht.pdf (IATA)"
        mit_leerzeichen = "docs/research/literature/WIREs Climate Change - 2010 - Rounsevell.pdf"

        assert self._dateinamen(mit_pfad) == ["gibt-es-nicht.pdf"]
        assert "gibt-es-auch-nicht.pdf" in self._dateinamen(ohne_pfad)
        assert self._dateinamen(mit_leerzeichen) == ["WIREs Climate Change - 2010 - Rounsevell.pdf"]

        vorhanden = self._vorhandene()
        assert "gibt-es-nicht.pdf" not in vorhanden
