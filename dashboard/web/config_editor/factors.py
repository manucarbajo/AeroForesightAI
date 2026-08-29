"""Die Ausgangslage des Laufs: sieben Faktoren, eine Frage (P1.9-W3.3).

**Die Faktorlage gehört zum Experiment, nicht zum Modell.** Sie sagt, von
welcher Weltlage *dieser* Lauf ausgeht — angespannte Geopolitik oder ruhige,
strenge Regulierung oder milde. Zwei Läufe desselben Modells dürfen sich genau
darin unterscheiden; das ist der Zweck der Szenariotechnik. Die Systemgrößen
dahinter (CO₂-Abgabe, SAF-Quote, Ölpreis samt ihren Regeln) sind dagegen das
Modell und bleiben im Bereich «Modell».

Bis P1.9-W3.1 lagen beide zusammen im Schritt «Rahmenbedingungen»; mit dem
Umzug wanderte die Faktorlage mit ins Modell, wo sie nicht hingehört. W3.3 holt
sie zurück — als **ein** Schritt mit sieben Auswahlen, nicht als Formularwand.

**Der Schalter «Eigene Werte anwenden» ist mitgekommen**, und das war eine
Entscheidung über den Wortlaut des Pakets hinaus: Er entscheidet, ob die Auswahl
auf diesem Bildschirm überhaupt wirkt. Bliebe er im Modell-Bereich, zeigte
dieser Schritt sieben Auswahlfelder und daneben einen Hinweis, dass man
anderswo etwas einschalten muss, damit sie zählen — genau die Art
wirkungsloser Anzeige, gegen die dieses Paket angetreten ist.
"""

from __future__ import annotations

from dash import html

from dashboard.config_catalog import factor_options_from_file, load_config_file
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c


def _meta(factors_file: str) -> dict[str, dict]:
    """Namen und Leitfragen der Faktoren aus der Konfigurationsdatei holen."""

    try:
        payload = load_config_file(factors_file)
    except Exception:  # noqa: BLE001 - fehlende Datei darf den Schritt nicht sprengen
        return {}
    return {k: v for k, v in payload.items() if isinstance(v, dict) and v.get("name")}


def wirken_eigene_werte(draft: dict) -> bool:
    """Ob die Auswahl auf diesem Schritt überhaupt in den Lauf eingeht."""

    return bool(draft.get("apply_custom_overrides")) or draft.get("scenario_mode") == "custom"


def selects(draft: dict) -> html.Div:
    """Die sieben Auswahlfelder — eines je Faktor."""

    factors_file = draft.get("factors_file", "factors.json")
    options = factor_options_from_file(factors_file)
    if not options:
        return ui.alert("Keine Faktoren in der gewählten Datei gefunden.", "warning")

    meta = _meta(factors_file)
    states = draft.get("factor_states") or {}

    fields = []
    for factor_id in sorted(options):
        available = options[factor_id]
        keys = list(available.keys())
        current = states.get(factor_id) or (keys[0] if keys else None)
        info = meta.get(factor_id, {})
        fields.append(
            c.select(
                f"factor_states.{factor_id}",
                current,
                [{"label": available[key], "value": key} for key in keys],
                label=f"{factor_id} · {info.get('name', factor_id)}",
                hint=info.get("description") or None,
            )
        )

    # **Drei Spalten ab `xl`** (P1.9-W3.5): Sieben Auswahlen in zwei Spalten
    # sind vier Reihen, in drei Spalten drei. Tailwinds Haltepunkte messen das
    # Fenster und nicht die Spalte -- bei 1280 px greift `xl`, bei 1024 px
    # bleibt es bei zwei, und das ist richtig so: Dort ist die Inhaltsspalte
    # 696 px breit, und drei Auswahlfelder mit Leitfrage passen nicht hinein.
    children: list = [ui.grid(*fields, cols="lg:grid-cols-2 xl:grid-cols-3")]
    if factors_file != "factors.json":
        children.insert(
            0,
            html.Div(
                ui.button(
                    "Faktoren neu laden",
                    id=c.action_id("reload-factors"),
                    variant="secondary",
                    icon_name="refresh",
                ),
                className="mb-4",
            ),
        )
    return html.Div(children)


def layout(draft: dict) -> html.Div:
    """Der Schritt «Ausgangslage».

    Ein vorbereitetes Szenario bringt seine eigene Faktorlage mit und setzt sich
    hier durch — das steht als Hinweis dabei, statt sieben Auswahlfelder
    anzubieten, die im Lauf nichts bewirken.
    """

    aus_preset = draft.get("scenario_mode") == "sweep" and draft.get("sweep_id")

    return html.Div(
        [
            ui.section(
                None,
                ui.lede(
                    "Sieben Faktoren beschreiben die Welt, in der der Lauf startet — je "
                    "Faktor zwei mögliche Zustände. Aus ihrer Kombination bewertet die "
                    "CIB-Matrix später, ob die Ausgangslage in sich stimmig ist."
                ),
                (
                    ui.alert(
                        "Sie haben ein vorbereitetes Szenario gewählt. Es bringt seine eigene "
                        "Faktorlage mit und gilt unvermischt — die Auswahl hier wirkt in diesem "
                        "Lauf nicht. Über «Werte übernehmen und selbst anpassen» im ersten "
                        "Schritt können Sie von ihr ausgehen und dann selbst ändern.",
                        "info",
                        class_name="mb-4",
                    )
                    if aus_preset
                    else None
                ),
                ui.card(
                    # Der Schalter steht **vor** den Auswahlfeldern: Er
                    # entscheidet, ob sie überhaupt zählen.
                    c.check("apply_custom_overrides", wirken_eigene_werte(draft)),
                    html.Div(selects(draft), className="mt-5"),
                ),
                actions=ui.doc_link("faktoren-konzept"),
            )
        ]
    )
