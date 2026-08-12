"""Usage: python3 scripts/dev/measure-ink-off-band.py — for every current sprite the referentiel places outside its height band, measures the INKED bounding box on disk and reports both.

Intention: `list-off-band-sprites.py` judges the height recorded in the referentiel, which is the delivered box, not the drawing. On the flat path pieces that gap mattered — six of eleven had all
their ink inside the tile and needed no new drawing at all. The same doubt applies to every other off-band sprite, and it has to be measured before any of them is called a retake: a generation is a
spend, and this script is what tells a wrong box apart from a wrong drawing.

Python rather than PHP: the tile-scale service and the alpha bounding box (Pillow) both live in Python, and the point is to ask them rather than restate the model.
"""

import json
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import tile_scale

data = json.loads((ROOT / 'assets' / 'subjects.json').read_text(encoding='utf-8'))

print(f"{'Sprite':<52}{'Sujet':>8}{'Boîte':>8}{'Encre':>8}{'Plancher':>10}{'Plafond':>9}  Verdict (mesures en pixels, fourchettes déclarées en TY)")

for code, subject in sorted(data['subjects'].items()):
    # The cover commands the canvas when the subject declares one — same reading as `generate-sprite.py`. See `list-off-band-sprites.py` for what judging on the
    # footprint cost.
    spread = subject.get('cover') or subject.get('footprint') or {}
    if not spread:
        continue
    for variant in subject.get('variants', []):
        # The band is the variant's own declaration since 2026-08-10, so it is read here per variant and never per subject.
        low, high = tile_scale.variant_band(spread['columns'], spread['rows'], variant, f"{code} / {variant.get('ref')}")
        for representation in variant.get('representations', []):
            if representation.get('status') != 'current':
                continue
            measures = (representation.get('measures') or {}).get('delivered_px')
            if not measures:
                continue
            if low <= measures['height'] <= high:
                continue
            path = ROOT / 'assets' / representation['path']
            if not path.is_file():
                raise SystemExit(f"Sprite inscrit mais absent du disque : {path}")
            box = Image.open(path).convert('RGBA').getbbox()
            if box is None:
                raise SystemExit(f"Sprite entièrement transparent, rien à mesurer : {path}")
            inked = box[3] - box[1]
            verdict = 'dans la fourchette' if low <= inked <= high else ('TROP BAS' if inked < low else 'trop haut')
            print(f"{representation['path']:<52}{code:>8}{measures['height']:>8}{inked:>8}{low:>10}{high:>9}  {verdict}")
