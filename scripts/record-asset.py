#!/usr/bin/env python3
"""Export a produced image and inscribe it in the referentiel — the last steps of the chain, in one
gesture.

The design forbids keeping the referentiel by hand ("Le catalogue s'écrit à l'entrée, jamais à la
main"), because a hand-kept file and the disk diverge within a week. This is the only writer.

It resizes the master to delivery definition (export-asset.py), writes the sprite under
assets/cutout/, and records it in assets/sujets.json: the sujet (created together with its first
variant if the code is new), the variant it belongs to, and the representation itself — livrable path,
master path, image number, and the measures the export took.

The referentiel keeps versions instead of overwriting, and does not identify a variant by a computed
ref string: it stores the same fields (orientation, action, shape, and a type's own variant
fields) as plain keys, so this tool does too, instead of building and parsing a string nothing else
needs.

Usage:
  python3 record-asset.py <source> --code <XX-nnn> --type <type> \\
      [--name <kind-nn>] [--footprint <columns>x<rows>] [--height <tiles>] \\
      [--variant <ref>] [--frame <n>] [--dry-run]

  <source>     path relative to assets/, or absolute
  --type       must be one of the types the referentiel already declares
  --variant    the REF of the variant, as the referentiel writes it — e.g.
               orientation-south_action-idle_shape-ns_posts-1_frame-01. Left out, the main view's.
               An unknown ref is refused: a variant is declared before it is produced.
  --frame      the image's own number within its variant (glossaire: frame-01, frame-02...) — not a
               version number, defaults to 1
  --dry-run    show what would be written, touch nothing
"""
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# export-asset.py and check-sujets.py are hyphenated, so they are loaded by path rather than imported
# by name. The deliverable is the master resized: this tool records that one, never a second copy of
# its own making.
EXPORT = Path(__file__).resolve().parent / "export-asset.py"
spec = importlib.util.spec_from_file_location("export_asset", EXPORT)
export_asset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_asset)

CHECK_SUJETS = Path(__file__).resolve().parent / "check-sujets.py"
spec = importlib.util.spec_from_file_location("check_sujets", CHECK_SUJETS)
check_sujets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_sujets)

SUJETS = check_sujets.SUJETS  # assets/sujets.json — one path, held by the checker, not recopied here

def parse_footprint(text):
    columns, _, rows = text.partition("x")

    # Whole tiles, never fractional — and the referentiel's own checker requires an int
    # (check-sujets.py, check_schema): a float footprint would write a sujet its own gate refuses.
    return {"columns": int(columns), "rows": int(rows or columns)}


MAIN_VIEW_REF = "orientation-south_action-idle_frame-01"


def matching_variant(sujet, ref):
    """The variant of `sujet` that goes by this ref.

    A variant is designated by its ref and by nothing else — the ref is its identifier, written in the referentiel, never recomputed (sujets-et-variantes.md).
    This used to compare the fields one by one, absence included, which is a second way of saying the same thing and a second way of getting it wrong.
    """
    for variant in sujet["variants"]:
        if variant.get("ref") == ref:
            return variant

    return None


def record(data, code, type_name, ref, name=None, footprint=None, height=None):
    """Find the sujet and the variant this ref designates, and return the variant ready to receive a new
    representation. A sujet and its first variant are created TOGETHER: the referentiel refuses a
    sujet without at least one variant (check-sujets.py), so there is never a moment where the file
    would hold one without the other.

    A variant is never invented here: its ref is written in the referentiel by whoever declares it, so
    an unknown ref is a fault and not an invitation to create one under a name nobody chose.
    """
    types = data["types"]
    if type_name not in types:
        raise SystemExit(f"FAULT type inconnu : {type_name!r} — attendu parmi {sorted(types)} "
                         f"(le référentiel, plus l'ancienne liste du catalogue gelé)")

    sujet = data["sujets"].get(code)
    if sujet is None:
        sujet = {
            "profil": name, "type": type_name,
            "emprise": footprint or {"columns": 1, "rows": 1},
            "hauteur": height,
            "variants": [{"ref": ref, "orientation": "south", "action": "idle", "shape": "plain",
                           "principale": True, "representations": []}],
        }
        data["sujets"][code] = sujet
    else:
        if footprint is not None:
            sujet["emprise"] = footprint
        if height is not None:
            sujet["hauteur"] = height
        if name is not None:
            sujet["profil"] = name

    variant = matching_variant(sujet, ref)
    if variant is None:
        known = [entry.get("ref") for entry in sujet["variants"]]
        raise SystemExit(f"FAULT {code} n'a aucune variante de ref {ref!r} — une variante se déclare au référentiel avant d'être produite. Déclarées : {known}")

    return variant


def add_representation(variant, representation):
    """Add a new version, never overwrite one, and NEVER drop one — the referentiel keeps every version
    an image has ever had (operator, 2026-08-05: on garde tout, on versionne tout).

    It used to drop the oldest beyond three kept: the file lost its entry while the image stayed on
    disk, and the image became an orphan that no variant claimed — a fault by the referentiel's own
    checker, born of a rule that was meant to keep things. How many versions are SHOWN is a question for
    the review page and for it alone; it is not a reason to forget one here.
    """
    representations = variant.setdefault("representations", [])
    for previous in representations:
        if previous.get("statut") == "courante":
            previous["statut"] = "anterieure"
    representations.insert(0, representation)


def main(arguments):
    options = {}
    positional = []
    index = 0
    while index < len(arguments):
        token = arguments[index]
        if token == "--dry-run":
            options["dry_run"] = True
            index += 1
        elif token.startswith("--"):
            options[token[2:]] = arguments[index + 1]
            index += 2
        else:
            positional.append(token)
            index += 1
    if not positional or "code" not in options or "type" not in options:
        print(__doc__)
        return 2

    source = Path(positional[0])
    if not source.is_absolute():
        source = export_asset.ASSETS / positional[0]
    if not source.is_file():
        print(f"ABSENT {source}")
        return 1

    code = options["code"]
    frame = int(options.get("frame", 1))
    footprint = parse_footprint(options["footprint"]) if "footprint" in options else None
    height = float(options["height"]) if "height" in options else None

    try:
        data = check_sujets.load()
    except check_sujets.Fault as fault:
        print(f"FAULT {fault}")
        return 1
    # The variant is named by its ref, the identifier the referentiel holds for it. Left out, it is the main view's — the ref every sujet's first variant has.
    ref = options.get("variant") or MAIN_VIEW_REF
    variant = record(data, code, options["type"], ref, options.get("name"), footprint, height)

    sprite, measures = export_asset.export(source)
    target = export_asset.destination(source)
    # Relative to assets/, never to the repository: every path already in the referentiel is written
    # this way (check-sujets.py's own scan_cutout/claimed_paths compare on exactly this form), and a
    # path written the other way would silently read back as an unclaimed file.
    relative_target = str(target.resolve().relative_to(export_asset.ASSETS))
    relative_source = str(source.resolve().relative_to(export_asset.ASSETS))
    # Exactly what the export measured, and nothing else.
    kept = {key: measures[key] for key in
            ("delivered_px", "silhouette_px", "contact_px", "anchor_px", "master_size_px",
             "kind", "footprint") if key in measures}
    representation = {
        "type": "sprite", "path": relative_target, "maitre": relative_source,
        "numero_image": frame, "mesures": kept, "statut": "courante",
    }
    add_representation(variant, representation)

    try:
        check_sujets.check_schema(data)
    except check_sujets.Fault as fault:
        print(f"FAULT le référentiel ne validerait plus après cet ajout : {fault}")
        return 1

    # The measures go into the referentiel, where they are read when needed; printing them here put
    # thirty lines into the caller's context at every image, for a fact that holds in one line. What
    # the launcher needs is what was recorded and where — the rest is in the file (execution.md).
    delivered = kept.get("delivered_px") or {}
    print(f"{code} / {ref} · frame {frame} · {delivered.get('width')} × {delivered.get('height')} px "
          f"→ {relative_target}")
    if options.get("dry_run"):
        print("  (dry run — nothing written)")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    sprite.save(target)
    SUJETS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  référentiel {SUJETS}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
