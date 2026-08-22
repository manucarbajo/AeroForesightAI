"""Baut aus dashboard/landing.py eine statische Vergleichsseite.

landing.py rendert die alte Landingpage in Streamlit. Die Inhalte stecken dort
in Modul-Konstanten als HTML-Strings; nur das Layout-Gerüst (Spalten, Buttons)
kommt aus Streamlit. Wir lesen die Konstanten per AST aus, ohne das Modul zu
importieren (es würde streamlit brauchen), und setzen das Gerüst aus
render_landing() statisch nach.
"""

from __future__ import annotations

import ast
import io
import sys
from pathlib import Path

LANDING = Path(sys.argv[1])
THEME = Path(sys.argv[2])
OUT = Path(sys.argv[3])


def module_strings(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        out[t.id] = node.value.value
    return out


def light_tokens(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "_LIGHT" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise SystemExit("_LIGHT nicht gefunden")


L = module_strings(LANDING)
tokens = light_tokens(THEME)

root_vars = "\n".join(f"  --{k}: {v};" for k, v in tokens.items())

# Streamlit-Buttons als statische Platzhalter nachbauen.
BTN_PRIMARY = (
    '<a href="#" style="display:inline-flex; align-items:center; justify-content:center;'
    " padding:10px 20px; background:var(--accent); color:var(--on-accent);"
    ' border-radius:8px; font-size:14px; font-weight:600; text-decoration:none;">'
    "Zur Plattform →</a>"
)
BTN_NAV = (
    '<a href="#" style="display:inline-flex; align-items:center; justify-content:center;'
    " padding:8px 18px; background:var(--accent); color:var(--on-accent);"
    ' border-radius:8px; font-size:13px; font-weight:600; text-decoration:none;">'
    "Anmelden</a>"
)

order = [
    "_USP_HTML",
    "_PROBLEM_HTML",
    "_PIPELINE_HTML",
    "_PREVIEW_HTML",
    "_PERSONAS_HTML",
    "_ACTORS_HTML",
    "_TRUST_HTML",
    "_TRIPLESET_HTML",
    "_FOOTER_HTML",
]
missing = [
    k
    for k in ["_LANDING_CSS", "_NAV_HTML", "_HERO_TEXT_HTML", "_HERO_GRAPHIC_HTML", *order]
    if k not in L
]
if missing:
    raise SystemExit(f"Fehlende Konstanten in landing.py: {missing}")

sections = "\n".join(L[k] for k in order)

# Das Streamlit-spezifische CSS (Sidebar ausblenden) stört hier nicht, bleibt drin.
landing_css = L["_LANDING_CSS"]

html = f"""<!DOCTYPE html>
<html lang="de"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Alte Landingpage (Vergleich) | AeroForesight AI</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root {{
{root_vars}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
  font-size: 15px;
  line-height: 1.6;
}}
.wrap {{ max-width: 1100px; margin: 0 auto; padding: 28px 40px 60px; }}
h1, h2, h3 {{ color: var(--text); }}
.hero-row {{
  display: grid;
  grid-template-columns: 1.25fr 0.75fr;
  gap: 40px;
  align-items: center;
  margin: 40px 0 8px;
}}
.nav-row {{ display: flex; justify-content: space-between; align-items: center; gap: 20px; }}
.hero-cta {{ display: flex; align-items: center; gap: 24px; }}
@media (max-width: 900px) {{
  .hero-row {{ grid-template-columns: 1fr; }}
  .wrap {{ padding: 20px 20px 48px; }}
}}
.compare-banner {{
  position: sticky; top: 0; z-index: 999;
  background: var(--amber-soft); border-bottom: 1px solid var(--border);
  padding: 10px 20px; font-size: 13px; color: var(--text-secondary);
}}
.compare-banner a {{ color: var(--accent); font-weight: 600; }}
</style>
{landing_css}
</head>
<body>
<div class="compare-banner">
  <strong>Alte Landingpage</strong> — statischer Nachbau aus <code>dashboard/landing.py</code> zum Vergleich.
  &nbsp;·&nbsp; <a href="/aeroforesight-ai-landing-page/index.html">Zur neuen Landingpage →</a>
</div>
<div class="wrap">
  <div class="nav-row">
    {L["_NAV_HTML"]}
    {BTN_NAV}
  </div>
  <div class="hero-row">
    <div>
      {L["_HERO_TEXT_HTML"]}
      <div class="hero-cta">
        {BTN_PRIMARY}
        <a href="#methodik" style="font-size:14px; font-weight:500; color:var(--text-secondary); text-decoration:none;">Wie die Simulation funktioniert</a>
      </div>
    </div>
    <div>{L["_HERO_GRAPHIC_HTML"]}</div>
  </div>
{sections}
</div>
</body></html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write(html)
print("OK", OUT, len(html), "bytes")
