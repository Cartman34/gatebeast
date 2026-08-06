#!/usr/bin/env python3
"""Order ONE SPRITE — the single command that produces any of them, whatever the subject.

USAGE
  python3 scripts/generate-sprite.py <REF DU SUJET> <REF DE LA VARIANTE> \\
      [--ref <image> | --plate <image>] [--model <nom>] [--generate]

  Une image se commande par les deux refs, et par rien d'autre :
    generate-sprite.py OB-010 orientation-south_action-idle_shape-ns_posts-1_frame-01 --ref ...
    generate-sprite.py CH-019 orientation-south_action-idle_shape-ne_frame-01 --plate ...

  Tout ce que la consigne doit savoir de la variante — sa forme, sa composition, son portillon, et ce
  que son type déclare d'autre — est LU au référentiel, jamais retapé ici. Une ref inconnue est
  refusée, avec la liste de celles que le sujet déclare.

  --ref points at a usage sample of this SAME sujet, already assembled — the reference shows the
  piece itself. --plate points at a world reference plate where the sujet appears AMONG OTHERS — the
  reference shows a whole scene, and the consigne says so, asking the generator to pick this sujet out
  of it rather than copy the plate. The two say a different thing because they show a different thing;
  at most one may be given.

  Without --generate it stops after assembling the prompt, writing a draft under local/ so it can be
  read before anything is produced.

INTENTION
  ONE COMMAND ORDERS A SPRITE, END TO END, and there is no second one. There were two for a while —
  one for subjects laid end to end, one for the rest — and the split was never a fact of the model but
  a habit of writing a new command wherever a need appeared. Everything is a sprite laid on the grid
  beside others; what differs is the SHAPE, which says which edges a piece joins, `plain` joining none.

  Nothing about the subject is retyped on the command line: its emprise, its couvert, its shape and
  every variant its type declares are READ from the referentiel, and its description from the
  inventory, quoted word for word. What is proper to one subject — a fence's posts, a path's camber —
  lives in its own description, never in this code: a clause naming posts and rails unconditionally is
  exactly what once made this command unusable for a path.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_common
import plate_common
import production_report
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

# The posts clause is proper to the fence's own composition field, not to every assembling sujet — kept
# here because only one type declares it today, but gated on that declaration below, never applied by
# default.
POSTS_TEXT = {
    0: "AUCUN poteau vertical dans cette case : les deux lisses la traversent seules.",
    1: "UN SEUL poteau vertical, planté au CENTRE de la case.",
    2: "DEUX poteaux verticaux, plantés au tiers et aux deux tiers de la case, de sorte que le "
       "vide à gauche, le vide du milieu et le vide à droite soient égaux.",
}


def sheet_of(code: str, candidates: tuple = (), required: tuple = ()) -> tuple:
    """The label and the description of a subject, read verbatim from its inventory entry.

    `candidates` are everything this variant asks for that a fiche may describe on its own — its
    density, its proposition, its gate, its form. The fiche decides: whichever of them it writes a
    description for is the description to quote, and a value it says nothing about leaves the base one
    in place (a number of posts is a finish, rendered by a clause of the consigne instead).

    `required` are the values whose field declares `defines_kind` — another piece, not the same one
    finished differently. Their own description is mandatory: missing, sheet_description faults rather
    than letting the consigne carry the plain fence's description for a gate.

    Two candidates described at once is a fault too: which one the consigne quotes is a decision of the
    fiche, and nothing here is entitled to pick.
    """
    for path in sorted(SHEETS.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith(f"- **{code} "):
                continue
            label = line.split("**")[1].replace(code, "").strip()
            written = [value for value in candidates if value in required or asset_common.declares_qualified_description(line, value)]
            if len(written) > 1:
                raise SystemExit(f"FAULT {code} décrit à part plusieurs des valeurs demandées ensemble ({', '.join(written)}) — laquelle citer appartient à la fiche, rien ici ne la choisit.")
            description, _ = asset_common.sheet_description(line, code, written[0] if written else None)
            return label, description
    raise SystemExit(f"FAULT {code} n'est pas à l'inventaire — rien ne se produit sans fiche.")


def sujet_type(code: str) -> tuple:
    """The sujet's own entry and its type declaration in the referentiel — read, never guessed, so a
    clause proper to one variant field (composition, portillon...) only ever appears for the types that declare
    it, and so a sujet's own extra instruction is taken from the referentiel rather than assumed."""
    try:
        data = check_sujets.load()
    except check_sujets.Fault as fault:
        raise SystemExit(f"FAULT {fault}")
    sujet = data["sujets"].get(code)
    if sujet is None:
        raise SystemExit(f"FAULT {code} n'est pas au référentiel — rien ne se produit sans fiche.")

    return data["types"][sujet["type"]], sujet


def variant_of(sujet, ref, code):
    """The variant this ref designates, read from the referentiel — a variant is designated by its ref and by nothing else (sujets-et-variantes.md).

    An unknown ref is a fault, and the known ones are listed with it: a variant is declared before it is produced, and producing one nobody declared would
    put on disk an image the referentiel cannot name.
    """
    for variant in sujet["variants"]:
        if variant.get("ref") == ref:
            return variant
    known = [entry.get("ref") for entry in sujet["variants"]]
    raise SystemExit(f"FAULT {code} n'a aucune variante de ref {ref!r}. Déclarées :\n  " + "\n  ".join(known))


def wanted_variants(text, type_, code):
    """The variants asked for on the command line — the values themselves, comma-separated: `posts-2,gate-open`, `medium`.

    A variant is an enumerated value and nothing else. Each one is unique across everything a type declares, so naming the value names the variant: the
    lookup here only says which declaration it came from. Named options, one per variant, are what this replaces — `--posts` was added the day the fence
    gained its post compositions, `--portillon` the day it gained its gates, and a type could then declare a variant the referentiel accepted, the review
    page displayed and the recorder wrote, but that no command could ask for, because no option carried its name.
    """
    declarations = {key[:-1]: value["values"] for key, value in type_.items()
                    if key.endswith("s") and isinstance(value, dict) and "values" in value}
    asked = {}
    for value in (piece.strip() for piece in (text or "").split(",") if piece.strip()):
        holders = [name for name, values in declarations.items() if value in values]
        if not holders:
            known = sorted(item for values in declarations.values() for item in values)
            raise SystemExit(f"FAULT variante inconnue pour {code} : {value!r} — le type n'en déclare aucune de ce nom. Déclarées : {known}.")
        asked[holders[0]] = value

    return asked


def build(code: str, variant_ref: str, reference: Path, generate: bool, plate: Path = None,
          model: str = None) -> int:
    """One image is commanded by the ref of its sujet and the ref of its variant, and by nothing else — `OB-010` then
    `orientation-south_action-idle_shape-ew_gate-open_frame-01`. Everything the consigne needs about that variant is read from the referentiel: its shape,
    its composition, its gate, whatever its type declares. Nothing that the ref already carries is ever retyped on the command line.
    """
    posts, portillon = None, None
    if reference and plate:
        raise SystemExit("FAULT --ref et --plate sont exclusifs : une référence montre le sujet "
                         "seul, l'autre le montre parmi d'autres — jamais les deux à la fois.")
    # No image is ever ordered blind (operator, 2026-08-05). A reference is what holds a sujet's
    # treatment, its material and its light steady from one piece to the next; without one, every
    # generation reinvents them and the pieces stop matching. Refused here rather than left to whoever
    # types the command, so forgetting it is impossible instead of merely discouraged.
    if generate and not (reference or plate):
        raise SystemExit("FAULT aucune référence fournie — une génération se commande toujours avec "
                         "son image de référence (--ref pour une image du sujet seul, --plate pour "
                         "une scène où il apparaît parmi d'autres).")
    type_, sujet = sujet_type(code)
    extras = asset_common.extra_instructions(code, sujet, type_)
    # An image is commanded BY THE REF of its variant: the referentiel holds that variant, and everything the consigne needs about it — its shape, its
    # composition, its gate, whatever its type declares — is read there rather than retyped on the command line. What used to be asked value by value is
    # now asked once, by the name the variant already goes by everywhere else.
    declared = variant_of(sujet, variant_ref, code)
    shape = declared.get("shape", shape_vocab.DEFAULT_SHAPE)
    asked = {key: value for key, value in declared.items()
             if isinstance(type_.get(f"{key}s"), dict) and value}
    posts = int(asked["composition"].rsplit("-", 1)[1]) if "composition" in asked else posts
    portillon = asked.get("portillon", portillon)
    # The composition field applies to a PIECE, not to its type unconditionally: the referentiel itself
    # says so now (assets/sujets.json, portillons.rend_inapplicable) after a portillon piece was given
    # a post its own fiche never asks for — a portillon hangs on iron pivots, not a post, whatever
    # --posts says. Read here, never re-decided: a variant field that a requested value renders
    # inapplicable simply does not apply, exactly as the referentiel declares it, for any field that says so.
    portillon_field = type_.get("portillons") or {}
    inapplicable = set(portillon_field.get("rend_inapplicable", [])) if portillon else set()
    applies_composition = bool(type_.get("compositions")) and "compositions" not in inapplicable
    if posts is not None and not applies_composition:
        reason = (f"un portillon ({portillon}) n'a pas de composition — sa fiche le tient sur des "
                 f"pivots de fer" if portillon else
                 f"le type de {code} ne déclare pas de composition")
        raise SystemExit(f"FAULT {reason} — --posts n'a rien à quoi s'appliquer ici.")
    if applies_composition and posts is None:
        # The TYPE's own declared default, never a number written here: this tool kept its own, one post, while the referentiel declared two — so a piece
        # asked for without a composition came out different depending on which of the two you believed.
        posts = int(type_["compositions"]["default"].rsplit("-", 1)[1])

    # Which asked value the sheet is quoted for — THE FICHE DECIDES, and it decides for every field alike: a description proper to a value or a form is an
    # optional mark of the fiche format (inventaire/README.md), written where the sujet changes with that value. Keyed on `defines_kind` before, the clause
    # only ever reached the gates: the three grass densities and the two building propositions all carry their own descriptions, none of their fields
    # declares `defines_kind`, and every one of those variants was therefore produced with the base description — a variant that is in fact the main view.
    # `defines_kind` says which variant LEADS a label (sujets-et-variantes.md); it never said which description gets quoted, and reading it that way is what
    # made a whole family of variants unproducible in silence. What it does keep is its own guarantee: such a value MUST be described, never quietly served
    # the base text.
    required = [value for name, value in asked.items() if (type_.get(f"{name}s") or {}).get("defines_kind")]
    candidates = [value for _, value in sorted(asked.items())]
    if shape != shape_vocab.DEFAULT_SHAPE:
        candidates.append(shape)
    label, description = sheet_of(code, candidates, required)
    edges = shape_vocab.edges_of(shape)
    joined = [SIDE[edge] for edge in edges]
    reach = " et ".join(", ".join(joined).rsplit(", ", 1))
    free = [SIDE[edge] for edge in shape_vocab.EDGES if edge not in edges]
    # The canvas comes from what the sujet actually covers — its couvert when it declares one, its emprise otherwise — read from the referentiel, never
    # assumed. Asking for one cell whatever the sujet is what refused a thicket of two by two at export.
    spread = sujet.get("couvert") or sujet["emprise"]
    master = tile_scale.master_definition(spread["columns"], spread["rows"], height=sujet.get("hauteur"))
    # Every sprite is laid on the grid beside others — there is no category that does not assemble. What differs is the SHAPE: it says which edges the piece
    # joins, and `plain` joins none. The clauses about reaching an edge follow the shape, and nothing else.
    joins_edges = bool(edges)

    # A piece joining two edges that are not opposite is a CORNER, and saying only which edges it reaches has not been enough: one such piece came back as
    # a straight run. So the turn is named for what it is, and the angle it makes is said in degrees.
    opposite = {"n": "s", "s": "n", "e": "w", "w": "e"}
    turn_clause = ""
    if len(edges) == 2 and opposite[edges[0]] != edges[1]:
        turn_clause = (f"CETTE PIÈCE EST UN ANGLE, PAS UNE LIGNE DROITE : le sujet ENTRE par le bord {SIDE[edges[0]]}, atteint le centre de la case, y "
                       f"TOURNE À ANGLE DROIT et repart vers le bord {SIDE[edges[1]]}. Les deux branches se rejoignent au centre en un coude franc de "
                       f"quatre-vingt-dix degrés, et aucune ne traverse la case de part en part.")

    # Which edges the piece joins, said only when it joins any. A subject whose shape is `plain` joins none: telling it about edges it does not reach would
    # describe an assembly that does not exist, which is exactly what made the older command unusable for a lone subject.
    join_clause = ""
    if joins_edges:
        free_clause = "Les bords " + " et ".join(free) + " restent libres : rien ne les touche." if free else ""
        join_clause = (f"LA PIÈCE DEMANDÉE : le sujet passe par le CENTRE de la case et rejoint le bord {reach}, et eux seuls.\n{free_clause}")
    else:
        join_clause = ("LE SUJET EST SEUL DANS SA CASE : il ne rejoint aucun bord, rien ne se prolonge hors de lui, et il ne s'assemble avec rien.")

    composition_clause = ""
    if applies_composition:
        # The rails run in one piece only when nothing interrupts them. A portillon replaces the central bay, so claiming an unbroken run there contradicts
        # the very sheet quoted below — found by rereading the assembled consigne before the first two-post gate was ordered. What both cases share, and all
        # that matters for the join, is that the rails meet the cell edge at the same height and thickness as the reference. An ANGLE never runs in one
        # piece either: its two branches meet at the corner post rather than crossing the cell.
        run = ("Les lisses courent de chaque bord rejoint jusqu'au poteau qui porte le battant"
               if portillon and portillon != "gate-none" else
               "Les deux lisses courent d'un bord rejoint jusqu'au poteau d'angle, où elles tournent"
               if turn_clause else
               "Les deux lisses courent d'un seul tenant d'un bord rejoint à l'autre")
        composition_clause = f"""{POSTS_TEXT[posts]}
{run}, à la même hauteur et à la même
épaisseur qu'elles ont dans l'image de référence, pour que deux cases posées bout à bout se
prolongent sans décrochement.
"""

    active_reference = reference or plate
    clause = ""
    if reference:
        clause = f"""
RÉFÉRENCE — ouvre et regarde le fichier {asset_common.reference_address(reference)}. C'est une image
déjà produite de ce même sujet, montrant plusieurs de ses pièces assemblées, dont celle qu'on te
demande ici. Elle donne la matière, la couleur et la lumière à reprendre à l'identique. On te demande
d'extraire cette pièce précise et de la dessiner seule, pas d'en inventer une nouvelle.
"""
    elif plate:
        clause = f"""
RÉFÉRENCE — ouvre et regarde le fichier {asset_common.reference_address(plate)}. C'est une scène du
monde, déjà validée, où {label} apparaît PARMI D'AUTRES éléments — pas une image de ce seul sujet.
Elle donne le style, la matière, la lumière ET L'ANGLE DE PRISE DE VUE à reprendre pour CE SUJET
précis, repéré dans l'image ; le reste de la scène ne se copie pas et n'apparaît pas dans le résultat.
"""

    prompt = f"""{plate_common.STYLE_FR}

{asset_common.CAMERA_FR}

ASSET DE JEU — {label}, SEUL SUJET DE L'IMAGE, destiné à être posé comme sprite sur une carte vue de
dessus.

DIMENSIONS ATTENDUES : l'image fait {spread['columns']} case(s) de large — c'est contractuel. Sa hauteur
suit ce que le sujet occupe réellement une fois la caméra appliquée : un sujet qui a de l'épaisseur ou
qui se dresse monte librement au-dessus de son emprise, et l'image le suit.

{asset_common.CADRAGE_TRACE if joins_edges else asset_common.CADRAGE_CUTOUT}

{asset_common.TRACE_FR if joins_edges else ""}

{join_clause}
{turn_clause}
{composition_clause}
{clause}
{asset_common.REGLES_FR}

LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :
{code} : {description}

{asset_common.extra_clause(extras)}

{asset_common.RAPPEL_CAMERA_FR}
"""

    # The default shape is never written, here as in a ref: a subject that joins no edge has nothing to say about its shape.
    name = code if shape == shape_vocab.DEFAULT_SHAPE else f"{code}_shape-{shape}"
    if applies_composition:
        name += f"_posts-{posts}"
    if portillon:
        name += f"_portillon-{portillon}"
    # Any other variant asked for names the file too, so two of them never land on the same image.
    for other, value in sorted(asked.items()):
        if other not in ("composition", "portillon"):
            name += f"_{other}-{value}"
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
    # Rebuilding the review page still belongs to the queue (scripts/sprite-queue.py), which owns the
    # ordering: two generations finishing at once would rebuild that one shared page simultaneously.
    # The export and the report, themselves, belong HERE — they concern this image and nothing else,
    # they cost no shared resource, and an image without its report is an image nobody can judge.
    print(f"génération vers {image.relative_to(REPO)}")

    run = production_report.Run(name)
    with run.step("consigne"):
        pass  # already assembled and frozen above; the step records it as done
    try:
        with run.step("génération"):
            done = subprocess.run(["php", str(REPO / "scripts" / "generate-image.php"),
                                   str(image), prompt], cwd=REPO.parent,
                                  capture_output=True, text=True)
            print(done.stdout, end="", flush=True)
            run.session = production_report.Run.session_of(done.stdout)
            failed = done.returncode
            if failed:
                raise SystemExit(f"FAULT la génération de {name} a échoué (code {failed}).")
        with run.step("redimensionnement"):
            # The delivery resize belongs to the run, and so does its own account of itself: the
            # sizes, the measured silhouette and the pose point it computes are exactly what the
            # final report has to carry (operator, 2026-08-05). Captured rather than left on the
            # terminal, or it would be lost the moment the run ends.
            exported = subprocess.run(
                ["python3", str(REPO / "scripts" / "export-asset.py"), str(image)],
                cwd=REPO.parent, capture_output=True, text=True)
            print(exported.stdout, end="", flush=True)
            extras["Redimensionnement à la définition de livraison"] = (
                "```\n" + (exported.stdout or exported.stderr or "aucune sortie").strip() + "\n```")
            if exported.returncode:
                raise SystemExit(f"FAULT le redimensionnement de {name} a échoué.")
        with run.step("inscription"):
            # Chained here, never left to whoever remembers: the rule is that every sprite produced is recorded under its variant, without exception. A
            # sprite was produced and forgotten the day this was a separate command someone had to think of running.
            recorded = subprocess.run(
                ["python3", str(REPO / "scripts" / "record-asset.py"), str(image),
                 "--code", code, "--type", sujet["type"], "--variant", variant_ref],
                cwd=REPO.parent, capture_output=True, text=True)
            print(recorded.stdout, end="", flush=True)
            if recorded.returncode:
                raise SystemExit(f"FAULT l'inscription de {name} a échoué : "
                                 f"{(recorded.stderr or recorded.stdout).strip().splitlines()[-1]}")
    finally:
        # Written whatever happened: a run that broke is exactly the one whose timings and consigne
        # someone will want to read.
        with run.step("rapport"):
            run.write(image, prompt, extras)

    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    reference = Path(argv[argv.index("--ref") + 1]).resolve() if "--ref" in argv else None
    plate_value = Path(argv[argv.index("--plate") + 1]).resolve() if "--plate" in argv else None
    chosen = argv[argv.index("--model") + 1] if "--model" in argv else None
    raise SystemExit(build(argv[0], argv[1], reference, "--generate" in argv, plate_value, chosen))
