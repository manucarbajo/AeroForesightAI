"""Rebuild cib_frozen.json with domain-correct values.

Based on: Weimer-Jehle (2023), lecture slides (Folie 19-22)

F7 wurde am 2026-08-26 von "Marktstruktur" auf "Geopolitische Stabilitaet"
gezogen (P0.2). Die 48 F7-Zellen sind dabei einzeln unter der neuen Lesart
geprueft worden: 19 geaendert, 29 unveraendert bestaetigt. Ihre Begruendungen
stehen in F7_REASONING und landen als `reasoning` in der JSON — fuer die
uebrigen 120 Zellen holt das [P2.3] nach.

Factors:
  F1: Mobilitaetsnachfrage  F1.1=Reiseboom       F1.2=Stagnation/Verzicht
  F2: Regulierung           F2.1=Moderat         F2.2=Net-Zero/Radikal
  F3: Technologie (SAF)     F3.1=Inkrementell    F3.2=Durchbruch
  F4: Wirtschaft            F4.1=Wachstum        F4.2=Rezession
  F5: Alternativen          F5.1=Keine           F5.2=Schienenausbau
  F6: Gesellschaft          F6.1=Akzeptiert      F6.2=Flight Shaming
  F7: Geopolit. Stabilitaet F7.1=Offene Luftraeume F7.2=Sperrungen/Konflikte
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Der Selbsttest unten importiert `src`. Wird das Skript über seinen Pfad
# gestartet (`python scripts/rebuild_cib_frozen.py`), liegt nur `scripts/` auf
# dem Suchpfad — der Neubau lief dann durch und brach danach mit einem
# ModuleNotFoundError ab, also genau nach dem Schreiben der Datei.
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# fmt: off
INFLUENCES = {
    # ── F1.1 (Global travel boom) ──────────────────────────────────────────
    ("F1.1", "F2.1"): +1,  # industry lobbies for moderate policy
    ("F1.1", "F2.2"): -2,  # industry resists radical regulation
    ("F1.1", "F3.1"): -1,  # slight innovation pressure, not urgent
    ("F1.1", "F3.2"): +2,  # large market = SAF investment incentive
    ("F1.1", "F4.1"): +3,  # high demand = economic activity = stable growth
    ("F1.1", "F4.2"): -2,  # high demand prevents recession
    ("F1.1", "F5.1"): +2,  # flying preferred = no investment in alternatives
    ("F1.1", "F5.2"): -2,  # flying preferred = less political will for rail
    ("F1.1", "F6.1"): +2,  # high demand = flying is normal = societal acceptance
    ("F1.1", "F6.2"): -2,  # high demand = flying is norm = less shaming
    ("F1.1", "F7.1"): +1,  # Dichter internationaler Reiseverkehr schafft wirtschaftliche Verflechtung und persoenliche Bindungen; daempfend auf Konflikte, aber schwach
    ("F1.1", "F7.2"): -1,  # Hohe Reisenachfrage arbeitet gegen Abschottung, ohne sie verhindern zu koennen

    # ── F1.2 (Stagnation & Verzicht) ───────────────────────────────────────
    ("F1.2", "F2.1"): -1,  # reduced industry lobbying
    ("F1.2", "F2.2"): +3,  # FOLIE 22: voluntary abstinence makes radical legislation easy!
    ("F1.2", "F3.1"): +1,  # less demand = less urgency for SAF breakthrough
    ("F1.2", "F3.2"): -1,  # less market = less SAF investment incentive
    ("F1.2", "F4.1"): -2,  # stagnating aviation = some economic damage
    ("F1.2", "F4.2"): +1,  # stagnation contributes to economic slowdown
    ("F1.2", "F5.1"): -2,  # stagnation driven by alternatives = F5.1 undermined
    ("F1.2", "F5.2"): +3,  # stagnation drives investment in alternatives
    ("F1.2", "F6.1"): -2,  # people not flying = flying not normalized
    ("F1.2", "F6.2"): +2,  # stagnation driven by social pressure
    ("F1.2", "F7.1"): -1,  # Weniger Mobilitaet = weniger Verflechtung; schwaches Gegenteil von F1.1
    ("F1.2", "F7.2"): +1,  # Rueckzug aufs Regionale begleitet Fragmentierung, verursacht sie aber nicht

    # ── F2.1 (Moderate climate protection / market focus) ──────────────────
    ("F2.1", "F1.1"): +1,  # affordable flying under moderate regulation
    ("F2.1", "F1.2"): -1,  # moderate policy = no incentive to avoid flying
    ("F2.1", "F3.1"): +3,  # no strong incentive = tech stays incremental
    ("F2.1", "F3.2"): -2,  # weak policy = no SAF breakthrough incentive
    ("F2.1", "F4.1"): +3,  # market-friendly = economic growth
    ("F2.1", "F4.2"): -3,  # moderate policy prevents economic disruption
    ("F2.1", "F5.1"): +2,  # no radical climate policy = no rail investment
    ("F2.1", "F5.2"): -2,  # no environmental urgency = no rail push
    ("F2.1", "F6.1"): +2,  # moderate policy signals flying is OK
    ("F2.1", "F6.2"): -2,  # moderate policy = society OK with flying
    ("F2.1", "F7.1"): +2,  # Moderater Klimaschutz mit Kompensationsfokus ist multilateral organisiert (CORSIA/ICAO) und staerkt damit kooperative Strukturen. Frueher +3 unter der Marktlesart; als geopolitische Wirkung ist das zu stark
    ("F2.1", "F7.2"): -1,  # Ein gemeinsames Regelwerk arbeitet gegen Fragmentierung

    # ── F2.2 (Net-Zero priority / radical regulation) ──────────────────────
    ("F2.2", "F1.1"): -2,  # strict = expensive flying = less demand
    ("F2.2", "F1.2"): +2,  # strict regulation = flying restricted = stagnation
    ("F2.2", "F3.1"): -2,  # strict regulation = pressure to move beyond incremental
    ("F2.2", "F3.2"): +3,  # radical regulation = strong SAF incentive
    ("F2.2", "F4.1"): -1,  # regulatory burden = slight economic drag
    ("F2.2", "F4.2"): +2,  # heavy regulation can cause economic stress
    ("F2.2", "F5.1"): -2,  # strict climate policy = invest in alternatives
    ("F2.2", "F5.2"): +3,  # strict climate policy = rail development
    ("F2.2", "F6.1"): -2,  # strict policy signals flying is harmful
    ("F2.2", "F6.2"): +2,  # regulation reinforces anti-flying sentiment
    ("F2.2", "F7.1"): -1,  # Radikale nationale Alleingaenge erzeugen Handelsreibung — vgl. den Streit um die EU-ETS-Einbeziehung des Luftverkehrs 2012
    ("F2.2", "F7.2"): +1,  # Unabgestimmte Verbote foerdern Blockbildung

    # ── F3.1 (Incremental tech / no SAF breakthrough) ──────────────────────
    ("F3.1", "F1.1"):  0,  # neutral
    ("F3.1", "F1.2"): +1,  # no eco-solution = less motivation to fly green
    ("F3.1", "F2.1"): +2,  # status quo tech supports status quo policy
    ("F3.1", "F2.2"): -1,  # no breakthrough = harder to justify radical policy
    ("F3.1", "F4.1"): -1,  # slightly higher operational costs
    ("F3.1", "F4.2"): +1,  # higher costs = some economic drag
    ("F3.1", "F5.1"): +1,  # no competition = status quo = no alternatives
    ("F3.1", "F5.2"): -1,  # but no eco-solution = slight push for alternatives
    ("F3.1", "F6.1"): +2,  # no green alternative = flying accepted as-is
    ("F3.1", "F6.2"): -1,  # incremental tech = some environmental concern remains
    ("F3.1", "F7.1"):  0,  # Inkrementelle Technik wirkt nicht auf die geopolitische Lage
    ("F3.1", "F7.2"): +1,  # Anhaltende Abhaengigkeit von fossilem Kerosin haelt den Luftverkehr fuer Versorgungsschocks offen

    # ── F3.2 (SAF breakthrough / E-Fuels) ──────────────────────────────────
    ("F3.2", "F1.1"): +2,  # green flying = guilt-free = more travel
    ("F3.2", "F1.2"): -2,  # SAF removes guilt = no reason to abstain
    ("F3.2", "F2.1"): +1,  # tech solves problem = moderate policy sufficient
    ("F3.2", "F2.2"): -2,  # tech solves problem = strict regulation less justified
    ("F3.2", "F4.1"): +2,  # new green aviation industry = economic growth
    ("F3.2", "F4.2"): -2,  # SAF = new economic opportunity
    ("F3.2", "F5.1"): +1,  # green flying = less need for alternatives
    ("F3.2", "F5.2"): -1,  # green aviation competes with rail
    ("F3.2", "F6.1"): +3,  # green flying = guilt-free = fully accepted
    ("F3.2", "F6.2"): -3,  # SAF removes environmental basis for flight shaming
    ("F3.2", "F7.1"): +1,  # Heimisch herstellbare E-Fuels senken die Importabhaengigkeit und damit einen Konflikttreiber
    ("F3.2", "F7.2"): -1,  # Gegenrichtung zu F3.2 -> F7.1

    # ── F4.1 (Stable economic growth) ──────────────────────────────────────
    ("F4.1", "F1.1"): +2,  # prosperity = can afford to fly
    ("F4.1", "F1.2"): -2,  # prosperity = no reason to cut travel
    ("F4.1", "F2.1"): +3,  # economic growth prefers market-friendly = moderate policy
    ("F4.1", "F2.2"): -2,  # prosperity = less urgency for radical regulation
    ("F4.1", "F3.1"):  0,  # neutral: prosperity finances any tech path equally
    ("F4.1", "F3.2"): +2,  # prosperity = resources for SAF R&D (net positive for breakthrough)
    ("F4.1", "F5.1"): +2,  # prosperity = prefer flying comfort
    ("F4.1", "F5.2"): -1,  # flying preferred over rail investment
    ("F4.1", "F6.1"): +3,  # prosperity = flying is part of good life = accepted
    ("F4.1", "F6.2"): -1,  # prosperity = flying is normal = less shaming
    ("F4.1", "F7.1"): +2,  # Wohlstand und Handel daempfen zwischenstaatliche Konflikte — unveraendert, weil unter beiden Lesarten dieselbe Wirkung
    ("F4.1", "F7.2"): -1,  # Stabile Wirtschaft arbeitet gegen Abschottung

    # ── F4.2 (Recession / economic crisis) ─────────────────────────────────
    ("F4.2", "F1.1"): -2,  # recession = less money for travel
    ("F4.2", "F1.2"): +2,  # recession = people cut travel
    ("F4.2", "F2.1"): +1,  # recession = prefer less regulatory burden
    ("F4.2", "F2.2"): -2,  # recession = can't afford strict regulation
    ("F4.2", "F3.1"): +2,  # recession = no resources for SAF breakthrough
    ("F4.2", "F3.2"): -3,  # recession = no investment for SAF
    ("F4.2", "F5.1"):  0,  # neutral
    ("F4.2", "F5.2"):  0,  # neutral
    ("F4.2", "F6.1"):  0,  # neutral
    ("F4.2", "F6.2"): +1,  # economic stress = environmental awareness
    ("F4.2", "F7.1"): -2,  # Wirtschaftliche Not befoerdert Nationalismus und Protektionismus — unveraendert gueltig
    ("F4.2", "F7.2"): +2,  # Rezession als Treiber von Blockbildung und Handelskonflikten

    # ── F5.1 (No attractive alternatives) ──────────────────────────────────
    ("F5.1", "F1.1"): +2,  # captive market = sustained flying demand
    ("F5.1", "F1.2"): -2,  # no alternatives = can't substitute = demand sustained
    ("F5.1", "F2.1"): +1,  # aviation monopoly = industry prefers moderate policy
    ("F5.1", "F2.2"): -1,  # no alternatives = harder to justify strict policy
    ("F5.1", "F3.1"): +1,  # no competition = no urgency for tech
    ("F5.1", "F3.2"): -1,  # no competitive pressure = less SAF urgency
    ("F5.1", "F4.1"): +1,  # aviation monopoly = some economic stability
    ("F5.1", "F4.2"): -1,  # monopoly provides some stability
    ("F5.1", "F6.1"): +2,  # no alternatives = flying is only option = normalized
    ("F5.1", "F6.2"): -1,  # hard to shame if no alternative exists
    ("F5.1", "F7.1"):  0,  # Kein Mechanismus: Ob die Schiene in Europa ausgebaut wird, beruehrt die weltpolitische Lage nicht. Frueher +2 aus der Marktlesart
    ("F5.1", "F7.2"):  0,  # Kein Mechanismus, siehe F5.1 -> F7.1

    # ── F5.2 (Rail development / modal shift) ──────────────────────────────
    ("F5.2", "F1.1"): -3,  # rail substitutes air = strongly reduces flying demand
    ("F5.2", "F1.2"): +3,  # rail drives air travel stagnation
    ("F5.2", "F2.1"):  0,  # neutral
    ("F5.2", "F2.2"): +1,  # alternatives = signal environmental consciousness
    ("F5.2", "F3.1"):  0,  # neutral
    ("F5.2", "F3.2"):  0,  # neutral - independent innovation paths
    ("F5.2", "F4.1"): +1,  # rail investment = infrastructure = some economic growth
    ("F5.2", "F4.2"):  0,  # neutral
    ("F5.2", "F6.1"): -1,  # alternatives available = flying less central
    ("F5.2", "F6.2"): +2,  # rail = environmental values = flight shaming
    ("F5.2", "F7.1"):  0,  # Kein Mechanismus: Schienenausbau ist Verkehrspolitik, nicht Geopolitik
    ("F5.2", "F7.2"):  0,  # Kein Mechanismus, siehe F5.2 -> F7.1

    # ── F6.1 (Flying accepted / no flight shaming) ─────────────────────────
    ("F6.1", "F1.1"): +3,  # societal acceptance = high demand
    ("F6.1", "F1.2"): -2,  # flying accepted = no stagnation
    ("F6.1", "F2.1"): +2,  # flying OK = society supports moderate policy
    ("F6.1", "F2.2"): -2,  # flying accepted = harder to justify radical restriction
    ("F6.1", "F3.1"): +2,  # no urgency = tech stays incremental
    ("F6.1", "F3.2"): -1,  # no urgency = less push for SAF breakthrough
    ("F6.1", "F4.1"): +2,  # flying = economic activity = growth
    ("F6.1", "F4.2"): -2,  # flying accepted = economic activity = no recession
    ("F6.1", "F5.1"): +2,  # flying preferred = no investment in alternatives
    ("F6.1", "F5.2"): -3,  # flying preferred = political opposition to rail spending
    ("F6.1", "F7.1"):  0,  # Kein Mechanismus: Gesellschaftliche Flugakzeptanz treibt keine Weltpolitik. Frueher +3 und damit der hoechste Wert der Spalte — reiner Rest der Marktlesart
    ("F6.1", "F7.2"):  0,  # Kein Mechanismus, siehe F6.1 -> F7.1

    # ── F6.2 (Flight shaming) ──────────────────────────────────────────────
    ("F6.2", "F1.1"): -3,  # shaming drastically reduces air travel demand
    ("F6.2", "F1.2"): +2,  # shaming drives stagnation
    ("F6.2", "F2.1"): -3,  # shaming demands more than moderate policy
    ("F6.2", "F2.2"): +2,  # shaming supports radical climate policy
    ("F6.2", "F3.1"): -1,  # shaming puts pressure on incremental tech
    ("F6.2", "F3.2"): +2,  # environmental pressure drives SAF innovation
    ("F6.2", "F4.1"): -2,  # less flying = some economic damage
    ("F6.2", "F4.2"): +1,  # reduced economic activity from aviation
    ("F6.2", "F5.1"): -2,  # shaming demands alternatives
    ("F6.2", "F5.2"): +3,  # shaming = invest in alternatives = rail
    ("F6.2", "F7.1"):  0,  # Kein Mechanismus: Flugscham ist ein innergesellschaftliches Phaenomen
    ("F6.2", "F7.2"):  0,  # Kein Mechanismus, siehe F6.2 -> F7.1

    # ── F7.1 (Open global markets) ─────────────────────────────────────────
    ("F7.1", "F1.1"): +2,  # Offene Lufträume ermoeglichen Nachfrage, erzeugen sie aber nicht — deshalb schwaecher als die Sperrwirkung von F7.2
    ("F7.1", "F1.2"): -1,  # Ohne Reisehindernisse kein erzwungener Verzicht
    ("F7.1", "F2.1"): +2,  # Eine kooperative Ordnung bringt multilaterale, moderate Instrumente hervor (ICAO/CORSIA)
    ("F7.1", "F2.2"): -1,  # Kooperation macht nationale Alleingaenge unwahrscheinlicher, koordinierte harte Schritte aber eher — deshalb nur schwach negativ. Frueher -2 aus der Lobby-Logik der Marktlesart
    ("F7.1", "F3.1"):  0,  # Neutral
    ("F7.1", "F3.2"): +1,  # Kooperation ermoeglicht gemeinsame SAF-Standards und Technologietransfer
    ("F7.1", "F4.1"): +2,  # Stabile Ordnung = Handel, Investitionen, Wachstum
    ("F7.1", "F4.2"): -1,  # Stabilitaet senkt das Rezessionsrisiko
    ("F7.1", "F5.1"): +1,  # Verlaessliche Flugverbindungen mindern den Druck, Alternativen aufzubauen
    ("F7.1", "F5.2"): -1,  # Gegenrichtung zu F7.1 -> F5.1
    ("F7.1", "F6.1"): +1,  # Ungestoertes Fliegen bleibt selbstverstaendlich — schwach, weil Akzeptanz vor allem am Klimadiskurs haengt (F6-Eigenlogik). Frueher +2
    ("F7.1", "F6.2"): -1,  # Gegenrichtung zu F7.1 -> F6.1

    # ── F7.2 (Market fragmentation) ────────────────────────────────────────
    ("F7.2", "F1.1"): -3,  # Luftraumsperrungen und Pandemien sind der groesste beobachtete Nachfrageschock der Branche (2020: rund zwei Drittel Rueckgang; Sperrung des russischen Luftraums). Frueher -2 — unter der Marktlesart war der Mechanismus schwaecher
    ("F7.2", "F1.2"): +2,  # Sperrungen erzwingen Verzicht und Substitution unmittelbar
    ("F7.2", "F2.1"):  0,  # Neutral: Fragmentierung hilft moderater Politik nicht
    ("F7.2", "F2.2"): +1,  # Ohne multilaterales Instrument gehen einzelne Bloecke unabgestimmt hart vor
    ("F7.2", "F3.1"): +1,  # Zerrissene Lieferketten und fehlende Skalen halten SAF teuer
    ("F7.2", "F3.2"): -1,  # Gegenrichtung zu F7.2 -> F3.1
    ("F7.2", "F4.1"): -2,  # Konflikte und Sanktionen schaedigen Wachstum
    ("F7.2", "F4.2"): +2,  # Geopolitische Schocks sind ein klassischer Rezessionsausloeser (Oelpreiskrisen 1973/79, Pandemie 2020). Frueher +1
    ("F7.2", "F5.1"): -1,  # Wird Fliegen unzuverlaessig, ist es nicht mehr alternativlos. Frueher 0
    ("F7.2", "F5.2"): +1,  # Gestoerte Luftverbindungen erhoehen den Druck auf die Schiene
    ("F7.2", "F6.1"): -1,  # Eingeschraenktes Fliegen verliert an Selbstverstaendlichkeit
    ("F7.2", "F6.2"):  0,  # Kein Mechanismus: Konflikte erzeugen kein Klimabewusstsein. Frueher +1 aus einer Regional-Kultur-Annahme der Marktlesart
}
# fmt: on


#: Begruendung je F7-Zelle (P0.2, Lesart „Geopolitische Stabilitaet").
#: Fuer die uebrigen 120 Zellen holt P2.3 das nach.
F7_REASONING: dict[tuple[str, str], str] = {
    (
        "F1.1",
        "F7.1",
    ): "Dichter internationaler Reiseverkehr schafft wirtschaftliche Verflechtung und persoenliche Bindungen; daempfend auf Konflikte, aber schwach",
    (
        "F1.1",
        "F7.2",
    ): "Hohe Reisenachfrage arbeitet gegen Abschottung, ohne sie verhindern zu koennen",
    ("F1.2", "F7.1"): "Weniger Mobilitaet = weniger Verflechtung; schwaches Gegenteil von F1.1",
    ("F1.2", "F7.2"): "Rueckzug aufs Regionale begleitet Fragmentierung, verursacht sie aber nicht",
    (
        "F2.1",
        "F7.1",
    ): "Moderater Klimaschutz mit Kompensationsfokus ist multilateral organisiert (CORSIA/ICAO) und staerkt damit kooperative Strukturen. Frueher +3 unter der Marktlesart; als geopolitische Wirkung ist das zu stark",
    ("F2.1", "F7.2"): "Ein gemeinsames Regelwerk arbeitet gegen Fragmentierung",
    (
        "F2.2",
        "F7.1",
    ): "Radikale nationale Alleingaenge erzeugen Handelsreibung — vgl. den Streit um die EU-ETS-Einbeziehung des Luftverkehrs 2012",
    ("F2.2", "F7.2"): "Unabgestimmte Verbote foerdern Blockbildung",
    ("F3.1", "F7.1"): "Inkrementelle Technik wirkt nicht auf die geopolitische Lage",
    (
        "F3.1",
        "F7.2",
    ): "Anhaltende Abhaengigkeit von fossilem Kerosin haelt den Luftverkehr fuer Versorgungsschocks offen",
    (
        "F3.2",
        "F7.1",
    ): "Heimisch herstellbare E-Fuels senken die Importabhaengigkeit und damit einen Konflikttreiber",
    ("F3.2", "F7.2"): "Gegenrichtung zu F3.2 -> F7.1",
    (
        "F4.1",
        "F7.1",
    ): "Wohlstand und Handel daempfen zwischenstaatliche Konflikte — unveraendert, weil unter beiden Lesarten dieselbe Wirkung",
    ("F4.1", "F7.2"): "Stabile Wirtschaft arbeitet gegen Abschottung",
    (
        "F4.2",
        "F7.1",
    ): "Wirtschaftliche Not befoerdert Nationalismus und Protektionismus — unveraendert gueltig",
    ("F4.2", "F7.2"): "Rezession als Treiber von Blockbildung und Handelskonflikten",
    (
        "F5.1",
        "F7.1",
    ): "Kein Mechanismus: Ob die Schiene in Europa ausgebaut wird, beruehrt die weltpolitische Lage nicht. Frueher +2 aus der Marktlesart",
    ("F5.1", "F7.2"): "Kein Mechanismus, siehe F5.1 -> F7.1",
    ("F5.2", "F7.1"): "Kein Mechanismus: Schienenausbau ist Verkehrspolitik, nicht Geopolitik",
    ("F5.2", "F7.2"): "Kein Mechanismus, siehe F5.2 -> F7.1",
    (
        "F6.1",
        "F7.1",
    ): "Kein Mechanismus: Gesellschaftliche Flugakzeptanz treibt keine Weltpolitik. Frueher +3 und damit der hoechste Wert der Spalte — reiner Rest der Marktlesart",
    ("F6.1", "F7.2"): "Kein Mechanismus, siehe F6.1 -> F7.1",
    ("F6.2", "F7.1"): "Kein Mechanismus: Flugscham ist ein innergesellschaftliches Phaenomen",
    ("F6.2", "F7.2"): "Kein Mechanismus, siehe F6.2 -> F7.1",
    (
        "F7.1",
        "F1.1",
    ): "Offene Lufträume ermoeglichen Nachfrage, erzeugen sie aber nicht — deshalb schwaecher als die Sperrwirkung von F7.2",
    ("F7.1", "F1.2"): "Ohne Reisehindernisse kein erzwungener Verzicht",
    (
        "F7.1",
        "F2.1",
    ): "Eine kooperative Ordnung bringt multilaterale, moderate Instrumente hervor (ICAO/CORSIA)",
    (
        "F7.1",
        "F2.2",
    ): "Kooperation macht nationale Alleingaenge unwahrscheinlicher, koordinierte harte Schritte aber eher — deshalb nur schwach negativ. Frueher -2 aus der Lobby-Logik der Marktlesart",
    ("F7.1", "F3.1"): "Neutral",
    ("F7.1", "F3.2"): "Kooperation ermoeglicht gemeinsame SAF-Standards und Technologietransfer",
    ("F7.1", "F4.1"): "Stabile Ordnung = Handel, Investitionen, Wachstum",
    ("F7.1", "F4.2"): "Stabilitaet senkt das Rezessionsrisiko",
    ("F7.1", "F5.1"): "Verlaessliche Flugverbindungen mindern den Druck, Alternativen aufzubauen",
    ("F7.1", "F5.2"): "Gegenrichtung zu F7.1 -> F5.1",
    (
        "F7.1",
        "F6.1",
    ): "Ungestoertes Fliegen bleibt selbstverstaendlich — schwach, weil Akzeptanz vor allem am Klimadiskurs haengt (F6-Eigenlogik). Frueher +2",
    ("F7.1", "F6.2"): "Gegenrichtung zu F7.1 -> F6.1",
    (
        "F7.2",
        "F1.1",
    ): "Luftraumsperrungen und Pandemien sind der groesste beobachtete Nachfrageschock der Branche (2020: rund zwei Drittel Rueckgang; Sperrung des russischen Luftraums). Frueher -2 — unter der Marktlesart war der Mechanismus schwaecher",
    ("F7.2", "F1.2"): "Sperrungen erzwingen Verzicht und Substitution unmittelbar",
    ("F7.2", "F2.1"): "Neutral: Fragmentierung hilft moderater Politik nicht",
    ("F7.2", "F2.2"): "Ohne multilaterales Instrument gehen einzelne Bloecke unabgestimmt hart vor",
    ("F7.2", "F3.1"): "Zerrissene Lieferketten und fehlende Skalen halten SAF teuer",
    ("F7.2", "F3.2"): "Gegenrichtung zu F7.2 -> F3.1",
    ("F7.2", "F4.1"): "Konflikte und Sanktionen schaedigen Wachstum",
    (
        "F7.2",
        "F4.2",
    ): "Geopolitische Schocks sind ein klassischer Rezessionsausloeser (Oelpreiskrisen 1973/79, Pandemie 2020). Frueher +1",
    ("F7.2", "F5.1"): "Wird Fliegen unzuverlaessig, ist es nicht mehr alternativlos. Frueher 0",
    ("F7.2", "F5.2"): "Gestoerte Luftverbindungen erhoehen den Druck auf die Schiene",
    ("F7.2", "F6.1"): "Eingeschraenktes Fliegen verliert an Selbstverstaendlichkeit",
    (
        "F7.2",
        "F6.2",
    ): "Kein Mechanismus: Konflikte erzeugen kein Klimabewusstsein. Frueher +1 aus einer Regional-Kultur-Annahme der Marktlesart",
}


def _factor_labels() -> list[str]:
    """`["F1 <Name aus factors.json>", …]` — die eine Namensquelle."""

    raw = json.loads((REPO / "configs" / "factors.json").read_text(encoding="utf-8"))
    return [f"{fid} {raw[fid]['name']}" for fid in sorted(raw)]


def main() -> None:
    factors = ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]
    descriptors = [f"{f}.{s}" for f in factors for s in ("1", "2")]

    # Build cells
    cells: dict = {}
    for (src, tgt), inf in INFLUENCES.items():
        cells[f"{src}|{tgt}"] = {
            "source_descriptor": src,
            "target_descriptor": tgt,
            "influence": inf,
            "reasoning": F7_REASONING.get((src, tgt), ""),
        }

    # Verify same-sign contradictions
    contradictions = []
    for src in descriptors:
        for tgt_f in factors:
            if tgt_f == src[:2]:
                continue
            v1 = INFLUENCES.get((src, f"{tgt_f}.1"), 0)
            v2 = INFLUENCES.get((src, f"{tgt_f}.2"), 0)
            if v1 * v2 > 0:
                contradictions.append(f"  {src} -> {tgt_f}.1={v1:+d} AND {tgt_f}.2={v2:+d}")

    if contradictions:
        print(f"WARNING: {len(contradictions)} same-sign contradictions remain:")
        for c in contradictions:
            print(c)
    else:
        print("OK: No same-sign contradictions found.")

    # Compute factor scores
    factor_scores = []
    for f in factors:
        active = sum(
            abs(INFLUENCES.get((f"{f}.1", tgt), 0)) + abs(INFLUENCES.get((f"{f}.2", tgt), 0))
            for tgt in descriptors
            if not tgt.startswith(f)
        )
        passive = sum(
            abs(INFLUENCES.get((src, f"{f}.1"), 0)) + abs(INFLUENCES.get((src, f"{f}.2"), 0))
            for src in descriptors
            if not src.startswith(f)
        )
        factor_scores.append({"factor_id": f, "active_score": active, "passive_score": passive})
        print(f"  {f}: active={active}, passive={passive}")

    result = {
        "cells": cells,
        "entries": [],
        "round_generated": 0,
        "factor_scores": factor_scores,
        "metadata": {
            "frozen": True,
            "source": "llm_proposed_pending_review_v3",
            "note": (
                "Reference matrix for the aviation socio-technical system (F1-F7). Values encode "
                "cross-impact relationships based on Strategic Foresight methodology "
                "(Weimer-Jehle 2023) and lecture slides (Folie 19-22). Frozen by design: CIB "
                "methodology requires a static reference matrix for reproducible consistency "
                "scoring. ACHTUNG PROVENIENZ: Die 48 F7-Zellen wurden am 2026-08-26 unter der "
                "Lesart 'Geopolitische Stabilitaet' neu bewertet (P0.2) — modellgeneriert und "
                "noch nicht fachlich abgenommen, siehe reasoning je Zelle. Die uebrigen 120 "
                "Zellen stammen aus der Erstbewertung durch das Team und haben noch keine "
                "Begruendung (P2.3)."
            ),
            # Nicht abgeschrieben, sondern aus `factors.json` gelesen: Genau
            # diese doppelte Pflege war die F7-Drift. Wer den Faktor dort
            # umbenennt, benennt ihn hier mit — ein Auseinanderlaufen ist beim
            # Neubau baulich nicht mehr möglich, und `tests/test_factor_naming.py`
            # fängt eine Änderung von Hand ab.
            "factors": _factor_labels(),
        },
    }

    out = REPO / "configs" / "cib_frozen.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten {len(cells)} cells to {out}")

    # Quick sanity: compute scores for three archetypes
    from src.cib.scenario_consistency import ConsistencyChecker, ScenarioDescriptor
    from src.models.cib_models import CIBMatrix

    matrix = CIBMatrix.model_validate(result)
    checker = ConsistencyChecker(matrix)

    scenarios = {
        "BAU": {
            "F1": "F1.1",
            "F2": "F2.1",
            "F3": "F3.1",
            "F4": "F4.1",
            "F5": "F5.1",
            "F6": "F6.1",
            "F7": "F7.1",
        },
        "Wende": {
            "F1": "F1.2",
            "F2": "F2.2",
            "F3": "F3.2",
            "F4": "F4.1",
            "F5": "F5.2",
            "F6": "F6.2",
            "F7": "F7.1",
        },
        "Konflikt": {
            "F1": "F1.2",
            "F2": "F2.2",
            "F3": "F3.1",
            "F4": "F4.2",
            "F5": "F5.2",
            "F6": "F6.2",
            "F7": "F7.2",
        },
    }
    print("\nScenario consistency scores:")
    for name, states in scenarios.items():
        s = ScenarioDescriptor(factor_states=states)
        cs = checker.compute_consistency_score(s)
        r = checker.check_scenario(s)
        print(f"  {name}: consistency={cs:.4f}, conflicts={len(r.conflicts)}")


if __name__ == "__main__":
    main()
