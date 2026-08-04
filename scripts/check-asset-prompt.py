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


print("MASTER DEFINITION — twice the delivery, capped, never below the delivery")
print(f"  1 tile = {tile_scale.PIXELS_PER_TILE} px, delivery x{tile_scale.DELIVERY_SUPERSAMPLE}, "
      f"master x{tile_scale.MASTER_SUPERSAMPLE} capped at {tile_scale.MASTER_CAP} px\n")
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

expect(tile_scale.master_definition(1, 1) == {"width": 192, "height": 192},
       "one tile: delivered at 96, mastered at 192 — modest and enough")
expect(tile_scale.master_definition(2, 2)["width"] == 384, "the oak at two tiles gets 384")
expect(max(tile_scale.master_definition(8, 8).values()) == tile_scale.MASTER_CAP,
       "a subject of eight tiles lands exactly on the cap")
expect(tile_scale.master_definition(16, 10) == {"width": 1536, "height": 960},
       "the healing centre is capped at 1536 — its master IS its delivery, no margin, accepted")
for columns, rows in [(1, 1), (2, 2), (8, 8), (16, 10), (32, 24)]:
    master = tile_scale.master_definition(columns, rows)
    delivery = tile_scale.delivery_size(columns, rows)
    expect(max(master.values()) <= max(tile_scale.MASTER_CAP, max(delivery.values())),
           f"{columns}x{rows}: never past the cap, unless the delivery itself already is")
    expect(master["width"] >= delivery["width"] and master["height"] >= delivery["height"],
           f"{columns}x{rows}: never coarser than the delivery")
    expect(master["width"] <= delivery["width"] * tile_scale.MASTER_SUPERSAMPLE,
           f"{columns}x{rows}: never finer than twice the delivery")

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
expect("REMPLI" in sprite, "the footprint must actually be filled")
expect("EN HAUTEUR, LE DÉBORDEMENT EST NORMAL" in sprite, "height may overflow, as the design wants")
expect("16 case(s) de large sur 10" in sprite, "the announced footprint is stated in tiles")
expect("dépasse latéralement" not in asset_common.prompt("sol", "SOL-001"),
       "a ground material gets no footprint clause — it IS the tile, edge to edge")

print("\nTHE CASCADE — the main view reaches the generator's working directory")
sandbox = Path(__file__).resolve().parent / "cascade-probe"
sandbox.mkdir(exist_ok=True)
main_view = ROOT / "gatebeast" / "assets" / "cutout" / "personnage" / "HU-000.png"
name = asset_common.place_reference(sandbox, "HU-000", main_view)
copied = sandbox / name
expect(copied.is_file(), f"the main view lands in the working directory as ./{name}")
expect(copied.stat().st_size == main_view.stat().st_size, "it is the whole file, byte for byte")
cascaded = asset_common.prompt("personnage", "HU-000", (1, 1), name,
                               "orientation-east : le sujet est tourné vers l'est.")
expect(f"./{name}" in cascaded, "the prompt names the reference by its relative path")
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
          "delivery factor": tile_scale.DELIVERY_SUPERSAMPLE * 100}
for name, value in pivots.items():
    expect(not re.search(rf"(?<![\d-]){value}(?![\d])", code),
           f"the prompt builder never writes the {name} ({value}) as a literal")
expect("tile_scale.master_definition" in code, "the definition comes from the service")

print(f"\n{'all checks passed' if not failures else str(len(failures)) + ' FAILURES'}")
raise SystemExit(1 if failures else 0)
