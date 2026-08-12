#!/usr/bin/env python3
"""USAGE: python3 scripts/dev/crop-plate-corner.py <image> <sortie> <gauche> <haut> <droite> <bas> [agrandissement] — writes that region of the image, optionally scaled up.

INTENTION: the operator points at one subject inside a whole reference plate ("the fir at the top left"), and a full plate read at once is too coarse to describe that subject faithfully. Cropping and
enlarging first is what lets it be looked at rather than guessed. In Python because Pillow is the project's image library and has no PHP equivalent installed here.
"""
import sys
from pathlib import Path

from PIL import Image

source, target = Path(sys.argv[1]), Path(sys.argv[2])
box = tuple(int(value) for value in sys.argv[3:7])
zoom = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
cut = Image.open(source).crop(box)
if zoom != 1.0:
    cut = cut.resize((int(cut.width * zoom), int(cut.height * zoom)), Image.LANCZOS)
cut.save(target)
print(f"{source.name} {box} -> {target} {cut.width}x{cut.height}")
