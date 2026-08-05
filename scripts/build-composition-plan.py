#!/usr/bin/env python3
"""Render any composition plan from its declaration. The standard entry point.

Usage: python3 scripts/build-composition-plan.py <plan.json>

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
SUJETS = REPO / "assets" / "sujets.json"

# The fifteen shapes the design defines, in its own order — shape_vocab's, not a copy of its own:
# reported so a plan says out loud which shapes it exercises and which it leaves out (a missing shape
# is a missing sprite), on the same list every other tool that knows about shapes uses.
EVERY_SHAPE = shape_vocab.edge_combinations()

# A quarter turn, applied to one edge: n becomes e, e becomes s, and so on. Used only to tell whether
# two SHAPES are the same drawing seen at a different rotation — nothing here decides whether a given
# subject is actually allowed to rotate, that is assets/sujets.json's call (see rotates_of below).
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


def rotates_of(sujets: dict, code: str) -> bool:
    """Whether CODE's type is drawn once and rotated by the engine, or drawn separately per shape.

    Never guessed from the code's own letters — assets/sujets.json is the one place that knows, and a
    plan that cannot ask it FAILS LOUDLY rather than assume either answer: a wrong guess here would
    either short the piece count for a volumed subject (fence, wall) or double-produce a flat one
    (path, water) for nothing.
    """
    sujet = sujets.get("sujets", {}).get(code)
    if sujet is None:
        raise SystemExit(f"FAULT {code} absent de {SUJETS.relative_to(REPO)} — rien ne se compte "
                          f"sans fiche")
    type_name = sujet["type"]
    type_entry = sujets.get("types", {}).get(type_name)
    if type_entry is None:
        raise SystemExit(f"FAULT type {type_name} (sujet {code}) absent de "
                          f"{SUJETS.relative_to(REPO)}")
    if "rotates" not in type_entry:
        raise SystemExit(f"FAULT le type {type_name} (sujet {code}) ne déclare pas s'il pivote "
                          f"(clé 'rotates' absente) — {SUJETS.relative_to(REPO)}")

    return type_entry["rotates"]


def _load_sujets() -> dict:
    """The subjects referentiel, read once per run — the one place that knows whether a type pivots.

    Absent or unreadable is a briefing fault like any other missing sheet in this codebase: it FAILS
    LOUDLY here rather than falling back on a guess (a name ending in a shape-bearing family, say),
    which is exactly the shortcut that would make the count wrong for the one subject where it matters.
    """
    if not SUJETS.is_file():
        raise SystemExit(f"FAULT référentiel des sujets introuvable : {SUJETS.relative_to(REPO)}")
    try:
        return json.loads(SUJETS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"FAULT référentiel des sujets illisible ({SUJETS.relative_to(REPO)}) : "
                          f"{error}")


def build(source: Path) -> int:
    plan = json.loads(source.read_text(encoding="utf-8"))
    if plan.get("format") != "gatebeast-composition-plan":
        print(f"FAULT {source.name} is not a composition plan")
        return 1

    columns, rows = plan["grid"]["columns"], plan["grid"]["rows"]
    default_cell = plan.get("default_cell", "transparent")

    # A declared cell is one placed subject. It covers one cell unless it says otherwise — a
    # building, a wide tree, a bridge take several — and it joins its neighbours only where it says
    # so. Both are optional and default to the common case: one cell, no connection.
    traces, subjects, placed, occupied = {}, {}, [], {}
    for cell in plan["cells"]:
        column, row = cell["column"], cell["row"]
        width, height = cell.get("columns", 1), cell.get("rows", 1)
        subject = cell["subject"]
        footprint = composition_plan.tiles(column, row, column + width - 1, row + height - 1)
        for key in sorted(footprint):
            if key in occupied:
                print(f"FAULT ({key[0]},{key[1]}) is taken by {occupied[key]} and by {subject}")
                return 1
            if not (1 <= key[0] <= columns and 1 <= key[1] <= rows):
                print(f"FAULT {subject} at ({column},{row}) reaches ({key[0]},{key[1]}), "
                      f"outside the grid")
                return 1
            occupied[key] = subject
        placed.append((subject, column, row, column + width - 1, row + height - 1))
        subjects[(column, row)] = subject
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
            traces[(column, row)] = set(cell["joins"])

    faults = composition_plan.check_traces(traces, columns, rows)
    for key, joined in traces.items():
        for edge in sorted(joined):
            dx, dy = composition_plan.STEP[edge]
            neighbour = (key[0] + dx, key[1] + dy)
            # Two subjects that meet is a real case — a path reaching a gate — but never a silent
            # one: it is worth seeing on the plan.
            if neighbour in subjects and subjects[neighbour] != subjects[key]:
                print(f"NOTE ({key[0]},{key[1]}) {subjects[key]} joins {edge} onto "
                      f"{subjects[neighbour]}")
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
    # assets/sujets.json is the only way to tell the two apart; guessing from the subject's own name
    # would be exactly the shortcut the operator flagged.
    sujets = _load_sujets() if traces else {}
    shapes_by_subject = {}
    for key, joined in traces.items():
        shape = composition_plan.shape_of(joined).replace("shape-", "")
        shapes_by_subject.setdefault(subjects[key], set()).add(shape)
    drawings_by_subject = {
        subject: (len({rotation_class(shape) for shape in shapes}) if rotates_of(sujets, subject)
                  else len(shapes))
        for subject, shapes in shapes_by_subject.items()
    }
    drawings_needed = sum(drawings_by_subject.values())

    elements = [(subject, c1, r1, c2, r2, "") for subject, c1, r1, c2, r2 in placed]

    # LE COUVERT DE CHAQUE SUJET POSÉ, LU AU RÉFÉRENTIEL ET JAMAIS DEVINÉ. Le couvert est ce que le volume surplombe ; à défaut d'être déclaré il vaut l'emprise, et rien
    # n'est alors dessiné, puisqu'il n'y a pas de débord à montrer. Le référentiel n'est chargé qu'une fois : il l'était déjà pour savoir quels types pivotent.
    sujets = sujets or _load_sujets()
    spreads = {}
    for subject in set(subjects.values()) | {name for name, *_ in placed}:
        sujet = sujets.get("sujets", {}).get(subject) if isinstance(sujets, dict) else None
        if not sujet:
            continue
        spread = sujet.get("couvert") or sujet.get("emprise")
        if spread:
            spreads[subject] = (spread["columns"], spread["rows"])

    # A short key per DISTINCT piece — same subject, same shape, same subject composition (e.g. same
    # posts variant). The same key is reused wherever that piece is laid, so the plan says at a
    # glance which cells carry the same sprite, and doubles as the cutting map. Letters follow the
    # reading order of first appearance.
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pieces, keys = {}, {}
    for key in sorted(traces, key=lambda item: (item[1], item[0])):
        signature = (subjects[key], composition_plan.shape_of(traces[key]))
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

    print(f"cases {len(traces)} · sujets {', '.join(sorted(set(subjects.values())))} · "
          f"cellule par défaut {default_cell}")
    for shape in EVERY_SHAPE:
        print(f"  shape-{shape:<6} {f'x{tally[shape]}' if shape in tally else 'ABSENTE'}")
    print(f"formes exercées : {len(tally)}/{len(EVERY_SHAPE)}")
    for subject, count in drawings_by_subject.items():
        pivote = "pivote" if rotates_of(sujets, subject) else "ne pivote pas"
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
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(build(Path(sys.argv[1])))
