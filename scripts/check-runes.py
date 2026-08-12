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


def load():
    """The rune data, read from its one file.

    HELD HERE BECAUSE THE PATH IS HELD HERE, and the tooling that builds a creature's consigne needs the very same file: the individual, its species, its shape
    and its colour. Before this, the prompt builder carried its own copy of all four — and the copy is what this whole chain has been removing.
    """
    if not DATA.is_file():
        raise RuntimeError(f"FAULT la donnée des runes est absente : {DATA}")
    return json.loads(DATA.read_text(encoding="utf-8"))


def main():
    data = load()
    shapes, individuals = data["shapes"], data["individuals"]
    declared = dict(DECLARATION.findall(REFERENTIAL.read_text(encoding="utf-8")))

    faults = []
    # THE SIZE IS CHECKED FIRST BECAUSE IT IS THE ONE VALUE EVERY TRACE NEEDS: shapes and anchors say what and where, this says how big. Missing, the renderer
    # has no size at all and each caller would invent its own — which is exactly the state this key ended.
    size = data.get("size_tx")
    if not isinstance(size, (int, float)) or not 0 < size <= 1:
        faults.append(f"la taille de la rune (« size_tx ») doit être une fraction de case entre 0 et 1, et vaut {size!r}")

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
        # THE SPECIES IS CHECKED LIKE THE REST since the consigne of every creature now resolves through it: an individual without it produces no description at
        # all, and that is a generation lost — the very failure that made this link a declared value rather than a code split in two.
        if not re.fullmatch(r"SP-\d+", carried.get("species", "")):
            faults.append(f"{code} n'a pas d'espèce déclarée : {carried.get('species')!r}")

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
        return 1

    print(f"{len(declared)} rune(s) déclarée(s) : chacune a sa forme, son tracé, sa couleur et son espèce. Taille : {size} case.")
    return 0


# LOADED WITHOUT RUNNING: the prompt builder imports `load()` from here, and a module that checks and exits the moment it is imported would take its caller down
# with it. The check is the command's job, not the file's.
if __name__ == "__main__":
    sys.exit(main())
