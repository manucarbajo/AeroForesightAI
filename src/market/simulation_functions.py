"""Deterministic simulation functions for market and policy metrics.

All numeric values for price, tax, SAF, and demand are computed here,
never parsed from LLM output.
"""

from __future__ import annotations

from collections.abc import Mapping

from src.market.market_feedback import (
    initial_provider_markup,
    resolve_market_feedback_config,
    zielauslastung,
)
from src.market.property_engine import (
    MARKET_PROPERTY_IDS,
    resolve_exogenous_system_properties,
    resolve_trajectory,
)
from src.models.property_models import (
    MarketFeedbackConfig,
    PriceCoefficientsConfig,
    PriceModelConfig,
    PropertiesConfig,
)
from src.models.state_models import FactorState
from src.rule_engine import KNOWN_METRICS, RuleContext, rule_matches

METRIC_IDS = MARKET_PROPERTY_IDS


def active_parameters(tick: int, properties: PropertiesConfig) -> dict[str, float]:
    """Return active exogenous system property values for one tick."""
    return resolve_exogenous_system_properties(tick, properties)


def compose_ticket_price(
    cost_pressure: float,
    provider_markup: float,
    *,
    properties: PropertiesConfig | None,
    tick: int,
) -> float:
    """published ticket price from cost layer + runtime margin property.

    Custom taxes (percentage on base) and fees (absolute surcharges) defined
    via ``price_component_type`` on system properties are applied here:
        final = (base) * (1 + sum_of_tax_rates) + sum_of_absolute_fees

    *properties* und *tick* sind **Pflicht** — dieselbe Regel wie bei
    `compute_cost_pressure` (P0.7). Beide hatten Defaults, und beide verschoben
    das Ergebnis still: ohne *properties* fielen Steuern und Gebühren ganz weg,
    und ``tick=0`` löste die Trajektorien vor ihrem ersten definierten Tick auf.
    Wer wirklich nur die Kostenschicht will, schreibt ``properties=None`` —
    eine Aussage statt eines Versehens.
    """
    base = cost_pressure + max(0.0, provider_markup)

    if properties is None:
        return base

    params = active_parameters(tick, properties)
    total_tax_rate = 0.0
    total_fees = 0.0
    for sp in properties.system_properties:
        if sp.price_component_type == "tax":
            total_tax_rate += params.get(sp.id, 0.0)
        elif sp.price_component_type == "fee":
            total_fees += params.get(sp.id, 0.0)

    return base * (1.0 + total_tax_rate) + total_fees


def compute_ticket_price(
    base_price: float,
    carbon_tax: float,
    fuel_price_change: float,
    oil_index: float,
    saf_share: float,
    efuel_subsidy: float,
    *,
    coefficients: PriceCoefficientsConfig | None = None,
) -> float:
    """Compute ticket cost from base price and policy parameters (coefficients from config)."""
    coeffs = coefficients or PriceCoefficientsConfig()

    fuel_factor = 1.0 + fuel_price_change

    oil_factor = oil_index

    carbon_surcharge = carbon_tax * coeffs.carbon_per_tonne

    saf_premium = saf_share * coeffs.saf_premium_factor

    subsidy_offset = efuel_subsidy * saf_share

    price = base_price * fuel_factor * oil_factor + carbon_surcharge + saf_premium - subsidy_offset

    return max(coeffs.min_ticket_price, price)


def update_cost_index(previous_index: float, fuel_price_change: float) -> float:
    """accumulate fuel inflation on cost layer (not on prior ticket price)."""
    return max(0.1, previous_index * (1.0 + fuel_price_change))


def compute_cost_pressure(
    tick: int,
    properties: PropertiesConfig,
    *,
    price_model: PriceModelConfig | None = None,
    cost_index: float = 1.0,
    factors: Mapping[str, FactorState],
    system_properties: Mapping[str, float],
) -> float:
    """Kostenanteil aus ``price_model.base_price``, nicht aus dem Vortickpreis.

    *factors* und *system_properties* sind seit P0.7 **Pflicht**. Sie waren
    optional und fielen auf ``None`` zurück — was bedeutete: kein Faktor steht
    in irgendeinem Zustand, also greift kein bedingter Kostentreiber. Wer sie
    vergaß, bekam still eine andere Zahl. Genau das ist im `environment_node`
    passiert, und der dortige Wert ist die Größe, gegen die die F4-Regeln
    schwellen. Ein Aufrufer, der wirklich keine Faktoren hat, sagt das jetzt
    mit ``factors={}`` — eine Aussage statt eines Versehens.
    """
    model = price_model or properties.price_model

    params = active_parameters(tick, properties)

    effective_base = model.base_price * cost_index

    fuel_change = 0.0 if model.compound_fuel_on_cost else params.get("fuel_price_change", 0.0)

    base_cost = compute_ticket_price(
        base_price=effective_base,
        carbon_tax=params.get("carbon_tax_level", 0.0),
        fuel_price_change=fuel_change,
        oil_index=params.get("oil_price_index", 1.0),
        saf_share=params.get("saf_mandate_share", 0.0),
        efuel_subsidy=params.get("efuel_subsidy", 0.0),
        coefficients=model.coefficients,
    )

    regulatory_cost = 0.0
    factors_dict = factors
    sys_props = system_properties

    # Bis P0.4 stand hier ein dritter, eigener Evaluator — mit per ``elif``
    # verketteten Vergleichen, weshalb ``below`` neben ``above`` nie geprüft
    # wurde. Die Kostentreiber laufen jetzt über dieselbe Auswertung wie
    # Faktor- und Shift-Regeln. Anders als dort ist eine leere Klausel hier
    # zulässig: ein Kostentreiber darf unbedingt gelten.
    context = RuleContext(
        tick=tick,
        factors=factors_dict,
        metrics={name: None for name in KNOWN_METRICS} | {"tick": float(tick)},
        system_properties=sys_props,
    )

    for reg in properties.regulatory_influences:
        if not rule_matches(reg.when, context, rule_id=reg.id):
            continue
        traj_val = resolve_trajectory(reg.trajectory, tick)
        regulatory_cost += reg.cost_contribution + traj_val

    maintenance_idx = sys_props.get("maintenance_cost_index", 1.0)
    staff_idx = sys_props.get("staff_cost_index", 1.0)
    adjusted_base_cost = base_cost * maintenance_idx * staff_idx
    return adjusted_base_cost + regulatory_cost


def clip_price_change(
    new_price: float,
    previous_price: float,
    max_fraction: float,
) -> float:
    """limit per-tick price delta (numerical stability)."""
    if previous_price <= 0:
        return max(1.0, new_price)

    max_delta = previous_price * max_fraction

    delta = new_price - previous_price

    if abs(delta) <= max_delta:
        return max(1.0, new_price)

    return max(1.0, previous_price + max(-max_delta, min(max_delta, delta)))


def apply_market_feedback(
    cost_pressure: float,
    booking_rate: float,
    previous_markup: float,
    previous_ticket_price: float,
    config: MarketFeedbackConfig,
    *,
    coefficients: PriceCoefficientsConfig | None = None,
    properties: PropertiesConfig | None,
    tick: int,
) -> tuple[float, float]:
    """adjust provider_markup from observed booking rate vs target."""
    coeffs = coefficients or PriceCoefficientsConfig()

    if not config.enabled:

        markup = max(0.0, previous_markup)

        price = clip_price_change(
            compose_ticket_price(cost_pressure, markup, properties=properties, tick=tick),
            previous_ticket_price,
            config.max_price_change_fraction,
        )

        return price, max(0.0, price - cost_pressure)

    gap = booking_rate - config.target_booking_rate

    anchor = (
        previous_ticket_price
        if previous_ticket_price > 0
        else compose_ticket_price(cost_pressure, previous_markup, properties=properties, tick=tick)
    )

    scale = max(cost_pressure, 1.0)

    markup_delta = (
        config.damping
        * gap
        * config.markup_adjustment_per_tick
        * max(previous_markup, scale * coeffs.margin_reference_fraction)
    )

    markup_path_price = compose_ticket_price(
        cost_pressure, max(0.0, previous_markup + markup_delta), properties=properties, tick=tick
    )

    yield_multiplier = 1.0 + config.damping * gap * config.markup_adjustment_per_tick

    yield_path_price = anchor * yield_multiplier

    raw_price = (
        min(markup_path_price, yield_path_price)
        if gap < 0
        else max(markup_path_price, yield_path_price)
    )

    if booking_rate >= config.target_booking_rate * coeffs.target_booking_tolerance:

        target_margin = (
            max(coeffs.margin_floor_fraction, previous_markup / scale)
            if scale > 0
            else coeffs.margin_reference_fraction
        )

        raw_price = max(raw_price, cost_pressure * (1.0 + target_margin))

    # Hard Floor (Die Rote Linie): Der Preis darf niemals unter die Grenzkosten + Steuern + Gebühren fallen.
    # Das erlaubt Loss-Leading zur Deckung von Fixkosten, verbietet aber Dumping unter die echten Grenzkosten.
    marginal_cost = cost_pressure * config.marginal_cost_fraction
    floor_price = compose_ticket_price(marginal_cost, 0.0, properties=properties, tick=tick)
    raw_price = max(raw_price, floor_price)

    new_price = clip_price_change(raw_price, anchor, config.max_price_change_fraction)

    params = active_parameters(tick, properties) if properties else {}
    total_tax_rate = (
        sum(
            params.get(sp.id, 0.0)
            for sp in properties.system_properties
            if sp.price_component_type == "tax"
        )
        if properties
        else 0.0
    )
    total_fees = (
        sum(
            params.get(sp.id, 0.0)
            for sp in properties.system_properties
            if sp.price_component_type == "fee"
        )
        if properties
        else 0.0
    )

    base_price_no_tax = (new_price - total_fees) / max(1e-6, 1.0 + total_tax_rate)
    new_markup = max(0.0, base_price_no_tax - cost_pressure)

    return new_price, new_markup


def sync_demand_level(
    booking_rate: float,
    previous_demand: float,
    growth_rate: float,
    *,
    target_booking_rate: float = 0.75,
    booking_weight: float = 0.6,
) -> float:
    """couple macro demand index to observed micro booking rate."""
    macro = previous_demand * (1.0 + growth_rate)

    if target_booking_rate > 0:

        booking_component = booking_rate / target_booking_rate

    else:

        booking_component = booking_rate

    booking_component = max(0.0, min(2.0, booking_component))

    demand = (1.0 - booking_weight) * macro + booking_weight * booking_component

    return max(0.0, min(2.0, demand))


def compute_demand(
    base_demand: float,
    growth_rate: float,
    price_elasticity: float,
    price_delta: float,
) -> float:
    """Compute demand level from base demand, growth, and price effect."""
    growth_factor = 1.0 + growth_rate

    price_effect = 1.0 - price_elasticity * price_delta

    demand = base_demand * growth_factor * price_effect

    return max(0.0, min(2.0, demand))


def _runtime_markup(
    properties: PropertiesConfig, previous_markup: float | None, *, tick: int
) -> float:

    if previous_markup is not None:

        return previous_markup

    return initial_provider_markup(properties, tick=tick)


def compute_market_metrics(
    tick: int,
    properties: PropertiesConfig,
    *,
    previous_price: float,
    base_price: float = 100.0,
    previous_demand: float = 1.0,
    previous_markup: float | None = None,
    previous_cost_index: float = 1.0,
    booking_rate: float | None = None,
    price_elasticity: float = 0.5,
    factors: Mapping[str, FactorState],
    system_properties: Mapping[str, float],
) -> dict[str, float]:
    """Deterministische Marktkennzahlen für einen Tick (M4-aware).

    *factors* und *system_properties* sind seit P0.7 Pflicht, aus demselben
    Grund wie bei `compute_cost_pressure`: Sie werden dorthin durchgereicht,
    und ein vergessenes Argument liefert still eine Zahl ohne die bedingten
    Kostentreiber. Der Vorschau-Zweig in `agent_node` hat auf diesem Weg dem
    Agenten im ersten Tick einen falschen Kostendruck gezeigt.
    """
    params = active_parameters(tick, properties)

    price_model = properties.price_model

    feedback = resolve_market_feedback_config(properties)

    # **Die Zielauslastung folgt der Kapazität** (P2.8, 2026-08-31). Hier und
    # nicht in `apply_market_feedback`, weil `system_properties` genau hier
    # schon vorliegt — ein zusätzlicher Kontextparameter weiter unten müsste
    # sonst durchgereicht werden, mit allem, was Invariante 1 dazu sagt.
    #
    # **Vor beiden Verwendern**, damit `apply_market_feedback` und
    # `sync_demand_level` denselben Sollwert sehen. Getrennt gesetzt liefen sie
    # auseinander, und das Nachfrageniveau folgte einem anderen Ziel als der
    # Preis.
    feedback = feedback.model_copy(
        update={"target_booking_rate": zielauslastung(feedback, system_properties)}
    )

    coefficients = price_model.coefficients

    anchor_price = previous_price if previous_price > 0 else base_price

    provider_markup = _runtime_markup(properties, previous_markup, tick=tick)

    fuel_change = params.get("fuel_price_change", 0.0)

    if price_model.compound_fuel_on_cost:

        cost_index = update_cost_index(previous_cost_index, fuel_change)

    else:

        cost_index = previous_cost_index

    cost_pressure = compute_cost_pressure(
        tick,
        properties,
        cost_index=cost_index,
        factors=factors,
        system_properties=system_properties,
    )

    # **Unter `marge` regelt der Anbieter nicht nach** (P2.8-B): Er hält seinen
    # Aufschlag, und die Auslastung schwankt. Damit bleibt der Preis gleich,
    # wenn Kapazität dazukommt — die reale Lage 2015–2019, die unter der
    # Auslastungsstrategie nicht darstellbar ist.
    regelt_nach = feedback.enabled and feedback.strategie == "auslastung"

    if booking_rate is not None and regelt_nach:

        ticket_price, provider_markup = apply_market_feedback(
            cost_pressure,
            booking_rate,
            provider_markup,
            anchor_price,
            feedback,
            coefficients=coefficients,
            properties=properties,
            tick=tick,
        )

        demand_level = sync_demand_level(
            booking_rate,
            previous_demand,
            params.get("demand_growth_rate", 0.0),
            target_booking_rate=feedback.target_booking_rate,
            booking_weight=feedback.booking_weight,
        )

    else:

        ticket_price = compose_ticket_price(
            cost_pressure, provider_markup, properties=properties, tick=tick
        )

        ticket_price = clip_price_change(
            ticket_price, anchor_price, feedback.max_price_change_fraction
        )

        total_tax_rate = (
            sum(
                params.get(sp.id, 0.0)
                for sp in properties.system_properties
                if sp.price_component_type == "tax"
            )
            if properties
            else 0.0
        )
        total_fees = (
            sum(
                params.get(sp.id, 0.0)
                for sp in properties.system_properties
                if sp.price_component_type == "fee"
            )
            if properties
            else 0.0
        )
        base_price_no_tax = (ticket_price - total_fees) / max(1e-6, 1.0 + total_tax_rate)

        provider_markup = max(0.0, base_price_no_tax - cost_pressure)

        price_delta = (ticket_price - anchor_price) / anchor_price if anchor_price > 0 else 0.0

        demand_level = compute_demand(
            base_demand=previous_demand,
            growth_rate=params.get("demand_growth_rate", 0.0),
            price_elasticity=price_elasticity,
            price_delta=price_delta,
        )

    return {
        "carbon_tax_level": params.get("carbon_tax_level", 0.0),
        "fuel_price_change": params.get("fuel_price_change", 0.0),
        "oil_price_index": params.get("oil_price_index", 1.0),
        "saf_mandate_share": params.get("saf_mandate_share", 0.0),
        "efuel_subsidy": params.get("efuel_subsidy", 0.0),
        "demand_growth_rate": params.get("demand_growth_rate", 0.0),
        "cost_pressure": cost_pressure,
        "cost_index": cost_index,
        "provider_markup": provider_markup,
        "markup": provider_markup,
        "demand_level": demand_level,
        "ticket_price": ticket_price,
        **({"booking_rate": booking_rate} if booking_rate is not None else {}),
    }
