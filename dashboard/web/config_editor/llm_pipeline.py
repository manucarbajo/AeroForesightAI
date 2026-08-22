"""Tab «LLM & Pipeline»: Modellwahl und die Schalter der Simulationspipeline."""

from __future__ import annotations

from dash import html

from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c


def layout(draft: dict) -> html.Div:
    return html.Div(
        [
            ui.section(
                "LLM",
                ui.card(
                    ui.grid(
                        html.Div(
                            [
                                c.check("Mock-LLM", "mock_llm", draft.get("mock_llm", True)),
                                c.check(
                                    "Deterministisch (ohne Agenten-LLM)",
                                    "deterministic_only",
                                    draft.get("deterministic_only", False),
                                ),
                            ],
                            className="space-y-1",
                        ),
                        html.Div(),
                        c.text("Ollama-Modell", "model", draft.get("model", "llama3.2")),
                        c.text(
                            "Ollama Base-URL",
                            "base_url",
                            draft.get("base_url", "http://localhost:11434"),
                        ),
                        c.slider(
                            "Temperature",
                            "temperature",
                            float(draft.get("temperature", 0.7)),
                            min=0.0,
                            max=1.5,
                            step=0.05,
                        ),
                        c.number(
                            "Max Tokens",
                            "max_tokens",
                            int(draft.get("max_tokens", 2048)),
                            min=256,
                            max=8192,
                            step=1,
                        ),
                        cols="md:grid-cols-2",
                    )
                ),
                subtitle="Die Agenten liefern ausschließlich Narrative — Kennzahlen "
                "berechnet immer Python.",
            ),
            ui.section(
                "Pipeline",
                ui.card(
                    ui.grid(
                        c.check("Markt aus", "no_market", draft.get("no_market", False)),
                        c.check("Redebedarf-Modus", "redebedarf", draft.get("redebedarf", False)),
                        c.check("Kein Protocol", "no_protocol", draft.get("no_protocol", False)),
                        c.check(
                            "Keine Szenarien", "no_scenarios", draft.get("no_scenarios", False)
                        ),
                        cols="sm:grid-cols-2 lg:grid-cols-4",
                    ),
                    html.Div(
                        ui.grid(
                            c.number(
                                "Checkpoint alle N Ticks",
                                "checkpoint_interval",
                                int(draft.get("checkpoint_interval", 5)),
                                min=0,
                                step=1,
                            ),
                            c.text(
                                "Resume (Run-ID oder Pfad)",
                                "resume_from",
                                draft.get("resume_from", ""),
                            ),
                            cols="md:grid-cols-2",
                        ),
                        className="mt-5",
                    ),
                    html.Div(
                        ui.grid(
                            c.check("Seed setzen", "use_seed", draft.get("use_seed", False)),
                            c.number(
                                "Seed",
                                "seed",
                                int(draft.get("seed") if draft.get("seed") is not None else 42),
                                min=0,
                                step=1,
                            ),
                            cols="sm:grid-cols-2",
                        ),
                        className="mt-5",
                    ),
                    html.Div(
                        c.check(
                            "Figures nach Lauf erzeugen",
                            "generate_figures",
                            draft.get("generate_figures", True),
                            hint="Speichert PNGs unter `outputs/<run_id>/figures/` und zeigt sie "
                            "im Tab «Figures» unter «PNG-Export».",
                        ),
                        className="mt-5",
                    ),
                ),
            ),
        ]
    )
