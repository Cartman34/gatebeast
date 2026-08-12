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

Usage: python3 scripts/generate-usage-sample.py <plan.json> [--ref <image>] [--model <name>] [--generate]
       python3 scripts/generate-usage-sample.py -h|--help — this text, and nothing is generated

  --model a model to run the generator on, instead of its own configured default (e.g. gpt-5.6-sol).
          It is a setting of the run and never enters the consigne, which stays the same text whatever
          produced it; the report names the model all the same, so two runs can be compared.

  --ref   a style reference already validated (e.g. a reference plate). Same mechanism as
          generate-sprite.py's own --ref: the file is dropped in the generator's working
          directory, and the consigne says it gives the TREATMENT, the MATERIAL and the LIGHT —
          never the subject, which stays the fiche's alone.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_common
import plate_common
import production_report
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


def build(source: Path, generate: bool = False, references: list = None, model: str = None) -> int:
    references = references or []
    # No image is ever ordered blind (operator, 2026-08-05): a reference holds the treatment, the
    # material and the light steady, and without one every generation reinvents them.
    if generate and not references:
        raise SystemExit("FAULT aucune référence fournie — une génération se commande toujours avec "
                         "son image de référence (--ref).")
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
    # Its own path, never a copy laid beside the image: nothing is ever duplicated or moved to be read
    # (operator, 2026-08-05) — the generator opens the file where it actually lives.
    plan_name = asset_common.reference_address(source.with_suffix(".svg"))

    clause = ""
    if references:
        clause = f"""
RÉFÉRENCE — ouvre et regarde le fichier {asset_common.reference_address(references[0])}. C'est une image du monde déjà validée, et {label} Y EST DESSINÉ,
parmi d'autres éléments. C'EST EXACTEMENT CE {label.upper()}-LÀ QUE L'ON TE DEMANDE : sa matière, sa couleur, sa largeur par rapport à ce qui l'entoure, la
façon dont ses bords se terminent, et l'angle sous lequel on le voit. Repère-le dans l'image et reproduis-le à l'identique. Sa description ci-dessous dit
la même chose avec des mots : l'image et le texte se confirment, ils ne se contredisent pas. Le reste de l'image — les bâtiments, la végétation, les
habitants — ne se copie pas et n'apparaît pas dans le résultat.
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

LE PLAN EST AUSSI FOURNI EN FICHIER : ouvre et regarde {plan_name}. C'est
le même plan, dessiné : un point au centre de chaque case occupée, et un trait de ce point vers chaque
bord rejoint. Lis-le, il fait foi avec la liste ci-dessus.

LA GRILLE, EN CASES : {columns} cases de large sur {rows} cases de profondeur. Toutes les cases ont le
même pas, où qu'elles soient dans l'image, et ce pas ne varie jamais : aucun point de fuite, aucun
rétrécissement des rangées du fond. Deux cases de même contenu restent superposables au décalage près —
c'est ce qui permet d'y découper des pièces réutilisables.

CECI NE DIT RIEN DE L'ANGLE DE PRISE DE VUE, ET NE L'ANNULE SURTOUT PAS. C'est le PAS de la grille qui
est constant, pas le sujet qui serait vu de la verticale : chaque case garde exactement la caméra en
plongée décrite plus haut, celle sous laquelle le sujet apparaît dans l'image de référence. Confondre
les deux est l'erreur qui a déjà été faite : le générateur a lu « aucune perspective » comme « vue en
plan » et a rendu une carte à plat, inutilisable comme sprite.

À QUOI CETTE IMAGE VA SERVIR, ET C'EST CE QUI COMMANDE TOUT LE RESTE : ON VA Y DÉCOUPER DES SPRITES DE JEU. Chaque case de ta grille sera prélevée telle
quelle et posée dans le jeu comme une tuile. Tu dessines donc des sprites, sous l'angle des sprites du projet — celui décrit dans la clause de caméra
ci-dessus, et celui sous lequel le sujet apparaît dans l'image de référence. Ce que tu rends est ce que le joueur verra à l'écran.

LE PLAN, LUI, N'EST PAS CE QU'IL FAUT DESSINER. Il est donné MIS À PLAT, vu de la verticale, comme une carte : il dit seulement QUELLES CASES sont occupées
et QUELS BORDS le tracé rejoint dans chacune. Il ne dit rien de l'allure du sujet et ne se recopie pas. Dessine la tuile telle qu'elle sera posée dans le
jeu, avec sa matière, son grain et sa lumière, puis répète-la de case en case aux emplacements que le plan indique.

L'image fait donc {columns} cases de large. N'écris aucune dimension dans l'image.

LE SUJET ÉPOUSE CE PLAN INCLINÉ : ses traces, ses nuances, ses irrégularités et tout ce que sa fiche
lui donne sont projetés dans cette même orientation, et la lumière venant du haut à gauche révèle cette
orientation sur la surface elle-même. Il se montre avec le volume que sa fiche lui donne, et sans lui
en ajouter aucun si elle ne lui en donne pas.

{asset_common.FOND}

{asset_common.TRACE_FR}
{clause}
{asset_common.REGLES_FR}

CE QUE SA FICHE PRÉCISE, et qui s'applique à chaque case de l'image :
{detail}

LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :
{code} : {description}
"""

    # Sous var/tmp/, parce qu'un brouillon est vraiment temporaire et se refait d'une commande ; le reste de var/ garde ce qui se conserve. Jamais dans local/, qui est le
    # répertoire de l'agent et où l'outillage n'écrit rien (opérateur, 2026-08-06).
    draft = REPO / "var" / "tmp" / "consignes" / f"usage-{code}.txt"
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

    print(f"consigne figée : {frozen.relative_to(REPO)}")
    print(f"génération lancée vers {image.relative_to(REPO)}")

    # A usage sample is not a sprite: it is never exported to a delivery definition and never recorded
    # as a representation. Its run is still timed and still leaves its report, for the same reason
    # every other one does — an image nobody can account for is an image nobody can judge.
    run = production_report.Run(f"usage-{code}", kind="subjects")
    run.model = model
    with run.step("consigne"):
        pass
    try:
        with run.step("génération"):
            # The model travels as an environment value, the same way the parallelism does: it is a
            # setting of the run, never part of the consigne, which must stay the same text whatever
            # produced it.
            environment = dict(os.environ, IMAGE_TRACE_KIND="subjects")
            if model:
                environment["IMAGE_MODEL"] = model
            result = subprocess.run(["php", str(REPO / "scripts" / "generate-image.php"),
                                     str(image), prompt], cwd=REPO.parent, env=environment,
                                    capture_output=True, text=True)
            print(result.stdout, end="", flush=True)
            run.session = production_report.Run.session_of(result.stdout)
    finally:
        with run.step("rapport"):
            run.write(image, prompt)

    return result.returncode


if __name__ == "__main__":
    # ASKED BEFORE ANYTHING ELSE HERE: every other path through this block can spend a generation.
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        raise SystemExit(0)
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    argv = sys.argv[1:]
    # ONE reference, and one only (operator, 2026-08-05): the consigne points at the sujet INSIDE that
    # image and asks for that one exactly. Two images would give two versions of the same sujet to copy.
    refs = [Path(argv[position + 1]).resolve()
            for position, token in enumerate(argv) if token == "--ref"][:1]
    chosen = argv[argv.index("--model") + 1] if "--model" in argv else None
    raise SystemExit(build(Path(argv[0]), "--generate" in argv, refs, chosen))
