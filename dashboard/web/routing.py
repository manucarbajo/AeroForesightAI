"""Wo im Adressraum was liegt.

Die Landingpage ist der Einstieg und liegt auf `/`. Das Dashboard liegt
darunter auf `/app/`. Beides kommt aus demselben Server — ein Start, eine
Adresse, kein zweiter Dienst daneben.

Alle Pfade laufen über dieses Modul, damit das Präfix an einer einzigen Stelle
steht. Bewusst ohne Dash-Import, damit es von überall benutzbar ist.
"""

from __future__ import annotations

#: Unterhalb dieses Pfads bedient Dash die Anwendung. Mit Schrägstrich am
#: Ende, weil Dash das für `url_base_pathname` so verlangt.
BASE_PATH = "/app/"

#: Die Landingpage.
LANDING_PATH = "/"


def url(path: str = "") -> str:
    """Interner Pfad zu einer Adresse — `runs` wird zu `/app/runs`."""

    return BASE_PATH + path.lstrip("/")


def relative(pathname: str | None) -> str:
    """Adresse zu internem Pfad — `/app/doku/cib` wird zu `doku/cib`.

    Kommt auch mit `/app` ohne abschließenden Schrägstrich zurecht: Diese
    Adresse landet über einen Umleitungsschritt von Flask ohnehin bei `/app/`,
    aber `dcc.Location` meldet sie zwischendurch so, wie sie eingetippt wurde.
    """

    path = (pathname or "").strip()
    trimmed = BASE_PATH.rstrip("/")
    if path == trimmed or path.startswith(BASE_PATH):
        path = path[len(trimmed) :]
    return path.strip("/")
