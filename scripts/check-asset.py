#!/usr/bin/env python3
"""Measure a produced or cut-out asset against what the design requires — step 6 of the chain.

The design lists what the mechanical step must check (chaine-de-production.md): "fond uniforme et
détourable, transparence effective après détourage, sujet remplissant le cadre, emprise mesurée
conforme à l'emprise annoncée, régularité et raccord bord à bord pour une matière de sol, luminance
dans la bande de la direction artistique". Each of those is one block below, and nothing here is a
matter of taste — the judgement step handles what cannot be counted.

WHAT IS MEASURED
  SOURCE          size, aspect, whether the file carries an alpha channel.
  BACKGROUND      (opaque cutout source only) how magenta and how uniform the four border strips are.
                  A background that is not uniform cannot be keyed without eating into the subject.
  SUBJECT         the bounding box of what is not background, against the frame.
  TRANSPARENCY    after the cutout: the share of fully transparent pixels, of partial pixels, and
                  whether any fully opaque magenta survives — the proof that keying really happened.
  FOOTPRINT       the apparent ground extent, confronted with the footprint the referentiel declares.
                  It is read off the SILHOUETTE WIDTH, not off the ground contact: the footprint is the
                  cell a subject occupies, and a standing human occupies its tile with its body, not
                  with the span of its two boots. The contact span is measured all the same, because
                  that is what places the pose point.
                  The confrontation is done on the SHAPE RATIO (footprint columns / declared height)
                  rather than on an absolute count of tiles: converting a horizontal ground extent with
                  a scale read off a vertical standing extent would be wrong under the world's 70°
                  camera, and the design does not fix that projection. See the note at the bottom.
  TILING          (ground material) edge-to-edge join: the seam that appears when the tile is repeated,
                  compared with the texture's own column-to-column variation. A tile joins invisibly
                  when the seam is no worse than the material's natural grain.
  REGULARITY      (ground material) the largest luminance gap between the four quadrants.
  LIGHT           mean luminance and dark share, measured on the SUBJECT ONLY, against the art
                  direction's band — the same constants the plates are held to.

Usage:
  python3 check-asset.py <path> [...]         paths relative to assets/, or absolute
  python3 check-asset.py --code CH-010 <path> force the referentiel's sujet instead of guessing it
"""
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import key_color
from plate_metrics import DARK_MAX, LUMINANCE_MAX, LUMINANCE_MIN

# check-sujets.py is hyphenated, so it is loaded by path rather than imported by name (the same
# mechanism record-asset.py already uses for cut-asset.py).
CHECK_SUJETS = Path(__file__).resolve().parent / "check-sujets.py"
spec = importlib.util.spec_from_file_location("check_sujets", CHECK_SUJETS)
check_sujets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_sujets)

REPOSITORY = Path(__file__).resolve().parents[1]
ASSETS = REPOSITORY / "assets"


@dataclass
class Profile:
    """Just what this checker needs of a sujet, read from the referentiel — its type, footprint and
    height, never the whole sujet."""
    code: str
    type: str
    footprint: dict
    height: float

BORDER = 0.04        # share of the image width taken as the border strip
DARK_LEVEL = 60      # luminance under which a pixel counts as a dark zone
QUADRANT_GAP = 12.0  # luminance points between quadrants above which a tile reads as irregular
SEAM_RATIO = 1.5     # a seam worse than this many times the natural grain is a visible join
CONTACT_BAND = 0.03  # share of the height taken as the ground-contact band
SHAPE_TOLERANCE = 0.35  # relative gap allowed between the measured and declared shape ratio

GROUND_TYPES = ("sol", "chemin")


def luminance(rgb):
    return (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).astype(numpy.float32)


def background_block(rgb):
    """The four border strips: how magenta they are, and how uniform."""
    height, width = rgb.shape[:2]
    margin = max(2, int(width * BORDER))
    strips = numpy.concatenate([
        rgb[:margin, :].reshape(-1, 3), rgb[-margin:, :].reshape(-1, 3),
        rgb[:, :margin].reshape(-1, 3), rgb[:, -margin:].reshape(-1, 3),
    ])
    measured = key_color.distance(strips)
    mean = strips.mean(axis=0)
    spread = float(numpy.mean(numpy.max(numpy.abs(strips.astype(numpy.float32) - mean), axis=1)))

    return {
        "magenta": 100 * float(key_color.is_background(measured).mean()),
        "mean": tuple(int(round(channel)) for channel in mean),
        "spread": spread,
        "uniform": spread < 12,
    }


def subject_mask(rgb, alpha):
    """What is subject: the opaque part when there is alpha, everything not magenta otherwise."""
    if alpha is not None:
        return alpha > 0
    return ~key_color.is_background(key_color.distance(rgb))


def box_block(mask):
    height, width = mask.shape
    rows = numpy.flatnonzero(mask.any(axis=1))
    columns = numpy.flatnonzero(mask.any(axis=0))
    if rows.size == 0:
        return None

    return {
        "width": 100 * (int(columns[-1]) - int(columns[0]) + 1) / width,
        "height": 100 * (int(rows[-1]) - int(rows[0]) + 1) / height,
        "margin_top": 100 * int(rows[0]) / height,
        "margin_bottom": 100 * (height - 1 - int(rows[-1])) / height,
    }


def transparency_block(rgb, alpha):
    """Effective transparency after the cutout, and whether any opaque magenta survived it."""
    if alpha is None:
        return None
    opaque = alpha >= 250
    leftover = float((opaque & key_color.is_background(key_color.distance(rgb))).mean())

    return {
        "fully_transparent": 100 * float((alpha == 0).mean()),
        "partial": 100 * float(((alpha > 0) & (alpha < 250)).mean()),
        "opaque_magenta": 100 * leftover,
        "keyed": bool((alpha == 0).any()) and leftover < 0.01,
    }


def footprint_block(mask, profile):
    """The apparent ground contact, confronted with the referentiel's declared footprint."""
    height, width = mask.shape
    rows = numpy.flatnonzero(mask.any(axis=1))
    columns = numpy.flatnonzero(mask.any(axis=0))
    if rows.size == 0:
        return None
    top, bottom = int(rows[0]), int(rows[-1])
    silhouette_height = bottom - top + 1
    silhouette_width = int(columns[-1]) - int(columns[0]) + 1
    band = max(1, int(round(silhouette_height * CONTACT_BAND)))
    contact_columns = numpy.flatnonzero(mask[bottom - band + 1: bottom + 1, :].any(axis=0))
    contact_width = int(contact_columns[-1]) - int(contact_columns[0]) + 1

    block = {
        "contact_px": contact_width,
        "silhouette_px": {"width": silhouette_width, "height": silhouette_height},
        "anchor_px": {"x": (int(contact_columns[0]) + int(contact_columns[-1])) / 2,
                      "y": float(bottom + 1)},
        "measured_ratio": silhouette_width / silhouette_height,
    }
    if profile is None:
        block["declared"] = None
        return block

    block["declared"] = {"columns": profile.footprint["columns"], "rows": profile.footprint["rows"],
                         "height": profile.height}
    if profile.height:
        expected = profile.footprint["columns"] / profile.height
        block["declared_ratio"] = expected
        block["gap"] = abs(block["measured_ratio"] - expected) / expected
        block["consistent"] = block["gap"] <= SHAPE_TOLERANCE

    return block


def tiling_block(rgb):
    """Edge-to-edge join: the seam created by repeating the tile, against its own column variation."""
    values = rgb.astype(numpy.float32)
    vertical_seam = float(numpy.mean(numpy.abs(values[:, 0] - values[:, -1])))
    horizontal_seam = float(numpy.mean(numpy.abs(values[0, :] - values[-1, :])))
    natural_columns = float(numpy.mean(numpy.abs(values[:, 1:] - values[:, :-1])))
    natural_rows = float(numpy.mean(numpy.abs(values[1:, :] - values[:-1, :])))
    vertical_ratio = vertical_seam / (natural_columns or 1)
    horizontal_ratio = horizontal_seam / (natural_rows or 1)

    return {
        "vertical_seam": vertical_seam, "horizontal_seam": horizontal_seam,
        "natural_columns": natural_columns, "natural_rows": natural_rows,
        "vertical_ratio": vertical_ratio, "horizontal_ratio": horizontal_ratio,
        "joins": vertical_ratio <= SEAM_RATIO and horizontal_ratio <= SEAM_RATIO,
    }


def regularity_block(rgb):
    """The largest luminance gap between the four quadrants of a material."""
    height, width = rgb.shape[:2]
    grey = luminance(rgb)
    means = [float(grey[:height // 2, :width // 2].mean()), float(grey[:height // 2, width // 2:].mean()),
             float(grey[height // 2:, :width // 2].mean()), float(grey[height // 2:, width // 2:].mean())]
    gap = max(means) - min(means)

    return {"gap": gap, "regular": gap < QUADRANT_GAP}


def light_block(rgb, mask):
    """Luminance and dark share, on the subject only — the background must not weigh in."""
    grey = luminance(rgb)[mask]
    if grey.size == 0:
        return None
    mean = float(grey.mean())
    dark = 100 * float((grey < DARK_LEVEL).mean())
    gaps = []
    if mean < LUMINANCE_MIN:
        gaps.append(f"{LUMINANCE_MIN - mean:.1f} under the band")
    elif mean > LUMINANCE_MAX:
        gaps.append(f"{mean - LUMINANCE_MAX:.1f} over the band")
    if dark > DARK_MAX:
        gaps.append(f"dark share {dark - DARK_MAX:.1f} pts over the ceiling")

    return {"luminance": mean, "dark": dark, "gaps": gaps, "within": not gaps}


def find_profile(data, path, forced=None):
    """The referentiel's sujet for a file: forced code, a code whose representation claims that file,
    or a code equal to the file's stem."""
    sujets = data["sujets"]
    if forced:
        if forced not in sujets:
            raise KeyError(f"unknown profile: {forced}")
        return _profile_of(forced, sujets[forced])
    try:
        relative = path.resolve().relative_to(ASSETS).as_posix()
    except ValueError:
        relative = None
    if relative:
        for code, sujet in sujets.items():
            for variant in sujet["variantes"]:
                for representation in variant.get("representations", []):
                    if representation["path"] == relative:
                        return _profile_of(code, sujet)
    stem = path.stem
    if stem in sujets:
        return _profile_of(stem, sujets[stem])

    return None


def _profile_of(code, sujet):
    return Profile(code, sujet["type"], sujet["emprise"], sujet.get("hauteur"))


def report(path, profile):
    raw = Image.open(path)
    alpha = None
    if raw.mode in ("RGBA", "LA"):
        alpha = numpy.asarray(raw.convert("RGBA").getchannel("A"))
    rgb = numpy.asarray(raw.convert("RGB"))
    height, width = rgb.shape[:2]
    is_ground = profile is not None and profile.type in GROUND_TYPES
    if profile is None and path.parent.name in ("sol", "chemin"):
        is_ground = True

    print(f"\n{path.name}  {width}x{height}  "
          f"{'square' if width == height else f'ratio {width / height:.2f}'}  "
          f"alpha: {'yes' if alpha is not None else 'no'}  "
          f"profile: {profile.code if profile else 'NOT IN REFERENTIEL'}")

    if alpha is None and not is_ground:
        block = background_block(rgb)
        print(f"  background   {block['magenta']:.1f} % magenta on the borders, mean {block['mean']}, "
              f"spread {block['spread']:.1f}  ({'UNIFORM' if block['uniform'] else 'NOT UNIFORM'})")

    transparency = transparency_block(rgb, alpha)
    if transparency is not None:
        # A ground material fills its frame edge to edge: it has no background, so nothing to key.
        verdict = ("no background to key" if is_ground
                   else "KEYED" if transparency["keyed"] else "NOT KEYED")
        print(f"  transparency {transparency['fully_transparent']:.1f} % fully transparent, "
              f"{transparency['partial']:.2f} % partial, "
              f"{transparency['opaque_magenta']:.3f} % opaque magenta left  ({verdict})")

    mask = subject_mask(rgb, alpha)
    if not is_ground:
        box = box_block(mask)
        if box is None:
            print("  subject      NOTHING BUT BACKGROUND")
            return
        # Framing is only a question on the generator's output; a cut-out sprite fills its own box by
        # construction, so saying "full frame" about it would mean nothing.
        if alpha is None:
            print(f"  subject      {box['width']:.0f} % of the width, {box['height']:.0f} % of the "
                  f"height; margins {box['margin_top']:.0f} % top, {box['margin_bottom']:.0f} % bottom "
                  f" ({'full frame' if box['height'] >= 65 else 'SUBJECT TOO SMALL'})")

        footprint = footprint_block(mask, profile)
        if footprint:
            line = (f"  footprint    contact {footprint['contact_px']} px over a silhouette of "
                    f"{footprint['silhouette_px']['width']}x{footprint['silhouette_px']['height']} px, "
                    f"anchor at ({footprint['anchor_px']['x']:.1f}, {footprint['anchor_px']['y']:.0f}); "
                    f"shape ratio {footprint['measured_ratio']:.3f}")
            if footprint.get("declared_ratio") is not None:
                line += (f" vs declared {footprint['declared_ratio']:.3f} "
                         f"({footprint['declared']['columns']}x{footprint['declared']['rows']} tiles, "
                         f"height {footprint['declared']['height']}) — gap {100 * footprint['gap']:.0f} % "
                         f"({'CONSISTENT' if footprint['consistent'] else 'INCONSISTENT'})")
            elif profile is None:
                line += "  — no declared footprint to compare with (sujet absent from the referentiel)"
            else:
                line += "  — the profile declares no height, so no comparison is possible"
            print(line)
    else:
        tiling = tiling_block(rgb)
        print(f"  tiling       seam {tiling['vertical_seam']:.1f} vertical / "
              f"{tiling['horizontal_seam']:.1f} horizontal against a natural variation of "
              f"{tiling['natural_columns']:.1f} / {tiling['natural_rows']:.1f}  "
              f"(x{tiling['vertical_ratio']:.2f} / x{tiling['horizontal_ratio']:.2f} — "
              f"{'JOINS EDGE TO EDGE' if tiling['joins'] else 'VISIBLE JOIN'})")
        regular = regularity_block(rgb)
        print(f"  regularity   {regular['gap']:.1f} luminance points between quadrants  "
              f"({'regular' if regular['regular'] else 'IRREGULAR'})")

    light = light_block(rgb, mask)
    if light:
        print(f"  light        luminance {light['luminance']:.1f} (band {LUMINANCE_MIN:.0f}-"
              f"{LUMINANCE_MAX:.0f}), dark share {light['dark']:.1f} % (ceiling {DARK_MAX:.0f} %)  "
              + ("WITHIN THE BAND" if light["within"] else "OUT OF BAND — " + ", ".join(light["gaps"])))


def main(arguments):
    forced = None
    if "--code" in arguments:
        index = arguments.index("--code")
        forced = arguments[index + 1]
        arguments = arguments[:index] + arguments[index + 2:]
    if not arguments:
        print(__doc__)
        return 2

    try:
        data = check_sujets.load()
    except check_sujets.Fault as fault:
        print(f"FAULT {fault}")
        return 1
    missing = 0
    for argument in arguments:
        path = Path(argument)
        if not path.is_absolute():
            path = ASSETS / argument
        if not path.is_file():
            print(f"ABSENT {path}")
            missing += 1
            continue
        report(path, find_profile(data, path, forced))

    print("\nNote — the footprint is confronted on the shape ratio, not on an absolute count of tiles. "
          "The world is seen under a 70° camera, which foreshortens the vertical; turning a horizontal "
          "ground extent into tiles with a scale read off a standing height would therefore be wrong, "
          "and the design fixes no projection for it. Settling that belongs to the render port.")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
