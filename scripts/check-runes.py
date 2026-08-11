#!/usr/bin/env python3
"""Check the rune data against the content referential: every declared rune has a shape, a colour and a drawable path.

USAGE
  python3 scripts/check-runes.py — reads assets/runes.json and doc/conception/referentiels/contenu/creatures-temoins.md, and reports what is missing on either
  side. Prints its verdict and what is wrong, nothing else.

INTENTION
  The rune is traced at render from declared data, so a rune the data does not carry is a creature that will be drawn bare, and a shape nobody claims is dead
  weight that nothing will ever reveal. The two sides are written by different hands — the referential names the runes, the data file draws them — and nothing
  held them together. Python rather than PHP: this reads a JSON file and a Markdown one and compares two sets, which is where the language is at its shortest,
  and it sits beside the other check-*.py of the project.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "assets/runes.json"
REFERENTIAL = REPO / "doc/conception/referentiels/contenu/creatures-temoins.md"
# « - **SP-001-1 :** rune en **arche** (un arc simple), turquoise. » — the code and the shape name are what must match on both sides.
DECLARATION = re.compile(r"\*\*(SP-\d+-\d+)\s*:\*\*\s*rune en \*\*([^*]+)\*\*")

data = json.loads(DATA.read_text(encoding="utf-8"))
shapes, individuals = data["shapes"], data["individuals"]
declared = dict(DECLARATION.findall(REFERENTIAL.read_text(encoding="utf-8")))

faults = []
for code, name in declared.items():
    carried = individuals.get(code)
    if carried is None:
        faults.append(f"{code} est déclaré au référentiel — rune en « {name} » — et absent de {DATA.name}")
        continue
    shape = shapes.get(carried["shape"])
    if shape is None:
        faults.append(f"{code} porte la forme « {carried['shape']} », qu'aucune géométrie ne définit")
        continue
    if shape["label"] != name:
        faults.append(f"{code} : le référentiel dit « {name} », la donnée dit « {shape['label']} »")
    if not shape.get("path"):
        faults.append(f"la forme « {carried['shape']} » n'a pas de tracé")
    if not re.fullmatch(r"#[0-9a-f]{6}", carried.get("color", "")):
        faults.append(f"{code} n'a pas de couleur en code : {carried.get('color')!r}")

for code in individuals:
    if code not in declared:
        faults.append(f"{code} porte une rune dans la donnée et n'est déclaré nulle part au référentiel")
for name, shape in shapes.items():
    if not any(carried["shape"] == name for carried in individuals.values()):
        faults.append(f"la forme « {name} » n'est réclamée par aucun individu")

if faults:
    print(f"{len(faults)} écart(s) entre le référentiel des créatures et la donnée des runes :")
    for fault in faults:
        print(f"  {fault}")
    sys.exit(1)

print(f"{len(declared)} rune(s) déclarée(s) : chacune a sa forme, son tracé et sa couleur.")
