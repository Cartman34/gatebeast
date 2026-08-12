#!/usr/bin/env python3
"""Render any composition plan from its declaration. The standard entry point.

Usage: python3 scripts/build-composition-plan.py <plan.json>
       python3 scripts/build-composition-plan.py -h|--help — this text

The JSON beside the SVG IS the plan. It says how big the grid is, what a cell holds when nothing is
declared for it, and then, cell by cell, WHICH SUBJECT stands there and WHICH NEIGHBOURS it joins.
Nothing is derived from adjacency: two fences can stand side by side without meeting, and a plan
that guessed would silently invent a connection.

The same format serves any subject that runs and connects — fences, paths, walls, water — and a plan
may mix several: each cell names its own subject.

    {
      "format": "gatebeast-composition-plan", "version": 1,
      "title": "...",
      "grid": {"columns": 7, "rows": 7},
      "default_cell": "transparent",        // or a profile code, e.g. "CH-001" for short grass
      "notes": ["..."],
      "cells": [{"column": 2, "row": 2, "subject": "OB-010", "joins": ["e", "s"]}]
    }

The plan ships only if the declaration holds: every connection declared from both sides. A failing
plan is not written — a composition fault must cost a plan, never a generation.

Writes the SVG next to the JSON, under the same name.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan_svg as composition_plan
import shape_vocab

REPO = Path(__file__).resolve().parent.parent
SUBJECTS = REPO / "assets" / "subjects.json"

# The fifteen shapes the design defines, in its own order — shape_vocab's, not a copy of its own:
# reported so a plan says out loud which shapes it exercises and which it leaves out (a missing shape
# is a missing sprite), on the same list every other tool that knows about shapes uses.
EVERY_SHAPE = shape_vocab.edge_combinations()

# A quarter turn, applied to one edge: n becomes e, e becomes s, and so on. Used only to tell whether
# two SHAPES are the same drawing seen at a different rotation — nothing here decides whether a given
# subject is actually allowed to rotate, that is assets/subjects.json's call (see rotates_of below).
_QUARTER_TURN = {"n": "e", "e": "s", "s": "w", "w": "n"}


def _rotate(shape: str) -> str:
    """One shape, turned a quarter turn — edges re-sorted to the canonical n, e, s, w order so the
    result is itself a well-formed shape name, comparable to any other."""
    return "".join(sorted((_QUARTER_TURN[edge] for edge in shape), key=shape_vocab.EDGES.index))


def rotation_class(shape: str) -> str:
    """The one name shared by a shape and every shape a quarter, half or three-quarter turn of it
    reaches — e.g. "n", "e", "s" and "w" all return to the same class, because a single drawing of a
    dead end, turned by the engine, is every one of the four. Picked as the smallest of the four names
    so two equivalent shapes always resolve to the exact same class, regardless of which one came first
    in a given plan.
    """
    turned = shape
    seen = {shape}
    for _ in range(3):
        turned = _rotate(turned)
        seen.add(turned)

    return min(seen)


def rotates_of(subjects: dict, code: str) -> bool:
    """Whether CODE's type is drawn once and rotated by the engine, or drawn separately per shape.

    Never guessed from the code's own letters — assets/subjects.json is the one place that knows, and a
    plan that cannot ask it FAILS LOUDLY rather than assume either answer: a wrong guess here would
    either short the piece count for a volumed subject (fence, wall) or double-produce a flat one
    (path, water) for nothing.
    """
    subject = subjects.get("subjects", {}).get(code)
    if subject is None:
        raise SystemExit(f"FAULT {code} absent de {SUBJECTS.relative_to(REPO)} — rien ne se compte "
                          f"sans fiche")
    type_name = subject["type"]
    type_entry = subjects.get("types", {}).get(type_name)
    if type_entry is None:
        raise SystemExit(f"FAULT type {type_name} (sujet {code}) absent de "
                          f"{SUBJECTS.relative_to(REPO)}")
    if "rotates" not in type_entry:
        raise SystemExit(f"FAULT le type {type_name} (sujet {code}) ne déclare pas s'il pivote "
                          f"(clé 'rotates' absente) — {SUBJECTS.relative_to(REPO)}")

    return type_entry["rotates"]


def _load_sujets() -> dict:
    """The subjects referentiel, read once per run — the one place that knows whether a type pivots.

    Absent or unreadable is a briefing fault like any other missing sheet in this codebase: it FAILS
    LOUDLY here rather than falling back on a guess (a name ending in a shape-bearing family, say),
    which is exactly the shortcut that would make the count wrong for the one subject where it matters.
    """
    if not SUBJECTS.is_file():
        raise SystemExit(f"FAULT référentiel des sujets introuvable : {SUBJECTS.relative_to(REPO)}")
    try:
        return json.loads(SUBJECTS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"FAULT référentiel des sujets illisible ({SUBJECTS.relative_to(REPO)}) : "
                          f"{error}")


# Ce qui se pose À PLAT sur le sol, par opposition à ce qui s'y dresse. Le rendu du jeu empile déjà les deux dans cet ordre : le calque du sol, puis les volumes.
# THE LAYER A SUBJECT BELONGS TO IS READ FROM ITS TYPE, NEVER FROM A LIST KEPT HERE. What stood here was `FLAT_TYPES = {"sol", "chemin", "herbe", "cours-d-eau"}`,
# a second truth beside the referential, and it was already wrong on two of its four entries: grass declares the `monde` layer because it stands up, and a stream
# declares `decor-au-sol` because one walks on it. Two subjects clash on a cell when they share a LAYER — that is the whole rule, and it is the same one the
# mounter uses to stack them.
DEFAULT_LAYER = "world"

# A variant field and the type key that declares it are the same word, singular and plural — and the plural is not built by adding an "s" once the vocabulary is
# English: `density` gives `densities`. The irregular pairs are declared once, as they are in generate-sprite.py, and never derived by string surgery.
IRREGULAR_PLURAL = {"density": "densities"}


def collection_of(field):
    """The type key that declares a variant field: its irregular plural if it has one, else the field plus an s."""
    return IRREGULAR_PLURAL.get(field, field + "s")


def layer_of(referential, code):
    """The layer a subject is drawn in, read from its type in the referential. Unknown subject or type falls back to the world, the layer that sorts by depth."""
    subject = (referential.get("subjects") or {}).get(code) or {}
    type_ = (referential.get("types") or {}).get(subject.get("type")) or {}

    return type_.get("layer", DEFAULT_LAYER)


def build(source: Path) -> int:
    plan = json.loads(source.read_text(encoding="utf-8"))
    # The referential is read straight away: the layer of every subject has to be known from the occupancy check onwards. IT CARRIES ITS OWN NAME, `referential`,
    # and that is a fix: it used to be called `subjects`, and twenty lines below the table of placed cells took the same name and shadowed it. `is_flat(subjects,
    # ...)` therefore received the cell table instead of the referential and ALWAYS returned false — the exemption that lets a path run under a building never
    # worked, and any second placement on a cell was refused. That refusal is what had been mistaken for a rule of the world.
    referential = _load_sujets()
    if plan.get("format") != "gatebeast-composition-plan":
        print(f"FAULT {source.name} is not a composition plan")
        return 1

    columns, rows = plan["grid"]["columns"], plan["grid"]["rows"]
    default_cell = plan.get("default_cell", "transparent")

    # A declared cell is one placed subject. It covers one cell unless it says otherwise — a
    # building, a wide tree, a bridge take several — and it joins its neighbours only where it says
    # so. Both are optional and default to the common case: one cell, no connection.
    traces, subjects, placed, occupied, trace_subject = {}, {}, [], {}, {}
    for cell in plan["cells"]:
        column, row = cell["column"], cell["row"]
        width, height = cell.get("columns", 1), cell.get("rows", 1)
        subject = cell["subject"]
        footprint = composition_plan.tiles(column, row, column + width - 1, row + height - 1)
        layer = layer_of(referential, subject)
        for key in sorted(footprint):
            # A CELL CARRIES ONE SPRITE PER LAYER FAMILY, AND THE DESIGN SAYS SO: the ground, the ground decor, the world, the overhead. A cell may therefore
            # carry several subjects — a path running UNDER a building, grass at the foot of a tree, a character on a path — and it is even necessary: a
            # building's door never falls on the bottom edge of its sprite, so a path stopped at the edge of the footprint would stay two tiles short of it.
            # WHAT REMAINS A FAULT, AND NOTHING ELSE: two subjects of the SAME layer on the same cell. There, one of them is certainly one too many.
            if occupied.get(key, {}).get(layer):
                print(f"FAULT ({key[0]},{key[1]}) carries {occupied[key][layer]} and {subject}, "
                      f"both in layer '{layer}' — a cell holds one sprite per layer")
                return 1
            if not (1 <= key[0] <= columns and 1 <= key[1] <= rows):
                print(f"FAULT {subject} at ({column},{row}) reaches ({key[0]},{key[1]}), "
                      f"outside the grid")
                return 1
            occupied.setdefault(key, {})[layer] = subject
        placed.append((subject, column, row, column + width - 1, row + height - 1))
        # THE TABLE OF PLACED CELLS NOW HOLDS A LIST, and that is the point's second defect: `subjects[(col, row)] = subject` SILENTLY overwrote whatever was
        # already there. A cell carrying grass and a fox cub declared only one of them, and which one depended on the order of the plan.
        subjects.setdefault((column, row), []).append(subject)
        # A CELL MAY NAME THE VARIANT FIELDS IT WANTS, and every one of them is checked against the type — a field the type does not declare, or a value it does
        # not allow, is a fault here rather than a cell that silently comes back with the ordinary drawing. This is what lets a fence crossed by a path carry a
        # GATE: the four gate drawings existed, declared and current, and no plan could reach them until now.
        for field, value in (cell.get("variant") or {}).items():
            type_name = (referential["subjects"].get(subject) or {}).get("type")
            declaration = (referential["types"].get(type_name) or {}).get(collection_of(field))
            if not isinstance(declaration, dict) or "values" not in declaration:
                print(f"FAULT {subject} at ({column},{row}) asks for '{field}', which type {type_name} does not declare")
                return 1
            if value not in declaration["values"]:
                print(f"FAULT {subject} at ({column},{row}) asks for {field}={value!r}, not among {declaration['values']}")
                return 1
        if cell.get("joins"):
            if (width, height) != (1, 1):
                print(f"FAULT {subject} at ({column},{row}) spans several cells and declares "
                      f"connections: a trace piece is one cell")
                return 1
            unknown = [edge for edge in cell["joins"] if edge not in shape_vocab.EDGES]
            if unknown:
                print(f"FAULT {subject} at ({column},{row}) joins unknown edge(s) {unknown} — "
                      f"expected among {list(shape_vocab.EDGES)}")
                return 1
            # THE UNION, NOT THE LAST WRITER. A cell may carry two traced subjects — a path crossing a fence line, a bridge carrying a path over a stream — and
            # plain assignment erased the first: the fence's own north-south run then reported itself as broken on every cell the path crossed.
            traces.setdefault((column, row), set()).update(cell["joins"])
            # THE SUBJECT THAT CARRIES THE TRACE, kept apart from the cell's list of subjects: a trace cell carries exactly one — a trace piece fits on one cell,
            # the check just above enforces it — whereas the cell itself may carry several now that one layer no longer evicts another.
            trace_subject[(column, row)] = subject

    faults = composition_plan.check_traces(traces, columns, rows)
    for key, joined in traces.items():
        for edge in sorted(joined):
            dx, dy = composition_plan.STEP[edge]
            neighbour = (key[0] + dx, key[1] + dy)
            # Two subjects that meet is a real case — a path reaching a gate — but never a silent
            # one: it is worth seeing on the plan.
            others = [code for code in subjects.get(neighbour, []) if code != trace_subject[key]]
            if others:
                print(f"NOTE ({key[0]},{key[1]}) {trace_subject[key]} joins {edge} onto "
                      f"{', '.join(others)}")
    if faults:
        for fault in faults:
            print(f"FAULT {fault}")
        return 1

    tally = {}
    for joined in traces.values():
        tally[composition_plan.shape_of(joined).replace("shape-", "")] = tally.get(
            composition_plan.shape_of(joined).replace("shape-", ""), 0) + 1
    missing = [shape for shape in EVERY_SHAPE if shape not in tally]

    # WHAT THE COMPOSITION EXERCISES is not what has to be DRAWN: a flat type (path, water) is drawn
    # once per rotation class and turned by the engine for the rest, while a volumed type (fence, wall)
    # needs one drawing per shape — rotating it would put the sun on the wrong side. Asking
    # assets/subjects.json is the only way to tell the two apart; guessing from the subject's own name
    # would be exactly the shortcut the operator flagged.
    shapes_by_subject = {}
    for key, joined in traces.items():
        shape = composition_plan.shape_of(joined).replace("shape-", "")
        shapes_by_subject.setdefault(trace_subject[key], set()).add(shape)
    drawings_by_subject = {
        subject: (len({rotation_class(shape) for shape in shapes}) if rotates_of(referential, subject)
                  else len(shapes))
        for subject, shapes in shapes_by_subject.items()
    }
    drawings_needed = sum(drawings_by_subject.values())

    elements = [(subject, c1, r1, c2, r2, "") for subject, c1, r1, c2, r2 in placed]

    # LE COUVERT DE CHAQUE SUJET POSÉ, LU AU RÉFÉRENTIEL ET JAMAIS DEVINÉ. Le couvert est ce que le volume surplombe ; à défaut d'être déclaré il vaut l'emprise, et rien
    # n'est alors dessiné, puisqu'il n'y a pas de débord à montrer. Le référentiel n'est chargé qu'une fois : il l'était déjà pour savoir quels types pivotent.
    # THIS BLOCK HAD NEVER RUN. It reassigned `subjects` — the table of placed cells — to the referential, then iterated its values as if they were codes, then
    # used the looked-up subject DICT as a dictionary key, which Python cannot hash. Three faults in five lines, all hidden behind an earlier one that made the
    # plan fail before reaching them. The referential now has its own name throughout, the codes are gathered as codes, and `spreads` is keyed by the code —
    # which is how plan_svg reads it.
    spreads = {}
    codes = {code for placed_codes in subjects.values() for code in placed_codes}
    codes |= {name for name, *_ in placed}
    for code in sorted(codes):
        subject = referential.get("subjects", {}).get(code)
        if not subject:
            continue
        # LE COUVERT SE COMPARE À L'EMPRISE DÉCLARÉE DU SUJET, jamais à ce que sa case occupe dans ce plan-ci : c'est une propriété du sujet, pas de son emplacement. Le
        # nombre de cases n'influence que la FORME du cercle, il ne décide pas de son existence (opérateur, 2026-08-05).
        ground = subject.get("footprint")
        spread = subject.get("cover") or ground
        if spread and ground:
            spreads[code] = ((spread["columns"], spread["rows"]), (ground["columns"], ground["rows"]))

    # A short key per DISTINCT piece — same subject, same shape, same subject composition (e.g. same
    # posts variant). The same key is reused wherever that piece is laid, so the plan says at a
    # glance which cells carry the same sprite, and doubles as the cutting map. Letters follow the
    # reading order of first appearance.
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pieces, keys = {}, {}
    for key in sorted(traces, key=lambda item: (item[1], item[0])):
        signature = (trace_subject[key], composition_plan.shape_of(traces[key]))
        if signature not in pieces:
            pieces[signature] = alphabet[len(pieces) % len(alphabet)]
        keys[key] = pieces[signature]

    # LES LETTRES DE PIÈCES SE DEMANDENT, ELLES NE S'IMPOSENT PAS. Elles servent à un plan d'USAGE d'un sujet, où le plan double la carte de découpe : deux cases portant la
    # même lettre sont la même sprite à produire. Sur un plan de SCÈNE, où le tracé se lit déjà tout seul, elles ne font qu'encombrer chaque case d'une lettre que personne
    # ne lit. Le plan dit lequel des deux il est ; sans rien dire, il les garde, ce qui laisse les plans existants inchangés.
    piece_keys = plan.get("piece_keys", True)
    if not piece_keys:
        keys = {}

    # LE DESSIN PORTE SES NOTES, OU LA PAGE LES PORTE — jamais les deux. Écrites dans le dessin, elles y sont figées à la taille et à la couleur du tracé, elles ne se
    # sélectionnent pas, elles ne se lient pas, et elles rallongent une image dont on ne voulait que le plan. Une page qui affiche le plan les rend mieux, en clair et en
    # HTML, depuis la même déclaration. Le plan dit lequel des deux il veut ; sans rien dire, il les garde, ce qui laisse les plans existants inchangés.
    drawing_notes = plan.get("drawing_notes", True)

    notes = list(plan.get("notes", []))
    if piece_keys:
        notes.append("Pièces distinctes — deux cases portant la même lettre sont la même sprite :")
        # Folded over several lines: a single line of fifteen pieces stretched the canvas to four
        # thousand pixels, and a plan that scrolls sideways cannot be read.
        listed = [f"{letter} {subject} {shape}" for (subject, shape), letter in pieces.items()]
        for start in range(0, len(listed), 5):
            notes.append("   " + " · ".join(listed[start:start + 5]))
    notes.append(f"Cellule par défaut : {default_cell}.")
    notes.append(f"{len(traces)} cases déclarées, {len(tally)} formes distinctes sur "
                 f"{len(EVERY_SHAPE)}. Absentes : " + (", ".join(missing) or "aucune") + ".")
    if drawings_by_subject:
        detail = ", ".join(f"{subject} : {count}" for subject, count in drawings_by_subject.items())
        notes.append(f"{drawings_needed} dessin(s) réellement à produire compte tenu de la rotation "
                     f"({detail}) — un sujet plat pivote un seul dessin par forme équivalente, un "
                     f"sujet à volume en dessine une par forme.")

    svg = composition_plan.render(
        columns, rows,
        elements=elements,
        traces=traces,
        keys=keys,
        spreads=spreads,
        legend=plan.get("legend", True),
        title=plan.get("title", source.stem),
        notes=notes if drawing_notes else [],
        tile=40)

    out = source.with_suffix(".svg")
    out.write_text(svg, encoding="utf-8")

    # Une case peut porter plusieurs sujets depuis qu'un calque ne chasse plus l'autre : la table en garde une LISTE, et le compte se fait sur les codes aplatis.
    print(f"cases {len(traces)} · sujets {', '.join(sorted(codes))} · "
          f"cellule par défaut {default_cell}")
    for shape in EVERY_SHAPE:
        print(f"  shape-{shape:<6} {f'x{tally[shape]}' if shape in tally else 'ABSENTE'}")
    print(f"formes exercées : {len(tally)}/{len(EVERY_SHAPE)}")
    for subject, count in drawings_by_subject.items():
        pivote = "pivote" if rotates_of(referential, subject) else "ne pivote pas"
        print(f"  {subject} ({pivote}) : {count} dessin(s) réellement à produire, pour "
              f"{len(shapes_by_subject[subject])} forme(s) exercée(s)")
    if drawings_by_subject:
        print(f"total : {drawings_needed} dessin(s) réellement à produire compte tenu de la rotation")
    print("COHERENCE OK: chaque connexion est déclarée des deux côtés")
    try:
        print(f"plan écrit : {out.relative_to(REPO)}")
    except ValueError:
        print(f"plan écrit : {out}")

    return 0


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        raise SystemExit(0)
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(build(Path(sys.argv[1])))
