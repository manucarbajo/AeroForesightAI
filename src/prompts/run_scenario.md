Du schreibst **sachliche** explorative Szenarien nach einem abgeschlossenen Simulationslauf (Flugverkehr). Keine erfundenen Geschichten, keine Prognose.

Wir haben in Python bereits 3 Zukunfts-Pfade (Konstellationen aus Faktoren) mathematisch vorausberechnet. Du findest sie im `RUN CONTEXT` unter `precalculated_scenarios`. 
Jeder dieser Pfade hat einen `consistency_score`, der aus unserer CIB-Matrix (Cross-Impact Balance) berechnet wurde. Differenziere Deine Analyse der Stabilität und Wahrscheinlichkeit präzise nach folgendem Spektrum:
- **Score > 0.7 (Hochgradig stabil):** Sehr harmonische Kombination. Das Szenario hat eine sehr hohe Eintrittswahrscheinlichkeit und kaum innere Spannungen. Es ist ein "Lock-in"-Zustand, der nur schwer aufzubrechen ist.
- **Score 0.4 bis 0.7 (Moderat / Fragil):** Das Szenario ist grundsätzlich möglich und plausibel, hat aber Reibungspunkte. Es ist oft ein Übergangszustand, der durch kleine gesellschaftliche Schocks oder Krisen kippen könnte.
- **Score < 0.4 (Instabil / Konfliktreich):** Ein massiver Widerspruch zwischen den Faktoren (z.B. starkes Wachstum vs. radikale Verbote). Sehr unwahrscheinlich als Dauerzustand. Es herrscht hoher Anpassungsdruck und gesellschaftlicher Konflikt.

**Aufgabe:**
Schreibe eine kurze, sachliche Analyse dieses Laufs und der 3 Pfade.

**Aufbau Deiner Antwort:**
1. **summary** — 1–2 Sätze: Zusammenfassung des Laufs und kurze Nennung der drei errechneten Pfade.
2. **run_narrative** — kompakt: Ticks, Nachfrage-/Preistrend, wichtigste Faktorwechsel.
3. **Drei Szenarien** — Schreibe für jeden der 3 vorgegebenen Pfade:
   - **title**: Erfinde einen kreativen, hochgradig passenden Titel für dieses Szenario, der die Essenz der Faktoren auf den Punkt bringt (z.B. "Nachhaltigkeitskrise bei hohem Wachstum").
   - **story**: Schreibe eine ausführliche und tiefgehende Analyse in 2-3 detaillierten Absätzen (mindestens 8-12 Sätze). WICHTIG: Schreibe alle Absätze zusammenhängend in **einen einzigen String** unter dem Key `story` und nutze `\n\n` für Zeilenumbrüche. Erstelle KEINE mehrfachen `story`-Keys!
     - **Absatz 1 (Qualitative Welt):** Beschreibe detailliert und in eigenen Worten die qualitative Ausgestaltung dieser Szenariowelt. Wie sieht der Alltag aus? Welche Konsequenzen ergeben sich für Gesellschaft, Wirtschaft und Umwelt? **WICHTIG: Setze nach JEDEM relevanten Satz die zugehörige Faktor-ID in Klammern, auf die sich die Aussage stützt (z.B. "(F1.2)").**
     - **Absatz 2 (Akteure):** Beleuchte konkret die Auswirkungen auf die Akteure: Wie verhalten sich Passagiere, Airlines und die Politik in dieser Welt? **WICHTIG: Setze auch hier zwingend die entsprechenden Faktor-IDs (z.B. "(F2.1)") ans Ende der Sätze, damit der Leser sofort erkennt, worauf Deine Logik basiert.**
     - **Absatz 3 (Logik & Stabilität):** Integriere die Kausalitäts-Logik der Modulunterlagen. Beschreibe detaillierte Wenn-Dann-Wechselwirkungen explizit für die in diesem Szenario vorkommenden Faktoren. Schließe zwingend mit einer tiefgehenden Bewertung der Wahrscheinlichkeit und Stabilität ab, die den exakten CIB-Score aus dem RUN CONTEXT nennt und erklärt, *warum* dieser Score (hoch oder niedrig) durch die Faktoren zustande kommt.

Antworte mit **einem JSON-Objekt** (kein Markdown, kein Codeblock).
GIB KEINE ERKLÄRUNGEN ODER TEXT VOR ODER NACH DEM JSON AUS. STARTE DIREKT MIT `{`:
{
  "title": "kurzer Gesamttitel",
  "summary": "1–2 sachliche Sätze",
  "run_narrative": "kompakter Laufverlauf",
  "scenarios": [
    {
      "rank": 1,
      "title": "[Erfinde einen passenden Titel]",
      "story": "[Hier schreibst du deine extrem ausführliche Analyse (Welt, Akteure, Logik & Score). Schreibe tiefgehend und detailliert!]"
    },
    {
      "rank": 2,
      "title": "[Erfinde einen passenden Titel]",
      "story": "[Dein Text für Szenario 2...]"
    },
    {
      "rank": 3,
      "title": "[Erfinde einen passenden Titel]",
      "story": "[Dein Text für Szenario 3...]"
    }
  ],
  "limitations": "kurzer Hinweis, z.B. dass dies explorative Szenarien sind"
}

Regeln:
- Genau **3** Szenarien, rank = 1, 2 und 3.
- Übernimm KEINE `factor_constellation` oder `tick_grounding` in den Output, das erledigt Python selbst.
- story: sachlich, nicht erzählend, logische Beweisführung anhand von Faktoren und CIB Score.
