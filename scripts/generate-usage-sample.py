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

Usage: python3 scripts/generate-usage-sample.py <plan.json> [--ref <image>] [--generate]

  --ref   a style reference already validated (e.g. a reference plate). Same mechanism as
          generate-sprite-trace.py's own --ref: the file is dropped in the generator's working
          directory, and the consigne says it gives the TREATMENT, the MATERIAL and the LIGHT —
          never the subject, which stays the fiche's alone.
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
    """The label and the description of a subject, read from the inventory it lives in.

    The inventory is the master: nothing here paraphrases it, the description travels verbatim.
    """
    for path in sorted(SHEETS.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith(f"- **{code} "):
                continue
            label = line.split("**")[1].replace(code, "").strip()
            # What the sheet says around the description — footprint, passage, composition. It carries
            # decisions the generator must honour, so it travels too, up to (never past) the
            # description itself: a sheet may carry a description proper to one form, and a usage
            # sample shows a whole assembly, not that form — quoting it here would invite the generator
            # to draw it.
            after = line.split("** — ", 1)[-1]
            description, start = asset_common.sheet_description(after, code)
            detail = after[:start].replace("**", "").replace("`", "")

            return label, description, " ".join(detail.split()).strip(" .—,")
    raise SystemExit(f"FAULT {code} n'est pas à l'inventaire — rien ne se produit sans fiche.")


def build(source: Path, generate: bool = False, reference: Path = None) -> int:
    source = source.resolve()  # the caller may pass a relative path; every path below is absolute
    plan = json.loads(source.read_text(encoding="utf-8"))
    columns, rows = plan["grid"]["columns"], plan["grid"]["rows"]
    subjects = sorted({cell["subject"] for cell in plan["cells"]})
    if len(subjects) != 1:
        raise SystemExit("FAULT un exemple d'usage ne porte qu'un sujet ; ce plan en porte "
                         f"{len(subjects)}.")
    code = subjects[0]
    label, description, detail = sheet_of(code)

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
        listing.append(f"— colonne {cell['column']}, rangée {cell['row']} : le tracé y passe et "
                       f"rejoint le bord {reach} de cette case.")
    listing = "\n".join(listing)
    occupied = {(cell["column"], cell["row"]) for cell in plan["cells"]}

    # The plan travels as a file too. The generator reads an SVG as well as a PNG, so the drawing and
    # the written list say the same thing twice, by two routes.
    plan_name = f"plan-{code}.svg"

    clause = ""
    if reference:
        clause = f"""
RÉFÉRENCE — le fichier ./{reference.name} est présent dans ton répertoire de travail. Il montre le
style, la matière et la lumière à reprendre. Le sujet demandé est celui décrit ci-dessous, pas celui
de l'image : la référence donne le traitement, la fiche donne le sujet.
"""

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

PROJECTION RÉGULIÈRE, SOUS LA MÊME CAMÉRA QUE CI-DESSUS, JAMAIS À PLAT : chaque case de la grille est
vue sous EXACTEMENT la même plongée que celle décrite plus haut — aucune ne se dresse plus de face,
aucune ne s'aplatit plus de dessus qu'une autre. Ce qui est banni, c'est la fuyante d'une vraie
perspective, où les cases du fond rétréciraient vers un point de fuite : ici toutes les cases restent
à la même taille et au même angle, du premier au dernier rang. Deux cases de même contenu sont donc
superposables au décalage près — c'est ce qui permet d'y découper des pièces réutilisables — sans que
rien n'y perde le volume et l'inclinaison de la caméra du projet.

{asset_common.FOND}

{asset_common.TRACE_FR}
{clause}
{asset_common.REGLES_FR}

CE QUE SA FICHE PRÉCISE, et qui s'applique à chaque case de l'image :
{detail}

LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :
{code} : {description}
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
    with asset_common.working_reference(reference, source.parent):
        result = subprocess.run(["php", str(REPO / "scripts" / "generate-image.php"),
                                 str(image), prompt], cwd=REPO.parent)

    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    argv = sys.argv[1:]
    ref = Path(argv[argv.index("--ref") + 1]).resolve() if "--ref" in argv else None
    raise SystemExit(build(Path(argv[0]), "--generate" in argv, ref))
