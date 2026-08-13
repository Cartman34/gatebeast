#!/usr/bin/env python3
"""Export a produced image and inscribe it in the referentiel — the last steps of the chain, in one
gesture.

The design forbids keeping the referentiel by hand ("Le catalogue s'écrit à l'entrée, jamais à la
main"), because a hand-kept file and the disk diverge within a week. This is the only writer.

It resizes the master to delivery definition (export-asset.py), writes the sprite under
assets/cutout/, and records it in assets/subjects.json: the sujet (created together with its first
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
  --session    the generator session this image came out of, as generate-image.php reports it. Left
               out, the version records `null`: an image nobody can attribute to a session is a fact,
               not a fault, and it is written down as such rather than guessed at.
  --dry-run    show what would be written, touch nothing
  -h|--help    this text

THE SESSION BELONGS TO THE VERSION, NOT TO A REPORT (operator, 2026-08-13). It was captured at
generation and written only into var/generations/, which is not versioned: the id then existed on one
machine, until the next cleanup, and for nobody else — two versions had already lost theirs by
2026-08-13, which the sprites page prints at every build. Recorded here it lives in a versioned file,
beside the path and the measures of the very version it produced.

WHERE THE SESSION WAS LAUNCHED IS NOT RECORDED, AND THAT IS A DECISION. A session can only be reopened
from its own launch directory, so the directory matters — but generate-image.php pins it to the
project root for every generation there has ever been (its PROJECT_ROOT, so that all the project's
sessions are listed in one place). It is therefore a constant, not a property of a version, and
writing it onto each of them would copy one value two hundred times over.
"""
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# export-asset.py and check-subjects.py are hyphenated, so they are loaded by path rather than imported
# by name. The deliverable is the master resized: this tool records that one, never a second copy of
# its own making.
EXPORT = Path(__file__).resolve().parent / "export-asset.py"
spec = importlib.util.spec_from_file_location("export_asset", EXPORT)
export_asset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_asset)

CHECK_SUBJECTS = Path(__file__).resolve().parent / "check-subjects.py"
spec = importlib.util.spec_from_file_location("check_subjects", CHECK_SUBJECTS)
check_subjects = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_subjects)

SUBJECTS = check_subjects.SUBJECTS  # assets/subjects.json — one path, held by the checker, not recopied here

def parse_footprint(text):
    columns, _, rows = text.partition("x")

    # Whole tiles, never fractional — and the referentiel's own checker requires an int
    # (check-subjects.py, check_schema): a float footprint would write a sujet its own gate refuses.
    return {"columns": int(columns), "rows": int(rows or columns)}


MAIN_VIEW_REF = "orientation-south_action-idle_frame-01"


def matching_variant(subject, ref):
    """The variant of `sujet` that goes by this ref.

    A variant is designated by its ref and by nothing else — the ref is its identifier, written in the referentiel, never recomputed (sujets-et-variantes.md).
    This used to compare the fields one by one, absence included, which is a second way of saying the same thing and a second way of getting it wrong.
    """
    for variant in subject["variants"]:
        if variant.get("ref") == ref:
            return variant

    return None


def record(data, code, type_name, ref, name=None, footprint=None, height=None):
    """Find the sujet and the variant this ref designates, and return the variant ready to receive a new
    representation. A sujet and its first variant are created TOGETHER: the referentiel refuses a
    sujet without at least one variant (check-subjects.py), so there is never a moment where the file
    would hold one without the other.

    A variant is never invented here: its ref is written in the referentiel by whoever declares it, so
    an unknown ref is a fault and not an invitation to create one under a name nobody chose.
    """
    types = data["types"]
    if type_name not in types:
        raise SystemExit(f"FAULT type inconnu : {type_name!r} — attendu parmi {sorted(types)} "
                         f"(le référentiel, plus l'ancienne liste du catalogue gelé)")

    subject = data["subjects"].get(code)
    if subject is None:
        subject = {
            "profile": name, "type": type_name,
            "footprint": footprint or {"columns": 1, "rows": 1},
            "height": height,
            "variants": [{"ref": ref, "orientation": "south", "action": "idle", "shape": "plain",
                           "main": True, "representations": []}],
        }
        data["subjects"][code] = subject
    else:
        if footprint is not None:
            subject["footprint"] = footprint
        if height is not None:
            subject["height"] = height
        if name is not None:
            subject["profile"] = name

    variant = matching_variant(subject, ref)
    if variant is None:
        known = [entry.get("ref") for entry in subject["variants"]]
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
        if previous.get("status") == "current":
            previous["status"] = "previous"
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
        data = check_subjects.load()
    except check_subjects.Fault as fault:
        print(f"FAULT {fault}")
        return 1
    # The variant is named by its ref, the identifier the referentiel holds for it. Left out, it is the main view's — the ref every sujet's first variant has.
    ref = options.get("variant") or MAIN_VIEW_REF
    variant = record(data, code, options["type"], ref, options.get("name"), footprint, height)

    # The ref travels to the export because the height band lives on the VARIANT since 2026-08-10, and the export judges the image against it. Left out, the export
    # refuses — rightly: a file name names the subject, never the variant, and two variants of one subject may legitimately come back at different heights.
    sprite, measures = export_asset.export(source, variant_ref=ref)
    target = export_asset.destination(source)
    # THE THEME NEEDS NO BRANCHING HERE EITHER: both paths are read off the files themselves, so whatever subtree the theme put them under is what gets recorded. The referentiel therefore carries
    # the theme without ever naming it, which is what lets a second theme exist without rewriting a single recorded path.
    # Relative to assets/, never to the repository: every path already in the referentiel is written
    # this way (check-subjects.py's own scan_cutout/claimed_paths compare on exactly this form), and a
    # path written the other way would silently read back as an unclaimed file.
    relative_target = str(target.resolve().relative_to(export_asset.ASSETS))
    relative_source = str(source.resolve().relative_to(export_asset.ASSETS))
    # Exactly what the export measured, and nothing else.
    kept = {key: measures[key] for key in
            ("delivered_px", "silhouette_px", "contact_px", "anchor_px", "master_size_px",
             "kind", "footprint") if key in measures}
    # `null` RATHER THAN AN EMPTY STRING, and the key is written either way: not having a session at all is what is being said here, and an empty string would
    # say instead that the session is known and blank (execution.md, "L'absence de valeur se dit null"). Always writing the key also keeps a version produced
    # since this change and left without a session distinguishable from one produced before it, which simply has no key.
    representation = {
        "type": "sprite", "path": relative_target, "master": relative_source,
        "image_number": frame, "measures": kept, "status": "current",
        "generator_session": options.get("session") or None,
    }
    add_representation(variant, representation)

    try:
        check_subjects.check_schema(data)
    except check_subjects.Fault as fault:
        print(f"FAULT le référentiel ne validerait plus après cet ajout : {fault}")
        return 1

    # The measures go into the referentiel, where they are read when needed; printing them here put
    # thirty lines into the caller's context at every image, for a fact that holds in one line. What
    # the launcher needs is what was recorded and where — the rest is in the file (execution.md).
    delivered = kept.get("delivered_px") or {}
    print(f"{code} / {ref} · frame {frame} · {delivered.get('width')} × {delivered.get('height')} px "
          f"→ {relative_target}")
    # NAMED, NOT PASSED OVER. An unattributable version is a state this tool knows how to name, so it reaches the launcher's own output rather than only the
    # report's (execution.md, "Une erreur remonte toujours" and its nuance). It stops nothing: the image is exported and recorded either way.
    if representation["generator_session"] is None:
        print(f"  SANS SESSION — le générateur n'en a remonté aucune, cette version n'en portera donc pas.\n"
              f"  Solution — l'identifiant reste écrit dans le journal d'événements du générateur, "
              f"« var/generations/<sprites|subjects>/{source.stem}-generateur.jsonl » : relis-le, et passe-le à --session.")
    if options.get("dry_run"):
        print("  (dry run — nothing written)")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    sprite.save(target)
    SUBJECTS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  référentiel {SUBJECTS}")

    return 0


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        raise SystemExit(0)
    sys.exit(main(sys.argv[1:]))
