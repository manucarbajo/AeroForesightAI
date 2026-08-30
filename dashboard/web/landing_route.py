"""Die Landingpage aus derselben Anwendung ausliefern.

Sie ist bewusst statisches HTML geblieben und wird nicht in Dash-Komponenten
übersetzt: Es sind fünf fertige Seiten ohne lokale Dateien — Schriften und
Tailwind kommen vom CDN, alle Illustrationen sind Inline-SVG. Sie hier
einzubinden heißt deshalb nur, sie zu servieren.

Der Gewinn ist der Einstieg: `python -m dashboard.web.app` startet einen
Server, und wer die Adresse öffnet, landet auf der Landingpage und kommt von
dort ins Dashboard. Kein zweiter Dienst, keine fest verdrahtete Portnummer.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, abort, render_template_string, request, send_from_directory

LANDING_DIR = Path(__file__).resolve().parents[2] / "aeroforesight-ai-landing-page"

#: Wohin eine Demo-Anfrage geschrieben wird. Eine Zeile JSON je Anfrage —
#: anhängend, damit ein Absturz mitten im Schreiben höchstens die letzte Zeile
#: beschädigt und nicht die Ablage.
#:
#: **Kein externer Dienst, kein Mailversand** (P1.4). Das Deployment-Ziel ist
#: Datenhoheit; eine Anfrage über einen fremden Server zu leiten wäre genau der
#: Widerspruch, den dieses Paket sonst abräumt. Wer Benachrichtigungen will,
#: legt sie über diese Datei — sie bleibt die Wahrheit.
ANFRAGEN_DATEI = Path(os.environ.get("AF_DEMO_ANFRAGEN", Path("outputs") / "demo_anfragen.jsonl"))

#: Was das Formular als Pflicht kennzeichnet. **Serverseitig geprüft**, denn ein
#: `required`-Attribut ist eine Bitte an den Browser, keine Schranke.
PFLICHTFELDER = ("firstName", "lastName", "email", "company", "position", "role")

#: Alles, was aufgenommen wird. Ein Feld, das hier nicht steht, landet nicht in
#: der Ablage — auch dann nicht, wenn jemand es mitschickt.
FELDER = (*PFLICHTFELDER, "phone", "message")


def available_pages() -> set[str]:
    """Welche Seiten es gibt — Grundlage der Zugriffsprüfung."""

    if not LANDING_DIR.is_dir():
        return set()
    return {path.name for path in LANDING_DIR.glob("*.html")}


# --- Die Demo-Anfrage ------------------------------------------------------


_SEITE = """<!DOCTYPE html>
<html class="light" lang="de"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{{ titel }} | AeroForesight AI</title>
<link href="/app/assets/00-tailwind.css" rel="stylesheet"/>
<link href="/app/assets/01-schriften.css" rel="stylesheet"/>
</head>
<body class="font-body bg-slate-50 text-slate-900">
<main class="max-w-xl mx-auto px-6 py-24">
  <h1 class="font-headline text-3xl font-bold text-navy-800 mb-4">{{ titel }}</h1>
  <p class="text-slate-600 leading-relaxed mb-6">{{ text }}</p>
  {% if fehlend %}
  <ul class="list-disc pl-6 text-slate-600 mb-6">
    {% for feld in fehlend %}<li>{{ feld }}</li>{% endfor %}
  </ul>
  {% endif %}
  <a class="inline-block rounded bg-navy-800 px-5 py-3 text-white font-headline text-sm"
     href="{{ zurueck }}">{{ knopf }}</a>
</main>
</body></html>"""


#: Klartext für die Rückmeldung. Ein Feldname wie «firstName» sagt dem Absender
#: nichts.
KLARTEXT = {
    "firstName": "Vorname",
    "lastName": "Nachname",
    "email": "E-Mail-Adresse",
    "company": "Unternehmen",
    "position": "Position",
    "role": "Ihre Rolle",
    "privacy": "Zustimmung zur Datenverarbeitung",
}


def _fehlende_felder(formular) -> list[str]:
    """Was fehlt — in Klartext, nicht als Feldname."""

    fehlend = [f for f in PFLICHTFELDER if not (formular.get(f) or "").strip()]
    if not formular.get("privacy"):
        fehlend.append("privacy")
    return [KLARTEXT.get(f, f) for f in fehlend]


def anfrage_speichern(daten: dict, *, ziel: Path | None = None) -> Path:
    """Eine Anfrage anhängen und den Pfad zurückgeben.

    Als eigene Funktion, damit der Test sie ohne Flask aufrufen kann — und
    damit die Ablage einen Namen hat, den man in der Doku nennen kann.
    """

    pfad = Path(ziel or ANFRAGEN_DATEI)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with pfad.open("a", encoding="utf-8") as datei:
        datei.write(json.dumps(daten, ensure_ascii=False) + "\n")
    return pfad


def register(server: Flask) -> None:
    """Landingpage auf `/` und ihre Unterseiten anmelden."""

    @server.route("/")
    def landing_index():  # pragma: no cover - dünner Flask-Wrapper
        if "index.html" not in available_pages():
            abort(404)
        return send_from_directory(LANDING_DIR, "index.html")

    @server.route("/<page>.html")
    def landing_page(page: str):  # pragma: no cover - dünner Flask-Wrapper
        # Gegen die tatsächlich vorhandenen Dateien prüfen statt gegen ein
        # Muster: So kann kein Pfad nach außerhalb des Ordners zeigen.
        name = f"{page}.html"
        if name not in available_pages():
            abort(404)
        return send_from_directory(LANDING_DIR, name)

    @server.route("/demo-anfrage", methods=["POST"])
    def demo_anfrage():
        """Eine Demo-Anfrage entgegennehmen (P1.4).

        **Bis zum 2026-08-30 ging sie ins Leere:** Das Formular trug
        `action="#"`, jede Anfrage wurde verworfen, und der Absender merkte
        nichts davon. Das ist der schlimmste Fall — nicht ein Fehler, sondern
        ein Formular, das so tut, als hätte es etwas getan.

        Deshalb sieht der Absender hier **immer**, was passiert ist: was
        angekommen ist, oder was fehlt.
        """

        fehlend = _fehlende_felder(request.form)
        if fehlend:
            return (
                render_template_string(
                    _SEITE,
                    titel="Da fehlt noch etwas",
                    text="Ihre Anfrage wurde **nicht** abgeschickt. Diese Angaben "
                    "brauchen wir noch:",
                    fehlend=fehlend,
                    zurueck="/demo-anfragen.html",
                    knopf="Zurück zum Formular",
                ),
                400,
            )

        anfrage_speichern(
            {
                "eingegangen": datetime.now(timezone.utc).isoformat(),
                **{feld: (request.form.get(feld) or "").strip() for feld in FELDER},
            }
        )
        return render_template_string(
            _SEITE,
            titel="Danke — Ihre Anfrage ist da",
            text="Wir melden uns innerhalb von zwei Werktagen bei Ihnen. "
            "Eine Kopie Ihrer Angaben liegt bei uns; eine Bestätigungsmail "
            "verschicken wir bewusst nicht, weil dafür ein externer "
            "Maildienst nötig wäre.",
            fehlend=None,
            zurueck="/",
            knopf="Zurück zur Startseite",
        )
