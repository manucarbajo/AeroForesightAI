"""Eine Demo-Anfrage kommt an — und wer eine schickt, erfährt es (P1.4).

`demo-anfragen.html` trug `action="#"`. Jede Anfrage wurde verworfen, und der
Absender merkte nichts davon: kein Fehler, keine Meldung, nur ein Formular, das
so tut, als hätte es etwas getan. Von allen Zuständen ist das der schlechteste.

**Was hier geprüft wird, ist beides:** dass die Anfrage in der Ablage landet,
und dass der Absender in *beiden* Fällen sieht, was passiert ist.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from flask import Flask

from dashboard.web import landing_route

VOLLSTAENDIG = {
    "firstName": "Alex",
    "lastName": "Berger",
    "email": "alex.berger@example.org",
    "phone": "+49 30 123456",
    "company": "Beispiel Airlines",
    "position": "Leitung Strategie",
    "role": "airline",
    "message": "Wie wirkt eine CO₂-Abgabe von 200 EUR/t auf die Kurzstrecke?",
    "privacy": "on",
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Ein Server mit einer Ablage, die nur diesem Test gehört."""

    ziel = tmp_path / "anfragen.jsonl"
    monkeypatch.setattr(landing_route, "ANFRAGEN_DATEI", ziel)

    server = Flask(__name__)
    landing_route.register(server)
    server.config.update(TESTING=True)
    testklient = server.test_client()
    testklient.ablage = ziel
    return testklient


def _zeilen(pfad: Path) -> list[dict]:
    if not pfad.is_file():
        return []
    return [json.loads(z) for z in pfad.read_text(encoding="utf-8").splitlines() if z.strip()]


class TestEineVollstaendigeAnfrageKommtAn:
    def test_it_lands_in_the_file(self, client):
        antwort = client.post("/demo-anfrage", data=VOLLSTAENDIG)

        assert antwort.status_code == 200
        zeilen = _zeilen(client.ablage)
        assert len(zeilen) == 1
        assert zeilen[0]["email"] == "alex.berger@example.org"
        assert zeilen[0]["message"].startswith("Wie wirkt")
        assert zeilen[0]["eingegangen"], "Ohne Zeitstempel weiß niemand, wann sie kam"

    def test_the_sender_sees_that_it_arrived(self, client):
        text = client.post("/demo-anfrage", data=VOLLSTAENDIG).get_data(as_text=True)

        assert "Danke" in text
        # **Und keine Zusage, die wir nicht halten.** Eine Bestätigungsmail
        # bräuchte einen Maildienst; wir sagen, dass wir keine schicken.
        assert "Bestätigungsmail" in text

    def test_two_requests_do_not_overwrite_each_other(self, client):
        client.post("/demo-anfrage", data=VOLLSTAENDIG)
        client.post("/demo-anfrage", data={**VOLLSTAENDIG, "email": "zweite@example.org"})

        adressen = [z["email"] for z in _zeilen(client.ablage)]
        assert adressen == ["alex.berger@example.org", "zweite@example.org"]

    def test_only_the_known_fields_are_stored(self, client):
        """Ein Feld, das niemand erwartet, landet nicht in der Ablage."""

        client.post("/demo-anfrage", data={**VOLLSTAENDIG, "geheim": "sollte nicht ankommen"})

        gespeichert = _zeilen(client.ablage)[0]
        assert "geheim" not in gespeichert
        assert set(gespeichert) == {"eingegangen", *landing_route.FELDER}


class TestEineUnvollstaendigeAnfrageWirdNichtVerschluckt:
    """**Der Ausgangsbefund war das stille Verwerfen.**"""

    @pytest.mark.parametrize("fehlt", landing_route.PFLICHTFELDER)
    def test_a_missing_required_field_is_reported(self, client, fehlt):
        daten = {**VOLLSTAENDIG}
        daten.pop(fehlt)

        antwort = client.post("/demo-anfrage", data=daten)
        text = antwort.get_data(as_text=True)

        assert antwort.status_code == 400
        assert _zeilen(client.ablage) == [], "Eine unvollständige Anfrage wurde abgelegt"
        assert (
            landing_route.KLARTEXT[fehlt] in text
        ), f"Der Absender erfährt nicht, dass «{fehlt}» fehlt:\n{text[:400]}"

    def test_the_required_check_is_server_side(self, client):
        """Ein `required`-Attribut ist eine Bitte an den Browser, keine Schranke.

        Wer das Formular umgeht — mit `curl`, mit abgeschaltetem JavaScript, mit
        einem eigenen Skript —, kommt daran vorbei. Deshalb steht die Prüfung
        auf dem Server.
        """

        antwort = client.post("/demo-anfrage", data={})

        assert antwort.status_code == 400
        assert _zeilen(client.ablage) == []

    def test_consent_is_not_optional(self, client):
        daten = {**VOLLSTAENDIG}
        daten.pop("privacy")

        antwort = client.post("/demo-anfrage", data=daten)

        assert antwort.status_code == 400
        assert _zeilen(client.ablage) == []
        assert "Zustimmung" in antwort.get_data(as_text=True)


class TestDasFormularZeigtAufDenEndpunkt:
    def test_the_form_no_longer_points_nowhere(self):
        """`action="#"` war der Befund."""

        seite = (landing_route.LANDING_DIR / "demo-anfragen.html").read_text(encoding="utf-8")

        assert 'action="/demo-anfrage"' in seite
        assert 'action="#"' not in seite

    def test_the_page_says_the_privacy_notice_is_a_draft(self):
        """Solange die Rechtstexte Platzhalter sind, gehört das an die Seite.

        Das Formular erhebt personenbezogene Daten und verlangt eine
        Zustimmung, die auf eine Entwurfsseite verweist. Es funktioniert — aber
        wer es benutzt, soll wissen, worauf er sich einlässt.
        """

        seite = (landing_route.LANDING_DIR / "demo-anfragen.html").read_text(encoding="utf-8")

        assert "Entwurf" in seite
        assert "Vor der Veröffentlichung" in seite
