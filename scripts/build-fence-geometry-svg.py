#!/usr/bin/env python3
"""Draw, in vector, the geometry a fence assembly should have — no texture, no colour.

USAGE
  python3 scripts/build-fence-geometry-svg.py <plan.json>
  Writes <plan>-geometrie.svg beside it.
  python3 scripts/build-fence-geometry-svg.py -h|--help — this text

INTENTION
  A drawing meant to specify an image has to look like that image, or it specifies nothing. Two
  things make the difference here, and both were learned by getting them wrong:

  - A RUN IS DRAWN IN ONE PIECE. Drawing each cell's half-rail separately gave a chain of capsules,
    with two rounded ends meeting at every joint — an assembly that reads as beads, not as a fence.
    So the collinear cells are merged first, and each run becomes a single bar.
  - A POST IS A CYLINDER. Straight sides, an ellipse on top, a curved foot. A rounded rectangle with
    a disc perched above reads as a plank with a lid.

  The proportions are MEASURED on the image the generator produced (scripts/dev/measure-fence.py), not
  supposed: post diameter, rail thickness, the height of each rail. The drawing therefore specifies
  something already proved possible.

  Geometry only. Texture, colour and light belong to the image and never to what specifies it.
"""
import json
import sys
from pathlib import Path

# Measured on assets/poc/fence/usage-OB-010-v2.png, one cell being 192 px. Every value is a
# fraction of a cell, so the drawing follows the tile size wherever it is used.
POST_DIAMETER = 0.32
POST_HEIGHT = 0.58          # ground to cap; the cap stands above the upper rail
RAIL_THICKNESS = 0.16
RAIL_HEIGHTS = (0.42, 0.16)  # upper, lower — centre height above the ground line

TILE = 110                  # drawing size only; the whole figure scales with it
INK = "#20222a"
FILL = "#ffffff"
LINE = 2.2


def runs_of(cells, horizontal: bool):
    """Maximal straight sequences of connected cells, so each run is drawn as one bar.

    A run is grown from a cell that has no connected neighbour before it, and extended while the
    connection is declared on both sides. Two cells that merely touch never join a run.
    """
    inside, found = set(cells), []
    before, after = ("w", "e") if horizontal else ("n", "s")
    for cell in sorted(cells, key=lambda item: (item[1], item[0])):
        if before in cells[cell]:
            continue  # not the head of a run
        column, row, length = cell[0], cell[1], 0
        while after in cells.get((column + (length + 1 if horizontal else 0) - (0 if horizontal else 0),
                                  row), set()) if False else True:
            step = (column + length + 1, row) if horizontal else (column, row + length + 1)
            if after not in cells[(column + length, row) if horizontal else (column, row + length)]:
                break
            if step not in inside:
                break
            length += 1
        found.append((column, row, length))

    return found


def cylinder(cx, ground, diameter, height):
    """A post: straight sides, an ellipse on top, a curved foot — a cylinder, not a lidded plank."""
    radius, squash = diameter / 2, diameter / 3.2
    top = ground - height

    return [
        f'<path d="M {cx - radius:.1f} {top:.1f} L {cx - radius:.1f} {ground:.1f} '
        f'A {radius:.1f} {squash:.1f} 0 0 0 {cx + radius:.1f} {ground:.1f} '
        f'L {cx + radius:.1f} {top:.1f} Z" fill="{FILL}" stroke="{INK}" stroke-width="{LINE}"/>',
        f'<ellipse cx="{cx:.1f}" cy="{top:.1f}" rx="{radius:.1f}" ry="{squash:.1f}" '
        f'fill="{FILL}" stroke="{INK}" stroke-width="{LINE}"/>',
    ]


def bar(x1, y1, x2, y2, thickness):
    """One rail, drawn in a single piece from end to end."""
    if y1 == y2:
        return (f'<rect x="{x1:.1f}" y="{y1 - thickness / 2:.1f}" width="{x2 - x1:.1f}" '
                f'height="{thickness:.1f}" fill="{FILL}" stroke="{INK}" stroke-width="{LINE}"/>')

    return (f'<rect x="{x1 - thickness / 2:.1f}" y="{y1:.1f}" width="{thickness:.1f}" '
            f'height="{y2 - y1:.1f}" fill="{FILL}" stroke="{INK}" stroke-width="{LINE}"/>')


def build(source: Path) -> int:
    source = source.resolve()
    plan = json.loads(source.read_text(encoding="utf-8"))
    columns, rows = plan["grid"]["columns"], plan["grid"]["rows"]
    cells = {(cell["column"], cell["row"]): set(cell["joins"]) for cell in plan["cells"]}
    posts = {(cell["column"], cell["row"]): cell.get("posts", 1) for cell in plan["cells"]}

    thickness = RAIL_THICKNESS * TILE
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {columns * TILE} '
             f'{rows * TILE}" font-family="sans-serif">',
             f'<rect width="{columns * TILE}" height="{rows * TILE}" fill="#f6f2e8"/>']

    # Drawn row by row from north to south, so a southern piece covers the one behind it, exactly as
    # the world's depth sorting does. Within a row: what recedes, then the posts, then what comes
    # forward — a rail leaving southwards passes in front of its post.
    for row in range(1, rows + 1):
        behind, front = [], []
        for (column, cell_row), joins in sorted(cells.items()):
            if cell_row != row:
                continue
            cx, ground = (column - 0.5) * TILE, (cell_row - 0.5) * TILE
            for height in RAIL_HEIGHTS:
                y = ground - height * TILE
                if "n" in joins:
                    behind.append(bar(cx, y - TILE / 2, cx, y, thickness))
                if "s" in joins:
                    front.append(bar(cx, y, cx, y + TILE / 2, thickness))
        parts += behind

        for (column, cell_row), count in sorted(posts.items()):
            if cell_row != row:
                continue
            cx, ground = (column - 0.5) * TILE, (cell_row - 0.5) * TILE
            for offset in {0: [], 1: [0.0], 2: [-1 / 6, 1 / 6]}[count]:
                parts += cylinder(cx + offset * TILE, ground, POST_DIAMETER * TILE,
                                  POST_HEIGHT * TILE)
        parts += front

        # East-west rails last in the row: seen broadside, they pass in front of the posts they are
        # pegged to. Merged across cells so a straight run is one bar, without a joint every metre.
        for column, cell_row, length in runs_of(cells, horizontal=True):
            if cell_row != row:
                continue
            x1 = (column - 1) * TILE + TILE / 2
            x2 = (column + length - 1) * TILE + TILE / 2
            if "w" in cells[(column, row)]:
                x1 -= TILE / 2
            if "e" in cells[(column + length, row)] if (column + length, row) in cells else False:
                x2 += TILE / 2
            ground = (cell_row - 0.5) * TILE
            for height in RAIL_HEIGHTS:
                if x2 > x1:
                    parts.append(bar(x1, ground - height * TILE, x2, ground - height * TILE,
                                     thickness))

    parts.append("</svg>")
    target = source.with_name(source.stem + "-geometrie.svg")
    target.write_text("\n".join(parts), encoding="utf-8")

    print(f"géométrie écrite : {target.name} · {len(cells)} pièces")
    print(f"mesures de l'image : poteau {POST_DIAMETER} case, lisse {RAIL_THICKNESS}, "
          f"hauteurs {RAIL_HEIGHTS}")

    return 0


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        raise SystemExit(0)
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(build(Path(sys.argv[1])))
