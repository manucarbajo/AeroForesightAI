"""Modellpfad gegen Zielreihe — indexiert, auf Jahresmitteln, mit benannter Lücke.

**Verglichen wird die relative Veränderung, nicht das Niveau.** Der absolute
Ticketpreis des Modells hängt an `base_price` und an acht Koeffizienten, von
denen seit P2.1 aktenkundig keiner geschätzt ist. Ein Vergleich auf Euro-Niveau
prüfte eine Genauigkeit, die das Modell nie behauptet hat.

**Und verglichen wird auf Jahresmitteln, nicht monatlich.** Das ist keine
Bequemlichkeit, sondern eine Korrektur: Der erste Anlauf maß die monatliche
Bewegungsrichtung und kam auf 44 % Treffer — *unter* dem Münzwurf. Die Ursache
war die Kennzahl, nicht das Modell. Air-Fare-Preise schwanken saisonal
gewaltig — die Zielreihe um durchschnittlich **34 Indexpunkte innerhalb eines
Jahres**, das Modell nur um **14**, weil es keine Saison kennt. Der
Monatsvergleich maß damit vor allem, ob das Modell eine Sommersaison hat. Das
tut es nicht, und das war nie behauptet.

Die Saisonkennzahl bleibt trotzdem stehen — als das, was sie ist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean

from src.backtest.reihen import alle_monate, ist_bewertet


def indexieren(reihe: dict[str, float], *, basisjahr: str) -> dict[str, float]:
    """Auf das Mittel eines Basisjahres normieren, 100 = Basisjahr.

    Dieselbe Basis wie die Zielreihe: Eurostats `CP0733` steht auf 2015 = 100,
    und das ist genau der Anfang des Fensters.
    """

    basiswerte = [w for m, w in reihe.items() if m.startswith(basisjahr)]
    if not basiswerte:
        raise ValueError(f"Keine Werte im Basisjahr {basisjahr}")
    basis = mean(basiswerte)
    if basis == 0:
        raise ValueError("Basis ist null — Index nicht bildbar")
    return {m: 100.0 * w / basis for m, w in reihe.items()}


def jahresmittel(reihe: dict[str, float]) -> dict[str, float]:
    je_jahr: dict[str, list[float]] = {}
    for monat, wert in reihe.items():
        je_jahr.setdefault(monat[:4], []).append(wert)
    return {jahr: mean(werte) for jahr, werte in sorted(je_jahr.items())}


def saisonspanne(reihe: dict[str, float]) -> float:
    """Wie weit die Reihe **innerhalb** eines Jahres schwankt, im Mittel."""

    je_jahr: dict[str, list[float]] = {}
    for monat, wert in reihe.items():
        je_jahr.setdefault(monat[:4], []).append(wert)
    spannen = [max(w) - min(w) for w in je_jahr.values() if len(w) > 1]
    return mean(spannen) if spannen else 0.0


@dataclass(frozen=True)
class Abweichung:
    """Was der Vorlauf über den Preispfad sagt — und worüber er schweigt."""

    #: Jahresmittel beider Reihen, indexiert. Die eigentliche Auskunft.
    modell_je_jahr: dict[str, float]
    ziel_je_jahr: dict[str, float]
    #: Mittlerer absoluter Abstand der Jahresmittel, nur bewertete Jahre.
    mittlerer_abstand: float
    #: Das Jahr mit dem größten Abstand.
    groesster_abstand: float
    groesster_abstand_jahr: str
    #: Trifft das Modell die **Richtung** der Jahresveränderung?
    richtungstreffer: str
    #: Saisonschwankung beider Reihen — zur Einordnung, nicht zur Bewertung.
    saison_modell: float
    saison_ziel: float
    bewertete_jahre: list[str]
    unbewertete_jahre: list[str]
    hinweise: list[str] = field(default_factory=list)

    def abstand_ueber(self, jahre: list[str]) -> float | None:
        vorhanden = [j for j in jahre if j in self.modell_je_jahr and j in self.ziel_je_jahr]
        if not vorhanden:
            return None
        return round(mean(abs(self.modell_je_jahr[j] - self.ziel_je_jahr[j]) for j in vorhanden), 2)


def bewerten(
    modell: dict[str, float],
    ziel: dict[str, float],
    *,
    basisjahr: str = "2015",
) -> Abweichung:
    """Modell und Ziel indexiert vergleichen; 2020/21 mitrechnen, nicht bewerten."""

    modell_idx = indexieren(modell, basisjahr=basisjahr)
    ziel_idx = indexieren(ziel, basisjahr=basisjahr)

    gemeinsam = {m for m in alle_monate() if m in modell_idx and m in ziel_idx}
    if not gemeinsam:
        raise ValueError("Modell und Ziel überlappen nicht")

    m_jahr = jahresmittel({m: v for m, v in modell_idx.items() if m in gemeinsam})
    z_jahr = jahresmittel({m: v for m, v in ziel_idx.items() if m in gemeinsam})

    alle_jahre = sorted(set(m_jahr) & set(z_jahr))
    bewertet = [j for j in alle_jahre if ist_bewertet(f"{j}-01")]
    ausgenommen = [j for j in alle_jahre if j not in bewertet]
    if not bewertet:
        raise ValueError("Keine bewertbaren Jahre")

    abstaende = {j: abs(m_jahr[j] - z_jahr[j]) for j in bewertet}
    groesstes = max(abstaende, key=abstaende.__getitem__)

    # Richtung der Jahresveränderung, über die bewerteten Jahre in Folge.
    treffer = sum(
        1
        for a, b in zip(bewertet, bewertet[1:])
        if (m_jahr[b] - m_jahr[a] > 0) == (z_jahr[b] - z_jahr[a] > 0)
    )
    vergleiche = max(0, len(bewertet) - 1)

    hinweise = [
        f"Verglichen wird der Index (Basis {basisjahr} = 100) auf **Jahresmitteln**, "
        "nicht das Preisniveau und nicht monatlich.",
        "Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten "
        "(P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.",
    ]
    if ausgenommen:
        hinweise.append(
            f"{', '.join(ausgenommen)} sind mitgerechnet, aber nicht bewertet: Der "
            "Einbruch war keine Preiswirkung, und das Modell kennt keine "
            "Reisebeschränkung."
        )

    saison_m, saison_z = saisonspanne(modell_idx), saisonspanne(ziel_idx)
    if saison_z > 2 * saison_m:
        hinweise.append(
            f"Die Zielreihe schwankt saisonal um {saison_z:.0f} Indexpunkte im Jahr, "
            f"das Modell um {saison_m:.0f}. **Ein Monatsvergleich misst deshalb vor "
            "allem die fehlende Saison** — deswegen die Jahresmittel."
        )

    return Abweichung(
        modell_je_jahr={j: round(v, 2) for j, v in m_jahr.items()},
        ziel_je_jahr={j: round(v, 2) for j, v in z_jahr.items()},
        mittlerer_abstand=round(mean(abstaende.values()), 2),
        groesster_abstand=round(abstaende[groesstes], 2),
        groesster_abstand_jahr=groesstes,
        richtungstreffer=f"{treffer}/{vergleiche}",
        saison_modell=round(saison_m, 2),
        saison_ziel=round(saison_z, 2),
        bewertete_jahre=bewertet,
        unbewertete_jahre=ausgenommen,
        hinweise=hinweise,
    )
