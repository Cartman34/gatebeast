#!/usr/bin/env python3
"""Build the tile-size comparison page: the same slice of world at each candidate size.

Nothing is generated. The scenes are composed from masters already produced and validated, then
resampled down to each candidate — exactly what changing the tile size would cost in real life, a
re-export and no reshoot. What the page shows is therefore what would really be obtained.

The page offers the two readings that matter, because they answer different questions:
  - at native size, how much world fits on a screen;
  - brought to the same width, how much detail each size keeps.

Usage: python3 artefacts/taille-de-case/build.py
Writes page.html beside this script.
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
POC = REPO / "assets" / "poc"

CANDIDATES = [16, 24, 48]
COLUMNS, ROWS = 12, 8
HUMAN_TILES = 1.9

GRASS = POC / "sol" / "CH-001.png"
FENCE_EW = POC / "cloture" / "OB-010_shape-ew.png"
OAK = POC / "vegetation" / "TR-060.png"
TALL_GRASS = POC / "vegetation" / "TR-062.png"


def fitted(path: Path, tile: int, columns: int) -> Image.Image:
    """A master brought to the size it would be delivered at for a footprint that wide.

    Width carries the scale: the footprint describes the ground, and a tall subject rises higher.
    """
    image = Image.open(path).convert("RGBA")
    width = tile * columns

    return image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)


def scene(tile: int) -> Image.Image:
    board = Image.new("RGBA", (COLUMNS * tile, ROWS * tile), (0, 0, 0, 0))

    ground = fitted(GRASS, tile, 1)
    for column in range(COLUMNS):
        for row in range(ROWS):
            board.alpha_composite(ground, (column * tile, row * tile))

    fence = fitted(FENCE_EW, tile, 1)
    for column in range(COLUMNS):
        board.alpha_composite(fence, (column * tile, 5 * tile - (fence.height - tile)))

    oak = fitted(OAK, tile, 2)
    board.alpha_composite(oak, (2 * tile, 3 * tile - (oak.height - 2 * tile)))

    tuft = fitted(TALL_GRASS, tile, 1)
    for column, row in ((7, 2), (8, 6), (10, 3)):
        board.alpha_composite(tuft, (column * tile, row * tile - (tuft.height - tile)))

    # A plain silhouette stands in for a human: no validated human sprite exists yet, and the
    # question here is size on screen, which a silhouette answers honestly.
    tall, wide = HUMAN_TILES * tile, tile * 0.55
    left, top = 5 * tile + (tile - wide) / 2, 7 * tile + tile - tall
    pen = ImageDraw.Draw(board)
    pen.rounded_rectangle([left, top + tall * 0.28, left + wide, top + tall],
                          radius=wide / 2.6, fill=(38, 42, 52, 235))
    head = tall * 0.26
    pen.ellipse([left + (wide - head) / 2, top, left + (wide + head) / 2, top + head],
                fill=(38, 42, 52, 235))

    return board


def data_uri(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def build() -> int:
    panels = []
    for tile in CANDIDATES:
        image = scene(tile)
        panels.append({
            "tile": tile,
            "width": image.width,
            "height": image.height,
            "human": round(HUMAN_TILES * tile),
            "map": f"{64 * tile} × {48 * tile}",
            "onScreen": f"{1920 // tile} × {1080 // tile}",
            "image": data_uri(image),
        })

    data = {
        "title": "Quelle taille pour une case ?",
        "lede": ("Aucune image n'a été générée : les scènes sont composées à partir des maîtres déjà "
                 "validés, puis rééchantillonnées. C'est exactement ce que coûterait un changement de "
                 "taille — un ré-export, aucune reprise."),
        "slice": f"{COLUMNS} × {ROWS} cases",
        "panels": panels,
    }

    template = (HERE / "template.html").read_text(encoding="utf-8")
    page = template.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (HERE / "page.html").write_text(page, encoding="utf-8")

    weight = (HERE / "page.html").stat().st_size / 1024
    print(f"tailles {', '.join(str(t) for t in CANDIDATES)} · page {weight:.0f} Ko")

    return 0


if __name__ == "__main__":
    raise SystemExit(build())
