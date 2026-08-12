"""Usage: python3 scripts/check-axonometry.py <image.png> [...] — measures whether a sprite holds the world's parallel projection, and reports what it found.
       python3 scripts/check-axonometry.py -h|--help — this text

WHAT IT CAN AND CANNOT DECIDE, SAID PLAINLY. A single drawing of an unknown object carries no ground truth: nothing in the pixels says which edges were MEANT to be vertical, so no measurement can
prove a projection. What CAN be measured is the one thing the projection forbids — CONVERGENCE. Under a parallel projection, the two sides of an upright volume stay parallel; under a perspective
one they lean towards a vanishing point, and the silhouette tapers. A sprite whose sides fan in or out is therefore wrong, and that IS decidable from the image alone.

So this is a VERDICT, never a refusal (doc/glossaire.md): "converging" when it finds a taper, "parallel" when it does not, and "not enough structure" when the subject has no upright sides to
measure — a tuft of grass, a puddle, a path. Saying "cannot conclude" honestly is the whole point: a check that guessed on a shapeless subject would be worse than no check at all.

HOW, AND WHY THIS WAY. The silhouette's left and right boundaries are read row by row off the alpha channel, over the part of the height where the subject actually stands. A straight line is fitted
to each side, and their slopes are compared: two sides that lean the SAME way are a subject drawn at an angle, which is allowed and common; two sides that lean TOWARDS each other, or away, are a
taper — that is convergence. The taper is expressed in degrees and printed, so nobody has to trust the word alone.

DELIBERATELY WITHOUT ANY NEW LIBRARY. A Hough transform over detected edges would find every straight segment rather than just the silhouette's two sides, and would decide more cases. It needs
scikit-image, which is not installed and is not on the project's validated tool list — and an unvalidated tool is asked for, never tried (règles du dépôt). This version uses numpy and Pillow, which
the chain already carries. What it costs is written above: it reads the outline, not the inner edges, so a subject whose sides are hidden by its own crown says "cannot conclude" more often.

Python rather than PHP for the usual reason: image measurement lives here, and this asks the same two libraries every other measuring tool asks.
"""

import json
import sys
from pathlib import Path

import numpy
import scipy.ndimage
from PIL import Image

# Ce qu'on appelle le corps du sujet : la tranche de hauteur où l'on mesure ses côtés. On écarte le haut, où une couronne ou un toit débordent et donnent une
# largeur qui ne dit rien du volume, et le tout bas, où l'herbe et les racines élargissent le pied. Ce qui reste est la partie qui se dresse.
BODY_TOP = 0.35
BODY_BOTTOM = 0.90

# En dessous de cette hauteur en pixels, la mesure n'a pas de quoi s'appuyer : une pente sur dix lignes ne veut rien dire.
MINIMUM_ROWS = 24

# La régularité exigée d'un côté pour qu'on le prenne pour une arête. Un bord dentelé — feuillage, eau, herbe — ne se prête pas à une droite, et c'est là qu'un
# outil naïf conclurait à tort. Mesurée comme l'écart type des résidus, en pixels.
MAXIMUM_ROUGHNESS = 3.0

# L'écart de pente entre les deux côtés au-delà duquel on parle de convergence. Un dessin à la main n'est jamais au degré près : l'épreuve de projection du
# 2026-08-06 a montré des copies tenant à un ou deux degrés. Au-delà de cinq, ce n'est plus de l'imprécision, c'est un point de fuite.
CONVERGENCE_DEGREES = 5.0

# READING THE INNER EDGES, AND ONLY ON WHAT IS BUILT (operator, 2026-08-08: "au moins sur les bâtiments ?"). The silhouette says nothing on a subject whose sides
# are hidden by its own crown or dentelled by foliage — which is most of them, and the reason this check answered "aucun verdict" on every building it was given.
# A BUILT subject is the favourable case and the only one worth this: the corner of a wall, a door jamb, the edge of a gable are long, straight, frank segments,
# and they are exactly what carries the projection. A tree has none and never will.
#
# scipy rather than a new library: its gradients are already installed, next to numpy and Pillow. scikit-image would have brought a Hough transform and was asked
# for; it turned out not to be needed, so it was not introduced (règles du dépôt: an unvalidated tool is asked for, never tried).
GRADIENT_PERCENTILE = 92          # what counts as an edge pixel: the strongest 8 % of the opaque zone
NEAR_VERTICAL_DEGREES = 25.0      # beyond this, an edge is a roof slope or a ground line, not an upright
MINIMUM_EDGE_PIXELS = 200         # below this on either side, the subject has no upright structure to read

# THE WALLS, AND NOT THE ROOF — this band is the whole difference between a measure and a false alarm. Read over the body at large, the farmhouse came back at
# 19.6° of taper and would have been declared faulty; the same drawing read over its lower band comes back at 2.4°. What made the difference was the ROOF: seen
# at an angle, its tile seams are countless short edges, tilted by the plane they lie on and not by any perspective, and within the near-vertical window. They
# swamp the walls, which are the only edges that carry the projection. A wall is at the bottom of a building, so that is where this looks.
WALLS_TOP = 0.70
WALLS_BOTTOM = 0.94


def sides(alpha):
    """The left and right boundary of the silhouette, row by row, over the body of the subject. None when there is nothing to measure."""
    opaque = alpha > 0
    rows = numpy.flatnonzero(opaque.any(axis=1))
    if rows.size < MINIMUM_ROWS:
        return None
    top, bottom = int(rows[0]), int(rows[-1])
    height = bottom - top + 1
    first = top + int(height * BODY_TOP)
    last = top + int(height * BODY_BOTTOM)
    if last - first < MINIMUM_ROWS:
        return None
    ys, lefts, rights = [], [], []
    for y in range(first, last + 1):
        columns = numpy.flatnonzero(opaque[y])
        if columns.size == 0:
            continue
        ys.append(y)
        lefts.append(int(columns[0]))
        rights.append(int(columns[-1]))
    if len(ys) < MINIMUM_ROWS:
        return None

    return numpy.array(ys, dtype=float), numpy.array(lefts, dtype=float), numpy.array(rights, dtype=float)


def lean(ys, xs):
    """(angle from vertical in degrees, roughness in pixels) of one side, by least squares."""
    slope, intercept = numpy.polyfit(ys, xs, 1)
    residual = xs - (slope * ys + intercept)

    return float(numpy.degrees(numpy.arctan(slope))), float(numpy.std(residual))


def is_built(path):
    """Whether this file draws a BUILT subject, read from the referential by the code in its name — never guessed from the letters."""
    stem = Path(path).stem
    code = stem.split("_")[0].rsplit("-v", 1)[0]
    try:
        data = json.loads((Path(__file__).resolve().parent.parent / "assets" / "subjects.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    subject = (data.get("subjects") or {}).get(code)

    return bool(subject) and subject.get("type") == "building"


def inner_lean(path):
    """(left, right, count) — the median tilt of the near-vertical inner edges on each half of the subject, in degrees from the vertical.

    Under a parallel projection every upright edge is vertical wherever it stands, so both halves read around zero and their difference is nil. Under a
    perspective one the uprights fan towards a vanishing point: those left of centre lean one way, those right of centre the other, and the DIFFERENCE between
    the two halves is the taper — the same quantity the silhouette measures, read where the subject actually has edges.
    """
    image = Image.open(path)
    opaque = numpy.asarray(image.convert("RGBA"))[:, :, 3] > 128
    grey = numpy.asarray(image.convert("L"), dtype=float)
    gx = scipy.ndimage.sobel(grey, axis=1)
    gy = scipy.ndimage.sobel(grey, axis=0)
    strength = numpy.hypot(gx, gy)

    band = numpy.zeros_like(opaque)
    band[int(opaque.shape[0] * WALLS_TOP):int(opaque.shape[0] * WALLS_BOTTOM)] = True
    useful = opaque & band
    if not useful.any():
        return None
    strong = useful & (strength > numpy.percentile(strength[useful], GRADIENT_PERCENTILE))
    # The gradient points ACROSS an edge; turning it a quarter gives the edge's own direction, measured from the vertical.
    angle = numpy.degrees(numpy.arctan2(gx, -gy))
    columns = numpy.arange(opaque.shape[1])[None, :].repeat(opaque.shape[0], 0)
    middle = columns[useful].mean()

    read = []
    for half in (columns < middle, columns >= middle):
        tilts = angle[strong & half]
        tilts = tilts[numpy.abs(tilts) < NEAR_VERTICAL_DEGREES]
        if len(tilts) < MINIMUM_EDGE_PIXELS:
            return None
        read.append((float(numpy.median(tilts)), len(tilts)))

    return read[0][0], read[1][0], read[0][1] + read[1][1]


def verdict(path):
    """(kept, sentence) — kept says whether the criterion holds; an undecidable subject is never a failure."""
    # THE INNER EDGES FIRST, ON A BUILT SUBJECT: they decide where the silhouette cannot. The outline of a building is dentelled by its own roof and its planters,
    # which is why this check answered "aucun verdict" on all three buildings it was ever given — while their walls and jambs were right there, unread.
    if is_built(path):
        inner = inner_lean(path)
        if inner is not None:
            left, right, pixels = inner
            taper = abs(left - right)
            if taper > CONVERGENCE_DEGREES:
                return False, (f"CONVERGENCE lue sur les arêtes intérieures : {taper:.1f}° d'écart entre les deux moitiés "
                               f"(gauche {left:+.1f}°, droite {right:+.1f}°, sur {pixels} pixels d'arête)")
            return True, (f"projection parallèle tenue, lue sur les arêtes intérieures : {taper:.1f}° d'écart "
                          f"(gauche {left:+.1f}°, droite {right:+.1f}°, sur {pixels} pixels d'arête)")

    alpha = numpy.asarray(Image.open(path).convert("RGBA"))[:, :, 3]
    measured = sides(alpha)
    if measured is None:
        return True, "silhouette trop courte pour mesurer ses côtés — aucun verdict"
    ys, lefts, rights = measured
    left_angle, left_rough = lean(ys, lefts)
    right_angle, right_rough = lean(ys, rights)
    if left_rough > MAXIMUM_ROUGHNESS or right_rough > MAXIMUM_ROUGHNESS:
        return True, (f"côtés trop irréguliers pour conclure (irrégularité {left_rough:.1f} px à gauche, "
                      f"{right_rough:.1f} px à droite) — aucun verdict")
    # DEUX CÔTÉS QUI PENCHENT DU MÊME CÔTÉ SONT UN SUJET INCLINÉ, PAS UNE PERSPECTIVE : c'est leur écart qui trahit le point de fuite, jamais leur pente commune.
    taper = abs(left_angle - right_angle)
    if taper > CONVERGENCE_DEGREES:
        return False, (f"CONVERGENCE : les deux côtés s'écartent de {taper:.1f}° l'un de l'autre "
                       f"(gauche {left_angle:+.1f}°, droite {right_angle:+.1f}°), au-delà des {CONVERGENCE_DEGREES}° tolérés")

    return True, (f"projection parallèle tenue : {taper:.1f}° entre les deux côtés "
                  f"(gauche {left_angle:+.1f}°, droite {right_angle:+.1f}°)")


def main(paths):
    faults = 0
    for name in paths:
        path = Path(name)
        if not path.is_file():
            print(f"ABSENTE : {name}")
            faults += 1
            continue
        kept, sentence = verdict(path)
        print(f"{'OK  ' if kept else 'HORS'} {path.name} — {sentence}")
        faults += 0 if kept else 1

    return 1 if faults else 0


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        raise SystemExit(0)
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 scripts/check-axonometry.py <image.png> [...]")
    sys.exit(main(sys.argv[1:]))
