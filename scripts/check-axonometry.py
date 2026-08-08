"""Usage: python3 scripts/check-axonometry.py <image.png> [...] — measures whether a sprite holds the world's parallel projection, and reports what it found.

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

import sys
from pathlib import Path

import numpy
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


def verdict(path):
    """(kept, sentence) — kept says whether the criterion holds; an undecidable subject is never a failure."""
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
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 scripts/check-axonometry.py <image.png> [...]")
    sys.exit(main(sys.argv[1:]))
