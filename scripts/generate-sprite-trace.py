#!/usr/bin/env python3
"""Order one sprite of a piece of an assembling subject — a fence, a path, a wall, a watercourse.

USAGE
  python3 scripts/generate-sprite-trace.py <CODE> <forme> [--posts N] [--portillon <valeur>] \\
      [--ref <image> | --plate <image>] [--generate]
  e.g.  generate-sprite-trace.py OB-010 ns --posts 1 --ref assets/poc/cloture/usage-OB-010-v2.png
  e.g.  generate-sprite-trace.py OB-010 ew --portillon gate-closed --ref ...
  e.g.  generate-sprite-trace.py CH-019 ne --plate assets/revue-da/planche-p1-campagne-v8.png

  --posts and --portillon only ever apply to a sujet whose TYPE declares that axis in
  assets/sujets.json — read there, never guessed from the code. Passing --posts for a type that has
  no composition axis is refused.

  --ref points at a usage sample of this SAME sujet, already assembled — the reference shows the
  piece itself. --plate points at a world reference plate where the sujet appears AMONG OTHERS — the
  reference shows a whole scene, and the consigne says so, asking the generator to pick this sujet out
  of it rather than copy the plate. The two say a different thing because they show a different thing;
  at most one may be given.

  Without --generate it stops after assembling the prompt, writing a draft under local/ so it can be
  read before anything is produced.

INTENTION
  A fence, a path, a wall is laid end to end: its pieces must agree down to the height and thickness
  of what crosses the cell edge. That agreement cannot be obtained by describing each piece afresh —
  it is obtained by showing the piece IN PLACE and asking for it again alone.

  This tool serves ANY assembling sujet, whatever its type. What is common to every one of them —
  passing through the centre of its cell, reaching exactly the edges it joins, cut clean there to
  connect, free elsewhere — lives here. What is proper to one sujet — a fence's posts, a path's
  camber — lives in ITS OWN fiche or type declaration, never in this code: a clause that named posts
  and rails unconditionally is exactly what made this tool unusable for a path.

  No prompt is written by hand: it is assembled from the shared style base, the inventory sheet
  quoted word for word, and the clause of the piece asked for.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_common
import plate_common
import shape_vocab
import tile_scale

# check-sujets.py is hyphenated, so it is loaded by path (record-asset.py already uses this mechanism
# for the same file, and cut-asset.py before it).
CHECK_SUJETS = Path(__file__).resolve().parent / "check-sujets.py"
spec = importlib.util.spec_from_file_location("check_sujets", CHECK_SUJETS)
check_sujets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_sujets)

REPO = Path(__file__).resolve().parent.parent
SHEETS = REPO / "doc" / "conception" / "referentiels" / "visuel" / "inventaire"
SIDE = {"n": "NORD", "e": "EST", "s": "SUD", "w": "OUEST"}

# The posts clause is proper to the fence's own composition axis, not to every assembling sujet — kept
# here because only one type declares it today, but gated on that declaration below, never applied by
# default.
POSTS_TEXT = {
    0: "AUCUN poteau vertical dans cette case : les deux lisses la traversent seules.",
    1: "UN SEUL poteau vertical, planté au CENTRE de la case.",
    2: "DEUX poteaux verticaux, plantés au tiers et aux deux tiers de la case, de sorte que le "
       "vide à gauche, le vide du milieu et le vide à droite soient égaux.",
}


def sheet_of(code: str, qualifier: str = None) -> tuple:
    """The label and the description of a subject, read verbatim from its inventory entry. Without
    `qualifier`, the base description; with one (e.g. a portillon value like "gate-closed"), the
    description proper to it — see asset_common.sheet_description."""
    for path in sorted(SHEETS.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith(f"- **{code} "):
                continue
            label = line.split("**")[1].replace(code, "").strip()
            description, _ = asset_common.sheet_description(line, code, qualifier)
            return label, description
    raise SystemExit(f"FAULT {code} n'est pas à l'inventaire — rien ne se produit sans fiche.")


def sujet_type(code: str) -> dict:
    """The sujet's own type declaration in the referentiel — read, never guessed, so a clause proper
    to one axis (composition, portillon...) only ever appears for the types that declare it."""
    try:
        data = check_sujets.load()
    except check_sujets.Fault as fault:
        raise SystemExit(f"FAULT {fault}")
    sujet = data["sujets"].get(code)
    if sujet is None:
        raise SystemExit(f"FAULT {code} n'est pas au référentiel — rien ne se produit sans fiche.")

    return data["types"][sujet["type"]]


def build(code: str, shape: str, posts: int, reference: Path, generate: bool,
          portillon: str = None, plate: Path = None) -> int:
    if reference and plate:
        raise SystemExit("FAULT --ref et --plate sont exclusifs : une référence montre le sujet "
                         "seul, l'autre le montre parmi d'autres — jamais les deux à la fois.")
    if not shape_vocab.valid_shape(shape):
        raise SystemExit(f"FAULT forme invalide : {shape!r} — ni « plain », ni une combinaison de "
                          f"bords n/e/s/w dans l'ordre.")
    type_ = sujet_type(code)
    # The composition axis applies to a PIECE, not to its type unconditionally: the referentiel itself
    # says so now (assets/sujets.json, portillons.rend_inapplicable) after a portillon piece was given
    # a post its own fiche never asks for — a portillon hangs on iron pivots, not a post, whatever
    # --posts says. Read here, never re-decided: an axis that a requested value renders inapplicable
    # simply does not apply, exactly as the referentiel declares it, for any axis that says so.
    portillon_axis = type_.get("portillons") or {}
    inapplicable = set(portillon_axis.get("rend_inapplicable", [])) if portillon else set()
    applies_composition = bool(type_.get("compositions")) and "compositions" not in inapplicable
    if posts is not None and not applies_composition:
        reason = (f"un portillon ({portillon}) n'a pas de composition — sa fiche le tient sur des "
                 f"pivots de fer" if portillon else
                 f"le type de {code} ne déclare pas d'axe de composition")
        raise SystemExit(f"FAULT {reason} — --posts n'a rien à quoi s'appliquer ici.")
    if applies_composition and posts is None:
        posts = 1  # the tool's own long-standing default when --posts is left out, unchanged

    label, description = sheet_of(code, portillon)
    edges = shape_vocab.edges_of(shape)
    joined = [SIDE[edge] for edge in edges]
    reach = " et ".join(", ".join(joined).rsplit(", ", 1))
    free = [SIDE[edge] for edge in shape_vocab.EDGES if edge not in edges]
    master = tile_scale.master_definition(1, 1)

    composition_clause = ""
    if applies_composition:
        composition_clause = f"""{POSTS_TEXT[posts]}
Les deux lisses courent d'un seul tenant d'un bord rejoint à l'autre, à la même hauteur et à la même
épaisseur qu'elles ont dans l'image de référence, pour que deux cases posées bout à bout se
prolongent sans décrochement.
"""

    active_reference = reference or plate
    clause = ""
    if reference:
        clause = f"""
RÉFÉRENCE — le fichier ./{reference.name} est présent dans ton répertoire de travail. C'est une image
déjà produite de ce même sujet, montrant plusieurs de ses pièces assemblées, dont celle qu'on te
demande ici. Regarde-la : elle donne la matière, la couleur et la lumière à reprendre à l'identique.
On te demande d'extraire cette pièce précise et de la dessiner seule, pas d'en inventer une nouvelle.
"""
    elif plate:
        clause = f"""
RÉFÉRENCE — le fichier ./{plate.name} est présent dans ton répertoire de travail. C'est une planche du
monde, déjà validée, où {label} apparaît PARMI D'AUTRES éléments — pas une image de ce seul sujet.
Elle donne le style, la matière et la lumière à reprendre pour CE SUJET précis, repéré dans l'image ;
le reste de la planche ne se copie pas et n'apparaît pas dans le résultat.
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
{composition_clause}
{clause}
{asset_common.REGLES_FR}

LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :
{code} : {description}
"""

    name = f"{code}_shape-{shape}"
    if applies_composition:
        name += f"_posts-{posts}"
    if portillon:
        name += f"_portillon-{portillon}"
    draft = REPO / "local" / f"prompt-{name}.txt"
    draft.parent.mkdir(exist_ok=True)
    draft.write_text(prompt, encoding="utf-8")
    print(f"{code} — {label} · forme {shape}"
          + (f" · {posts} poteau(x)" if applies_composition else "")
          + (f" · portillon {portillon}" if portillon else "") + f" · {master['width']} px")
    print(f"brouillon écrit : {draft.relative_to(REPO)}")

    if not generate:
        return 0

    # The destination depends on the SUJET's own code, never on a reference: a reference is an input
    # the generator reads, not a place to write to. Deriving it from the reference used to send a
    # produced tracé into assets/revue-da/ whenever the reference given for it lived there.
    target = REPO / "assets" / "poc" / asset_common.CODE_FOLDER.get(code[:2], "divers")
    target.mkdir(parents=True, exist_ok=True)
    # One generation per version, and nothing is thrown away: an existing piece keeps its place and
    # the new one takes the next version number, with its own frozen prompt beside it.
    version, image = 1, target / f"{name}.png"
    while image.exists():
        version += 1
        image = target / f"{name}-v{version}.png"
    image.with_suffix(".txt").write_text(prompt, encoding="utf-8")

    print(f"consigne figée : {image.with_suffix('.txt').relative_to(REPO)}")
    # This tool generates, and stops there. Exporting the master and rebuilding the review page
    # belong to the queue (scripts/sprite-queue.py), which owns the ordering: chained from here, two
    # generations finishing at once would rebuild the page simultaneously, and the queue could not
    # prevent it.
    print(f"génération vers {image.relative_to(REPO)}")

    with asset_common.working_reference(active_reference, target):
        return subprocess.run(["php", str(REPO / "scripts" / "generate-image.php"),
                               str(image), prompt], cwd=REPO.parent).returncode


if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    posts_value = int(argv[argv.index("--posts") + 1]) if "--posts" in argv else None
    ref = Path(argv[argv.index("--ref") + 1]).resolve() if "--ref" in argv else None
    plate_value = Path(argv[argv.index("--plate") + 1]).resolve() if "--plate" in argv else None
    portillon_value = argv[argv.index("--portillon") + 1] if "--portillon" in argv else None
    raise SystemExit(build(argv[0], argv[1], posts_value, ref, "--generate" in argv,
                           portillon_value, plate_value))
