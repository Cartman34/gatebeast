#!/usr/bin/env python3
"""Build the sprite tracking page: every type, every profile, every expected variant, with its state.

The inventory below is a design decision handed down by the owner's coordinator and is reproduced as
given — codes, names and footprints are not invented and not corrected here.

Variant addresses follow the model in sujets-et-variantes.md: orientation and action are always
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
import json
import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[1] / "scripts"
ASSETS = HERE.parents[1] / "assets"
# The tile scale is a service, not a number to retype. The page shows what it says.
sys.path.insert(0, str(SCRIPTS))
import tile_scale
THUMBNAILS = json.loads((SCRIPTS / "thumbnails.json").read_text(encoding="utf-8"))
OUT = HERE / "page.html"

JUDGEMENTS_PATH = ASSETS / "jugements.json"


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
    for entry in data.get("jugements", []):
        image = entry.get("image", "")
        # A judgement names its image from the repository root; this page addresses images relative
        # to assets/, so the leading "assets/" is dropped to line the two up.
        if image.startswith("assets/"):
            image = image[len("assets/"):]
        by_path[image] = entry
    return by_path


JUDGEMENTS = load_judgements()

STORAGE_KEY = "gatebeast-suivi-sprites-v1"

# The production states. A word and a mark always travel with the colour, so nothing on this page is
# ever carried by colour alone. "en défaut" is a mechanical failure of the chain; "rejetée" is the
# owner turning an image down — two different things that must never be counted together.
STATUS = {
    "planned": {"label": "prévue", "mark": "○"},
    "running": {"label": "en production", "mark": "◐"},
    "done": {"label": "produite", "mark": "●"},
    "validated": {"label": "validée", "mark": "✓"},
    # U+00D7 rather than a heavier cross: it is present in every font, so the mark cannot turn to tofu.
    "fault": {"label": "en défaut", "mark": "×"},
    "rejected": {"label": "rejetée", "mark": "⊘"},
}
# The life of an image, then the two ways it can end badly. "produite" means the chain returned an
# image; "validée" means the owner accepted it — two different facts that must never be counted as one.
STATUS_ORDER = ["planned", "running", "done", "validated", "fault", "rejected"]

ACTIONS = [
    ("produce", "à produire"),
    ("validate", "valider"),
    ("retry", "à reprendre"),
    ("drop", "écarter"),
]

# What can be asked of a variant depends on what exists. Nothing can be retried or set aside before an
# image has ever been produced, and nothing can be asked of one being produced right now.
# The two failing states are not spelled out by the owner; retry and drop are the only moves that make
# sense on an image that exists but did not pass, so they are what is offered.
STATE_ACTIONS = {
    "planned": ["produce"],
    "running": [],
    "done": ["validate", "retry", "drop"],
    "validated": ["retry", "drop"],
    "fault": ["retry", "drop"],
    "rejected": ["retry", "drop"],
}

LABELS = {
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
    "scopes": {
        "park": "maquette du parc",
        "later": "cible ultérieure",
        "trial": "essai de capacité",
    },
}


DEFAULT_SHAPE = "plain"


def address(orientation="south", action="idle", shape=DEFAULT_SHAPE, garniture=None, frame=1):
    """The address of one image, per sujets-et-variantes.md.

    Orientation and action are always written. The shape follows the action, and only when it leaves
    its default `plain` — the value of every subject that does not assemble end to end, which is very
    nearly all of them. The garniture, when the variant carries one, follows the shape it belongs to.
    Directions would come next, then the frame.
    """
    pieces = [f"orientation-{orientation}", f"action-{action}"]
    if shape != DEFAULT_SHAPE:
        pieces.append(f"shape-{shape}")
    if garniture:
        pieces.append(f"garniture-{garniture}")
    pieces.append(f"frame-{frame:02d}")

    return "_".join(pieces)


# ---- the referentiel of sujets is the single source: no duplicate model lives here anymore ---------
# This page used to carry its own list of expected types, profiles and variants, kept by hand beside
# assets/sujets.json. The two drifted apart the day a new axis (garnitures) or a new shape arrived and
# only one of them learned about it — exactly what left three freshly produced fence pieces sitting in
# "hors modèle" although they were perfectly legitimate. There is now exactly one model: the referentiel
# itself, read here and never copied.
SUJETS_DATA = json.loads((ASSETS / "sujets.json").read_text(encoding="utf-8"))
TYPES = SUJETS_DATA["types"]
SUJETS = SUJETS_DATA["sujets"]
HORS_REFERENTIEL = {key: value for key, value in SUJETS_DATA.get("_hors_referentiel", {}).items()
                    if key != "_comment"}

# A ground material is the one type delivered as an exact box rather than at a contractual width —
# the same fact export-asset.py holds under the same name, asked of the referentiel rather than
# retyped, since "sol" is the type whose layer is "sol".
TILE_TYPE = "sol"

# French section headings. The referentiel itself stays in the technical vocabulary it is written in;
# only display strings live here, exactly as any other UI label on this page does.
TYPE_LABELS = {
    "sol": "Sol", "chemin": "Chemin", "cloture": "Clôture et mur", "arbre": "Arbre",
    "bosquet-arbres": "Bosquet d'arbres", "herbe": "Herbe", "batiment": "Bâtiment",
    "humain": "Humain", "creature": "Créature",
}
GARNITURE_LABELS = {"posts-2": "deux poteaux", "posts-1": "un poteau", "posts-0": "sans poteau"}


def type_rule(type_def):
    """What a type declares, in one line — derived from the referentiel's own data, never hand-written
    prose that could say something the data no longer does."""
    bits = [f"calque {type_def['layer']}",
            "passage ouvert par défaut" if type_def["passage_default"] == "open"
            else "passage fermé par défaut"]
    if type_def.get("assembles"):
        bits.append("s'assemble bout à bout, " + ("pivote" if type_def.get("rotates") else "ne pivote pas"))
    if type_def.get("garnitures"):
        values = ", ".join(type_def["garnitures"]["values"])
        bits.append(f"garnitures {values} (défaut {type_def['garnitures']['default']})")
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
          for entry in sujet["variantes"]
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
# a drawing: the edges are what the address means, and what a layout is checked against.
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
    """The size a sprite is actually SHOWN at: delivery-scale pixels, 96 per tile by default — the
    working size of this page, big enough to judge a sprite, no toggle down to the game's own display
    size (an earlier version of this page showed sprites at the real game's 24 px per tile; the
    operator could not judge anything at that size, so it is not the default any more).

    Every figure is ASKED of tile_scale.py, never retyped here. A deliverable is already exported at
    exactly this fineness, so it is shown at its own native size; a master stand-in, exported at a
    different, larger definition, is scaled down to the very same effective size instead of its own —
    the two must read at one consistent scale on this page, whichever one happens to be on screen.

    Width comes from the footprint — the ground the subject occupies — and height only ever follows the
    image's own proportions, never the other way around: scaling to a declared height would shrink a
    tall building until its base stopped covering its tiles. A tall subject overflows upward instead.
    A ground material is the one exception: it takes its footprint on both axes, because it has to tile
    edge to edge.
    """
    columns, rows = footprint
    if kind == "tile":
        return tile_scale.delivery_size(columns, rows)
    width, height = image_size(code)

    return tile_scale.delivery_box(columns, width, height)


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


def escape(text):
    return html.escape(str(text), quote=True)


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
                <input class="note" type="text" data-note="{escape(identifier)}"
                       placeholder="commentaire" aria-label="Commentaire — {escape(subject)}" />
              </div>"""


def register(identifier, code, profile_label, type_label, address_text, scope, status):
    registry.append({"id": identifier, "code": code, "profile": profile_label, "type": type_label,
                     "address": address_text, "scope": scope, "status": status})


def variant_caption(type_def, entry):
    """What actually distinguishes this variant, in the order it matters: shape first (the defining
    fact of an assembling subject), its garniture next when it carries one, and its orientation last —
    but only for a subject the renderer does not turn, the same condition the address itself follows.
    """
    if type_def.get("assembles"):
        caption = shape_label(entry.get("shape", DEFAULT_SHAPE))
    else:
        caption = "vue principale"
    if entry.get("garniture"):
        caption = f"{caption} · {GARNITURE_LABELS.get(entry['garniture'], entry['garniture'])}"
    orientation_speaks = type_def.get("assembles") and not type_def.get("rotates")
    if orientation_speaks and entry.get("orientation") in ORIENTATION_LABELS:
        caption = f"{caption} · {ORIENTATION_LABELS[entry['orientation']]}"

    return caption


def variant_shot(path, footprint, kind, label):
    """One representation. A path under poc/ is a master standing in for a livrable that does not
    exist yet, marked as such; a path under cutout/ is the livrable itself — the distinction the slot
    used to read off a disk scan is now read directly off the referentiel's own path.
    """
    code = thumbnail_key(path)
    if path.startswith("poc/"):
        return shot_markup(code, footprint, kind, f"{label} — maître, pas encore exporté",
                           extra=" shot-frame--master")
    return shot_markup(code, footprint, kind, label)


def representation_meta_markup(identifier, path, code, label):
    """Everything about one representation that is NOT the picture itself, in the encart's text area:
    whether it stands in for an unexported master, and its judgement — nothing here is ever laid over
    the image (see shot_markup()), so reading it never hides part of the sprite it is about.
    """
    tag = ('<p class="shot-tag">maître, pas encore exporté</p>' if path.startswith("poc/") else "")

    return tag + judge_body_markup(identifier, code, label)


def slot_markup(sujet_code, sujet, type_name, type_def, entry):
    """One variant, captioned by what actually distinguishes it, holding every representation it has —
    never just one, so a second attempt at the same posture is never hidden behind the first.

    The operator's own actions and comment field are offered here UNCONDITIONALLY, whether or not a
    representation exists and whether or not a judgement covers it: the machine's score is one more
    fact next to the sprite, never a gate on what the operator may do with it.
    """
    caption = variant_caption(type_def, entry)
    footprint = (sujet["emprise"]["columns"], sujet["emprise"]["rows"])
    kind = "tile" if type_name == TILE_TYPE else "sprite"
    addr = address(entry.get("orientation", "south"), entry.get("action", "idle"),
                  entry.get("shape", DEFAULT_SHAPE), entry.get("garniture"))
    identifier = f"{sujet_code}|{addr}"
    subject = f"{sujet_code} {caption}"
    representations = entry.get("representations", [])
    # Objectively knowable from the referentiel alone: a representation exists, or it does not. The
    # owner's own validation or rejection is never derived here — it lives in the operator's own
    # checkboxes and the recap they copy out, which this status never overrides.
    status = "done" if representations else "planned"
    register(identifier, sujet_code, sujet["profil"], TYPE_LABELS.get(type_name, type_name), addr,
             "park", status)

    wide = tile_scale.delivery_width(footprint[0]) > 200
    if representations:
        vis = "".join(variant_shot(rep["path"], footprint, kind, subject) for rep in representations)
        judge = "\n".join(
            representation_meta_markup(f"{identifier}|{index}", rep["path"],
                                       thumbnail_key(rep["path"]), subject)
            for index, rep in enumerate(representations))
    else:
        vis = (f'<div class="frame" style="{empty_style(footprint)}" role="img" '
               f'aria-label="Aucune image produite — {escape(footprint_label(footprint))}"></div>')
        judge = ""

    return f"""          <li class="slot slot--park{' slot--wide' if wide else ''}" data-slot="{escape(identifier)}" data-status="{status}">
            <div class="slot-vis">{vis}</div>
            <div class="slot-body">
              <div class="slot-line"><span class="slot-caption">{escape(caption)}</span>{status_markup(status, ' status--pill')}</div>
              <p class="slot-address">{escape(addr)}</p>
{judge}
{actions_markup(identifier, subject, status)}
            </div>
          </li>"""


def thumbnail_key(relative_path):
    """The THUMBNAILS key for a disk path: the path itself, its ".png" dropped."""
    return relative_path[:-4] if relative_path.endswith(".png") else relative_path


# Masters are loaded on demand, never scanned up front like THUMBNAILS: a master is only worth its
# weight on the page when it stands in for a deliverable that does not exist yet, so only the ones
# actually shown are ever read and base64-encoded.
MASTERS = {}


def master_entry(relative_path):
    """Read a poc master straight off the disk and cache it under the same key scheme as THUMBNAILS."""
    key = thumbnail_key(relative_path)
    if key not in MASTERS:
        path = ASSETS / relative_path
        data = path.read_bytes()
        with Image.open(path) as probe:
            size = probe.size
        MASTERS[key] = {"uri": f"data:image/png;base64,{base64.b64encode(data).decode('ascii')}",
                        "size": size}
    return key


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
    smaller either than the real game's own display size (tile_scale's 24 px per tile) — a FLOOR, not
    a viewing size, so a very flat sprite still keeps a full tile to aim at even if a future working
    scale were ever turned down. At today's 96 px working scale the floor essentially never binds; it
    stays here because the day it does, it is exactly the fault it exists to prevent.
    """
    shown = working_box(footprint, kind, code)
    floor = tile_scale.tile_box(*footprint)

    return {"width": max(shown["width"], floor["width"]), "height": max(shown["height"], floor["height"])}


def shot_markup(code, footprint, kind, label, extra=""):
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

    The bytes live once in a CSS custom property; this element only points at it, and the enlarged
    view points at the very same declaration. The page never carries an image twice.
    """
    frame = frame_style(footprint, kind, code)

    return (f'<div class="shot-frame{extra}" role="button" tabindex="0" '
            f'aria-label="{escape(label)} — voir en pleine taille" '
            f'style="width:{frame["width"]}px;height:{frame["height"]:.0f}px" '
            f'data-img="{escape(code)}">'
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


def judge_body_markup(identifier, code, label):
    """The score and verdict, always visible; the criterion-by-criterion detail folds behind a button,
    never crowding the encart. A sprite with no judgement yet says so, plainly — normal display, no
    image, no interaction, just the fact."""
    judgement = judgement_for(code)
    if judgement is None:
        return '            <p class="judge-pending">pas encore jugée</p>'
    criteria = "\n".join(
        f'                  <li class="judge-criterion{"" if item.get("tenu") else " judge-criterion--failed"}">'
        f'<span class="dot" aria-hidden="true">{"✓" if item.get("tenu") else "×"}</span> '
        f'{escape(item.get("nom", ""))}'
        + (f' — {escape(item["note"])}' if item.get("note") else "") + "</li>"
        for item in judgement.get("criteres", []))
    report_id = f"judge-{slug(identifier)}"

    return f"""            <div class="judge">
              <button type="button" class="judge-toggle" data-open="{escape(report_id)}"
                      aria-expanded="false" aria-label="Rapport de jugement — {escape(label)}">
                <span class="judge-score">{escape(judgement.get('score'))}/{escape(judgement.get('sur'))}</span>
                <span class="judge-verdict">{escape(judgement.get('verdict', ''))}</span>
                <span class="judge-open-word">rapport</span>
              </button>
              <div class="judge-report" data-report="{escape(report_id)}" hidden>
                <ul class="judge-criteria">
{criteria}
                </ul>
                <p class="judge-rapport">{escape(judgement.get('rapport', ''))}</p>
              </div>
            </div>"""



def sujet_markup(sujet_code, type_name, type_def):
    """One sujet's card: its own specs, drawn from the referentiel alone, and every variant it declares.

    No hand-written libellé or narrative detail lives here any more — the referentiel does not carry
    one (sujets-et-variantes.md: "tu ne recopies aucun libellé"), so none is invented on its behalf.
    """
    sujet = SUJETS[sujet_code]
    variants = sujet["variantes"]
    produced = sum(1 for entry in variants if entry.get("representations"))
    footprint = (sujet["emprise"]["columns"], sujet["emprise"]["rows"])

    specs = [("Emprise", footprint_label(footprint)), ("Calque", type_def["layer"]),
             ("Images", f"{produced} / {len(variants)}")]
    if type_def.get("assembles"):
        shapes = []
        for entry in variants:
            shape = entry.get("shape", DEFAULT_SHAPE)
            if shape not in shapes:
                shapes.append(shape)
        specs.append(("Formes", ", ".join(f"shape-{name}" for name in shapes)))
    if type_def.get("garnitures"):
        specs.append(("Garnitures", ", ".join(type_def["garnitures"]["values"])))
    if sujet.get("hauteur") is not None:
        height = sujet["hauteur"]
        specs.append(("Hauteur", f"{height} case{'s' if height != 1 else ''}"))
    spec_markup = "\n".join(
        f"            <div><dt>{escape(name)}</dt><dd>{escape(value)}</dd></div>"
        for name, value in specs)

    blocks = [f"""      <article class="profile">
        <header class="profile-head">
          <p class="profile-id"><code class="code">{escape(sujet_code)}</code></p>
          <h3>{escape(sujet['profil'])}</h3>
          <dl class="specs">
{spec_markup}
          </dl>
        </header>"""]
    blocks.append('        <ul class="slots">')
    blocks.extend(slot_markup(sujet_code, sujet, type_name, type_def, entry) for entry in variants)
    blocks.append("        </ul>")
    blocks.append("      </article>")

    return "\n".join(blocks)


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
    variant_count = sum(len(SUJETS[code]["variantes"]) for code in codes)

    return f"""    <section class="type" aria-labelledby="type-{anchor}">
      <header class="type-head">
        <h2 id="type-{anchor}">{escape(TYPE_LABELS.get(type_name, type_name))}</h2>
        <p class="type-count"><span>{variant_count}</span> image{'s' if variant_count > 1 else ''}</p>
        <p class="type-rule">{escape(type_rule(type_def))}</p>
      </header>
{sujets_markup}
    </section>"""


DISK_KIND_LABELS = {"poc": "brute (poc)", "cutout": "livrable"}
STRAY_CAP = 220  # a stray carries no footprint to size against, so it is capped instead


def stray_shot_markup(key, label):
    """A stray image, near its own resolution, over a checkerboard, opening full size on click. Works
    for a deliverable and for a master alike: image_size() does not care which catalogue it came from.

    The frame equals the image here — a stray carries no footprint to size a bigger target against —
    but it is, like every other shot, the whole and only click target: nothing is laid over the
    picture (see shot_markup()), so its own score and kind live in stray-body instead.
    """
    width, height = image_size(key)
    scale = min(1.0, STRAY_CAP / width)
    style = f"width:{width * scale:.0f}px;height:{height * scale:.0f}px"

    return (f'<div class="shot-frame" role="button" tabindex="0" '
            f'aria-label="{escape(label)} — voir en pleine taille" style="{style}" '
            f'data-img="{escape(key)}">'
            f'<div class="shot" style="{shot_background(key, "sprite")}"></div>'
            f'</div>')


def stray_vis_markup(entry):
    if entry["kind"] == "cutout":
        return stray_shot_markup(thumbnail_key(entry["path"]), entry["path"])

    # No deliverable exists for this stray either: its master is shown instead, same rule as a
    # modelled variant — nothing on disk stays invisible for lack of an export.
    key = master_entry(entry["path"])
    return stray_shot_markup(key, f'{entry["path"]} — maître, pas encore exporté')


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
              for entry in sujet["variantes"]
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
                      "variants": registry, "images": IMAGES, "storageKey": STORAGE_KEY},
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
.page { max-width: 1080px; margin: 0 auto; padding: 40px 20px 132px; }

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
  display: grid; grid-template-columns: 1fr auto; align-items: baseline; gap: 6px 18px;
  border-top: 2px solid var(--ink); padding-top: 12px;
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

/* ---- profile ---- */
.profile {
  margin-top: 22px; background: var(--surface); border: 1px solid var(--line);
  border-radius: 3px; padding: 20px 20px 22px;
}
.profile-head { display: flex; flex-direction: column; gap: 8px; }
.profile-id { margin: 0; display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.code {
  font-size: 13px; font-weight: 700; letter-spacing: 0.05em; padding: 2px 7px;
  background: var(--surface-sunk); border: 1px solid var(--line); border-radius: 2px;
}
.pname { font-size: 12.5px; color: var(--ink-faint); }
.profile h3 { margin: 0; font-size: 19px; font-weight: 700; letter-spacing: -0.012em; }
.specs {
  display: flex; flex-wrap: wrap; gap: 6px 26px; margin: 4px 0 0;
  padding: 11px 0 0; border-top: 1px solid var(--line);
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
  gap: 8px; list-style: none; margin: 14px 0 0; padding: 0;
}
.slot {
  display: flex; align-items: flex-start; gap: 10px; min-width: 0; padding: 8px 9px;
  background: var(--surface-sunk); border: 1px solid var(--line); border-radius: 3px;
}
/* A footprint too wide for a column takes the whole row rather than being shrunk out of scale. */
.slot--wide { grid-column: 1 / -1; flex-direction: column; }
.slot-vis { flex: none; max-width: 100%; overflow-x: auto; display: flex; flex-wrap: wrap; gap: 6px; }
.slot-body { min-width: 0; flex: 1 1 auto; display: flex; flex-direction: column; gap: 3px; }
.slot-line { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 8px; margin: 0; }
/* An unshot variant is a magenta keying field the exact size of the ground it will cover. */
.frame {
  border-radius: 2px; background: var(--key-field); border: 1.5px dashed var(--key-edge);
  display: flex; align-items: center; justify-content: center;
}
/* A master standing in for a missing deliverable is a real picture, but not the one that will end up
   in the game: a warm ring outside the frame keeps it visibly different from a genuine, delivered
   shot at a glance — OUTSIDE, on a positive offset, so it never draws over the picture itself; the
   same fact is also said in words, in shot-tag below, for whoever cannot rely on the colour alone. */
.shot-frame--master { outline: 2px solid var(--warn); outline-offset: 2px; }
.shot-tag { margin: 2px 0 0; font-size: 10.5px; color: var(--warn); font-style: italic; }
.slot-caption { font-size: 12px; font-weight: 700; }
.slot-address {
  margin: 0; font-size: 10px; line-height: 1.35; color: var(--ink-faint);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.slot--wide .slot-address, .slot:hover .slot-address { white-space: normal; overflow-wrap: anywhere; }

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
.act-note[aria-expanded="true"], .act-note[data-filled="true"] {
  background: var(--key-field); border-color: var(--key-edge); color: var(--key);
}
.slot-more { margin-top: 4px; }
.note {
  width: 100%; font-family: var(--mono); font-size: 11px; padding: 4px 6px;
  border: 1px solid var(--line); border-radius: 2px; background: var(--surface); color: var(--ink);
}
.note::placeholder { color: var(--ink-faint); }
.note:focus-visible { outline: 2px solid var(--key); outline-offset: 1px; }
.slot[data-marked="true"], .trial[data-marked="true"] { border-color: var(--key-edge); }

/* ---- judgement: score always visible, the criterion-by-criterion detail folds behind it ---- */
.judge-pending { margin: 2px 0 0; font-size: 10.5px; color: var(--ink-faint); font-style: italic; }
.judge-toggle {
  display: inline-flex; align-items: center; gap: 6px; margin-top: 2px; padding: 3px 7px;
  font-family: var(--mono); font-size: 10.5px; border: 1px solid var(--line); border-radius: 2px;
  background: var(--surface); color: var(--ink); cursor: pointer;
}
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
  max-width: 100%; align-self: center;
}
.viewer-foot { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.viewer-cap { margin: 0; font-size: 11.5px; color: var(--ink-soft); flex: 1 1 auto; }
.viewer-tile { display: flex; flex-direction: column; gap: 7px; align-items: center; }
.viewer-repeat {
  background-repeat: repeat; border: 1px solid var(--line); border-radius: 2px; max-width: 100%;
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

  function entryFor(id) {
    if (!state[id]) { state[id] = { acts: {}, note: "" }; }
    if (!state[id].acts) { state[id].acts = {}; }
    return state[id];
  }

  function persist() {
    try { window.localStorage.setItem(DATA.storageKey, JSON.stringify(state)); }
    catch (error) { /* a full or blocked store must not break the page */ }
  }

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
        out.push("  - " + entry.code + " " + entry.address);
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
        out.push("  - " + entry.code + " " + entry.address);
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

  Array.prototype.forEach.call(document.querySelectorAll(".act input"), function (box) {
    var id = box.getAttribute("data-id");
    var act = box.getAttribute("data-act");
    var entry = entryFor(id);
    box.checked = Boolean(entry.acts[act]);
    box.addEventListener("change", function () {
      entryFor(id).acts[act] = box.checked;
      persist();
      render();
    });
  });

  Array.prototype.forEach.call(document.querySelectorAll(".note"), function (field) {
    var id = field.getAttribute("data-note");
    var entry = entryFor(id);
    field.value = entry.note || "";
    field.addEventListener("input", function () {
      entryFor(id).note = field.value;
      persist();
      markNote(id);
      render();
    });
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

  // ---- judgement report: folded by default, no state kept — the file behind it can change any time
  // ---- a judging agent runs again, so nothing here is worth remembering across a reload.
  Array.prototype.forEach.call(document.querySelectorAll(".judge-toggle"), function (button) {
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

  // The whole frame is the click target and the ONLY one — nothing is laid over the picture any
  // more, so there is no separate eye button to also wire up. It is a div, not a native <button>,
  // so its own keyboard activation (Enter and Space) is handled here explicitly.
  Array.prototype.forEach.call(document.querySelectorAll(".shot-frame"), function (node) {
    node.addEventListener("click", function () { openViewer(node); });
    node.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " " || event.key === "Spacebar") {
        event.preventDefault();
        openViewer(node);
      }
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll("[data-close]"), function (node) {
    node.addEventListener("click", closeViewer);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !viewer.hidden) { closeViewer(); }
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

page = f"""<title>Suivi des sprites — maquette du parc</title>
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
    <p class="eyebrow">GateBeast · maquette du parc · suivi de production</p>
    <h1>Suivi des sprites de la maquette du parc</h1>
    <p class="standfirst">Chaque type, chaque profil, chaque image attendue, une par une, avec son
      adresse exacte et son état. Une case magenta est une image qui reste à tirer — le magenta est
      la couleur que la chaîne détoure, donc ici le vide à combler.</p>
  </header>

  <section class="track" aria-labelledby="track-title">
    <div class="track-head">
      <h2 id="track-title">État de la production</h2>
      <p class="track-total"><strong>{len(park_variants)}</strong> images à produire pour la maquette,
        réparties sur {sujet_total} sujets</p>
    </div>
    <ul class="track-grid">
{status_cells}
    </ul>
    <p class="track-foot"><em>{awaiting}</em> variante en attente d'un arbitrage du propriétaire —
      seule une image en défaut en demande un.</p>
    <div class="filters" role="group" aria-labelledby="filter-label">
      <p class="filter-label" id="filter-label">N'afficher que</p>
      <button type="button" class="filter is-on" data-filter="all" aria-pressed="true">tout</button>
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
      <strong>forme</strong> et la <strong>garniture</strong> ne s'écrivent que si elles s'écartent de
      leur défaut. Aucune image n'a été générée pour cette page.</p>
    <p>Ce qui est plat, le rendu le pivote — une seule image par forme de chemin ; ce qui a du volume
      se dessine orientation par orientation et combinaison par combinaison, sans quoi le soleil
      passerait du mauvais côté.</p>
    <p>Toutes les emprises sont en <strong>cases</strong> — une case vaut un mètre. Cette page affiche
      chaque sprite à sa propre <strong>définition de livraison</strong>, plus grande que sa taille
      réelle en jeu pour qu'on puisse la juger ; le jeu, lui, affiche
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
    <div class="viewer-img" id="viewer-img" role="img"></div>
    <div class="viewer-tile" id="viewer-repeat-block" hidden>
      <div class="viewer-repeat" id="viewer-repeat" role="img"></div>
      <p class="viewer-cap">Répétée à l'échelle de la maquette — une jointure se verrait ici.</p>
    </div>
    <div class="viewer-foot">
      <figcaption class="viewer-cap" id="viewer-cap"></figcaption>
      <button type="button" class="btn" id="viewer-close" data-close="1">{escape(LABELS['viewerClose'])}</button>
    </div>
  </figure>
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
expected_park = sum(len(sujet["variantes"]) for sujet in SUJETS.values())
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
# address or an owner's typed comment never was.
body = page.split("</style>", 1)[1].split("<script", 1)[0]
body_without_reports = re.sub(r'<div class="judge-report"[^>]*>.*?</div>', "", body, flags=re.S)
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
