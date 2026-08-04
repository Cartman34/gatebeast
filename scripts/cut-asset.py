#!/usr/bin/env python3
"""Cut out a produced image into a deliverable sprite: real transparency, cropped to the silhouette.

Step 5 of the production chain. The generator returns an opaque square with the subject sitting on a
flat magenta field; a sprite needs the opposite — a transparent background and no wasted margin. This
script does that conversion and measures what step 6 will confront with the catalogue.

WHY MAGENTA CAN BE KEYED WITHOUT EATING THE SUBJECT
  Pure magenta appears in no material of this world. Measured on the three POC images, the distribution
  of the per-pixel distance to pure magenta (largest channel gap) is bimodal with an EMPTY VALLEY:

    HU-000     72.5 % of pixels at distance <= 20, then nothing until 160, then the subject
    SP-001-1   68.2 % of pixels at distance <= 20, then nothing until 160, then the subject
    SOL-001    no pixel below 200 at all (a tile has no background)

  Between 30 and 160 sits about one pixel in a thousand: that is the anti-aliased rim, and nothing else.
  There is therefore no threshold in that range that is "almost right" — any of them separates the two
  populations completely.

THE THRESHOLDS ARE NOT HELD HERE
  The key colour, the distance, the two thresholds and the alpha ramp all belong to key_color, the one
  service that owns them, together with the measured reasoning behind their values. This script asks
  that service and never compares against magenta on its own.

  THREE EXTRA GUARANTEES
  - Only background CONNECTED TO A BORDER is removed. A magenta-looking region enclosed by the subject
    stays opaque, so the silhouette can never be punched through.
  - Remaining holes inside the silhouette are filled back to opaque, for the same reason.
  - Opaque specks smaller than SPECK are dropped. A single stray pixel in a corner would otherwise
    stretch the crop box across the whole image and put the pose point where nothing stands. The floor
    is deliberately tiny (an 8x8 blob) so no real detail of a subject can reach it.

DE-FRINGING, TWICE
  A rim pixel is a mix of magenta and subject. Its colour is un-mixed against the known backdrop
  (C = (P - (1-a)*M) / a) so no violet halo survives around the sprite.
  A fully transparent pixel still carries a colour in the file, and every renderer that filters or
  builds mipmaps blends it back in. Its magenta is therefore replaced by the colour of the nearest
  opaque pixel — invisible at alpha 0, and the only thing that keeps a scaled sprite from glowing pink
  at its edges.

MEASURES RETURNED
  size          the cropped sprite, in pixels
  silhouette    the opaque bounding box as a share of the source image
  contact       the opaque span on the bottom band of the silhouette — the apparent ground width
  anchor        the pose point, in pixels inside the cropped sprite: middle of that contact span,
                on the bottom edge of the silhouette
  transparency  the share of fully transparent and of partial pixels after the cut

Usage:
  python3 cut-asset.py <path> [...]        paths relative to assets/, or absolute
  python3 cut-asset.py --dry-run <path>    measure only, write nothing
  python3 cut-asset.py --out <dir> <path>  write elsewhere than assets/cutout/
"""
import json
import sys
from pathlib import Path

import numpy
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import key_color

REPOSITORY = Path(__file__).resolve().parents[1]
ASSETS = REPOSITORY / "assets"
CUTOUT = ASSETS / "cutout"

SPECK = 64       # an opaque island smaller than this many pixels is field noise, not subject
CONTACT_BAND = 0.03  # share of the silhouette height taken as the ground-contact band


def border_connected(mask):
    """The part of a boolean mask that touches an image border, 4-connected."""
    labels, count = ndimage.label(mask)
    if count == 0:
        return numpy.zeros_like(mask)
    border = numpy.concatenate([labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]])
    outside = set(int(value) for value in numpy.unique(border) if value)

    return numpy.isin(labels, list(outside)) if outside else numpy.zeros_like(mask)


def drop_specks(alpha, floor=SPECK):
    """Erase opaque islands too small to be part of a subject — isolated noise in the flat field."""
    labels, count = ndimage.label(alpha > 0.0)
    if count <= 1:
        return alpha
    areas = ndimage.sum(numpy.ones_like(labels), labels, index=range(1, count + 1))
    too_small = [index for index, area in enumerate(areas, start=1) if area < floor]
    if not too_small:
        return alpha

    return numpy.where(numpy.isin(labels, too_small), 0.0, alpha)


def defringe(rgb, alpha):
    """Un-mix a rim pixel from the magenta it was blended with."""
    partial = (alpha > 0.0) & (alpha < 1.0)
    if not partial.any():
        return rgb
    cleaned = rgb.astype(numpy.float32)
    share = alpha[partial][:, None]
    mixed = cleaned[partial]
    backdrop = key_color.MAGENTA.astype(numpy.float32)
    cleaned[partial] = numpy.clip((mixed - (1.0 - share) * backdrop) / share, 0, 255)

    return cleaned.astype(numpy.uint8)


def bleed(rgb, alpha):
    """Push the nearest opaque colour into the transparent area, so filtering cannot reveal magenta."""
    empty = alpha <= 0.0
    if not empty.any() or empty.all():
        return rgb
    _, indices = ndimage.distance_transform_edt(empty, return_indices=True)

    return rgb[indices[0], indices[1]]


def measure(alpha, source_size):
    """Silhouette, ground contact and pose point, from the alpha of the CROPPED sprite."""
    height, width = alpha.shape
    opaque = alpha > 0.0
    rows = numpy.flatnonzero(opaque.any(axis=1))
    columns = numpy.flatnonzero(opaque.any(axis=0))
    if rows.size == 0:
        return None
    bottom = int(rows[-1])
    band_height = max(1, int(round(height * CONTACT_BAND)))
    band = opaque[bottom - band_height + 1: bottom + 1, :]
    band_columns = numpy.flatnonzero(band.any(axis=0))
    contact_left, contact_right = int(band_columns[0]), int(band_columns[-1])
    source_width, source_height = source_size

    return {
        "size_px": {"width": width, "height": height},
        "silhouette_share": {
            "width": round(100 * width / source_width, 1),
            "height": round(100 * height / source_height, 1),
        },
        "contact_px": {"left": contact_left, "right": contact_right,
                       "width": contact_right - contact_left + 1},
        "anchor_px": {"x": round((contact_left + contact_right) / 2, 1), "y": float(bottom + 1)},
        "aspect": round(width / height, 3),
        "transparency": {
            "fully_transparent": round(100 * float((alpha <= 0.0).mean()), 2),
            "partial": round(100 * float(((alpha > 0.0) & (alpha < 1.0)).mean()), 2),
        },
    }


def already_alpha(path):
    """True when the file already carries its own real transparency.

    The generator used to render an opaque square on a flat magenta field, which this script had to
    key out. It now renders a real alpha channel directly, so an image in that mode needs no keying at
    all: it is already the cutout, only oversized. Keying it again on top would find no magenta and
    silently flatten the transparency it already has (see the fault this replaced), so a modern image
    is detected here and routed around the whole keying pipeline.
    """
    with Image.open(path) as probe:
        if probe.mode not in ("RGBA", "LA"):
            return False
        alpha = numpy.asarray(probe.convert("RGBA"))[:, :, 3]

    return bool((alpha < 255).any())


def crop(path):
    """Trim an image that already has its own alpha to the silhouette. No keying, no de-fringing:

    the transparency is the generator's own and is kept byte for byte, only the empty margin is cut.
    """
    source = Image.open(path).convert("RGBA")
    rgba = numpy.asarray(source)
    alpha = rgba[:, :, 3].astype(numpy.float32) / 255.0

    opaque = alpha > 0.0
    if not opaque.any():
        raise ValueError(f"nothing but transparency in {path}")
    rows = numpy.flatnonzero(opaque.any(axis=1))
    columns = numpy.flatnonzero(opaque.any(axis=0))
    box = (int(columns[0]), int(rows[0]), int(columns[-1]) + 1, int(rows[-1]) + 1)
    cropped_rgba = rgba[box[1]:box[3], box[0]:box[2]]
    cropped_alpha = alpha[box[1]:box[3], box[0]:box[2]]

    measures = measure(cropped_alpha, source.size)
    measures["source_size_px"] = {"width": source.size[0], "height": source.size[1]}
    measures["crop_box"] = {"left": box[0], "top": box[1], "right": box[2], "bottom": box[3]}
    measures["mode"] = "crop (alpha already present)"

    return Image.fromarray(cropped_rgba, "RGBA"), measures


def cut(path):
    """Cut one image out. Returns (RGBA sprite, measures). Nothing is written here.

    Two paths coexist because the generator changed under this tool. A modern image already carries
    its own alpha and is only cropped, by crop() above. An old magenta-backed image still needs the
    keying below.
    """
    if already_alpha(path):
        return crop(path)

    source = Image.open(path).convert("RGB")
    rgb = numpy.asarray(source)
    alpha = key_color.alpha_ramp(key_color.distance(rgb))

    # Only background that reaches a border is removed, and holes left inside the subject are closed.
    background = border_connected(alpha <= 0.0)
    alpha = numpy.where(background, 0.0, numpy.maximum(alpha, 0.0))
    solid = ndimage.binary_fill_holes(alpha >= 1.0)
    alpha = numpy.where(solid, 1.0, alpha)
    alpha = drop_specks(alpha)

    cleaned = defringe(rgb, alpha)

    opaque = alpha > 0.0
    if not opaque.any():
        raise ValueError(f"nothing but background in {path}")
    rows = numpy.flatnonzero(opaque.any(axis=1))
    columns = numpy.flatnonzero(opaque.any(axis=0))
    box = (int(columns[0]), int(rows[0]), int(columns[-1]) + 1, int(rows[-1]) + 1)
    cropped_rgb = cleaned[box[1]:box[3], box[0]:box[2]]
    cropped_alpha = alpha[box[1]:box[3], box[0]:box[2]]
    cropped_rgb = bleed(cropped_rgb, cropped_alpha)

    sprite = numpy.dstack([cropped_rgb,
                           numpy.round(cropped_alpha * 255).astype(numpy.uint8)])
    measures = measure(cropped_alpha, source.size)
    measures["source_size_px"] = {"width": source.size[0], "height": source.size[1]}
    measures["crop_box"] = {"left": box[0], "top": box[1], "right": box[2], "bottom": box[3]}
    measures["thresholds"] = {"hard": key_color.HARD, "soft": key_color.SOFT}
    measures["mode"] = "magenta key"

    return Image.fromarray(sprite, "RGBA"), measures


def destination(path, out=None):
    """Where the sprite goes: assets/cutout/<same relative path>, source left untouched."""
    if out:
        return Path(out) / path.name
    try:
        relative = path.resolve().relative_to(ASSETS)
    except ValueError:
        return CUTOUT / path.name
    # Drop the leading production folder (poc/, revue-da/...) so cutouts sit by type.
    parts = relative.parts[1:] if len(relative.parts) > 1 else relative.parts

    return CUTOUT.joinpath(*parts)


def main(arguments):
    dry_run = "--dry-run" in arguments
    arguments = [argument for argument in arguments if argument != "--dry-run"]
    out = None
    if "--out" in arguments:
        index = arguments.index("--out")
        out = arguments[index + 1]
        arguments = arguments[:index] + arguments[index + 2:]
    if not arguments:
        print(__doc__)
        return 2

    failed = 0
    for argument in arguments:
        path = Path(argument)
        if not path.is_absolute():
            path = ASSETS / argument
        if not path.is_file():
            print(f"ABSENT {path}")
            failed += 1
            continue
        sprite, measures = cut(path)
        target = destination(path, out)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            sprite.save(target)
        print(f"{path.name} -> {'(dry run)' if dry_run else target}")
        print(json.dumps(measures, indent=2))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
