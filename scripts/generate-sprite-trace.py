#!/usr/bin/env python3
"""Order one sprite of a piece of an assembling subject — a fence, a path, a wall, a watercourse.

USAGE
  python3 scripts/generate-sprite-trace.py <CODE> <forme> [--posts N] [--ref <image>] [--generate]
  e.g.  generate-sprite-trace.py OB-010 ns --posts 1 --ref assets/poc/cloture/usage-OB-010-v2.png

  Without --generate it stops after assembling the prompt, writing a draft under local/ so it can be
  read before anything is produced.

INTENTION
  A fence, a path, a wall is laid end to end: its pieces must agree down to the height and thickness
  of what crosses the cell edge. That agreement cannot be obtained by describing each piece afresh —
  it is obtained by showing the piece IN PLACE and asking for it again alone.

  Hence the reference image: not another form of the same subject, which never worked, but the usage
  sample where this very piece already stands among its neighbours. The generator reads a PNG.

  No prompt is written by hand: it is assembled from the shared style base, the inventory sheet
  quoted word for word, and the clause of the piece asked for.
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_common
import plate_common
import tile_scale

REPO = Path(__file__).resolve().parent.parent
SHEETS = REPO / "doc" / "conception" / "referentiels" / "visuel" / "inventaire"
SIDE = {"n": "NORD", "e": "EST", "s": "SUD", "w": "OUEST"}


def sheet_of(code: str) -> tuple:
    """The label and the English description of a subject, read verbatim from its inventory entry."""
    for path in sorted(SHEETS.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"- **{code} "):
                label = line.split("**")[1].replace(code, "").strip()
                english = next((part.strip() for part in reversed(line.split("*"))
                                if part.strip().startswith(("A ", "An ", "The "))), "")
                return label, english
    raise SystemExit(f"FAULT {code} n'est pas à l'inventaire — rien ne se produit sans fiche.")


def build(code: str, shape: str, posts: int, reference: Path, generate: bool) -> int:
    label, english = sheet_of(code)
    joined = [SIDE[edge] for edge in shape]
    reach = " et ".join(", ".join(joined).rsplit(", ", 1))
    free = [SIDE[edge] for edge in "nesw" if edge not in shape]
    master = tile_scale.master_definition(1, 1)

    garniture = {
        0: "AUCUN poteau vertical dans cette case : les deux lisses la traversent seules.",
        1: "UN SEUL poteau vertical, planté au CENTRE de la case.",
        2: "DEUX poteaux verticaux, plantés au tiers et aux deux tiers de la case, de sorte que le "
           "vide à gauche, le vide du milieu et le vide à droite soient égaux.",
    }[posts]

    clause = ""
    if reference:
        clause = f"""
RÉFÉRENCE — le fichier ./{reference.name} est présent dans ton répertoire de travail. C'est une image
déjà produite de ce même sujet, montrant plusieurs de ses pièces assemblées, dont celle qu'on te
demande ici. Regarde-la : elle donne la matière, la couleur, l'épaisseur des lisses, la forme des
poteaux et la lumière. **Reprends-les à l'identique.** On te demande d'extraire cette pièce et de la
dessiner seule, pas d'en inventer une nouvelle.
"""

    prompt = f"""{plate_common.STYLE_FR}

{asset_common.CAMERA_FR}

ASSET DE JEU — une seule pièce de {label}, SEUL SUJET DE L'IMAGE, destinée à être détourée et posée
comme sprite sur une carte vue de dessus.

DÉFINITION ATTENDUE : {master['width']} × {master['height']} pixels, soit exactement une case carrée.

{asset_common.CADRAGE_TRACE}

{asset_common.TRACE_FR}

LA PIÈCE DEMANDÉE : le tracé traverse la case en passant par son CENTRE et rejoint le bord {reach},
et eux seuls. {"Les bords " + " et ".join(free) + " restent libres : rien ne les touche." if free else ""}
{garniture}
Les deux lisses courent d'un seul tenant d'un bord rejoint à l'autre, à la même hauteur et à la même
épaisseur qu'elles ont dans l'image de référence, pour que deux cases posées bout à bout se
prolongent sans décrochement.
{clause}
{asset_common.REGLES_FR}

LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :
{code} : {english}
"""

    name = f"{code}_shape-{shape}_posts-{posts}"
    draft = REPO / "local" / f"prompt-{name}.txt"
    draft.parent.mkdir(exist_ok=True)
    draft.write_text(prompt, encoding="utf-8")
    print(f"{code} — {label} · forme {shape} · {posts} poteau(x) · {master['width']} px")
    print(f"brouillon écrit : {draft.relative_to(REPO)}")

    if not generate:
        return 0

    target = reference.parent if reference else REPO / "assets" / "poc"
    # One generation per version, and nothing is thrown away: an existing piece keeps its place and
    # the new one takes the next version number, with its own frozen prompt beside it.
    version, image = 1, target / f"{name}.png"
    while image.exists():
        version += 1
        image = target / f"{name}-v{version}.png"
    image.with_suffix(".txt").write_text(prompt, encoding="utf-8")
    if reference and reference.parent != target:
        shutil.copy(reference, target / reference.name)

    print(f"consigne figée : {image.with_suffix('.txt').relative_to(REPO)}")
    # This tool generates, and stops there. Exporting the master and rebuilding the review page
    # belong to the queue (scripts/sprite-queue.py), which owns the ordering: chained from here, two
    # generations finishing at once would rebuild the page simultaneously, and the queue could not
    # prevent it.
    print(f"génération vers {image.relative_to(REPO)}")

    return subprocess.run(["php", str(REPO / "scripts" / "generate-image.php"),
                           str(image), prompt], cwd=REPO.parent).returncode


if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    posts_value = int(argv[argv.index("--posts") + 1]) if "--posts" in argv else 1
    ref = Path(argv[argv.index("--ref") + 1]).resolve() if "--ref" in argv else None
    raise SystemExit(build(argv[0], argv[1], posts_value, ref, "--generate" in argv))
