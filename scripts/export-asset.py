#!/usr/bin/env python3
"""Turn a master render into a deliverable: resized to delivery definition, nothing else.

Step 5 of the production chain, replacing the cutting step it used to hold. The master carries its own real alpha
— the generator stopped rendering a magenta field a while ago — so nothing here needs to be keyed,
cropped, de-fringed or hole-filled: the only thing separating a master from a deliverable is that the
delivery is not sized for a master's job (a wide margin for cascading references, a definition picked
for editing headroom). SCALING IT DOWN TO DELIVERY DEFINITION IS THE ONLY TRANSFORM THIS SCRIPT APPLIES.

WHY CROPPING WAS DROPPED
  The tool this replaces cropped a master to its opaque bounding box. That crop was a correction applied
  after the fact for a framing the CONSIGNE should have specified — and on a piece that assembles edge to
  edge, correcting after the fact is actively wrong: two pieces cropped each to their own silhouette stop
  lining up, because each keeps a different amount of empty margin. Measured on OB-010's east-west run,
  the crop had shaved twelve pixels off the piece's height relative to its neighbours.
  THE RULE THAT REPLACES IT: a badly framed master means the consigne under-specified the framing, and
  the consigne is what gets fixed — never the pixels. This script does not know how to fix a consigne,
  so it does not try; it only reports what it measures, so a wrong framing is visible rather than quietly
  papered over.

WHERE THE FOOTPRINT AND THE DELIVERY DEFINITION COME FROM
  The footprint and the type are asked of assets/subjects.json — the referentiel of sujets, by the
  inventory code the master's own file name starts with — never guessed here, never retyped. A code
  the referentiel does not carry is a briefing fault in itself: rien ne se produit sans fiche, so this
  tool refuses rather than fall back on assets/catalogue.json, which is FROZEN and never read here.
  The delivery definition is asked of tile_scale.py, the one service that owns it, in the form
  appropriate to what the code's TYPE actually is: a ground material ("sol") is delivered at an exact
  box, because it has to tile edge to edge; every other type is a sprite, delivered at a contractual
  WIDTH with its height following the master's own proportions — fixing a sprite's height would squash
  a tall subject's base off its own tiles.

A MASTER WHOSE DEFINITION IS NOT THE CLEAN ONE tile_scale EXPECTS IS A CONSIGNE FAULT, NOT THIS TOOL'S
  A master is asked, at generation time, for an exact width (sprite) or an exact box (tile) computed by
  tile_scale.master_definition(). If the file on disk does not match that, the consigne that produced it
  asked for the wrong thing, or was not followed — a fact about the CONSIGNE, not about this pixel data.
  This script SIGNALS the mismatch and refuses that file rather than silently resampling from a wrong
  starting point, which is exactly the kind of after-the-fact correction this tool exists to stop making.

  --force LIFTS ONLY THIS CHECK, FOR A NAMED, REVIEWED EXCEPTION — never a default, never silent. A
  handful of deliverables predate this tool's whole master/delivery contract: their master was never
  kept, so nothing here can be "corrected" back to one. Feeding their existing, oversized deliverable
  back in as the source and scaling it down is still exactly one thing — a scale, alpha untouched, no
  crop — so it is the same operation this tool always performs; --force only says a human already
  looked at this particular file and decided its size mismatch is not a fresh mistake to chase.

WHAT THIS SCRIPT MEASURES, NOT DECIDES
  silhouette    the opaque bounding box of the delivered image, in pixels and as a share of it
  contact       the opaque span on the bottom band of the silhouette — the apparent ground width
  anchor        the pose point, in pixels: middle of that contact span, on the silhouette's bottom edge
  These are read off the delivered pixels and reported for the catalogue to record — never acted on by
  this script itself. A subject that overflows its footprint or floats clear of its base is not fixed
  here; it is measured, so the fault is visible where it belongs.

Usage:
  python3 export-asset.py <path> [...]        paths under assets/poc/, or absolute
  python3 export-asset.py --dry-run <path>    measure only, write nothing
  python3 export-asset.py --out <dir> <path>  write elsewhere than assets/cutout/
  python3 export-asset.py -h|--help           this text
  python3 export-asset.py --force <path>      export despite a briefing-fault mismatch — reviewed
                                               case by case, see --force above; never the default
"""
import json
import re
import sys
from pathlib import Path

import numpy
from PIL import Image


sys.path.insert(0, str(Path(__file__).resolve().parent))
import tile_scale

REPOSITORY = Path(__file__).resolve().parents[1]
ASSETS = REPOSITORY / "assets"
CUTOUT = ASSETS / "cutout"
SUBJECTS = ASSETS / "subjects.json"

CONTACT_BAND = 0.03  # share of the silhouette height taken as the ground-contact band, unchanged rule

# The referentiel says which type is a ground material — the one case delivered as an exact box rather
# than at a contractual width. Kept here as the single fact this script needs from its richer type
# list, rather than reading and interpreting the whole referentiel structure.
TILE_TYPE = "sol"

CODE_PATTERN = re.compile(r"^([A-Z]{2,3}-\d{3}(?:-\d+)?)")


def code_of(path):
    """The inventory code a master's file name starts with — the only association this tool makes;
    it never guesses one for a file the catalogue does not already know."""
    match = CODE_PATTERN.match(path.stem)
    if not match:
        raise ValueError(f"cannot read an inventory code off {path.name}")

    return match.group(1)


def profile_of(code):
    """Ask the referentiel of sujets for a code's type and footprint — never guessed, never retyped,
    and never asked of assets/catalogue.json, which is frozen.

    A code the referentiel does not carry is refused: rien ne se produit sans fiche, and fabricating a
    footprint here would be exactly the kind of invention the referentiel exists to rule out.
    """
    data = json.loads(SUBJECTS.read_text(encoding="utf-8"))
    subject = data.get("subjects", {}).get(code)
    if subject is None:
        raise ValueError(f"FAULT {code}: absent de assets/subjects.json — rien ne s'exporte sans fiche")
    # LE COUVERT D'ABORD, L'EMPRISE À DÉFAUT — la même lecture que la génération, et c'est tout l'objet de cette ligne. L'image est demandée à la largeur de ce que le volume
    # SURPLOMBE ; la mesurer contre ce qui touche le SOL refusait toute image juste d'un sujet dont la couronne déborde de son pied. Constaté sur le sapin puis sur le
    # pommier : deux générations correctes jetées parce que les deux bouts de la chaîne ne lisaient pas la même étendue.
    spread = subject.get("cover") or subject["footprint"]
    footprint = int(spread["columns"]), int(spread["rows"])

    return subject["type"], footprint, subject.get("height")


def variant_of(code, variant_ref):
    """The variant a ref designates, read from the referentiel. An absent ref is a fault: the band lives on the variant, so without it there is nothing to check
    against — and inventing a subject-wide fallback is exactly the derivation that was retired on 2026-08-10."""
    if not variant_ref:
        raise ValueError(f"FAULT {code}: aucune ref de variante donnée — la fourchette de hauteur se déclare au variant, passez --variant <ref>.")
    data = json.loads(SUBJECTS.read_text(encoding="utf-8"))
    for variant in data["subjects"][code].get("variants", []):
        if variant.get("ref") == variant_ref:
            return variant
    known = ", ".join(variant.get("ref", "?") for variant in data["subjects"][code].get("variants", []))
    raise ValueError(f"FAULT {code}: aucune variante de ref {variant_ref!r}. Déclarées : {known}")


def briefing_fault(kind, footprint, master_size, declared_height=None):
    """None if the master matches what its own consigne should have asked tile_scale for; otherwise
    the sentence explaining the mismatch, for the caller to report rather than resample around.
    """
    expected = tile_scale.master_definition(*footprint)
    width, height = master_size
    columns, rows = footprint
    if kind == "tile":
        if (width, height) != (expected["width"], expected["height"]):
            return (f"master is {width}x{height}px, tile_scale expects exactly "
                    f"{expected['width']}x{expected['height']}px for a {columns}x{rows} tile")
        return None
    if width != expected["width"]:
        return (f"master is {width}px wide, tile_scale expects exactly {expected['width']}px for a "
                f"{columns}x{rows} footprint")
    return None


def height_verdict(footprint, master_size, code, variant_ref):
    """Whether the master's height sits in the band ITS VARIANT DECLARES — a VERDICT, never a refusal.

    A validator measures and says whether a criterion holds; it refuses nothing and corrects nothing (operator, 2026-08-06, doc/glossaire.md). This one was
    written as a fatal fault first, and it blocked a path that was perfectly good — exactly the confusion the rule exists to prevent.

    The band matters because nothing else watched the height: a care centre came out twelve tiles tall for eight declared, a thicket at 1.6 for six, and the
    whole mock-up looked wrongly calibrated with no measure to say why. No single height is right — a ridge, a chimney, a leaning crown move it — but there is a
    floor and a ceiling, and since 2026-08-10 BOTH ARE DECLARED ON THE VARIANT rather than derived from the subject's height: no formula can know that a tuft of
    grass is low and an oak towers, and a variant that lies down is not the height of the same variant standing.

    Returns (kept, sentence): kept says whether the criterion holds, the sentence says what was measured against what.
    """
    columns, rows = footprint
    variant = variant_of(code, variant_ref)
    low, high = tile_scale.variant_band(columns, rows, variant, f"{code} / {variant_ref}")
    drawn = master_size[1]
    sentence = (f"hauteur {round(drawn / tile_scale.ty_in_pixels(columns, rows), 2)} TY pour une fourchette déclarée de "
                f"{variant['height_min_ty']} à {variant['height_max_ty']} TY")

    return low <= drawn <= high, sentence


def measure(alpha):
    """The apparent footprint and pose point, read off the delivered image's own alpha channel —
    reported, never acted on."""
    height, width = alpha.shape
    opaque = alpha > 0.0
    rows = numpy.flatnonzero(opaque.any(axis=1))
    columns = numpy.flatnonzero(opaque.any(axis=0))
    if rows.size == 0:
        return None
    left, right = int(columns[0]), int(columns[-1])
    top, bottom = int(rows[0]), int(rows[-1])
    band_height = max(1, int(round(height * CONTACT_BAND)))
    band = opaque[bottom - band_height + 1: bottom + 1, :]
    band_columns = numpy.flatnonzero(band.any(axis=0))
    contact_left, contact_right = int(band_columns[0]), int(band_columns[-1])

    return {
        "delivered_px": {"width": width, "height": height},
        "silhouette_px": {"left": left, "top": top, "right": right, "bottom": bottom,
                          "width": right - left + 1, "height": bottom - top + 1},
        "silhouette_share": {"width": round(100 * (right - left + 1) / width, 1),
                             "height": round(100 * (bottom - top + 1) / height, 1)},
        "contact_px": {"left": contact_left, "right": contact_right,
                       "width": contact_right - contact_left + 1},
        "anchor_px": {"x": round((contact_left + contact_right) / 2, 1), "y": float(bottom + 1)},
    }


def export(path, force=False, variant_ref=None):
    """Resize one master to delivery definition. Returns (RGBA image, measures). Nothing written here.

    Raises on a briefing fault unless force=True: refusing is the whole point — resampling from a
    master that was not what its own consigne should have produced would only hide the fault inside a
    plausible-looking file. force is for the one reviewed exception (see --force in the module doc):
    the fault still gets INTO the measures, it is just not fatal.
    """
    code = code_of(path)
    type_name, footprint, height = profile_of(code)
    kind = "tile" if type_name == TILE_TYPE else "sprite"

    source = Image.open(path).convert("RGBA")
    fault = briefing_fault(kind, footprint, source.size, height)
    if fault and not force:
        raise ValueError(f"FAULT {path.name}: {fault}")
    # LA HAUTEUR EST UN VERDICT, PAS UN REFUS : elle se mesure, elle se dit, et elle laisse passer. Un validateur constate qu'un critère est tenu ou non ; il ne
    # refuse rien (opérateur, 2026-08-06). Rapportée au lanceur dans sa sortie à lui, et écrite dans les mesures pour que la page de suivi puisse la montrer.
    kept, sentence = height_verdict(footprint, source.size, code, variant_ref)
    if not kept:
        print(f"HORS FOURCHETTE {path.name} : {sentence}")

    if kind == "tile":
        delivered = tile_scale.delivery_size(*footprint)
    else:
        delivered = tile_scale.delivery_box(footprint[0], source.size[0], source.size[1])

    # Resampling is the one transform this tool applies. LANCZOS resamples colour and alpha together,
    # exactly as it would any other channel — no cropping, no retouching, no keying.
    resized = source.resize((delivered["width"], round(delivered["height"])), Image.LANCZOS)
    alpha = numpy.asarray(resized)[:, :, 3].astype(numpy.float32) / 255.0

    measures = measure(alpha)
    measures["master_size_px"] = {"width": source.size[0], "height": source.size[1]}
    measures["kind"] = kind
    measures["footprint"] = {"columns": footprint[0], "rows": footprint[1]}
    measures["height"] = {"tenue": kept, "constat": sentence}
    if fault:
        measures["briefing_fault_overridden"] = fault

    return resized, measures


def destination(path, out=None):
    """Where the deliverable goes: assets/cutout/<same relative path>, the master left untouched.

    THE ASSET THEME IS CARRIED BY THE MASTER'S OWN LOCATION, and that is why nothing here names it. The generator already writes its master under assets/poc/<theme subtree>/<type>/, so mirroring
    the master's relative path puts the deliverable under assets/cutout/<theme subtree>/<type>/ on its own. Reading the theme here would be a second source for the same answer — and a second
    source is a chance for the two to disagree. scripts/check-asset-theme.php is what keeps that promise honest.
    """
    if out:
        return Path(out) / path.name
    try:
        relative = path.resolve().relative_to(ASSETS)
    except ValueError:
        return CUTOUT / path.name
    # Drop the leading production folder (poc/, revue-da/...) so deliverables sit by type.
    parts = relative.parts[1:] if len(relative.parts) > 1 else relative.parts

    return CUTOUT.joinpath(*parts)


def main(arguments):
    dry_run = "--dry-run" in arguments
    force = "--force" in arguments
    arguments = [argument for argument in arguments if argument not in ("--dry-run", "--force")]
    # THE HEIGHT BAND LIVES ON THE VARIANT, so the validator has to be told WHICH variant it is looking at (operator, 2026-08-10). The file name alone names the
    # subject and never the variant, and two variants of one subject may legitimately come back at different heights — an oak standing and the same oak lying down.
    variant_ref = None
    if "--variant" in arguments:
        index = arguments.index("--variant")
        variant_ref = arguments[index + 1]
        arguments = arguments[:index] + arguments[index + 2:]
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
        try:
            deliverable, measures = export(path, force=force, variant_ref=variant_ref)
        except ValueError as error:
            print(str(error))
            failed += 1
            continue
        target = destination(path, out)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            deliverable.save(target)
        print(f"{path.name} -> {'(dry run)' if dry_run else target}")
        print(json.dumps(measures, indent=2))

    return 1 if failed else 0


if __name__ == "__main__":
    # ASKED HERE AND NOT AT MODULE LEVEL: record-asset.py imports this file by path, and a guard on the
    # import path would stop it the moment it is itself called with --help.
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        raise SystemExit(0)
    sys.exit(main(sys.argv[1:]))
