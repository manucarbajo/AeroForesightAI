"""Der Bereich «Einrichten»: eine Frage nach der anderen, allein auf dem Schirm.

Bis P1.6 stand das in der linken Spalte — 10,7 Bildschirme in 336 px. P1.6 hat
daraus einen eigenen Bereich gemacht, aber die Form blieb eine Bildlaufstrecke:
bei 1280 px **7,3 Bildschirme**, unten hinter einer Trennlinie vier Editor-
Reiter. Reiter unterhalb des Falzes sind keine Gliederung; man findet sie nur,
wenn man ohnehin weiß, dass es sie gibt. Wer zum ersten Mal hier stand, sah eine
Wand und keinen nächsten Schritt.

Seit P1.7 ist das Einrichten eine **Schrittfolge** (`config_editor.wizard`) und
bekommt dafür den ganzen Bildschirm: Solange dieser Bereich offen ist, blendet
der Rahmen Bedienfeld, Telemetrie und Zeitleiste aus (`af-shell--focus` in
`app.py`). Einrichten ist eine überlegte, lineare Arbeit — daneben eine Szene
laufen zu lassen, die einen *anderen* Lauf zeigt, lenkt nur ab.

**Der Start liegt am Ende der Schrittfolge**, nicht mehr im Bedienfeld daneben:
Wer hier ist, richtet ein; wer gestartet hat, sieht zu. Der Knopf im Bedienfeld
bleibt trotzdem bestehen — beide lösen **denselben** Callback aus, es gibt
weiterhin genau eine Prüfung und genau ein `runner.start`.
"""

from __future__ import annotations

from dash import html

from dashboard.web.config_editor import wizard
from dashboard.web.state import initial_draft_dict


def layout(draft: dict | None = None) -> html.Div:
    """Der Einstieg — und dahinter die Schrittfolge.

    Begonnen wird seit P1.7-C **nicht** auf Schritt 1, sondern bei der Frage,
    welche Art von Lauf es werden soll. Ohne sie war «alle Szenarien
    nacheinander» eine Ankreuzoption hinter der Feinabstimmung des zweiten
    Schritts — vorhanden, aber unauffindbar —, und wer nur den vorhandenen
    Entwurf noch einmal starten wollte, blätterte dafür durch acht Fragen.
    """

    return html.Div(wizard.layout(draft or initial_draft_dict(), wizard.ENTRY))
