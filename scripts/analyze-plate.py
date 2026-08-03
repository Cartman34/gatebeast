#!/usr/bin/env python3
"""Measure a plate against the art direction, instead of judging it by eye.

The measurement itself lives in plate_metrics.py, shared with the report builder so the two always
agree. This is its command-line face: the reference line, the light target, then one line per plate
with its light verdict underneath.

Usage: python3 analyze-plate.py <image.png> [...]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_metrics import (ASSETS, DARK_MAX, LUMINANCE_MAX, LUMINANCE_MIN, REFERENCE, light_verdict,
                           measure)

print(f"RÉFÉRENCE   cases chargées {REFERENCE['cases_chargees']:5.1f} %  "
      f"détail {REFERENCE['energie_moyenne']:5.1f}  luminance {REFERENCE['luminance']:5.1f}  "
      f"zones sombres {REFERENCE['part_sombre']:4.1f} %  saturation {REFERENCE['saturation']:4.1f} %")
print(f"CIBLE LUMIÈRE  luminance {LUMINANCE_MIN:.0f}-{LUMINANCE_MAX:.0f}  "
      f"zones sombres <= {DARK_MAX:.0f} %  (toutes les planches, sans exception)")

for argument in sys.argv[1:]:
    path = Path(argument)
    if not path.is_absolute():
        path = ASSETS / path
    if not path.is_file():
        print(f"ABSENT {path.name}")
        continue
    mesure = measure(path)
    print(f"{path.name:28s} cases chargées {mesure['cases_chargees']:5.1f} %  "
          f"détail {mesure['energie_moyenne']:5.1f}  luminance {mesure['luminance']:5.1f}  "
          f"zones sombres {mesure['part_sombre']:4.1f} %  saturation {mesure['saturation']:4.1f} %  "
          f"| écart charge {mesure['cases_chargees'] - REFERENCE['cases_chargees']:+5.1f} pts")
    print(f"{'':28s} {light_verdict(mesure)}")
