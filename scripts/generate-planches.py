#!/usr/bin/env python3
"""Reference plates: fix the art direction on a lot of varied content.

Six plates are planned (see referentiels/visuel/planches-de-reference.md); this run produces the first
two, which are adjacent and share a path across their common edge.

Everything about frame, camera, light, scale and coherence comes from the conception's reference scene.
The style is anchored to the image the owner retained.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

STYLE = (
    "Art style: soft toon-shaded 3D render, sculpted rounded volumes, clear specular highlights and rim "
    "light, cel shading in two crisp bands, no outline."
)

ANCHOR = (
    "STYLE REFERENCE — ./da-b4-r15-scene.png is the exact target. Reproduce ITS rendering with no "
    "deviation: the same modelling of volumes, the same crisp two-band cel shading, the same frank "
    "saturated colours, the same amount of surface detail, the same degree of stylisation. If what you "
    "produce looks smoother, greyer, softer or more photographic than that image, it is wrong. Take ONLY "
    "the style from it — its layout and its creatures do not apply."
)

COMMON = """
FRAME AND SCALE — 1536 x 1152 pixels, representing a grid of 32 columns by 24 rows of square tiles. Do NOT
draw the grid. A standing human is 1 tile tall: one thirty-second of the image width — the reference scale.
A base creature is 1 tile. Buildings are far larger and are square to the map axes, never turned at an
angle; nothing sticks out sideways beyond its stated footprint.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, NO distant mountains against sky, no
vanishing point. Roofs and treetops seen from above.

LIGHT — sun from the UPPER LEFT, every shadow falling to the LOWER RIGHT. Shadows are SIMPLE: plain,
soft-edged, one per object. The image is BRIGHT with FRANK clear colours, never muted or washed out. No
deep shadow. Perfectly sharp edge to edge: no blur, no haze, no depth of field.

THE WORLD HAS LIVED — wear everywhere: weathered wood, moss and lichen at the foot of walls, mismatched
tiles, plants reclaiming corners. Nothing looks new or synthetic.

WATER FLOWS — any stream or river shows its direction: oriented ripples, eddies behind stones, grass bent
by the current.

INTERNAL COHERENCE — nothing ends in the void. A bridge lands on a path, or it is broken and the path
stops with it. A door opens onto an access. Stairs lead somewhere. A boat is moored or beached.

VARIETY IS THE POINT — few elements repeat. Different tree species, different path materials, every
building distinct from every other, including houses among themselves.

PEOPLE — humans of all real ethnicities, both genders, of visibly different trades, each doing something,
each facing a stated direction.

CREATURES — many different original creatures, none with a human face. Each wears ONE RUNE: a small
glowing symbol, ONE single continuous stroke, ONE colour, following the curve of its body like a natural
marking. A rune fits in about a QUARTER OF A TILE, roughly twelve pixels across — an absolute size, so on
a larger creature it looks tiny. No two creatures wear the same rune shape. Humans wear no rune.

No text, no interface, no logos, no grid lines.
"""

PLATES = {
    "p1-campagne": """
PLATE P1 — WOODED COUNTRYSIDE. A rich rural plate, densely filled and varied.

CONTENT — farms with barns and fenced yards, a working windmill, orchards in rows, hedgerows, a pond with
ducks and reeds, hay stacks, a well, vegetable plots, clearings, scattered boulders, several distinct tree
species: broad oaks, slim birches, dark firs, fruit trees in blossom.

PATHS — dirt tracks and grassy trails linking every building; a small stone bridge over a brook, landing
on a track at both ends. A MAIN DIRT ROAD runs horizontally along row 16 and LEAVES THE IMAGE at the RIGHT
EDGE on row 16 — it must reach the very edge cleanly, as it continues into the neighbouring plate.

PEOPLE — a farmer forking hay, facing right; a woman carrying a basket of apples, walking left; a miller
in the mill doorway, facing down; two children running along a track, facing down-right; an older man
mending a fence, kneeling, facing up.

CREATURES — at least seven different species going about their lives: one drinking at the pond's edge from
the bank, one dozing under an orchard tree, two of the same species chasing each other across a field,
one perched on a fence post watching, one following a farmer, one half hidden in tall grass.
""",
    "p2-bourg": """
PLATE P2 — MARKET TOWN. A dense built plate, every building different.

CONTENT — paved streets, a central square with a stone fountain, a covered market hall, a smithy with its
forge, a bakery with its oven chimney, a pottery workshop with drying racks, a two storey inn with a sign,
terraced houses each clearly distinct in width, roof shape, colour and materials, walled gardens behind
them, window boxes, washing lines, barrels, crates, a notice board.

PATHS — cobbled streets, one flagstone lane, a gravel alley. A COBBLED MAIN STREET runs horizontally along
row 16 and ENTERS THE IMAGE at the LEFT EDGE on row 16, arriving from the countryside — it must meet the
very edge cleanly. Another street leaves at the RIGHT EDGE on row 8.

PEOPLE — a blacksmith at the anvil, facing right; a baker setting bread on a stall, facing down; a potter
at the wheel, facing left; a merchant and a customer face to face at a stall, in conversation; a woman
drawing water at the fountain, facing up; a child chasing a creature across the square, facing left; a
guard leaning on a spear by the hall, facing down. All of visibly different origins.

CREATURES — several domesticated creatures in town: one harnessed to a small cart, one sleeping on a warm
doorstep, one perched on the market hall roof, one being fed at a stall, one trotting beside its trainer.
Each of a different species.
""",
}

arguments = []
for key, plate in PLATES.items():
    prompt = f"{STYLE}\n\n{ANCHOR}\n{COMMON}\n{plate}"
    (ASSETS / f"prompt-{key}.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/planche-{key}.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)
