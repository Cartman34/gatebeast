"""Plate measurement, in one place so the command-line tool and the report builder agree.

Three things the eye argues about and numbers settle:
- CLUTTER: how much fine detail covers the ground, as the share of tiles that read as busy.
- BRIGHTNESS: the plate must stay bright, light values dominant, shadows short and pale.
- COLOUR: colours must stay frank, never muted or washed out.

Absolute values mean little; the gap to the reference and to the targets means everything.
"""
from pathlib import Path

from PIL import Image, ImageFilter

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"
TILES_X, TILES_Y = 32, 24
BUSY_TILE = 22.0  # mean edge energy above which a tile reads as visually busy

# Light target set by the operator (2026-08-03) for EVERY plate: they must be equally and strongly bright.
LUMINANCE_MIN, LUMINANCE_MAX = 115.0, 130.0
DARK_MAX = 10.0


def measure(path: Path) -> dict:
    image = Image.open(path).convert("RGB")
    grey = image.convert("L")
    edges = grey.filter(ImageFilter.FIND_EDGES)

    tile_w = image.width // TILES_X
    tile_h = image.height // TILES_Y
    busy = 0
    total = 0
    energies = []
    for row in range(TILES_Y):
        for column in range(TILES_X):
            box = (column * tile_w, row * tile_h, (column + 1) * tile_w, (row + 1) * tile_h)
            tile = edges.crop(box)
            histogram = tile.histogram()
            count = sum(histogram) or 1
            energy = sum(value * level for level, value in enumerate(histogram)) / count
            energies.append(energy)
            total += 1
            if energy > BUSY_TILE:
                busy += 1

    small = image.resize((160, 120))
    pixels = list(small.getdata())
    luminance = sum(0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in pixels) / len(pixels)
    dark = sum(1 for r, g, b in pixels if 0.2126 * r + 0.7152 * g + 0.0722 * b < 60) / len(pixels)
    saturation = sum((max(p) - min(p)) / (max(p) or 1) for p in pixels) / len(pixels)

    return {
        "taille": f"{image.width}x{image.height}",
        "cases_chargees": 100 * busy / total,
        "energie_moyenne": sum(energies) / len(energies),
        "luminance": luminance,
        "part_sombre": 100 * dark,
        "saturation": 100 * saturation,
    }


def light_verdict(mesure: dict) -> str:
    """The operator's light target, stated plainly: LUMIÈRE OK, or what is out of band and by how much."""
    ecarts = []
    if mesure["luminance"] < LUMINANCE_MIN:
        ecarts.append(f"luminance {LUMINANCE_MIN - mesure['luminance']:.1f} sous la bande")
    elif mesure["luminance"] > LUMINANCE_MAX:
        ecarts.append(f"luminance {mesure['luminance'] - LUMINANCE_MAX:.1f} au-dessus de la bande")
    if mesure["part_sombre"] > DARK_MAX:
        ecarts.append(f"sombre {mesure['part_sombre'] - DARK_MAX:.1f} pts au-dessus du plafond")

    return "LUMIÈRE OK" if not ecarts else "LUMIÈRE FAUTIVE — " + ", ".join(ecarts)


def reference_path(name: str = "da-b4-r15-scene.png") -> Path:
    """Where the reference plate sits. It was moved into Saves/, so both places are looked at."""
    for candidate in (ASSETS / name, ASSETS / "Saves" / name):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"reference plate not found: {name}")


REFERENCE = measure(reference_path())
