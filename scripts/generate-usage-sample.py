#!/usr/bin/env python3
"""Assemble the prompt of a usage sample — the example image where a subject is seen assembled.

A usage sample is not a sprite: it is one image showing every piece of an assembling subject laid out
together, so the pieces can be compared to one another. Its layout comes from a composition plan, and
the plan is the only place the layout is declared.

No prompt is ever written by hand (see the production chain). This tool builds it from three sources
and nothing else: the shared style base, the composition plan, and the subject's inventory sheet
quoted WORD FOR WORD.

The draft is written to local/ — never beside the image. A prompt only lands in assets/ at the moment
its image is produced, and it is frozen from then on.

Usage: python3 scripts/build-usage-sample-prompt.py <plan.json>
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_common
import plate_common
import tile_scale

REPO = Path(__file__).resolve().parent.parent
SHEETS = REPO / "doc" / "conception" / "referentiels" / "visuel" / "inventaire"


def sheet_of(code: str) -> tuple:
    """The label and the English description of a subject, read from the inventory it lives in.

    The inventory is the master: nothing here paraphrases it, the description travels verbatim.
    """
    for path in sorted(SHEETS.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith(f"- **{code} "):
                continue
            label = line.split("**")[1].replace(code, "").strip()
            parts = line.split("*")
            english = next((part.strip() for part in reversed(parts)
                            if part.strip().startswith(("A ", "An ", "The "))), "")
            # What the sheet says in French around the description — footprint, passage, garnitures.
            # It carries decisions the generator must honour, so it travels too. Everything after the
            # label is kept except the English description itself, and the emphasis is dropped: the
            # sheet uses bold freely, and a naive split on it loses half the sentence.
            after = line.split("** — ", 1)[-1]
            detail = after.replace(f"*{english}*", "").replace("**", "").replace("`", "")
            # A sheet may carry a description proper to one form. A usage sample shows a whole
            # assembly, not that form: quoting it here would invite the generator to draw it.
            detail = detail.split("Description propre")[0]

            return label, english, " ".join(detail.split()).strip(" .—,")
    raise SystemExit(f"FAULT {code} n'est pas à l'inventaire — rien ne se produit sans fiche.")


def build(source: Path, generate: bool = False) -> int:
    source = source.resolve()  # the caller may pass a relative path; every path below is absolute
    plan = json.loads(source.read_text(encoding="utf-8"))
    columns, rows = plan["grid"]["columns"], plan["grid"]["rows"]
    subjects = sorted({cell["subject"] for cell in plan["cells"]})
    if len(subjects) != 1:
        raise SystemExit("FAULT un exemple d'usage ne porte qu'un sujet ; ce plan en porte "
                         f"{len(subjects)}.")
    code = subjects[0]
    label, english, detail = sheet_of(code)

    # The definition is calculated, never chosen: the conversion service owns the tile, and the
    # sample is delivered at twice the display size, capped as every other asset is.
    master = tile_scale.master_definition(columns, rows)
    width, height = master["width"], master["height"]

    # The composition is spelled out cell by cell, with its coordinates. An ASCII grid was tried and
    # is not enough: it says which cells are taken but nothing of what each one holds, and the
    # generator reads it as a shape to make pretty rather than a layout to follow.
    side = {"n": "nord", "e": "est", "s": "sud", "w": "ouest"}
    listing = []
    for cell in sorted(plan["cells"], key=lambda item: (item["row"], item["column"])):
        joins = [side[edge] for edge in ("n", "e", "s", "w") if edge in cell["joins"]]
        reach = " et ".join(", ".join(joins).rsplit(", ", 1))
        listing.append(f"— colonne {cell['column']}, rangée {cell['row']} : la clôture y passe et "
                       f"rejoint le bord {reach} de cette case.")
    listing = "\n".join(listing)
    occupied = {(cell["column"], cell["row"]) for cell in plan["cells"]}

    # The plan travels as a file too. The generator reads an SVG as well as a PNG, so the drawing and
    # the written list say the same thing twice, by two routes.
    plan_name = f"plan-{code}.svg"

    prompt = f"""{plate_common.STYLE_FR}

{asset_common.CAMERA_FR}

EXEMPLE D'USAGE — une seule image montrant {label} POSÉE EN PLACE, toutes ses pièces assemblées, pour
qu'on puisse les comparer entre elles. Ce n'est pas une sprite : c'est la référence d'ensemble.

LA COMPOSITION, à respecter exactement — une grille de {columns} × {rows} cases, numérotées de 1 à
{columns} en colonnes de la gauche vers la droite, et de 1 à {rows} en rangées du haut vers le bas.
Les {len(occupied)} cases ci-dessous portent le sujet ; **toutes les autres sont vides**, et il n'y a
rien dedans. Ne déplace aucune case, n'en ajoute aucune, n'en retire aucune, ne rends la figure ni
plus symétrique ni plus régulière qu'elle ne l'est — elle est ainsi volontairement.

{listing}

LE PLAN EST AUSSI FOURNI EN FICHIER : ./{plan_name} est présent dans ton répertoire de travail. C'est
le même plan, dessiné : un point au centre de chaque case occupée, et un trait de ce point vers chaque
bord rejoint. Lis-le, il fait foi avec la liste ci-dessus.

DÉFINITION ATTENDUE : {width} × {height} pixels, soit exactement {columns} × {rows} cases carrées.
Chaque case fait la même taille, où qu'elle soit dans l'image. N'écris aucune dimension dans l'image.

AUCUNE CONVERGENCE DE PERSPECTIVE : la grille du sol est vue sous le même angle partout, les cases ne
rétrécissent pas vers le haut. Deux cases de même contenu sont superposables au décalage près — c'est
ce qui permet d'y découper des pièces réutilisables.

{asset_common.FOND}

{asset_common.TRACE_FR}

{asset_common.REGLES_FR}

CE QUE SA FICHE PRÉCISE, et qui s'applique à chaque case de l'image :
{detail}

LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :
{code} : {english}
"""

    draft = REPO / "local" / f"prompt-usage-{code}.txt"
    draft.parent.mkdir(exist_ok=True)
    draft.write_text(prompt, encoding="utf-8")

    print(f"sujet {code} — {label}")
    print(f"grille {columns} × {rows} cases · {len(occupied)} cases occupées")
    print(f"définition calculée {width} × {height} px")
    print(f"brouillon écrit : {draft.relative_to(REPO)}")

    if not generate:
        return 0

    # The image is produced ONCE. Its prompt is frozen beside it at that moment and never rewritten:
    # it is the only trace of how the image was obtained.
    # One generation per version, and nothing is ever thrown away: a sample that already exists is
    # kept, and the new one takes the next version number with its own frozen prompt beside it.
    version, image = 1, source.parent / f"usage-{code}.png"
    while image.exists():
        version += 1
        image = source.parent / f"usage-{code}-v{version}.png"
    frozen = image.with_suffix(".txt")
    frozen.write_text(prompt, encoding="utf-8")
    # The generator works in the image's directory, so the plan must be there for it to be read.
    (source.parent / plan_name).write_text(source.with_suffix(".svg").read_text(encoding="utf-8"),
                                           encoding="utf-8")

    print(f"consigne figée : {frozen.relative_to(REPO)}")
    print(f"génération lancée vers {image.relative_to(REPO)}")
    result = subprocess.run(["php", str(REPO / "scripts" / "generate-image.php"),
                             str(image), prompt], cwd=REPO.parent)

    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(build(Path(sys.argv[1]), "--generate" in sys.argv))
