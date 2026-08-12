#!/usr/bin/env python3
"""USAGE: python3 scripts/dev/draw-anchor-grid.py <image sous assets/> [grossissement] — writes var/tmp/anchor-grid.png, the sprite magnified under a
labelled grid, so a point can be READ off it instead of guessed.

INTENTION: a rune anchor is posed by eye, one per image, and the eye needs coordinates to name what it sees. Read at its delivered size a sprite is a
hundred pixels tall on screen, and a point picked off it is wrong by ten. The grid is drawn every GRID_STEP source pixels and numbered every
GRID_LABEL, so the answer is read rather than estimated — the same reason the runes are looked at on a sheet rather than trusted as coordinates.

Python rather than PHP: Pillow draws and measures images, and it is the language this project already uses for image measurement.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

GRID_STEP = 8
GRID_LABEL = 32
GRID_COLOR = (255, 0, 128, 110)
GRID_COLOR_LABEL = (255, 0, 128, 220)
ZOOM_DEFAULT = 5

if len(sys.argv) < 2:
    sys.exit("Usage: python3 scripts/dev/draw-anchor-grid.py <image sous assets/> [grossissement]")

root = Path(__file__).resolve().parents[2]
source = root / "assets" / sys.argv[1]
if not source.is_file():
    raise RuntimeError(f"FAULT l'image est absente : {source}")
zoom = int(sys.argv[2]) if len(sys.argv) > 2 else ZOOM_DEFAULT

sprite = Image.open(source).convert("RGBA")
width, height = sprite.size
# NEAREST and nothing else: a smoothed magnification invents pixels between the real ones, and the point read off it would not be the point stored.
board = sprite.resize((width * zoom, height * zoom), Image.NEAREST)
# The checkerboard is what makes a transparent sprite readable at all — a light square on a dark one, the same trick the review page uses behind its images.
ground = Image.new("RGBA", board.size, (32, 32, 36, 255))
draw = ImageDraw.Draw(ground)
for y in range(0, height * zoom, 16):
    for x in range(0, width * zoom, 16):
        if (x // 16 + y // 16) % 2 == 0:
            draw.rectangle([x, y, x + 15, y + 15], fill=(44, 44, 50, 255))
ground.alpha_composite(board)

draw = ImageDraw.Draw(ground)
for x in range(0, width + 1, GRID_STEP):
    labelled = x % GRID_LABEL == 0
    draw.line([(x * zoom, 0), (x * zoom, height * zoom)], fill=GRID_COLOR_LABEL if labelled else GRID_COLOR)
    if labelled:
        draw.text((x * zoom + 2, 2), str(x), fill=GRID_COLOR_LABEL)
for y in range(0, height + 1, GRID_STEP):
    labelled = y % GRID_LABEL == 0
    draw.line([(0, y * zoom), (width * zoom, y * zoom)], fill=GRID_COLOR_LABEL if labelled else GRID_COLOR)
    if labelled:
        draw.text((2, y * zoom + 2), str(y), fill=GRID_COLOR_LABEL)

out = root / "var" / "tmp" / "anchor-grid.png"
out.parent.mkdir(parents=True, exist_ok=True)
ground.save(out)
print(f"{out} — {width}×{height} px grossis {zoom} fois, grille tous les {GRID_STEP} px, chiffrée tous les {GRID_LABEL}")
