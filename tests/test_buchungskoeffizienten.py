"""P2.1 — jeder Koeffizient des Buchungsmodells sagt, woher er kommt.

Acht Zahlen bestimmen, wie stark Preis, CO₂-Abgabe und Bahnalternative gegen den
Nutzen arbeiten — und damit jede Buchungsrate, die das Produkt ausgibt. Bis zum
2026-08-30 standen sie als Literale in `booking_probability`, ohne dass
irgendwo stand, woher sie stammen.

**Die Herkunftsangabe trennt zwei Dinge, die auseinanderfallen:** die
Funktionsform und den Zahlenwert. Dass der Preis negativ in den Nutzen eingeht,
ist belegt (Ben-Akiva/Lerman 1985, McFadden 1974). Dass der Faktor für die
Substitution **1,5** beträgt, ist es nicht — `docs/research/references.md` sagt
für genau diesen Term, es gebe «keine Standard-Einheitsformel, sondern
modellabhängig».

**Eine Literaturangabe an eine handgesetzte Zahl zu heften wäre schlimmer als
gar keine**: Sie sähe aus wie eine Kalibrierung. Deshalb prüfen diese Tests
nicht, *dass* eine Quelle dasteht, sondern dass sie **beides** benennt — und
dass keine von ihnen so tut, als sei der Wert geschätzt.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.config_loader import load_properties_config
from src.models.property_models import BookingModelConfig

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLER = REPO_ROOT / "src" / "population" / "population_sampler.py"
PROPERTIES_JSON = REPO_ROOT / "configs" / "properties.json"

NAMEN = tuple(BookingModelConfig.model_fields)


class TestJederKoeffizientTraegtSeineHerkunft:
    @pytest.mark.parametrize("name", NAMEN)
    def test_die_quelle_ist_ein_satz(self, name: str) -> None:
        quelle = getattr(BookingModelConfig(), name).quelle

        assert len(quelle) >= 60, (
            f"Die Herkunft von `{name}` ist zu knapp für eine Auskunft: {quelle!r}. "
            "Sie soll einem Fachprüfer sagen, was belegt ist und was gesetzt."
        )

    @pytest.mark.parametrize("name", NAMEN)
    def test_sie_sagt_ob_der_wert_gesetzt_oder_geschaetzt_ist(self, name: str) -> None:
        """Der Kern: Kein Koeffizient darf offenlassen, woher seine Zahl kommt."""

        quelle = getattr(BookingModelConfig(), name).quelle.lower()

        bekennt_sich = any(
            wort in quelle for wort in ("gesetzt", "normierung", "normierungsgröße", "ausgangswert")
        )
        assert bekennt_sich, (
            f"Die Herkunft von `{name}` sagt nicht, ob die Zahl gesetzt oder geschätzt "
            f"ist: {quelle!r}. Genau diese Auskunft ist der Zweck des Feldes."
        )

    def test_keine_quelle_behauptet_eine_schaetzung(self) -> None:
        """**Keiner** dieser Werte ist aus Daten geschätzt. Sagt eine Quelle das
        doch, ist entweder die Angabe falsch oder jemand hat wirklich
        kalibriert — dann gehört dieser Test angepasst, mit der Studie daneben."""

        behauptend = [
            name
            for name in NAMEN
            if any(
                wort in getattr(BookingModelConfig(), name).quelle.lower()
                for wort in ("geschätzt aus", "kalibriert an", "empirisch ermittelt")
            )
        ]
        assert not behauptend, (
            f"Diese Koeffizienten behaupten eine Schätzung: {behauptend}. "
            "Eine erfundene Provenienz ist schlimmer als eine fehlende."
        )

    def test_eine_floskel_wird_abgewiesen(self) -> None:
        """Der Wächter im Modell selbst — sonst wäre `quelle` ein Pflichtfeld
        ohne Anspruch, und `quelle=\"tbd\"` erfüllte ihn."""

        from src.models.property_models import BookingCoefficient

        with pytest.raises(ValueError):
            BookingCoefficient(wert=1.0, quelle="handgesetzt")


class TestDieZahlenStehenNichtMehrImCode:
    """Sonst gäbe es sie zweimal — und die Herkunftsangabe hinge an der falschen."""

    def test_booking_probability_traegt_keine_eigenen_zahlen(self) -> None:
        baum = ast.parse(SAMPLER.read_text(encoding="utf-8"))
        funktion = next(
            k
            for k in ast.walk(baum)
            if isinstance(k, ast.FunctionDef) and k.name == "booking_probability"
        )

        # `0.0` und `1.0` bleiben erlaubt: Sie sind die Grenzen des
        # Wertebereichs und der neutrale Faktor, keine Modellparameter.
        erlaubt = {0.0, 1.0}
        zahlen = [
            k.value
            for k in ast.walk(funktion)
            if isinstance(k, ast.Constant)
            and isinstance(k.value, (int, float))
            and not isinstance(k.value, bool)
            and float(k.value) not in erlaubt
        ]

        assert not zahlen, (
            f"`booking_probability` trägt wieder eigene Zahlen: {zahlen}. "
            "Sie gehören nach `BookingModelConfig` — dort tragen sie ihre Herkunft."
        )

    def test_die_alten_konstanten_sind_weg(self) -> None:
        quelle = SAMPLER.read_text(encoding="utf-8")
        baum = ast.parse(quelle)
        namen = {
            ziel.id
            for k in baum.body
            if isinstance(k, ast.Assign)
            for ziel in k.targets
            if isinstance(ziel, ast.Name)
        }

        alt = {
            "DEFAULT_GREEN_PREMIUM",
            "HIGH_PRICE_SENSITIVITY_THRESHOLD",
            "HIGH_PRICE_SENSITIVITY_PENALTY",
            "DEFAULT_CARBON_ECO_BASELINE",
            "DEFAULT_LOGIT_THRESHOLD",
        }
        assert not (namen & alt), f"Alte Modellkonstanten sind zurück: {sorted(namen & alt)}"


class TestDateiUndModellLaufenNichtAuseinander:
    """Zwei Orte, eine Wahrheit — und ein Test, der das hält.

    Die Werte stehen im Modell (mit Herkunft) **und** in
    `configs/properties.json` (damit man sie im Editor sieht). Das ist eine
    Doppelung, und die trägt dieses Projekt nur mit einem Wächter daneben —
    dieselbe Entscheidung wie beim gebauten Stylesheet.
    """

    @pytest.mark.parametrize("name", NAMEN)
    def test_der_wert_stimmt_ueberein(self, name: str) -> None:
        aus_datei = getattr(load_properties_config().booking_model, name)
        aus_modell = getattr(BookingModelConfig(), name)

        assert aus_datei.wert == aus_modell.wert, (
            f"`{name}`: Datei sagt {aus_datei.wert}, Modell sagt {aus_modell.wert}. "
            "Ein Lauf nimmt die Datei — die Herkunftsangabe im Modell beschriebe "
            "dann eine andere Zahl."
        )

    @pytest.mark.parametrize("name", NAMEN)
    def test_die_herkunft_stimmt_ueberein(self, name: str) -> None:
        aus_datei = getattr(load_properties_config().booking_model, name)
        aus_modell = getattr(BookingModelConfig(), name)

        assert aus_datei.quelle == aus_modell.quelle

    def test_die_ausgelieferte_datei_traegt_den_block(self) -> None:
        """Ohne ihn fiele der Lauf auf die Modellvorgaben zurück — richtig, aber
        unsichtbar. Wer die Konfiguration liest, soll die Zahlen finden."""

        daten = json.loads(PROPERTIES_JSON.read_text(encoding="utf-8"))

        assert "booking_model" in daten, "configs/properties.json kennt die Koeffizienten nicht"
        assert set(daten["booking_model"]) == set(NAMEN)


def test_ein_schreibzugriff_des_modell_editors_verliert_den_block_nicht(tmp_path, monkeypatch):
    """Der Editor kennt `booking_model` nicht — und darf es trotzdem nicht löschen.

    Seine Schreiber lesen die ganze Datei, setzen einen Schlüssel und schreiben
    zurück. Damit überlebt jeder Block, den sie nicht kennen. Das ist eine
    Eigenschaft, auf die man sich verlässt, sobald man einen neuen hinzufügt —
    also gehört sie gemessen und nicht angenommen.
    """

    import shutil

    import dashboard.config_catalog as catalog

    shutil.copy(PROPERTIES_JSON, tmp_path / "properties.json")
    monkeypatch.setattr(catalog, "CONFIGS_DIR", tmp_path)
    catalog.save_saturation_to_file(
        catalog.SaturationEditState(booking_increase=0.45, utility_penalty_factor=0.8),
        "properties.json",
    )
    danach = json.loads((tmp_path / "properties.json").read_text(encoding="utf-8"))

    assert "booking_model" in danach, (
        "Ein Schreibzugriff des Modell-Editors hat die Buchungskoeffizienten "
        "aus der Datei entfernt — dann fiele der Lauf still auf die "
        "Modellvorgaben zurück."
    )
    assert danach["booking_model"]["substitution_weight"]["wert"] == 1.5
    assert danach["booking_model"]["substitution_weight"]["quelle"]
