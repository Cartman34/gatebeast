#!/usr/bin/env python3
"""Order ONE SPRITE — the single command that produces any of them, whatever the subject.

USAGE
  python3 scripts/generate-sprite.py <REF DU SUJET> <REF DE LA VARIANTE> \\
      [--ref <image> | --plate <image>] [--model <nom>] [--rework "<motif>" | --rework @<fichier>] [--generate]
  python3 scripts/generate-sprite.py -h|--help — ce texte, et rien n'est produit.

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

  LA CONSIGNE EST DÉCOUPÉE EN SECTIONS TITRÉES, et un fichier « .parts.json » écrit à côté d'elle dit
  quel niveau a écrit chacune — `common`, `type`, `variant`, `description`, `parameters`, `call`, les
  six étant des identifiants, donc anglais. Il se lit par « php scripts/show-prompt-parts.php », et
  « --grep "<phrase>" » répond à la seule question utile devant une image fausse : d'où vient cette
  phrase, donc où se porte le correctif.

  With --generate the command runs the chain to its end: it produces the image, resizes it to the
  delivery definition, records it under its variant, AND THEN REPUBLISHES THE SPRITES REVIEW PAGE —
  an image that exists without appearing on that page exists for nobody, and gets produced again.

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
import contextlib
import datetime
import fcntl
import hashlib
import importlib.util
import json
import math
import os
import re
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
# for the same file, and the cutting step of the old chain before it).
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

# CE QU'ON VOIT DU PERSONNAGE SELON L'ORIENTATION QU'IL DÉCLARE, et rien d'autre : sa silhouette, ses vêtements et ses couleurs restent à sa description, qui ne
# change pas d'une vue à l'autre. La phrase de posture vivait dans cette description, en toutes lettres et au sud — envoyée telle quelle pour la vue de dos, elle
# demandait exactement le contraire de ce que la variante déclarait, et une consigne qui se contredit produit une image au hasard.
#
# AND NOT ONE OF THESE FOUR SAYS « PROFILE » OR « FRONT VIEW » ANY MORE, WHICH IS THE FAULT THAT COST THE MOST. « De profil » names an eye-level side view: it
# contradicts the sixty-degree plunge the socle prescribes, and the generator obeys the clause closest to the subject — so it drew the creature at eye level and
# the operator refused it, « mauvais angle caméra » (2026-08-12). These clauses now say only WHICH WAY THE SUBJECT IS TURNED; from where it is looked at belongs
# to the socle, and to the socle alone.
ORIENTATION_TEXT = {
    "south": "IL EST TOURNÉ VERS NOUS : sa face avant, son visage et l'avant de son corps sont du côté du BAS de l'image.",
    "north": "IL EST TOURNÉ VERS LE FOND : on ne voit PAS son visage — c'est l'arrière de sa tête et l'arrière de son corps qui sont tournés vers nous.",
    # THE EAST VIEW IS SPELLED OUT HARDER THAN THE OTHERS, AND IT IS NOT A WHIM: it came back wrong three times on 2026-08-12, drawn turned left — which is the
    # WEST view. Turning left is the common way to draw an animal, and a clause naming a side is answered by the habit rather than by the ask. So the direction is
    # said three times and in three ways — where the muzzle points, which edge of the image it points AT, and where the back is.
    "east": ("IL EST TOURNÉ VERS LA DROITE DE L'IMAGE. SON VISAGE, SON MUSEAU ET SON REGARD POINTENT VERS LE BORD DROIT, sa queue ou son dos vers le BORD GAUCHE, "
             "et c'est son flanc GAUCHE qui est tourné vers nous. Un sujet qui regarde vers la gauche de l'image est la vue de l'ouest, et c'est un refus."),
    "west": ("IL EST TOURNÉ VERS LA GAUCHE DE L'IMAGE. SON VISAGE, SON MUSEAU ET SON REGARD POINTENT VERS LE BORD GAUCHE, sa queue ou son dos vers le BORD DROIT, "
             "et c'est son flanc DROIT qui est tourné vers nous."),
}

# WHAT THE SUBJECT IS DOING — an axis the model has always declared and the prompt never carried. Asked for the four walking views of the human on 2026-08-12, the
# assembled prompt said nothing about walking at all: it would have produced a standing figure, and the reproach made to the image would have had no ground. The
# resting action says nothing, as a default should; every other action names the pose it wants, once, here.
ACTION_TEXT = {
    "walk": ("IL EST EN TRAIN DE MARCHER, ET CELA SE VOIT SANS AMBIGUÏTÉ : une jambe est portée en avant, pied posé, l'autre est en arrière et son talon se "
             "décolle ; les bras balancent en opposition aux jambes, celui du côté de la jambe avancée partant en arrière. Son buste est légèrement penché dans "
             "le sens de la marche. Ce n'est pas une pose arrêtée : figée, la silhouette doit se lire comme quelqu'un qui avance, pas comme quelqu'un qui pose."),
}


@contextlib.contextmanager
def held(name: str, what: str):
    """Tient un verrou nommé le temps d'un bloc, ou refuse d'entrer.

    DEUX LANCEMENTS DU MÊME VARIANT NE PARTENT PAS ENSEMBLE (opérateur, 2026-08-12 : « tu dois avoir un lock entre des lancements concurrents de génération d'un
    même variant de sujet de sprite »). Le verrou de version, posé plus bas, empêche deux images d'écraser le même fichier ; il n'empêche pas de payer deux
    générations pour une seule demande. Celui-ci refuse la seconde et le dit.

    LE FICHIER SE CRÉE EN EXCLUSIF, comme la réservation de version : c'est la seule façon pour deux processus de ne pas croire tous les deux l'avoir pris. Il
    porte le numéro du processus et l'heure, parce qu'un verrou resté d'une commande morte doit pouvoir se comprendre et se retirer sans deviner.
    """
    folder = REPO / "var" / "locks"
    folder.mkdir(parents=True, exist_ok=True)
    lock = folder / f"{name}.lock"
    try:
        with open(lock, "x", encoding="utf-8") as held_by:
            held_by.write(f"{os.getpid()} {datetime.datetime.now().isoformat(timespec='seconds')}\n")
    except FileExistsError:
        raise SystemExit(f"FAULT {what} est déjà en cours : {lock.relative_to(REPO)} est tenu par « {lock.read_text(encoding='utf-8').strip()} ». "
                         f"Attendez la fin, ou retirez ce fichier si la commande qui le tenait est morte.")
    try:
        yield
    finally:
        # RENDU MÊME QUAND LA GÉNÉRATION CASSE : un verrou qu'un échec laisse en place bloque le variant pour toujours, et le prochain lancement croira qu'une
        # commande tourne encore.
        lock.unlink(missing_ok=True)


# THE SIX LEVELS A CONSIGNE IS WRITTEN FROM. Four are documented at doc/conception/referentiels/visuel/assets/ecriture-des-consignes.md; `parameters` is what
# a subject declares and the command reads back from the referential — its dimensions, its footprint, its pose point; `call` is what the launcher brings on
# the command line — a reference image, a rework motive. The distinction is not cosmetic: it says WHERE a wrong sentence gets fixed, and fixing at the wrong
# level costs one generation every time.
#
# A LEVEL SAYS WHERE THE CONSTRAINT COMES FROM, NEVER WHICH PIECE OF CODE BUILT THE STRING. The two part company more often than one would think: a sentence
# this command writes itself, but which holds for every subject alike, is `common` — it is not a parameter of anything. `parameters` was called `composed`
# until 2026-08-13, and that name stated the assembly mechanism instead of the nature of what is said; the project already had the word, and a document under
# it (doc/conception/referentiels/visuel/parametres-des-sujets.md).
#
# THEY ARE IDENTIFIERS, SO THEY ARE ENGLISH, AND EACH IS TAKEN FROM OUR OWN VOCABULARY RATHER THAN INVENTED. `common` is named after asset_common.py, which
# holds most of what is true of every image; `description` after assets/descriptions/, where what is true of one subject only is written. Both replace French
# words the glossary forbids by name: « variante » in the feminine, when the project says « un variant », and « fiche », which names indifferently a
# description, a subject's whole record, a variant's or a sprite's — one never knows which. The French prose that explains them stays French: one says « le
# `common`, ce socle partagé », never the reverse.
LEVEL_COMMON = "common"
LEVEL_TYPE = "type"
LEVEL_VARIANT = "variant"
LEVEL_DESCRIPTION = "description"
LEVEL_PARAMETERS = "parameters"
LEVEL_CALL = "call"
# WHICH TITLE EACH SOURCE OF EXTRA INSTRUCTION GETS, AND THE LEVEL THAT WROTE IT. The three used to arrive as one string already joined, under a single block
# that could only confess it mixed levels — and it is the block one reads FIRST when an image comes back wrong, so it was the worst possible place not to know
# where to correct. asset_common now names its three sources, and each becomes its own section.
EXTRA_SECTION_OF = {
    asset_common.EXTRA_FROM_TYPE: "Consigne du type",
    asset_common.EXTRA_FROM_INVENTORY: "Consigne de l'entrée d'inventaire",
    asset_common.EXTRA_FROM_SUBJECT: "Consigne du sujet",
}

# THE SECTIONS OF A CONSIGNE, IN THE ORDER THEY ARE WRITTEN, WITH THE LEVEL THAT WROTE EACH ONE — declared here, once. The template writes its titles from this
# table and the split reads them back from it, so a title and its level can never disagree: there is one vocabulary, not two.
#
# A GROUP TITLE NAMES A THEME, NEVER AN ORIGIN. The origin is the level, and the level lives on the leaves — a group may perfectly well hold sections of
# different levels, and two of them do. « Ce que dit sa description » was refused for the group below holding the orientation and the action: those are
# `variant`, and the title would have sent a hurried reader to correct them in assets/descriptions/, where they are not. That is exactly the cost this whole
# split exists to remove, reintroduced by a title.
#
# GROUPS DO NOT REORDER ANYTHING. Sections of one level are not contiguous — `common` opens the consigne, comes back for the cut-out and the rendering rules,
# and closes it with the camera reminder — so grouping by level would mean moving blocks, and the order carries meaning: what is read last weighs the most with
# this generator. A group is therefore a contiguous run of the consigne, and nothing ever moves.
SECTIONS = (
    # THE TWO SECTIONS ADDRESSED TO THE AGENT ARE `common`, ALTHOUGH THIS COMMAND WRITES THEM. How to read the consigne, and what to hand back afterwards,
    # hold for every image of the world alike and depend on no subject: they are not a parameter of anything. Their level says where the constraint comes from,
    # not which piece of code produced the string — and getting that backwards is what would send someone looking for them in a subject's own file.
    ("Comment travailler", (
        ("Comment lire cette consigne", LEVEL_COMMON),
        ("Ce que tu nous rapportes", LEVEL_COMMON),
    )),
    ("La sprite et son rendu", (
        ("Ce que tu produis", LEVEL_COMMON),
        ("Style", LEVEL_COMMON),
        ("Caméra", LEVEL_COMMON),
    )),
    ("Le sujet et ses mesures", (
        ("Le sujet à dessiner", LEVEL_PARAMETERS),
        ("Dimensions de l'image", LEVEL_PARAMETERS),
        ("Assise au sol et élévation", LEVEL_PARAMETERS),
    )),
    ("Le cadrage et l'assemblage", (
        ("Détourage", LEVEL_COMMON),
        ("Raccord entre cases", LEVEL_COMMON),
        ("Bords rejoints", LEVEL_VARIANT),
        ("Angle de la pièce", LEVEL_VARIANT),
        ("Composition de la pièce", LEVEL_VARIANT),
    )),
    # ALONE, BECAUSE WRAPPING ONE SECTION IN A GROUP OF ITS OWN ONLY ADDS A TITLE TO READ. A group earns its line when it gathers.
    (None, (("Image de référence", LEVEL_CALL),)),
    (None, (("Règles de rendu", LEVEL_COMMON),)),
    ("Ce qu'il est et ce qu'il fait", (
        ("Description du sujet", LEVEL_DESCRIPTION),
        ("Orientation", LEVEL_VARIANT),
        ("Action", LEVEL_VARIANT),
    )),
    ("Consignes supplémentaires", (
        # The shared opening sentence is the socle's — true of every image that carries any extra instruction — and each source that follows brings its own
        # level. Its own title says what it does rather than repeating its group's, which would have read as a near-duplicate.
        ("Comment elles s'ajoutent", LEVEL_COMMON),
        ("Consigne du type", LEVEL_TYPE),
        ("Consigne de l'entrée d'inventaire", LEVEL_DESCRIPTION),
        ("Consigne du sujet", LEVEL_DESCRIPTION),
    )),
    # THE LAST TWO ARE NOT GROUPED TOGETHER ALTHOUGH THEY ARE NEIGHBOURS AND AKIN. The only honest title would have been « ce qui prime en dernier » — and
    # telling the agent that the end weighs the most tells it that the rest weighs less.
    (None, (("Rappel de la caméra", LEVEL_COMMON),)),
    (None, (("Point prioritaire", LEVEL_CALL),)),
)
LEVEL_OF = {title: level for _, leaves in SECTIONS for title, level in leaves}
GROUP_OF = {title: group for group, leaves in SECTIONS for title, _ in leaves}
if len(LEVEL_OF) != sum(len(leaves) for _, leaves in SECTIONS):
    # A TITLE IS THE KEY THE SPLIT LOOKS UP, so two sections sharing one would make the second unattributable while looking perfectly fine in the consigne.
    raise SystemExit("FAULT deux sections de consigne portent le même titre — un titre est ce par quoi le découpage retrouve un bloc, il ne peut pas servir "
                     "deux fois. Solution : renomme l'une des deux dans SECTIONS, en tête de scripts/generate-sprite.py.")

# THE TWO MARKDOWN DEPTHS, WRITTEN ONCE: the assembler puts them in and the splitter takes them out, so a change of depth has to move both at the same time.
# A group heading carries no level and no parentheses — that is precisely what tells it apart from a section standing alone at the same depth.
GROUP_MARK = "## "
GROUPED_MARK = "### "
SECTION_PATTERN = re.compile(r"^(#{2,3}) (.+) \(([^()]+)\)$")
PARTS_FORMAT = "gatebeast-prompt-parts"

# THE SECTION THAT SAYS WHO THE STRUCTURE IS FOR, AND IT IS NOT THE IMAGE MODEL. The consigne is read by an AGENT, which rewrites it for its own image model,
# and instructions may be addressed to that agent alone — they never reach the model, so they cannot be drawn (ecriture-des-consignes.md, « À qui la consigne
# s'adresse »). That is what makes the levels writable in the titles at all: without this section, a title and a bracketed word are just more text that the
# rewriting may carry into the picture, which is how a consigne ends up producing an image with a caption on it. The addressing has to be EXPLICIT.
READING_FR = """\
CETTE SECTION S'ADRESSE À TOI, L'AGENT QUI LIT CETTE CONSIGNE, ET À TOI SEUL : elle ne fait pas partie de ce qu'il faut dessiner, et tu ne la transmets pas à
ton modèle d'images.
La consigne est découpée en sections, chacune ouverte par un titre. Une section porte son titre sous la forme « Titre (mot) », et le mot entre parenthèses
nomme l'endroit de NOTRE système d'où vient la section : il nous sert à savoir où porter une correction, et il ne décrit rien de l'image. Un titre SANS
parenthèses regroupe les sections qui suivent et dit seulement de quoi elles parlent ensemble.
Les titres et ces mots entre parenthèses sont donc de la structure, pas de la matière : ce qu'il faut dessiner est le CONTENU des sections, et lui seul.\
"""

# WHAT WE ASK THE AGENT TO HAND BACK, AND WHY IT IS WORTH ASKING. Between our consigne and the picture there is a rewriting nobody here sees: the agent
# reformulates our text for its own image model. When an image comes back wrong, three very different causes are indistinguishable today — our consigne
# prescribed badly, the rewriting dropped the clause, or the image model did not hold it — and each calls for the opposite fix. Three days went on the parallel
# projection, prescribed four times and absent from the image, without being able to tell which (opérateur, 2026-08-13).
#
# IT ASKS FOR THE TEXT, NOT AN ACCOUNT OF IT. An agent asked to show its work will readily answer « voici en substance ce que j'ai demandé », and an
# approximate trace is worse than none: it looks like evidence and analyses get built on it. Hence the markers, and hence saying in as many words that what is
# expected between them is the text itself.
#
# AND IT ASKS FOR A MESSAGE, NOT A FILE, BECAUSE THE WRAPPER FORBIDS FILES. scripts/generate-image.php tells the agent « Aucun autre fichier » — it must drop
# its PNG and nothing else, which is what keeps a generation from scattering things through the repository. So the text comes back through its own answer, and
# this command lifts it out of the generator's event log afterwards.
TRANSMITTED_START = "<<<CONSIGNE-TRANSMISE-DEBUT>>>"
TRANSMITTED_END = "<<<CONSIGNE-TRANSMISE-FIN>>>"
REPORTING_FR = f"""\
CETTE SECTION S'ADRESSE À TOI, L'AGENT QUI LIT CETTE CONSIGNE, ET NON À TON MODÈLE D'IMAGES : elle ne décrit rien de l'image et tu ne la lui transmets pas.
Quand tu as fini, ton dernier message se termine par la consigne EXACTE que tu as transmise à ton modèle d'images, encadrée par ces deux lignes, chacune seule
sur sa ligne :
{TRANSMITTED_START}
{TRANSMITTED_END}
Entre ces deux lignes, nous attendons le TEXTE LUI-MÊME, intégral et mot pour mot, tel que tu l'as envoyé — la chose, et non un compte rendu de la chose.
Si tu as envoyé plusieurs consignes successives, donne celle qui a produit l'image que tu enregistres.\
"""


class Outline:
    """Writes the titles of one consigne as it is assembled, opening each group above its first section that has something to say.

    IT HAS TO REMEMBER, WHICH IS WHY IT IS AN OBJECT AND NOT A FUNCTION. A group's title is written once, above the first of its sections that survives — and
    which one that is only becomes known while assembling: a variant with no gate writes no composition, a subject joining no edge writes no corner. Held in a
    module-level set instead, two consignes assembled in the same process would see the second lose all its group titles.

    A GROUP WHOSE SECTIONS ARE ALL EMPTY WRITES NOTHING AT ALL — no title standing over nothing, which the generator would read for no reason.
    """

    def __init__(self):
        self.opened = set()

    def heading(self, title: str) -> str:
        """The title lines that open one section: its group's, when it is the first to need it, then its own.

        A TITLE NAMES A NOTION AND NOTHING ELSE — no figure, no unit, no colon, no appended explanation.

        THE LEVEL IS WRITTEN HERE, IN THE OPEN, AND THAT ONLY BECAME SAFE ON 2026-08-13. The reader is an agent, not the image model, and a consigne may
        address that agent without a word of it reaching the model — so the structure it needs to read the document costs nothing in drawing risk, provided
        the addressing is stated, which READING_FR does. It is still recorded in the split file beside the consigne: two statements of the same fact that a
        command can compare catch a divergence neither would show alone.
        """
        if title not in LEVEL_OF:
            raise SystemExit(f"FAULT la section « {title} » n'est déclarée nulle part, donc le découpage ne saurait pas de quel niveau elle vient.\n"
                             f"  Solution — ajoute-la à SECTIONS, en tête de scripts/generate-sprite.py, à sa place dans l'ordre de la consigne, avec son "
                             f"niveau et dans son groupe.")
        group = GROUP_OF[title]
        if group is None:
            return f"{GROUP_MARK}{title} ({LEVEL_OF[title]})\n"
        opening = ""
        if group not in self.opened:
            self.opened.add(group)
            opening = f"{GROUP_MARK}{group}\n"

        return f"{opening}{GROUPED_MARK}{title} ({LEVEL_OF[title]})\n"

    def section(self, title: str, content: str) -> str:
        """One whole section — its title, then its content — or nothing at all when there is nothing to say.

        An empty section writes no title: a title standing over nothing is text the generator reads for no reason, and the split would carry a block with no
        content.
        """
        return f"{self.heading(title)}{content}" if content.strip() else ""

    def sections(self, pieces: list) -> str:
        """A run of sections built outside the template, joined exactly as their source joined them — one newline, and nothing else."""
        return "\n".join(self.section(title, content) for title, content in pieces)


def prompt_parts(prompt: str) -> list:
    """The assembled consigne cut back into its sections, each with the level that wrote it.

    IT CUTS ON THE TITLES THE CONSIGNE ALREADY CARRIES, and computes nothing else: a block runs from its own title to the next one's. The tiling is therefore
    exact by construction — no gap, no overlap, no arithmetic to get wrong — and the caller checks that total against the consigne's own length anyway.

    THE TILING IS FLAT, ON THE LEAVES, AND THE HIERARCHY IS A FIELD RATHER THAN A NESTING. A group's title line belongs to the section that follows it, so
    there is still ONE contiguous run of blocks and ONE sum to check. Tiling at two depths would need two sums and a rule saying who owns the group's title
    line: two more things to get wrong, for nothing gained — the guarantee is exactly as strong this way.

    OFFSETS AND LENGTHS ARE IN BYTES, not in characters, and that is deliberate: the consigne is written as UTF-8 and read back by a PHP command, where a
    string index is a byte. Character offsets would land mid-accent on the first « é » and point at the wrong place with no error at all.
    """
    starts, group, pending = [], None, None
    offset = 0
    for line in prompt.splitlines(keepends=True):
        found = SECTION_PATTERN.match(line.rstrip("\n"))
        if found:
            depth, title, said = found.group(1), found.group(2), found.group(3)
            # THE LEVEL IS STATED TWICE — in the title the generator reads, and in the split beside it — so the two can be compared. Reading it back here
            # rather than trusting the table is what turns the second statement into a control instead of a copy.
            if LEVEL_OF.get(title) != said:
                raise SystemExit(f"FAULT le titre « {title} » annonce le niveau « {said} » dans la consigne, et la table SECTIONS lui en donne un autre.\n"
                                 f"  Solution — un titre ne s'écrit jamais à la main dans le gabarit : passe-le par Outline.section(), qui prend son niveau "
                                 f"à SECTIONS.")
            grouped = depth == GROUPED_MARK.strip()
            if grouped and group is None:
                raise SystemExit(f"FAULT la sous-section « {title} » ne suit aucun titre de groupe, donc rien ne dit à quoi elle se rattache.\n"
                                 f"  Solution — déclare-la dans un groupe à SECTIONS, ou sors-la en section seule, qui s'écrit d'un cran moins profond.")
            if not grouped:
                if pending is not None:
                    raise SystemExit(f"FAULT le groupe « {group} » n'a aucune sous-section : « {title} » se présente à sa suite au même niveau que lui.\n"
                                     f"  Solution — un groupe rassemble, sinon il n'est qu'un titre de plus à lire ; déclare « {title} » en section seule.")
                group = None
            starts.append((pending if pending is not None else offset, title, said, group))
            pending = None
        elif line.startswith(GROUP_MARK):
            group, pending = line.rstrip("\n")[len(GROUP_MARK):], offset
        offset += len(line.encode("utf-8"))
    if not starts or starts[0][0] != 0:
        raise SystemExit("FAULT la consigne assemblée ne commence pas par un titre, donc son début n'appartiendrait à aucun bloc.\n"
                         "  Solution — la première section du gabarit de scripts/generate-sprite.py doit écrire son titre : vérifie que sa clause n'est pas "
                         "vide.")
    parts = []
    for index, (start, title, said, held) in enumerate(starts):
        stop = starts[index + 1][0] if index + 1 < len(starts) else offset
        parts.append({"level": said, "group": held, "title": title, "offset": start, "length": stop - start})

    return parts


def transmitted_prompt(log: Path) -> str:
    """The consigne the agent says it handed to its own image model, lifted out of its event log — or None when it reported none.

    IT LOOKS ONLY AT WHAT THE AGENT SAID, never at the whole log. The log also carries our own consigne, which contains the markers themselves inside the
    clause that asks for them: scanning the file as one text would find those and hand back our own words as if they were the agent's answer — a trace that
    looks like evidence and is a mirror. So only `agent_message` items are read, and the LAST one carrying both markers wins, an agent being free to speak
    several times before it is done.

    ABSENCE IS A RESULT, NOT A FAULT. An agent that did not answer as asked has produced an image all the same, and losing that image over a missing trace
    would be absurd. It returns None, and the caller says so out loud rather than writing an empty file that would read as an empty rewriting.
    """
    if not log.is_file():
        return None
    said = None
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            # A truncated last line is what a killed generation leaves behind; it says nothing about the lines before it, which are whole.
            continue
        message = event.get("msg") or event
        item = message.get("item") or {}
        if message.get("type") != "item.completed" or item.get("item_type") != "agent_message":
            continue
        text = item.get("text") or ""
        if TRANSMITTED_START in text and TRANSMITTED_END in text:
            said = text.split(TRANSMITTED_START, 1)[1].rsplit(TRANSMITTED_END, 1)[0].strip("\n")

    return said


def write_prompt_parts(written: Path, prompt: str) -> Path:
    """Write the split beside the consigne it describes, and return where it went.

    IT NEVER TOUCHES THE CONSIGNE ITSELF. The frozen consigne is the exact trace of what was sent to the generator; a marker inserted into it would make it
    diverge from what was really received, and that trace is the only thing it guarantees. The split therefore lives in the neighbouring file — and beside it,
    never under var/, because the two are useless apart and a trace that only exists on one machine is a trace already half lost.

    THE FINGERPRINT IS WHAT KEEPS IT FROM LYING. Offsets alone go stale in silence the day the consigne is reassembled; tied to the fingerprint of this exact
    text, a stale split is REFUSED by its reader instead of attributing sentences to the wrong level.
    """
    parts = prompt_parts(prompt)
    body = prompt.encode("utf-8")
    covered = sum(part["length"] for part in parts)
    if covered != len(body):
        raise SystemExit(f"FAULT le découpage ne recouvre pas toute la consigne : {covered} octets pavés pour {len(body)}.\n"
                         f"  Solution — un morceau de texte du gabarit se trouve hors de toute section ; place-le sous un titre déclaré à SECTIONS.")
    beside = written.with_name(written.stem + ".parts.json")
    beside.write_text(json.dumps({
        "format": PARTS_FORMAT, "version": 1, "prompt": written.name, "length": len(body),
        "fingerprint": "sha256:" + hashlib.sha256(body).hexdigest(), "parts": parts,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return beside


# THE SPRITES REVIEW PAGE'S ROUTE, WRITTEN ONCE. It has already changed once — `review-server/suivi-sprites/build.php` was the older form — and an address
# copied into two commands would only ever have been caught up in one of them.
REVIEW_PAGE_ROUTE = "/sprites"
REPUBLISH_COMMAND = ("php", "review-server/build.php", REVIEW_PAGE_ROUTE)


def republish_review_page() -> bool:
    """Rebuild the sprites review page; return False, naming the command that repairs it, when the rebuild fails.

    EVERY WRITE THAT CHANGES WHAT THE PAGE SHOWS REPUBLISHES IT, or nobody can judge on what is displayed. The repository rule names the two together, in one
    sentence: every sprite produced is recorded under its subject AND the review artefact is republished, without exception. The mechanism used to live in
    `scripts/sprite-queue.py`, a production queue that died when its two generators merged into this command; the republication fell with it, silently, and
    three sprites produced on 2026-08-12 appeared nowhere. Hung on a queue that can be removed, it disappears with that queue — its place is in the command
    that produces, the very one that already records into the referential.

    THE LOCK IS TAKEN BLOCKING, WHICH IS THE OPPOSITE OF `held()`. That one refuses the second taker, as a generation needs, where a second launch is a doubled
    cost. Here two images produced together must BOTH end up on the page: each waits its turn and rebuilds. The production queue already serialized this one
    step with a thread lock; this one holds between processes, since every command is now its own.

    A FAILURE DOES NOT RAISE: the image is produced and recorded, that much is acquired, and losing it because a page could not be rebuilt would cost a
    generation. The failure is reported to the launcher in its own output, with the command that repairs it.
    """
    folder = REPO / "var" / "locks"
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / "review-page.lock", "w", encoding="utf-8") as turn:
        fcntl.flock(turn, fcntl.LOCK_EX)
        try:
            built = subprocess.run(list(REPUBLISH_COMMAND), cwd=REPO, capture_output=True, text=True)
        finally:
            fcntl.flock(turn, fcntl.LOCK_UN)
    if built.returncode:
        # The LAST non-blank line of the output: that is the one naming what broke, and dumping the whole build would drown the remedy in the middle of it.
        said = [line.strip() for line in ((built.stderr or "") + "\n" + (built.stdout or "")).splitlines() if line.strip()]
        print(f"FAULT la republication de la page de revue a échoué (code {built.returncode}) : {said[-1] if said else 'aucune sortie'}\n"
              f"  Solution — l'image est produite et inscrite, rien n'est perdu ; refais la page à la main : {' '.join(REPUBLISH_COMMAND)}", flush=True)
        return False
    print(f"page de revue republiée : {REVIEW_PAGE_ROUTE}")

    return True


def frozen_reference(code: str, variant_ref: str = None):
    """The subject's FROZEN reference — the one image a generation may look at — or None when none has been frozen yet.

    A REFERENCE IS FIXED, AND IT NEVER FOLLOWS THE LATEST VERSION (opérateur, 2026-08-12 : « faut arrêter de prendre les images précédentes en référence […] tu
    peux avoir une image de référence mais elle ne change jamais. Sinon si tu changes et le prompt et l'image, tu perds tout »). This used to return the CURRENT
    deliverable, so every rework handed the generator both a new consigne and a new model at once: no change could be attributed to either, and a defect carried
    by the image survived every correction written into the text — what the generator SEES weighs more than what it reads. The oak came back as an elevation
    three times for exactly that reason, each time modelled on the elevation before it.

    So the reference is DECLARED, under the key `reference`, on the variant first and on the subject otherwise, and it is frozen the day a version is judged
    good. Until one is judged, a subject has NO reference and its consigne stands alone — which is the only way the consigne can be measured at all.
    """
    data = json.loads((REPO / "assets" / "subjects.json").read_text(encoding="utf-8"))
    subject = data.get("subjects", {}).get(code)
    if not subject:
        return None
    # LE VARIANT LUI-MÊME D'ABORD, ET C'EST UNE FAUTE PAYÉE : la référence dit de reprendre la matière et la couleur À L'IDENTIQUE, donc donner à un variant qui a
    # sa propre palette la référence d'un autre efface exactement ce qui le distingue. Constaté sur la proposition 2 du centre de soin, dont les couleurs de la
    # scène de référence ont été remplacées par celles de la vue principale (opérateur, 2026-08-07). Le variant déclare donc la sienne quand il en a une, et ne
    # retombe sur celle du sujet que lorsqu'il n'en déclare aucune.
    for variant in subject.get("variants", []):
        if variant.get("ref") == variant_ref and variant.get("reference"):
            declared = variant["reference"]
            break
    else:
        declared = subject.get("reference")
    if not declared:
        return None
    # UNE RÉFÉRENCE DÉCLARÉE QUI N'EST PAS LÀ EST UNE FAUTE, PAS UNE ABSENCE. Rendre None ferait repartir la génération sans modèle en silence, alors que quelqu'un
    # a précisément décidé qu'elle en avait un : c'est l'erreur transparente que ce dépôt paie le plus cher.
    path = REPO / "assets" / declared
    if not path.is_file():
        raise SystemExit(f"FAULT la référence figée de {code} est déclarée à « {declared} », et ce fichier n'existe pas.")

    return path


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
    # LE VERROU SE PREND AVANT TOUT LE RESTE QUAND ON GÉNÈRE, et il tient jusqu'à la fin de la commande : c'est la seule place où il empêche vraiment la dépense.
    # Pris plus tard, la seconde commande aurait déjà assemblé sa consigne et réservé un numéro — donc laissé une consigne figée sans image à côté.
    with contextlib.ExitStack() as bench:
        if generate:
            bench.enter_context(held(f"{code}_{variant_ref}", f"une génération de {code} / {variant_ref}"))

        return draw(code, variant_ref, reference, generate, plate, model, rework)


def draw(code: str, variant_ref: str, reference: Path, generate: bool, plate: Path = None,
         model: str = None, rework: str = None) -> int:
    """Le corps de la commande, tenu sous le verrou par `build()` — jamais appelé directement."""
    posts, gate = None, None
    if generate and not (reference or plate):
        frozen = frozen_reference(code, variant_ref)
        if frozen is not None:
            reference = frozen
            print(f"référence figée : {frozen.relative_to(REPO)} — déclarée au référentiel, elle ne suit jamais la dernière version")
        else:
            print(f"aucune référence figée pour {code} : la consigne dessine seule, et c'est ce qui rend son effet mesurable")
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
    # READ, NEVER COMPUTED (operator, 2026-08-10). The two figures are the variant's own judgement of how tall this drawing must come back, in tiles; a variant
    # that does not carry them stops the command rather than falling back on anything.
    floor, ceiling = tile_scale.variant_band(spread["columns"], spread["rows"], declared, f"{code} / {variant_ref}")
    # THE FIGURES ARE SAID EXACTLY AS THE VARIANT DECLARES THEM, AND NOTHING ROUNDS THEM ANY MORE. They used to be a pixel band converted back into tiles, so the
    # conversion had to round the floor UP and the ceiling DOWN to stay stricter than the band — a ceiling of 92 px read as « 1,0 case » had authorised exactly
    # what the checker refuses, and eight flat pieces came back square. Now the tiles ARE the declaration and the pixels are derived from them, so rounding can
    # only lie. It also inverted the band whenever floor and ceiling met: a path piece declared at 0,875 came out « ENTRE 0,9 ET 0,8 », which asks for nothing.
    low = f"{declared['height_min_ty']}".replace(".", ",")
    high = f"{declared['height_max_ty']}".replace(".", ",")
    band_px = f"{round(floor)} à {round(ceiling)} pixels"
    # WHERE THE SUBJECT SETS DOWN, IN PIXELS, AND IT IS A PARAMETER RATHER THAN A HABIT (opérateur, 2026-08-12 : « le milieu de la base d'un arbre doit être dans
    # le milieu de son emprise, sinon tu ne pourras rien ajouter devant », puis « certains sprites ne seront pas centrés au milieu de leur emprise mais le sujet
    # et le variant doivent pouvoir réécrire ça »). It resolves level by level, exactly like the passage does: the variant wins over the subject, the subject over
    # the default — the middle of the bottom edge of the footprint, which the catalogue already calls the pose point.
    # SAID IN PIXELS BECAUSE AN APPROXIMATION PRODUCES AN APPROXIMATION: « centré » was read as « à peu près au milieu », and a foot two tiles off centre makes
    # the tile in front of it unusable. The height is a band, so only the horizontal position can be a figure; the vertical one is the ground line itself.
    anchor = declared.get("anchor") or subject.get("anchor") or {"x": 0.5}
    pose_x = round(anchor["x"] * master["width"])
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
    # SINCE THE TILE IS WORTH 1 IN BOTH DIRECTIONS, THE FORESHORTENING IS NO LONGER SAID IN TILES — it lives in what a tile is worth in pixels, stated once above.
    # This clause used to announce a depth of « 1,75 case » for two rows, which contradicted the height band in the very same consigne: the band counted tiles of
    # width, the clause counted tiles of depth, and the generator was handed two units under one name. In tiles, a rectangle two rows deep is two tiles deep.
    # « VU DE HAUT » ÉTAIT AMBIGU, ET L'AMBIGUÏTÉ SE PAYAIT EN PERSPECTIVE (opérateur, 2026-08-13 : « sors de vrais termes techniques, il comprend », et « on doit
    # éviter de lui dire ce qu'il ne faut pas faire, il faut être plus précis dans ce qu'on lui dit qu'il faut faire »). Un sol « vu de haut » sous une façade
    # demandée de front ne se concilie que par un point de fuite : le générateur recevait deux ordres inconciliables et tranchait en dessinant une perspective.
    # ET LA CLAUSE A FINI PAR DISPARAÎTRE ENTIÈREMENT, LE 2026-08-13. Réécrite comme une projection, elle disait mot pour mot ce que la clause de caméra dit déjà
    # d'une face horizontale — largeur conservée, profondeur mise à l'échelle. Le même paramètre à deux niveaux, et le plus proche du sujet l'emporte sur le
    # socle : c'est la configuration que le référentiel d'écriture désigne comme la plus dangereuse, et celle qui a coûté trois jours sur la caméra. Ce qui
    # reste ici est la seule chose que le socle ne peut pas savoir : COMBIEN de cases ce sujet-ci occupe au sol.
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
        # IT SPEAKS OF THE NEIGHBOUR, NOT OF THE EDGE. « Il ne rejoint aucun bord » said the opposite of a sheet ordering a building to fill its footprint « jusqu'à
        # ses deux bords » — the same word, twenty lines apart, for two different things. A fence or another building may be laid AGAINST this subject on the map,
        # which is the renderer's business and never the generator's (opérateur, 2026-08-12).
        join_clause = ("CE SUJET NE S'ASSEMBLE AVEC AUCUN VOISIN : sa matière ne se prolonge dans aucune case voisine, ne se raccorde à rien et ne fusionne avec "
                       "rien. Il se dessine ENTIER, ses quatre côtés compris, et occupe toute l'emprise annoncée jusqu'à ses limites.")

    # LA CLAUSE D'ORIENTATION NE VAUT QUE POUR CE QUI TOURNE, et le modèle le dit tout seul : un type dont le lot déclare plusieurs orientations a des sujets qui
    # se présentent autrement selon la vue — un personnage, une créature —, tandis qu'un chemin, un arbre ou une clôture n'en déclarent qu'une et ne tournent pas.
    # Le critère se lit donc au type, il ne s'écrit pas en liste ici : une liste de types serait fausse au premier type qui tourne et qu'on aurait oublié d'y mettre.
    orientation_clause = ""
    turning = {view.get("orientation") for view in type_.get("batch_v0", []) if view.get("orientation")}
    if len(turning) > 1:
        # PRISE AU VARIANT DÉCLARÉ, PAS DANS `asked` : celui-ci ne garde que les champs dont le type déclare une collection de valeurs — composition, portillon,
        # densité —, et l'orientation n'en est pas une : c'est un axe que tout variant porte, au même titre que son action.
        facing = declared.get("orientation")
        if facing not in ORIENTATION_TEXT:
            raise SystemExit(f"FAULT {code} tourne, et l'orientation demandée est {facing!r} — aucune clause n'existe pour elle, et une vue sans clause "
                             f"reprendrait celle du sud sans le dire. Orientations connues : {', '.join(sorted(ORIENTATION_TEXT))}.")
        orientation_clause = f"CE QU'ON VOIT DE LUI : {ORIENTATION_TEXT[facing]}"

    # CE QU'IL FAIT SE DIT AUSSI, ET IL NE SE DISAIT NULLE PART. The action is declared on every variant and was carried by no clause: asked for a walking human,
    # the assembled prompt spoke only of an orientation, so it would have drawn a standing one. Refused rather than guessed — an unknown action would silently
    # produce the resting pose under another name, which is the transparent fault this repository forbids.
    doing = declared.get("action", "idle")
    action_clause = ""
    if doing != "idle":
        if doing not in ACTION_TEXT:
            raise SystemExit(f"FAULT {code} demande l'action {doing!r}, et aucune clause n'existe pour elle — sans clause, l'image reviendrait au repos sans le "
                             f"dire. Actions connues : repos, {', '.join(sorted(ACTION_TEXT))}.")
        action_clause = f"CE QU'IL FAIT : {ACTION_TEXT[doing]}"

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

    # THE REFERENCE OFTEN SHOWS ANOTHER VIEW OF THE SUBJECT, AND THE CONSIGNE MUST SAY SO — this is the fault the operator named on 2026-08-12: « ce n'est pas
    # normal qu'un seul variant ait un souci, ça veut probablement dire que l'arbo de consigne est mal montée ». The reference clause below claims the reference
    # is authoritative for « la FORME PROPRE du sujet — son plan, ses proportions, ses ÉLÉMENTS ET LEUR PLACE », while the orientation clause further down asks
    # for another view of it. For every variant that keeps the reference's own view the two agree and nothing shows; for the east and north views they order
    # opposite things, and the generator settles it by copying the reference — a mirrored creature and a squashed human, both on 2026-08-12.
    # WHAT THE REFERENCE SHOWS IS READ FROM THE REFERENTIAL, NEVER GUESSED: its path is that of a representation, and the representation belongs to a variant
    # that declares its orientation. Unknown path means unknown view, and the clause then says only that the direction is never taken from it.
    reference_view = None
    if reference:
        wanted = reference.resolve().as_posix()
        for variant in subject.get("variants", []):
            for shown in variant.get("representations", []):
                if wanted.endswith(str(shown.get("path", "")).lstrip("/")):
                    reference_view = variant.get("orientation")
    view_clause = ""
    if reference and len(turning) > 1 and reference_view != declared.get("orientation"):
        seen = ORIENTATION_TEXT.get(reference_view)
        view_clause = (
            "\nATTENTION — CETTE RÉFÉRENCE NE MONTRE PAS LA VUE QU'ON TE DEMANDE"
            + (f", ELLE MONTRE UNE AUTRE ORIENTATION DU MÊME SUJET : {seen}" if seen else ", et l'orientation qu'elle montre n'est pas celle demandée.")
            + "\nTU N'EN REPRENDS DONC NI LA DIRECTION, NI LA POSE, NI LA PLACE DE SES PARTIES DANS L'IMAGE : la vue demandée est celle, et seulement celle, que "
              "dit la clause « CE QU'ON VOIT DE LUI » plus bas. De la référence tu reprends ce qui ne dépend pas du point de vue — la matière, les couleurs, la "
              "lumière, le niveau de détail, la silhouette générale et les PROPORTIONS, qui elles ne changent pas d'une vue à l'autre.\n"
            "ET TU NE COMPRIMES RIEN : une vue de profil n'est pas une vue de face rétrécie en largeur. C'est le même sujet, à la même hauteur et aux mêmes "
            "proportions, vu de son côté.\n")
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
{view_clause}"""
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
    # AND IT SPEAKS OF NO PAST, BECAUSE THE GENERATOR HAS NONE (opérateur, 2026-08-12 : « l'agent IA n'a aucune connaissance de l'historique, on ne doit PAS lui en
    # parler »). It used to open with « la version précédente a été rejetée » — a sentence about an image this generator never saw, in a session that never
    # happened for it. What is left is what a retry actually is: the point that matters most, said positively, and placed last because what is read last weighs
    # the most. The motive text itself must be written the same way, prescriptive and not narrative.
    rework_clause = ""
    if rework:
        rework_clause = (
            "\nCE POINT EST LE PLUS IMPORTANT DE TOUTE LA CONSIGNE, ET IL PRIME SUR TOUT LE RESTE :\n"
            f"{rework}\n"
        )

    # SORTI DU GABARIT POUR TENIR LA LARGEUR DU DÉPÔT, ET SEULEMENT POUR ÇA : le texte de la clause ne se replie jamais — il part tel quel au générateur, et un
    # retour à la ligne ajouté ici serait un retour à la ligne de plus dans la consigne. Son TITRE, lui, reste écrit dans le gabarit : l'ordre dans lequel les
    # titres sont demandés est celui qui décide au-dessus de quelle section s'ouvre un groupe, et le sortir d'ici ouvrirait le sien un cran trop tôt.
    dimensions_text = f"""\
DIMENSIONS ATTENDUES, ET ELLES SONT CONTRACTUELLES : l'image fait EXACTEMENT {spread['columns']} TX de large, et sa hauteur tient ENTRE {low} ET {high} TY,
soit {band_px} — et c'est le chiffre en pixels qui fait foi, jamais la fraction de case.
Cette fourchette n'est pas indicative : en dessous, le sujet est écrasé dans son emprise et ne se dresse plus ; au-dessus, il écrase tout ce qui l'entoure. Elle a été
décidée pour CE sujet dans CETTE posture, et pour aucun autre : une image hors de ces deux nombres est refusée."""

    ground_text = f"""\
CE QUI TOUCHE LE SOL ET CE QUI S'ÉLÈVE, ET C'EST LA CHOSE LA PLUS SOUVENT MANQUÉE. Le sujet POSE AU SOL un rectangle de {subject['footprint']['columns']} TX de large sur
{subject['footprint']['rows']} TY de profondeur.
Il occupe le BAS de l'image, et sa dernière rangée tolère un léger débord pour que la matière se raccorde à ce qui l'entoure.
TOUT CE QUE LE SUJET DRESSE — murs, toit, tronc, feuillage — MONTE AU-DESSUS de ce rectangle et occupe le reste de la hauteur de l'image. Un sujet
entièrement contenu dans son rectangle au sol, sans rien qui s'élève par-dessus, est refusé : c'est un sujet écrasé, pas un sujet vu sous cette caméra.
LE POINT DE POSE EST UNE MESURE, PAS UNE IMPRESSION : le MILIEU DE LA BASE du sujet — le pied du tronc, le seuil du bâtiment, le centre de la touffe — tombe à
EXACTEMENT {pose_x} PIXELS du bord gauche de l'image, et repose sur le bord BAS de l'image. Décalé, le sujet empêche de poser quoi que ce soit devant lui sur la
carte."""

    # THE EXTRA INSTRUCTIONS, SOURCE BY SOURCE, AND THE TEXT COMES OUT IDENTICAL. asset_common joins its header and its values with a single newline; the same
    # newline joins the sections here, so inserting the titles is the only difference. Their PIECES are prepared here and their titles written from the
    # template, for the same reason as above: a group opens above the first section that asks for it, so the asking must happen in the consigne's own order.
    extra_pieces = [("Comment elles s'ajoutent", asset_common.EXTRA_HEADER)] if extras else []
    extra_pieces += [(EXTRA_SECTION_OF[source], text) for source, text in extras.items()]

    outline = Outline()
    prompt = f"""{outline.section("Comment lire cette consigne", READING_FR)}

{outline.section("Ce que tu nous rapportes", REPORTING_FR)}

{outline.section("Ce que tu produis", asset_common.CONTEXTE_FR)}

{outline.section("Style", plate_common.STYLE_FR)}

{outline.section("Caméra", asset_common.CAMERA_FR)}

{outline.heading("Le sujet à dessiner")}ASSET DE JEU — {label}, SEUL SUJET DE L'IMAGE, destiné à être posé comme sprite sur une carte vue de
dessus.

{outline.section("Dimensions de l'image", dimensions_text)}

{outline.section("Assise au sol et élévation", ground_text)}

{outline.section("Détourage", asset_common.CADRAGE_TRACE if joins_edges else asset_common.CADRAGE_CUTOUT)}

{outline.section("Raccord entre cases", asset_common.TRACE_FR if joins_edges else "")}

{outline.section("Bords rejoints", join_clause)}
{outline.section("Angle de la pièce", turn_clause)}
{outline.section("Composition de la pièce", composition_clause)}
{outline.section("Image de référence", clause)}
{outline.section("Règles de rendu", asset_common.REGLES_FR)}

{outline.heading("Description du sujet")}LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :
{code} : {description}
{outline.section("Orientation", orientation_clause)}
{outline.section("Action", action_clause)}

{outline.sections(extra_pieces)}

{outline.section("Rappel de la caméra", asset_common.RAPPEL_CAMERA_FR)}
{outline.section("Point prioritaire", rework_clause)}"""

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
    # THE SPLIT FOLLOWS THE DRAFT TOO, and that is where it earns most of its keep: reading a consigne before spending a generation is exactly when one asks
    # « quel niveau a écrit cette phrase », and the answer decides where the fix goes.
    write_prompt_parts(draft, prompt)
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
    #
    # LE NUMÉRO SE RÉSERVE DANS LE MÊME GESTE QU'IL SE TROUVE, ET C'EST UNE FAUTE PAYÉE LE 2026-08-12. Le code cherchait le premier numéro libre, PUIS écrivait
    # dessus : entre les deux, rien ne tenait le nom. Six générations lancées ensemble sur deux sujets ont toutes trouvé le même numéro libre — trois ont écrit
    # dans HU-000-v3, trois dans SP-001-v2 —, quatre images ont été écrasées avec leur consigne figée, et le référentiel s'est retrouvé avec trois variantes
    # déclarant le même dessin. Rien n'avait levé.
    #
    # `x` CRÉE LE FICHIER OU ÉCHOUE, sans intervalle possible : c'est la seule façon pour deux processus de ne pas croire tous les deux avoir le numéro. Le
    # fichier réservé est la CONSIGNE, écrite ici de toute façon — réserver l'image aurait laissé un PNG vide que le générateur aurait ensuite écrasé, et un
    # fichier vide sur le disque est exactement ce qu'un contrôle prendrait pour une image produite.
    version, image = 1, target / f"{name}.png"
    while True:
        # L'IMAGE EXISTANTE GARDE SA PLACE, MÊME SANS SA CONSIGNE À CÔTÉ : les toutes premières pièces ont été produites avant que la consigne ne se fige, et
        # se fier à la seule réservation les écraserait. Les deux conditions se cumulent, elles ne se remplacent pas.
        if image.exists():
            version += 1
            image = target / f"{name}-v{version}.png"
            continue
        try:
            with open(image.with_suffix('.txt'), 'x', encoding='utf-8') as frozen:
                frozen.write(prompt)
            break
        except FileExistsError:
            version += 1
            image = target / f"{name}-v{version}.png"

    print(f"consigne figée : {image.with_suffix('.txt').relative_to(REPO)}")
    # THE SPLIT IS FROZEN WITH THE CONSIGNE, AND AS SOON AS IT IS: the two are only useful together, and the reserved name is what tells them apart from the
    # next version's pair. Written after the reservation, so it can never claim a consigne another process took.
    print(f"découpage figé : {write_prompt_parts(image.with_suffix('.txt'), prompt).relative_to(REPO)}")
    # REBUILDING THE REVIEW PAGE BELONGS TO THIS COMMAND NOW, NOT TO A QUEUE. It lived in `scripts/sprite-queue.py`, which held the ordering between two
    # concurrent generations; that queue died when the two generators merged, and the republication fell with it. The ordering is now held by the lock inside
    # `republish_review_page()`. The export and the report have always belonged here — they concern this image and nothing else.
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
        # THE THIRD FILE OF THE TRIO, AND IT TRAVELS WITH THE OTHER TWO: the consigne we sent, its split, and the consigne the agent says it passed on. Apart,
        # none of them answers the only question that matters when an image is wrong — where, between our text and the picture, the clause was lost.
        # OUTSIDE THE STEP, BECAUSE IT MUST NOT FAIL THE RUN. A missing trace loses a comparison; raising here would lose the image itself.
        transmitted = transmitted_prompt(run.traces / f"{image.stem}-generateur.jsonl")
        if transmitted:
            beside = image.with_name(f"{image.stem}.transmitted.txt")
            beside.write_text(transmitted + "\n", encoding="utf-8")
            print(f"consigne transmise recueillie : {beside.relative_to(REPO)}")
        else:
            # NO EMPTY FILE, EVER. One would read as an empty rewriting — a fact — where the truth is that we do not know what was passed on.
            print("SANS CONSIGNE TRANSMISE — l'agent n'a pas rapporté ce qu'il a passé à son modèle d'images, donc rien n'est écrit à côté de l'image.\n"
                  f"  Solution — la réponse complète de l'agent reste dans « {(run.traces / f'{image.stem}-generateur.jsonl').relative_to(REPO)} » : "
                  f"cherches-y « {TRANSMITTED_START} ». Si elle n'y est pas non plus, il n'a pas suivi la demande et c'est la clause « Ce que tu nous "
                  f"rapportes » qu'il faut revoir.", flush=True)
        with run.step("redimensionnement"):
            # The delivery resize belongs to the run, and so does its own account of itself: the
            # sizes, the measured silhouette and the pose point it computes are exactly what the
            # final report has to carry (operator, 2026-08-05). Captured rather than left on the
            # terminal, or it would be lost the moment the run ends.
            exported = subprocess.run(
                # The variant ref travels with the file: the height band lives on the variant, and the file name alone never says which variant it is.
                ["python3", str(REPO / "scripts" / "export-asset.py"), str(image), "--variant", variant_ref],
                cwd=REPO.parent, capture_output=True, text=True)
            print(exported.stdout, end="", flush=True)
            extras["Redimensionnement à la définition de livraison"] = (
                "```\n" + (exported.stdout or exported.stderr or "aucune sortie").strip() + "\n```")
            if exported.returncode:
                raise SystemExit(f"FAULT le redimensionnement de {name} a échoué.")
        with run.step("inscription"), held("subjects", "une inscription au référentiel"):
            # LE RÉFÉRENTIEL EST UN FICHIER UNIQUE, DONC L'INSCRIPTION SE FAIT À UN SEUL À LA FOIS. Le verrou du variant ne protège que les lancements du MÊME
            # variant ; deux sujets différents produits ensemble se retrouvaient à réécrire le même fichier, et le 2026-08-12 il en a perdu des inscriptions.
            # Le verrou est pris ici, au plus tard et pour le temps le plus court : une génération dure deux minutes, son inscription un centième de seconde.
            # Chained here, never left to whoever remembers: the rule is that every sprite produced is recorded under its variant, without exception. A
            # sprite was produced and forgotten the day this was a separate command someone had to think of running.
            # THE SESSION TRAVELS TO THE REFERENTIAL, AND NOT ONLY TO THE REPORT (operator, 2026-08-13: « il faut que l'id de la session soit dans la version du
            # variant »). It was captured just above, from the generator's own output, and written into var/generations/ alone — a folder that is not
            # versioned, so the id lived on this machine only and vanished with the next cleanup. Passed here, it is recorded on the version itself. Omitted
            # when the generator reported none: record-asset.py then writes `null`, which says exactly that, and the report keeps saying it too.
            session_option = ["--session", run.session] if run.session else []
            recorded = subprocess.run(
                ["python3", str(REPO / "scripts" / "record-asset.py"), str(image),
                 "--code", code, "--type", subject["type"], "--variant", variant_ref, *session_option],
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

    # AFTER THE RECORDING, AND OUTSIDE THE REPORT'S STEPS. Outside the `try`, because a generation that broke has nothing new to show: the page is only rebuilt
    # once an image really made it into the referential. Outside `run.step`, because a step reads "faite" as long as it does not raise, and this one never
    # raises — the report would then claim a successful republication over a failed one, which is exactly the transparent fault this repository pays for most.
    republish_review_page()

    return 0


if __name__ == "__main__":
    # ASKED BEFORE ANYTHING ELSE: every other path through this block can spend a generation. Here and not at module level — this file is imported by name
    # elsewhere, and a guard on the import path would stop its caller the moment that caller is itself run with --help.
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        raise SystemExit(0)
    argv = sys.argv[1:]
    if len(argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    reference = Path(argv[argv.index("--ref") + 1]).resolve() if "--ref" in argv else None
    plate_value = Path(argv[argv.index("--plate") + 1]).resolve() if "--plate" in argv else None
    chosen = argv[argv.index("--model") + 1] if "--model" in argv else None
    rework = argv[argv.index("--rework") + 1] if "--rework" in argv else None
    # LE MOTIF PEUT VENIR D'UN FICHIER, ET C'EST LA FORME À PRÉFÉRER. Un motif de rejet cite l'opérateur, donc il porte ses guillemets, ses tirets et ses
    # parenthèses — et une garde de shell refuse la commande sur ces caractères-là, au milieu du travail. Le fichier fait passer le texte sans que la ligne de
    # commande ait à le porter. Refusé plutôt que deviné : un « @ » qui ne désigne aucun fichier est une faute de frappe, pas un motif.
    if rework and rework.startswith("@"):
        motive = Path(rework[1:])
        if not motive.is_file():
            raise SystemExit(f"FAULT le motif de reprise devait se lire dans « {motive} », qui n'existe pas.")
        rework = motive.read_text(encoding="utf-8").strip()
    raise SystemExit(build(argv[0], argv[1], reference, "--generate" in argv, plate_value, chosen, rework))
