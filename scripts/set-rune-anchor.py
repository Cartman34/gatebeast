#!/usr/bin/env python3
"""Pose the rune anchor of one representation — the point the renderer draws that individual's rune on.

Usage:
  python3 scripts/set-rune-anchor.py --path cutout/creature/SP-001.png --x 48 --y 54 [--tilt 0] [--dry-run]
  python3 scripts/set-rune-anchor.py --list
  python3 scripts/set-rune-anchor.py -h|--help — this text

  --path is the delivered path of the representation, as the referential spells it. --x and --y are read off the image, in its own
  pixels, origin top left — `python3 scripts/dev/draw-anchor-grid.py <image>` draws the grid they are read from. --tilt is the
  inclination in degrees, for a surface that is not facing the viewer; it defaults to 0, which is a plain upright rune.

Intention:
  THE ANCHOR IS POSED BY EYE, ONE PER IMAGE, AND NOTHING COMPUTES IT (referentiels/technique/rendu-en-calques.md). The renderer never
  looks for a forehead and never follows a posture: it applies what the image declares. So this value has to be written by somebody
  looking at the sprite — and the one thing a tool can do is make sure that what they write lands in the right place, in the right
  spelling, and inside the image.

  IT REFUSES RATHER THAN GUESSES. An unknown path, a point outside the delivered image, a representation that carries no measures:
  each stops the command and names what was wrong. The alternative — writing the anchor onto the first representation that looks
  close enough — produces a referential that is wrong in a way no one can see, which is the failure this project forbids by name.

  Python rather than PHP because it rewrites the same referential as record-asset.py and set-asset-verdict.py, and all of them load
  and dump it through check-subjects.py, which holds that one spelling.
"""

import argparse
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Loaded by path because the file name carries a dash: it is the same import record-asset.py does, for the same reason.
_spec = importlib.util.spec_from_file_location("check_subjects", ROOT / "scripts" / "check-subjects.py")
check_subjects = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_subjects)

ANCHOR_KEY = "rune_anchor_px"
CREATURE_TYPE = "creature"


def representations(data):
    """Every representation of the referential, with the code and the variant it belongs to."""
    for code, subject in data["subjects"].items():
        for variant in subject.get("variants", []):
            for representation in variant.get("representations", []):
                yield code, subject, variant, representation


def find(data, wanted):
    found = [item for item in representations(data) if item[3].get("path") == wanted]
    if not found:
        raise SystemExit(f"FAULT aucune représentation n'a le chemin « {wanted} » — « --list » donne celles qui attendent une ancre.")
    if len(found) > 1:
        raise SystemExit(f"FAULT le chemin « {wanted} » est porté par {len(found)} représentations — le référentiel a un doublon.")
    return found[0]


def show_missing(data):
    missing = [(code, item.get("path")) for code, subject, variant, item in representations(data)
               if subject.get("type") == CREATURE_TYPE and ANCHOR_KEY not in item]
    if not missing:
        print("Toutes les représentations de créature portent leur ancre de rune.")
        return
    print(f"{len(missing)} représentation(s) de créature sans ancre de rune :")
    for code, path in missing:
        print(f"  {code}  {path}")


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--path")
    parser.add_argument("--x", type=float)
    parser.add_argument("--y", type=float)
    parser.add_argument("--tilt", type=float, default=0.0)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()

    data = check_subjects.load()
    if arguments.list:
        show_missing(data)
        return
    if arguments.path is None or arguments.x is None or arguments.y is None:
        raise SystemExit("FAULT il faut « --path », « --x » et « --y » — ou « --list » pour voir ce qui attend une ancre.")

    code, subject, variant, representation = find(data, arguments.path)
    if subject.get("type") != CREATURE_TYPE:
        raise SystemExit(f"FAULT « {code} » n'est pas une créature : seule une créature porte une rune.")
    # THE POINT IS CHECKED AGAINST THE IMAGE IT IS POSED ON: outside it, the renderer would draw the rune beside the beast, and
    # nothing downstream would notice — the sprite would simply look unmarked.
    delivered = (representation.get("measures") or {}).get("delivered_px")
    if not delivered:
        raise SystemExit(f"FAULT la représentation « {arguments.path} » n'a pas de mesures : sa taille livrée est inconnue.")
    if not (0 <= arguments.x <= delivered["width"] and 0 <= arguments.y <= delivered["height"]):
        raise SystemExit(f"FAULT le point ({arguments.x}, {arguments.y}) est hors de l'image livrée "
                         f"({delivered['width']}×{delivered['height']} px).")

    representation[ANCHOR_KEY] = {"x": arguments.x, "y": arguments.y, "tilt_deg": arguments.tilt}
    if arguments.dry_run:
        print(f"{code} — {arguments.path} : ancre ({arguments.x}, {arguments.y}), inclinaison {arguments.tilt}° — rien écrit.")
        return
    check_subjects.save(data)
    print(f"{code} — {arguments.path} : ancre de rune posée en ({arguments.x}, {arguments.y}), inclinaison {arguments.tilt}°.")


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        raise SystemExit(0)
    sys.exit(main())
