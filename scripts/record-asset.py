#!/usr/bin/env python3
"""Cut a produced image out and inscribe it in the referentiel — chain steps 5 and 9, in one gesture.

The design forbids keeping the referentiel by hand ("Le catalogue s'écrit à l'entrée, jamais à la
main"), because a hand-kept file and the disk diverge within a week. This is the only writer.

It cuts the source image (cut-asset.py), writes the sprite under assets/cutout/, and records it in
assets/sujets.json: the sujet (created together with its first variant if the code is new), the
variant it belongs to, and the representation itself — livrable path, master path, image number, and
the measures taken at cut time.

Was built on the frozen assets/catalogue.json (asset_catalog.py) and its Variant/Profile classes.
Rebuilt against the referentiel directly: the referentiel keeps versions instead of overwriting, and
does not identify a variant by a computed address string the way the catalogue did — it stores the
same fields (orientation, action, shape, and a type's own axes) as plain keys, so this tool now does
too, instead of building and parsing a string nothing else needs.

Usage:
  python3 record-asset.py <source> --code <XX-nnn> --type <type> \\
      [--name <kind-nn>] [--footprint <columns>x<rows>] [--height <tiles>] \\
      [--variant <key>=<value>,...] [--frame <n>] [--dry-run]

  <source>     path relative to assets/, or absolute
  --type       must be one of the types the referentiel already declares
  --variant    comma-separated key=value pairs among orientation, action, shape, composition,
               portillon; a key left out keeps the main view's own default (south, idle, plain).
               e.g. --variant shape=ns,composition=posts-1
  --frame      the image's own number within its variant (lexique: frame-01, frame-02...) — not a
               version number, defaults to 1
  --dry-run    show what would be written, touch nothing
"""
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shape_vocab

# cut-asset.py and check-sujets.py are hyphenated, so they are loaded by path rather than imported by
# name — the same mechanism this file already used for cut-asset.py.
CUT = Path(__file__).resolve().parent / "cut-asset.py"
spec = importlib.util.spec_from_file_location("cut_asset", CUT)
cut_asset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cut_asset)

CHECK_SUJETS = Path(__file__).resolve().parent / "check-sujets.py"
spec = importlib.util.spec_from_file_location("check_sujets", CHECK_SUJETS)
check_sujets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_sujets)

SUJETS = check_sujets.SUJETS  # assets/sujets.json — one path, held by the checker, not recopied here

MAIN_VIEW = {"orientation": "south", "action": "idle", "shape": shape_vocab.DEFAULT_SHAPE}
# The fields that identify a variant in the referentiel. Never a computed address: the referentiel
# stores exactly these, as plain keys, and nothing more is needed to find or create one.
VARIANT_KEYS = ("orientation", "action", "shape", "composition", "portillon")


def parse_footprint(text):
    columns, _, rows = text.partition("x")

    # Whole tiles, never fractional — and the referentiel's own checker requires an int
    # (check-sujets.py, check_schema): a float footprint would write a sujet its own gate refuses.
    return {"columns": int(columns), "rows": int(rows or columns)}


def parse_variant(text):
    """A variant descriptor from the command line: comma-separated key=value pairs, among the fields
    the referentiel itself stores for a variant. Missing keys fall back to the main view's own
    defaults. Never an address string — the referentiel does not keep one, so nothing here builds one.
    """
    values = dict(MAIN_VIEW)
    if text:
        for pair in text.split(","):
            key, separator, value = pair.partition("=")
            key = key.strip()
            if not separator or key not in VARIANT_KEYS:
                raise SystemExit(f"FAULT clé de variante inconnue ou mal formée : {pair!r} — attendu "
                                 f"parmi {VARIANT_KEYS}")
            values[key] = value.strip()
    if not shape_vocab.valid_shape(values["shape"]):
        raise SystemExit(f"FAULT forme invalide : {values['shape']!r}")

    return values


def matching_variant(sujet, wanted):
    """The variant of `sujet` whose fields equal `wanted` exactly — every one of VARIANT_KEYS, absence
    included, since a variant without a composition is not the same variant as one that has one."""
    for variant in sujet["variantes"]:
        if all(variant.get(key) == wanted.get(key) for key in VARIANT_KEYS):
            return variant

    return None


def record(data, code, type_name, wanted, name=None, footprint=None, height=None):
    """Find or create the sujet and its variant, and return the variant ready to receive a new
    representation. A sujet and its first variant are created TOGETHER: the referentiel refuses a
    sujet without at least one variant (check-sujets.py), so there is never a moment where the file
    would hold one without the other.
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
            "variantes": [],
        }
        data["sujets"][code] = sujet
    else:
        if footprint is not None:
            sujet["emprise"] = footprint
        if height is not None:
            sujet["hauteur"] = height
        if name is not None:
            sujet["profil"] = name

    variant = matching_variant(sujet, wanted)
    if variant is None:
        variant = dict(wanted)
        variant["representations"] = []
        sujet["variantes"].append(variant)

    return variant


def add_representation(variant, representation):
    """Add a new version, never overwrite one — the referentiel's own rule (rien ne se jette), which
    replaces the frozen catalogue's policy of silently overwriting whatever already sat at the same
    address. The previous 'courante' becomes 'anterieure'; beyond three kept 'anterieure', the oldest
    drops out of the FILE only — its image stays on disk, exactly like every image in this repository.
    """
    representations = variant.setdefault("representations", [])
    for previous in representations:
        if previous.get("statut") == "courante":
            previous["statut"] = "anterieure"
    representations.insert(0, representation)

    kept, extra = 0, []
    for previous in representations[1:]:
        if previous.get("statut") != "anterieure":
            continue
        kept += 1
        if kept > check_sujets.MAX_PREVIOUS_REPRESENTATIONS:
            extra.append(previous)
    for previous in extra:
        representations.remove(previous)


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
        source = cut_asset.ASSETS / positional[0]
    if not source.is_file():
        print(f"ABSENT {source}")
        return 1

    code = options["code"]
    wanted = parse_variant(options.get("variant"))
    frame = int(options.get("frame", 1))
    footprint = parse_footprint(options["footprint"]) if "footprint" in options else None
    height = float(options["height"]) if "height" in options else None

    try:
        data = check_sujets.load()
    except check_sujets.Fault as fault:
        print(f"FAULT {fault}")
        return 1
    variant = record(data, code, options["type"], wanted, options.get("name"), footprint, height)

    sprite, measures = cut_asset.cut(source)
    target = cut_asset.destination(source)
    # Relative to assets/, never to the repository: every path already in the referentiel is written
    # this way (check-sujets.py's own scan_cutout/claimed_paths compare on exactly this form), and a
    # path written the other way would silently read back as an unclaimed file.
    relative_target = str(target.resolve().relative_to(cut_asset.ASSETS))
    relative_source = str(source.resolve().relative_to(cut_asset.ASSETS))
    kept = {key: measures[key] for key in
            ("size_px", "contact_px", "anchor_px", "aspect", "transparency", "thresholds")}
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

    print(f"{code}  {wanted}  frame {frame}")
    print(f"  sprite  {relative_target}")
    print(f"  source  {relative_source}")
    print(json.dumps(kept, indent=2))
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
