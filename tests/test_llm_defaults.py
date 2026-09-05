"""P3.4: Modellname und Endpunkt kommen aus einer Quelle (2026-09-05).

**Der Befund wuchs mit jedem neuen Modul.** `"llama3.2"` stand in neun
Produktionsdateien, der Endpunkt in zwei Schreibweisen über sieben — und die
beim Dash-Umbau *neu* entstandenen `config_editor`-Module hatten die
Hartkodierung geerbt, ohne dass jemand sie dort hingeschrieben hätte: Sie war
kopiert. Ein Endpunktwechsel war damit eine Suche über das ganze Repo, und
`configs/simulation_config.json` führte still ein anderes Modell (`llama3`) als
alle anderen Stellen.

**Warum der Wächter ein AST-Durchlauf ist und keine Liste:** Eine Aufzählung der
neun Dateien fängt einen Rückfall an bekannter Stelle und übersieht das zehnte
Modul — genau die Bauform, die bei Invariante 1 (`test_cost_pressure_source.py`)
und beim Farbfundament (`test_web_theme.py`) schon einmal die richtige war. Was
hier gemessen wird, ist nicht «steht es noch in Datei X», sondern «gibt es
irgendwo eine zweite Quelle».
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src.llm.defaults import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    ENV_KEYS,
)
from src.llm.llm_client import OllamaConfig

ROOT = Path(__file__).resolve().parent.parent

#: Die Bäume, in denen keine zweite Quelle stehen darf. `legacy_streamlit` ist
#: bewusst draußen: abgelöste Oberfläche, nur noch zum Vergleich lauffähig
#: (P5.2 entfernt sie).
GEPRUEFTE_BAEUME = ("src", "dashboard")

#: Die Datei, die die Werte **halten darf** — sie ist die Quelle.
QUELLE = Path("src") / "llm" / "defaults.py"

#: Was als hartkodierte Wiederholung gilt. Bewusst nur Modellname und Endpunkt:
#: `0.7` und `2048` sind auch außerhalb dieses Themas gewöhnliche Zahlen, und ein
#: Wächter, der jede 0,7 im Repo meldet, wird abgeschaltet statt gelesen.
VERBOTENE_TEXTE = (DEFAULT_MODEL, "llama3", "11434", "localhost:11434")


def _laufzeit_zeichenketten(pfad: Path) -> list[tuple[int, str]]:
    """Alle Zeichenketten einer Datei **außer** Docstrings und Kommentaren.

    Docstrings dürfen `llama3.2` nennen — sie erklären, und `dashboard/
    llm_status.py` tut das mit Recht («Ollama führt Modelle als `llama3.2:latest`»).
    Kommentare tauchen im Syntaxbaum ohnehin nicht auf. Was übrig bleibt, ist
    Code, der einen Wert *setzt*.
    """

    baum = ast.parse(pfad.read_text(encoding="utf-8"))
    docstrings: set[int] = set()
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            if knoten.body and isinstance(knoten.body[0], ast.Expr):
                erster = knoten.body[0].value
                if isinstance(erster, ast.Constant) and isinstance(erster.value, str):
                    docstrings.add(id(erster))

    gefunden: list[tuple[int, str]] = []
    for knoten in ast.walk(baum):
        if (
            isinstance(knoten, ast.Constant)
            and isinstance(knoten.value, str)
            and id(knoten) not in docstrings
        ):
            gefunden.append((knoten.lineno, knoten.value))
    return gefunden


class TestEineQuelleFuerModellUndEndpunkt:
    def test_kein_modul_traegt_eine_zweite_quelle(self):
        """Ein Endpunktwechsel ist genau eine Änderung — die Zusage von P3.4."""

        befunde: list[str] = []
        for baum in GEPRUEFTE_BAEUME:
            for pfad in sorted((ROOT / baum).rglob("*.py")):
                relativ = pfad.relative_to(ROOT)
                if relativ == QUELLE or "legacy_streamlit" in relativ.parts:
                    continue
                for zeile, text in _laufzeit_zeichenketten(pfad):
                    treffer = [v for v in VERBOTENE_TEXTE if v in text]
                    if treffer:
                        befunde.append(f"{relativ}:{zeile} enthält {treffer} in {text!r}")

        assert not befunde, (
            "Diese Stellen tragen Modellname oder Endpunkt selbst, statt sie aus "
            f"`{QUELLE.as_posix()}` zu nehmen:\n  " + "\n  ".join(befunde)
        )

    def test_der_waechter_wuerde_einen_rueckfall_bemerken(self, tmp_path, monkeypatch):
        """Ein Wächter, der nie etwas sieht, könnte auch blind sein.

        Nachgestellt wird die häufigste Form des Rückfalls: ein neues Modul mit
        einem eigenen Vorgabewert — so ist er in `config_editor/compute_mode.py`
        entstanden, per Kopie und ohne Absicht.
        """

        rueckfall = tmp_path / "src" / "neues_modul.py"
        rueckfall.parent.mkdir(parents=True)
        rueckfall.write_text(
            '"""Ein Modul, das llama3.2 nur erwähnt — das ist erlaubt."""\n'
            'MODELL = "llama3.2"\n',
            encoding="utf-8",
        )

        zeichenketten = _laufzeit_zeichenketten(rueckfall)

        assert ("llama3.2" in text for _, text in zeichenketten)
        assert [t for _, t in zeichenketten] == ["llama3.2"], (
            "Der Docstring wurde mitgezählt oder die Zuweisung übersehen — im "
            "ersten Fall meldet der Wächter Erklärungen, im zweiten nichts."
        )

    def test_der_endpunkt_ist_ipv4(self):
        """**Nicht `localhost`**, und das ist kein Geschmack.

        `localhost` löst auf manchen Windows-Installationen zuerst nach `::1`
        auf, während Ollama nur auf IPv4 lauscht — der Aufruf läuft dann in einen
        Verbindungsfehler, den niemand dem Namen ansieht. Vorher standen beide
        Schreibweisen im Repo, in fünf und zwei Dateien.
        """

        assert DEFAULT_BASE_URL == "http://127.0.0.1:11434"
        assert "localhost" not in DEFAULT_BASE_URL

    def test_die_ausgelieferte_config_nennt_dasselbe_modell(self):
        """Der sichtbarste Beleg des Befunds: `simulation_config.json` führte `llama3`.

        Niemandem fiel es auf, weil der Wert nirgends ankam — genau die Hälfte
        des Befunds, die mit dem Anschluss von `config.llm` weggeht.
        """

        import json

        config = json.loads((ROOT / "configs" / "simulation_config.json").read_text("utf-8"))

        assert config["llm"]["model"] == DEFAULT_MODEL, (
            "Die ausgelieferte Konfiguration nennt ein anderes Modell als der "
            "Vorgabewert — und seit P3.4 wird sie wirklich gelesen."
        )


class TestDieUmgebungWirktUeberall:
    """Der Sweep-Befund vom 2026-08-27: `OLLAMA_BASE_URL` blieb wirkungslos.

    Die Env-Übersetzung saß ausschließlich in `studio_helpers.LocalOllama`. Jeder
    Aufrufer, der `OllamaConfig()` direkt baute — der Sweep-Pfad tut genau das —,
    ignorierte sie stillschweigend. Beim Nachstellen eines Sweeps gegen einen
    toten Endpunkt stand trotz `OLLAMA_BASE_URL=…:9` weiterhin der Vorgabewert
    da. **Eine Variable zu setzen und nichts zu bewirken ist dieselbe Klasse von
    Problem wie ein hartkodierter Wert.**
    """

    def test_ohne_umgebung_gelten_die_vorgabewerte(self, monkeypatch):
        for name in ENV_KEYS:
            monkeypatch.delenv(name, raising=False)

        config = OllamaConfig()

        assert config.model == DEFAULT_MODEL
        assert config.base_url == DEFAULT_BASE_URL
        assert config.temperature == DEFAULT_TEMPERATURE
        assert config.max_tokens == DEFAULT_MAX_TOKENS

    @pytest.mark.parametrize(
        ("name", "feld", "wert", "erwartet"),
        [
            ("OLLAMA_BASE_URL", "base_url", "http://127.0.0.1:9", "http://127.0.0.1:9"),
            ("OLLAMA_MODEL", "model", "mistral", "mistral"),
            ("OLLAMA_TEMPERATURE", "temperature", "0.1", 0.1),
            ("OLLAMA_MAX_TOKENS", "max_tokens", "256", 256),
        ],
    )
    def test_jede_variable_erreicht_einen_direkt_gebauten_client(
        self, monkeypatch, name, feld, wert, erwartet
    ):
        monkeypatch.setenv(name, wert)

        assert getattr(OllamaConfig(), feld) == erwartet

    def test_jede_dokumentierte_variable_wird_wirklich_gelesen(self, monkeypatch):
        """`ENV_KEYS` ist die Doku — sie darf nichts versprechen, was nicht wirkt."""

        for name, feld in ENV_KEYS.items():
            monkeypatch.setenv(name, "0.5" if feld == "temperature" else "7")
            wert = getattr(OllamaConfig(), feld)
            monkeypatch.delenv(name)
            vorgabe = getattr(OllamaConfig(), feld)

            assert wert != vorgabe, f"{name} bewirkt nichts an `{feld}`"

    def test_ein_ausdruecklicher_wert_gewinnt_gegen_die_umgebung(self, monkeypatch):
        """Sonst könnte eine gesetzte Variable einen Lauf umlenken, den jemand
        ausdrücklich anders konfiguriert hat."""

        monkeypatch.setenv("OLLAMA_MODEL", "mistral")

        assert OllamaConfig(model="llama3.2").model == "llama3.2"

    def test_eine_kaputte_zahl_faellt_zurueck_und_sagt_es(self, monkeypatch, caplog):
        """Ein `OLLAMA_TEMPERATURE=0,7` mit Komma ist der Alltagsfall.

        Der Rückfall bleibt — ein Lauf soll an einer Kommazahl nicht scheitern —,
        aber er ist nicht mehr still. Vorher bekam wer `2,0` schrieb genauso 0,7
        und keinen Hinweis.
        """

        import logging

        monkeypatch.setenv("OLLAMA_TEMPERATURE", "0,7")

        with caplog.at_level(logging.WARNING):
            config = OllamaConfig()

        assert config.temperature == DEFAULT_TEMPERATURE
        assert "OLLAMA_TEMPERATURE" in caplog.text

    def test_gelesen_wird_beim_bauen_nicht_beim_importieren(self, monkeypatch):
        """Ein Modul-Import darf nicht festlegen, was eine Stunde später gilt.

        Und ein Test, der die Umgebung setzt, käme sonst grundsätzlich zu spät —
        die Zusage dieses Tests ist die Voraussetzung aller anderen hier.
        """

        vorher = OllamaConfig().model
        monkeypatch.setenv("OLLAMA_MODEL", "ein-anderes-modell")

        assert OllamaConfig().model == "ein-anderes-modell" != vorher
