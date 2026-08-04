#!/usr/bin/env python3
"""Render each plate's composition as an ASCII plan.

An image cannot be checked against a composition by eye alone. The plan draws the same data the prompt is
built from, so the intent is readable tile by tile: where the paths run, where they reach the border, what
covers the ground, who stands where.

The plan is the INTENT, not the produced image: comparing the two is exactly how a deviation is found.
"""
from pathlib import Path

WIDTH, HEIGHT = 32, 24
OUTPUT = Path(__file__).resolve().parent.parent / "doc" / "conception" / "referentiels" / "visuel" / "plans-ascii.md"

LEGEND = [
    (".", "sol nu du biome (herbe, sable, roche selon la planche)"),
    ("~", "eau"),
    ("≈", "eau peu profonde, vasière, écume"),
    ("=", "chemin de terre"),
    (":", "passerelle de planches"),
    ("%", "sol dur : pavés, dalles, pierre"),
    ("B", "pont ou gué"),
    ("S", "escalier"),
    ("#", "bâtiment (emprise au sol)"),
    ("D", "porte du bâtiment"),
    ("+", "aménagement clos : potager, enclos, terrain"),
    ("T", "arbre"),
    ('"', "roseaux, buissons, hautes herbes"),
    ("f", "culture : champ, verger, plantation"),
    ("o", "objet posé"),
    ("H", "humain"),
    ("c", "créature"),
    ("M", "créature majestueuse"),
]


class Plan:
    """A tile grid that elements are painted onto, in the order the composition states them."""

    def __init__(self, title, subtitle, ground="."):
        self.title = title
        self.subtitle = subtitle
        self.grid = [[ground] * WIDTH for _ in range(HEIGHT)]

    def rect(self, symbol, c1, r1, c2, r2):
        for row in range(r1 - 1, r2):
            for column in range(c1 - 1, c2):
                if 0 <= row < HEIGHT and 0 <= column < WIDTH:
                    self.grid[row][column] = symbol

    def line(self, symbol, c1, r1, c2, r2):
        self.rect(symbol, min(c1, c2), min(r1, r2), max(c1, c2), max(r1, r2))

    def put(self, symbol, column, row):
        if 1 <= column <= WIDTH and 1 <= row <= HEIGHT:
            self.grid[row - 1][column - 1] = symbol

    def render(self):
        header = "    " + "".join(str(c % 10) for c in range(1, WIDTH + 1))
        lines = [header, "   +" + "-" * WIDTH + "+"]
        for index, row in enumerate(self.grid, start=1):
            lines.append(f"{index:2d} |" + "".join(row) + f"| {index:2d}")
        lines.append("   +" + "-" * WIDTH + "+")
        lines.append(header)

        return "\n".join(lines)


def campagne():
    plan = Plan("P1 — Campagne boisée", "sol : prairie")
    plan.line("=", 1, 16, 32, 16)
    plan.line("=", 12, 16, 12, 24)
    plan.line("=", 8, 12, 8, 16)
    plan.line("=", 22, 11, 22, 16)
    plan.line("=", 17, 16, 17, 19)
    plan.line("~", 28, 1, 28, 13)
    plan.line("~", 20, 13, 28, 13)
    plan.line("~", 20, 13, 20, 24)
    plan.rect("#", 2, 2, 13, 11)
    plan.put("D", 8, 11)
    plan.rect("#", 15, 3, 24, 9)
    plan.put("D", 19, 9)
    plan.rect("#", 26, 4, 31, 10)
    plan.put("D", 28, 10)
    plan.rect("#", 14, 19, 23, 24)
    plan.put("D", 17, 19)
    plan.rect("f", 24, 17, 31, 23)
    plan.rect("+", 2, 12, 7, 15)
    plan.rect("f", 26, 11, 31, 15)
    plan.line('"', 2, 16, 7, 16)
    plan.line('"', 14, 12, 19, 12)
    plan.line("B", 20, 16, 21, 16)
    for column, row in [(10, 18), (3, 18), (15, 14), (30, 2), (1, 8), (31, 20)]:
        plan.put("T", column, row)
    for column, row in [(25, 10), (27, 16), (29, 16), (14, 10), (10, 15), (16, 10)]:
        plan.put("o", column, row)
    for column, row in [(9, 13), (14, 16), (28, 11), (18, 16), (19, 16)]:
        plan.put("H", column, row)
    for column, row in [(24, 16), (26, 20), (21, 14), (5, 17), (6, 18)]:
        plan.put("c", column, row)
    plan.rect("M", 10, 20, 11, 21)

    return plan


def marais():
    plan = Plan("P4 — Marais", "sol : vase et eau peu profonde", "≈")
    plan.line("~", 1, 1, 32, 24)
    plan.line('"', 1, 1, 32, 5)
    plan.line('"', 1, 20, 32, 24)
    plan.line('"', 24, 6, 32, 19)
    plan.line(":", 12, 1, 12, 20)
    plan.line(":", 12, 12, 32, 12)
    plan.line(":", 5, 8, 12, 8)
    plan.line(":", 20, 12, 20, 20)
    plan.rect("#", 2, 2, 13, 11)
    plan.put("D", 7, 11)
    plan.rect("#", 21, 15, 31, 23)
    plan.put("D", 20, 20)
    plan.rect("#", 15, 6, 18, 8)
    for column, row in [(4, 17), (8, 4), (17, 19), (24, 4), (29, 20),
                        (2, 13), (9, 21), (16, 16), (26, 10), (30, 6)]:
        plan.put("T", column, row)
    for column, row in [(14, 13), (7, 22), (17, 17), (27, 7), (14, 14), (21, 20)]:
        plan.put("o", column, row)
    for column, row in [(10, 8), (16, 12), (20, 18)]:
        plan.put("H", column, row)
    for column, row in [(6, 15), (25, 11), (28, 17), (18, 21), (19, 22)]:
        plan.put("c", column, row)
    plan.rect("M", 7, 3, 8, 4)

    return plan


def falaise():
    plan = Plan("P5 — Falaise", "sol : pelouse rase sur roche")
    plan.rect("~", 26, 1, 32, 24)
    plan.line("≈", 25, 1, 25, 24)
    plan.line("=", 1, 10, 14, 10)
    plan.line("=", 14, 10, 14, 20)
    plan.line("=", 14, 20, 24, 20)
    plan.line("=", 4, 14, 14, 14)
    plan.line("S", 25, 18, 27, 22)
    plan.put("S", 32, 20)
    plan.rect("#", 6, 2, 17, 11)
    plan.put("D", 11, 11)
    plan.rect("#", 19, 3, 23, 7)
    plan.rect("#", 3, 16, 9, 21)
    plan.put("D", 6, 21)
    plan.line('"', 2, 12, 13, 12)
    for column, row in [(5, 7), (8, 20), (21, 14), (23, 10), (16, 19), (22, 21)]:
        plan.put("T", column, row)
    for column, row in [(24, 19), (7, 22), (13, 13), (14, 9), (10, 16), (12, 17), (11, 19)]:
        plan.put("o", column, row)
    for column, row in [(19, 9), (11, 18), (14, 20)]:
        plan.put("H", column, row)
    for column, row in [(20, 16), (6, 10), (23, 6), (24, 7)]:
        plan.put("c", column, row)

    return plan


def plage():
    plan = Plan("P6 — Plage", "sol : sable ferme puis dunes")
    plan.rect("~", 1, 1, 32, 6)
    plan.rect("≈", 1, 7, 32, 8)
    plan.line("=", 4, 20, 26, 20)
    plan.line("=", 12, 10, 12, 20)
    plan.line("=", 20, 16, 20, 20)
    plan.line("S", 1, 20, 4, 20)
    plan.rect("#", 14, 15, 25, 24)
    plan.put("D", 19, 15)
    plan.rect("#", 5, 14, 10, 19)
    plan.rect("#", 11, 7, 13, 14)
    for column, row in [(2, 22), (7, 23), (16, 22), (23, 21), (29, 23), (27, 17), (30, 21)]:
        plan.put("T", column, row)
    for column, row in [(8, 21), (13, 9), (11, 15), (17, 13), (24, 12)]:
        plan.put("o", column, row)
    for column, row in [(12, 12), (19, 14), (7, 20)]:
        plan.put("H", column, row)
    for column, row in [(22, 9), (9, 17), (15, 19), (16, 20)]:
        plan.put("c", column, row)

    return plan


PLANS = [campagne(), marais(), falaise(), plage()]

# Also written one file per plate, so the review page can show the plan beside the image.
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"
FICHIERS = {"P1": "p1-campagne", "P4": "p4-marais", "P5": "p5-falaise", "P6": "p6-plage"}
for plan in PLANS:
    code = plan.title.split(" ")[0]
    (ASSETS / f"plan-{FICHIERS[code]}.txt").write_text(plan.render() + "\n", encoding="utf-8")

parts = [
    "# Plans ASCII des planches",
    "",
    "**Intention :** rendre lisible, case par case, ce que la composition demande — avant de regarder "
    "l'image. Le plan est l'**intention**, jamais le résultat : c'est en comparant les deux qu'un écart se "
    "trouve, et qu'on sait si la faute vient de la consigne ou de la production.",
    "",
    "Grille de 32 colonnes sur 24 rangées, une case pour un mètre. Les numéros de colonne sont donnés par "
    "leur chiffre des unités.",
    "",
    "## Légende",
    "",
    "| Signe | Sens |",
    "|---|---|",
]
parts += [f"| `{symbol}` | {sens} |" for symbol, sens in LEGEND]
parts.append("")
parts.append("Un bâtiment est dessiné par son **emprise au sol** ; sa hauteur déborde vers le haut à "
             "l'écran sans figurer au plan. Une créature majestueuse occupe deux cases.")
parts.append("")

for plan in PLANS:
    parts.append(f"## {plan.title}")
    parts.append("")
    parts.append(f"*{plan.subtitle}*")
    parts.append("")
    parts.append("```")
    parts.append(plan.render())
    parts.append("```")
    parts.append("")

parts.append("## P2 — Bourg et P3 — Contreforts")
parts.append("")
parts.append("Non tracés : leur composition n'a pas encore été réécrite au format de composition. Elles "
             "le seront avant leur prochaine production.")

OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(f"OK {OUTPUT}")
