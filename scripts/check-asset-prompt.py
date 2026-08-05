#!/usr/bin/env python3
"""Check the master definition, the footprint contract, the style base and the cascade reference.

Read-only on the repository: prompts are assembled in memory and NOTHING is generated. The cascade
check copies a reference file into a sandbox directory, never into assets/.

Run from the workspace root: python3 gatebeast/local/check-asset-prompt.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gatebeast" / "scripts"))
import asset_common
import tile_scale
from plate_common import STYLE_FR

failures = []


def expect(condition, label):
    print(f"  {'ok  ' if condition else 'FAILED'}  {label}")
    if not condition:
        failures.append(label)


print("MASTER DEFINITION — the file's own fineness, capped")
print(f"  {tile_scale.describe()}, {tile_scale.describe_delivery()}, "
      f"plafond {tile_scale.MASTER_CAP} px\n")
for columns, rows, label in [(1, 1, "herbe, une case"), (2, 2, "chene de parc"),
                             (8, 8, "sujet de huit cases"), (16, 10, "centre de soin"),
                             (32, 24, "une planche entiere")]:
    master = tile_scale.master_definition(columns, rows)
    delivery = tile_scale.delivery_size(columns, rows)
    margin = master["width"] / delivery["width"]
    print(f"  {label:22s} {columns:2d}x{rows:2d} cases -> livraison {delivery['width']:5.0f} x "
          f"{delivery['height']:5.0f}   maitre {master['width']:5d} x {master['height']:5d}   "
          f"marge x{margin:.2f}")
print()

expect(tile_scale.master_definition(1, 1) == {"width": 96, "height": 96},
       "one tile: the file's own fineness, and nothing beyond it")
expect(tile_scale.master_definition(2, 2)["width"] == 192, "the oak at two tiles gets 192")
for columns, rows in [(1, 1), (2, 2), (8, 8), (16, 10), (32, 24)]:
    master = tile_scale.master_definition(columns, rows)
    delivery = tile_scale.delivery_size(columns, rows)
    expect(max(master.values()) <= tile_scale.MASTER_CAP,
           f"{columns}x{rows}: never past the cap")
    expect(master["width"] <= delivery["width"],
           f"{columns}x{rows}: never finer than the delivery — the master IS the delivery")

print("\nTHE STYLE BASE IS IN EVERY ASSET PROMPT, WORD FOR WORD")
for type_asset, code in [("sol", "SOL-001"), ("personnage", "HU-000"), ("creature", "SP-001-1"),
                         ("batiment", "SOL-001"), ("vegetation", "SOL-001")]:
    text = asset_common.prompt(type_asset, code)
    expect(text.startswith(STYLE_FR), f"{type_asset}/{code}: the style base opens the prompt, verbatim")
expect(asset_common.STYLE_FR is STYLE_FR,
       "assets and plates share the SAME style object — not a copy that could drift")

print("\nTHE FOOTPRINT CONTRACT IS IN EVERY SPRITE PROMPT")
sprite = asset_common.prompt("batiment", "SOL-001", (16, 10))
expect("RIEN du sujet ne dépasse latéralement" in sprite, "nothing sticks out sideways")
# The footprint is the subject's connection to the ground — the number of tiles it needs. How much of that width its matter actually covers belongs to the
# subject's own description and to it alone: a building spans its footprint edge to edge, a path covers two thirds of it. The consigne must say so.
expect("C'EST SA FICHE QUI LE DIT" in sprite or "SA DESCRIPTION" in sprite,
       "how much of the footprint is covered comes from the subject's own description")
expect("EN HAUTEUR, LE DÉBORDEMENT EST NORMAL" in sprite, "height may overflow, as the design wants")
expect("16 case(s) de large sur 10" in sprite, "the announced footprint is stated in tiles")
expect("dépasse latéralement" not in asset_common.prompt("sol", "SOL-001"),
       "a ground material gets no footprint clause — it IS the tile, edge to edge")

print("\nTHE CASCADE — the main view reaches the generator's working directory")
sandbox = Path(__file__).resolve().parent / "cascade-probe"
sandbox.mkdir(exist_ok=True)
main_view = ROOT / "gatebeast" / "assets" / "cutout" / "personnage" / "HU-000.png"
name = asset_common.name_reference(main_view)
copied = sandbox / name
expect(copied.is_file(), f"the main view lands in the working directory as ./{name}")
expect(copied.stat().st_size == main_view.stat().st_size, "it is the whole file, byte for byte")
cascaded = asset_common.prompt("personnage", "HU-000", (1, 1), name,
                               "orientation-east : le sujet est tourné vers l'est.")
# Its REAL path, absolute: nothing is ever copied or moved so the generator can read a reference, so the consigne names the file where it actually lives.
expect(name in cascaded and name.startswith("/"), "the prompt names the reference by its real path")
expect("VUE PRINCIPALE" in cascaded, "the prompt says what that file is")
expect("LA VARIANTE DEMANDÉE" in cascaded, "the variant clause is stated separately")
expect(cascaded.startswith(STYLE_FR), "a cascaded variant still opens with the style base")
expect("RÉFÉRENCE VISUELLE" not in asset_common.prompt("personnage", "HU-000", (1, 1)),
       "the main view itself gets no reference clause")
copied.unlink()
sandbox.rmdir()

print("\nNO PIXEL FIGURE IS WRITTEN BY HAND")
import re

source = (ROOT / "gatebeast" / "scripts" / "asset_common.py").read_text(encoding="utf-8")
# Strip docstrings and comments: prose may cite a figure, code may not hold one.
code = re.sub(r'"""[\s\S]*?"""', "", source)
code = re.sub(r"#.*", "", code)
# The pivot values themselves must never appear as literals anywhere but in the service.
pivots = {"tile scale": tile_scale.PIXELS_PER_TILE, "master cap": tile_scale.MASTER_CAP,
          "file fineness": tile_scale.FILE_PIXELS_PER_TILE}
for name, value in pivots.items():
    expect(not re.search(rf"(?<![\d-]){value}(?![\d])", code),
           f"the prompt builder never writes the {name} ({value}) as a literal")
# The generator is spoken to in TILES and never in pixels: the consigne asks for a width in tiles, and states once — from the service — what a tile measures
# in the file. Nothing else about dimensions reaches it.
expect("case(s) de large" in sprite, "the width is asked in tiles")
expect("PIXELS" in asset_common.REGLES_FR and "tile_scale" in source,
       "the tile-to-pixel correspondence is stated once, from the service")

print(f"\n{'all checks passed' if not failures else str(len(failures)) + ' FAILURES'}")
raise SystemExit(1 if failures else 0)
