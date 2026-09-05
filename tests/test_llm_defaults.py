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

        # (Kein `assert (... for ...)` hier — ein Generator ist immer wahr. Die
        # Zusage steht in der Zeile darunter und prüft die *vollständige* Menge.)
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


class TestDerZustandTraegtDasSprachmodell:
    """P3.4, zweite Hälfte: `state.config.llm` wird wirklich benutzt.

    **Das Feld war da und tat nichts.** `SimulationConfig.llm` las kein
    Laufpfad — der echte Client entstand aus den CLI-Argumenten bzw. aus
    `RunLaunchConfig`, und die einzigen Leser waren die Studio-Schema-Defaults.
    Sichtbarster Beleg: `configs/simulation_config.json` führte `llama3`, während
    überall sonst `llama3.2` stand, und niemandem fiel es auf, weil der Wert
    nirgends ankam. `validation` prüfte ihn trotzdem — eine Prüfung ohne
    Gegenstand.

    Der Plan nennt drei Möglichkeiten und die schlechteste davon: «Halb
    stehenlassen». Entschieden wurde **anschließen**.
    """

    @staticmethod
    def _draft(**overrides):
        from dashboard.config_catalog import default_config_draft

        draft = default_config_draft()
        draft.mock_llm = False
        draft.rounds = 2
        for name, wert in overrides.items():
            setattr(draft, name, wert)
        return draft

    def test_der_entwurf_erreicht_den_zustand(self):
        from dashboard.config_catalog import prepare_simulation_state

        state = prepare_simulation_state(self._draft(model="mistral", temperature=0.25))

        assert state.config.llm.model == "mistral"
        assert state.config.llm.temperature == 0.25

    def test_der_client_bekommt_genau_das_was_im_zustand_steht(self):
        """**Die tragende Zusage.** Eine Quelle, zwei Leser — nicht zwei Quellen.

        Gemessen wird nicht «beide rufen dieselbe Funktion» (das wäre
        Codelektüre), sondern dass der gebaute Client Feld für Feld dasselbe
        trägt wie der Zustand.
        """

        from dashboard.config_catalog import llm_config_from_draft, prepare_simulation_state
        from src.llm import OllamaClient, OllamaConfig

        draft = self._draft(model="mistral", base_url="http://127.0.0.1:9", temperature=0.25)
        state = prepare_simulation_state(draft)
        aus_draft = llm_config_from_draft(draft)
        client = OllamaClient(
            OllamaConfig(
                base_url=aus_draft.base_url,
                model=aus_draft.model,
                temperature=aus_draft.temperature,
                max_tokens=aus_draft.max_tokens,
            )
        )

        assert client.config.model == state.config.llm.model
        assert client.config.base_url == state.config.llm.base_url
        assert client.config.temperature == state.config.llm.temperature
        assert client.config.max_tokens == state.config.llm.max_tokens

    def test_die_cli_leitet_dasselbe_ab(self):
        from argparse import Namespace

        from src.run_simulation import _llm_config_from_args, _ollama_client

        args = Namespace(
            model="mistral", base_url="http://127.0.0.1:9", temperature=0.25, max_tokens=128
        )
        llm_config = _llm_config_from_args(args)
        client = _ollama_client(llm_config)

        assert client.config.model == llm_config.model == "mistral"
        assert client.config.base_url == llm_config.base_url
        assert client.config.temperature == llm_config.temperature
        assert client.config.max_tokens == llm_config.max_tokens

    def test_ohne_sprachmodell_bleibt_das_feld_unberuehrt(self):
        """**Eine Regel, keine Lücke.** Gerufen wird nichts, also beschreibt es nichts.

        Die Werte ungeprüft mitzuschreiben hätte außerdem einen Mock-Lauf an
        einer Temperatur scheitern lassen, die niemand benutzt — und genau das
        war die bewusste Entscheidung, die vorher in `validate_draft` stand.
        """

        from dashboard.config_catalog import llm_config_from_draft, prepare_simulation_state
        from src.config_loader import load_simulation_config
        from src.llm.defaults import DEFAULT_MODEL

        draft = self._draft(mock_llm=True, model="mistral", temperature=5.0)

        assert llm_config_from_draft(draft) is None
        state = prepare_simulation_state(draft)
        assert state.config.llm.model == DEFAULT_MODEL != "mistral"
        assert state.config.llm.temperature == load_simulation_config().llm.temperature

    def test_ein_leeres_modellfeld_wird_gemeldet_und_nicht_ersetzt(self):
        """Kein erfundener Vorgabewert — die Regel aus P1.9-W5.1.

        Der erste Anlauf von `llm_config_from_draft` schrieb
        `draft.model.strip() or DEFAULT_MODEL`, und damit wurde aus «kein Modell
        angegeben» stillschweigend ein Lauf mit `llama3.2`. Aufgefallen ist es,
        weil die alte Doppelprüfung in `validate_draft` diesen Fall gemeldet
        hatte und die neue nicht mehr.
        """

        from dashboard.config_catalog import validate_draft

        befunde = [str(b) for b in validate_draft(self._draft(model=""))]

        assert any("Modellname" in b for b in befunde), befunde

    def test_die_pruefung_meldet_jeden_befund_genau_einmal(self):
        """Vorher stand jeder doppelt da — als «config.llm: …» und «Technik: …».

        Solange die Werte den Zustand nicht erreichten, war die zweite Prüfung
        nötig; seit sie es tun, war sie eine Doppelung. Gemessen am 2026-09-05.
        """

        from dashboard.config_catalog import validate_draft

        befunde = [str(b) for b in validate_draft(self._draft(temperature=5.0, max_tokens=0))]

        assert len(befunde) == 2, befunde
        assert len({b.split(":", 1)[1] for b in befunde}) == 2


class TestDerMockKommtNurAufAnsage:
    """P3.4, dritte Hälfte: `get_llm()` wählte still den Mock.

    **P0.1 hat den stillen Mock bei *Fehlern* beseitigt — die Auswahl davor
    blieb.** War weder ``OLLAMA_MODEL`` noch ``LLAMA_HTTP_URL`` noch
    ``LLAMA_TRANSFORMERS_MODEL`` gesetzt, gab `get_llm()` kommentarlos ein
    `MockLLM()` zurück. Wer Studio ohne gesetzte Umgebung startete, bekam
    **erfundene Agenten-Antworten, ohne sie angefordert zu haben** — kein
    `--mock-llm`, kein Hinweis, und nach der Definition aus Invariante 1 auch
    kein «Ausfall», weil nie ein Aufruf gescheitert ist.

    Zwei Aufrufer hingen daran: der Studio-Graph und die Szenario-CLI.
    """

    @staticmethod
    def _ohne_backend(monkeypatch) -> None:
        for name in (
            "OLLAMA_MODEL",
            "LLAMA_HTTP_URL",
            "LLAMA_TRANSFORMERS_MODEL",
            "AEROFORESIGHT_MOCK_LLM",
        ):
            monkeypatch.delenv(name, raising=False)

    def test_ohne_backend_wird_nichts_erfunden(self, monkeypatch):
        """**Die tragende Zusage.** Ohne Ansage kein Mock — lieber gar keine Antwort."""

        from src.llm import get_llm

        self._ohne_backend(monkeypatch)

        with pytest.raises(RuntimeError, match="Kein Sprachmodell konfiguriert"):
            get_llm()

    def test_die_meldung_nennt_jeden_weg_hinaus(self, monkeypatch):
        """Eine Abweisung ohne Ausweg ist eine Sackgasse."""

        from src.llm import get_llm
        from src.llm.studio_helpers import MOCK_ENV

        self._ohne_backend(monkeypatch)

        with pytest.raises(RuntimeError) as fehler:
            get_llm()

        text = str(fehler.value)
        for weg in ("OLLAMA_MODEL", "LLAMA_HTTP_URL", "LLAMA_TRANSFORMERS_MODEL", MOCK_ENV):
            assert weg in text, f"Die Meldung nennt {weg} nicht"

    def test_auf_ansage_kommt_er(self, monkeypatch):
        from src.llm import MockLLM, get_llm

        self._ohne_backend(monkeypatch)

        assert isinstance(get_llm(mock=True), MockLLM)

    def test_auch_ueber_die_umgebung(self, monkeypatch):
        """Nötig, weil die beiden Aufrufer `get_llm()` **ohne Parameter** bauen.

        Ein Schalter allein im Aufruf hätte den Studio-Graphen und die
        Szenario-CLI nicht erreicht — dort gibt es keine Stelle, die ihn setzt.
        """

        from src.llm import MockLLM, get_llm
        from src.llm.studio_helpers import MOCK_ENV

        self._ohne_backend(monkeypatch)
        monkeypatch.setenv(MOCK_ENV, "1")

        assert isinstance(get_llm(), MockLLM)

    def test_jede_wahl_steht_im_log(self, monkeypatch, caplog):
        """Ein Lauf, dessen Backend man nicht feststellen kann, ist der Zustand,
        den Invariante 1 verhindern soll."""

        import logging

        from src.llm import get_llm

        self._ohne_backend(monkeypatch)
        monkeypatch.setenv("OLLAMA_MODEL", "mistral")

        with caplog.at_level(logging.INFO):
            get_llm()

        assert "mistral" in caplog.text
        assert "Ollama" in caplog.text

    def test_der_bewusste_mock_geht_weiterhin_an_dieser_auswahl_vorbei(self):
        """`--mock-llm` und «Ohne Sprachmodell» bauen `MockLLM()` direkt.

        Das ist seit P0.1 so und richtig: Der Schalter soll nicht davon abhängen,
        ob gerade `OLLAMA_MODEL` in der Umgebung steht.
        """

        import ast
        from pathlib import Path

        for pfad, funktion in (
            (ROOT / "src" / "run_simulation.py", "_main"),
            (ROOT / "dashboard" / "run_launcher.py", "_build_llm"),
        ):
            quelle = Path(pfad).read_text(encoding="utf-8")
            baum = ast.parse(quelle)
            treffer = [
                knoten
                for knoten in ast.walk(baum)
                if isinstance(knoten, ast.FunctionDef) and knoten.name == funktion
            ]
            assert treffer, f"{pfad.name} hat keine Funktion '{funktion}'"
            aufrufe = {
                knoten.func.id
                for knoten in ast.walk(treffer[0])
                if isinstance(knoten, ast.Call) and isinstance(knoten.func, ast.Name)
            }
            assert "MockLLM" in aufrufe, (
                f"{pfad.name}::{funktion} baut den bewussten Mock nicht mehr selbst — "
                "wenn er über `get_llm()` geht, hängt er wieder an der Umgebung."
            )
