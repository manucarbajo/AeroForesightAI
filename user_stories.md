# Anforderungserhebung

> **Methodische Grundlage:** Gemäß Ludewig & Lichter, Kap. 15.4.4 beschreiben Anforderungen den Nutzen, den eine Software bringen soll (funktionale Anforderungen), und welche Eigenschaften es haben muss (nicht-funktionale Anforderungen). Sie werden aus Sicht der Stakeholder formuliert und müssen eindeutig, prüfbar, konsistent und verfolgbar sein.

---

## Funktionale Anforderungen (User Stories)

#### Formatierung
User Stories folgen dem Format (vgl. Ludewig & Lichter, Kap. 15.7.4, S. 377 ff.):
> **Als** [Rolle] **möchte ich** [Funktion], **damit** [Nutzen].

#### Priorisierung
Die Priorisierung der Stories erfolgte mit der Methode MoSCoW
* **M (Must-have):**
* **S (Should-have):**
* **C (Could-have):**
* **W (Won't-have):**

---

### Rolle: Foresight-Analyst
*Der Analyst konfiguriert die Simulation und nutzt die Ergebnisse für strategische Berichte.*

| ID | User Story | Priorität | Phase |
| :--- | :--- | :--- | :--- |
| **US-A1** | Als Foresight-Analyst möchte ich eine vorgefertigte Konfigurationsdatei (z.B. JSON) hochladen können, in der die Basis-Prompts und Ziele der drei Hauptakteure (Konsument, Anbieter, Regulator) hinterlegt sind, damit ich die Simulation schnell starten kann. | Must | Setup |
| **US-A2** | Als Foresight-Analyst möchte ich eine zentrale strategische Fragestellung (z.B. „Zukunft des Flugverkehrs 2040“) eingeben können, damit die Agenten einen klaren Rahmen haben. | Must | Setup |
| **US-A3** | Als Foresight-Analyst möchte ich den Simulationslauf mit einem einfachen Klick auf „Start“ initiieren können, damit das System die Gesprächsrunden automatisch abarbeitet. | Must | Simulation |
| **US-A4** | Als Foresight-Analyst möchte ich nach Abschluss das vollständige Gesprächsprotokoll im Klartext lesen können, um qualitative Argumentationslinien nachzuvollziehen. | Must | Output |
| **US-A5** | Als Foresight-Analyst möchte ich am Ende eine maschinell abgeleitete Cross-Impact-Bilanz (CIB) und eine Visualisierung erhalten, um die gegenseitige Beeinflussung der Akteure zu sehen. | Must | Output |
| **US-A6** | Als Foresight-Analyst möchte ich das Protokoll und die CIB-Matrix lokal abspeichern können, um sie für spätere Berichte zu nutzen. | Should | Output |
| **US-A7** | Als Foresight-Analyst möchte ich die geladenen Agenten-Prompts vor dem Start im UI anpassen können, um Nuancen ohne JSON-Änderung zu testen. | Should | Setup |

### Rolle: Dozenten / Evaluatoren
*Diese Gruppe prüft die methodische Qualität und die logische Konsistenz der Simulation im Hinblick auf ein Forschungsprojekt.*

| ID | User Story | Priorität | Phase |
| :--- | :--- | :--- | :--- |
| **US-E1** | Als Evaluator möchte ich die final verwendeten System-Prompts transparent einsehen können, um deren Qualität zu bewerten. | Must | Evaluation |
| **US-E2** | Als Evaluator möchte ich den Log der Agenten lesen können, um auf logische Argumentation oder Halluzinationen zu prüfen. | Must | Evaluation |
| **US-E3** | Als Evaluator möchte ich nachvollziehen können, wie die CIB-Matrix generiert wird, um die methodische Quantifizierung zu validieren. | Must | Evaluation |
| **US-E4** | Als Forscher möchte ich in den Logs erkennen können, ob "emergentes Verhalten" (neue Argumente außerhalb des Prompts) stattfindet. | Could | Analyse |

### Rolle: Systementwickler (wir)
*Verantwortlich für Architektur, Stabilität und Modell-Integration.*

| ID | User Story | Priorität | Phase |
| :--- | :--- | :--- | :--- |
| **US-D1** | Als Systementwickler möchte ich jeden gesendeten Prompt und jede Antwort im Hintergrund loggen, um Fehlerursachen (Prompt vs. Modell) zu finden. | Must | Architektur |
| **US-D2** | Als Systementwickler möchte ich den Langgraph-State nach jedem Agenten-Zug zwischenspeichern, um bei Abstürzen dort fortfahren zu können. | Should | Architektur |
| **US-D3** | Als Systementwickler möchte ich das verwendete lokale Modell zentral in einer Config ändern können, um die Performance verschiedener LLMs zu testen. | Should | Setup |

---

## Nicht-funktionale Anforderungen (NFA)

| ID | Kategorie | Anforderung | Priorität |
|:---|:---|:---|:---:|
| **NFA-01** | **Nachvollziehbarkeit** | Das System muss durch Prompting und Systemgrenzen Halluzinationen minimieren. Ergebnisse müssen auf den Simulationsstand zurückführbar sein. | **Must** |
| **NFA-02** | **Reproduzierbarkeit** | Bei identischer Konfiguration und identischem LLM (Temperature = 0) soll die Simulation vergleichbare Ergebnisse liefern. | **Should** |
| **NFA-03** | **Konfigurierbarkeit** | Die Domäne (Akteure, Ziele) muss ausschließlich über Konfigurationsdateien anpassbar sein, ohne den Kerncode zu ändern. | **Must** |
| **NFA-04** | **Lokalität** | Das System muss vollständig lokal laufen können. | **Must** |
| **NFA-05** | **Dokumentation** | Alle Systemkomponenten und Nutzungsprozesse müssen in Markdown dokumentiert sein. | **Must** |
| **NFA-06** | **Modularität** | Das System muss modular aufgebaut sein (Trennung von LangGraph-Logik, Prompt-Management und Extraktion). | **Must** |
| **NFA-07** | **Performance** | Eine vollständige Simulationsrunde soll schnell durchlaufen können. | **Could** |
| **NFA-08** | **Transparenz** | Alle verwendeten Prompts und Entscheidungslogiken müssen für den Nutzer offenliegen. | **Should** |


---

## Abgrenzung (Out of Scope)

| ID | Aspekt | Begründung |
|:---|:---|:---|
| **OOS-01** | Grafische Benutzeroberfläche (GUI) | Prototyp; CLI/Konfigurationsdateien/Notebooks ausreichend |
| **OOS-02** | Qualitative Simulation | Fokus auf qualitative Simulation durch LLM-basierte Agenten |
| **OOS-03** | Mehrsprachigkeit | Prototyp arbeitet primär auf Deutsch oder Englisch |
| **OOS-04** | Mehrbenutzerbetrieb | Einzelplatz-Prototyp |
| **OOS-05** | Persistente Datenbank | Dateibasierte Speicherung (JSON/Markdown) ausreichend |