#!/usr/bin/env python3
"""Order ONE SPRITE — the single command that produces any of them, whatever the subject.

USAGE
  python3 scripts/generate-sprite.py <REF DU SUJET> <REF DE LA VARIANTE> \\
      [--ref <image> | --plate <image>] [--model <nom>] [--rework "<motif du rejet>"] [--generate]

  --rework est la REPRISE UNIQUE que la chaîne de production autorise : le motif exact du rejet, cité
  en toutes lettres, ajouté en fin de consigne. Il ne se donne qu'une fois par version — une seconde
  reprise met l'image en défaut, elle ne se retente pas.

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
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_common
import asset_theme
import plate_common
import production_report
import shape_vocab
import tile_scale

# check-subjects.py is hyphenated, so it is loaded by path (record-asset.py already uses this mechanism
# for the same file, and cut-asset.py before it).
CHECK_SUBJECTS = Path(__file__).resolve().parent / "check-subjects.py"
spec = importlib.util.spec_from_file_location("check_subjects", CHECK_SUBJECTS)
check_subjects = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_subjects)

REPO = Path(__file__).resolve().parent.parent
SHEETS = REPO / "doc" / "conception" / "referentiels" / "visuel" / "inventaire"
# Un fichier par description, lu en entier. L'inventaire garde ce qui n'est pas la description : code, profil, type, emprise, hauteur, formes, décisions et raisons.
DESCRIPTIONS = REPO / "assets" / "descriptions"
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


def current_sprite(code: str, variant_ref: str = None):
    """The subject's own current deliverable, or None when it has never been drawn — the reference a generation takes by default.

    Reads the referentiel rather than the disk: an image on the disk that no variant claims is precisely what the referentiel exists to rule out, and taking one
    as a reference would propagate whatever it is. The MAIN view is preferred when it has one, since that is the view the others are meant to agree with.
    """
    data = json.loads((REPO / "assets" / "subjects.json").read_text(encoding="utf-8"))
    subject = data.get("subjects", {}).get(code)
    if not subject:
        return None
    # LE VARIANT LUI-MÊME D'ABORD, ET C'EST UNE FAUTE PAYÉE : la référence dit de reprendre la matière et la couleur À L'IDENTIQUE, donc donner la vue principale à
    # un variant qui a sa propre palette efface exactement ce qui le distingue. Constaté sur la proposition 2 du centre de soin, dont les couleurs de la scène de
    # référence ont été remplacées par celles de la vue principale (opérateur, 2026-08-07). Sa version précédente est la bonne référence : c'est elle qui porte ce
    # qu'il est. La vue principale ne sert qu'à un variant qui n'a encore jamais été dessiné.
    variants = sorted(subject.get("variants", []),
                      key=lambda v: (v.get("ref") != variant_ref, not v.get("main", False)))
    for variant in variants:
        for representation in variant.get("representations", []):
            if representation.get("status") != "current":
                continue
            path = REPO / "assets" / representation["path"]
            if path.is_file():
                return path

    return None


# A VARIANT FIELD AND THE TYPE KEY THAT DECLARES IT ARE THE SAME WORD, ONE SINGULAR AND ONE PLURAL — and the plural was built by adding an "s", which held only
# as long as the vocabulary was French. `densite` gave `densites` and `portillon` gave `portillons`; in American English `density` gives `densities`, and
# `density` + "s" finds nothing. The grass then lost its own description and every density came out as the sparse one — caught by diff-prompts.sh on 2026-08-08,
# before a single generation was ordered. String surgery is not a naming rule: the irregular pairs are declared here, once, and both directions read them.
IRREGULAR = {"density": "densities"}
COLLECTION_OF = {field: plural for field, plural in IRREGULAR.items()}
FIELD_OF = {plural: field for field, plural in IRREGULAR.items()}


def collection_of(field: str) -> str:
    """The type key that declares a variant field: its irregular plural if it has one, else the field plus an s."""
    return COLLECTION_OF.get(field, field + "s")


def field_of(collection: str) -> str:
    """The variant field a type key declares — the exact reverse of collection_of, never a truncation."""
    return FIELD_OF.get(collection, collection[:-1])


def sheet_of(code: str, candidates: tuple = (), replacing: tuple = ()) -> tuple:
    """The label and the description of a subject, read verbatim from its inventory entry.

    `candidates` are everything this variant asks for that the entry may describe on its own — its density, its proposition, its gate, its form. Whichever of
    them the entry describes apart is quoted; a value it says nothing about adds nothing (a number of posts is a finish, rendered by a clause of the consigne).

    A described value COMPLETES the subject's own description by default, and REPLACES it only when its field is in `replacing` — the fields declaring
    `defines_kind`, which say the variant is another piece rather than the same one finished differently. That default is the operator's (2026-08-06): three
    densities of the same grass differ by a count of tufts and nothing else, so the subject is described ONCE and each density writes only its quantity. Making
    every value replace the description forced the whole grass to be rewritten three times over — three texts to keep in step for one number that changed, and
    the two that were not being read came out identical to the third. A gate stays a replacement: it is not a fence with an option.

    A replacing value's own description is mandatory: missing, sheet_description faults rather than letting the consigne carry the plain fence's description for
    a gate. Two values replacing at once is a fault too — which one the consigne quotes belongs to the entry, and nothing here is entitled to pick. Several
    values COMPLETING is not a fault: they add up, in the order the variant declares them.
    """
    # LA DESCRIPTION SE LIT DANS SON PROPRE FICHIER, PRIS EN ENTIER — on ne cherche plus l'italique dans un document (opérateur, 2026-08-07 : « je te déconseille de
    # parser un MD, soit tu prends tout, soit t'en fais un autre »). Le fichier EST la description : rien n'y est reconnu, donc rien ne peut y être manqué. C'est
    # l'extraction par reconnaissance de forme qui obligeait une fiche à tenir sur une ligne, et qui refusait une génération sans jamais en dire la cause.
    # L'ÉTIQUETTE, ELLE, RESTE CELLE DE L'INVENTAIRE : c'est un nom d'affichage, pas la matière de la consigne.
    label = None
    for path in sorted(SHEETS.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"- **{code} "):
                label = line.split("**")[1].replace(code, "").strip()
                break
        if label is not None:
            break
    if label is None:
        raise SystemExit(f"FAULT {code} n'est pas à l'inventaire — rien ne se produit sans fiche.")

    def description_file(qualifier=None):
        return DESCRIPTIONS / (f"{code}_{qualifier}.md" if qualifier else f"{code}.md")

    described = [value for value in candidates if value in replacing or description_file(value).is_file()]
    replaced = [value for value in described if value in replacing]
    if len(replaced) > 1:
        raise SystemExit(f"FAULT {code} : {', '.join(replaced)} remplacent tous la description du sujet et sont demandés ensemble — laquelle citer appartient à l'inventaire, pas à cet outil.")
    if replaced:
        chosen = description_file(replaced[0])
        if not chosen.is_file():
            raise SystemExit(f"FAULT {code} n'a pas de description propre à {replaced[0]!r} — elle est obligatoire pour ce qualificatif, la description de base ne s'y substitue jamais. "
                             f"Fichier attendu : {chosen.relative_to(REPO)}")
        return label, chosen.read_text(encoding="utf-8").strip()
    base = description_file()
    if not base.is_file():
        raise SystemExit(f"FAULT {code} n'a pas de description écrite — elle est obligatoire. Fichier attendu : {base.relative_to(REPO)}")
    parts = [description_file(value).read_text(encoding="utf-8").strip() for value in described]

    return label, "\n".join([base.read_text(encoding="utf-8").strip()] + parts)


def sujet_type(code: str) -> tuple:
    """The sujet's own entry and its type declaration in the referentiel — read, never guessed, so a
    clause proper to one variant field (composition, portillon...) only ever appears for the types that declare
    it, and so a sujet's own extra instruction is taken from the referentiel rather than assumed."""
    try:
        data = check_subjects.load()
    except check_subjects.Fault as fault:
        raise SystemExit(f"FAULT {fault}")
    subject = data["subjects"].get(code)
    if subject is None:
        raise SystemExit(f"FAULT {code} n'est pas au référentiel — rien ne se produit sans fiche.")

    return data["types"][subject["type"]], subject


def variant_of(subject, ref, code):
    """The variant this ref designates, read from the referentiel — a variant is designated by its ref and by nothing else (sujets-et-variantes.md).

    An unknown ref is a fault, and the known ones are listed with it: a variant is declared before it is produced, and producing one nobody declared would
    put on disk an image the referentiel cannot name.
    """
    for variant in subject["variants"]:
        if variant.get("ref") == ref:
            return variant
    known = [entry.get("ref") for entry in subject["variants"]]
    raise SystemExit(f"FAULT {code} n'a aucune variante de ref {ref!r}. Déclarées :\n  " + "\n  ".join(known))


def wanted_variants(text, type_, code):
    """The variants asked for on the command line — the values themselves, comma-separated: `posts-2,gate-open`, `medium`.

    A variant is an enumerated value and nothing else. Each one is unique across everything a type declares, so naming the value names the variant: the
    lookup here only says which declaration it came from. Named options, one per variant, are what this replaces — `--posts` was added the day the fence
    gained its post compositions, `--portillon` the day it gained its gates, and a type could then declare a variant the referentiel accepted, the review
    page displayed and the recorder wrote, but that no command could ask for, because no option carried its name.
    """
    declarations = {field_of(key): value["values"] for key, value in type_.items()
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
          model: str = None, rework: str = None) -> int:
    """One image is commanded by the ref of its sujet and the ref of its variant, and by nothing else — `OB-010` then
    `orientation-south_action-idle_shape-ew_gate-open_frame-01`. Everything the consigne needs about that variant is read from the referentiel: its shape,
    its composition, its gate, whatever its type declares. Nothing that the ref already carries is ever retyped on the command line.
    """
    posts, gate = None, None
    if reference and plate:
        raise SystemExit("FAULT --ref et --plate sont exclusifs : une référence montre le sujet "
                         "seul, l'autre le montre parmi d'autres — jamais les deux à la fois.")
    # No image is ever ordered blind (operator, 2026-08-05). A reference is what holds a sujet's
    # treatment, its material and its light steady from one piece to the next; without one, every
    # generation reinvents them and the pieces stop matching. Refused here rather than left to whoever
    # types the command, so forgetting it is impossible instead of merely discouraged.
    # LA COMMANDE CHOISIT LA RÉFÉRENCE ELLE-MÊME, ET C'EST LA CORRECTION D'UNE FAUTE PAYÉE TROIS FOIS. Une planche du monde porte un point de fuite, et le sujet
    # produit avec elle en référence le reprend — même quand sa fiche lui interdit d'être vu de biais (constaté sur le centre de soin, 2026-08-07). Ce qu'il VOIT
    # pèse plus lourd que ce qu'on lui écrit. La bonne référence est donc toujours la sprite courante du sujet lui-même quand elle existe : c'est elle qui tient
    # sa matière, sa lumière et sa projection d'une pièce à la suivante. La planche ne sert qu'au tout premier dessin, quand rien n'existe encore de lui.
    #
    # Laissé au choix de celui qui tape la commande, ce point a produit trois pièces de clôture qui n'étaient pas le même objet, et un bâtiment qui converge.
    if generate and not (reference or plate):
        current = current_sprite(code, variant_ref)
        if current is not None:
            reference = current
            print(f"référence choisie : {current.relative_to(REPO)} — la sprite courante du sujet, jamais une planche du monde")
        else:
            raise SystemExit("FAULT aucune référence fournie et ce sujet n'a encore aucune sprite — c'est un premier dessin, donnez-lui une planche du monde avec "
                             "--plate, et regardez sa projection avant de l'inscrire.")
    type_, subject = sujet_type(code)
    extras = asset_common.extra_instructions(code, subject, type_)
    # An image is commanded BY THE REF of its variant: the referentiel holds that variant, and everything the consigne needs about it — its shape, its
    # composition, its gate, whatever its type declares — is read there rather than retyped on the command line. What used to be asked value by value is
    # now asked once, by the name the variant already goes by everywhere else.
    declared = variant_of(subject, variant_ref, code)
    shape = declared.get("shape", shape_vocab.DEFAULT_SHAPE)
    asked = {key: value for key, value in declared.items()
             if isinstance(type_.get(collection_of(key)), dict) and value}
    posts = int(asked["composition"].rsplit("-", 1)[1]) if "composition" in asked else posts
    gate = asked.get("gate", gate)
    # The composition field applies to a PIECE, not to its type unconditionally: the referentiel itself
    # says so now (assets/subjects.json, portillons.makes_inapplicable) after a portillon piece was given
    # a post its own fiche never asks for — a portillon hangs on iron pivots, not a post, whatever
    # --posts says. Read here, never re-decided: a variant field that a requested value renders
    # inapplicable simply does not apply, exactly as the referentiel declares it, for any field that says so.
    portillon_field = type_.get("gates") or {}
    inapplicable = set(portillon_field.get("makes_inapplicable", [])) if gate else set()
    applies_composition = bool(type_.get("compositions")) and "compositions" not in inapplicable
    if posts is not None and not applies_composition:
        reason = (f"un portillon ({gate}) n'a pas de composition — sa fiche le tient sur des "
                 f"pivots de fer" if gate else
                 f"le type de {code} ne déclare pas de composition")
        raise SystemExit(f"FAULT {reason} — --posts n'a rien à quoi s'appliquer ici.")
    if applies_composition and posts is None:
        # The TYPE's own declared default, never a number written here: this tool kept its own, one post, while the referentiel declared two — so a piece
        # asked for without a composition came out different depending on which of the two you believed.
        posts = int(type_["compositions"]["default"].rsplit("-", 1)[1])

    # Which values the entry is quoted for — THE ENTRY DECIDES, for every field alike: a description proper to a value or a form is an optional mark of the
    # entry's format (inventaire/README.md), written where the subject changes with that value. Keyed on `defines_kind` before, the clause only ever reached the
    # gates: the three grass densities and the two building propositions all carry their own descriptions, none of their fields declares `defines_kind`, and
    # every one of those variants was therefore produced with the base description — a variant that was in fact the main view.
    # `defines_kind` keeps a job here, but a narrower one: it says whether a described value REPLACES the subject's description or COMPLETES it. Replacing is
    # for another piece — a gate is not a fence with an option. Completing is the default and the ordinary case: a density is the same grass in a different
    # quantity, so the grass is described once and the density adds its count.
    # A VALUE THE VARIANT DOES NOT CARRY FALLS BACK TO ITS FIELD'S DEFAULT, exactly as a composition does (sujets-et-variantes.md, decision 18): the main view
    # of the grass declares no density and must still be the sparse one, whose count lives in that value's own description.
    replacing = [value for name, value in asked.items() if (type_.get(collection_of(name)) or {}).get("defines_kind")]
    resolved = dict(asked)
    for name, declaration in type_.items():
        field = field_of(name)
        if isinstance(declaration, dict) and declaration.get("default") and field not in resolved and name not in inapplicable:
            resolved[field] = declaration["default"]
    candidates = [value for _, value in sorted(resolved.items())]
    if shape != shape_vocab.DEFAULT_SHAPE:
        candidates.append(shape)
    label, description = sheet_of(code, candidates, replacing)
    edges = shape_vocab.edges_of(shape)
    joined = [SIDE[edge] for edge in edges]
    reach = " et ".join(", ".join(joined).rsplit(", ", 1))
    free = [SIDE[edge] for edge in shape_vocab.EDGES if edge not in edges]
    # The canvas comes from what the sujet actually covers — its couvert when it declares one, its emprise otherwise — read from the referentiel, never
    # assumed. Asking for one cell whatever the sujet is what refused a thicket of two by two at export.
    spread = subject.get("cover") or subject["footprint"]
    master = tile_scale.master_definition(spread["columns"], spread["rows"], height=subject.get("height"))
    # The height IN TILES the consigne asks for, said out loud. It was computed here and used only to check the file afterwards, never told to the generator,
    # which was left to invent a proportion: the care centre came back at twelve tiles of height for eight declared, the thicket at 1.6 for six, and the whole
    # mock-up looked wrongly calibrated (operator, 2026-08-06). One speaks to the generator in tiles, so it is said in tiles.
    # The height IN TILES the consigne asks for, said as a BAND rather than a figure: no single height is right — a ridge, a chimney, a crown leaning one way
    # move it — but there is a floor and a ceiling, and both come from the model (tile_scale.master_band). Said in tiles, because the generator is spoken to in
    # tiles, and written with commas, because the consigne is French and a decimal point in it reads as a thousands mark.
    per_tile = master["width"] / spread["columns"]
    floor, ceiling = tile_scale.master_band(spread["columns"], spread["rows"], height=subject.get("height"))
    low = f"{round(floor / per_tile, 1)}".replace(".", ",")
    high = f"{round(ceiling / per_tile, 1)}".replace(".", ",")
    # THE GROUND RECTANGLE, SAID AS THE CAMERA ACTUALLY SEES IT — and read from the model, never retyped. The clause used to claim the depth was respected "tile
    # for tile" while the dimensions clause said the camera crushed it: a plain contradiction, and one that pushes the generator towards perspective depth cues to
    # make a ten-deep rectangle read as ten deep inside fewer tiles of image.
    #
    # THE CLAUSE BRANCHES EXACTLY AS THE MODEL DOES, AND READS THE MODEL'S OWN FACTOR — never a figure typed here. tile_scale.master_definition foreshortens the
    # ground depth ONLY for a height that RISES: a flat piece (height zero or recessed) keeps a square canvas on purpose, because it is an assembling piece and
    # must meet its neighbours edge to edge. Two wrong versions preceded this one: "tile for tile" for everyone, which contradicted the height band and pushed the
    # generator towards perspective cues; then 0.866 for everyone, which told a path its cell was foreshortened while its own band asked for a full square.
    # ONE RULE FOR EVERY SUBJECT, FLAT OR STANDING, AND READ OFF THE PIXEL LADDER. A projected tile is 96 × 84, so a ground depth is drawn at 84/96 of its measure
    # whatever stands on it — the exemption that kept flat pieces square was a tile seen from straight above, not from the world's camera. Two wrong versions
    # preceded this one: "tile for tile" for everyone, which contradicted the height band; then a branch that told a path its cell was square, which contradicted
    # the projected tile the mounter now lays it on.
    rounded_depth = f"{round(tile_scale.projected_depth_tiles(subject['footprint']['rows']), 2)}".replace(".", ",")
    ground_clause = (
        f"CE RECTANGLE EST VU DE HAUT, DONC RACCOURCI EN PROFONDEUR : sous la plongée à soixante degrés, sa profondeur se dessine sur "
        f"{rounded_depth} case(s) de haut dans l'image, pour {subject['footprint']['columns']} case(s) de large. Sa largeur, elle, ne raccourcit pas."
    )
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
               if gate and gate != "gate-none" else
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
CE QUE TU PRENDS DE CETTE IMAGE, ET RIEN D'AUTRE : la MATIÈRE (pierre, bois, tuile, feuillage et leur
grain), les COULEURS exactes, la LUMIÈRE et son ombrage, le niveau de détail, et la FORME PROPRE du
sujet — son plan, ses proportions, ses éléments et leur place.
CE QUE TU N'EN PRENDS PAS, ET C'EST AUSSI IMPORTANT : sa PRISE DE VUE. Elle peut porter une
perspective, une convergence, un point de fuite, des murs qui penchent l'un vers l'autre, une façade
qui s'évase : ce sont des défauts qu'on corrige, pas des traits à reprendre. Tu redresses ce que tu
vois en AXONOMÉTRIE ORTHOGRAPHIQUE, comme décrit plus haut — arêtes verticales parallèles entre elles,
fuyantes parallèles entre elles, aucun rétrécissement ni vers le bas ni vers le haut.
LA RÉFÉRENCE FAIT FOI POUR LA MATIÈRE ET POUR LA FORME, JAMAIS POUR LA PROJECTION.
"""
    elif plate:
        clause = f"""
RÉFÉRENCE — ouvre et regarde le fichier {asset_common.reference_address(plate)}. C'est une scène du
monde, déjà validée, où {label} apparaît PARMI D'AUTRES éléments — pas une image de ce seul sujet.
CE QUE TU PRENDS DE CETTE SCÈNE, ET RIEN D'AUTRE : le STYLE, la MATIÈRE, les COULEURS et la LUMIÈRE de
CE SUJET précis, repéré dans l'image. Le reste de la scène ne se copie pas et n'apparaît pas dans le
résultat : ni les éléments voisins, ni le sol, ni le cadrage, ni la composition.
CE QUE TU N'EN PRENDS PAS, ET IL FAUT LE DIRE PARCE QUE L'IMAGE LE MONTRE : sa PRISE DE VUE. Cette
scène est rendue AVEC UN POINT DE FUITE — les bâtiments y montrent la face tournée vers le centre de
l'image, les fuyantes s'y rejoignent, les objets loin du centre y penchent. Rien de tout cela ne se
reprend. Une sprite se dessine une fois et se pose n'importe où sur la carte : elle ne peut donc pas
dépendre d'une position dans une scène. Tu reprends l'angle décrit plus haut, en PROJECTION PARALLÈLE,
et tu redresses tout ce que la scène montre de convergent.
"""

    # THE PRODUCTION CHAIN'S SINGLE RETRY, TOOLED AT LAST. The chain has allowed it from the start — "one retry at most, with a prompt reinforced ON THE EXACT
    # GROUND OF THE REJECTION" — but nothing could state that ground: relaunching meant drawing the same prompt again at random, which is not a retry, it is a
    # second draw. The clause comes LAST, after the camera reminder, because what the generator reads last weighs the most; and it names what was missed without
    # restating the subject, whose sheet already says it — repeating the sheet would fix nothing, since the sheet is precisely what was just followed badly.
    rework_clause = ""
    if rework:
        rework_clause = (
            "\nREPRISE — LA VERSION PRÉCÉDENTE A ÉTÉ REJETÉE SUR CE POINT PRÉCIS, ET C'EST LE SEUL À CORRIGER :\n"
            f"{rework}\n"
            "Tout le reste de l'image précédente était juste et se reprend tel quel : même plan, même palette, même matière, même lumière, même projection.\n"
        )

    prompt = f"""{asset_common.CONTEXTE_FR}

{plate_common.STYLE_FR}

{asset_common.CAMERA_FR}

ASSET DE JEU — {label}, SEUL SUJET DE L'IMAGE, destiné à être posé comme sprite sur une carte vue de
dessus.

DIMENSIONS ATTENDUES, ET ELLES SONT CONTRACTUELLES : l'image fait EXACTEMENT {spread['columns']} case(s) de large, et sa hauteur tient ENTRE {low} ET {high} case(s).
Cette fourchette n'est pas indicative : en dessous, le sujet est écrasé dans son emprise et ne se dresse plus ; au-dessus, il écrase tout ce qui l'entoure. Elle vient de
la caméra appliquée à la taille réelle du sujet — sa profondeur au sol, plus ce qu'il dresse au-dessus, écrasé par la plongée.

CE QUI TOUCHE LE SOL ET CE QUI S'ÉLÈVE, ET C'EST LA CHOSE LA PLUS SOUVENT MANQUÉE. Le sujet POSE AU SOL un rectangle de {subject['footprint']['columns']} case(s) de large sur
{subject['footprint']['rows']} case(s) de profondeur. {ground_clause}
LE BORD DU FOND FAIT EXACTEMENT LA MÊME LARGEUR QUE LE BORD DE DEVANT, et les deux côtés du rectangle sont PARALLÈLES : un rectangle qui se rétrécit vers le fond est une perspective, et elle est
interdite. Il occupe le BAS de l'image, et sa dernière rangée tolère un léger débord pour que la matière se raccorde à ce qui l'entoure.
TOUT CE QUE LE SUJET DRESSE — murs, toit, tronc, feuillage — MONTE AU-DESSUS de ce rectangle et occupe le reste de la hauteur de l'image. Un sujet
entièrement contenu dans son rectangle au sol, sans rien qui s'élève par-dessus, est refusé : c'est un sujet écrasé, pas un sujet vu sous cette caméra.

LE SUJET REMPLIT LE CADRE : il touche le haut et le bas, à une fine marge transparente près.

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
{rework_clause}"""

    # The default shape is never written, here as in a ref: a subject that joins no edge has nothing to say about its shape.
    name = code if shape == shape_vocab.DEFAULT_SHAPE else f"{code}_shape-{shape}"
    if applies_composition:
        name += f"_posts-{posts}"
    if gate:
        name += f"_portillon-{gate}"
    # Any other variant asked for names the file too, so two of them never land on the same image.
    for other, value in sorted(asked.items()):
        if other not in ("composition", "gate"):
            name += f"_{other}-{value}"
    # LE BROUILLON EST VRAIMENT TEMPORAIRE, DONC IL VA SOUS var/tmp/ (opérateur, 2026-08-06) : il se refait d'une commande, et la consigne d'une image RÉELLEMENT produite
    # est figée à côté de cette image. Le reste de var/ garde ce qui se conserve — rapports, journaux. Jamais dans local/, qui est le répertoire de l'agent et où l'outillage
    # n'écrit rien : trente-cinq brouillons s'y étaient accumulés sans que personne sache qui les produisait.
    draft = REPO / "var" / "tmp" / "consignes" / f"{name}.txt"
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(prompt, encoding="utf-8")
    print(f"{code} — {label} · forme {shape}"
          + (f" · {posts} poteau(x)" if applies_composition else "")
          + (f" · portillon {gate}" if gate else "") + f" · {master['width']} px")
    print(f"brouillon écrit : {draft.relative_to(REPO)}")

    if not generate:
        return 0

    # The destination depends on the SUJET's own code, never on a reference: a reference is an input
    # the generator reads, not a place to write to. Deriving it from the reference used to send a
    # produced tracé into assets/revue-da/ whenever the reference given for it lived there.
    # LE THÈME S'INTERCALE ICI, ET NULLE PART AILLEURS DANS CETTE COMMANDE : un thème regroupe tous les sprites du jeu, donc il se lit au moment où l'on décide
    # où une image se pose. Le thème d'origine ne porte pas son nom dans les chemins — le fragment est vide pour lui —, si bien que ce branchement ne déplace
    # aucun fichier tant qu'il est le thème courant, et qu'un second thème n'aura qu'à se déclarer pour vivre à côté du premier.
    target = REPO / "assets" / "poc" / asset_theme.subtree() / asset_common.CODE_FOLDER.get(code[:2], "divers")
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
                 "--code", code, "--type", subject["type"], "--variant", variant_ref],
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
    rework = argv[argv.index("--rework") + 1] if "--rework" in argv else None
    raise SystemExit(build(argv[0], argv[1], reference, "--generate" in argv, plate_value, chosen, rework))
