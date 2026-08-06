#!/usr/bin/env python3
"""Build the sprite tracking page: every type, every profile, every expected variant, with its state.

The inventory below is a design decision handed down by the owner's coordinator and is reproduced as
given — codes, names and footprints are not invented and not corrected here.

Variant refs follow the model in sujets-et-variantes.md: orientation and action are always
written, a direction only when it leaves its default, then the frame.

FRENCH TEXT NEVER ENTERS THE SCRIPT BY CONCATENATION. Every string the page's behaviour needs — status
words, action labels, recap headings — is carried in one JSON block and read from it at runtime. The
JavaScript below contains no French literal at all, so an apostrophe can never terminate a string and
silently break the page. Text is written into the document with textContent, never with innerHTML.

Generates no image: it embeds thumbnails already built from files that exist.
Run from the workspace root: python3 gatebeast/local/build-review-page.py
"""
import base64
import html
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1] / "scripts"
ASSETS = HERE.parents[1] / "assets"
# The tile scale is a service, not a number to retype. The page shows what it says.
sys.path.insert(0, str(SCRIPTS))
import tile_scale
# check-sujets.py is hyphenated, so it is loaded by path rather than imported by name — the same
# mechanism the production tools use for it. It holds how many earlier versions this page shows.
_spec = importlib.util.spec_from_file_location("check_sujets", SCRIPTS / "check-sujets.py")
check_sujets = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_sujets)
THUMBNAILS = json.loads((SCRIPTS / "thumbnails.json").read_text(encoding="utf-8"))
# Entries built by an earlier run of scripts/build-thumbnails.py hold their image at full definition.
# They are dropped here rather than trusted: every image this page shows is now read from disk and
# reduced to screen size on the way in (master_entry, shrink_to_screen), which is what keeps the page
# small enough for the browser to apply its own declarations at all.
THUMBNAILS = {}
OUT = HERE / "page.html"

JUDGEMENTS_PATH = ASSETS / "jugements.json"

# Les critères mesurés, nommés pour l'opérateur : l'outil de mesure les nomme en anglais parce qu'il est du code, la page se lit.
CRITERIA_FR = {"transparency": "Fond transparent", "footprint": "Emprise au sol", "light": "Lumière dans la bande",
               "tiling": "Raccord bord à bord", "regularity": "Régularité de la matière"}


def load_judgements():
    """Every judgement, keyed by the same path scheme this page addresses images with.

    A judging agent may not have run yet, or may run again later with a fresh file: its absence is not
    an error, and its content is never assumed — a malformed file is treated the same as a missing one
    rather than crashing the whole page over a report this script does not own.
    """
    if not JUDGEMENTS_PATH.is_file():
        return {}
    try:
        data = json.loads(JUDGEMENTS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    by_path = {}
    for entry in data.get("judgments", []):
        image = entry.get("image", "")
        # A judgement names its image from the repository root; this page addresses images relative
        # to assets/, so the leading "assets/" is dropped to line the two up.
        if image.startswith("assets/"):
            image = image[len("assets/"):]
        by_path[image] = entry

    # LES ÉVALUATIONS DU RAPPORT PASSENT DEVANT, ET C'EST LA DÉCISION DE L'OPÉRATEUR (2026-08-05) : l'agent qui jugeait a été débranché, et c'est le rapport de production qui
    # pose désormais le score, à partir de ses propres mesures. Elles sont donc chargées après et écrasent ce que le fichier des jugements disait de la même image — sans quoi
    # une note d'agent, figée à la veille et jamais réécrite, continuerait de s'afficher à la place de la mesure du jour.
    for stored in sorted((ASSETS.parent / "var" / "generations").glob("*/*-evaluation.json")):
        try:
            evaluation = json.loads(stored.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        score = evaluation.get("score") or {}
        criteria = [{"name": CRITERIA_FR.get(item["name"], item["name"]), "passed": item.get("met", False),
                     "mesure": item.get("mesure", ""), "attendu": item.get("attendu", "")}
                    for item in evaluation.get("criteria", [])]
        failed = [item["name"] for item in criteria if not item["passed"]]
        entry = {"image": evaluation.get("image", ""), "score": score.get("met"), "total": score.get("total"),
                 # LA PASTILLE NE SE LIT PAS, ELLE SE VOIT. Tout tenu : une coche, et la bordure verte suffit à le dire. Un critère raté : c'est un avertissement ; plusieurs :
                 # c'est une erreur. Aucun mot, donc rien à replier sur trois lignes — le détail est dans la popin qu'elle ouvre, et la couleur reste le seul signal.
                 "verdict": "✓" if not failed else "",
                 "tone": "met" if not failed else ("warn" if len(failed) == 1 else "failed"),
                 "criteria": criteria}
        # La même évaluation vaut pour le maître et pour l'image détourée : c'est une seule image examinée, adressée de deux façons par la page. Les familles ne sont pas
        # devinées — on prend celles qui existent réellement sur le disque, ce qui évite d'inventer une adresse pour un dossier qui n'a jamais existé.
        for folder in ("cutout", "poc"):
            for family in sorted(item.name for item in (ASSETS / folder).iterdir() if item.is_dir()):
                by_path[f"{folder}/{family}/{evaluation.get('image', '')}"] = entry

    return by_path


JUDGEMENTS = load_judgements()

STORAGE_KEY = "gatebeast-suivi-sprites-v1"

# The production states. A word and a mark always travel with the colour, so nothing on this page is
# ever carried by colour alone. "en défaut" is a mechanical failure of the chain; "rejetée" is the
# owner turning an image down — two different things that must never be counted together.
STATUS = {
    "planned": {"label": "Prévue", "mark": "○"},
    "running": {"label": "En production", "mark": "◐"},
    "done": {"label": "Produite", "mark": "●"},
    "validated": {"label": "Validée", "mark": "✓"},
    # U+00D7 rather than a heavier cross: it is present in every font, so the mark cannot turn to tofu.
    "fault": {"label": "En défaut", "mark": "×"},
    "rejected": {"label": "Rejetée", "mark": "⊘"},
}
# The life of an image, then the two ways it can end badly. "produite" means the chain returned an
# image; "validée" means the owner accepted it — two different facts that must never be counted as one.
STATUS_ORDER = ["planned", "running", "done", "validated", "fault", "rejected"]

ACTIONS = [
    ("produce", "À produire"),
    ("validate", "Valider"),
    ("retry", "À reprendre"),
    ("drop", "Écarter"),
]

# What can be asked of a variant depends only on WHETHER AN IMAGE EXISTS. Nothing can be judged before one has ever been produced, and nothing is asked of one being produced
# right now. Dès qu'une image existe, LES TROIS VERDICTS RESTENT OFFERTS, quel que soit celui déjà donné — l'opérateur change d'avis quand il veut, et il l'a demandé en
# toutes lettres : « le bouton ne doit jamais être bloqué » (2026-08-05). Retirer « Valider » d'une image marquée à reprendre l'obligeait à passer par un autre état pour
# revenir sur son propre verdict, ce qui n'est pas un garde-fou mais une porte fermée à clé sur sa propre décision.
JUDGED = ["validate", "retry", "drop"]
STATE_ACTIONS = {
    "planned": ["produce"],
    "running": [],
    "done": JUDGED,
    "validated": JUDGED,
    "fault": JUDGED,
    "rejected": JUDGED,
}

LABELS = {
    # Le bouton d'effacement porte deux mots selon son moment : il efface, puis il rend. Ils vivent ici parce que le script ne porte aucun texte français.
    "fold": "▴",
    "unfold": "▾",
    "noteClear": "Effacer le commentaire",
    "noteRestore": "Rétablir le commentaire effacé",
    "recapTitle": "SUIVI DES SPRITES — RELEVÉ DU PROPRIÉTAIRE",
    "recapEmpty": "Rien de coché pour l'instant. Cochez une action ou écrivez un commentaire sur une "
                  "variante : le relevé se remplit ici, prêt à être copié.",
    "sections": {
        "produce": "À PRODUIRE",
        "validate": "VALIDÉES",
        "retry": "À REPRENDRE",
        "drop": "À ÉCARTER",
        "note": "COMMENTAIRES",
    },
    "copy": "Copier le relevé",
    "copied": "Relevé copié",
    "copyFailed": "Copie refusée par le navigateur — sélectionnez le texte à la main",
    "fold": "Replier",
    "unfold": "Déplier",
    "reset": "Tout effacer",
    "resetConfirm": "Effacer toutes vos cases cochées et vos commentaires ?",
    "barSummary": "relevé du propriétaire",
    "counted": "entrée",
    "countedPlural": "entrées",
    "filterOne": "variante affichée",
    "filterMany": "variantes affichées",
    "filterAllSuffix": "tout est affiché",
    "viewerFull": "— pleine taille de la source embarquée",
    "viewerRepeat": "répétée à l'échelle de la maquette",
    "viewerClose": "Fermer",
    "compareCurrent": "Version actuelle",
    "comparePrevious": "Version antérieure",
    "scopes": {
        "park": "maquette du parc",
        "later": "cible ultérieure",
        "trial": "essai de capacité",
    },
}


DEFAULT_SHAPE = "plain"


# A ref is not composed here, nor anywhere else: it is WRITTEN on the variant in the referentiel and read from there (sujets-et-variantes.md). The function
# that used to build one from the fields is gone — one notion, one place, and a page that shows exactly what the file says.


def type_variant_keys(type_def):
    """Every extra variant field a type declares, in a fixed alphabetical order.

    A variant field is any type key ending in "s" whose value carries "values" and "default" — the
    shape `compositions` and `portillons` already have, and whichever comes next without needing a
    change here. Alphabetical because nothing in the referentiel orders these fields itself, and the
    ref and the caption must agree on the very same order everywhere on the page.
    """
    return sorted(key for key, value in type_def.items()
                 if key.endswith("s") and isinstance(value, dict)
                 and "values" in value and "default" in value)


def leading_variant_keys(type_def):
    """Variant fields the type marks as changing what a variant fundamentally IS, not just how it is
    finished — `defines_kind: true` on the field's own declaration, read generically like every other
    variant field property (type_variant_keys()): a fixed marker the referentiel states, never a guess
    from a field's name or its number of values (composition also has three values, and never changes
    what the piece is). No current field carries this marker yet, so nothing leads until the
    referentiel adds it to one.
    """
    return [key for key in type_variant_keys(type_def) if type_def[key].get("defines_kind")]


def variant_field_values(type_def, entry):
    """Every value a variant carries on one of its type's variant fields that is not that field's own
    default — the referentiel's own rule (doc/glossaire.md, composition d'un sujet): a default is never
    written, since writing it on every variant would only make every other one harder to read by
    comparison. A variant names its value under the field's own singular name (`compositions` ->
    `composition`, `portillons` -> `portillon`), read here from what the type actually declares, never
    assumed from a fixed list — a third field tomorrow needs no change to this function either.
    """
    values = []
    for variant_key in type_variant_keys(type_def):
        field = variant_key[:-1]
        value = entry.get(field)
        if value and value != type_def[variant_key]["default"]:
            values.append(value)

    return values


# ---- the referentiel of sujets is the single source: no duplicate model lives here anymore ---------
# This page used to carry its own list of expected types, profiles and variants, kept by hand beside
# assets/sujets.json. The two drifted apart the day a new variant field (compositions) or a new shape arrived and
# only one of them learned about it — exactly what left three freshly produced fence pieces sitting in
# "hors modèle" although they were perfectly legitimate. There is now exactly one model: the referentiel
# itself, read here and never copied.
SUJETS_DATA = json.loads((ASSETS / "sujets.json").read_text(encoding="utf-8"))
TYPES = SUJETS_DATA["types"]
SUJETS = SUJETS_DATA["sujets"]
HORS_REFERENTIEL = {key: value for key, value in SUJETS_DATA.get("_hors_referentiel", {}).items()
                    if key != "_comment"}

# The French label a human actually reads is not this page's to invent or copy: it lives on the
# inventory sheets, the sole source of truth, and it changes there without this page knowing. Same
# read as artefacts/exemples-usage/build.py (`\*\*CODE libellé\*\*`), so a sheet is written once and
# both consumers agree on what it says.
INVENTAIRE_DIR = HERE.parents[1] / "doc" / "conception" / "referentiels" / "visuel" / "inventaire"

# Every sujet code the inventory sheets could not put a label to — a fact about the inventory, not a
# defect in this page, but one nobody should have to open the page to discover (see the report printed
# at the end of this script, alongside SKIPPED_IMAGES).
MISSING_LABELS = []

# Every image whose frozen consigne could not be found beside its master. A named state, not a fault:
# the earliest images of the project predate the rule that freezes one. Reported to the launcher in
# this script's own output all the same — an anomaly the page swallows is an anomaly nobody sees.
MISSING_PROMPTS = []


def load_sujet_labels():
    labels = {}
    if not INVENTAIRE_DIR.is_dir():
        return labels
    sheets = {path: path.read_text(encoding="utf-8") for path in sorted(INVENTAIRE_DIR.glob("*.md"))}
    for code in SUJETS:
        for text in sheets.values():
            match = re.search(rf"\*\*{re.escape(code)}\s+([^*]+)\*\*", text)
            if match:
                labels[code] = match.group(1).strip()
                break
    return labels


SUJET_LABELS = load_sujet_labels()

# A ground material is the one type delivered as an exact box rather than at a contractual width —
# the same fact export-asset.py holds under the same name, asked of the referentiel rather than
# retyped, since "sol" is the type whose layer is "sol".
TILE_TYPE = "sol"

# French section headings. The referentiel itself stays in the technical vocabulary it is written in;
# only display strings live here, exactly as any other UI label on this page does.
TYPE_LABELS = {
    "sol": "Sol", "chemin": "Chemin", "cours-d-eau": "Cours d'eau", "cloture": "Clôture et mur",
    "arbre": "Arbre", "bosquet-arbres": "Bosquet d'arbres", "herbe": "Herbe",
    "batiment": "Bâtiment", "humain": "Humain", "creature": "Créature",
}
# Human-readable text for a value the referentiel names, tried by ANY variant field (composition,
# portillon, and whichever comes next) — never keyed to one field by name, since a raw value like
# "posts-1" or "ferme" cannot collide between fields. A value with no entry here is shown exactly as
# the referentiel spells it (variant_caption()) rather than block on a translation this page does not
# own.
VARIANT_VALUE_LABELS = {
    "posts-2": "deux poteaux", "posts-1": "un poteau", "posts-0": "sans poteau",
    "gate-none": "sans portillon", "gate-closed": "portillon fermé", "gate-open": "portillon ouvert",
}


def type_rule(type_def):
    """What a type declares, in one line — derived from the referentiel's own data, never hand-written
    prose that could say something the data no longer does."""
    bits = [f"calque {type_def['layer']}",
            "passage ouvert par défaut" if type_def["passage_default"] == "open"
            else "passage fermé par défaut"]
    if type_def.get("assembles"):
        bits.append("s'assemble bout à bout, " + ("pivote" if type_def.get("rotates") else "ne pivote pas"))
    for variant_key in type_variant_keys(type_def):
        declaration = type_def[variant_key]
        values = ", ".join(declaration["values"])
        bits.append(f"{variant_key} {values} (défaut {declaration['default']})")
    if type_def.get("parts"):
        bits.append("parties qui pointent : " + ", ".join(type_def["parts"]))

    return " · ".join(bits)


# ---- disk inventory: the disk is the authority on what exists --------------------------------------
# The referentiel says what is WANTED and what already has a representation. It cannot say what IS on
# disk right now: only assets/poc/ and assets/cutout/ can. Every PNG found there is accounted for below
# — matched by the exact path its variant's own representations name, or, when no variant claims it (a
# capability trial, a discarded attempt, an earlier version, a reference plate), left visible in a
# "hors modèle" group instead of being silently dropped. No sprite is ever hidden by this page.


def scan_pngs(base):
    # A "usage-" file is a usage sample: one image showing an assembling subject's pieces laid out
    # together for comparison (generate-usage-sample.py). It is not a sprite — it has its own
    # artefact — so "every sprite stays on this page" does not reach it, and it never enters the scan.
    return sorted(path for path in base.rglob("*.png") if not path.name.startswith("usage-")) \
        if base.is_dir() else []


DISK = {"poc": scan_pngs(ASSETS / "poc"), "cutout": scan_pngs(ASSETS / "cutout")}

def _rest_of(relative_path):
    """A disk path with its leading poc/cutout folder dropped — the identity a master and its own
    export share, so claiming one accounts for the other."""
    return relative_path.split("/", 1)[1] if "/" in relative_path else relative_path


# Every path any variant's representations already name — the referentiel's own claim, taken exactly
# as written, never a guess from a file name. A representation only ever names the deliverable (a
# master is not itself a representation, per rendu-en-calques.md — "une variante porte des
# représentations, pas des images"), so the master BEHIND an already-claimed export is accounted for
# through the same subject identity, not through a claim of its own: CLAIMED_RESTS is what actually
# decides a stray, CLAIMED only tells a slot which exact file to show.
CLAIMED = {representation["path"]
          for sujet in SUJETS.values()
          for entry in sujet["variants"]
          for representation in entry.get("representations", [])}
CLAIMED_RESTS = {_rest_of(path) for path in CLAIMED}

# Anything the referentiel does not claim, master or export: a probe, a discarded shape, an older
# version, a reference plate. A poc master and its own cutout are the SAME stray subject, not two —
# they are grouped below by their path with the leading poc/cutout folder dropped, so a stray never
# doubles into two entries.
_stray_files = {}
for _kind, _paths in DISK.items():
    for _path in _paths:
        _relative = _path.relative_to(ASSETS).as_posix()
        _rest = _rest_of(_relative)
        if _rest in CLAIMED_RESTS:
            continue
        _stray_files.setdefault(_rest, {})[_kind] = _relative

# One entry per stray subject, cutout preferred over poc — the same rule a claimed variant follows,
# kept in a stable order so a re-run of this script never reshuffles the page.
HORS_MODELE = [
    {"kind": "cutout" if "cutout" in _stray_files[_rest] else "poc",
     "path": _stray_files[_rest].get("cutout") or _stray_files[_rest]["poc"]}
    for _rest in sorted(_stray_files)
]

# A shape is the set of edges a track reaches. The label spells that out in French rather than naming
# a drawing: the edges are what the ref means, and what a layout is checked against.
EDGE_LABELS = {"n": "nord", "e": "est", "s": "sud", "w": "ouest"}
DRAWING_LABELS = {1: "extrémité", 2: "ligne", 3: "trois branches", 4: "croisement"}


def shape_label(shape):
    if shape == DEFAULT_SHAPE:
        return "pleine"
    edges = list(shape)
    drawing = DRAWING_LABELS[len(edges)]
    if len(edges) == 2 and set(edges) not in ({"n", "s"}, {"e", "w"}):
        drawing = "angle"

    return f"{drawing} {'-'.join(EDGE_LABELS[edge] for edge in edges)}"


def shape_edges_label(shape):
    """Just the edges a shape connects, no drawing word in front (`ligne`, `angle`...) — used when a
    leading variant field already names what kind of piece this is (variant_caption()): repeating the drawing
    word in front of it would only restate what the leading label already said. A plain subject
    (DEFAULT_SHAPE) has no edges of its own to name.
    """
    if shape == DEFAULT_SHAPE:
        return ""
    return "-".join(EDGE_LABELS[edge] for edge in shape)


ORIENTATION_LABELS = {"north": "nord", "east": "est", "south": "sud", "west": "ouest"}


# ---- images: declared once, referenced everywhere -------------------------------------------------
# Each image's bytes appear exactly once in the whole page, as a CSS custom property on :root. The
# maquette-scale view and the click-to-enlarge view both point at that one declaration through
# var(--img-CODE), so nothing is ever embedded twice however many places show it.
def image_token(code):
    return f"--img-{slug(code)}"


def image_uri(code):
    """The embedded bytes of any image, deliverable or master — whichever catalogue holds it."""
    return (THUMBNAILS.get(code) or MASTERS[code])["uri"]


def image_declarations():
    # Called after every slot and every stray has been rendered, so MASTERS already holds every
    # master this page had to fall back on — none is declared, none is embedded, until it is shown.
    codes = sorted(set(THUMBNAILS) | set(MASTERS))
    return "\n".join(f"  {image_token(code)}: url({image_uri(code)});" for code in codes)


def footprint_label(footprint):
    columns, rows = footprint
    unit = "case" if (columns, rows) == (1, 1) else "cases"

    return f"{columns} × {rows} {unit}"


def working_box(footprint, kind, code):
    """The size a sprite is actually SHOWN at: the game's own display fineness, 24 pixels per tile of
    footprint width — exactly what the player sees on screen, so nothing validated here can read
    differently once it is in the game.

    Every figure is ASKED of tile_scale.py, never retyped here, whatever definition the underlying
    file happens to be exported or mastered at — a deliverable and a master stand-in both come down to
    the same display size, so the two read at one consistent scale on this page.

    Width comes from the footprint — the ground the subject occupies — and height only ever follows the
    image's own proportions, never the other way around: scaling to a declared height would shrink a
    tall building until its base stopped covering its tiles. A tall subject overflows upward instead.
    A ground material is the one exception: it takes its footprint in both dimensions, because it has
    to tile edge to edge.
    """
    columns, rows = footprint
    if kind == "tile":
        return tile_scale.tile_box(columns, rows)
    width, height = image_size(code)

    return tile_scale.sprite_box(columns, width, height)


def maquette_style(code, footprint, kind):
    box = working_box(footprint, kind, code)

    return f"width:{box['width']}px;height:{box['height']:.0f}px"


def empty_style(footprint):
    """An unshot variant occupies the ground it will occupy: its footprint, at maquette scale."""
    columns, rows = footprint
    box = tile_scale.tile_box(columns, rows)

    return f"width:{box['width']}px;height:{box['height']}px"

# Every variant the page carries, in page order, for the runtime recap.
registry = []

# Every variant that holds more than one representation, keyed by its identifier — the comparison
# popin's own data, built as each slot is rendered and read back only once every slot has run.
comparisons = {}

# Everything a control opens in the shared popin, keyed by the control's own key: a variant's metadata, an image's frozen consigne. Held as data rather
# than as markup so nothing of it is ever laid inline in the flow — an inline fold pushes every slot below it out of place and is unreadable next to a
# sprite (operator, 2026-08-05). Each entry carries its title, its kind, and either rows of facts or one block of verbatim text.
panels = {}

# Each image's own frozen consigne and its production report, keyed by the display code the viewer is opened with, so the enlarged view shows both beside
# the picture — what was asked, and how it was obtained.
prompts = {}
reports = {}


def current_representation(representations):
    """The one representation a variant shows in its main slot — the referentiel's own authority, not
    a guess read off a file name: a representation carries `statut: "courante"` once a variant has
    more than one, per doc/outils/referentiel-des-sujets.md ("une version active par variante"). A
    lone representation needs no marking at all — there is nothing else it could be.
    """
    if len(representations) == 1:
        return representations[0]
    marked = [rep for rep in representations if rep.get("statut") == "courante"]
    assert len(marked) == 1, (
        f"exactly one representation must carry statut=\"courante\" among {len(representations)}: "
        f"{[rep['path'] for rep in representations]}")

    return marked[0]


def previous_representations(representations, current):
    """The earlier versions this page SHOWS beside the current one, in the referentiel's own order —
    most recent first. The referentiel keeps every version without limit; three are shown in all, the
    current one and the two before it (operator, 2026-08-05)."""
    return [rep for rep in representations
            if rep is not current][:check_sujets.SHOWN_PREVIOUS_REPRESENTATIONS]


def escape(text):
    return html.escape(str(text), quote=True)


def lead_capital(text):
    """Capitalise a standalone label's leading letter, and nothing else — never Title Case the rest
    of it, and never touch a code or a technical ref, which keep the exact case their files
    carry. Applied only at the point a composed phrase (a variant's caption, a type's rule) becomes
    the whole content of a displayed label; the fragments it is built from stay as they are, since
    most of them are also used mid-sentence elsewhere, where a leading capital would be wrong.
    """
    return text[:1].upper() + text[1:] if text else text


def status_markup(status, extra=""):
    entry = STATUS[status]

    return (f'<p class="status status--{status}{extra}">'
            f'<span class="dot" aria-hidden="true">{entry["mark"]}</span>'
            f'<span class="status-word">{escape(entry["label"])}</span></p>')


def actions_markup(identifier, subject, status):
    """The marks that make sense for this state stay visible. The comment folds away.

    Offering "à reprendre" on a variant that has never been produced asks the owner to judge something
    that does not exist, so each state only shows the moves it actually allows. The comment is always
    available: there is always something one might want to say.
    """
    allowed = STATE_ACTIONS[status]
    chips = "\n".join(
        f'                <label class="act">'
        f'<input type="checkbox" data-act="{key}" data-id="{escape(identifier)}" '
        f'aria-label="{escape(label)} — {escape(subject)}" />'
        f'<span>{escape(label)}</span></label>'
        for key, label in ACTIONS if key in allowed)

    return f"""              <div class="actions">
{chips}
                <button type="button" class="act-note" data-open="{escape(identifier)}"
                        aria-expanded="false" aria-label="Commentaire — {escape(subject)}">＋</button>
              </div>
              <div class="slot-more" data-more="{escape(identifier)}" hidden>
                <textarea class="note" rows="2" data-note="{escape(identifier)}"
                          placeholder="Commentaire" aria-label="Commentaire — {escape(subject)}"></textarea>
                <button type="button" class="note-clear" data-clear="{escape(identifier)}"
                        title="Effacer le commentaire"
                        aria-label="Effacer le commentaire — {escape(subject)}" hidden>×</button>
              </div>"""


def register(identifier, code, profile_label, type_label, ref_text, scope, status):
    registry.append({"id": identifier, "code": code, "profile": profile_label, "type": type_label,
                     "ref": ref_text, "scope": scope, "status": status})


def field_varies(variants, getter):
    """Whether `getter(entry)` takes more than one distinct value across ONE sujet's own variants —
    the population variant_caption()'s label-brevity rule is judged against: a field that can only
    ever be one thing for this sujet distinguishes none of its variants from another, however many
    values it could take elsewhere in the referentiel or for another sujet of the same type. A sujet
    with a single variant never varies on anything, by construction — there is nothing to tell it
    apart from.
    """
    return len({getter(entry) for entry in variants}) > 1


def variant_caption(type_def, entry, varies):
    """What actually distinguishes this variant, in the order it matters.

    A LABEL SAYS WHAT DISTINGUISHES A VARIANT, NOTHING MORE (the operator's own rule): a field that
    cannot take more than one value across this sujet's own variants (varies, from field_varies() —
    asked of the shape, the orientation and every variant field alike, never hardcoded per field) is
    left out of the caption entirely, however meaningful it looks in isolation — "sud" says nothing
    when every variant of this sujet faces south. The day a sujet actually has more than one
    orientation (a character, a creature), it reappears in the caption on its own, with no change
    needed here.

    Every variant field that DOES vary is always named, default value included (a caption exists to
    tell two variants apart at a glance, and staying silent on a field whenever it holds the default
    would let "deux poteaux" and "un poteau" both read as plain "ligne nord-sud"). Most fields trail
    after the shape, in the same fixed order the ref itself lists them. But a field the type marks
    as changing what the piece fundamentally IS (leading_variant_keys(): `defines_kind`) LEADS the
    caption instead, and only when it actually holds a value other than its own default — a fence
    stays "ligne nord-sud" until a portillon is what it is, at which point the caption reads
    "Portillon ouvert, nord-sud", not "Ligne nord-sud · … · portillon ouvert" where the one fact that
    matters arrives last. The shape's own drawing word (`ligne`, `angle`...) is dropped in that case
    (shape_edges_label()): the leading label already says what kind of piece this is, so it would only
    repeat itself.
    """
    leading_keys = leading_variant_keys(type_def)
    leading_labels = []
    trailing_labels = []
    for variant_key in type_variant_keys(type_def):
        field = variant_key[:-1]
        if not varies.get(field):
            continue
        default = type_def[variant_key]["default"]
        value = entry.get(field, default)
        label = VARIANT_VALUE_LABELS.get(value, value)
        if variant_key in leading_keys and value != default:
            leading_labels.append(label)
        else:
            trailing_labels.append(label)

    shape_speaks = type_def.get("assembles") and varies.get("shape")
    if leading_labels:
        edges = shape_edges_label(entry.get("shape", DEFAULT_SHAPE)) if shape_speaks else ""
        caption = ", ".join(filter(None, [" · ".join(leading_labels), edges]))
    elif shape_speaks:
        caption = shape_label(entry.get("shape", DEFAULT_SHAPE))
    else:
        # Either the subject does not assemble, or it does but this sujet only ever uses one shape:
        # either way there is nothing left to say about shape, so it falls back to the same neutral
        # caption a non-assembling subject gets.
        caption = "vue principale"

    for label in trailing_labels:
        caption = f"{caption} · {label}"
    orientation_speaks = (type_def.get("assembles") and not type_def.get("rotates")
                         and varies.get("orientation"))
    if orientation_speaks and entry.get("orientation") in ORIENTATION_LABELS:
        caption = f"{caption} · {ORIENTATION_LABELS[entry['orientation']]}"

    return caption


def unread_shot_markup(label, path, style):
    """A representation the referentiel names but this page could not embed — for whichever reason
    SKIPPED_IMAGES names for this exact path (unreadable, or too heavy — see master_entry()).

    GENERAL RULE, NOT SPECIFIC TO EITHER CASE: a page whose one job is to report the state of
    production must never crash, and never show an empty frame under a "produced" label either, over
    an image it could not embed. It shows this plainly marked placeholder instead, at exactly the box
    the caller sizes it at — never an invented size — so every other sprite on the page keeps showing
    regardless. Applies wherever a representation's bytes are embedded: a modelled variant's slot
    (variant_shot()) and a stray file alike (stray_vis_markup()).
    """
    reason = SKIPPED_IMAGES.get(path, {"short": "Image indisponible", "detail": "raison inconnue"})

    return (f'<div class="frame frame--unread" style="{style}" role="img" '
            f'aria-label="{escape(label)} — {escape(reason["detail"])} : {escape(path)}">'
            f'<span>{escape(reason["short"])}</span></div>')


def variant_shot(path, footprint, kind, label):
    """One representation. A path under poc/ is a master standing in for a livrable that does not
    exist yet, marked as such; a path under cutout/ is the livrable itself — the distinction the slot
    used to read off a disk scan is now read directly off the referentiel's own path.

    The referentiel naming a representation does not mean this page can already read its bytes: a
    fresh export can land on disk before scripts/build-thumbnails.py has caught up (see
    resolve_image()). When even a direct read fails, unread_shot_markup() shows the gap honestly
    instead of taking the whole page down over one file.

    A representation heavy enough to cross MAX_EMBED_BYTES still shows — as a thumbnail sized to the
    very box it is displayed at (display_code_for()), never the untouched original, which stays
    reachable through the eye and a click on the picture (shot_markup()'s own full_code).
    """
    full_code = resolve_image(path)
    if full_code is None:
        return unread_shot_markup(label, path, empty_style(footprint))
    box = working_box(footprint, kind, full_code)
    display_code = display_code_for(path, full_code, box)
    if path.startswith("poc/"):
        return shot_markup(display_code, footprint, kind, f"{label} — maître, pas encore exporté",
                           extra=" shot-frame--master", full_code=full_code)
    return shot_markup(display_code, footprint, kind, label, full_code=full_code)


def representation_meta_markup(identifier, path, code, label, master=None):
    """Everything about one representation that is NOT the picture itself, in the encart's text area:
    whether it stands in for an unexported master, and its judgement — nothing here is ever laid over
    the image (see shot_markup()), so reading it never hides part of the sprite it is about.
    """
    tag = ('<p class="shot-tag">Maître, pas encore exporté</p>' if path.startswith("poc/") else "")
    # The consigne is frozen beside the MASTER, never beside the deliverable the export writes.
    remember_prompt(code, master or path)

    return tag + judge_body_markup(identifier, code, label)


def frozen_prompt(path):
    """The consigne that produced ONE image, read from the file frozen beside its master.

    Every image keeps its own consigne, written next to it and never rewritten once the image exists
    (chaine-de-production.md) — so the text belongs to the representation, not to the variant: two
    versions of the same variant were produced by two different consignes, and showing one for the
    other would be worse than showing none.

    Returns None when the file is absent, which is a real state and not a fault here: the very first
    images of the project predate the rule. It is reported to the launcher all the same, in the run's
    own output, so it can be found (see MISSING_PROMPTS).
    """
    master = ASSETS / path
    frozen = master.with_suffix(".txt")
    if not frozen.is_file():
        MISSING_PROMPTS.append(path)
        return None

    return frozen.read_text(encoding="utf-8")


def remember_prompt(code, master_path):
    """Keep this image's own consigne AND its production report, so the enlarged view can show both beside the picture.

    The three belong together and nowhere else: the picture says what came out, the consigne says what was asked, and the report says how it was obtained —
    the model, the session to reopen, the timings, the measures. Judging on any one of them alone is what sent this project chasing the wrong cause more
    than once. All keyed by the image's own display code, the very key the viewer is opened with, so no control has to carry the text around.
    """
    if code is None or not master_path:
        return
    text = frozen_prompt(master_path)
    if text is not None:
        prompts[code] = text
    # The report is a trace of the run, kept under var/generations/ — assets/ holds assets and nothing else. Sprites and usage samples each have their own
    # folder there, and a report is looked for in both rather than guessed at from the path.
    stem = Path(master_path).stem
    for kind in ("sprites", "subjects"):
        report = ASSETS.parent / "var" / "generations" / kind / f"{stem}-rapport.md"
        if report.is_file():
            break
    if report.is_file():
        reports[code] = report.read_text(encoding="utf-8")
    # THE SCORE COMES FIRST, AND IT COMES FROM ITS OWN FILE. The evaluation is stored beside the report by the measuring tool, and it is re-derivable from the image at any
    # time — so an image produced before the score existed shows one too, as soon as it is re-examined. Placed above the report rather than inside it because it is the one
    # line anyone reads before deciding whether to read the rest.
    stored = report.parent / f"{stem}-evaluation.json"
    if stored.is_file():
        evaluation = json.loads(stored.read_text(encoding="utf-8"))
        failed = [criterion["name"] for criterion in evaluation["criteria"] if not criterion["met"]]
        head = (f"SCORE {evaluation['score']['met']}/{evaluation['score']['total']} critères tenus"
                + ("" if not failed else " — en échec : " + ", ".join(failed)))
        reports[code] = head + "\n\n" + reports.get(code, "")


# The OPERATOR's own word on a representation — "validee", "a-reprendre", "ecartee" — a wholly
# different opinion from the judging agent's scored report (judge_body_markup(), assets/jugements.json):
# one is the owner deciding, the other is a machine critique. Different vocabulary on purpose (never
# "retenue"/"à refaire", the judge's own words), so the two can never be misread as the same fact.
VERDICT_LABELS = {"validee": "Validée", "a-reprendre": "À reprendre", "ecartee": "Écartée"}
# The verdict's own CSS colour family — named for what it reads as, not reusing the production
# STATUS's "validated"/"fault"/"rejected" slots (those track the CHAIN's own state, a different fact
# entirely: whether an image exists at all, never whether the operator liked it).
VERDICT_STYLES = {"validee": "validated", "a-reprendre": "rework", "ecartee": "rejected"}
# The production state a verdict imposes on its variant. Only these three: a verdict the operator has not given leaves the variant in the state the files
# alone give it. "rework" is the verdict's own colour family, "fault" the production state — the two words differ on purpose and are not interchangeable.
VERDICT_STATUS = {"validee": "validated", "a-reprendre": "fault", "ecartee": "rejected"}


def operator_verdict_markup(representation):
    """The operator's verdict and comment on one exact representation, visible without opening
    anything — the comment is often what matters most, so it travels right along with the word, never
    behind a fold. Nothing is shown at all when the referentiel carries no verdict yet for this exact
    representation: silence here means "not yet judged by the operator", the same way
    judge_body_markup() stays silent for an unjudged image.
    """
    verdict = representation.get("verdict")
    if not verdict:
        return ""
    style = VERDICT_STYLES.get(verdict, "rework")
    label = VERDICT_LABELS.get(verdict, verdict)
    comment = representation.get("commentaire_operateur")
    comment_markup = f'<p class="verdict-comment">{escape(comment)}</p>' if comment else ""

    return (f'<div class="verdict verdict--{style}">'
            f'<span class="verdict-word">{escape(label)}</span></div>{comment_markup}')


def rejected_shot_markup(path, footprint, label):
    """The picture behind a representation the operator has already turned down: never painted in the
    main flow — the project's own rule, an écartée image is retired from view, never deleted or
    hidden — but still one click away through the eye, which is why the file is resolved (embedded)
    here even though nothing draws it.
    """
    resolve_image(path)

    return (f'<div class="frame frame--rejected" style="{empty_style(footprint)}" role="img" '
            f'aria-label="{escape(label)} — image écartée, disponible via le bouton œil">'
            f'<span>Image&nbsp;écartée</span></div>')


def ground_extent(sujet):
    """What the sujet stands on and blocks — its emprise, in cells."""
    return (sujet["emprise"]["columns"], sujet["emprise"]["rows"])


def drawn_extent(sujet):
    """What the sujet's volume covers, and therefore what its picture spans — its couvert, which falls back to its emprise when it declares none.

    Two different facts, and confusing them is what squashed the apple tree: the emprise says where it stands, the couvert says how far its canopy reaches.
    """
    couvert = sujet.get("couvert")

    return (couvert["columns"], couvert["rows"]) if couvert else ground_extent(sujet)


def main_variant(sujet):
    """The sujet's PRINCIPAL variant — the one every other one cascades from.

    Taken from the referentiel, which marks it with "principale": true, and never guessed here: which
    piece of an assembling sujet leads is a design decision, not something a display can deduce from a
    shape's name. A sujet with a single variant has that one for principal, marker or not — there is
    nothing else it could be.
    """
    variants = sujet["variants"]
    for entry in variants:
        if entry.get("principale"):
            return entry

    return variants[0] if len(variants) == 1 else None


def ordered_variants(sujet):
    """The sujet's variants, its principal one first — it is the reference the others are judged
    against, so it is the one the eye must meet first."""
    principal = main_variant(sujet)
    if principal is None:
        return sujet["variants"]

    return [principal] + [entry for entry in sujet["variants"] if entry is not principal]


def slot_markup(sujet_code, sujet, type_name, type_def, entry, varies, principal=False):
    """One variant, captioned by what actually distinguishes it, holding its current representation.

    A variant can carry more than one representation when a posture was attempted twice — only the
    latest is ever shown in this flow; the earlier attempts are not dropped, they move to the
    comparison popin (see compare_button_markup()) so a second attempt at the same posture is never
    hidden, only kept out of the way.

    The operator's own actions and comment field are offered here UNCONDITIONALLY, whether or not a
    representation exists and whether or not a judgement covers it: the machine's score is one more
    fact next to the sprite, never a gate on what the operator may do with it.
    """
    caption = variant_caption(type_def, entry, varies)
    # The picture is drawn on the COUVERT — what the subject's volume overhangs — because that is the extent the image itself covers; the emprise is what
    # it stands on, and using it to size the drawing squashed an apple tree whose canopy spreads three cells wide into one (sujets-et-variantes.md).
    footprint = drawn_extent(sujet)
    kind = "tile" if type_name == TILE_TYPE else "sprite"
    # READ, never recomposed: the ref is the variant's identifier and it is written in the referentiel (sujets-et-variantes.md). This page used to build one
    # of its own from the fields, which is a second way of naming the same thing — and the day the two disagreed, nothing would have said which was right.
    ref = entry["ref"]
    identifier = f"{sujet_code}|{ref}"
    subject = f"{sujet_code} {caption}"
    representations = entry.get("representations", [])
    # The state of a variant is what the referentiel knows of it: no image yet, an image produced, or an image the OPERATOR has already ruled on. His
    # verdict outranks the mere fact that a file exists — being asked to judge again what he has already judged is what this rule exists to stop.
    status = "done" if representations else "planned"
    if representations:
        status = VERDICT_STATUS.get(current_representation(representations).get("verdict"), status)
    register(identifier, sujet_code, sujet["profil"], TYPE_LABELS.get(type_name, type_name), ref,
             "park", status)

    # The layout threshold is asked at the very scale the page actually draws at, never at a scale
    # that was true under an earlier rendering choice.
    wide = tile_scale.sprite_width(footprint[0]) > 200
    meta = variant_meta_markup(identifier, sujet_code, sujet, type_def, entry, subject)
    tools = ""
    verdict_markup = ""
    if representations:
        current = current_representation(representations)
        previous = previous_representations(representations, current)
        # An écartée current representation is retired from the flow — the operator already turned
        # it down — but never deleted and never hidden: it stays one click away through the eye
        # (rejected_shot_markup()), while the ordinary picture simply is not painted here.
        if current.get("verdict") == "ecartee":
            vis = rejected_shot_markup(current["path"], footprint, subject)
        else:
            vis = variant_shot(current["path"], footprint, kind, subject)
        current_code = thumbnail_key(current["path"])
        judge = representation_meta_markup(identifier, current["path"], current_code, subject,
                                           master=current.get("maitre"))
        verdict_markup = operator_verdict_markup(current)
        tool_buttons = [enlarge_button_markup(current_code, subject), meta]
        meta = ""  # placed among the tools; never a second time below
        if previous:
            tool_buttons.append(compare_button_markup(identifier, subject))
            # Each previous representation must actually be embedded here, not merely named: the
            # comparison popin shows it in full, and nothing guarantees a superseded version is
            # already in THUMBNAILS just because the current one is. resolve_image() reads it off
            # disk when needed (or records why it could not, per master_entry()); the JS side already
            # degrades gracefully to a blank tile with its caption if a code never resolves.
            for rep in previous:
                resolve_image(rep["path"])
            comparisons[identifier] = {
                "subject": subject,
                "current": {"code": current_code, "path": current["path"],
                           "verdict": VERDICT_LABELS.get(current.get("verdict")),
                           "comment": current.get("commentaire_operateur"),
                           "judge": judge_summary(current_code)},
                "previous": [{"code": thumbnail_key(rep["path"]), "path": rep["path"],
                             "verdict": VERDICT_LABELS.get(rep.get("verdict")),
                             "comment": rep.get("commentaire_operateur"),
                             "judge": judge_summary(thumbnail_key(rep["path"]))}
                            for rep in previous],
            }
        tools = f'              <div class="encart-tools">{"".join(tool_buttons)}</div>'
    else:
        vis = (f'<div class="frame" style="{empty_style(footprint)}" role="img" '
               f'aria-label="Aucune image produite — {escape(footprint_label(footprint))}"></div>')
        judge = ""

    # The image this slot is showing, carried into the page so the operator's own answers can be tied
    # to it: an answer is given to an image, and must not outlive the image it was given to.
    shot = current["path"] if representations else ""

    lead = '<span class="lead-mark">Principale</span>' if principal else ""

    return f"""          <li class="slot slot--park{' slot--wide' if wide else ''}{' slot--lead' if principal else ''}" data-slot="{escape(identifier)}" data-shot="{escape(shot)}" data-status="{status}">
            <div class="slot-vis">{vis}</div>
            <div class="slot-body">
              <div class="slot-line"><span class="slot-caption">{escape(lead_capital(caption))}</span>{lead}{status_markup(status, ' status--pill')}</div>
              <p class="slot-ref">{escape(ref)}</p>
{verdict_markup}
{tools}
{meta}
{judge}
{actions_markup(identifier, subject, status)}
            </div>
          </li>"""


def thumbnail_key(relative_path):
    """The THUMBNAILS key for a disk path: the path itself, its ".png" dropped."""
    return relative_path[:-4] if relative_path.endswith(".png") else relative_path


# Masters are loaded on demand, never scanned up front like THUMBNAILS: an image is only worth its
# weight on the page when it is actually shown, so only the ones actually shown are ever read and
# base64-encoded. Originally holding only poc masters standing in for an unexported deliverable, this
# cache now equally holds any representation whose bytes have not reached THUMBNAILS yet (see
# master_entry()) — the name stays because most of what lands here still is a master.
MASTERS = {}


# Every representation the referentiel names but this run could not read at all — a fact of
# production (missing, still landing, or corrupt), never a code error, so it must not raise. Keyed by
# relative path; each value holds the short phrase the page itself shows in the slot
# (unread_shot_markup()) and the fuller detail printed to whoever launched the build (see the report
# at the end of this script) — a defect visible only inside the page is a defect nobody watches.
SKIPPED_IMAGES = {}

# The size past which a representation gets a genuine thumbnail for the main slot instead of embedding
# its own full bytes there (see display_code_for()) — a GUARD-RAIL now, not a refusal: no image at or
# under this weight has ever failed to display on this page (the heaviest confirmed working is
# cutout/vegetation/TR-061-v2.png at 120 263 bytes), so this sits comfortably above that with room to
# spare, in one place, easy to raise the day a heavier image turns out to display fine too. The FULL
# image is still always embedded, whatever its weight — the eye and a click on the picture must keep
# opening the untouched original (shot_markup()), never the thumbnail.
MAX_EMBED_BYTES = 500_000

# The thumbnail is built at this many times its own CSS display size, so a screen that packs two (or
# three) device pixels into one CSS pixel still shows it sharp rather than upscaled and soft.
THUMBNAIL_SUPERSAMPLE = 2


def master_entry(relative_path):
    """Read any image straight off the disk and cache it under the same key scheme as THUMBNAILS.

    Originally written for a poc master standing in for an unexported deliverable, this is now the
    general fallback for any representation the referentiel names whose bytes are not in THUMBNAILS
    yet: a fresh export can land on disk between two runs of scripts/build-thumbnails.py, and this
    page must show it anyway rather than wait for that cache to catch up.

    Always reads and caches the FULL file, whatever its weight — the eye and a click on the picture
    must be able to open the untouched original (shot_markup()); see display_code_for() for what the
    main slot actually paints instead when that full file is heavy.

    Returns the cache key on success. Returns None, touching nothing, when the file is missing or PIL
    cannot identify it as an image (still being written, truncated, corrupt) — the two conditions this
    function can actually NAME as a fact of production rather than a defect in this script. Only these
    are caught: nothing here shields a KeyError, a TypeError, or any other failure this function cannot
    name — those are code errors, and the project's rule is that a code error always raises and always
    reaches the operator running the build, never swallowed for the sake of a prettier page. On what it
    does catch, the caller shows a plainly marked "unread" placeholder for that one representation
    instead of losing every other sprite over it (unread_shot_markup()), and its size is never guessed
    from a name or a footprint — only ever read from the file itself.
    """
    key = thumbnail_key(relative_path)
    if key in MASTERS:
        return key
    path = ASSETS / relative_path
    try:
        data = path.read_bytes()
        with Image.open(path) as probe:
            size = probe.size
            data, size = shrink_to_screen(probe, data, size)
    except (FileNotFoundError, UnidentifiedImageError) as error:
        SKIPPED_IMAGES[relative_path] = {
            "short": "Image non lisible",
            "detail": f"illisible ({type(error).__name__}: {error})",
        }
        return None
    MASTERS[key] = {"uri": f"data:image/png;base64,{base64.b64encode(data).decode('ascii')}",
                    "size": size, "bytes": len(data)}

    return key


# The longest side an image keeps once embedded in this page. A screen shows the enlarged view at a
# few hundred pixels; carrying a 1536-pixel master into the file bought nothing and cost megabytes.
SCREEN_LONG_SIDE = 640


def shrink_to_screen(image, data, size):
    """Give back the bytes to embed for this image, reduced to what a screen can actually show.

    A page that embeds every master at full definition reached thirteen megabytes, and past a certain
    point the browser stopped applying the declarations altogether: every image declared after that
    point came back "is not defined" and painted nothing, while the ones before it kept working. That
    is the defect this exists to remove — the file on disk is untouched and stays the reference; only
    what travels inside the page is reduced.
    """
    if max(size) <= SCREEN_LONG_SIDE:
        return data, size
    scale = SCREEN_LONG_SIDE / max(size)
    reduced = image.convert("RGBA").resize(
        (max(1, round(size[0] * scale)), max(1, round(size[1] * scale))), Image.LANCZOS)
    buffer = io.BytesIO()
    reduced.save(buffer, format="PNG", optimize=True)

    return buffer.getvalue(), reduced.size


def image_bytes(code):
    """How many bytes an embedded image's own file held, from whichever catalogue holds it — the
    figure display_code_for() weighs against MAX_EMBED_BYTES."""
    return (THUMBNAILS.get(code) or MASTERS[code])["bytes"]


def thumbnail_entry(relative_path, full_code, css_width, css_height):
    """Build (once, then cache) a genuine thumbnail for a representation too heavy to embed at its own
    full size in the main slot: resized to the exact box the page shows it at, times
    THUMBNAIL_SUPERSAMPLE for a dense screen — never the untouched original, and never smaller than
    what is actually shown. Cached under its own key, distinct from full_code, so the eye and a click
    on the picture keep reaching the original untouched (see display_code_for(), shot_markup()).
    """
    key = f"{full_code}#thumbnail"
    if key in MASTERS:
        return key
    target_width = max(1, round(css_width * THUMBNAIL_SUPERSAMPLE))
    target_height = max(1, round(css_height * THUMBNAIL_SUPERSAMPLE))
    with Image.open(ASSETS / relative_path) as source:
        resized = source.convert("RGBA").resize((target_width, target_height), Image.LANCZOS)
    buffer = io.BytesIO()
    resized.save(buffer, format="PNG", optimize=True)
    data = buffer.getvalue()
    MASTERS[key] = {"uri": f"data:image/png;base64,{base64.b64encode(data).decode('ascii')}",
                    "size": (target_width, target_height), "bytes": len(data)}

    return key


def display_code_for(relative_path, full_code, box):
    """The code the main slot actually paints, given the CSS box (box['width']/box['height']) it is
    shown at. Identical to full_code for anything already at or under MAX_EMBED_BYTES — nothing to
    gain from a second copy of an image already light. Past that weight, a genuine thumbnail
    (thumbnail_entry()) takes its place in the slot; the eye and a click on the picture still open
    full_code, untouched, regardless of which one this function returns.
    """
    if image_bytes(full_code) <= MAX_EMBED_BYTES:
        return full_code

    return thumbnail_entry(relative_path, full_code, box["width"], box["height"])


def resolve_image(relative_path):
    """The embeddable code for a representation's bytes, whichever catalogue ends up holding them:
    the pre-built THUMBNAILS cache when it already knows the path, a direct disk read otherwise (see
    master_entry()). None means neither succeeded — the file could not be characterised at all, and
    nothing about it may be guessed.
    """
    key = thumbnail_key(relative_path)
    if key in THUMBNAILS:
        return key

    return master_entry(relative_path)


def image_size(code):
    """The pixel size of any embedded image, deliverable or master — the two catalogues never mix
    their bytes, but a caller sizing a box does not need to know which one it is looking at."""
    return (THUMBNAILS.get(code) or MASTERS[code])["size"]


def shot_background(code, kind):
    """The image on top, a checkerboard beneath: the only way its own transparency can be judged.

    A CSS background list is painted front to back, so listing the image first and the checker second
    lets every transparent pixel of the PNG show the checker straight through it.
    """
    fit = "100% 100%" if kind == "tile" else "contain"
    position = "center" if kind == "tile" else "center bottom"

    return (f"background:var({image_token(code)}) {position} / {fit} no-repeat, "
            f"repeating-conic-gradient(var(--checker-a) 0 25%, var(--checker-b) 0 50%) "
            f"top left / 16px 16px repeat")


def frame_style(footprint, kind, code):
    """The click target's own size: never smaller than the picture shown at working_box(), and never
    smaller either than the footprint's own tile box — a FLOOR, not a viewing size, so a very flat
    sprite (an image much wider than it is tall) still keeps a full tile to aim at rather than the
    sliver its own drawn pixels would otherwise offer.
    """
    shown = working_box(footprint, kind, code)
    floor = tile_scale.tile_box(*footprint)

    return {"width": max(shown["width"], floor["width"]), "height": max(shown["height"], floor["height"])}


def shot_markup(code, footprint, kind, label, extra="", full_code=None):
    """A produced image, posed on the bottom edge of a click target sized by frame_style() — never
    smaller than the footprint, however thin or tall the picture itself is, so the WHOLE target is
    worth aiming at, not just the pixels the image happens to draw.

    NOTHING IS LAID OVER THE PICTURE — not a button, not a score, not a label. The owner is here to
    judge the sprite itself, and any element posed on top of it hides part of what has to be looked
    at, worst of all on a one-tile subject where an overlay can cover most of the image. Every other
    fact about this shot — its open-full-size control, whether it stands in for an unexported master,
    its judgement — lives in the encart's text area instead (see representation_meta_markup()).

    The frame itself is the whole click target: a focusable, labelled div rather than a native
    <button>, because the button that used to sit on the image is gone and this is what replaces it —
    the SAME action, moved off the picture rather than dropped.

    `code` is what is actually PAINTED here — possibly a thumbnail (display_code_for()). `full_code`
    (the untouched original, defaulting to `code` when the two are the same file) is what opens in the
    viewer: a click on the picture, or the eye, must always reach the real thing, never the thumbnail
    substituted for it. Each of the two bytes involved lives once in its own CSS custom property; nothing
    here or in the viewer ever carries either one twice.
    """
    if full_code is None:
        full_code = code
    frame = frame_style(footprint, kind, code)

    return (f'<div class="shot-frame{extra}" role="button" tabindex="0" '
            f'aria-label="{escape(label)} — voir en pleine taille" '
            f'style="width:{frame["width"]}px;height:{frame["height"]:.0f}px" '
            f'data-img="{escape(full_code)}">'
            f'<div class="shot" style="{maquette_style(code, footprint, kind)};'
            f'{shot_background(code, kind)}"></div>'
            f'</div>')


def judgement_for(code):
    """The judgement for the image actually shown — trying the poc/cutout counterpart of the same
    file first, because a judging agent reviews the master while this page prefers the deliverable
    the moment one is exported. The two are the same artistic content at two sizes; a judgement of one
    still describes the other, so it is not lost the day an export appears.
    """
    if not code:
        return None
    direct = JUDGEMENTS.get(f"{code}.png")
    if direct is not None:
        return direct
    if code.startswith("cutout/"):
        return JUDGEMENTS.get(f"poc/{code[len('cutout/'):]}.png")
    if code.startswith("poc/"):
        return JUDGEMENTS.get(f"cutout/{code[len('poc/'):]}.png")
    return None


def judge_summary(code):
    """A short, text-only account of the judging agent's report for one exact image — score, its own
    verdict, its own words — for the comparison popin, which builds its content with textContent only
    (never innerHTML, see the SCRIPT's own rule): the full folding criteria list judge_body_markup()
    offers inline has no place there, only what a plain paragraph can carry. A JUDGEMENT FOLLOWS THE
    IMAGE, NEVER THE VARIANT: judgement_for(code) is already keyed to this exact file, so a
    representation that has become "antérieure" still reads its own report here, right next to it,
    instead of losing it the moment a new version takes its place in the main flow.
    """
    judgement = judgement_for(code)
    if judgement is None:
        return None
    score = f"{judgement.get('score')}/{judgement.get('total')}"
    verdict = judgement.get("verdict", "")
    report = judgement.get("report", "")

    return f"{score} {verdict} — {report}" if report else f"{score} {verdict}"


def judge_body_markup(identifier, code, label):
    """The score and verdict, always visible; the criterion-by-criterion detail OPENS IN THE POPIN, never unfolding in place. A sprite with no evaluation yet says so, plainly.

    Le détail se lit dans la popin partagée, celle des métadonnées et des consignes, et non plus déplié sous la pastille (opérateur, 2026-08-05) : déplié, il repoussait tout
    l'encart vers le bas et se lisait à côté d'une image qu'il faisait fuir. CHAQUE CRITÈRE Y DONNE SA MESURE ET CE QU'ON ATTENDAIT — un verdict sans ses deux valeurs oblige
    à rouvrir l'image pour comprendre ce qui cloche.
    """
    judgement = judgement_for(code)
    if judgement is None:
        return '            <p class="judge-pending">Pas encore évaluée</p>'

    key = f"{identifier}|evaluation"
    rows = []
    for item in judgement.get("criteria", []):
        # Le troisième champ dit au rendu si le critère est tenu : c'est ce qui rend la marque VERTE ou ROUGE. Sans lui la liste était grise d'un bout à l'autre, et le seul
        # signe distinguant un critère raté d'un critère tenu était une croix minuscule — l'opérateur avait la couleur avant, elle lui a manqué tout de suite.
        name = ("✓ " if item.get("passed") else "× ") + item.get("name", "")
        told = item.get("mesure") or item.get("comment") or ""
        wanted = item.get("attendu")
        rows.append([name, told + (f"\nAttendu : {wanted}" if wanted else ""),
                     "met" if item.get("passed") else "failed"])
    panels[key] = {"title": f"Évaluation — {label}", "kind": "facts", "rows": rows}
    words = f"Évaluation — {escape(label)}"

    return f"""            <div class="judge">
              <button type="button" class="judge-toggle panel-open judge--{escape(judgement.get('tone', ''))}"
                      data-panel="{escape(key)}" aria-label="{words}" title="{words}">
                <span class="judge-score">{escape(judgement.get('score'))}/{escape(judgement.get('total'))}</span>
                <span class="judge-verdict">{escape(judgement.get('verdict', ''))}</span>
                <span class="judge-open-word">Rapport</span>
              </button>
            </div>"""



# An eye, drawn inline so the page keeps no external resource: an open-eye outline plus its pupil,
# the plainest glyph that reads as "look at this" without a word. aria-hidden because the button that
# holds it already carries the accessible name — a screen reader must not hear the icon a second time.
EYE_ICON = ('<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false">'
            '<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>')


def enlarge_button_markup(code, label):
    """The eye control: opens the very same full-size viewer a click on the picture opens, but living
    in the encart next to the other buttons rather than over the image — nothing is ever laid over the
    picture itself (see shot_markup()). It borrows the judge-toggle's own look rather than a new one.

    Shown as an EYE GLYPH, not a text label — the operator asked for the icon specifically. The
    accessible name (aria-label) and the hover tooltip (title) both carry the same words a sighted
    reader would otherwise get from a label, so nothing is lost by dropping the text on screen.
    """
    words = f"Agrandir — {escape(label)}"

    return (f'<button type="button" class="judge-toggle enlarge" data-img="{escape(code)}" '
            f'aria-label="{words}" title="{words}">{EYE_ICON}</button>')


def compare_button_markup(identifier, subject):
    """Opens the version-comparison popin for a variant that carries more than one representation.
    Only offered when there is something to compare against — a single-version variant has nothing
    behind its current shot.
    """
    return (f'<button type="button" class="judge-toggle compare-versions" '
            f'data-compare="{escape(identifier)}" '
            f'aria-label="Comparer les versions — {escape(subject)}">Comparer les versions</button>')


def usage_sample_button(sujet_code):
    """The control that opens this sujet's usage sample full size, when it has one.

    A usage sample is not a sprite and never appears among the variants: it is the one image showing
    the sujet's pieces assembled, and it is what the pieces are judged against. It therefore belongs to
    the SUJET's own header, next to its specs, not to any single variant.

    Found on disk rather than in the referentiel, which does not record usage samples: the file is
    named usage-<CODE>.png beside the masters, later versions taking a -vN suffix. The latest version
    is the one offered — an earlier sample has been superseded, exactly like a sprite's own versions.
    """
    samples = list((ASSETS / "poc").glob(f"*/usage-{sujet_code}*.png"))
    if not samples:
        return ""
    # Ordered by VERSION NUMBER, never by name. Sorting these names alphabetically puts the very first sample last — "usage-CH-019.png" outranks
    # "usage-CH-019-v4.png" because a dot sorts after a hyphen — so the page offered the oldest image of the sujet while claiming to show the latest.
    latest = max(samples, key=lambda path: int(path.stem.rsplit("-v", 1)[1]) if "-v" in path.stem else 1)
    relative = str(latest.resolve().relative_to(ASSETS))
    code = resolve_image(relative)
    if code is None:
        return ""
    words = f"Exemple d'usage — {escape(sujet_code)}"
    # The sample's own consigne travels with it, shown beside the picture once it is opened full size — it is the one image every piece is judged against,
    # so what was ASKED of it matters exactly as much as what came back.
    remember_prompt(code, relative)

    return (f'          <div class="encart-tools"><button type="button" class="judge-toggle enlarge usage-sample" '
            f'data-img="{escape(code)}" aria-label="{words}" title="{words}">'
            f'{EYE_ICON} Exemple d\'usage</button></div>')


# The metadata control, drawn rather than typed: the circled-i character renders as a thin, badly aligned glyph that reads as a stray letter next to the
# eye. An inline SVG is the same shape at any size, keeps its stroke weight, and takes the button's own colour through currentColor.
INFO_ICON = ('<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false">'
             '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/>'
             '<path d="M12 11v5.5" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round"/>'
             '<circle cx="12" cy="7.5" r="1.15" fill="currentColor"/></svg>')


def variant_meta_markup(identifier, sujet_code, sujet, type_def, entry, label):
    """Every fact the referentiel holds about ONE variant, opened from its own icon, right beside itself.

    A sujet-level list ("Formes : shape-n, shape-ns, ...") tells the operator which values EXIST but never which one the variant under his eyes carries —
    he has to match a caption against a list, for every variant, every time. The facts belong to the variant, so they are shown on the variant.

    Everything comes from the referentiel and from the representation itself: the variant fields and their values, the sujet's own footprint and height, its layer,
    the file paths and the measures the export took. Nothing is composed for display and nothing is guessed — a field the referentiel does not carry is
    simply absent from the panel.
    """
    rows = [("Sujet", sujet_code), ("Profil", sujet.get("profil", "")),
            ("Calque", type_def.get("layer", "")),
            ("Orientation", ORIENTATION_LABELS.get(entry.get("orientation", "south"),
                                                   entry.get("orientation", "south"))),
            ("Action", entry.get("action", "idle")),
            ("Forme", f"shape-{entry.get('shape', DEFAULT_SHAPE)}"),
            ("Emprise au sol", footprint_label(ground_extent(sujet))),
            ("Couvert", footprint_label(drawn_extent(sujet))
                        + ("" if sujet.get("couvert") else " — le sujet ne déborde pas de son emprise"))]
    if sujet.get("hauteur") is not None:
        height = sujet["hauteur"]
        rows.append(("Hauteur de l'image", f"{height} case{'s' if height != 1 else ''}"))
    for variant_key in type_variant_keys(type_def):
        field = variant_key[:-1]
        value = entry.get(field)
        # A silence is a fact of its own and is shown as one: it is never resolved to the field's default here, which would state something the referentiel
        # does not say (lots-de-variantes.md, on an entry that writes each field it requires and never inherits one).
        rows.append((lead_capital(variant_key), value if value else "non précisé"))
    if entry.get("principale"):
        rows.append(("Rôle", "variante principale du sujet"))

    for index, representation in enumerate(entry.get("representations", [])):
        rank = "courante" if representation.get("statut") == "courante" else f"antérieure {index}"
        rows.append((f"Image ({rank})", representation.get("path", "")))
        if representation.get("maitre"):
            rows.append((f"Maître ({rank})", representation["maitre"]))
        measures = representation.get("mesures") or {}
        anchor = measures.get("anchor_px")
        if anchor:
            rows.append((f"Point de pose ({rank})", f"x {anchor['x']}, y {anchor['y']}"))

    key = f"{identifier}|meta"
    panels[key] = {"title": f"Métadonnées — {label}", "kind": "facts",
                   "rows": [[name, str(value)] for name, value in rows if value != ""]}
    words = f"Métadonnées — {escape(label)}"

    # ICON ONLY, and no wider than the icon (operator, 2026-08-05). The word "Détail" beside it repeated what the icon already says and stretched a control that
    # sits inline among many others. What it means stays available to a reader and to a screen reader alike, through the title and the aria-label.
    return (f'<button type="button" class="judge-toggle icon-only panel-open" data-panel="{escape(key)}" '
            f'aria-label="{words}" title="{words}">{INFO_ICON}</button>')


def sujet_markup(sujet_code, type_name, type_def):
    """One sujet's card: its own specs, drawn from the referentiel alone, and every variant it declares.

    No hand-written libellé or narrative detail lives here any more — the referentiel does not carry
    one (sujets-et-variantes.md: "tu ne recopies aucun libellé"), so none is invented on its behalf.
    """
    sujet = SUJETS[sujet_code]
    variants = sujet["variants"]
    produced = sum(1 for entry in variants if entry.get("representations"))
    footprint = (sujet["emprise"]["columns"], sujet["emprise"]["rows"])

    # What actually distinguishes one variant of THIS sujet from another — asked once here, of the
    # shape, the orientation and every variant field alike, and handed to every slot below
    # (variant_caption()): a field that cannot take more than one value for this sujet has nothing to
    # teach a caption, however meaningful it looks on its own. A fact that never varies still deserves
    # to be said once, not silently dropped — orientation says so below, in the sujet's own specs
    # instead of on every variant.
    varies = {"orientation": field_varies(variants, lambda entry: entry.get("orientation", "south")),
             "shape": field_varies(variants, lambda entry: entry.get("shape", DEFAULT_SHAPE))}
    for variant_key in type_variant_keys(type_def):
        field = variant_key[:-1]
        default = type_def[variant_key]["default"]
        varies[field] = field_varies(
            variants, lambda entry, field=field, default=default: entry.get(field, default))

    # Two ranks, because a card that shows everything shows nothing: the FIRST holds what is looked at while judging a picture — the ground it takes and how
    # far it reaches — and the SECOND everything else, opened from the sujet's own icon like a variant's facts are. The forms and the variant field values
    # left this card altogether: they listed what EXISTS, never what the variant under the eye carries, and each variant now says that for itself.
    specs = [("Emprise au sol", footprint_label(ground_extent(sujet))),
             ("Couvert", footprint_label(drawn_extent(sujet)))]
    detail = [("Profil", sujet.get("profil", "")), ("Calque", type_def["layer"]),
              ("Images", f"{produced} / {len(variants)}")]
    if not varies["orientation"]:
        orientation = variants[0].get("orientation", "south")
        detail.append(("Orientation", ORIENTATION_LABELS.get(orientation, orientation)))
    if sujet.get("hauteur") is not None:
        height = sujet["hauteur"]
        detail.append(("Hauteur de l'image", f"{height} case{'s' if height != 1 else ''}"))
    if not sujet.get("couvert"):
        detail.append(("Débordement", "aucun — le couvert vaut l'emprise"))
    spec_markup = "\n".join(
        f"            <div><dt>{escape(name)}</dt><dd>{escape(value)}</dd></div>"
        for name, value in specs)

    key = f"sujet|{sujet_code}"
    panels[key] = {"title": f"Détail du sujet — {sujet_code}", "kind": "facts",
                   "rows": [[name, str(value)] for name, value in detail if value != ""]}
    words = f"Détail du sujet — {escape(sujet_code)}"
    detail_button = (f'<button type="button" class="judge-toggle panel-open" data-panel="{escape(key)}" '
                     f'aria-label="{words}" title="{words}">{INFO_ICON}</button>')

    label = SUJET_LABELS.get(sujet_code)
    if label is None:
        MISSING_LABELS.append(sujet_code)
        heading = '<span class="missing-label">Libellé manquant</span>'
    else:
        heading = escape(lead_capital(label))

    # UN SUJET ENTIÈREMENT VALIDÉ SE REPLIE. Il n'y a plus rien à en décider : il ne garde que son libellé, sa ref et son image principale, et plusieurs sujets repliés se
    # rangent côte à côte en grille. Ce qui reste à juger occupe la page ; ce qui est acquis prend la place d'une vignette.
    def settled_variant(entry):
        representations = entry.get("representations") or []
        if not representations:
            return False

        return VERDICT_STATUS.get(current_representation(representations).get("verdict")) == "validated"

    settled = all(settled_variant(entry) for entry in ordered_variants(sujet))
    folded = " profile--folded" if settled else ""

    blocks = [f"""      <article class="profile{folded}">
        <header class="profile-head">
          <h3>{heading}</h3>
          <p class="profile-id"><code class="code">{escape(sujet_code)}</code>
            <span class="pname">{escape(sujet['profil'])}</span>{detail_button}{unfold_button(settled, sujet_code)}</p>
          <dl class="specs">
{spec_markup}
          </dl>
{usage_sample_button(sujet_code)}
        </header>"""]
    blocks.append('        <ul class="slots">')
    blocks.extend(slot_markup(sujet_code, sujet, type_name, type_def, entry, varies,
                              principal=entry is main_variant(sujet))
                  for entry in ordered_variants(sujet))
    blocks.append("        </ul>")
    blocks.append("      </article>")

    return "\n".join(blocks)


def unfold_button(settled, sujet_code):
    """The control that folds a sujet away and opens it back up. OFFERED ON EVERY SUJET, without exception.

    Ce que l'état d'un sujet décide n'est PAS l'existence de ce bouton mais seulement la position de départ : replié quand tout est validé, déplié tant qu'il reste à juger.
    N'en donner qu'à ceux qui sont repliés rendait inatteignable ce qui était acquis, et interdisait de ranger ce qu'on venait de finir de regarder.
    """
    words = f"Replier ou déplier le sujet — {escape(sujet_code)}"

    # UN BOUTON ICÔNE, comme les deux autres de cette ligne — c'est ce qui a été demandé, et le remplacer par un mot était une invention de ma part. Le chevron pointe vers
    # ce qui va se passer : vers le bas pour ouvrir, vers le haut pour ranger. Ce qu'il fait se lit au survol, comme pour l'icône d'information à côté.
    return (f'<button type="button" class="profile-unfold" aria-label="{words}" title="{words}" '
            f'aria-expanded="{"false" if settled else "true"}">'
            f'<span class="unfold-word">{"▾" if settled else "▴"}</span></button>')


def slug(text):
    """A safe html id: no accent, no space, nothing that would break aria-labelledby."""
    import unicodedata

    flat = unicodedata.normalize("NFKD", text.lower())
    flat = "".join(character for character in flat if not unicodedata.combining(character))

    return re.sub(r"[^a-z0-9]+", "-", flat).strip("-")


def type_section_markup(type_name, type_def):
    """One section per type that the referentiel actually inscribes at least one sujet under. A type
    with no sujet yet (humain, creature: only sondes stand in for them today) is declared above, in
    TYPES, but earns no empty section here — there is nothing to show, and an empty section would say
    otherwise.
    """
    codes = sorted(code for code, sujet in SUJETS.items() if sujet["type"] == type_name)
    if not codes:
        return None
    anchor = slug(type_name)
    sujets_markup = "\n".join(sujet_markup(code, type_name, type_def) for code in codes)
    variant_count = sum(len(SUJETS[code]["variants"]) for code in codes)

    return f"""    <section class="type" aria-labelledby="type-{anchor}">
      <header class="type-head">
        <h2 id="type-{anchor}">{escape(TYPE_LABELS.get(type_name, type_name))}
          <span class="slug">{escape(type_name)}</span></h2>
        <p class="type-count"><span>{variant_count}</span> image{'s' if variant_count > 1 else ''}</p>
        <p class="type-rule">{escape(lead_capital(type_rule(type_def)))}</p>
      </header>
      <div class="profiles">
{sujets_markup}
      </div>
    </section>"""


DISK_KIND_LABELS = {"poc": "Brute (poc)", "cutout": "Livrable"}
STRAY_CAP = 220  # a stray carries no footprint to size against, so it is capped instead


def stray_shot_markup(full_code, label, path):
    """A stray image, near its own resolution, over a checkerboard, opening full size on click. Works
    for a deliverable and for a master alike: image_size() does not care which catalogue it came from.

    The frame equals the DISPLAY image here — a stray carries no footprint to size a bigger target
    against — but it is, like every other shot, the whole and only click target: nothing is laid over
    the picture (see shot_markup()), so its own score and kind live in stray-body instead. A click or
    the eye still opens full_code untouched, exactly like a modelled variant's slot
    (display_code_for()).
    """
    width, height = image_size(full_code)
    scale = min(1.0, STRAY_CAP / width)
    box = {"width": width * scale, "height": height * scale}
    display_code = display_code_for(path, full_code, box)

    return (f'<div class="shot-frame" role="button" tabindex="0" '
            f'aria-label="{escape(label)} — voir en pleine taille" '
            f'style="width:{box["width"]:.0f}px;height:{box["height"]:.0f}px" '
            f'data-img="{escape(full_code)}">'
            f'<div class="shot" style="{shot_background(display_code, "sprite")}"></div>'
            f'</div>')


def stray_vis_markup(entry):
    """A stray's own picture — same resolve-then-show rule as a modelled variant's slot
    (variant_shot()): a stray found on disk is not guaranteed to already be in THUMBNAILS either, and
    an unreadable file must not take the whole "hors modèle" section down with it.
    """
    if entry["kind"] == "cutout":
        key = resolve_image(entry["path"])
        if key is None:
            return unread_shot_markup(entry["path"], entry["path"],
                                      f"width:{STRAY_CAP}px;height:{STRAY_CAP}px")
        return stray_shot_markup(key, entry["path"], entry["path"])

    # No deliverable exists for this stray either: its master is shown instead, same rule as a
    # modelled variant — nothing on disk stays invisible for lack of an export.
    key = master_entry(entry["path"])
    if key is None:
        return unread_shot_markup(entry["path"], entry["path"],
                                  f"width:{STRAY_CAP}px;height:{STRAY_CAP}px")
    return stray_shot_markup(key, f'{entry["path"]} — maître, pas encore exporté', entry["path"])


def hors_modele_markup():
    """Every disk file the model above could not claim. Never filtered, never hidden.

    This is not a slot: it carries no status, no checkbox, no comment field — the self-check below
    counts those against the model's own registry, and a stray file is not one of its variants.
    """
    if not HORS_MODELE:
        return ""
    items = "\n".join(
        f'          <li class="stray">'
        f'<div class="stray-vis">{stray_vis_markup(entry)}</div>'
        f'<div class="stray-body">'
        f'<code class="code">{escape(DISK_KIND_LABELS[entry["kind"]])}</code>'
        f'<span class="stray-path">{escape(entry["path"])}</span>'
        f'{judge_body_markup("hors-modele-" + entry["path"], thumbnail_key(entry["path"]), entry["path"])}'
        f'</div></li>'
        for entry in HORS_MODELE)
    count = len(HORS_MODELE)

    # Deliberately NOT class="type": the filter script hides any ".type" that holds no ".profile", and
    # this section holds strays, never a profile — it must stay outside that machinery, always shown.
    return f"""    <section class="hors-modele" aria-labelledby="type-hors-modele">
      <header class="type-head">
        <h2 id="type-hors-modele">Hors modèle</h2>
        <p class="type-count"><span>{count}</span> fichier{'s' if count > 1 else ''}</p>
        <p class="type-rule">Présents sur le disque, sous <code>assets/poc/</code> ou
          <code>assets/cutout/</code>, mais qu'aucun profil ni aucune variante du modèle ci-dessus ne
          réclame par son nom : une sonde de capacité, une forme non retenue, une version antérieure,
          une planche de référence. Le modèle n'invente rien, mais il ne cache rien non plus.</p>
      </header>
      <ul class="strays">
{items}
      </ul>
    </section>"""


sections = "\n".join(filter(None, (type_section_markup(name, TYPES[name]) for name in TYPES)))
hors_modele = hors_modele_markup()

# Every registered variant belongs to the park — the referentiel carries no "later, off the park"
# scope of its own. "park_variants" keeps its name only so the self-checks below barely move.
park_variants = registry
counts = {key: sum(1 for entry in park_variants if entry["status"] == key) for key in STATUS}
awaiting = counts["fault"]
sujet_total = len(SUJETS)

status_cells = "\n".join(
    f"""        <li class="track-cell track-cell--{key}">
          <span class="dot" aria-hidden="true">{STATUS[key]['mark']}</span>
          <span class="track-figure">{counts[key]}</span>
          <span class="track-word">{escape(STATUS[key]['label'])}</span>
        </li>""" for key in STATUS_ORDER)

filter_buttons = "\n".join(
    f"""        <button type="button" class="filter" data-filter="{key}" aria-pressed="false">
          <span class="dot" aria-hidden="true">{STATUS[key]['mark']}</span>{escape(STATUS[key]['label'])}
        </button>""" for key in STATUS_ORDER)

# Pure ASCII with \\u escapes, and no literal "<": the data block can neither mojibake nor close its
# own tag, whatever the document's charset turns out to be.
# The viewer is told each image's natural size and the NAME of its single css declaration — never the
# image data, which exists once and only once in the stylesheet.
TILE_CODES = {thumbnail_key(rep["path"])
              for sujet in SUJETS.values() if sujet["type"] == TILE_TYPE
              for entry in sujet["variants"]
              for rep in entry.get("representations", [])
              if rep["path"].startswith("cutout/")}

# Every image actually embedded on the page — deliverables AND the masters shown in their place —
# must be openable in the full-size viewer, so the two catalogues are combined here.
IMAGES = {code: {"token": image_token(code)[len("--img-"):],
                 "width": image_size(code)[0], "height": image_size(code)[1],
                 # A ground material also gets a repeated view, which is where a join would show.
                 # Both figures come from the scale service, never from the page.
                 "tile": code in TILE_CODES,
                 "tilePx": tile_scale.tiles_to_pixels(1),
                 "repeatPx": tile_scale.tiles_to_pixels(6)}
          for code in set(THUMBNAILS) | set(MASTERS)}

PAYLOAD = json.dumps({"labels": LABELS, "actions": [key for key, _ in ACTIONS],
                      "variants": registry, "images": IMAGES, "storageKey": STORAGE_KEY,
                      "comparisons": comparisons, "panels": panels, "prompts": prompts,
                      "reports": reports},
                     ensure_ascii=True).replace("<", "\\u003c")

STYLE = """
:root {
  color-scheme: light dark;
  --ground: #F2F4EF;
  --surface: #FFFFFF;
  --surface-sunk: #EBEEE6;
  --ink: #171B15;
  --ink-soft: #5C6459;
  --ink-faint: #8B9287;
  --line: #D8DDD2;
  --rule: rgba(23, 27, 21, 0.05);
  --key: #A3007A;
  --key-field: rgba(255, 0, 255, 0.055);
  --key-edge: rgba(196, 0, 150, 0.5);
  --st-planned: #6E7669;
  --st-running: #A66300;
  --st-done: #2F7A3B;
  --st-fault: #B3261E;
  --st-validated: #1B5E3A;
  --st-rejected: #8C1D18;
  --warn: #8A5A00;
  --warn-field: rgba(138, 90, 0, 0.09);
  --checker-a: #D7DBD0;
  --checker-b: #F2F4EF;
  --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --ground: #12150F; --surface: #1B1F19; --surface-sunk: #161A14;
    --ink: #E8EDE4; --ink-soft: #9AA494; --ink-faint: #6E7869; --line: #2E342B;
    --rule: rgba(232, 237, 228, 0.045);
    --key: #FF7BDD; --key-field: rgba(255, 0, 255, 0.09); --key-edge: rgba(255, 90, 220, 0.45);
    --st-planned: #8E9887; --st-running: #E5B255; --st-done: #7CC98A; --st-fault: #FF8F84;
    --st-validated: #6FD8A4;
    --st-rejected: #E8776B;
    --warn: #E0B267; --warn-field: rgba(224, 178, 103, 0.12);
    --checker-a: #23271F; --checker-b: #171A14;
  }
}
:root[data-theme="dark"] {
  --ground: #12150F; --surface: #1B1F19; --surface-sunk: #161A14;
  --ink: #E8EDE4; --ink-soft: #9AA494; --ink-faint: #6E7869; --line: #2E342B;
  --rule: rgba(232, 237, 228, 0.045);
  --key: #FF7BDD; --key-field: rgba(255, 0, 255, 0.09); --key-edge: rgba(255, 90, 220, 0.45);
  --st-planned: #8E9887; --st-running: #E5B255; --st-done: #7CC98A; --st-fault: #FF8F84;
  --st-validated: #6FD8A4;
  --st-rejected: #E8776B;
  --warn: #E0B267; --warn-field: rgba(224, 178, 103, 0.12);
  --checker-a: #23271F; --checker-b: #171A14;
}
:root[data-theme="light"] {
  --ground: #F2F4EF; --surface: #FFFFFF; --surface-sunk: #EBEEE6;
  --ink: #171B15; --ink-soft: #5C6459; --ink-faint: #8B9287; --line: #D8DDD2;
  --rule: rgba(23, 27, 21, 0.05);
  --key: #A3007A; --key-field: rgba(255, 0, 255, 0.055); --key-edge: rgba(196, 0, 150, 0.5);
  --st-planned: #6E7669; --st-running: #A66300; --st-done: #2F7A3B; --st-fault: #B3261E;
  --st-validated: #1B5E3A;
  --st-rejected: #8C1D18;
  --warn: #8A5A00; --warn-field: rgba(138, 90, 0, 0.09);
  --checker-a: #D7DBD0; --checker-b: #F2F4EF;
}

body {
  margin: 0;
  background-color: var(--ground);
  /* One case is one metre: the page stands on the world's own grid. */
  background-image:
    repeating-linear-gradient(to right, var(--rule) 0 1px, transparent 1px 44px),
    repeating-linear-gradient(to bottom, var(--rule) 0 1px, transparent 1px 44px);
  color: var(--ink);
  font-family: var(--mono);
  font-size: 15px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}
* { box-sizing: border-box; }
/* The page grows with the screen instead of holding one fixed width: on a wide display it takes the room it needs to show two wide subjects side by side,
   on a small one it takes everything there is. It never goes edge to edge — a ceiling keeps the reading comfortable and the margins deliberate, and the
   running text inside keeps its own narrower measure so nothing is read across the whole width. */
.page { width: min(100%, 1760px); margin: 0 auto; padding: 40px clamp(12px, 3vw, 48px) 132px; }

.masthead { display: flex; flex-direction: column; gap: 20px; }
.eyebrow {
  margin: 0; font-size: 11.5px; letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--ink-faint);
}
.masthead h1 {
  margin: 0; font-size: clamp(29px, 5vw, 42px); line-height: 1.07; font-weight: 700;
  letter-spacing: -0.025em; text-wrap: balance; max-width: 21ch;
}
.standfirst {
  margin: 0; font-family: var(--sans); font-size: 16px; line-height: 1.6;
  color: var(--ink-soft); max-width: 62ch;
}

/* ---- tracking panel ---- */
.track {
  margin-top: 30px; background: var(--surface); border: 1px solid var(--line); border-radius: 3px;
  padding: 18px 18px 20px;
}
.track-head {
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 16px;
  padding-bottom: 14px; border-bottom: 1px solid var(--line);
}
.track-head h2 { margin: 0; font-size: 13px; letter-spacing: 0.13em; text-transform: uppercase; }
.track-total { margin: 0; font-size: 13px; color: var(--ink-soft); font-variant-numeric: tabular-nums; }
.track-total strong { font-size: 19px; color: var(--ink); letter-spacing: -0.02em; }
.track-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(132px, 1fr)); gap: 10px;
  list-style: none; margin: 15px 0 0; padding: 0;
}
.track-cell {
  display: flex; align-items: baseline; gap: 8px; padding: 11px 13px;
  background: var(--surface-sunk); border: 1px solid var(--line); border-radius: 3px;
  border-left-width: 3px;
}
.track-cell--planned { border-left-color: var(--st-planned); }
.track-cell--running { border-left-color: var(--st-running); }
.track-cell--done { border-left-color: var(--st-done); }
.track-cell--fault { border-left-color: var(--st-fault); }
.track-cell--validated { border-left-color: var(--st-validated); }
.track-cell--rejected { border-left-color: var(--st-rejected); }
.track-cell .dot { font-size: 13px; line-height: 1; }
.track-cell--planned .dot { color: var(--st-planned); }
.track-cell--running .dot { color: var(--st-running); }
.track-cell--done .dot { color: var(--st-done); }
.track-cell--fault .dot { color: var(--st-fault); }
.track-cell--validated .dot { color: var(--st-validated); }
.track-cell--rejected .dot { color: var(--st-rejected); }
.track-figure { font-size: 22px; font-weight: 700; font-variant-numeric: tabular-nums; letter-spacing: -0.03em; }
.track-word { font-size: 11.5px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-faint); }
.track-foot {
  margin: 14px 0 0; font-family: var(--sans); font-size: 13.5px; color: var(--ink-soft);
  max-width: 70ch;
}
.track-foot em { font-style: normal; color: var(--ink); font-family: var(--mono); }

/* ---- filter ---- */
.filters {
  display: flex; flex-wrap: wrap; align-items: center; gap: 7px;
  margin-top: 16px; padding-top: 15px; border-top: 1px solid var(--line);
}
.filter-label {
  margin: 0 5px 0 0; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--ink-faint);
}
.filter {
  display: inline-flex; align-items: center; gap: 6px; font-family: var(--mono); font-size: 11.5px;
  letter-spacing: 0.05em; padding: 6px 11px; border-radius: 3px; border: 1px solid var(--line);
  background: var(--surface); color: var(--ink-soft); cursor: pointer;
}
.filter .dot { font-size: 11px; line-height: 1; }
.filter[data-filter="planned"] .dot { color: var(--st-planned); }
.filter[data-filter="running"] .dot { color: var(--st-running); }
.filter[data-filter="done"] .dot { color: var(--st-done); }
.filter[data-filter="fault"] .dot { color: var(--st-fault); }
.filter[data-filter="validated"] .dot { color: var(--st-validated); }
.filter[data-filter="rejected"] .dot { color: var(--st-rejected); }
.filter:hover { border-color: var(--ink-faint); }
.filter.is-on {
  background: var(--ink); border-color: var(--ink); color: var(--ground); font-weight: 700;
}
.filter.is-on .dot { color: var(--ground); }
.filter:focus-visible { outline: 2px solid var(--key); outline-offset: 2px; }
.filter-state {
  margin: 11px 0 0; font-family: var(--sans); font-size: 13px; color: var(--ink-soft);
  min-height: 1.3em;
}
/* The slots and profiles carry their own display, so hiding must be stated louder than they do. */
[hidden] { display: none !important; }

/* ---- recap ---- */
.recap {
  margin-top: 14px; background: var(--surface); border: 1px solid var(--key-edge);
  border-radius: 3px; padding: 12px 18px;
}
.recap-head { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; }
.recap-head h2 { margin: 0; font-size: 13px; letter-spacing: 0.13em; text-transform: uppercase; flex: 1 1 auto; }
/* One short line, never hand-wrapped: it folds on its own at whatever width the page has. */
.recap-intro {
  margin: 4px 0 0; font-family: var(--sans); font-size: 12.5px; color: var(--ink-soft);
}
.recap-text {
  margin: 8px 0 0; padding: 10px 14px; background: var(--surface-sunk); border: 1px solid var(--line);
  border-radius: 3px; font-family: var(--mono); font-size: 12.5px; line-height: 1.65;
  white-space: pre-wrap; overflow-wrap: anywhere; max-height: 320px; overflow-y: auto;
  color: var(--ink);
}
.recap-text[data-empty="true"] { color: var(--ink-faint); }
.recap-text:focus-visible { outline: 2px solid var(--key); outline-offset: 2px; }
.btn {
  font-family: var(--mono); font-size: 12px; letter-spacing: 0.06em; padding: 8px 13px;
  border-radius: 3px; border: 1px solid var(--ink); background: var(--ink); color: var(--ground);
  cursor: pointer;
}
.btn--quiet { background: transparent; color: var(--ink-soft); border-color: var(--line); }
.btn:hover { opacity: 0.86; }
.copy-state { font-size: 12px; color: var(--st-done); flex: 1 1 100%; min-height: 1.2em; margin: 0; }
.copy-state[data-tone="fail"] { color: var(--st-fault); }

/* ---- type sections ---- */
.type { margin-top: 54px; }
.type-head {
  display: grid; grid-template-columns: 1fr auto; align-items: baseline; gap: 4px 18px;
  border-top: 2px solid var(--ink); padding-top: 8px;
}
.type-head h2 { margin: 0; font-size: 21px; font-weight: 700; letter-spacing: -0.01em; }
.type-count {
  margin: 0; font-size: 11.5px; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--ink-faint); font-variant-numeric: tabular-nums;
}
.type-count span { color: var(--ink); font-weight: 700; font-size: 14px; }
.type-rule {
  grid-column: 1 / -1; margin: 0; font-family: var(--sans); font-size: 14px;
  color: var(--ink-soft); max-width: 72ch;
}

/* Les sujets d'un type se rangent en grille : ceux qui restent à juger prennent la ligne entière, ceux qui sont acquis se serrent côte à côte. */
.profiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 8px; align-items: start; }
.profiles > .profile:not(.profile--folded) { grid-column: 1 / -1; }

/* UN SUJET REPLIÉ NE MONTRE QUE CE QU'IL EST : son image principale, son libellé, sa ref. Tout ce qui sert à décider disparaît, puisqu'il n'y a plus rien à décider — et un
   bouton le rouvre, parce que ranger n'est pas fermer. L'image passe à gauche, le texte à sa droite : la carte tient alors sur deux lignes au lieu de quatre. */
.profile--folded { display: flex; align-items: center; gap: 10px; padding: 8px 10px; }
.profile--folded .specs,
.profile--folded .profile-detail,
.profile--folded .slot-body,
.profile--folded .slot:not(.slot--lead) { display: none; }
.profile--folded .profile-head { gap: 2px; order: 2; min-width: 0; }
.profile--folded .slots { order: 1; margin: 0; display: block; flex: 0 0 auto; }
.profile--folded .slot { padding: 0; background: none; border: 0; }
.profile--folded .slot > .slot-vis { float: none; margin: 0; }
.profile--folded h3 { font-size: 15px; }
.profile--folded .profile-id { gap: 6px; }
/* Posé contre l'icône d'information, pas rejeté au bout de la ligne : les deux commandes du sujet se tiennent ensemble, là où on regarde son identité. */
.profile-unfold {
  width: 22px; height: 22px; padding: 0; line-height: 1;
  display: inline-flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 13px;
  border: 1px solid var(--line); border-radius: 2px; background: var(--surface); color: var(--ink); cursor: pointer;
}
.profile-unfold:hover { color: var(--ink); border-color: var(--ink-faint); }

/* ---- profile ---- */
/* RESSERRÉ, PARCE QUE LA PAGE SE PARCOURT. Un type d'un seul sujet et d'une seule image tenait un écran entier, presque vide (opérateur, 2026-08-05) : ce sont les marges
   qui prenaient la place, pas le contenu. Rien n'est retiré, tout est simplement rapproché — la page se lit d'un coup d'œil au lieu de se dérouler. */
.profile {
  margin-top: 12px; background: var(--surface); border: 1px solid var(--line);
  border-radius: 3px; padding: 11px 12px 12px;
}
.profile-head { display: flex; flex-direction: column; gap: 5px; }
.profile-id { margin: 0; display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.code {
  font-size: 13px; font-weight: 700; letter-spacing: 0.05em; padding: 2px 7px;
  background: var(--surface-sunk); border: 1px solid var(--line); border-radius: 2px;
}
.pname { font-size: 12.5px; color: var(--ink-faint); }
/* A sujet the inventory sheets never gave a label to — shown for what it is, not filled in. */
.missing-label { color: var(--warn); font-style: italic; font-weight: 600; }
.profile h3 { margin: 0; font-size: 19px; font-weight: 700; letter-spacing: -0.012em; }
.specs {
  display: flex; flex-wrap: wrap; gap: 4px 20px; margin: 3px 0 0;
  padding: 6px 0 0; border-top: 1px solid var(--line);
}
.specs div { display: flex; align-items: baseline; gap: 8px; }
.specs dt { font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-faint); }
.specs dd { margin: 0; font-size: 13.5px; font-variant-numeric: tabular-nums; }
.profile-detail {
  margin: 12px 0 0; font-family: var(--sans); font-size: 13.5px; color: var(--ink-soft); max-width: 68ch;
}


/* ---- variant slots: dense, because production will fill this page ---- */
.slots {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(292px, 1fr));
  gap: 6px; list-style: none; margin: 8px 0 0; padding: 0;
  /* A column never grows past what its picture needs: left free, four columns of a wide page stretched each slot far beyond its own content. */
  justify-content: start;
}
/* LA VIGNETTE NE PREND PAS UNE COLONNE À ELLE. Posée en flottant, elle laisse le titre venir à côté d'elle — l'alignement que l'opérateur veut garder — puis tout ce qui
   suit reprend TOUTE la largeur sous elle. En colonne, elle réservait sa largeur sur toute la hauteur du bloc et repliait chaque libellé sur trois lignes contre un vide. */
.slot {
  display: block; min-width: 0; padding: 8px 9px;
  background: var(--surface-sunk); border: 1px solid var(--line); border-radius: 3px;
}
.slot::after { content: ""; display: block; clear: both; }
.slot > .slot-vis { float: left; margin: 0 8px 4px 0; }
/* A footprint too wide for a column takes the whole row rather than being shrunk out of scale. */
/* A wide subject takes two columns, not the whole row: at the scale this page draws, two of them sit side by side comfortably, and giving each a full row
   left most of it empty next to a picture that had stopped growing long before. It falls back to the whole row only when the grid itself has but one. */
.slot--wide { grid-column: span 2; }
/* Une emprise large occupe déjà toute la largeur : sa vignette ne flotte pas, elle se pose au-dessus du texte comme avant. */
.slot--wide > .slot-vis { float: none; margin: 0 0 6px; }
@media (max-width: 640px) { .slot--wide { grid-column: 1 / -1; } }
.slot-vis { flex: none; max-width: 100%; overflow-x: auto; display: flex; flex-wrap: wrap; gap: 6px; }
/* En bloc, et non en colonne flex : un enfant de flex ne coule pas autour d'un flottant, et la vignette redeviendrait une colonne. Les écarts entre lignes sont donc portés
   par les lignes elles-mêmes. */
.slot-body { min-width: 0; display: block; }
.slot-body > * + * { margin-top: 3px; }
.slot-line { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 8px; margin: 0; }
/* An unshot variant is a magenta keying field the exact size of the ground it will cover. */
.frame {
  border-radius: 2px; background: var(--key-field); border: 1.5px dashed var(--key-edge);
  display: flex; align-items: center; justify-content: center;
}
/* A representation the referentiel names but this page could not embed — unreadable or too heavy —
   never the same warning as an unshot variant (above): something exists, it just is not shown here. */
.frame--unread {
  background: var(--warn-field); border: 1.5px dashed var(--warn); color: var(--warn);
  font-size: 10.5px; text-align: center; padding: 4px;
}
/* An écartée representation: the operator's own call, never a chain fault — its own colour, never
   the warning tone above (that one means "this page could not read the file", a different fact). */
.frame--rejected {
  background: var(--surface-sunk); border: 1.5px dashed var(--st-rejected); color: var(--st-rejected);
  font-size: 10.5px; text-align: center; padding: 4px;
}

/* ---- operator verdict: a different opinion from the judge's own score, never the same look ---- */
.verdict { margin: 3px 0 0; }
.verdict-word {
  display: inline-block; padding: 1px 7px 2px; border-radius: 2px; font-size: 10.5px;
  font-weight: 700; letter-spacing: 0.03em;
}
.verdict--validated .verdict-word { background: var(--st-validated); color: var(--ground); }
.verdict--rework .verdict-word { background: var(--st-running); color: var(--ground); }
.verdict--rejected .verdict-word { background: var(--st-rejected); color: var(--ground); }
.verdict-comment { margin: 3px 0 0; font-family: var(--sans); font-size: 11.5px; color: var(--ink-soft); }
/* A master standing in for a missing deliverable is a real picture, but not the one that will end up
   in the game: a warm ring outside the frame keeps it visibly different from a genuine, delivered
   shot at a glance — OUTSIDE, on a positive offset, so it never draws over the picture itself; the
   same fact is also said in words, in shot-tag below, for whoever cannot rely on the colour alone. */
.shot-frame--master { outline: 2px solid var(--warn); outline-offset: 2px; }
.shot-tag { margin: 2px 0 0; font-size: 10.5px; color: var(--warn); font-style: italic; }
.slot-caption { font-size: 12px; font-weight: 700; }
.slot-ref {
  margin: 0; font-size: 10px; line-height: 1.35; color: var(--ink-faint);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.slot--wide .slot-ref, .slot:hover .slot-ref { white-space: normal; overflow-wrap: anywhere; }

/* The click target: at least one tile per side (frame_style), the picture posed on its bottom edge
   inside it — a flat sprite gets a real target instead of the sliver of its own drawn pixels. Nothing
   else lives inside this element: no button, no badge, nothing that could sit on the picture — every
   other fact about the shot is in the encart's text area next to it, never on top of it. A plain div
   rather than a native <button> so its own background can hold the checkerboard and the image behind
   it; role="button" and tabindex give it the same keyboard reach a real button would. */
.shot-frame {
  position: relative; display: flex; align-items: flex-end; justify-content: center;
  cursor: zoom-in; border-radius: 2px; max-width: 100%; flex: none;
}
.shot-frame:focus-visible { outline: 2px solid var(--key); outline-offset: 2px; }
.shot {
  background-repeat: no-repeat; background-position: center bottom; background-size: contain;
  border-radius: 2px; max-width: 100%; width: 100%; height: 100%;
}

.status { display: flex; align-items: center; gap: 5px; margin: 0; }
/* The word always travels with the mark, so a missing glyph can never cost the reader the state. */
.dot { font-family: "Segoe UI Symbol", "Apple Symbols", "Noto Sans Symbols 2", var(--mono); }
.status .dot { font-size: 11px; line-height: 1; }
.status-word { font-size: 10px; letter-spacing: 0.07em; text-transform: uppercase; }
.status--planned .dot, .status--planned .status-word { color: var(--st-planned); }
.status--running .dot, .status--running .status-word { color: var(--st-running); }
.status--done .dot, .status--done .status-word { color: var(--st-done); }
.status--fault .dot, .status--fault .status-word { color: var(--st-fault); }
.status--validated .dot, .status--validated .status-word { color: var(--st-validated); }
.status--rejected .dot, .status--rejected .status-word { color: var(--st-rejected); }
.status--pill {
  display: inline-flex; padding: 1px 6px 2px; border-radius: 2px; border: 1px solid var(--line);
  background: var(--surface);
}

.actions { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 3px; }
/* The label is positioned so the hidden box cannot escape to the corner of the page. */
.act { display: inline-flex; position: relative; }
.act input {
  position: absolute; inset: 0; width: 1px; height: 1px; opacity: 0; margin: 0;
  clip-path: inset(50%); overflow: hidden;
}
.act span, .act-note {
  display: inline-block; font-family: var(--mono); font-size: 10px; letter-spacing: 0.03em;
  padding: 3px 6px; border: 1px solid var(--line); border-radius: 2px; background: var(--surface);
  color: var(--ink-soft); cursor: pointer; user-select: none;
}
.act input:checked + span {
  background: var(--key-field); border-color: var(--key-edge); color: var(--key); font-weight: 700;
}
.act input:focus-visible + span, .act-note:focus-visible { outline: 2px solid var(--key); outline-offset: 2px; }
/* DEUX ÉTATS, DEUX SIGNES, ET SURTOUT PAS LE MÊME. Rose plein : il y a un commentaire écrit là-dessous. Simple cadre marqué : le champ est ouvert, et c'est tout. Les deux
   partageaient la même couleur, si bien qu'un champ vidé mais resté ouvert continuait d'annoncer un texte qui n'existait plus. */
.act-note[data-filled="true"] {
  background: var(--key-field); border-color: var(--key-edge); color: var(--key);
}
.act-note[aria-expanded="true"][data-filled="false"] { border-color: var(--ink-faint); color: var(--ink); }
/* Tools that live IN the encart, next to the report — never over the picture. */
.encart-tools { display: flex; flex-wrap: wrap; gap: 4px; margin: 3px 0 0; }
/* A comment is a real text area, not a one-line field: it grows with what is written, up to four
   lines, and scrolls past that (see growNote() — the ceiling is computed there from this very
   line-height, so changing it here is enough). resize is off because the height is driven by the
   content, and a dragged handle would fight it. */
/* Le champ s'ouvre sur deux lignes, et il grandit avec ce qu'on y écrit jusqu'à quatre lignes, où il s'arrête et défile. Sa hauteur est
   posée en JS (voir fitNote) parce qu'elle dépend du texte réellement replié, que le CSS ne connaît pas. Il ne se redimensionne pas à la main : sa hauteur dit ce qu'il
   contient, et une poignée laisserait croire le contraire. */
.note {
  width: 100%; box-sizing: border-box; font-family: var(--mono); font-size: 11px; line-height: 1.45; padding: 4px 6px;
  border: 1px solid var(--line); border-radius: 2px; background: var(--surface); color: var(--ink);
  display: block; resize: none; overflow-y: auto;
}
/* The enlarged view holds the picture and, beside it, the consigne that produced it — side by side because they are only useful together. The text column
   is fixed and scrolls on its own, so a long consigne never shrinks the picture; below 900px the two stack, the picture staying first. */
.viewer-with-prompt { display: flex; align-items: flex-start; gap: 18px; }
/* The picture yields, the text does not: a consigne is read line by line and a narrow column makes it unreadable, while an image stays judgeable smaller.
   The stage therefore shrinks freely (min-width 0 plus a max-width on the image itself) and the text column keeps a fixed, generous width. */
.viewer-stage { display: flex; flex-direction: column; gap: 12px; min-width: 0; flex: 1 1 auto; }
/* The side column holds what accounts for the picture: what was asked, then how it was obtained. Each block scrolls on its own and copies on its own —
   they are pasted into different places and are never wanted stuck together. */
.viewer-side {
  flex: 0 0 min(46vw, 760px); display: flex; flex-direction: column; gap: 10px;
  max-height: min(80vh, 940px);
}
/* Each block takes the room its content needs and no more, and shares what is left with its neighbour: fold the consigne away and the report grows into
   the space it frees, rather than leaving a hole under it. */
.viewer-block {
  display: flex; flex-direction: column; gap: 6px; min-height: 0; flex: 1 1 auto;
  padding: 12px 14px; border: 1px solid var(--line); border-radius: 3px;
  background: var(--surface-sunk, var(--surface));
}
.viewer-block--folded { flex: 0 0 auto; }
.viewer-block .panel-text { overflow: auto; min-height: 0; }
/* Folded, a block keeps its head and gives all the room to the one below it. The consigne starts folded: the report already carries it in full, and what is
   read first is how the image was obtained, not what was asked for it. */
.viewer-block--folded .panel-text { display: none; }
.viewer-block-head { display: flex; align-items: center; gap: 10px; }
.viewer-block-title { margin: 0; font-size: 11px; font-weight: 700; color: var(--ink-soft); flex: 1 1 auto; }
@media (max-width: 900px) {
  .viewer-with-prompt { flex-direction: column; }
  .viewer-side { flex: 1 1 auto; max-width: 100%; }
}

/* The shared popin's own body — the frame around it is the comparison popin's, reused rather than copied so the two can never drift apart in look. */
.panel-body { padding: 14px 16px; overflow: auto; max-height: min(72vh, 900px); }
.panel-facts { margin: 0; }
/* Un critère tenu et un critère raté se distinguent à la couleur avant de se lire : c'est ce qui permet de voir en un coup d'œil ce qui cloche, sans parcourir la liste. */
/* Écrit avec la même portée que `.specs dt`, qui grise tous les intitulés : sans ça la couleur du verdict était annulée par lui et la liste restait uniformément terne. */
.specs dt.fact--met { color: var(--st-validated); }
.specs dt.fact--failed { color: var(--st-fault); }
.panel-facts dd { white-space: pre-line; }
/* A consigne is shown exactly as it was sent: monospaced, its own line breaks kept, long lines wrapped rather than cut off out of sight. */
.panel-text {
  margin: 0; font-family: var(--mono); font-size: 12px; line-height: 1.6; color: var(--ink);
  white-space: pre-wrap; word-break: break-word;
}

/* The principal variant leads its sujet and says so: it is the reference every other one is judged
   against, and it must be told apart at a glance, not hunted for in the list. */
/* No special border: the "Principale" mark and its place at the head of the list say it already, and a second signal on the frame was noise. */
.lead-mark {
  font-family: var(--sans); font-size: 10px; letter-spacing: 0.04em; text-transform: uppercase;
  color: var(--key); border: 1px solid var(--key); border-radius: 2px; padding: 1px 5px;
}
/* Le bouton d'effacement se pose CONTRE le champ, à sa droite, et non dedans : il lui est rattaché sans lui prendre de place sur son texte. Une croix suffit à le dire ; une
   flèche de retour la remplace quand le texte effacé est encore récupérable. */
.slot-more { margin-top: 4px; display: flex; align-items: flex-start; gap: 4px; }
.slot-more .note { flex: 1 1 auto; }
.note-clear {
  flex: 0 0 auto; width: 18px; height: 18px; padding: 0; line-height: 1;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 13px;
  border: 1px solid var(--line); border-radius: 2px; background: var(--surface); color: var(--ink-soft); cursor: pointer;
}
.note-clear:hover { color: var(--ink); border-color: var(--ink-faint); }
.note-clear[hidden] { display: none; }
.note::placeholder { color: var(--ink-faint); }
.note:focus-visible { outline: 2px solid var(--key); outline-offset: 1px; }
/* Une image sur laquelle un verdict est coché ne s'entoure plus de rose : le bouton coché le dit déjà, en couleur, à trois centimètres de là. Le cadre teinté ajoutait un
   second signal pour le même fait, et laissait croire à un état particulier de l'image elle-même. */
.trial[data-marked="true"] { border-color: var(--key-edge); }

/* ---- judgement: score always visible, the criterion-by-criterion detail folds behind it ---- */
.judge-pending { margin: 2px 0 0; font-size: 10.5px; color: var(--ink-faint); font-style: italic; }
.judge-toggle {
  display: inline-flex; align-items: center; gap: 6px; margin-top: 2px; padding: 3px 7px;
  font-family: var(--mono); font-size: 10.5px; border: 1px solid var(--line); border-radius: 2px;
  background: var(--surface); color: var(--ink); cursor: pointer;
}
/* The technical name stays visible beside its human title, small and quiet: it is what every file, ref and referentiel entry is keyed on, so hiding it
   forces a translation back and forth at every reading. Same treatment as a sujet's own profile slug, which already sits next to its code. */
.slug {
  font-family: var(--mono); font-size: 11px; font-weight: 400; letter-spacing: 0; color: var(--ink-faint);
  margin-left: 8px; vertical-align: middle;
}

/* A drawn icon keeps the exact size it declares and never inherits the line box of the text beside it — without this it sits low and looks clipped. */
.judge-toggle svg { display: block; flex: 0 0 auto; }
/* An icon button is exactly as wide as its icon: no word to make room for, so no room is made. The padding is even on all four sides, which is what makes it
   read as a square control among the worded ones rather than as a button whose label failed to load. */
.judge-toggle.icon-only { gap: 0; padding: 4px; width: fit-content; align-self: start; justify-self: start; }
/* La pastille prend la couleur de son verdict, et rien de plus : une bordure et le chiffre. Pas de fond teinté, pas de mot — la page compte déjà assez de couleurs à elle. */
.judge--met { border-color: var(--st-validated); }
.judge--met .judge-score, .judge--met .judge-verdict { color: var(--st-validated); }
.judge--warn { border-color: var(--warn); }
.judge--warn .judge-score { color: var(--warn); }
.judge--failed { border-color: var(--st-fault); }
.judge--failed .judge-score { color: var(--st-fault); }
.judge-score { font-weight: 700; font-variant-numeric: tabular-nums; }
.judge-verdict { color: var(--ink-soft); }
.judge-open-word { color: var(--ink-faint); text-transform: uppercase; letter-spacing: 0.05em; }
.judge-report {
  margin-top: 4px; padding: 8px; background: var(--surface-sunk); border: 1px solid var(--line);
  border-radius: 2px;
}
.judge-criteria { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 3px; }
.judge-criterion { font-size: 11px; color: var(--ink); }
.judge-criterion .dot { color: var(--st-validated); }
.judge-criterion--failed .dot { color: var(--st-fault); }
.judge-rapport { margin: 8px 0 0; font-family: var(--sans); font-size: 11.5px; color: var(--ink-soft); }

/* ---- full-size viewer: the same declaration as the maquette-scale view ---- */
.viewer { position: fixed; inset: 0; z-index: 40; display: grid; place-items: center; padding: 20px; }
.viewer-back { position: absolute; inset: 0; background: rgba(8, 10, 7, 0.72); }
.viewer-box {
  position: relative; margin: 0; display: flex; flex-direction: column; gap: 10px;
  max-width: 100%; max-height: 100%; padding: 14px; background: var(--surface);
  border: 1px solid var(--line); border-radius: 4px;
}
.viewer-img {
  background-repeat: no-repeat; background-position: center; background-size: contain;
  max-width: 100%; max-height: min(78vh, 900px); align-self: center;
}
.viewer-foot { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.viewer-cap { margin: 0; font-size: 11.5px; color: var(--ink-soft); flex: 1 1 auto; }
.viewer-tile { display: flex; flex-direction: column; gap: 7px; align-items: center; }
.viewer-repeat {
  background-repeat: repeat; border: 1px solid var(--line); border-radius: 2px; max-width: 100%;
}

/* ---- the popin shell, shared by every popin on this page: the version comparison, and the panel that shows a variant's metadata or an image's own
   ---- consigne. The shell is the frame, the backdrop and the head; what goes inside it is each popin's own business, styled under its own name. ---- */
.popin { position: fixed; inset: 0; z-index: 41; display: grid; place-items: center; padding: 20px; }
.popin-back { position: absolute; inset: 0; background: rgba(8, 10, 7, 0.72); }
.popin-box {
  position: relative; margin: 0; display: flex; flex-direction: column; gap: 12px;
  max-width: min(1100px, 100%); max-height: 100%; overflow-y: auto; padding: 16px;
  background: var(--surface); border: 1px solid var(--line); border-radius: 4px;
}
.popin-head { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.popin-title { margin: 0; font-size: 13px; font-weight: 700; flex: 1 1 auto; }
.comparaison-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;
}
.comparaison-item { margin: 0; display: flex; flex-direction: column; gap: 6px; }
.comparaison-pic {
  background-repeat: no-repeat; background-position: center; background-size: contain;
  background-color: var(--surface-sunk); width: 100%; border: 1px solid var(--line); border-radius: 2px;
}
.comparaison-item figcaption { font-size: 10.5px; color: var(--ink-soft); overflow-wrap: anywhere; }
.comparaison-verdict {
  margin: 2px 0 0; font-family: var(--sans); font-size: 11px; font-weight: 600; color: var(--ink);
}
.comparaison-judge {
  margin: 2px 0 0; font-family: var(--mono); font-size: 10.5px; color: var(--ink-soft);
}

/* ---- hors modèle: files the model could not claim, listed and never hidden ---- */
.hors-modele { margin-top: 54px; }
.hors-modele .type-head { border-top-color: var(--ink-faint); }
.strays {
  list-style: none; margin: 16px 0 0; padding: 0;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(292px, 1fr)); gap: 8px;
}
.stray {
  display: flex; align-items: flex-start; gap: 10px; padding: 8px 9px;
  background: var(--surface-sunk); border: 1px solid var(--line); border-radius: 3px;
}
.stray-vis { flex: none; max-width: 100%; overflow-x: auto; }
.stray-body { min-width: 0; display: flex; flex-direction: column; gap: 4px; align-self: center; }
.stray-path { font-size: 11px; color: var(--ink-soft); overflow-wrap: anywhere; }


/* ---- sticky bar ---- */
.bar {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 20;
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px;
  padding: 9px 18px; background: var(--surface); border-top: 1px solid var(--line);
  font-size: 12px;
}
.bar-count { font-variant-numeric: tabular-nums; color: var(--ink-soft); flex: 1 1 auto; }
.bar-count strong { color: var(--ink); font-size: 14px; }
.bar .btn { padding: 6px 11px; }

.colophon {
  margin-top: 54px; padding-top: 20px; border-top: 1px solid var(--line);
  font-family: var(--sans); font-size: 13px; color: var(--ink-faint); max-width: 70ch;
}
.colophon p { margin: 0 0 9px; }
.colophon p:last-child { margin-bottom: 0; }
.colophon code { font-family: var(--mono); }

:where(a, button):focus-visible { outline: 2px solid var(--key); outline-offset: 3px; }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
"""

SCRIPT = """
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("suivi-data").textContent);
  var L = DATA.labels;
  var order = DATA.variants;
  var state = {};
  try {
    var stored = window.localStorage.getItem(DATA.storageKey);
    if (stored) { state = JSON.parse(stored) || {}; }
  } catch (error) { state = {}; }

  function slotNode(id) {
    return document.querySelector('[data-slot="' + id.replace(/"/g, "") + '"]');
  }

  // Which image this slot is showing right now — the representation's own path, version suffix and
  // all. Empty when the variant has no image yet.
  function shotOf(id) {
    var node = slotNode(id);
    return node ? (node.getAttribute("data-shot") || "") : "";
  }

  function entryFor(id) {
    if (!state[id]) { state[id] = { acts: {}, note: "", shot: shotOf(id) }; }
    if (!state[id].acts) { state[id].acts = {}; }
    if (state[id].shot === undefined) { state[id].shot = shotOf(id); }
    return state[id];
  }

  function persist() {
    try { window.localStorage.setItem(DATA.storageKey, JSON.stringify(state)); }
    catch (error) { /* a full or blocked store must not break the page */ }
  }

  // A verdict and a comment are given to an IMAGE, never to a slot. Each stored answer therefore
  // remembers which image it was looking at, and a slot whose image has changed since — a new version
  // produced, a first image landing where there was none — starts blank rather than carrying a
  // judgement passed on something else. Only the slots whose image actually moved are cleared; every
  // other answer stands.
  //
  // An answer stored before this page recorded images at all has no image on it. It is ADOPTED by
  // whatever the slot shows now, never thrown away: erasing a review that was very probably about
  // this same image costs the operator his work, and guards against nothing. The first version of
  // this pass dropped them and wiped a whole review — the tie goes to keeping what was written.
  (function tieAnswersToTheImageTheyJudge() {
    var changed = false;
    Object.keys(state).forEach(function (id) {
      if (!slotNode(id) || !state[id]) { return; }  // a slot that no longer exists is not our business
      var shot = shotOf(id);
      if (state[id].shot === undefined) { state[id].shot = shot; changed = true; return; }
      if (state[id].shot === shot) { return; }
      delete state[id];
      changed = true;
    });
    if (changed) { persist(); }
  }());

  function marked(id) {
    var entry = state[id];
    if (!entry) { return false; }
    if (entry.note && entry.note.trim()) { return true; }
    return DATA.actions.some(function (act) { return entry.acts && entry.acts[act]; });
  }

  function lines() {
    var out = [];
    var total = 0;
    DATA.actions.forEach(function (act) {
      var picked = order.filter(function (entry) {
        var held = state[entry.id];
        return held && held.acts && held.acts[act];
      });
      if (!picked.length) { return; }
      total += picked.length;
      out.push(L.sections[act] + " (" + picked.length + ")");
      picked.forEach(function (entry) {
        out.push("  - " + entry.code + " " + entry.ref);
        out.push("      " + entry.type + " / " + entry.profile + " / " + L.scopes[entry.scope]);
      });
      out.push("");
    });
    var noted = order.filter(function (entry) {
      var held = state[entry.id];
      return held && held.note && held.note.trim();
    });
    if (noted.length) {
      total += noted.length;
      out.push(L.sections.note + " (" + noted.length + ")");
      noted.forEach(function (entry) {
        out.push("  - " + entry.code + " " + entry.ref);
        out.push("      " + state[entry.id].note.trim());
      });
      out.push("");
    }
    return { body: out, total: total };
  }

  var recapText = document.getElementById("recap-text");
  var barCount = document.getElementById("bar-count");
  var copyState = document.getElementById("copy-state");
  var current = "";

  function render() {
    var built = lines();
    if (built.total === 0) {
      current = "";
      recapText.textContent = L.recapEmpty;
      recapText.setAttribute("data-empty", "true");
    } else {
      var head = [L.recapTitle, new Date().toISOString().slice(0, 10), ""];
      current = head.concat(built.body).join("\\n").replace(/\\n+$/, "\\n");
      recapText.textContent = current;
      recapText.setAttribute("data-empty", "false");
    }
    barCount.textContent = "";
    var figure = document.createElement("strong");
    figure.textContent = String(built.total);
    barCount.appendChild(figure);
    var word = built.total > 1 ? L.countedPlural : L.counted;
    barCount.appendChild(document.createTextNode(" " + word + " \\u00b7 " + L.barSummary));
    order.forEach(function (entry) {
      var node = document.querySelector('[data-slot="' + entry.id.replace(/"/g, "") + '"]');
      if (node) { node.setAttribute("data-marked", marked(entry.id) ? "true" : "false"); }
    });
  }

  // The moves offered on one image exclude one another: validate, rework and reject can never both
  // hold for the same image, or the recap would list it twice, under two contradictory verdicts.
  // Checking one clears every other one already set for the same data-id; unchecking the one that is
  // set returns to no verdict at all, on purpose — the operator may want an image back in limbo
  // without being forced to pick a new one.
  function syncActs(id) {
    var acts = entryFor(id).acts;
    Array.prototype.forEach.call(
      document.querySelectorAll('.act input[data-id="' + id.replace(/"/g, "") + '"]'),
      function (box) { box.checked = Boolean(acts[box.getAttribute("data-act")]); });
  }

  Array.prototype.forEach.call(document.querySelectorAll(".act input"), function (box) {
    var id = box.getAttribute("data-id");
    var act = box.getAttribute("data-act");
    var entry = entryFor(id);
    box.checked = Boolean(entry.acts[act]);
    box.addEventListener("change", function () {
      var current = entryFor(id);
      if (box.checked) {
        Object.keys(current.acts).forEach(function (other) { current.acts[other] = false; });
      }
      current.acts[act] = box.checked;
      persist();
      syncActs(id);
      render();
      // TURNING AN IMAGE DOWN MEANS SAYING WHY. Ticking retry or drop opens the comment field and gives it the keyboard: without the reason, the next attempt starts blind,
      // which is exactly what cost three tries on the fir. Validating opens nothing — an accepted image has nothing to justify.
      if (box.checked && (act === "retry" || act === "drop")) {
        var field = document.querySelector('.note[data-note="' + id + '"]');
        var opener = document.querySelector('.act-note[data-open="' + id + '"]');
        var holder = document.querySelector('[data-more="' + id + '"]');
        if (field && holder) {
          holder.hidden = false;
          if (opener) { opener.setAttribute("aria-expanded", "true"); }
          field.focus({preventScroll: true});
        }
      }
    });
  });

  // A comment field is as tall as what it holds: one line to begin with, opening as you type up to FOUR lines, after which it scrolls. The height is measured here rather than
  // set in CSS because it depends on the text once wrapped to the field's own width, which only layout knows. Resetting the height to "auto" before reading scrollHeight is
  // what lets a field that has grown come back down when the text is deleted.
  function fitNote(field) {
    var style = window.getComputedStyle(field);
    var line = parseFloat(style.lineHeight);
    var edges = parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
    var frame = parseFloat(style.paddingTop) + parseFloat(style.paddingBottom) + edges;
    field.style.height = "auto";
    // TWO LINES AT REST, FOUR AT MOST. Measured alone, a single line gives a slot too shallow to write in — it reads as a broken input rather than a field, and the first
    // wrapped word is already hidden. Two lines is a field one can start writing in; four is where it stops growing and scrolls.
    var floor = Math.round(line * 2 + frame);
    var ceiling = Math.round(line * 4 + frame);
    field.style.height = Math.max(floor, Math.min(field.scrollHeight + edges, ceiling)) + "px";
  }

  // RAP — REPRISE AU POINT. This page is republished while it is being read, and a republish reloads it: the text is kept, but the view jumps back to the top and the reader
  // has to find their place again, mid-sentence. So the last place touched is written down with the moment it was touched, and a reload that happens soon after brings it
  // back into view. Only soon after: a page opened an hour later must open at the top, on the whole state of the production, not on the last field of the last session.
  // NEVER BY HEIGHT, ALWAYS BY ELEMENT. A scroll position in pixels is wrong the moment an image is added or removed above it — it lands somewhere else and reads as a bug.
  // What is remembered is WHICH VARIANT was in front of the reader, and the page brings that variant back into view whatever moved around it.
  var RECALL_EDIT_MS = 2000;    // after typing: a sentence is being carried on, so the window is short
  var RECALL_VIEW_MS = 30000;   // after plain scrolling: one was reading, so the window is wider

  var RECALL_KEY = "gatebeast-suivi-derniere-action";

  // The browser restores its own position in pixels, which is precisely what must not happen here: it is taken away so that only the element marker remains.
  if ("scrollRestoration" in window.history) {
    window.history.scrollRestoration = "manual";
  }

  function rememberPlace(id, kind) {
    try {
      window.localStorage.setItem(RECALL_KEY, JSON.stringify({id: id, at: Date.now(), kind: kind || "edit"}));
    } catch (error) {
      // An unavailable store costs nothing but this automatic return: none of what is typed depends on it.
    }
  }

  // What is in front of the eyes: the first variant whose top edge shows in the window. It is the closest thing to what the reader would say themselves — "I was at that one"
  // — and it depends on no height at all.
  var watching = null;
  window.addEventListener("scroll", function () {
    if (watching) { return; }
    watching = window.setTimeout(function () {
      watching = null;
      var slots = document.querySelectorAll("[data-id]");
      for (var index = 0; index < slots.length; index++) {
        var box = slots[index].getBoundingClientRect();
        if (box.top >= 0 && box.top < window.innerHeight) {
          rememberPlace(slots[index].getAttribute("data-id"), "view");
          return;
        }
      }
    }, 200);
  }, {passive: true});

  function returnToPlace() {
    var kept = null;
    try {
      kept = JSON.parse(window.localStorage.getItem(RECALL_KEY));
    } catch (error) {
      return;
    }
    var window_ms = kept && kept.kind === "view" ? RECALL_VIEW_MS : RECALL_EDIT_MS;
    if (!kept || !kept.id || Date.now() - kept.at > window_ms) {
      return;
    }
    var field = document.querySelector('.note[data-note="' + kept.id + '"]');
    var anchor = field || document.querySelector('[data-id="' + kept.id + '"]');
    if (!anchor) {
      return;
    }
    anchor.scrollIntoView({block: "center"});
    if (field) {
      // The field takes the keyboard back too, with the caret at the end of the text: the sentence carries on where it stopped, without one more click.
      field.focus({preventScroll: true});
      field.setSelectionRange(field.value.length, field.value.length);
    }
  }

  Array.prototype.forEach.call(document.querySelectorAll(".note"), function (field) {
    var id = field.getAttribute("data-note");
    var entry = entryFor(id);
    field.value = entry.note || "";
    fitNote(field);

    // CLEARING PUTS AWAY, IT DOES NOT DESTROY. A comment is cleared in one click, but the text stays within reach: the button turns into its restore wording and gives the
    // text back exactly as it was, until something else is typed. Without that, clearing hand-typed lines is a move nobody dares make, and the field stays cluttered.
    var clear = document.querySelector('.note-clear[data-clear="' + id + '"]');
    var stashed = null;

    function showClear() {
      clear.hidden = !field.value.trim() && stashed === null;
      clear.textContent = stashed === null ? "×" : "↺";
      clear.title = stashed === null ? L.noteClear : L.noteRestore;
    }

    // ONE WAY ONLY to record what the field holds, whichever hand changed it — the keyboard or the clear button. Two parallel paths is how a marker stays lit on a field that
    // has just been emptied, which is exactly what happened.
    function applyNote() {
      fitNote(field);
      entryFor(id).note = field.value;
      persist();
      render();
      markNote(id);
      showClear();
    }

    clear.addEventListener("click", function () {
      if (stashed === null) {
        stashed = field.value;
        field.value = "";
      } else {
        field.value = stashed;
        stashed = null;
      }
      applyNote();
    });

    field.addEventListener("focus", function () { fitNote(field); rememberPlace(id); });
    field.addEventListener("input", function () {
      rememberPlace(id);
      stashed = null;
      applyNote();
    });
    showClear();
  });

  // A settled sujet is folded away; this opens it back up, and folds it again. Nothing is lost either way — the fold is a tidy-up, never a closure.
  Array.prototype.forEach.call(document.querySelectorAll(".profile-unfold"), function (button) {
    button.addEventListener("click", function () {
      var card = button.closest(".profile");
      var folded = card.classList.toggle("profile--folded");
      button.setAttribute("aria-expanded", folded ? "false" : "true");
      // The chevron points at what is about to happen. It carries no wording to translate — what the button does is read from its tooltip.
      button.querySelector(".unfold-word").textContent = folded ? "▾" : "▴";
    });
  });

  // THREE TIMES, AND ALL THREE ARE NEEDED. The page embeds every one of its images: until they have their height, an element brought back into view ends up somewhere else
  // as soon as those above it unfold. So the marker is honoured at once, then again once the images have loaded, then once more shortly after — the last two cost nothing
  // when there is nothing left to correct, and without them the return kept missing its target.
  returnToPlace();
  window.addEventListener("load", function () {
    returnToPlace();
    window.setTimeout(returnToPlace, 250);
  });

  function announce(message, tone) {
    copyState.textContent = message;
    copyState.setAttribute("data-tone", tone);
    window.setTimeout(function () { copyState.textContent = ""; }, 4000);
  }

  function copy() {
    var text = current || recapText.textContent;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        announce(L.copied, "ok");
      }, function () { fallback(text); });
    } else { fallback(text); }
  }

  function fallback(text) {
    var holder = document.createElement("textarea");
    holder.value = text;
    holder.setAttribute("readonly", "readonly");
    holder.style.position = "fixed";
    holder.style.opacity = "0";
    document.body.appendChild(holder);
    holder.select();
    var done = false;
    try { done = document.execCommand("copy"); } catch (error) { done = false; }
    document.body.removeChild(holder);
    announce(done ? L.copied : L.copyFailed, done ? "ok" : "fail");
  }

  Array.prototype.forEach.call(document.querySelectorAll("[data-copy]"), function (button) {
    button.addEventListener("click", copy);
  });

  // A block folds away without leaving the view: its head stays, and the room goes to the block below.
  Array.prototype.forEach.call(document.querySelectorAll("[data-fold]"), function (button) {
    var block = document.getElementById(button.getAttribute("data-fold"));
    if (!block) { return; }
    button.addEventListener("click", function () {
      var folded = block.classList.toggle("viewer-block--folded");
      button.textContent = folded ? L.unfold : L.fold;
      button.setAttribute("aria-expanded", folded ? "false" : "true");
    });
  });

  // Each block of the enlarged view copies on its own — a consigne is pasted into a tool, a report into
  // a message, and neither is ever wanted with the other stuck to it.
  Array.prototype.forEach.call(document.querySelectorAll("[data-copy-block]"), function (button) {
    button.addEventListener("click", function () {
      var source = document.getElementById(button.getAttribute("data-copy-block"));
      if (!source) { return; }
      var text = source.textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { announce(L.copied, "ok"); },
                                                  function () { fallback(text); });
      } else { fallback(text); }
    });
  });

  // ---- comment fields fold away, and announce themselves when they hold something ----
  function markNote(id) {
    var button = document.querySelector('[data-open="' + id + '"]');
    if (!button) { return; }
    var held = state[id];
    var filled = Boolean(held && held.note && held.note.trim());
    button.setAttribute("data-filled", filled ? "true" : "false");
  }

  Array.prototype.forEach.call(document.querySelectorAll(".act-note"), function (button) {
    var id = button.getAttribute("data-open");
    var panel = document.querySelector('[data-more="' + id + '"]');
    if (state[id] && state[id].note) { panel.hidden = false; button.setAttribute("aria-expanded", "true"); }
    markNote(id);
    button.addEventListener("click", function () {
      panel.hidden = !panel.hidden;
      button.setAttribute("aria-expanded", panel.hidden ? "false" : "true");
      if (!panel.hidden) { panel.querySelector(".note").focus(); }
    });
  });

  // ---- the shared popin: a variant's metadata, an image's frozen consigne. It opens OVER the page, like the viewer and the comparison do, and never
  // ---- inside the flow: an inline fold shoves every slot below it out of place, and reading a long text squeezed beside a sprite is unusable.
  var panelBox = document.getElementById("panel");
  var panelTitle = document.getElementById("panel-title");
  var panelBody = document.getElementById("panel-body");
  var lastPanelOpener = null;

  function openPanel(button) {
    var entry = DATA.panels[button.getAttribute("data-panel")];
    if (!entry) { return; }
    lastPanelOpener = button;
    panelTitle.textContent = entry.title;
    panelBody.textContent = "";
    if (entry.kind === "text") {
      var block = document.createElement("pre");
      block.className = "panel-text";
      block.textContent = entry.text;  // textContent, never innerHTML: the consigne is text, not markup
      panelBody.appendChild(block);
    } else {
      var list = document.createElement("dl");
      list.className = "specs panel-facts";
      entry.rows.forEach(function (row) {
        var pair = document.createElement("div");
        var name = document.createElement("dt");
        name.textContent = row[0];
        // A row may say whether it stands or fails; that is what colours it. Rows that say nothing stay neutral, which is every plain fact panel.
        if (row[2]) { name.className = "fact--" + row[2]; }
        var value = document.createElement("dd");
        value.textContent = row[1];
        pair.appendChild(name);
        pair.appendChild(value);
        list.appendChild(pair);
      });
      panelBody.appendChild(list);
    }
    panelBox.hidden = false;
    document.getElementById("panel-close").focus();
  }

  function closePanel() {
    panelBox.hidden = true;
    if (lastPanelOpener) { lastPanelOpener.focus(); }
  }

  Array.prototype.forEach.call(document.querySelectorAll(".panel-open"), function (button) {
    button.addEventListener("click", function () { openPanel(button); });
  });
  Array.prototype.forEach.call(document.querySelectorAll("[data-close-panel]"), function (node) {
    node.addEventListener("click", closePanel);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !panelBox.hidden) { closePanel(); }
  });

  // ---- judgement report: folded by default, no state kept — the file behind it can change any time
  // ---- a judging agent runs again, so nothing here is worth remembering across a reload. Selected by
  // ---- data-open specifically: the eye and compare-versions buttons borrow this class for looks only.
  Array.prototype.forEach.call(document.querySelectorAll(".judge-toggle[data-open]"), function (button) {
    var id = button.getAttribute("data-open");
    var panel = document.querySelector('[data-report="' + id + '"]');
    button.addEventListener("click", function () {
      panel.hidden = !panel.hidden;
      button.setAttribute("aria-expanded", panel.hidden ? "false" : "true");
    });
  });

  // ---- full-size viewer. It points at the SAME css declaration the small view uses, so the ----
  // ---- image is never embedded a second time. ----
  var viewer = document.getElementById("viewer");
  var viewerImage = document.getElementById("viewer-img");
  var viewerCaption = document.getElementById("viewer-cap");
  var viewerRepeat = document.getElementById("viewer-repeat");
  var viewerRepeatBlock = document.getElementById("viewer-repeat-block");
  var viewerPrompt = document.getElementById("viewer-prompt");
  var viewerPromptText = document.getElementById("viewer-prompt-text");
  var viewerReport = document.getElementById("viewer-report");
  var viewerReportText = document.getElementById("viewer-report-text");
  var lastOpener = null;

  function openViewer(node) {
    var code = node.getAttribute("data-img");
    var size = DATA.images[code];
    if (!size) { return; }
    lastOpener = node;
    viewerImage.style.backgroundImage = "var(--img-" + size.token + ")";
    viewerImage.style.width = size.width + "px";
    viewerImage.style.height = size.height + "px";
    viewerImage.setAttribute("aria-label", code);
    viewerCaption.textContent = code + " " + L.viewerFull;
    // The consigne that produced this very image, shown BESIDE it in the enlarged view — the two are
    // read together or not at all: only their pairing says whether the consigne or the generator was
    // at fault. Absent for an image whose consigne was never frozen; the column then simply goes away.
    var written = DATA.prompts[code];
    viewerPromptText.textContent = written || "";
    viewerPrompt.hidden = !written;
    // And how it was obtained, under it: the model, the session to reopen, the timings, the measures.
    var account = DATA.reports[code];
    viewerReportText.textContent = account || "";
    viewerReport.hidden = !account;
    // A ground material also gets a repeated view at maquette scale: that is where a join shows,
    // and it is the only place the page repeats anything.
    if (size.tile) {
      viewerRepeat.style.backgroundImage = "var(--img-" + size.token + ")";
      viewerRepeat.style.backgroundSize = size.tilePx + "px " + size.tilePx + "px";
      viewerRepeat.style.width = size.repeatPx + "px";
      viewerRepeat.style.height = size.repeatPx + "px";
      viewerRepeat.setAttribute("aria-label", code + " " + L.viewerRepeat);
      viewerRepeatBlock.hidden = false;
    } else {
      viewerRepeatBlock.hidden = true;
    }
    viewer.hidden = false;
    document.getElementById("viewer-close").focus();
  }

  function closeViewer() {
    viewer.hidden = true;
    if (lastOpener) { lastOpener.focus(); }
  }

  // Two ways to open the same viewer on the same declaration: a click on the picture itself, and the
  // eye button living in the encart (see enlarge_button_markup() in build.py). Nothing is ever laid
  // over the picture, so the button lives beside it, never on top of it.
  // The frame is a div, not a native <button>, so its own keyboard activation (Enter and Space) is
  // handled here explicitly; the eye button is a real <button> and needs none of that.
  Array.prototype.forEach.call(document.querySelectorAll(".shot-frame"), function (node) {
    node.addEventListener("click", function () { openViewer(node); });
    node.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " " || event.key === "Spacebar") {
        event.preventDefault();
        openViewer(node);
      }
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll(".enlarge"), function (node) {
    node.addEventListener("click", function () { openViewer(node); });
  });
  Array.prototype.forEach.call(document.querySelectorAll("[data-close]"), function (node) {
    node.addEventListener("click", closeViewer);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !viewer.hidden) { closeViewer(); }
  });

  // ---- version comparison popin: the current representation next to up to three earlier attempts,
  // ---- each shown whole (never cropped, never scored) so the operator can tell which one to keep.
  var comparaison = document.getElementById("comparaison");
  var comparaisonTitle = document.getElementById("comparaison-title");
  var comparaisonGrid = document.getElementById("comparaison-grid");
  var lastComparaisonOpener = null;

  function comparaisonItem(record, isCurrent) {
    var size = DATA.images[record.code];
    var figure = document.createElement("figure");
    figure.className = "comparaison-item";
    var picture = document.createElement("div");
    picture.className = "comparaison-pic";
    if (size) {
      picture.style.backgroundImage = "var(--img-" + size.token + ")";
      picture.style.aspectRatio = size.width + " / " + size.height;
    }
    figure.appendChild(picture);
    var caption = document.createElement("figcaption");
    caption.textContent = (isCurrent ? L.compareCurrent : L.comparePrevious) + " \\u2014 " + record.path;
    figure.appendChild(caption);
    // The operator's own verdict travels with its own version here too — a different opinion from
    // the judge's score, shown nowhere near it, so a reader can never mistake one for the other.
    if (record.verdict) {
      var verdict = document.createElement("p");
      verdict.className = "comparaison-verdict";
      verdict.textContent = record.comment ? record.verdict + " \\u2014 " + record.comment : record.verdict;
      figure.appendChild(verdict);
    }
    // A judgement follows the image, never the variant: this exact file's own report, whether it is
    // the current picture or one already superseded — kept apart from the operator's verdict above,
    // a different opinion from a different source.
    if (record.judge) {
      var judge = document.createElement("p");
      judge.className = "comparaison-judge";
      judge.textContent = record.judge;
      figure.appendChild(judge);
    }
    return figure;
  }

  function openComparaison(node) {
    var entry = DATA.comparisons[node.getAttribute("data-compare")];
    if (!entry) { return; }
    lastComparaisonOpener = node;
    comparaisonTitle.textContent = entry.subject;
    comparaisonGrid.textContent = "";
    comparaisonGrid.appendChild(comparaisonItem(entry.current, true));
    entry.previous.forEach(function (record) {
      comparaisonGrid.appendChild(comparaisonItem(record, false));
    });
    comparaison.hidden = false;
    document.getElementById("comparaison-close").focus();
  }

  function closeComparaison() {
    comparaison.hidden = true;
    if (lastComparaisonOpener) { lastComparaisonOpener.focus(); }
  }

  Array.prototype.forEach.call(document.querySelectorAll(".compare-versions"), function (button) {
    button.addEventListener("click", function () { openComparaison(button); });
  });
  Array.prototype.forEach.call(document.querySelectorAll("[data-close-comparaison]"), function (node) {
    node.addEventListener("click", closeComparaison);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !comparaison.hidden) { closeComparaison(); }
  });

  // ---- filter by production state. The panel counters sit outside it and never move. ----
  var filterState = document.getElementById("filter-state");
  var filterButtons = document.querySelectorAll(".filter");

  function each(nodes, work) { Array.prototype.forEach.call(nodes, work); }

  function visible(node, selector) {
    var found = node.querySelectorAll(selector);
    for (var position = 0; position < found.length; position += 1) {
      if (!found[position].hidden) { return true; }
    }
    return false;
  }

  function applyFilter(which) {
    var shown = 0;
    each(document.querySelectorAll("[data-status]"), function (unit) {
      var keep = which === "all" || unit.getAttribute("data-status") === which;
      unit.hidden = !keep;
      if (keep) { shown += 1; }
    });
    each(document.querySelectorAll(".profile"), function (profile) {
      profile.hidden = !visible(profile, "[data-status]");
    });
    each(document.querySelectorAll(".type"), function (type) {
      type.hidden = !visible(type, ".profile");
    });

    each(filterButtons, function (button) {
      var on = button.getAttribute("data-filter") === which;
      button.classList.toggle("is-on", on);
      button.setAttribute("aria-pressed", on ? "true" : "false");
    });
    var word = shown > 1 ? L.filterMany : L.filterOne;
    filterState.textContent = shown + " " + word
      + (which === "all" ? " \\u2014 " + L.filterAllSuffix : "");
  }

  each(filterButtons, function (button) {
    button.addEventListener("click", function () {
      applyFilter(button.getAttribute("data-filter"));
    });
  });

  document.getElementById("reset").addEventListener("click", function () {
    // A sandboxed frame may refuse confirm(); a refusal must not make the button dead.
    var agreed = true;
    try { if (window.confirm) { agreed = window.confirm(L.resetConfirm); } }
    catch (error) { agreed = true; }
    if (!agreed) { return; }
    state = {};
    persist();
    Array.prototype.forEach.call(document.querySelectorAll(".act input"), function (box) {
      box.checked = false;
    });
    Array.prototype.forEach.call(document.querySelectorAll(".note"), function (field) {
      field.value = "";
      markNote(field.getAttribute("data-note"));
    });
    render();
  });

  render();
  applyFilter("all");
})();
"""

page = f"""<title>Suivi des sprites</title>
<style>{STYLE}</style>
<style>
/* Each image's bytes appear exactly once in this page. The maquette-scale views and the full-size
   viewer all point at these declarations, so nothing is ever embedded twice. */
:root {{
{image_declarations()}
}}
</style>
<main class="page">
  <header class="masthead">
    <p class="eyebrow">GateBeast · suivi de production</p>
    <h1>Suivi des sprites</h1>
    <p class="standfirst">Tous les sprites du projet, quel que soit ce pour quoi ils sont produits :
      chaque type, chaque profil, chaque image attendue, une par une, avec son adresse exacte et son
      état. La maquette du parc est la première à en consommer, d'autres suivront et viendront s'y
      ajouter. Une case magenta est une image qui reste à tirer — le magenta est la couleur que la
      chaîne détoure, donc ici le vide à combler.</p>
  </header>

  <section class="track" aria-labelledby="track-title">
    <div class="track-head">
      <h2 id="track-title">État de la production</h2>
      <p class="track-total"><strong>{len(park_variants)}</strong> images attendues,
        réparties sur {sujet_total} sujets</p>
    </div>
    <ul class="track-grid">
{status_cells}
    </ul>
    <p class="track-foot"><em>{awaiting}</em> variante en attente d'un arbitrage du propriétaire —
      seule une image en défaut en demande un.</p>
    <div class="filters" role="group" aria-labelledby="filter-label">
      <p class="filter-label" id="filter-label">N'afficher que</p>
      <button type="button" class="filter is-on" data-filter="all" aria-pressed="true">Tout</button>
{filter_buttons}
    </div>
    <p class="filter-state" id="filter-state" role="status" aria-live="polite"></p>
  </section>

  <section class="recap" aria-labelledby="recap-title">
    <div class="recap-head">
      <h2 id="recap-title">Votre relevé, à me coller en conversation</h2>
      <button type="button" class="btn" data-copy="1">{escape(LABELS['copy'])}</button>
      <button type="button" class="btn btn--quiet" id="reset">{escape(LABELS['reset'])}</button>
      <p class="copy-state" id="copy-state" role="status" aria-live="polite"></p>
    </div>
    <p class="recap-intro">Rien n'est envoyé : cochez ce qui compte, le relevé se copie ci-dessous.</p>
    <pre class="recap-text" id="recap-text" data-empty="true" tabindex="0"></pre>
  </section>

{sections}

{hors_modele}

  <footer class="colophon">
    <p>Les adresses suivent le référentiel des sujets, <code>assets/sujets.json</code>, la seule
      source que cette page lit : l'orientation et l'action s'écrivent toujours ; la
      <strong>forme</strong> et la <strong>composition</strong> ne s'écrivent que si elles s'écartent de
      leur défaut. Aucune image n'a été générée pour cette page.</p>
    <p>Ce qui est plat, le rendu le pivote — une seule image par forme de chemin ; ce qui a du volume
      se dessine orientation par orientation et combinaison par combinaison, sans quoi le soleil
      passerait du mauvais côté.</p>
    <p>Toutes les emprises sont en <strong>cases</strong> — une case vaut un mètre. Cette page affiche
      chaque sprite à la taille exacte où le jeu le montre réellement,
      <strong>{escape(tile_scale.describe())}</strong> — une valeur que cette page ne mesure jamais
      elle-même, et tient du seul service qui la détient.</p>
  </footer>
</main>

<div class="bar">
  <p class="bar-count" id="bar-count"></p>
  <button type="button" class="btn" data-copy="1">{escape(LABELS['copy'])}</button>
</div>

<div class="viewer" id="viewer" hidden>
  <div class="viewer-back" data-close="1"></div>
  <figure class="viewer-box">
    <div class="viewer-with-prompt">
      <div class="viewer-stage">
        <div class="viewer-img" id="viewer-img" role="img"></div>
        <div class="viewer-tile" id="viewer-repeat-block" hidden>
          <div class="viewer-repeat" id="viewer-repeat" role="img"></div>
          <p class="viewer-cap">Répétée à l'échelle de la maquette — une jointure se verrait ici.</p>
        </div>
      </div>
      <aside class="viewer-side">
        <section class="viewer-block viewer-block--folded" id="viewer-prompt" hidden>
          <div class="viewer-block-head">
            <p class="viewer-block-title">Consigne de génération</p>
            <button type="button" class="btn btn--quiet" data-fold="viewer-prompt"
                    aria-expanded="false">{escape(LABELS['unfold'])}</button>
            <button type="button" class="btn btn--quiet" data-copy-block="viewer-prompt-text">Copier</button>
          </div>
          <pre class="panel-text" id="viewer-prompt-text"></pre>
        </section>
        <section class="viewer-block" id="viewer-report" hidden>
          <div class="viewer-block-head">
            <p class="viewer-block-title">Rapport de production</p>
            <button type="button" class="btn btn--quiet" data-copy-block="viewer-report-text">Copier</button>
          </div>
          <pre class="panel-text" id="viewer-report-text"></pre>
        </section>
      </aside>
    </div>
    <div class="viewer-foot">
      <figcaption class="viewer-cap" id="viewer-cap"></figcaption>
      <button type="button" class="btn" id="viewer-close" data-close="1">{escape(LABELS['viewerClose'])}</button>
    </div>
  </figure>
</div>

<div class="popin" id="panel" hidden>
  <div class="popin-back" data-close-panel="1"></div>
  <div class="popin-box">
    <div class="popin-head">
      <p class="popin-title" id="panel-title"></p>
      <button type="button" class="btn" id="panel-close" data-close-panel="1">{escape(LABELS['viewerClose'])}</button>
    </div>
    <div class="panel-body" id="panel-body"></div>
  </div>
</div>

<div class="popin" id="comparaison" hidden>
  <div class="popin-back" data-close-comparaison="1"></div>
  <div class="popin-box">
    <div class="popin-head">
      <p class="popin-title" id="comparaison-title"></p>
      <button type="button" class="btn" id="comparaison-close" data-close-comparaison="1">{escape(LABELS['viewerClose'])}</button>
    </div>
    <div class="comparaison-grid" id="comparaison-grid"></div>
  </div>
</div>

<script type="application/json" id="suivi-data">{PAYLOAD}</script>
<script>{SCRIPT}</script>
"""

OUT.write_text(page, encoding="utf-8")

def check_structure(markup):
    """Walk the generated tags and fail on an unbalanced or illegally nested block element.

    No browser is available to render the page here, so the two faults that would silently wreck the
    layout are caught by reading the markup: a tag left open, and a paragraph inside a paragraph —
    which a browser auto-closes, tearing the block apart.
    """
    import re as regex

    void = {"input", "img", "br", "hr", "meta", "link", "source"}
    watched = {"main", "section", "article", "header", "footer", "aside", "div", "ul", "li", "dl",
               "dt", "dd", "p", "pre", "h1", "h2", "h3", "span", "code", "label", "button", "em",
               "strong", "style", "script", "title"}
    stack = []
    for match in regex.finditer(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>", markup):
        closing, name, attributes = match.group(1), match.group(2).lower(), match.group(3)
        if name not in watched or name in void or attributes.rstrip().endswith("/"):
            continue
        if closing:
            assert stack, f"</{name}> with nothing open"
            assert stack[-1] == name, f"</{name}> closes a {stack[-1]}"
            stack.pop()
        else:
            if name == "p":
                assert "p" not in stack, "a <p> opened inside another <p> — the browser would split it"
            stack.append(name)
    assert not stack, f"tags left open: {stack}"

    return True


def check_wiring(markup, script, ids):
    """Every element the behaviour reaches for must exist, and every control must map to a variant."""
    import re as regex

    for name in set(regex.findall(r'getElementById\("([^"]+)"\)', script)):
        assert f'id="{name}"' in markup, f'the script reaches for #{name}, which the page has not'
    boxes = sum(len(STATE_ACTIONS[entry["status"]]) for entry in registry)
    for selector, expected in ((r'class="act"', boxes),
                               (r'class="note"', len(ids)),
                               (r'data-copy="1"', 2)):
        found = markup.count(selector.replace("\\", ""))
        assert found == expected, f"{selector}: {found} found, {expected} expected"
    for entry in registry:
        identifier = entry["id"]
        assert markup.count(f'data-id="{identifier}"') == len(STATE_ACTIONS[entry["status"]]), \
            f"{identifier}: wrong number of actions for state {entry['status']}"
        assert f'data-note="{identifier}"' in markup, identifier
        assert f'data-slot="{identifier}"' in markup, identifier

    return True


# ---- self-check: what the page claims is what the data holds -------------------------------------
# Derived from the inventory rather than pinned: the counts move as the model and production move,
# and a frozen figure here would only ever be a false alarm.
expected_park = sum(len(sujet["variants"]) for sujet in SUJETS.values())
assert len(park_variants) == expected_park, (len(park_variants), expected_park)
assert not [entry for entry in registry if entry["scope"] == "trial"], "a trial is still on the page"
assert sum(counts.values()) == len(park_variants), counts
assert set(counts) == set(STATUS), counts
assert page.count('class="slot slot--') == len(registry), page.count('class="slot slot--')
# Each variant offers only the moves its state allows, so the boxes are counted state by state.
expected_boxes = sum(len(STATE_ACTIONS[entry["status"]]) for entry in registry)
assert page.count('type="checkbox"') == expected_boxes, page.count('type="checkbox"')
assert page.count('class="note"') == len(registry)
assert len({entry["id"] for entry in registry}) == len(registry), "duplicate variant identifier"
for code in set(THUMBNAILS) | set(MASTERS):
    assert image_uri(code) in page, f"{code} image not embedded"
assert "http://" not in page and "https://" not in page, "an external reference slipped in"
# The behaviour must carry no French literal: every accented character in the script would be one.
assert not any(character in SCRIPT for character in "éèêàçùôîœ"), "French text leaked into the script"
assert "</script>" not in PAYLOAD, "the JSON payload would close its own tag"
assert PAYLOAD.isascii(), "the data block must be pure ascii, whatever the document charset"
parsed = json.loads(PAYLOAD)
assert [entry["id"] for entry in parsed["variants"]] == [entry["id"] for entry in registry]
assert parsed["storageKey"] == STORAGE_KEY
identifiers = [entry["id"] for entry in registry]
# Strip every style and script block before walking the markup: their contents are not html.
markup_only = re.sub(r"<(style|script)\b.*?</\1>", "", page, flags=re.S)
check_structure(markup_only)
check_wiring(page, SCRIPT, identifiers)

# ---- every html id must be usable: no space, no accent, and each one unique ----------------------
# Only a standalone id attribute — never the tail of data-id or aria-labelledby.
ids = re.findall(r'(?<![-\w])id="([^"]*)"', page)
for name in ids:
    assert re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name), f"unusable html id: {name!r}"
assert len(set(ids)) == len(ids), "a duplicate html id"
for target in re.findall(r'aria-labelledby="([^"]+)"', page):
    assert target in ids, f"aria-labelledby points at a missing id: {target}"

# ---- the filter: every unit it moves, and every hook it reaches for ------------------------------
units = re.findall(r'data-status="([a-z]+)"', page)
assert set(units) <= set(STATUS), set(units) - set(STATUS)
by_state = {key: units.count(key) for key in STATUS}
# Every filterable unit is a variant of the referentiel. Nothing else is on the page any more: the
# capability trials are gone, and so is the old "later, off the park" scope.
assert sum(by_state.values()) == len(registry), by_state
assert len(units) == len(registry), (len(units), len(registry))
assert page.count('class="filter"') == len(STATUS) and page.count('class="filter is-on"') == 1
for hook in ("filter-state", "filter-label", "viewer", "viewer-img", "viewer-repeat"):
    assert f'id="{hook}"' in page, hook
for selector in (".profile", ".type", ".filter", "[data-status]"):
    assert selector in SCRIPT, selector
assert "[hidden] { display: none !important; }" in page, "hiding would lose to the slot's own display"

# ---- the project's rule: no subject is ever measured in pixels -----------------------------------
# A judgement's report is EXTERNAL, verbatim text this page only displays — not authored here, so it
# is not held to a rule about what this page itself is allowed to write, the same way a variant's own
# ref or an owner's typed comment never was.
body = page.split("</style>", 1)[1].split("<script", 1)[0]
# A frozen consigne is verbatim too, and for the same reason: it is the exact text that was SENT to
# the generator, quoted here so the operator can read it against the image. It legitimately names the
# definition asked for in pixels — that is a property of the file, not a measure of a subject — and
# rewriting it to satisfy a rule about this page's own words would destroy the only trace of how the
# image was obtained.
body_without_reports = re.sub(r'<div class="judge-report"[^>]*>.*?</div>', "", body, flags=re.S)
body_without_reports = re.sub(r'<div class="prompt-body"[^>]*>.*?</div>', "",
                              body_without_reports, flags=re.S)
mentions = [figure.strip() for figure in re.findall(r"(\d[\d\s,.]*?)\s*pixels?", body_without_reports)]
assert mentions == [str(tile_scale.PIXELS_PER_TILE)], f"a pixel figure beyond the conversion: {mentions}"
assert body.count(tile_scale.describe()) == 1, "the conversion must appear once, from the service"
# The page must not carry its own copy of the pivot, in markup or in behaviour.
assert str(tile_scale.PIXELS_PER_TILE) not in SCRIPT, "the behaviour holds a copy of the tile scale"

print(f"{OUT}  {len(page) / 1024:.1f} kB")
print(f"park {len(park_variants)} variants across {sujet_total} sujets; "
      f"statuses {counts}; awaiting arbitration {awaiting}")
print(f"registry {len(registry)} variants, {expected_boxes} action boxes offered "
      f"(state by state), {len(registry)} comment fields")
print(f"filterable units {len(units)} -> {by_state}")

# A defect visible only inside the page is a defect nobody watches: whoever launched this build must
# see it here too, distinctly, without opening page.html — the page itself only shows it per slot.
if SKIPPED_IMAGES:
    print(f"SKIPPED — {len(SKIPPED_IMAGES)} representation(s) the referentiel names but this run "
          f"could not embed (each shown in the page as its own short label):", file=sys.stderr)
    for path, reason in SKIPPED_IMAGES.items():
        print(f"  - {path}: {reason['detail']}", file=sys.stderr)

if MISSING_LABELS:
    print(f"MISSING LABELS — {len(MISSING_LABELS)} sujet(s) with no French label in "
          f"{INVENTAIRE_DIR} (shown in the page as \"Libellé manquant\"):", file=sys.stderr)
    for code in MISSING_LABELS:
        print(f"  - {code}", file=sys.stderr)
