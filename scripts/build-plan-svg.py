#!/usr/bin/env python3
"""Render each plate composition as a simple SVG plan.

Deliberately simplistic, per the operator: layout of the elements and their bounds, nothing more.
A 32x24 grid, one coloured rectangle per footprint with its label, one dot per inhabitant.
Plans are written next to the plates as plan-<plate>.svg and shown in the review page BEFORE any
generation is sent — a composition mistake caught on the plan saves a full generation.

The data below mirrors the CURRENT composition of each written plate. When a composition changes,
this file changes in the same gesture.
"""
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"
TILES_X, TILES_Y = 32, 24
TILE = 24  # SVG pixels per tile

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
DOTS = {"human": "#e04848", "creature": "#8a4fd0", "majestic": "#f0a000"}

# Each element: (type, c1, r1, c2, r2, label). Grid coordinates, inclusive, origin (1,1) top-left.
# Each inhabitant: (kind, c, r, label).
PLATES = {
    "p1-campagne": {
        "elements": [
            ("road", 1, 16, 32, 16, "route"),
            ("road", 12, 16, 12, 24, "route"),
            ("road", 8, 12, 8, 16, "acces ferme"), ("road", 19, 10, 19, 15, "acces grange"),
            ("road", 28, 11, 28, 16, "acces moulin"), ("road", 17, 16, 17, 18, "acces chaumiere"),
            # The brook runs straight down column 14: it no longer crosses the mill, the wheat field
            # nor any access path; the road crosses it once, on the bridge.
            ("water", 14, 1, 14, 24, "ru"),
            ("building", 13, 16, 15, 16, "pont"),
            ("building", 2, 2, 13, 11, "ferme"),
            ("building", 15, 3, 24, 9, "grange"),
            ("building", 26, 4, 31, 10, "moulin"),
            ("building", 15, 19, 23, 24, "chaumiere (porte en haut, 17)"),
            ("vegetation", 24, 17, 31, 23, "verger"),
            # Crops enlarged and doubled (operator, v7): a wider kitchen garden plus a second vegetable
            # field; the wheat moves clear of the mill access on column 28.
            ("field", 1, 12, 7, 15, "potager"),
            ("field", 2, 19, 7, 22, "legumes"),
            ("field", 24, 11, 27, 15, "ble"),
            ("vegetation", 2, 17, 7, 17, "haie"), ("vegetation", 15, 12, 18, 12, "haie"),
            # The oak is a multi-tile tree: a declared 3x3 footprint, crown wider still.
            ("vegetation", 9, 17, 11, 19, "chene (3x3)"), ("vegetation", 3, 18, 3, 18, ""),
            ("vegetation", 16, 14, 16, 14, ""), ("vegetation", 30, 2, 30, 2, ""),
            ("vegetation", 1, 8, 1, 8, ""), ("vegetation", 32, 12, 32, 12, ""),
            ("object", 22, 10, 22, 10, "meule"), ("object", 22, 15, 22, 15, "meule"),
            ("object", 23, 13, 23, 13, "meule"),
            ("object", 16, 10, 17, 10, "puits"), ("object", 10, 15, 11, 15, "charrette"),
            ("object", 12, 13, 12, 13, "abreuvoir"),
        ],
        "inhabitants": [
            ("human", 9, 13, "fermier"), ("human", 18, 16, ""), ("human", 28, 12, "meunier"),
            ("human", 20, 16, ""), ("human", 21, 16, ""),
            ("creature", 24, 16, ""), ("creature", 26, 20, ""), ("creature", 13, 14, ""),
            ("creature", 8, 18, ""), ("creature", 8, 19, ""),
            ("majestic", 9, 21, 10, 22, "majestueuse"),
        ],
    },
    "p2-bourg": {
        "elements": [
            ("road", 1, 16, 18, 16, "rue"),
            ("road", 18, 8, 18, 24, "rue"),
            ("road", 18, 8, 32, 8, "rue"),
            ("road", 22, 7, 22, 7, ""), ("road", 19, 12, 23, 12, "acces maison du potier"),
            # The camera looks steeply down: a building to the SOUTH raises its height over what sits
            # north of it. The house therefore goes north, the LOW workshop south — neither masks the
            # other (operator, 2026-08-03).
            ("road", 19, 20, 25, 20, "acces atelier"),
            ("road", 4, 17, 4, 17, ""), ("road", 8, 17, 8, 17, ""), ("road", 12, 17, 12, 17, ""),
            ("square", 10, 9, 17, 15, "place"),
            ("water", 13, 11, 14, 12, "fontaine"),
            # Paving belts (operator's rule): every non-adjoining building is surrounded by a one-tile
            # paved band, always joined to the street network. Each rect is the footprint PLUS its
            # belt, drawn before the building so only the belt shows.
            ("road", 1, 1, 10, 9, ""), ("road", 2, 9, 7, 13, ""),
            ("road", 19, 1, 32, 7, ""), ("road", 23, 9, 32, 18, ""),
            ("road", 25, 17, 32, 24, ""), ("road", 1, 17, 14, 24, "ceintures pavees"),
            ("building", 2, 1, 9, 8, "halle"),
            ("building", 20, 1, 31, 6, "boulangerie / forge / auberge"),
            ("building", 24, 10, 31, 17, "maison du potier (porte a gauche, 12)"),
            ("building", 26, 18, 31, 23, "atelier bas accole (porte a gauche, 20)"),
            ("building", 2, 18, 13, 24, "maisons mitoyennes"),
            ("building", 3, 10, 6, 12, "lavoir public"),
            ("road", 4, 13, 4, 15, "acces lavoir"),
            ("vegetation", 16, 17, 16, 17, "arbre"), ("vegetation", 21, 10, 21, 10, "arbre"),
            ("vegetation", 21, 22, 21, 22, "arbre"),
            ("field", 21, 18, 22, 19, "potager de pied de mur"),
            ("object", 11, 10, 12, 10, "etal"), ("object", 16, 10, 17, 10, "etal"),
            ("object", 15, 16, 16, 16, "charrette"), ("object", 9, 9, 9, 9, ""),
            ("object", 19, 15, 20, 15, "puits"), ("object", 29, 7, 29, 7, ""),
        ],
        "inhabitants": [
            ("human", 13, 13, "boulangere"), ("human", 26, 7, "forgeron"), ("human", 17, 12, "garde"),
            ("human", 11, 11, "marchand"), ("human", 24, 20, "potier"),
            ("human", 16, 16, ""), ("human", 17, 16, ""),
            ("creature", 12, 15, ""), ("creature", 20, 16, ""), ("creature", 6, 9, ""),
            ("majestic", 14, 9, 15, 10, "majestueuse"),
        ],
    },
    "p3-contreforts": {
        "elements": [
            ("rock", 1, 1, 13, 4, "paroi montagneuse"),
            ("rock", 16, 1, 19, 9, "paroi"),
            ("rock", 28, 1, 32, 8, "paroi"),
            ("rock", 29, 9, 32, 13, "eboulis"),
            ("road", 1, 8, 10, 8, "sentier"),
            ("road", 10, 8, 10, 14, ""), ("road", 10, 14, 26, 14, ""),
            ("road", 26, 14, 26, 24, "sentier"),
            ("road", 5, 9, 5, 11, "acces bergerie"),
            ("road", 23, 8, 23, 13, "acces mine"),
            ("road", 27, 17, 27, 17, "acces tour"),
            # Dry crevasse, two tiles wide, no water at all; the suspension bridge is its only crossing.
            ("rock", 14, 5, 15, 13, "crevasse seche (2 cases, sans eau)"),
            ("rock", 14, 15, 15, 15, ""),
            ("building", 14, 14, 15, 14, "pont suspendu"),
            ("building", 2, 12, 9, 19, "bergerie (porte en haut, 5)"),
            ("field", 2, 20, 9, 23, "enclos (murs seuls, interieur visible)"),
            ("vegetation", 11, 20, 25, 24, "foret de pins dense"),
            ("vegetation", 27, 20, 32, 24, "foret de pins dense"),
            ("building", 20, 1, 27, 7, "entree de mine (porte en bas, 23)"),
            ("building", 28, 16, 31, 19, "tour en ruine"),
            ("vegetation", 4, 6, 4, 6, "pin"), ("vegetation", 8, 6, 8, 6, "pin"),
            ("vegetation", 18, 18, 18, 18, "pin"), ("vegetation", 30, 14, 30, 14, "pin"),
            ("rock", 17, 11, 18, 12, "rochers"), ("rock", 7, 9, 8, 10, "rochers"),
            ("rock", 23, 17, 24, 18, "rochers"), ("rock", 12, 16, 13, 17, "rochers"),
            ("object", 21, 9, 22, 9, "chariot de mine"),
        ],
        "inhabitants": [
            ("human", 5, 15, "berger"), ("human", 23, 8, "mineur"), ("human", 12, 14, ""),
            ("creature", 4, 21, ""), ("creature", 7, 21, ""), ("creature", 16, 10, ""),
            ("creature", 29, 12, ""),
            ("majestic", 21, 10, 22, 11, "majestueuse"),
        ],
    },
    "p5-falaise": {
        "elements": [
            # Geometry decided by the operator (Q3): the cliff runs the WHOLE bottom edge and climbs the
            # right edge only below row 12; the sea lies beyond it, lower; the right joint is a wooden
            # walkway over the sea, reached by the stair carved down from the clifftop path.
            ("rock", 1, 21, 30, 22, "falaise (a-pic) sur tout le bord bas"),
            ("rock", 29, 13, 30, 19, "falaise (bord droit, sous la moitie)"),
            ("water", 1, 23, 32, 24, "mer en contrebas"),
            ("water", 31, 13, 32, 22, "mer"),
            ("rock", 5, 23, 7, 24, "rochers au pied"),
            ("rock", 18, 23, 20, 24, "rochers au pied"),
            ("road", 1, 12, 18, 12, "chemin"),
            ("road", 18, 1, 18, 12, "chemin"),
            ("road", 18, 12, 18, 20, ""), ("road", 18, 20, 28, 20, "chemin du bord de falaise"),
            ("road", 29, 20, 30, 20, "escalier taille (chemin -> passerelle)"),
            ("building", 31, 20, 32, 20, "passerelle au-dessus de la mer"),
            ("road", 25, 7, 25, 20, "acces phare"),
            ("road", 6, 12, 6, 13, "acces cabanon"),
            ("building", 24, 4, 27, 7, "phare elance (porte en bas, 25)"),
            ("building", 3, 13, 10, 20, "cabanon (porte en haut, 6)"),
            ("object", 12, 16, 15, 17, "filets a secher"),
            ("vegetation", 5, 4, 5, 4, "arbre couche"), ("vegetation", 13, 6, 13, 6, ""),
            ("vegetation", 10, 3, 12, 5, "ajoncs"), ("vegetation", 20, 16, 22, 18, "ajoncs"),
            ("vegetation", 8, 8, 10, 10, "bruyere"),
            ("rock", 2, 8, 3, 9, "rochers"), ("rock", 14, 9, 15, 10, "rochers"),
            ("object", 8, 11, 8, 11, "casiers"),
        ],
        "inhabitants": [
            ("human", 26, 11, "gardienne du phare"), ("human", 13, 15, "pecheuse"),
            ("human", 19, 13, ""), ("human", 27, 20, "pecheur"), ("human", 15, 12, "enfant"),
            ("creature", 7, 6, ""), ("creature", 21, 21, ""), ("creature", 30, 20, ""),
            ("creature", 16, 18, ""), ("creature", 9, 4, ""),
            ("majestic", 4, 10, 5, 11, "majestueuse"),
        ],
    },
    "p6-plage": {
        "elements": [
            # The path enters at the P5 joint (edge, row 20) then climbs inland: the shore stays an
            # open sand beach, not a trodden waterfront.
            ("road", 1, 20, 4, 20, "chemin (raccord P5)"),
            ("road", 4, 16, 4, 20, ""), ("road", 4, 16, 15, 16, "chemin dans les terres"),
            ("road", 26, 1, 26, 12, "chemin (raccord P3)"),
            ("road", 15, 12, 26, 12, "chemin"),
            ("road", 5, 10, 5, 15, "acces cabane 1"),
            ("road", 15, 11, 15, 16, "acces cabane 2"),
            ("road", 16, 13, 18, 13, "acces appontement"),
            ("water", 1, 22, 32, 24, "mer"), ("water", 20, 14, 32, 21, "mer"),
            ("building", 18, 13, 19, 22, "appontement"),
            ("building", 2, 2, 9, 9, "cabane de pecheur (porte en bas, 5)"),
            ("building", 12, 3, 19, 10, "cabane de pecheur (porte en bas, 15)"),
            ("field", 6, 12, 11, 15, "dunes"),
            ("vegetation", 2, 11, 2, 11, "palmier"), ("vegetation", 10, 13, 10, 13, "palmier"),
            ("vegetation", 21, 2, 21, 2, "palmier"), ("vegetation", 29, 4, 29, 4, "palmier"),
            # Land side widened (v4 measured 38.9% of load): coastal planting spread over more tiles
            # so the sand is punctuated, not bare.
            ("vegetation", 6, 12, 8, 13, "malcolmie des cotes"),
            ("vegetation", 11, 18, 14, 20, "malcolmie des cotes"),
            ("vegetation", 22, 5, 25, 8, "plantes littorales"),
            ("vegetation", 28, 8, 31, 11, "plantes littorales"),
            ("vegetation", 8, 2, 10, 4, "plantes littorales"),
            ("vegetation", 20, 21, 23, 21, "laisse de mer (algues, bois flotte)"),
            ("object", 5, 18, 6, 18, "barque"), ("object", 13, 19, 14, 19, "barque"),
            ("object", 21, 13, 21, 13, "casiers"), ("object", 16, 13, 16, 13, "casiers"),
            ("rock", 28, 12, 29, 13, "rochers"), ("rock", 2, 16, 3, 17, "rochers"),
            ("object", 4, 21, 4, 21, "coquillages"), ("object", 9, 21, 9, 21, "coquillages"),
            ("object", 15, 21, 15, 21, "coquillages"), ("object", 24, 20, 24, 20, "coquillages"),
        ],
        "inhabitants": [
            ("human", 10, 20, "pecheuse"), ("human", 19, 16, "pecheur"), ("human", 27, 8, ""),
            ("creature", 7, 19, ""), ("creature", 24, 18, ""), ("creature", 30, 22, ""),
            ("majestic", 12, 13, 13, 14, "majestueuse"),
        ],
    },
    "p4-marais": {
        "elements": [
            # Water first, so the walkways read as passing over it: irregular pools linked by slow
            # channels draining from (30,3) towards (4,22).
            ("water", 27, 2, 31, 7, "mare"),
            ("water", 21, 6, 27, 10, "chenal"),
            ("water", 14, 9, 21, 12, "mare"),
            ("water", 8, 11, 14, 16, "chenal"),
            ("water", 3, 14, 9, 18, "mare"),
            ("water", 2, 18, 7, 22, "chenal vers (4,22)"),
            ("water", 23, 12, 28, 14, "mare"),
            ("road", 12, 1, 12, 20, "passerelle"),
            ("road", 12, 12, 32, 12, "passerelle"),
            ("road", 5, 8, 12, 8, ""), ("road", 13, 8, 14, 8, "acces sechoir"),
            ("road", 20, 12, 20, 20, ""),
            ("building", 2, 2, 13, 11, "hutte pilotis"),
            ("building", 21, 15, 31, 23, "hutte pilotis"),
            ("building", 15, 6, 18, 8, "sechoir"),
            ("vegetation", 4, 17, 4, 17, "saule"), ("vegetation", 8, 4, 8, 4, "saule"),
            ("vegetation", 17, 19, 17, 19, "saule"), ("vegetation", 24, 4, 24, 4, "saule"),
            ("vegetation", 29, 20, 29, 20, "saule"),
            ("vegetation", 2, 13, 2, 13, "mangrove"), ("vegetation", 9, 21, 9, 21, "mangrove"),
            ("vegetation", 16, 16, 16, 16, "mangrove"), ("vegetation", 26, 10, 26, 10, "mangrove"),
            ("vegetation", 30, 6, 30, 6, "mangrove"), ("vegetation", 15, 3, 15, 3, "mangrove"),
            ("vegetation", 28, 14, 28, 14, "mangrove"),
            ("water", 10, 15, 10, 15, "nenuphars"), ("water", 25, 18, 25, 18, "nenuphars"),
            ("water", 6, 6, 6, 6, "nenuphars"),
            ("object", 14, 13, 14, 13, "barque"), ("object", 7, 22, 7, 22, "barque"),
            ("object", 17, 17, 17, 17, "nasse"), ("object", 27, 7, 27, 7, "nasse"),
        ],
        "inhabitants": [
            ("human", 10, 8, "tourbier"), ("human", 16, 12, "pecheuse"), ("human", 20, 18, "enfant"),
            ("creature", 6, 15, ""), ("creature", 25, 11, ""), ("creature", 28, 17, ""),
            ("creature", 18, 21, ""), ("creature", 19, 22, ""),
            ("majestic", 7, 3, 8, 4, "majestueuse"),
        ],
    },
}


def render(key: str, plate: dict) -> str:
    width, height = TILES_X * TILE, TILES_Y * TILE
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height + 30}" '
        f'font-family="sans-serif">',
        # Full-height background, legend included: the page behind may be dark.
        f'<rect width="{width}" height="{height + 30}" fill="#f6f2e8"/>',
    ]
    for kind, c1, r1, c2, r2, label in plate["elements"]:
        x, y = (c1 - 1) * TILE, (r1 - 1) * TILE
        w, h = (c2 - c1 + 1) * TILE, (r2 - r1 + 1) * TILE
        # A single-tile vegetation element is a tree: one tile of trunk on the ground, but its crown
        # projects wider. The dashed circle shows the occupied zone by projection (3 tiles across).
        if kind == "vegetation" and c1 == c2 and r1 == r2:
            parts.append(f'<circle cx="{x + TILE / 2}" cy="{y + TILE / 2}" r="{TILE * 1.5}" '
                         f'fill="{COLORS[kind]}" fill-opacity="0.3" stroke="{COLORS[kind]}" '
                         f'stroke-dasharray="4 3"/>')
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{COLORS[kind]}" '
                     f'fill-opacity="0.75" stroke="#00000040"/>')
        if label:
            parts.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 4}" text-anchor="middle" '
                         f'font-size="11" fill="#1d1a24">{label}</text>')
    # Grid above surfaces, light, so bounds stay readable.
    for column in range(TILES_X + 1):
        x = column * TILE
        parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="#00000018"/>')
    for row in range(TILES_Y + 1):
        y = row * TILE
        parts.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#00000018"/>')
    for inhabitant in plate["inhabitants"]:
        # (kind, c, r, label) for a one-tile inhabitant; (kind, c1, r1, c2, r2, label) for a larger
        # one — its real footprint is drawn, a dot cannot show a two-tile creature.
        if len(inhabitant) == 6:
            kind, c1, r1, c2, r2, label = inhabitant
            x, y = (c1 - 1) * TILE, (r1 - 1) * TILE
            w, h = (c2 - c1 + 1) * TILE, (r2 - r1 + 1) * TILE
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{TILE / 2}" '
                         f'fill="{DOTS[kind]}" fill-opacity="0.85" stroke="#fff" stroke-width="2"/>')
            x, y = x + w / 2, y + h / 2
        else:
            kind, c, r, label = inhabitant
            x, y = (c - 0.5) * TILE, (r - 0.5) * TILE
            parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{DOTS[kind]}" stroke="#fff" '
                         f'stroke-width="2"/>')
        if label:
            parts.append(f'<text x="{x}" y="{y - 10}" text-anchor="middle" font-size="10" '
                         f'fill="#1d1a24">{label}</text>')
    legend = [("bâtiment", COLORS["building"], "rect"), ("voie", COLORS["road"], "rect"),
              ("eau", COLORS["water"], "rect"), ("végétation", COLORS["vegetation"], "rect"),
              ("culture", COLORS["field"], "rect"), ("roche", COLORS["rock"], "rect"),
              ("objet", COLORS["object"], "rect"),
              ("humain", DOTS["human"], "dot"), ("créature", DOTS["creature"], "dot"),
              ("majestueuse", DOTS["majestic"], "dot")]
    x = 4
    for label, color, shape in legend:
        # Inhabitants are dots on the plan: the legend shows them as dots too.
        if shape == "dot":
            parts.append(f'<circle cx="{x + 6}" cy="{height + 14}" r="6" fill="{color}" '
                         f'stroke="#fff" stroke-width="2"/>')
        else:
            parts.append(f'<rect x="{x}" y="{height + 8}" width="12" height="12" fill="{color}"/>')
        parts.append(f'<text x="{x + 16}" y="{height + 18}" font-size="11" fill="#1d1a24">{label}</text>')
        x += 16 + 7 * len(label) + 12
    parts.append("</svg>")

    return "\n".join(parts)


def tiles(c1, r1, c2, r2):
    return {(c, r) for c in range(c1, c2 + 1) for r in range(r1, r2 + 1)}


def check(key: str, plate: dict) -> list:
    """Coherence checks on the composition data. A plan that fails does not ship."""
    faults = []
    roads = set()
    for kind, c1, r1, c2, r2, label in plate["elements"]:
        if kind in ("road", "square"):  # a paved square serves the buildings that touch it
            roads |= tiles(c1, r1, c2, r2)
    for kind, c1, r1, c2, r2, label in plate["elements"]:
        # An obstacle never sits on a way: nothing blocks a road unless it is a deliberate ruin.
        if kind in ("rock", "vegetation") and tiles(c1, r1, c2, r2) & roads:
            faults.append(f"{key}: '{label or kind}' ({c1},{r1})-({c2},{r2}) blocks a road")
        # Every building is served: at least one road tile touches its footprint (bridge-like
        # structures that sit ON the way count as served by construction).
        if kind == "building":
            footprint = tiles(c1, r1, c2, r2)
            reach = tiles(c1 - 1, r1 - 1, c2 + 1, r2 + 1)
            if not (reach & roads):
                faults.append(f"{key}: building '{label or kind}' ({c1},{r1})-({c2},{r2}) "
                              f"has no access road")
    return faults


all_faults = []
for key, plate in PLATES.items():
    all_faults += check(key, plate)

if all_faults:
    for fault in all_faults:
        print(f"FAULT {fault}")
    raise SystemExit(1)

for key, plate in PLATES.items():
    target = ASSETS / f"plan-{key}.svg"
    target.write_text(render(key, plate), encoding="utf-8")
    print(f"OK {target.name}")
print("COHERENCE OK: no obstacle on a road, every building served")
