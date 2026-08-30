"""Die Schriften einmal holen, damit kein Seitenaufruf sie holen muss (P1.4).

Bis zum 2026-08-30 lud jede Seite — Landingpage wie Dashboard — drei Schriften
von `fonts.googleapis.com`. Jeder Aufruf meldete damit die IP des Betrachters an
einen fremden Host; das widerspricht dem Deployment-Ziel Datenhoheit, und in
Deutschland kommt die Rechtslage dazu.

**Dieses Skript läuft einmal, nicht zur Laufzeit.** Es holt die Schriftdateien,
legt sie unter `dashboard/web/assets/fonts/` ab und schreibt die passenden
`@font-face`-Regeln nach `dashboard/web/assets/01-schriften.css`. Beides ist
versioniert: Ein frischer Checkout soll richtig aussehen, ohne dass jemand ein
Skript ausführt oder Netz hat.

    python scripts/schriften_holen.py

**Material Symbols wird ein Teilsatz.** Die vollständige variable Schrift wiegt
Megabyte; das Projekt benutzt gut vierzig Symbole. Google Fonts liefert über
`icon_names=` genau den passenden Ausschnitt.

**Und deshalb braucht der Teilsatz einen Wächter.** Ein Symbolname, der nicht
im Ausschnitt steckt, erscheint als sein eigener Text — «chevron_right» in
Buchstaben statt als Pfeil. Kein Fehler, keine Meldung, nur ein Wort, wo ein
Zeichen sein sollte. `tests/test_symbolschrift.py` hält jeden im Quelltext
benutzten Namen gegen die Liste unten.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
ASSETS = WURZEL / "dashboard" / "web" / "assets"
SCHRIFTEN = ASSETS / "fonts"
CSS = ASSETS / "01-schriften.css"

#: Ein Browser-Kennzeichen ist nötig: Google Fonts liefert je nach Absender
#: `woff2`, `woff` oder `ttf`. Ohne dieses bekommt man die grösste Variante.
KOPFZEILEN = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

#: Die Textschriften, so wie die Seiten sie bisher angefordert haben.
TEXTSCHRIFTEN = "family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600"

#: **Jedes Symbol, das irgendwo benutzt wird** — im Dashboard und auf der
#: Landingpage. Wer eines hinzufügt, trägt es hier ein und lässt das Skript
#: erneut laufen; sonst erscheint es als Wort. Der Test sagt es ihm.
SYMBOLE = sorted(
    {
        # Dashboard
        "add",
        "animation",
        "arrow_forward",
        "auto_awesome",
        "autorenew",
        "check_circle",
        "chevron_left",
        "chevron_right",
        "dark_mode",
        "delete",
        "download",
        "error",
        "fast_forward",
        "first_page",
        "forum",
        "image",
        "last_page",
        "light_mode",
        "pause",
        "photo_camera",
        "play_arrow",
        "refresh",
        "restart_alt",
        "save",
        "scatter_plot",
        "schedule",
        "science",
        "send",
        "stop",
        "stop_circle",
        "visibility",
        "insights",
        "zoom_in",
        "zoom_out",
        # **Die Zustände der Schrittliste.** Sie stehen in `_ZUSTAENDE`
        # (wizard.py) und nicht im Aufruf — der AST-Wächter sah sie
        # deshalb nicht, und die Schrittliste brach um 308 px aus, weil
        # «radio_button_unchecked» als Wort gesetzt wurde.
        "check",
        "remove",
        "radio_button_checked",
        "radio_button_unchecked",
        # Landingpage
        "analytics",
        "expand_more",
        "mail",
        "menu",
        "shield",
        "verified_user",
        "warning",
        # Wird von `ui.note` als Vorgabe gesetzt und taucht deshalb nicht in
        # jedem Aufruf auf.
        "lightbulb",
        "info",
        "tune",
        "compare_arrows",
        "history",
        "close",
        "search",
        "settings",
        "help",
    }
)


def _hole(url: str) -> bytes:
    anfrage = urllib.request.Request(url, headers=KOPFZEILEN)
    with urllib.request.urlopen(anfrage, timeout=30) as antwort:  # noqa: S310
        return antwort.read()


def _lokalisieren(css: str, praefix: str) -> str:
    """Jede entfernte Schriftadresse durch die lokale Datei ersetzen."""

    SCHRIFTEN.mkdir(parents=True, exist_ok=True)
    zaehler = 0

    def ersetze(treffer: re.Match) -> str:
        nonlocal zaehler
        url = treffer.group(1)
        endung = ".woff2" if ".woff2" in url else Path(url).suffix or ".woff2"
        name = f"{praefix}-{zaehler}{endung}"
        zaehler += 1
        (SCHRIFTEN / name).write_bytes(_hole(url))
        return f"url(fonts/{name})"

    return re.sub(r"url\((https://[^)]+)\)", ersetze, css)


def main() -> int:
    kopf = (
        "/* **Erzeugt von `scripts/schriften_holen.py` — nicht von Hand ändern**\n"
        "   (P1.4). Die Schriften liegen unter `assets/fonts/` und werden von\n"
        "   hier eingebunden; kein Seitenaufruf fragt mehr bei Google nach.\n\n"
        "   Die Ziffer im Dateinamen sortiert: Dash lädt seine Assets\n"
        "   alphabetisch, und diese Regeln gehören vor `dashboard.css`. */\n\n"
    )

    teile = [kopf]

    text_css = _hole(f"https://fonts.googleapis.com/css2?{TEXTSCHRIFTEN}&display=swap").decode(
        "utf-8"
    )
    teile.append(_lokalisieren(text_css, "text"))

    symbol_css = _hole(
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"
        "&icon_names=" + ",".join(SYMBOLE) + "&display=block"
    ).decode("utf-8")
    teile.append("\n\n/* Material Symbols — Teilsatz aus `SYMBOLE`. */\n")
    teile.append(_lokalisieren(symbol_css, "symbole"))

    CSS.write_text("\n".join(teile), encoding="utf-8")

    gewicht = sum(p.stat().st_size for p in SCHRIFTEN.glob("*")) / 1024
    print(f"{len(list(SCHRIFTEN.glob('*')))} Dateien, {gewicht:.0f} KiB -> {CSS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
