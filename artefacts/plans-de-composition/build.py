#!/usr/bin/env python3
"""Build the composition-plans gallery page.

A "composition plan" is a pair of files produced together for one game
subject: a JSON file that declares the grid, the title and the notes, and an
SVG file, drawn from that JSON, that shows the actual layout. This script
finds every such pair under ``assets/poc/``, reads the JSON for the caption
and embeds the SVG verbatim (no external references, so the page keeps
working under a strict CSP with no linked assets), and writes one static
HTML page listing all of them, largest and most legible first.

Run from the repository root:

    python3 artefacts/plans-de-composition/build.py

The script is idempotent: given the same source files it always produces the
same page, and a new composition plan dropped under assets/poc/ is picked up
automatically on the next run, with no code change required.
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = REPO_ROOT / "assets" / "poc"
OUTPUT_PATH = Path(__file__).resolve().parent / "page.html"

# Composition-plan SVGs live at assets/poc/**/plan-composition-*.svg.
# The "-geometrie" variants are exploratory studies, not plans: they are
# excluded explicitly.
PLAN_SVG_GLOB = "plan-composition-*.svg"
GEOMETRY_SUFFIX = "-geometrie.svg"


@dataclass(frozen=True)
class CompositionPlan:
    """One discovered composition plan: its declared metadata and its drawing."""

    title: str
    columns: int
    rows: int
    notes: list[str]
    svg_markup: str
    source_path: Path


def find_plan_svg_paths() -> list[Path]:
    """Locate every composition-plan SVG under assets/poc/, excluding geometry studies.

    Sorted by path for a stable, reproducible page order.
    """
    all_matches = ASSETS_DIR.glob(f"**/{PLAN_SVG_GLOB}")
    plan_paths = [path for path in all_matches if not path.name.endswith(GEOMETRY_SUFFIX)]
    return sorted(plan_paths)


def load_plan(svg_path: Path) -> CompositionPlan:
    """Pair an SVG with its declarative JSON sibling and load a CompositionPlan.

    The JSON file sits next to the SVG under the same base name (only the
    extension differs). It is the source of truth for the title, the grid
    size and the notes: the SVG itself is only the rendering, so nothing is
    inferred or invented from the filename.
    """
    json_path = svg_path.with_suffix(".json")
    if not json_path.exists():
        raise FileNotFoundError(
            f"Composition plan '{svg_path}' has no declarative JSON sibling at '{json_path}'."
        )

    declaration = json.loads(json_path.read_text(encoding="utf-8"))
    grid = declaration["grid"]

    return CompositionPlan(
        title=declaration["title"],
        columns=grid["columns"],
        rows=grid["rows"],
        notes=declaration.get("notes", []),
        svg_markup=svg_path.read_text(encoding="utf-8"),
        source_path=svg_path.relative_to(REPO_ROOT),
    )


def render_plan_section(plan: CompositionPlan) -> str:
    """Render one composition plan as a self-contained HTML section.

    The SVG markup is inlined directly into the page (never linked), which is
    what makes the page work under a strict content-security policy that
    forbids external resources. The SVG already paints its own light
    background, so it stays legible whether the surrounding page is in light
    or dark theme.
    """
    notes_html = "".join(f"<p class=\"plan-note\">{html.escape(note)}</p>" for note in plan.notes)
    return f"""
<section class="plan">
  <h2 class="plan-title">{html.escape(plan.title)}</h2>
  <p class="plan-meta">Grille {plan.columns}&nbsp;&times;&nbsp;{plan.rows} &mdash; source : <code>{html.escape(str(plan.source_path))}</code></p>
  {notes_html}
  <div class="plan-drawing">
    {plan.svg_markup}
  </div>
</section>"""


def render_page(plans: list[CompositionPlan]) -> str:
    """Assemble the full HTML page from the rendered plan sections."""
    sections_html = "\n".join(render_plan_section(plan) for plan in plans)

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Plans de composition &mdash; GateBeast</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #ffffff;
    --fg: #1d1a24;
    --muted: #5c5468;
    --border: #d8d3e0;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #17151d;
      --fg: #eeecf3;
      --muted: #a79fb5;
      --border: #3a3546;
    }}
  }}
  :root[data-theme="light"] {{ --bg: #ffffff; --fg: #1d1a24; --muted: #5c5468; --border: #d8d3e0; }}
  :root[data-theme="dark"] {{ --bg: #17151d; --fg: #eeecf3; --muted: #a79fb5; --border: #3a3546; }}

  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 2rem 1.5rem 4rem;
    background: var(--bg);
    color: var(--fg);
    font-family: system-ui, sans-serif;
  }}
  h1 {{
    font-size: 1.5rem;
    margin: 0 0 0.25rem;
  }}
  .page-intro {{
    color: var(--muted);
    margin: 0 0 2rem;
    max-width: 60ch;
  }}
  .plan {{
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0 0 2rem;
    max-width: 900px;
  }}
  .plan-title {{
    font-size: 1.15rem;
    margin: 0 0 0.35rem;
  }}
  .plan-meta {{
    color: var(--muted);
    font-size: 0.9rem;
    margin: 0 0 0.75rem;
  }}
  .plan-meta code {{
    font-size: 0.85em;
  }}
  .plan-note {{
    color: var(--muted);
    font-size: 0.9rem;
    margin: 0 0 0.5rem;
  }}
  .plan-drawing {{
    margin-top: 0.75rem;
    overflow-x: auto;
  }}
  .plan-drawing svg {{
    display: block;
    width: 100%;
    height: auto;
    max-width: 100%;
    border-radius: 6px;
  }}
</style>
</head>
<body>
<h1>Plans de composition</h1>
<p class="page-intro">Tous les plans de composition d&eacute;clar&eacute;s sous <code>assets/poc/</code>, chacun avec son sujet, sa grille et son dessin tel que produit.</p>
{sections_html}
</body>
</html>
"""


def main() -> None:
    """Discover every composition plan and (re)write the gallery page."""
    svg_paths = find_plan_svg_paths()
    if not svg_paths:
        raise SystemExit(f"No composition-plan SVG found under '{ASSETS_DIR}'.")

    plans = [load_plan(path) for path in svg_paths]
    page_html = render_page(plans)

    OUTPUT_PATH.write_text(page_html, encoding="utf-8")

    print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} with {len(plans)} composition plan(s):")
    for plan in plans:
        print(f"  - {plan.title}  ({plan.source_path})")


if __name__ == "__main__":
    main()
