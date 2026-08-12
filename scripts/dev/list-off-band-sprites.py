#!/usr/bin/env python3
"""
USAGE
  python3 scripts/dev/list-off-band-sprites.py — lists every current sprite whose delivered box no longer matches the projected tile, and says by how much.

INTENTION
  The projected tile became 96 × 84 on 2026-08-08; everything drawn before that was delivered on a square 96 × 96. Those files are not wrong drawings — they are
  drawings of a tile seen from straight above — and they will have to be redone. Which ones, and how many, is a count nobody should make by eye: it decides how
  much of the park has to go back through the generator, and that is the figure the operator needs before deciding whether to redo them in one go or at the pace
  of ordinary retakes. Read-only.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import tile_scale

data = json.loads((ROOT / "assets" / "subjects.json").read_text(encoding="utf-8"))
off, fine = [], 0

for code, subject in sorted(data["subjects"].items()):
    # THE CANVAS COMES FROM THE COVER WHEN THERE IS ONE, exactly as `generate-sprite.py` and `export-asset.py` read it: an oak stands on two tiles and spreads its
    # crown over six, so its master is six tiles wide. Judging it on the footprint compared a six-tile drawing to a two-tile band and called the tree wrong — which
    # is what happened to TR-060 and TR-063 on 2026-08-10, and it nearly cost two generations to redraw images that were right.
    spread = subject.get("cover") or subject.get("footprint") or {}
    if not spread:
        continue
    wanted = tile_scale.master_definition(spread["columns"], spread["rows"], subject.get("height"))
    for variant in subject.get("variants", []):
        # Read from the variant since 2026-08-10: no formula knows how tall a drawing should come back.
        low, high = tile_scale.variant_band(spread["columns"], spread["rows"], variant, f"{code} / {variant.get('ref')}")
        for representation in variant.get("representations", []):
            if representation.get("status") != "current":
                continue
            measures = (representation.get("measures") or {}).get("delivered_px")
            if not measures:
                continue
            if low <= measures["height"] <= high:
                fine += 1
                continue
            off.append((representation["path"], measures["width"], measures["height"], wanted["width"], wanted["height"], low, high))

for path, width, height, want_w, want_h, low, high in off:
    print(f"  {path}")
    print(f"      livré {width} × {height}  ·  attendu {want_w} × {want_h}  ·  fourchette {low}–{high}")

print(f"\n{len(off)} sprite(s) hors de leur fourchette, {fine} dedans.")
