"""Der Backtest gegen 2015–2024 (P2.7) — ein Vorlauf mit zwei Reihen.

**Warum das ein eigenes Paket ist und nicht Teil der Engine:** Der Backtest ist
eine *Auswertung*, kein Modellbestandteil. Er übersetzt Monate in Ticks, füttert
historische Verläufe als Rahmenszenario ein und vergleicht das Ergebnis mit einer
Zielreihe. Nichts davon gehört in `src/market/` oder `src/orchestration/` — und
vor allem gehört **die Kalenderzuordnung hierher und nirgendwo sonst**
(Invariante 5: ein Tick ist ein Tick, kein Monat).

**Der Umfang ist Absicht.** P2.7 nennt ihn einen Vorlauf: zwei Eingangsreihen,
eine Zielreihe, eine Kennzahl. Trifft schon der Preispfad die Größenordnung
nicht, sagt die Nachfrageseite nichts mehr dazu — sie hängt am Preis. Erst wenn
dieser Teil steht, lohnt der Rest.

**Was der Vorlauf beantwortet — und was nicht.** Er prüft Richtung,
Größenordnung und Wendepunkte des Ticketpreises, **indexiert auf 2015 = 100**.
Er prüft ausdrücklich **nicht** das Preisniveau in Euro: Das hängt an
`base_price` und acht Koeffizienten, von denen seit P2.1 aktenkundig keiner
geschätzt ist. Ein Niveauvergleich prüfte eine Genauigkeit, die das Modell nie
behauptet hat.
"""

from src.backtest.auswertung import Abweichung, bewerten
from src.backtest.rahmen import historischer_rahmen
from src.backtest.reihen import FENSTER, UNBEWERTET, Reihe, laden

__all__ = [
    "Abweichung",
    "FENSTER",
    "Reihe",
    "UNBEWERTET",
    "bewerten",
    "historischer_rahmen",
    "laden",
]
