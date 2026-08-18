# Quellen der Modellannahmen

## Quellenpflichtige Stellen:
- **A: Demografie / Bevölkerung**
- **B: Konsumentenverhalten**
- **C: Preis- und Marktmodell**
- **D: Politikeffekte**
- **E: Dynamische Regeln**
---

## A: Demografie / Bevölkerung
### Bevölkerungsentwicklung
Zielbevölkerung pro Tick wird gesetzt und kann wachsen/schrumpfen.
- **`run_population_tick`**
- **`src/population_sampler.py`**

&rarr; Smith, S. K., Tayman, J., & Swanson, D. A. State and Local Population Projections: Methodology and Analysis <br>
- **Quelle:** Demografische Projektionen nutzen Zeitreihen-/Szenariofortschreibungen; in der Literatur meist als Populationsprojektion (P_{t+1}=P_t + B - D + M) oder als Szenarioverlauf beschrieben.
- **Modell:** Diskrete Fortführung der Zielpopulation pro Tick.<br>run_population_tick: target_population = int(system_properties.get("bevoelkerungsentwicklung", len(individuals)));<br>Bei Wachstum werden neue Individuen erzeugt, bei Schrumpfung zufällig entfernt.

### Segmentverschiebung
Bevölkerungsanteile verschieben sich je nach Regelwerk.<br>
Unterschiedliche Gruppen haben unterschiedliche Gewichtungen/Präferenzen
- **`apply_factor_shifts`**
- **`initialize_population`**

&rarr; Schelling, T. C. (1971). Dynamic Models of Segregation. Journal of Mathematical Sociology
<br>
&rarr; Bonabeau, E. (2002). Agent-based modeling: Methods and techniques for simulating human systems. Proceedings of the National Academy of Sciences, 99(Suppl 3)
- **Quelle:** Schelling (1971) zeigt, dass lokale Regeln zu makroskopischen Verschiebungen/Clusterbildung führen können;<br>Bonabeau (2002) beschreibt ABM als heterogene Agenten mit lokalen Regeln.
- **Modell:** Regelbasierte Veränderung von Gruppenanteilen und individuellen Merkmalen. <br> apply_factor_shifts verändert Merkmale wie Awareness, Preisempfindlichkeit und Einkommen abhängig von Faktoren/Systembedingungen.

### Verteilung der Merkmale
Alter, WTP, Substitution, Awareness werden aus Verteilungen gezogen.
- **`initialize_population`**

&rarr; Alter: Böcker, L., & Thøgersen, J. Arbeiten zu Reiseverhalten und soziodemografischen Einflussfaktoren
oder allgemeiner Reiseverhaltensliteratur mit Altersunterschieden
<br>
&rarr; WTP: Train, K. E. (2009). Discrete Choice Methods with Simulation
<br>
&rarr; Substitution: Ben-Akiva, M., & Lerman, S. R. (1985). Discrete Choice Analysis: Theory and Application to Travel Demand

- **Quelle:** Train (2009): Random-Utility-/Choice-Modelle arbeiten mit heterogenen Präferenzverteilungen; typischerweise Normal-, Lognormal- oder andere Verteilungen für WTP/Parameter.
- **Modell:** Heterogene Individuen mit sampled WTP, Alter, Substitution, Awareness.<br> initialize_population sampled awareness teils Beta/Normal/Uniform, wtp Normal/Lognormal, age Normal/Lognormal/Uniform, substitution_readiness Beta/Normal/Uniform.
---

## B: Konsumentenverhalten
### Zahlungsbereitschaft
WTP wird individuell sampled und bestimmt Kaufentscheidung mit.
Green_premium erhöht effektive Zahlungsbereitschaft.
- **`initialize_population`**
- **`population_sampler.py`**
- **`_booking_probability`**

&rarr; Train, K. E. (2009). Discrete Choice Methods with Simulation. Cambridge University Press
<br>
&rarr; Hensher, D. A., Rose, J. M., & Greene, W. H. (2005/2015). Arbeiten zu Willingness-to-Pay und Choice Modelling
- **Quelle:** WTP wird in Choice-Modellen als monetäre Zahlungsbereitschaft bzw. Nutzenäquivalent verwendet; oft als Verteilungsparameter geschätzt, nicht als fester Wert.
- **Modell:** WTP als individuelle Schwelle bzw. Teil der Erschwinglichkeitsprüfung.<br> affordability_limit = wtp_eur * income_factor * (1.0 + green_premium * environmental_awareness)

### Preiselastizität
Ticketpreis wirkt direkt auf Buchungswahrscheinlichkeit.
- **`_booking_probability`**
- **`compute_demand.py`**

&rarr; Ben-Akiva, M., & Lerman, S. R. (1985). Discrete Choice Analysis: Theory and Application to Travel Demand
<br>
&rarr; Graham, A. (2013). Arbeiten zur Preiselastizität im Luftverkehr
- **Quelle:** In Nachfrage-/Choice-Modellen häufig als ε = definiert.<br>In diskreten Modellen als Preis-Term im Nutzen.
- **Modell:** Preis wirkt als negativer Term auf Nutzen und Nachfrage. <br>_booking_probability: price_penalty = person.price_sensitivity * (ticket_price/100); compute_demand: price_effect = 1.0 - price_elasticity * price_delta

### Substitutionsbereitschaft
Personen reagieren unterschiedlich stark auf Preisänderungen und Alternativen.
- **`_initialize_population`**
- **`_booking_probability.py`**

&rarr; Ben-Akiva, M., & Lerman, S. R. (1985). Discrete Choice Analysis
<br>
&rarr; McFadden, D. (1974). Conditional logit analysis of qualitative choice behavior
- **Quelle:** In der diskreten Wahltheorie entstehen Substitutionseffekte aus relativen Nutzenunterschieden; keine Standard-Einheitsformel, sondern modellabhängig.
- **Modell:** Ein individueller Substitutions-Term im Nutzen. <br>_booking_probability: substitution_penalty = person.substitution_readiness * normalized_price * 1.5

### Umweltbewusstsein
Höheres Umweltbewusstsein verändert Buchung und Wirkung von CO₂-Preisen.
- **`_booking_probability`**
- **`apply_factor_shifts`**

&rarr; Bamberg, S., Ajzen, I., & Schmidt, P. (2003). Choice of travel mode in the Theory of Planned Behavior
<br>
&rarr; Lanzini, P., & Khan, S. A. (2017). Arbeiten zu environmental attitudes and travel mode choice
- **Quelle:** Literatur modelliert Umweltbewusstsein meist als latenten Präferenz- oder Einstellungsfaktor; keine universelle Formel.
- **Modell:** Verstärkt oder verändert Preis-/CO₂-Reaktion.<br> _booking_probability: eco_penalty = person.environmental_awareness * normalized_tax; bei hoher Preis-Sensitivität zusätzlicher Bonus-/Penalty-Term.

### Logit-/Diskretwahlmodell
Buchungswahrscheinlichkeit basiert auf logistischer Nutzenfunktion.
- **`_booking_probability`**

&rarr; McFadden, D. (1974). Conditional logit analysis of qualitative choice behavior
- **Quelle:** McFadden-Logit: (P_i=\frac{e^{V_i}}{\sum_j e^{V_j}}); bei binärer Wahl häufig (P=1/(1+e^{-U})).
- **Modell:** Binäre Buchungswahrscheinlichkeit aus Nutzen. <br> probability = 1.0 / (1.0 + np.exp(-utility)); Entscheidung bei probability >= logit_threshold.

### Sättigung / Wiederholungseffekte
Buchung erhöht Sättigungslevel und beeinflusst spätere Buchung.
- **`evaluate_booking`**
- **`apply_factor_shifts`**

&rarr; Simonson, I. (1992). Arbeiten zu satiation / variety-seeking in consumer choice
<br>
&rarr; McAlister, L., & Pessemier, E. (1982). Variety seeking behavior: An interdisciplinary review
<br>
&rarr; Hui, S. K., & Bateson, J. E. G. Arbeiten zu saturation/habituation im Kaufverhalten
- **Quelle:** Satiation/Variety seeking wird in der Literatur meist als abnehmender Grenznutzen oder habituelle Dynamik beschrieben.
- **Modell:** Sättigung als Penalty und zeitlicher Abbau.<br>saturation_level steigt bei Buchung um booking_increase und sinkt pro Tick um get_decay_rate(...); wird als saturation_penalty im Nutzen verwendet.

### Alterswirkung
Alter wird als Merkmal in der Population geführt und kann Verhalten beeinflussen.
- **`_initialize_population`**

&rarr; Böcker, L., & Thøgersen, J. Arbeiten zu soziodemografischen Determinanten von Mobilität/Reiseverhalten
<br>
&rarr; Ory, D. T., & Mokhtarian, P. L. Arbeiten zu travel behavior by age/life cycle
<br>
&rarr; Mokhtarian, P. L., et al. zu age and travel demand
- **Quelle:** Alter wird empirisch als erklärende Variable in Mobilitäts- und Nachfragemodellen genutzt, meist ohne universelle Formel.
- **Modell:** Alter als individuelles Merkmal und Gruppierungsvariable.<br> age wird sampled und später in aggregate_population_stats in Altersgruppen ausgewertet
---

## C: Preis- und Marktmodell
### Kostenindex
Kosten werden zu einem Index verdichtet und treiben Preise.
- **`compute_cost_pressure`**
- **`update_cost_index`**

&rarr; Belobaba, P. P. Arbeiten zu Airline Revenue Management und Kosten-/Ertragssteuerung
<br>
&rarr; Doganis, R. (2019). Flying Off Course: The Economics of International Airlines
<br>
&rarr; Borenstein, S., & Rose, N. Arbeiten zu Airline economics / cost structure
- **Quelle:** Kostenmodelle im Luftverkehr nutzen Inputkosten, Treibstoffpreise, Gebühren und operative Kosten; häufig als Index oder Kostenkomponente.
- **Modell:** Kostenentwicklung als Index, der den Preis treibt. <br> update_cost_index / compute_cost_pressure bilden Kosten- und Druckkomponenten pro Tick ab.

### Markup
Startmarge wird gesetzt und beeinflusst Ticketpreis.
- **`initial_provider_markup`**
- **`compose_ticket_price`**

&rarr; Phillips, R. L. (2005). Pricing and Revenue Optimization
<br>
&rarr; Talluri, K. T., & van Ryzin, G. (2004). The Theory and Practice of Revenue Management
<br>
&rarr; Belobaba, P. P. Revenue-management-Literatur
- **Quelle:** Pricing-/Revenue-Management-Literatur arbeitet mit Preis = Kosten + Marge.
- **Modell:** Markup als expliziter Preisaufschlag. <br> compose_ticket_price(cost_pressure, markup, ...) und initial_provider_markup(properties)

### Ticketpreisbildung
Preis wird aus Kosten + Markup + weiteren Komponenten gebildet.
- **`compose_ticket_price`**

&rarr; Phillips, R. L. (2005). Pricing and Revenue Optimization
<br>
&rarr; Talluri, K. T., & van Ryzin, G. (2004). The Theory and Practice of Revenue Management
<br>
&rarr; Doganis (2019). Flying Off Course
- **Quelle:** Standardformel im Pricing: (p = c + m) bzw. mit Zusatzkomponenten.
- **Modell:** Aus Kosten und Markup zusammengesetzter Ticketpreis. <br> Sichtbarer Preis wird aus Kostenbasis und Markup berechnet; danach ggf. begrenzt/angepasst.

### Yield-Feedback / Revenue Management
Preis wird anhand Booking Rate vs. Target Booking Rate angepasst.
- **`apply_market_feedback`**

&rarr; Belobaba, P. P. (1987/1989/weiterführend). Arbeiten zu airline yield management
<br>
&rarr; Talluri & van Ryzin (2004). Revenue Management
<br>
&rarr; McGill, J. I., & van Ryzin, G. J. (1999). Revenue Management: Research Overview and Prospects
- **Quelle:** Revenue Management nutzt Nachfrage-/Booking-Feedback zur Anpassung von Preisen/Margen.
- **Modell:** Gedämpfte Rückkopplung auf Basis der Buchungsrate. <br> gap = booking_rate - target_booking_rate; markup_delta = damping * gap * markup_adjustment_per_tick * max(previous_markup, scale * margin_reference_fraction)

### Ziel-Buchungsrate / Auslastung
Es gibt eine Ziel-Buchungsrate als Steuerparameter.
- **`MarketFeedbackConfig`**

&rarr; Belobaba, P. P. (1987/1989/weiterführend). Arbeiten zu airline yield management
<br>
&rarr; Talluri & van Ryzin (2004). Revenue Management
<br>
&rarr; McGill, J. I., & van Ryzin, G. J. (1999). Revenue Management: Research Overview and Prospects
- **Quelle:** Zielwerte im Revenue Management sind typischerweise Load-Factor-/Booking-Targets; die Literatur gibt Konzepte, aber meist keinen universellen Wert.
- **Modell:** Ziel-Buchungsrate als Steuerparameter. <br> target_booking_rate = 0.37 in eurer Konfiguration/Implementierung.

### Dämpfung / Anpassungsrate
Preisänderungen werden geglättet und begrenzt.
- **`apply_market_feedback`**

&rarr; Talluri & van Ryzin (2004). Revenue Management
- **Quelle:** Dynamische Steuerung nutzt oft einen Dämpfungsfaktor (0<\lambda<1), um Überreaktionen zu verhindern.
- **Modell:** Skalierung der Feedbackstärke. <br> damping = 0.85, markup_adjustment_per_tick = 0.08
- 
### Mindespreis
Preis darf nicht unter Grenzkosten + Steuern/Gebühren fallen.
- **`apply_market_feedback`**

&rarr; Doganis (2019). Flying Off Course
<br>
&rarr; Phillips (2005). Pricing and Revenue Optimization
<br>
&rarr; Varian, H. R. Arbeiten zu pricing and cost floors / economic pricing
- **Quelle:** Preisuntergrenzen werden oft als Grenzkosten/Marginal Cost Floors interpretiert.
- **Modell:** Kein Preis unter den Kosten + Abgaben. <br> marginal_cost = cost_pressure * config.marginal_cost_fraction; floor_price = compose_ticket_price(marginal_cost, 0.0, ...); raw_price = max(raw_price, floor_price)

### Margen-Referenz
Preis passt sich an Referenzmargen an.
- **`apply_market_feedback`**

&rarr; Belobaba, P. P. (1987/1989/weiterführend). Arbeiten zu airline yield management
<br>
&rarr; Talluri & van Ryzin (2004). Revenue Management
<br>
&rarr; Phillips (2005). Pricing and Revenue Optimization
- **Quelle:** Margin management nutzt Referenzmargen oder Zielmargen; konkrete Formeln sind modellabhängig.
- **Modell:** Referenzierte Untergrenze für Markup-Anpassung. <br> margin_reference_fraction und margin_floor_fraction bestimmen die Mindestmarge bzw. Referenz.

---

## D: Politikeffekte
### CO₂-Preis-Effekt
CO₂-Steuer beeinflusst Buchungswahrscheinlichkeit direkt.
- **`_booking_probability`**
- **`evaluate_booking`**

&rarr; Sterner, T. (2007). Fuel taxes: An important instrument for climate policy 
<br>
&rarr; Parry, I. W. H., & Small, K. A. (2005). Does Britain or the United States have the right gasoline tax?
<br>
&rarr; Gillingham, K., & Stock, J. H. (2018). Arbeiten zu carbon pricing and emissions reductions
- **Quelle:** Carbon pricing wird oft als zusätzlicher Preis-/Kostenfaktor modelliert; Effekte hängen vom Steuersatz und der Sensitivität ab.
- **Modell:** Carbon tax als zusätzlicher Strafterm im Entscheidungsnutzen. <br>excess_carbon = max(0.0, carbon_tax - DEFAULT_CARBON_ECO_BASELINE); daraus eco_penalty.

### Grundlage für CO₂-Effekt
Es gibt einen Schwellenwert/Baseline, ab dem der CO₂-Effekt greift.
- **`DEFAULT_CARBON_ECO_BASELINE`**

&rarr; Nordhaus, W. (1991/2017). Arbeiten zur Klimapolitik und CO₂-Bepreisung
<br>
&rarr; IPCC-Berichte
- **Quelle:** Literatur nutzt oft Referenz- oder Schwellenwerte, um policy impact zu definieren.
- **Modell:** Schwellenwert, ab dem CO₂-Effekte wirken. <br>DEFAULT_CARBON_ECO_BASELINE = 50.0; erst oberhalb davon greift der eco_penalty voll.

### Policy-Sensitivität
CO₂-Preis wirkt stärker auf umweltbewusste oder preissensitive Personen.
- **`_booking_probability`**
- **`apply_factor_shifts`**

&rarr; Bamberg, S., Ajzen, I., & Schmidt, P. (2003)
<br>
&rarr; Lanzini, P., & Khan, S. A. (2017)
<br>
&rarr; Heffner, R. K., et al. Arbeiten zu environmental attitudes and transport choice
- **Quelle:** Policy-Reaktionen werden häufig durch Einstellungen/Normen moderiert; keine einheitliche Formel.
- **Modell:** Verstärkung von CO₂-Effekt durch Awareness/Preis-Sensitivität.<br> Bei hoher price_sensitivity addiert ihr einen extra Penalty-Term: HIGH_PRICE_SENSITIVITY_PENALTY * min(1.0, normalized_tax).

### Regelbasierte Reaktionen auf Faktoren
Externe Faktoren lösen Zustandsänderungen aus.
- **`apply_factor_shifts`**

&rarr; Bonabeau (2002) – ABM-Grundlagen
<br>
&rarr; Schelling (1971) – lokale Regeln, emergente Muster
<br>
&rarr; Macy & Willer (2002). From factors to actors: Computational sociology and agent-based modeling
- **Quelle:** ABM-Literatur beschreibt Zustandsübergänge über if/then-Regeln und lokale Interaktionen.
- **Modell:** System-/Faktoränderungen als bedingte Regelwerke. <br> apply_factor_shifts prüft when-Bedingungen (factor, system_property, above/below) und wendet delta-Effekte an.

### Systemische Einkommens-/Kostenänderungen
Externe Systemgrößen verändern Einkommen oder Sensitivität.
- **`apply_factor_shifts`**
- **`resolve_system_properties`**

&rarr; Mankiw / Makroökonomie-Grundlagen für Einkommenseffekte
- **Quelle:** Income effects werden oft als multiplicative Skalierung oder Indexveränderung modelliert.
- **Modell:** Einkommen verändert die individuelle Einkommenskomponente. <br> update_income_factors: income_factor = base_income_factor * income_index

### Green premium / Nachhaltigkeitsprämie
Nachhaltigkeit erhöht effektive Zahlungsbereitschaft.
- **`_booking_probability`**

&rarr; Roe, B., Teisl, M. F., Levy, A., & Russell, M. (2001).
<br>
&rarr; Michaud, C., Llerena, D., & Joly, I. Arbeiten zu green products willingness to pay
<br>
&rarr; Nielsen, K. S., & andere Arbeiten zu sustainable consumer behavior
- **Quelle:** Literatur zu nachhaltigen Produkten zeigt häufig eine Zahlungsbereitschaftsprämie.
- **Modell:** Nachhaltigkeit erhöht die effektive WTP. <br> affordability_limit = wtp_eur * income_factor * (1.0 + green_premium * environmental_awareness) mit green_premium = 0.1.

---

## E: Dynamische Regeln
### Faktor-/ Regelverschiebungen
Faktoren ändern sich durch Regelbedingungen.
- **`apply_factor_shifts`**

&rarr; Bonabeau, E. (2002). Agent-based modeling: Methods and techniques for simulating human systems
<br>
&rarr; Macy, M. W., & Willer, R. (2002). From factors to actors: Computational sociology and agent-based modeling
- **Quelle:** ABM- und Computational-Sociology-Literatur modelliert Zustandsübergänge als regelbasiert und dynamisch.
- **Modell:** Bedingungen lösen Veränderung von Personenmerkmalen aus. <br> apply_factor_shifts verändert environmental_awareness, price_sensitivity, base_income_factor abhängig von aktiven Regeln.

### Sättigungszunahme
Buchung erhöht den Sättigungslevel.
- **`evaluate_booking`**

&rarr; McAlister, L., & Pessemier, E. A. (1982). Variety seeking behavior: An interdisciplinary review
<br>
&rarr; Simonson, I. (1992). Arbeiten zu variety seeking und satiation
<br>
&rarr; Bawa, K. Arbeiten zu repeat purchase / satiation
- **Quelle:** Satiation/Variety-Seeking wird oft als kumulativer Abnutzungseffekt oder sinkender Grenznutzen beschrieben.
- **Modell:** Buchung erhöht Sättigung direkt um einen fixen Wert. <br> booking_increase = 0.6 und bei Buchung saturation_level = min(1.0, person.saturation_level + booking_increase)

### Sättigungsdecay
Sättigung sinkt pro Tick.
- **`run_population_tick`**

&rarr;  Liang, X. & Hong, C. & Chen, J. & Wang, Y. & Yang, M. (2024). A hybrid forecasting architecture for air passenger demand considering search engine data and spatial effect. Journal of Air Transport Management
- **Quelle:** Habituation/Decay wird häufig als zeitlicher Abbau modelliert.
- **Modell:** Sättigung sinkt pro Tick um einen Segmentwert. <br> get_decay_rate(...) liest prop.saturation_decay aus den Segmenten; Standardfallback ist 0.2.

### Persistente Individuen
Dieselben Personen werden über Ticks fortgeführt.
- **`run_population_tick`**

&rarr; Bonabeau, E. (2002). Agent-based modeling: Methods and techniques for simulating human systems
- **Quelle:** Mikrosimulation/ABM arbeitet mit langfristig verfolgten Individuen statt neuem Sample pro Zeitschritt.
- **Modell:** Gleiche Personen bleiben über Ticks erhalten. <br> run_population_tick arbeitet mit existierenden individuals weiter und ändert sie tickweise statt jedes Mal neu zu sampeln.

### Regelabhängige Zustandslogik
Bedingungen prüfen Faktoren und Systemwerte vor Shift.
- **`_rule_matches`**

&rarr; Bonabeau, E. (2002). Agent-based modeling: Methods and techniques for simulating human systems
<br>
&rarr; Macy, M. W., & Willer, R. (2002). From factors to actors: Computational sociology and agent-based modeling
<br>
&rarr; Gilbert & Troitzsch (1999) Simulation for the Social Scientist
- **Quelle:** Zustandsänderungen hängen von vorherigen Zuständen und aktuellen Bedingungen ab.
- **Modell:** Regeln werden nur angewandt, wenn Faktoren/Systemwerte passen. <br> _rule_matches prüft factor- und system_property-Bedingungen vor der Anwendung von Shift-Regeln.