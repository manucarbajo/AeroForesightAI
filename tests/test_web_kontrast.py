"""Kontrast von Texten, die das Stylesheet einfärbt — gerechnet, nicht geschätzt.

**Anlass (P7.9-U9.1, vorgezogen am 2026-09-11):** Das Wort «optional» in der
Schrittliste stand in 11 px auf `--text-faint`. Gemessen im laufenden Browser,
dunkles Design: **3,77** auf dem Grund, **2,87** auf der markierten Zeile.
WCAG 2.2 AA verlangt für diese Größe 4,5.

**Gerechnet wird aus den Tokens**, nicht am Bildschirm: Welche Farbe eine Regel
benutzt, steht in `assets/dashboard.css`; welchen Wert der Token hat, in
`theme.PALETTE` — und `tests/test_web_theme.py` hält beide deckungsgleich. So
läuft die Prüfung in jeder CI und nicht nur im opt-in-Browser-Wächter.

**Die Liste der Einzelfälle ist klein** und hält die Stellen, die schon einmal
zu blass waren. Jeder Fall nennt den Grund, auf dem der Text tatsächlich steht.

--------------------------------------------------------------------------

**Seit dem 2026-09-12 steht darunter der Wächter über die ganze Palette
(P7.0-U0.4), und er hat den Befund vom Symptom zur Ursache gedreht.**

Das Audit meldete «optional» und drei Symbole. Eine Messung im Browser über
**jeden** sichtbaren Textknoten aller fünf Bereiche in beiden Designs fand 19
verschiedene Kombinationen unter dem Grenzwert — und **alle 19 waren derselbe
Token**: `--text-faint`, hell `#94a3b8`, dunkel `#54708c`. Er trägt die
Chevrons, die Hinweiszeile einer Kennzahl, die Tick-Marken der Zeitleiste und
der Konsole, die Abschnittsmarken des Handbuchs. Gerechnet aus der Palette:

| Token | hell, schlechtester Grund | dunkel | verlangt |
| --- | ---: | ---: | ---: |
| `--text` | 16,16 | 13,51 | 4,5 |
| `--text-body` | 9,38 | 12,43 | 4,5 |
| `--text-muted` | **4,31** | 5,36 | 4,5 |
| `--text-faint` | **2,32** | **2,80** | 4,5 |

**Warum hier eine Sperrklinke steht und nicht die Zusage.** Die Lücke zu 4,5 zu
schließen heißt, den Wert des Tokens zu ändern — und ein `--text-faint`, das
4,5 erreicht, liegt auf `--text-muted` (4,31 bis 4,76). Dann haben zwei Token
dieselbe Aufgabe, und ob die Oberfläche drei Textstufen braucht oder zwei, ist
eine Frage des Gestaltungssystems (D1, P7.1-U1.1) und keine, die ein Wächter
entscheidet. Gehalten wird deshalb der **Ist-Stand**: Kein Token darf blasser
werden, und wer einen aufhellt, trägt den Gewinn ein. Dasselbe Muster wie beim
Höhenwächter aus P1.9-W0.1 — die Zahl steht als Ist-Stand da, nicht als
Freigabe.

**Was dieser Wächter nicht kann:** Er rechnet Token gegen Token, also die
Kombinationen, die das Stylesheet *erlauben* würde. Ob ein Knoten wirklich in
dieser Kombination dasteht und in welcher Schriftgröße, weiß nur der Browser.
Die Messung dort ist am 2026-09-12 einmal gelaufen und hat **keine** Ursache
außerhalb der Palette gefunden — was auch dazu passt, dass Regel 4 rohe
Farbwerte verbietet und `tests/test_web_theme.py` das durchsetzt. Ein
dauerhafter Durchlauf über alle Knoten bleibt U0.4s zweite Hälfte.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from dashboard.web import theme

CSS = Path(__file__).resolve().parents[1] / "dashboard" / "web" / "assets" / "dashboard.css"

#: WCAG 2.2 AA für normalen Text. «Groß» (ab 18,66 px oder 14 px fett) bekäme
#: 3,0 — keiner der Fälle hier ist groß.
MINDESTENS = 4.5

#: Selektor der Regel, die die Textfarbe setzt — und der Grund darunter.
FAELLE = [
    pytest.param(".af-step__tag", "canvas", id="optional-auf-dem-grund"),
    pytest.param(".af-step__tag", "surface-hover", id="optional-beim-zeigen"),
    pytest.param(
        ".af-step--current .af-step__tag", "accent-soft", id="optional-auf-der-markierten-zeile"
    ),
]


def _farbtoken(selektor: str) -> str:
    """Welchen Token die Regel für *selektor* als `color` setzt.

    Gesucht wird die **letzte** Regel mit genau diesem Selektor, außerhalb von
    `@media` — dieselbe Reihenfolge, in der der Browser sie anwendet.
    """

    text = CSS.read_text(encoding="utf-8")
    muster = re.compile(r"(?:^|\})\s*" + re.escape(selektor) + r"\s*\{([^}]*)\}", re.MULTILINE)
    token = None
    for regel in muster.finditer(text):
        farbe = re.search(r"(?:^|;)\s*color\s*:\s*var\(--([\w-]+)\)", regel.group(1))
        if farbe:
            token = farbe.group(1)
    assert token, f"Keine Regel `{selektor} {{ color: var(--…) }}` im Stylesheet."
    return token


def _leuchtdichte(hexwert: str) -> float:
    wert = hexwert.lstrip("#")
    kanaele = [int(wert[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [k / 12.92 if k <= 0.03928 else ((k + 0.055) / 1.055) ** 2.4 for k in kanaele]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def kontrast(vorne: str, hinten: str) -> float:
    hell, dunkel = sorted((_leuchtdichte(vorne), _leuchtdichte(hinten)), reverse=True)
    return (hell + 0.05) / (dunkel + 0.05)


@pytest.mark.parametrize("modus", [theme.LIGHT, theme.DARK])
@pytest.mark.parametrize(("selektor", "grund"), FAELLE)
def test_the_text_is_readable_on_its_ground(selektor, grund, modus):
    palette = theme.PALETTE[modus]
    token = _farbtoken(selektor)
    wert = kontrast(palette[token], palette[grund])

    assert wert >= MINDESTENS, (
        f"`{selektor}` steht in `--{token}` auf `--{grund}` ({modus}): "
        f"Kontrast {wert:.2f}, verlangt {MINDESTENS}."
    )


def test_the_contrast_formula_matches_known_values():
    """Die Formel selbst — sonst wäre jeder Fall oben aus dem falschen Grund grün."""

    assert kontrast("#000000", "#ffffff") == pytest.approx(21.0)
    assert kontrast("#777777", "#ffffff") == pytest.approx(4.48, abs=0.01)


# --- Die ganze Palette als Sperrklinke (P7.0-U0.4) ---------------------------

#: Auf welchen Gründen ein Texttoken vorkommen kann. **Nicht alle gegen alle:**
#: `--text-inverted` steht auf dem Akzent und nirgends sonst — es gegen die
#: neutralen Gründe zu rechnen ergäbe 1,00 und wäre ein Befund über eine
#: Kombination, die niemand baut. Dasselbe gilt für die Meldungsfarben:
#: `--warning-text` steht auf seinem eigenen Ton und auf den beiden Gründen, auf
#: denen eine Meldung liegen kann.
_NEUTRAL = (
    "canvas",
    "surface",
    "surface-raised",
    "surface-inset",
    "surface-hover",
    "surface-sunken",
    "paper-bg",
    "accent-soft",
)

GRUENDE: dict[str, tuple[str, ...]] = {
    "text": _NEUTRAL,
    "text-body": _NEUTRAL,
    "text-muted": _NEUTRAL,
    "text-faint": _NEUTRAL,
    "text-inverted": ("accent", "accent-hover"),
    **{
        f"{rolle}-text": (f"{rolle}-soft", "canvas", "surface")
        for rolle in ("accent", "positive", "negative", "warning", "demo")
    },
    **{
        token: ("console-bg",)
        for token in ("console-text", "console-info", "console-warning", "console-error")
    },
}

#: Der schlechteste Kontrast, den ein Token heute auf einem seiner Gründe
#: erreicht — gemessen am 2026-09-12. **Sperrklinke in beide Richtungen:**
#: Wird ein Wert kleiner, ist etwas blasser geworden. Wird er um mehr als
#: :data:`GEWINN_MELDEN` größer, steht der Eintrag zu hoch und die Klinke
#: schwebt über dem Ist-Stand — dann gehört der Gewinn eingetragen, sonst
#: verfällt er still.
SPERRKLINKE = {
    theme.LIGHT: {
        "accent-text": 11.42,  # auf --accent-soft
        "console-error": 5.95,  # auf --console-bg
        "console-info": 7.70,  # auf --console-bg
        "console-text": 13.14,  # auf --console-bg
        "console-warning": 9.59,  # auf --console-bg
        "demo-text": 8.19,  # auf --demo-soft
        "negative-text": 7.30,  # auf --negative-soft
        "positive-text": 7.25,  # auf --canvas
        "text": 16.16,  # auf --accent-soft
        "text-body": 9.38,  # auf --accent-soft
        "text-faint": 2.32,  # auf --accent-soft
        "text-inverted": 9.07,  # auf --accent-hover
        "text-muted": 4.31,  # auf --accent-soft
        "warning-text": 6.78,  # auf --canvas
    },
    theme.DARK: {
        "accent-text": 12.13,  # auf --accent-soft
        "console-error": 7.23,  # auf --console-bg
        "console-info": 9.35,  # auf --console-bg
        "console-text": 14.43,  # auf --console-bg
        "console-warning": 11.65,  # auf --console-bg
        "demo-text": 9.15,  # auf --demo-soft
        "negative-text": 8.93,  # auf --negative-soft
        "positive-text": 11.06,  # auf --positive-soft
        "text": 13.51,  # auf --surface-hover
        "text-body": 12.43,  # auf --surface-hover
        "text-faint": 2.80,  # auf --surface-hover
        "text-inverted": 9.35,  # auf --accent
        "text-muted": 5.36,  # auf --surface-hover
        "warning-text": 10.93,  # auf --warning-soft
    },
}

#: Ab welchem Gewinn der Eintrag nachzuziehen ist. 0,1 ist knapp über dem
#: Rundungsrauschen der eingetragenen zwei Stellen.
GEWINN_MELDEN = 0.1

#: Wohin es soll.
ZIEL = MINDESTENS

#: Welche Token heute unter :data:`ZIEL` liegen, als `«Design»/«Token»`.
#:
#: **Drei von zehn Paaren**, und es ist kein Zufall, welche: `--text-faint` in
#: beiden Designs und `--text-muted` im hellen, dort mit 4,31 knapp. Geschlossen
#: wird die Lücke mit P7.9-U9.1 und der Entscheidung über die Textstufen
#: (D1, P7.1-U1.1) — ein `--text-faint`, das 4,5 erreicht, liegt auf
#: `--text-muted`, und dann ist die Frage, ob es drei Stufen braucht oder zwei.
UNTER_AA = {
    f"{theme.LIGHT}/text-muted",
    f"{theme.LIGHT}/text-faint",
    f"{theme.DARK}/text-faint",
}


def _schlechtester(modus: str, token: str) -> tuple[float, str]:
    palette = theme.PALETTE[modus]
    werte = [(kontrast(palette[token], palette[grund]), grund) for grund in GRUENDE[token]]
    return min(werte)


class TestDiePaletteWirdNichtBlasser:
    """Die Sperrklinke über alle Textfarben — Herleitung im Modul-Docstring."""

    @pytest.mark.parametrize("modus", [theme.LIGHT, theme.DARK])
    @pytest.mark.parametrize("token", sorted(GRUENDE))
    def test_no_text_token_gets_paler(self, token, modus):
        wert, grund = _schlechtester(modus, token)
        gehalten = SPERRKLINKE[modus][token]

        assert wert >= gehalten - 0.005, (
            f"`--{token}` ist im {modus}en Design blasser geworden: {wert:.2f} auf "
            f"`--{grund}`, gehalten war {gehalten:.2f}."
        )
        assert wert <= gehalten + GEWINN_MELDEN, (
            f"`--{token}` erreicht im {modus}en Design jetzt {wert:.2f} auf `--{grund}` "
            f"statt {gehalten:.2f}. Den Gewinn eintragen — eine Sperrklinke über dem "
            "Ist-Stand ist wieder aus dem falschen Grund grün."
        )

    @pytest.mark.parametrize("modus", [theme.LIGHT, theme.DARK])
    def test_the_readable_tokens_reach_wcag_aa(self, modus):
        """Jeder Token außer den benannten Ausnahmen hält 4,5 auf jedem Grund.

        **Diese Zusage ist die eigentliche**, und sie deckt heute elf der
        vierzehn Token je Design ab — darunter alle Meldungsfarben auf ihrem
        eigenen Ton, die Konsole auf ihrem Grund und den Text auf dem Akzent.
        Unter 4,5 liegen nur `--text-faint` (beide Designs) und `--text-muted`
        im hellen, dort mit 4,31 knapp; sie stehen in :data:`UNTER_AA` mit ihrem
        Paket.

        **Abgeleitet, nicht aufgezählt:** Ein neuer Token, den jemand einführt,
        fällt hier auf, ohne dass ihn jemand einträgt.
        """

        befunde = [
            f"--{token}: {_schlechtester(modus, token)[0]:.2f} auf "
            f"`--{_schlechtester(modus, token)[1]}`"
            for token in GRUENDE
            if f"{modus}/{token}" not in UNTER_AA
            if _schlechtester(modus, token)[0] < ZIEL
        ]

        assert not befunde, (
            f"Diese Token tragen lesbaren Text und halten {ZIEL} nicht ({modus}):\n  "
            + "\n  ".join(befunde)
        )

    def test_exactly_these_tokens_are_still_below_wcag(self):
        """**Was noch fehlt, steht als Liste da statt als Absicht.**

        Gehalten wird nicht «diese beiden sind zu blass», sondern die **Menge**
        derer, die es sind. Sie schlägt in beide Richtungen an: Kommt ein Token
        dazu, ist etwas kaputtgegangen; fällt eines heraus, ist der Abstand
        geschlossen — dann gehört die Liste nachgezogen, statt dass der Gewinn
        still verfällt.

        Abgeleitet wird die Menge aus der Palette und nicht aufgezählt; die
        Erwartung ist die Aufzählung. So fällt auch ein **neues** Texttoken auf,
        das jemand einführt, ohne an den Kontrast zu denken.
        """

        zu_blass = {
            f"{modus}/{token}"
            for modus in (theme.LIGHT, theme.DARK)
            for token in GRUENDE
            if _schlechtester(modus, token)[0] < ZIEL
        }

        assert zu_blass == UNTER_AA, (
            f"Unter {ZIEL} liegen jetzt: {sorted(zu_blass)}\n"
            f"eingetragen sind:          {sorted(UNTER_AA)}\n"
            "Dazugekommen heißt kaputt; weggefallen heißt behoben — dann diese Liste "
            "nachziehen und den Token in `test_the_readable_tokens_reach_wcag_aa` "
            "aufnehmen."
        )
