#!/usr/bin/env python3
"""Draw every rune of assets/runes.json on one sheet, so the geometry is looked at instead of imagined.

USAGE
  python3 scripts/dev/draw-runes-sheet.py — writes var/tmp/runes.svg and, if rsvg-convert is there, var/tmp/runes.png.

INTENTION
  Twenty paths were written from twenty words — « une arche », « un croissant », « trois traits liés d'un seul geste ». Written blind, a path can be perfectly
  valid and draw something else entirely, and nobody would know until a creature wore it. This puts them all on one sheet, each with its name, at the size they
  will be seen: the check for coordinates is the eye, there is no other.
"""
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = json.loads((REPO / "assets/runes.json").read_text(encoding="utf-8"))
CELL, COLUMNS, PAD = 130, 5, 16
INK, GROUND = "#9ba3b0", "#0e1013"

shapes = list(DATA["shapes"].items())
colours = {carried["shape"]: carried["color"] for carried in DATA["individuals"].values()}
rows = (len(shapes) + COLUMNS - 1) // COLUMNS
width, height = COLUMNS * CELL, rows * CELL
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         f'<rect width="{width}" height="{height}" fill="{GROUND}"/>']
for index, (name, shape) in enumerate(shapes):
    x, y = (index % COLUMNS) * CELL, (index // COLUMNS) * CELL
    scale = (CELL - 2 * PAD) / 100
    parts.append(f'<g transform="translate({x + PAD} {y + PAD}) scale({scale:.4f})">'
                 f'<path d="{shape["path"]}" fill="none" stroke="{colours.get(name, INK)}" stroke-width="8" '
                 f'stroke-linecap="round" stroke-linejoin="round"/></g>')
    parts.append(f'<text x="{x + CELL / 2}" y="{y + CELL - 4}" fill="{INK}" font-family="sans-serif" font-size="11" '
                 f'text-anchor="middle">{shape["label"]}</text>')
parts.append("</svg>")

output = REPO / "var/tmp"
output.mkdir(parents=True, exist_ok=True)
svg = output / "runes.svg"
svg.write_text("\n".join(parts), encoding="utf-8")
print(f"{svg.relative_to(REPO)} — {len(shapes)} formes")

converter = shutil.which("rsvg-convert")
if converter is None:
    raise SystemExit("FAULT rsvg-convert est absent — le SVG est écrit, mais personne ne peut le regarder d'ici.")
png = output / "runes.png"
subprocess.run([converter, "-o", str(png), str(svg)], check=True)
print(f"{png.relative_to(REPO)}")
