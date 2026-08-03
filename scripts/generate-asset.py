#!/usr/bin/env python3
"""Generate one POC asset: one subject, alone, in the validated art direction.

Usage:
  python3 generate-asset.py <type> <code> [--dump]

  <type>  sol | batiment | vegetation | personnage | creature
  <code>  a sheet code — SP-nnn-i for a creature individual, HU-nnn for a human, SOL-nnn for an
          element, HU-000 for the player character.
  --dump  assemble and save the prompt without generating.

Output: assets/poc/<type>/<code>.png, with prompt-<code>.txt beside it. An existing asset is never
overwritten: the shot is refused, the way plate versions are protected.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asset_common import TYPES, shoot

if len(sys.argv) < 3:
    print(__doc__)
    print(f"types connus : {', '.join(TYPES)}")
    raise SystemExit(2)

sys.exit(shoot(sys.argv[1], sys.argv[2]))
