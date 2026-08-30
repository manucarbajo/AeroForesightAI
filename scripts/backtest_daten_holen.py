"""Holt die historischen Reihen für den Backtest (P2.7) — einmalig, nicht zur Laufzeit.

Dasselbe Muster wie `schriften_holen.py`: Das Ergebnis wird **eingecheckt**, das
Skript dokumentiert nur, woher es kam und wie man es auffrischt. Für einen
Backtest ist das keine Bequemlichkeit, sondern Bedingung — eine später revidierte
Reihe änderte sonst rückwirkend das Ergebnis eines Laufs, der längst
veröffentlicht ist.

Drei Reihen, alle am 2026-08-30 geprüft:

* **EUA-Auktionspreis** aus dem EEX-Archiv «Emission Spot Primary Market Auction
  Report», die Primärquelle. Gefiltert auf die **gemeinsame EU-Auktion allgemeiner
  Zertifikate** — die nationalen Auktionen (DE, PL) und die separaten
  Luftverkehrszertifikate (EUAA, sechs Auktionen im Jahr) bleiben draußen.
* **Brent-Rohölpreis** über FRED (`MCOILBRENTEU`), das die EIA-Reihe spiegelt.
  Der Umweg über FRED hat einen praktischen Grund: Die EIA-Seite lädt ihre
  Tabellen per JavaScript nach, FRED liefert eine glatte CSV.
* **Verbraucherpreisindex Flugreisen** aus Eurostat (`prc_hicp_midx`, COICOP
  `CP0733`, EU-27) — die Zielreihe. Basis **2015 = 100**, also genau der Anfang
  des Fensters.

Aufruf (das Extra `backtest` muss installiert sein — siehe `pyproject.toml`):

    python scripts/backtest_daten_holen.py

**Warum die Excel-Leser optional sind:** Sie werden nur zum Auffrischen gebraucht.
Wer das Repo klont, findet die CSVs vor und braucht weder `xlrd` noch `openpyxl`.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import zipfile
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
ZIEL = REPO_ROOT / "configs" / "backtest"

#: Das Fenster des Backtests. 2020 und 2021 werden **mitgerechnet**, aber nicht
#: bewertet — das Modell kennt keine Reisebeschränkung, und der Einbruch war
#: keine Preiswirkung (Entscheidung vom 2026-08-30).
VON, BIS = "2015-01", "2024-12"

EEX_URL = (
    "https://www.eex.com/fileadmin/EEX/Downloads/Markets/Environmentals/"
    "EUA_Emission_Spot_Primary_Market_Auction_Report/Archive_Reports/"
    "emission-spot-primary-market-auction-report-2012-2025-data.zip"
)
BRENT_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MCOILBRENTEU"
HICP_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_midx"
    "?format=JSON&lang=EN&unit=I15&coicop=CP0733&geo=EU27_2020"
    f"&sinceTimePeriod={VON}&untilTimePeriod={BIS}"
)


def _laden(url: str) -> bytes:
    return urlopen(
        Request(url, headers={"User-Agent": "AeroForesightAI/backtest"}), timeout=180
    ).read()


def _monat(wert: object) -> str | None:
    """Ein Datum aus einer Excel-Zelle als ``YYYY-MM``.

    Beide Formate kommen vor: Die Dateien bis 2019 tragen Excel-Seriennummern,
    ab 2020 echte Zeitstempel.
    """

    if isinstance(wert, datetime):
        return f"{wert.year:04d}-{wert.month:02d}"
    if isinstance(wert, date):
        return f"{wert.year:04d}-{wert.month:02d}"
    try:
        seriennummer = float(wert)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if seriennummer < 1:
        return None
    # Excels Epoche ist der 1899-12-30 (der 1900er-Schaltjahrfehler ist darin
    # schon verrechnet).
    tag = date.fromordinal(date(1899, 12, 30).toordinal() + int(seriennummer))
    return f"{tag.year:04d}-{tag.month:02d}"


#: Länderkürzel der **nationalen** Auktionen im Archiv. Sie gehören nicht in den
#: Referenzpreis: Deutschland und Polen versteigern eigene Kontingente, und die
#: Zuschlagspreise weichen ab.
NATIONALE_AUKTIONEN = frozenset({"DE", "PL", "NIR"})


def einordnen(name: str) -> str:
    """Eine Auktionsbezeichnung einordnen: ``eu``, ``national`` oder ``luftverkehr``.

    **Diese Funktion ist der Grund, warum der erste Anlauf ein ganzes Jahr
    verloren hat.** Er prüfte schlicht, ob die Bezeichnung auf «EU» endet — und
    2016 heißt sie `EU (TCAP)`. Zwölf Monate fielen lautlos heraus, und das
    Ergebnis sah weiterhin plausibel aus: 107 statt 120 Monate, verteilt über
    zehn Jahre, fällt niemandem auf.

    Über das Fenster kommen vier Schreibweisen derselben Auktion vor — `EU`,
    `EU (TCAP)`, `Auction 3. Period CAP2-EU`, `Auction 4. Period CAP3 EU` —,
    dazu die nationalen und die Luftverkehrszertifikate. Eine unbekannte
    Bezeichnung **scheitert laut** (siehe Aufrufer), statt still zu verschwinden:
    Ein künftiger Jahrgang mit neuer Schreibweise soll auffallen.
    """

    gross = name.upper().strip()
    if "EUAA" in gross:
        return "luftverkehr"
    # Ein angehängter Markierer wie «(TCAP)» sagt nichts über den Markt.
    kern = gross.split("(")[0].strip()
    letztes = kern.replace("-", " ").split()[-1] if kern else ""
    if letztes in NATIONALE_AUKTIONEN:
        return "national"
    if letztes == "EU":
        return "eu"
    return "unbekannt"


def _eex_zeilen(rohdaten: bytes, name: str):
    if name.endswith(".xls"):
        import xlrd

        blatt = xlrd.open_workbook(file_contents=rohdaten).sheet_by_index(0)
        for r in range(blatt.nrows):
            yield [blatt.cell_value(r, c) for c in range(blatt.ncols)]
    else:
        import openpyxl

        mappe = openpyxl.load_workbook(io.BytesIO(rohdaten), data_only=True)
        yield from (list(z) for z in mappe[mappe.sheetnames[0]].iter_rows(values_only=True))


def eua_monatsmittel() -> dict[str, float]:
    """Monatsmittel der EU-Auktions-Zuschlagspreise, in EUR je Tonne CO₂."""

    archiv = zipfile.ZipFile(io.BytesIO(_laden(EEX_URL)))
    je_monat: dict[str, list[float]] = defaultdict(list)

    for jahr in range(int(VON[:4]), int(BIS[:4]) + 1):
        treffer = [n for n in archiv.namelist() if f"-{jahr}-data." in n]
        if not treffer:
            raise SystemExit(f"EEX-Archiv enthält kein Jahr {jahr}")
        zeilen = list(_eex_zeilen(archiv.read(treffer[0]), treffer[0]))

        # **Die Kopfzeile wandert zwischen den Jahrgängen** (2015: Zeile 3,
        # ab 2020: Zeile 6), und ab 2020 kommt eine Spalte «Status» dazu. Sie
        # wird deshalb gesucht statt gezählt.
        kopf = next(
            (i for i, z in enumerate(zeilen) if any(str(c).strip() == "Date" for c in z if c)),
            None,
        )
        if kopf is None:
            raise SystemExit(f"Keine Kopfzeile im EEX-Blatt für {jahr}")
        spalte = {str(c).strip(): j for j, c in enumerate(zeilen[kopf]) if c}
        preis_spalte = next(
            (j for name, j in spalte.items() if name.startswith("Auction Price")), None
        )
        if preis_spalte is None or "Date" not in spalte or "Auction Name" not in spalte:
            raise SystemExit(f"Unerwartete Spalten im EEX-Blatt für {jahr}: {list(spalte)}")

        for zeile in zeilen[kopf + 1 :]:
            if len(zeile) <= max(preis_spalte, spalte["Auction Name"]):
                continue
            auktion = zeile[spalte["Auction Name"]]
            if not auktion:
                continue
            art = einordnen(str(auktion))
            if art == "unbekannt":
                raise SystemExit(
                    f"Unbekannte Auktionsbezeichnung im Jahrgang {jahr}: {auktion!r}. "
                    "Sie stillschweigend zu überspringen hat schon einmal ein ganzes "
                    "Jahr gekostet — bitte in `einordnen` aufnehmen."
                )
            if art != "eu":
                continue
            monat = _monat(zeile[spalte["Date"]])
            try:
                preis = float(zeile[preis_spalte])
            except (TypeError, ValueError):
                continue
            if monat and VON <= monat <= BIS:
                je_monat[monat].append(preis)

    return {m: round(sum(w) / len(w), 4) for m, w in sorted(je_monat.items())}


def brent_monatsmittel() -> dict[str, float]:
    text = _laden(BRENT_URL).decode("utf-8")
    reihe: dict[str, float] = {}
    for zeile in csv.DictReader(io.StringIO(text)):
        tag = zeile["observation_date"]
        monat = tag[:7]
        wert = zeile.get("MCOILBRENTEU", "")
        if VON <= monat <= BIS and wert not in ("", "."):
            reihe[monat] = float(wert)
    return dict(sorted(reihe.items()))


def hicp_flugreisen() -> dict[str, float]:
    daten = json.loads(_laden(HICP_URL).decode("utf-8"))
    stellen = daten["dimension"]["time"]["category"]["index"]
    werte = daten["value"]
    umgekehrt = {v: k for k, v in stellen.items()}
    return {
        umgekehrt[i]: float(werte[str(i)])
        for i in sorted(umgekehrt)
        if werte.get(str(i)) is not None
    }


def _schreiben(name: str, spalte: str, reihe: dict[str, float]) -> dict[str, object]:
    ZIEL.mkdir(parents=True, exist_ok=True)
    pfad = ZIEL / f"{name}.csv"
    zeilen = ["monat," + spalte] + [f"{m},{w}" for m, w in reihe.items()]
    inhalt = "\n".join(zeilen) + "\n"
    pfad.write_text(inhalt, encoding="utf-8", newline="")
    return {
        "datei": pfad.name,
        "zeilen": len(reihe),
        "von": min(reihe) if reihe else None,
        "bis": max(reihe) if reihe else None,
        "sha256": hashlib.sha256(inhalt.encode("utf-8")).hexdigest()[:16],
    }


def main() -> int:
    abgerufen = datetime.now(timezone.utc).date().isoformat()
    quellen: list[dict[str, object]] = []

    for name, spalte, url, hinweis, holen in (
        (
            "eua_auktionspreis",
            "eur_je_tonne",
            EEX_URL,
            "EEX, Emission Spot Primary Market Auction Report. Monatsmittel der "
            "Zuschlagspreise der gemeinsamen EU-Auktion allgemeiner Zertifikate; "
            "nationale Auktionen (DE, PL) und Luftverkehrszertifikate (EUAA) sind "
            "ausgeschlossen.",
            eua_monatsmittel,
        ),
        (
            "brent_rohoel",
            "usd_je_barrel",
            BRENT_URL,
            "Europe Brent Spot Price FOB, Monatsmittel. Erhoben von der US Energy "
            "Information Administration, hier über die FRED-Spiegelung "
            "(`MCOILBRENTEU`) bezogen, weil die EIA-Seite ihre Tabellen per "
            "JavaScript nachlädt.",
            brent_monatsmittel,
        ),
        (
            "hicp_flugreisen",
            "index_2015_100",
            HICP_URL,
            "Eurostat `prc_hicp_midx`, COICOP `CP0733` (Passenger transport by air), "
            "EU-27, Index 2015 = 100. **Die Zielreihe des Backtests.**",
            hicp_flugreisen,
        ),
    ):
        print(f"  {name} …", end=" ", flush=True)
        reihe = holen()
        eintrag = _schreiben(name, spalte, reihe)
        eintrag |= {"url": url, "abgerufen": abgerufen, "hinweis": hinweis, "spalte": spalte}
        quellen.append(eintrag)
        print(f"{eintrag['zeilen']} Monate ({eintrag['von']} bis {eintrag['bis']})")

    (ZIEL / "quellen.json").write_text(
        json.dumps(
            {
                "fenster": {"von": VON, "bis": BIS},
                "unbewertet": ["2020", "2021"],
                "unbewertet_grund": (
                    "Der Einbruch 2020 war keine Preiswirkung, sondern Folge von "
                    "Reisebeschränkungen. Das Modell hat dafür keinen Mechanismus. Die "
                    "Jahre werden mitgerechnet und gezeigt, aber nicht bewertet — sonst "
                    "bestätigte der Backtest eine Eingabe statt einer Rechnung."
                ),
                "reihen": quellen,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"\nGeschrieben nach {ZIEL.relative_to(REPO_ROOT)}/ samt quellen.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
