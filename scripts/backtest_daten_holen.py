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
#: Fluggäste, monatlich, EU-27. `PAS_CRD` sind die **beförderten** Passagiere
#: (nicht die ein- und ausgestiegenen, die jeden Umsteiger doppelt zählen),
#: `tra_cov=TOTAL` schließt Inlands- und Auslandsverkehr ein.
FLUGGAESTE_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/avia_paoc"
    "?format=JSON&lang=EN&geo=EU27_2020&freq=M&unit=PAS&tra_meas=PAS_CRD"
    "&tra_cov=TOTAL&schedule=TOTAL"
    f"&sinceTimePeriod={VON}&untilTimePeriod={BIS}"
)

#: Reales Bruttoinlandsprodukt, EU-27, **vierteljährlich**. Verkettete Volumen
#: zu Preisen von 2015 (`CLV15_MEUR`), saison- und kalenderbereinigt (`SCA`).
#:
#: **Warum real und nicht nominal**, obwohl nominal das Ergebnis schmeichelhafter
#: machte: Brons et al. (2002) — die Metaanalyse, an der die Elastizitäten dieses
#: Modells gemessen werden — verwenden GDP ausdrücklich preisbereinigt
#: («corrected for price level»). Nominal wüchse die Reihe bis 2019 um 14,8 %
#: statt 9,0 % und drehte die Nachfragerichtung des Backtests ins Positive. Genau
#: das wäre «auf den Backtest hin gebaut»: Die Wahl fiele dann nach dem Ergebnis
#: statt nach der Fachlage.
#:
#: **Vierteljährlich ist die feinste verfügbare Auflösung.** Volkswirtschaftliche
#: Gesamtrechnungen gibt es nicht monatlich. Die Umrechnung interpoliert linear
#: zwischen den Quartalsmitten und sagt das (siehe `bip_real`).
BIP_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp"
    "?format=JSON&lang=EN&geo=EU27_2020&na_item=B1GQ&unit=CLV15_MEUR&s_adj=SCA"
    "&freq=Q&sinceTimePeriod=2015-Q1&untilTimePeriod=2024-Q4"
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


def _eurostat_reihe(url: str) -> dict[str, float]:
    daten = json.loads(_laden(url).decode("utf-8"))
    stellen = daten["dimension"]["time"]["category"]["index"]
    werte = daten["value"]
    umgekehrt = {v: k for k, v in stellen.items()}
    return {
        umgekehrt[i]: float(werte[str(i)])
        for i in sorted(umgekehrt)
        if werte.get(str(i)) is not None
    }


def hicp_flugreisen() -> dict[str, float]:
    return _eurostat_reihe(HICP_URL)


def fluggaeste() -> dict[str, float]:
    return _eurostat_reihe(FLUGGAESTE_URL)


def bip_real() -> dict[str, float]:
    """Quartalswerte auf Monate bringen — linear zwischen den Quartalsmitten.

    **Die Interpolation erfindet keine Konjunktur**, sie verteilt eine bekannte
    Bewegung auf die Monate dazwischen. Das ist bei einer Größe, die ohnehin
    saisonbereinigt vorliegt, die ehrlichere Variante als ein Treppenverlauf:
    Eine Stufe zum Quartalsanfang schriebe dem Modell einen Sprung vor, den es in
    den Faktorregeln als Ereignis läse.

    Die Quartalsmitte ist der **zweite** Monat (Februar, Mai, August, November).
    Vor der ersten und nach der letzten Mitte wird der Randwert gehalten — dort
    gibt es nichts zu interpolieren, und Extrapolation wäre eine Behauptung.
    """

    quartale = _eurostat_reihe(BIP_URL)
    if not quartale:
        raise SystemExit("Eurostat lieferte keine BIP-Quartale")

    # Quartalsmitte als laufender Monatsindex: 2015-Q1 -> 2015-02 -> 1
    stuetzen: list[tuple[int, float]] = []
    for quartal, wert in sorted(quartale.items()):
        jahr, nummer = quartal.split("-Q")
        monat_im_jahr = (int(nummer) - 1) * 3 + 2
        stuetzen.append(((int(jahr) - 2015) * 12 + monat_im_jahr, wert))

    reihe: dict[str, float] = {}
    for laufend in range(1, 121):
        jahr, monat = divmod(laufend - 1, 12)
        name = f"{2015 + jahr}-{monat + 1:02d}"

        if laufend <= stuetzen[0][0]:
            reihe[name] = stuetzen[0][1]
        elif laufend >= stuetzen[-1][0]:
            reihe[name] = stuetzen[-1][1]
        else:
            links = max(s for s in stuetzen if s[0] <= laufend)
            rechts = min(s for s in stuetzen if s[0] >= laufend)
            if links[0] == rechts[0]:
                reihe[name] = links[1]
            else:
                anteil = (laufend - links[0]) / (rechts[0] - links[0])
                reihe[name] = links[1] + anteil * (rechts[1] - links[1])

    return {m: round(w, 1) for m, w in reihe.items()}


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
            "EU-27, Index 2015 = 100. **Zielreihe der Preisseite.**",
            hicp_flugreisen,
        ),
        (
            "bip_real",
            "mio_eur_kettenindex",
            BIP_URL,
            "Eurostat `namq_10_gdp`, reales BIP der EU-27 (`B1GQ`, verkettete Volumen "
            "zu Preisen von 2015, saison- und kalenderbereinigt), **vierteljährlich** "
            "und linear auf Monate interpoliert. Speist `income_index`. Real und nicht "
            "nominal, weil Brons et al. (2002) GDP preisbereinigt verwenden — nominal "
            "wüchse die Reihe fast doppelt so stark und schmeichelte dem Ergebnis.",
            bip_real,
        ),
        (
            "fluggaeste",
            "personen",
            FLUGGAESTE_URL,
            "Eurostat `avia_paoc`, beförderte Fluggäste (`PAS_CRD`), EU-27, monatlich, "
            "Inlands- und Auslandsverkehr. **Zielreihe der Nachfrageseite.** Der Wert "
            "für April 2020 — 0,89 statt rund 90 Millionen — ist echt und der Grund, "
            "warum 2020/21 nicht bewertet werden.",
            fluggaeste,
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
