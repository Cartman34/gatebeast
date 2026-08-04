#!/usr/bin/env python3
"""Cut a produced image out and inscribe it in the catalogue — chain steps 5 and 9, in one gesture.

The design forbids keeping the catalogue by hand ("Le catalogue s'écrit à l'entrée, jamais à la main"),
because a hand-kept catalogue and the files on disk diverge within a week. This is the only writer.

It cuts the source image (cut-asset.py), writes the sprite under assets/cutout/, and records the
profile and the image — address, deliverable path, source path, measured pose point and extent.

Usage:
  python3 record-asset.py <source> --code <XX-nnn> --type <type> \\
      [--name <kind-nn>] [--footprint <columns>x<rows>] [--height <tiles>] \\
      [--variant <address>] [--dry-run]

  <source>     path relative to assets/, or absolute
  --variant    full address; defaults to the main view, orientation-south_action-idle_frame-01
  --dry-run    show what would be written, touch nothing
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_catalog
from asset_catalog import Profile, Variant

# cut-asset.py is hyphenated, so it is loaded by path rather than imported by name.
import importlib.util

CUT = Path(__file__).resolve().parent / "cut-asset.py"
spec = importlib.util.spec_from_file_location("cut_asset", CUT)
cut_asset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cut_asset)

MAIN_VIEW = Variant("south", "idle").address(1)


def parse_footprint(text):
    columns, _, rows = text.partition("x")

    return {"columns": float(columns), "rows": float(rows or columns)}


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

    sprite, measures = cut_asset.cut(source)
    target = cut_asset.destination(source)
    address = options.get("variant", MAIN_VIEW)

    catalog = asset_catalog.load()
    code = options["code"]
    if code not in catalog:
        catalog.add(Profile(
            code, options["type"], options.get("name"),
            parse_footprint(options["footprint"]) if "footprint" in options else None,
            height=float(options["height"]) if "height" in options else None,
        ))
    profile = catalog.profile(code)
    if "footprint" in options:
        profile.footprint = parse_footprint(options["footprint"])
    if "height" in options:
        profile.height = float(options["height"])
    if "name" in options:
        profile.name = options["name"]

    relative_target = str(target.resolve().relative_to(cut_asset.REPOSITORY))
    relative_source = str(source.resolve().relative_to(cut_asset.REPOSITORY))
    kept = {key: measures[key] for key in
            ("size_px", "contact_px", "anchor_px", "aspect", "transparency", "thresholds")}
    catalog.record(code, address, relative_target, kept, relative_source)

    print(f"{code}  {address}")
    print(f"  sprite  {relative_target}")
    print(f"  source  {relative_source}")
    print(json.dumps(kept, indent=2))
    if options.get("dry_run"):
        print("  (dry run — nothing written)")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    sprite.save(target)
    written = catalog.save()
    print(f"  catalogue {written}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
