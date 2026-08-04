#!/usr/bin/env python3
"""The composition plan: the one way a composition is drawn before anything is generated.

A composition plan is a FLAT plan seen from above — never a perspective, never a rendering. It shows
where things sit and how much ground they take, and nothing else: a grid of cells, one coloured
rectangle per footprint with its label, a line through the cell centres for anything that runs and
connects, a dot per inhabitant, a legend. It is deliberately plain: a plan is read to catch a layout
mistake, and a mistake is caught faster on flat colour than on a drawing.

It is produced BEFORE any generation is ordered, and it carries checks that BLOCK: a plan whose
coherence fails does not ship, so the fault costs a plan and never a generation.

This module holds the drawing and the generic checks. Every plan — reference plates, asset sets, the
model park — goes through it, so no two plans can drift apart in how they read.
"""

TILE = 24  # SVG pixels per cell; a plan is read on screen, this is a drawing size, not a world size.

COLORS = {
    "building": "#c9885a",
    "road": "#d8b56e",
    "water": "#7fd4d4",
    "vegetation": "#7ab648",
    "field": "#cadb8e",
    "square": "#e2d3ae",
    "object": "#a89ec4",
    "rock": "#9a938c",
}
INK = "#000000"  # The trace is drawn thin and black: it is not a kind, it carries no colour of its own.

# A plan may hold subjects the palette above knows nothing about — a plan names its subjects by
# their inventory code. Each unknown code takes the next colour here, in order of appearance, so a
# plan reads the same every time it is rendered.
SPARE = ["#a89ec4", "#7ab648", "#d8b56e", "#7fd4d4", "#c9885a", "#cadb8e", "#9a938c", "#e2d3ae"]


def palette(kinds):
    """The colour of every kind a plan uses: the known ones keep theirs, the rest take a spare."""
    chosen = {}
    spare = list(SPARE)
    for kind in kinds:
        if kind in COLORS:
            chosen[kind] = COLORS[kind]
        else:
            chosen[kind] = spare.pop(0) if spare else "#b9b3c6"

    return chosen
DOTS = {"human": "#e04848", "creature": "#8a4fd0", "majestic": "#f0a000"}

LEGEND = [
    ("bâtiment", "building"), ("voie", "road"), ("eau", "water"), ("végétation", "vegetation"),
    ("culture", "field"), ("roche", "rock"), ("objet", "object"),
]

# The four edges of a cell, in the order the design fixes them: n, e, s, w.
EDGES = ("n", "e", "s", "w")
OPPOSITE = {"n": "s", "s": "n", "e": "w", "w": "e"}
STEP = {"n": (0, -1), "s": (0, 1), "e": (1, 0), "w": (-1, 0)}


def tiles(c1, r1, c2, r2):
    """Every cell of a footprint given by its inclusive corners."""
    return {(c, r) for c in range(c1, c2 + 1) for r in range(r1, r2 + 1)}


def shape_of(joined):
    """The shape name of a cell from the edges its trace joins, always in n, e, s, w order."""
    return "shape-" + "".join(edge for edge in EDGES if edge in joined)


def check_traces(traces, columns, rows):
    """Neighbour agreement, by calculation: what joins an edge must be joined back from the other side.

    traces maps (column, row) to the set of edges the trace joins in that cell. Returns the faults,
    empty when the layout holds.
    """
    faults = []
    for (column, row), joined in sorted(traces.items()):
        for edge in sorted(joined):
            dx, dy = STEP[edge]
            neighbour = (column + dx, row + dy)
            if not (1 <= neighbour[0] <= columns and 1 <= neighbour[1] <= rows):
                faults.append(f"({column},{row}) joins {edge} but there is nothing behind that edge")
                continue
            facing = traces.get(neighbour)
            if facing is None:
                faults.append(f"({column},{row}) joins {edge} but ({neighbour[0]},{neighbour[1]}) "
                              f"carries no trace")
            elif OPPOSITE[edge] not in facing:
                faults.append(f"({column},{row}) joins {edge} but ({neighbour[0]},{neighbour[1]}) "
                              f"does not join back")
    return faults


def check_layout(elements):
    """The generic layout rules: nothing blocks a way, every building is served.

    Only applied to what declares roads and buildings; a plan without them simply passes.
    """
    faults = []
    ways = set()
    for kind, c1, r1, c2, r2, label in elements:
        if kind in ("road", "square"):
            ways |= tiles(c1, r1, c2, r2)
    if not ways:
        return faults
    for kind, c1, r1, c2, r2, label in elements:
        if kind in ("rock", "vegetation") and tiles(c1, r1, c2, r2) & ways:
            faults.append(f"'{label or kind}' ({c1},{r1})-({c2},{r2}) blocks a way")
        if kind == "building" and not (tiles(c1 - 1, r1 - 1, c2 + 1, r2 + 1) & ways):
            faults.append(f"building '{label or kind}' ({c1},{r1})-({c2},{r2}) has no access")
    return faults


def _trace_marks(traces, tile):
    """A trace drawn from what the cell DECLARES: a dot at its centre, a branch to each edge it joins.

    Two connected cells each draw a branch to the edge they share, so the two meet into one
    continuous line crossing that edge. Two cells that merely touch draw nothing between them, and
    the gap is the information. A connection declared on one side only leaves a branch stopping at
    the edge with nothing facing it — the fault is visible, not just caught by the check.
    """
    parts = []
    width = max(1.0, tile * 0.04)
    for (column, row), joined in sorted(traces.items()):
        cx, cy = (column - 0.5) * tile, (row - 0.5) * tile
        for edge in sorted(joined):
            dx, dy = STEP[edge]
            parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + dx * tile / 2}" '
                         f'y2="{cy + dy * tile / 2}" stroke="{INK}" '
                         f'stroke-width="{width}" stroke-linecap="butt"/>')
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{width * 1.4}" fill="{INK}"/>')
    return parts


def _folded(notes, canvas, char=5.8):
    """Every note broken into lines that fit the canvas, keeping its own leading indentation.

    A note is written as one sentence by its caller; where it wraps is a matter of drawing, so it is
    decided here and nowhere else.
    """
    lines = []
    for note in notes:
        indent = note[:len(note) - len(note.lstrip())]
        room = max(20, int((canvas - 8 - len(indent) * char) / char))
        current = ""
        for word in note.split():
            if current and len(current) + 1 + len(word) > room:
                lines.append(indent + current)
                current = word
            else:
                current = f"{current} {word}".strip()
        lines.append(indent + current)

    return lines


def render(columns, rows, elements=(), inhabitants=(), traces=None, keys=None, title="", notes=(),
           legend_labels=None, tile=TILE):
    """The plan itself. Coordinates are cell coordinates, inclusive, origin (1,1) at the top left.

    A plan says very little on purpose: which cells a thing occupies, and — for anything that runs
    and connects — which of its neighbours it actually joins. Adjacency is not connection: two
    fences can stand side by side without meeting, so the connections are declared, never derived.
    """
    traces = traces or {}
    # Every kind used gets a colour: the palette's own for the kinds it knows, a spare for a subject
    # code it has never seen. Resolved once here so the same kind is the same colour everywhere.
    tint = palette(dict.fromkeys(kind for kind, *_ in elements))
    width, height = columns * tile, rows * tile
    top = 26 if title else 0
    # The canvas is sized on the DRAWING, and the text folds to fit it — never the reverse. Letting a
    # long legend stretch the canvas left the plan alone in a corner of a page four times too wide.
    canvas = max(width, 720)
    notes = _folded(notes, canvas)
    bottom = 30 + 14 * len(notes)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {canvas:.0f} {height + top + bottom}" font-family="sans-serif">',
        f'<rect width="{canvas:.0f}" height="{height + top + bottom}" fill="#f6f2e8"/>',
    ]
    if title:
        parts.append(f'<text x="4" y="17" font-size="14" font-weight="600" fill="#1d1a24">'
                     f'{title}</text>')
    parts.append(f'<g transform="translate(0,{top})">')

    for kind, c1, r1, c2, r2, label in elements:
        x, y = (c1 - 1) * tile, (r1 - 1) * tile
        w, h = (c2 - c1 + 1) * tile, (r2 - r1 + 1) * tile
        # A single-cell vegetation element is a tree: its crown projects wider than its trunk.
        if kind == "vegetation" and c1 == c2 and r1 == r2:
            parts.append(f'<circle cx="{x + tile / 2}" cy="{y + tile / 2}" r="{tile * 1.5}" '
                         f'fill="{tint[kind]}" fill-opacity="0.3" stroke="{tint[kind]}" '
                         f'stroke-dasharray="4 3"/>')
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{tint[kind]}" '
                     f'fill-opacity="0.75" stroke="#00000040"/>')
        if label:
            parts.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 4}" text-anchor="middle" '
                         f'font-size="11" fill="#1d1a24">{label}</text>')

    parts += _trace_marks(traces, tile)

    # One short key per DISTINCT piece, repeated wherever that same piece is laid. Two cells bearing
    # the same key are the same sprite, so the plan doubles as the cutting map. The key sits in the
    # cell's top-left corner: the trace runs from the centre to the edge midpoints and never goes
    # there, so nothing overlaps and the letter stays readable at any tile size.
    for (column, row), key in sorted((keys or {}).items()):
        x, y = (column - 1) * tile, (row - 1) * tile
        parts.append(f'<rect x="{x + 1.5}" y="{y + 1.5}" width="{tile * 0.30}" '
                     f'height="{tile * 0.30}" rx="{tile * 0.06}" fill="#f6f2e8" '
                     f'fill-opacity="0.88"/>')
        parts.append(f'<text x="{x + 1.5 + tile * 0.15}" y="{y + 1.5 + tile * 0.235}" '
                     f'text-anchor="middle" font-size="{tile * 0.22:.1f}" font-weight="700" '
                     f'fill="{INK}">{key}</text>')

    # Grid above the surfaces, light, so bounds stay readable.
    for column in range(columns + 1):
        x = column * tile
        parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="#00000018"/>')
    for row in range(rows + 1):
        y = row * tile
        parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#00000018"/>')

    for inhabitant in inhabitants:
        # (kind, c, r, label) for a one-cell inhabitant; (kind, c1, r1, c2, r2, label) for a larger
        # one — its real footprint is drawn, a dot cannot show a two-cell creature.
        if len(inhabitant) == 6:
            kind, c1, r1, c2, r2, label = inhabitant
            x, y = (c1 - 1) * tile, (r1 - 1) * tile
            w, h = (c2 - c1 + 1) * tile, (r2 - r1 + 1) * tile
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{tile / 2}" '
                         f'fill="{DOTS[kind]}" fill-opacity="0.85" stroke="#fff" stroke-width="2"/>')
            x, y = x + w / 2, y + h / 2
        else:
            kind, c, r, label = inhabitant
            x, y = (c - 0.5) * tile, (r - 0.5) * tile
            parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{DOTS[kind]}" stroke="#fff" '
                         f'stroke-width="2"/>')
        if label:
            parts.append(f'<text x="{x}" y="{y - 10}" text-anchor="middle" font-size="10" '
                         f'fill="#1d1a24">{label}</text>')

    # Legend: only the kinds actually used, so a plan never explains what it does not show. Known
    # kinds keep their French label; a subject code stands for itself, it needs no translation.
    named = dict((kind, label) for label, kind in LEGEND)
    x = 4
    for kind in dict.fromkeys(kind for kind, *_ in elements):
        label = named.get(kind, legend_labels.get(kind, kind) if legend_labels else kind)
        parts.append(f'<rect x="{x}" y="{height + 8}" width="12" height="12" fill="{tint[kind]}"/>')
        parts.append(f'<text x="{x + 16}" y="{height + 18}" font-size="11" fill="#1d1a24">'
                     f'{label}</text>')
        x += 16 + 7 * len(label) + 12
    for kind in ("human", "creature", "majestic"):
        if not any(inhabitant[0] == kind for inhabitant in inhabitants):
            continue
        label = {"human": "humain", "creature": "créature", "majestic": "majestueuse"}[kind]
        parts.append(f'<circle cx="{x + 6}" cy="{height + 14}" r="6" fill="{DOTS[kind]}" '
                     f'stroke="#fff" stroke-width="2"/>')
        parts.append(f'<text x="{x + 16}" y="{height + 18}" font-size="11" fill="#1d1a24">'
                     f'{label}</text>')
        x += 16 + 7 * len(label) + 12

    for index, note in enumerate(notes):
        parts.append(f'<text x="4" y="{height + 34 + 14 * index}" font-size="11" fill="#5c5468">'
                     f'{note}</text>')

    parts.append("</g></svg>")

    return "\n".join(parts)
