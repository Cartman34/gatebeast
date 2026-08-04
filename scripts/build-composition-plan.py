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

REPO = Path(__file__).resolve().parent.parent

# The fifteen shapes the design defines, in its own order. Reported so a plan says out loud which
# shapes it exercises and which it leaves out — a missing shape is a missing sprite.
EVERY_SHAPE = ["n", "e", "s", "w", "ns", "ew", "ne", "es", "sw", "nw",
               "nes", "esw", "nsw", "new", "nesw"]


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

    elements = [(subject, c1, r1, c2, r2, "") for subject, c1, r1, c2, r2 in placed]

    # A short key per DISTINCT piece — same subject, same shape, same garniture. The same key is
    # reused wherever that piece is laid, so the plan says at a glance which cells carry the same
    # sprite, and doubles as the cutting map. Letters follow the reading order of first appearance.
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pieces, keys = {}, {}
    for key in sorted(traces, key=lambda item: (item[1], item[0])):
        signature = (subjects[key], composition_plan.shape_of(traces[key]))
        if signature not in pieces:
            pieces[signature] = alphabet[len(pieces) % len(alphabet)]
        keys[key] = pieces[signature]

    notes = list(plan.get("notes", []))
    notes.append("Pièces distinctes — deux cases portant la même lettre sont la même sprite :")
    # Folded over several lines: a single line of fifteen pieces stretched the canvas to four
    # thousand pixels, and a plan that scrolls sideways cannot be read.
    listed = [f"{letter} {subject} {shape}" for (subject, shape), letter in pieces.items()]
    for start in range(0, len(listed), 5):
        notes.append("   " + " · ".join(listed[start:start + 5]))
    notes.append(f"Cellule par défaut : {default_cell}.")
    notes.append(f"{len(traces)} cases déclarées, {len(tally)} formes distinctes sur "
                 f"{len(EVERY_SHAPE)}. Absentes : " + (", ".join(missing) or "aucune") + ".")

    svg = composition_plan.render(
        columns, rows,
        elements=elements,
        traces=traces,
        keys=keys,
        title=plan.get("title", source.stem),
        notes=notes,
        tile=40)

    out = source.with_suffix(".svg")
    out.write_text(svg, encoding="utf-8")

    print(f"cases {len(traces)} · sujets {', '.join(sorted(set(subjects.values())))} · "
          f"cellule par défaut {default_cell}")
    for shape in EVERY_SHAPE:
        print(f"  shape-{shape:<6} {f'x{tally[shape]}' if shape in tally else 'ABSENTE'}")
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
