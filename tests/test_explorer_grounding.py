"""P2.5 — die Antwort des State Explorers wird gegen die Daten gehalten.

**Der Befund:** Das Glossar beschrieb den State Explorer als «grounded Q&A
ausschließlich über abgeschlossene Run-Daten — keine erfundenen Zahlen».
Durchgesetzt wurde davon **nichts**: `ask()` reichte die Antwort des
Sprachmodells unverändert zurück. Die Zusage war ein Satz im Prompt, keine
Schranke — und zwar an genau der Oberfläche, an der ein Fachprüfer sie zuerst
ausprobiert.

**Was die Prüfung beantwortet, und was nicht.** Sie sagt: *«Steht diese Zahl in
den Laufdaten?»* — nicht *«ist diese Zahl richtig»*. Der Unterschied ist keine
Spitzfindigkeit: Eine korrekt ausgerechnete Differenz («der Preis stieg um 12,50
Euro») steht nirgends in den Daten und wird als unbelegt markiert. Das ist
**gewollt**. Ein Prüfer soll sehen, welche Zahl abgelesen und welche gerechnet
ist; ob die Rechnung stimmt, kann keine Textprüfung wissen.

**Markieren statt zurückweisen** — die Produktentscheidung, die das Paket
offengelassen hatte. Zurückweisen wäre die härtere Zusage und die falsche: Eine
Antwort mit einer gerechneten Prozentangabe wäre damit unbrauchbar, obwohl sie
stimmt. Eine markierte Antwort lässt den Leser entscheiden und verschweigt
nichts.

**Fehlalarme sind hier teuer**, teurer als anderswo: Wer dreimal eine Markierung
an einer offensichtlich richtigen Zahl sieht, liest die vierte nicht mehr.
Deshalb prüfen unten mehr Fälle die *Ruhe* der Prüfung als ihren Alarm.
"""

from __future__ import annotations

import pytest

from src.reporting.state_explorer import Antwort, _zahlen, pruefe_gegen_kontext

#: Ein Kontextblock, wie ihn `build_grounded_context_block` erzeugt — knapp,
#: aber mit den Formen, die wirklich vorkommen: Nachkommastellen, Anteile,
#: ganze Zahlen.
KONTEXT = """
tick_mechanics:
  tick: 12
  ticket_price: 140.38
  booking_rate: 0.4818
  cost_pressure: 112.05
population: 1080
"""


class TestEineAbgeleseneZahlGiltAlsBelegt:
    """Die Ruhe der Prüfung — wichtiger als ihr Alarm."""

    @pytest.mark.parametrize(
        ("antwort", "warum"),
        [
            ("Der Ticketpreis lag bei 140,38 Euro.", "exakt, deutsche Schreibweise"),
            ("The ticket price was 140.38 EUR.", "exakt, englische Schreibweise"),
            ("Der Ticketpreis lag bei rund 140 Euro.", "gerundet auf ganze Euro"),
            ("Die Buchungsrate betrug 48,18 Prozent.", "Anteil als Prozent geschrieben"),
            ("Die Buchungsrate lag bei 48,2 %.", "Prozent, gerundet"),
            ("Es waren 1.080 Personen.", "mit Tausenderpunkt"),
            ("Es waren 1080 Personen in Tick 12.", "zwei Zahlen, beide abgelesen"),
            ("Es gab keine auffälligen Ereignisse.", "gar keine Zahl"),
        ],
    )
    def test_sie_wird_nicht_markiert(self, antwort: str, warum: str):
        ergebnis = pruefe_gegen_kontext(antwort, KONTEXT)

        assert ergebnis.belegt, f"Fehlalarm bei «{warum}»: {ergebnis.unbelegt}"


class TestEineErfundeneZahlWirdMarkiert:
    @pytest.mark.parametrize(
        ("antwort", "erwartet"),
        [
            ("Der Ticketpreis lag bei 152,90 Euro.", "152,90"),
            ("Die Buchungsrate betrug 61 Prozent.", "61"),
            ("Es waren 2400 Personen.", "2400"),
        ],
    )
    def test_sie_steht_im_befund(self, antwort: str, erwartet: str):
        ergebnis = pruefe_gegen_kontext(antwort, KONTEXT)

        assert not ergebnis.belegt
        assert erwartet in ergebnis.unbelegt

    def test_eine_gerechnete_zahl_wird_ebenfalls_markiert(self):
        """**Gewollt, und die Grenze der Prüfung.**

        «Der Preis stieg um 12,50 Euro» kann korrekt gerechnet sein — in den
        Daten steht die Zahl trotzdem nicht. Die Prüfung kann eine richtige
        Rechnung nicht von einer Erfindung unterscheiden und behauptet das auch
        nicht; der angehängte Vorbehalt sagt es ausdrücklich.
        """

        ergebnis = pruefe_gegen_kontext("Der Preis stieg um 12,50 Euro.", KONTEXT)

        assert "12,50" in ergebnis.unbelegt
        assert "eigene Rechnung" in str(ergebnis)

    def test_dieselbe_zahl_wird_nur_einmal_gemeldet(self):
        ergebnis = pruefe_gegen_kontext("Erst 999, dann wieder 999.", KONTEXT)

        assert ergebnis.unbelegt == ("999",)


class TestDieZahlenzerlegungIstDerWundePunkt:
    """**Hier saß der Fehler des ersten Anlaufs**, und er war unsichtbar.

    Das Muster für Tausendertrennung fraß die Nachkommastellen: `0.4818` wurde
    als `0.481` erkannt und zu **481** normalisiert. Eine Buchungsrate von 48 %
    galt damit als unbelegt, obwohl sie in den Daten stand — ein Fehlalarm auf
    der häufigsten Zahl des ganzen Modells.

    Trennzeichen sind mehrdeutig: Im Deutschen trennt das Komma die
    Nachkommastellen, im Englischen der Punkt, und eine Antwort kann beides
    enthalten. Entschieden wird nach der **Stellenzahl**.
    """

    @pytest.mark.parametrize(
        ("text", "wert", "stellen"),
        [
            ("140.38", 140.38, 2),
            ("140,38", 140.38, 2),
            ("0.4818", 0.4818, 4),
            ("48,2", 48.2, 1),
            ("1080", 1080.0, 0),
            # Drei Ziffern hinter einem einzelnen Trennzeichen sind mehrdeutig.
            # Gewählt ist die Tausenderlesart — in einem Text über
            # Bevölkerungszahlen die häufigere.
            ("1.080", 1080.0, 0),
            ("12.345,67", 12345.67, 2),
        ],
    )
    def test_sie_liest_beide_schreibweisen(self, text: str, wert: float, stellen: int):
        gefunden = _zahlen(text)

        assert len(gefunden) == 1, f"«{text}» zerfiel in {len(gefunden)} Zahlen"
        assert gefunden[0][1] == pytest.approx(wert)
        assert gefunden[0][2] == stellen

    def test_der_alte_fehler_wuerde_heute_auffallen(self):
        """Die Nachstellung — sonst prüft der Wächter nur sich selbst."""

        _, wert, _, _ = _zahlen("0.4818")[0]

        assert wert == pytest.approx(0.4818), f"Als {wert} gelesen statt als 0,4818"

    def test_ein_prozentzeichen_wird_als_einheit_erkannt(self):
        assert _zahlen("48,2 %")[0][3] is True
        assert _zahlen("48,2 Prozent")[0][3] is True
        assert _zahlen("48,2 Euro")[0][3] is False


class TestDerVorbehaltGehtNichtVerloren:
    """Eine Prüfung, deren Ergebnis niemand sieht, ist keine."""

    def test_eine_belegte_antwort_bleibt_unveraendert(self):
        text = "Der Ticketpreis lag bei 140,38 Euro."

        assert str(pruefe_gegen_kontext(text, KONTEXT)) == text

    def test_eine_unbelegte_antwort_traegt_die_warnung_im_text(self):
        """`str()` ist der Weg, auf dem der Vorbehalt bei den Oberflächen
        ankommt — Dashboard, Legacy-UI und CLI behandeln die Antwort als Text."""

        ergebnis = pruefe_gegen_kontext("Der Preis lag bei 152,90 Euro.", KONTEXT)
        ausgabe = str(ergebnis)

        assert "152,90" in ausgabe
        assert "Nicht in den Laufdaten belegt" in ausgabe
        assert ergebnis.text in ausgabe, "Die eigentliche Antwort fehlt"

    def test_die_zahl_der_geprueften_wird_mitgefuehrt(self):
        """Ohne sie sähe eine Antwort **ohne** Zahlen genauso sauber aus wie
        eine vollständig belegte — und das sind zwei verschiedene Aussagen."""

        ohne = pruefe_gegen_kontext("Keine Auffälligkeiten.", KONTEXT)
        mit = pruefe_gegen_kontext("Der Preis lag bei 140,38 Euro.", KONTEXT)

        assert ohne.geprueft == 0 and ohne.belegt
        assert mit.geprueft == 1 and mit.belegt


class TestAskFuehrtDiePruefungAus:
    """Die Zusage am Ende der Kette — nicht nur die Funktion daneben."""

    @staticmethod
    def _kontext(tmp_path):
        from src.reporting.state_explorer import RunExplorerContext

        return RunExplorerContext(
            run_id="test",
            run_dir=tmp_path,
            tick_mechanics={
                "ticks": [{"tick": 12, "ticket_price": 140.38, "booking_rate": 0.4818}]
            },
            event_log=[],
            price_history=[],
            factors_timeseries=[],
            metadata={},
            run_scenario={},
            focus_tick=12,
            checkpoint_tick=None,
            checkpoint_snapshot=None,
        )

    def test_eine_erfundene_zahl_kommt_markiert_zurueck(self, tmp_path):
        from src.reporting.state_explorer import StateExplorer

        class ErfindetZahlen:
            def call(self, prompt: str) -> str:
                return "Der Ticketpreis lag bei 999,99 Euro."

        explorer = StateExplorer(self._kontext(tmp_path), llm=ErfindetZahlen())
        antwort = explorer.ask("Wie hoch war der Preis?")

        assert isinstance(antwort, Antwort), "`ask` gibt wieder rohen Text zurück"
        assert "999,99" in antwort.unbelegt

    def test_der_rueckgabetyp_ist_kein_string_mehr(self, tmp_path):
        """**Der Rückfall, den es zu verhindern gilt.**

        Gäbe `ask` wieder eine Zeichenkette zurück, wäre die Prüfung weg und
        alles andere hier grün — die Tests oben prüfen `pruefe_gegen_kontext`,
        nicht den Weg dorthin.
        """

        from src.reporting.state_explorer import StateExplorer

        class Stumm:
            def call(self, prompt: str) -> str:
                return "Keine Angabe."

        explorer = StateExplorer(self._kontext(tmp_path), llm=Stumm())

        assert not isinstance(explorer.ask("?"), str)

    def test_eine_abgelesene_zahl_kommt_sauber_durch(self, tmp_path):
        """Sonst könnte `ask` alles markieren und wäre trotzdem grün."""

        from src.reporting.state_explorer import StateExplorer

        class LiestAb:
            def call(self, prompt: str) -> str:
                return "Der Ticketpreis lag bei 140,38 Euro."

        explorer = StateExplorer(self._kontext(tmp_path), llm=LiestAb())

        assert explorer.ask("Wie hoch war der Preis?").belegt


class TestDieTrennschaerfeStehtDabei:
    """**Befund B7c des Audits vom 2026-09-03.**

    Die Prüfung fragt «steht diese Zahl irgendwo in den Laufdaten» — **ohne
    Bezug zur Größe**. Das ist so gewollt und im Docstring von
    `pruefe_gegen_kontext` sauber gesagt; unsichtbar war die Folge daraus: Je
    mehr Zahlen im Kontextblock stehen, desto eher findet sich für eine
    erfundene zufällig eine Entsprechung. Ein «belegt» aus einem Block mit
    dreißig Zahlen wiegt anders als eines aus einem mit dreihundert, und wer die
    Antwort las, konnte das nicht wissen.

    **Behoben wird das nicht durch eine schärfere Prüfung, sondern durch eine
    ehrlichere Auskunft.** Eine Zuordnung von Zahl zu Größe wäre eine zweite
    Behauptung — sie müsste raten, worauf sich «140,38» im Satz bezieht. Die
    Grenze bleibt; sie steht jetzt nur dabei.
    """

    KONTEXT = "tick 1: preis 140.38, rate 0.4818; tick 2: preis 141.02, rate 0.4712"

    def test_die_zahl_der_kontextzahlen_wird_mitgefuehrt(self):
        antwort = pruefe_gegen_kontext("Der Preis lag bei 140,38.", self.KONTEXT)

        assert antwort.kontextzahlen > 0
        assert antwort.geprueft == 1

    def test_doppelte_zaehlen_nur_einmal(self):
        """Sonst maesse die Zahl die Laenge des Blocks statt seiner Vielfalt —
        und genau die Vielfalt entscheidet, wie leicht ein Zufallstreffer fällt."""

        einmal = pruefe_gegen_kontext("x", "preis 140.38")
        dreimal = pruefe_gegen_kontext("x", "preis 140.38, 140.38, 140.38")

        assert einmal.kontextzahlen == dreimal.kontextzahlen

    def test_der_vorbehalt_nennt_beide_zahlen(self):
        """Der angehängte Satz ist der einzige Weg, auf dem die Auskunft eine
        Oberfläche erreicht, die `str()` benutzt."""

        antwort = pruefe_gegen_kontext(
            "Der Preis lag bei 140,38 und stieg um 213,50.", self.KONTEXT
        )
        text = str(antwort)

        assert not antwort.belegt
        assert f"{antwort.geprueft} Zahlen" in text
        assert f"{antwort.kontextzahlen} verschiedene Zahlen" in text

    def test_eine_belegte_antwort_bleibt_still(self):
        """**Die Auskunft gehört zum Vorbehalt, nicht zu jeder Antwort.**

        Wer nichts Unbelegtes sagt, bekommt keinen Anhang — sonst stünde unter
        jeder Antwort eine Fußnote, und die Markierung, auf die es ankommt,
        ginge darin unter.
        """

        antwort = pruefe_gegen_kontext("Der Preis lag bei 140,38.", self.KONTEXT)

        assert antwort.belegt
        assert str(antwort) == antwort.text


def _grosser_kontext() -> str:
    """Ein Kontextblock in der Dichte eines echten Laufs (N10).

    Vierzig Ticks: Buchungsrate von 47,9 % auf 35,7 % fallend, Ticketpreis um
    140 EUR, CO₂-Abgabe 50 EUR, dazu viele kleine Deltas und Bruchteile — genau
    die Zahlen, an denen die Prüfung bis P8-V3 jede ganzzahlige Prozentangabe
    durchließ. Der Kontext des Tests aus P2.5 hatte fünf Zahlen und fand es nie.
    """

    zeilen = []
    for tick in range(1, 41):
        rate = 0.479 - (0.479 - 0.357) * (tick - 1) / 39
        zeilen.append(
            f"tick: {tick}, booking_rate: {rate:.4f}, ticket_price: {140.6 - 0.2 * tick:.2f}, "
            f"price_delta: {-0.0123 * (tick % 7):.4f}, demand_delta: {0.0071 * (tick % 5):.4f}, "
            f"carbon_tax_level: 50.0"
        )
    return "\n".join(zeilen)


class TestEineProzentangabeWirdAlsProzentGeprueft:
    """**N10 aus der Gegenprüfung vom 2026-09-21, behoben mit P8-V3.**

    Eine ganzzahlige Prozentangabe wurde zu einem Anteil verkleinert und auf
    null Stellen gerundet — «49 %» wurde 0,0, und jede Kontextzahl unter 0,5
    ebenfalls. Gegen einen echten Lauf galten 250 von 250 ganzzahligen
    Prozentangaben als belegt, darunter die falsche «49 %» einer echten
    `llama3.2`-Antwort. Nach der Korrektur, gemessen am 2026-09-30 an zwei
    Läufen: 72 und 70 von 250, und die übrigen Treffer sind Anteile, die wirklich
    in den Daten stehen.
    """

    def test_die_erfundene_rate_aus_dem_audit_wird_markiert(self):
        antwort = pruefe_gegen_kontext(
            "Die Buchungsrate stieg auf einen Maximalwert von 49 %.", _grosser_kontext()
        )

        assert antwort.unbelegt == ("49",)

    def test_eine_prozentangabe_trifft_keinen_preis(self):
        """«140 %» ist keine Aussage über einen Preis von 140 EUR."""

        assert not pruefe_gegen_kontext("Der Wert lag bei 140 %.", _grosser_kontext()).belegt

    @pytest.mark.parametrize("angabe", ["47,9 %", "48 %", "36 %", "35,7 Prozent"])
    def test_eine_abgelesene_rate_bleibt_belegt(self, angabe: str):
        antwort = pruefe_gegen_kontext(f"Die Buchungsrate lag bei {angabe}.", _grosser_kontext())

        assert antwort.belegt, antwort.unbelegt

    def test_die_meisten_erfundenen_prozente_fallen_auf(self):
        """Die Sperrklinke gegen den Rückfall: Vorher galten alle 240 als belegt."""

        kontext = _grosser_kontext()
        belegt = [
            p for p in range(11, 251) if pruefe_gegen_kontext(f"Es waren {p} %.", kontext).belegt
        ]

        # Belegt sind nur die Raten, die wirklich im Lauf vorkommen (36 bis 48 %),
        # und 100, das als harmlos gar nicht geprüft wird. «200 %» traf bis zur
        # Korrektur Tick 2 — eine ganze Zahl ist kein Anteil.
        assert set(belegt) <= set(range(35, 49)) | {100}, belegt
