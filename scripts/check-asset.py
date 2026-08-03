#!/usr/bin/env python3
"""Measure a produced asset against what an asset must be — capabilities constated, never assumed.

Four things decide whether an asset is usable as a sprite, and none of them is a matter of taste:

- BACKGROUND: is there a plain, keyable field? Measured on the four border strips — how close they are
  to pure magenta, and how uniform they are. A cutout asset whose background is not uniform cannot be
  keyed without eating into the subject.
- SUBJECT: does it fill the frame? The subject is whatever is not background; its bounding box is
  measured against the image, and the free margin around it reported.
- TRANSPARENCY: does the file carry an alpha channel with actually transparent pixels?
- SIZE: the produced dimensions, which the generator decides and we only observe.

A ground tile is judged differently: it has no background and must be REGULAR — the check compares its
quadrants instead of looking for a subject.

Usage: python3 check-asset.py <type>/<code>.png [...]   (paths relative to assets/poc)
"""
import sys
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parents[1] / "assets" / "poc"
MAGENTA = (255, 0, 255)
BORDURE = 0.04  # share of the image width taken as the border strip
PROCHE = 60     # channel distance under which a pixel counts as "the key colour"


def distance(pixel, cible) -> float:
    return max(abs(pixel[index] - cible[index]) for index in range(3))


def fond(image: Image.Image) -> dict:
    """The four border strips: how magenta they are, and how uniform."""
    largeur, hauteur = image.size
    marge = max(2, int(largeur * BORDURE))
    strips = [image.crop((0, 0, largeur, marge)), image.crop((0, hauteur - marge, largeur, hauteur)),
              image.crop((0, 0, marge, hauteur)), image.crop((largeur - marge, 0, largeur, hauteur))]
    pixels = [p for strip in strips for p in strip.getdata()]
    magenta = sum(1 for p in pixels if distance(p, MAGENTA) <= PROCHE) / len(pixels)
    moyenne = tuple(sum(p[i] for p in pixels) / len(pixels) for i in range(3))
    ecart = sum(distance(p, moyenne) for p in pixels) / len(pixels)

    return {"magenta": 100 * magenta, "moyenne": tuple(round(c) for c in moyenne), "ecart": ecart}


def sujet(image: Image.Image, couleur) -> dict:
    """Bounding box of everything that is not the background colour, as a share of the image."""
    largeur, hauteur = image.size
    petite = image.resize((160, int(160 * hauteur / largeur)))
    lp, hp = petite.size
    pixels = petite.load()
    gauche, droite, haut, bas = lp, -1, hp, -1
    for y in range(hp):
        for x in range(lp):
            if distance(pixels[x, y], couleur) > PROCHE:
                gauche, droite = min(gauche, x), max(droite, x)
                haut, bas = min(haut, y), max(bas, y)
    if droite < 0:
        return {"largeur": 0.0, "hauteur": 0.0, "marge_haut": 0.0, "marge_bas": 0.0}

    return {
        "largeur": 100 * (droite - gauche + 1) / lp,
        "hauteur": 100 * (bas - haut + 1) / hp,
        "marge_haut": 100 * haut / hp,
        "marge_bas": 100 * (hp - 1 - bas) / hp,
    }


def regularite(image: Image.Image) -> float:
    """For a tile: the biggest luminance gap between its four quadrants, in points."""
    largeur, hauteur = image.size
    quadrants = [(0, 0, largeur // 2, hauteur // 2), (largeur // 2, 0, largeur, hauteur // 2),
                 (0, hauteur // 2, largeur // 2, hauteur), (largeur // 2, hauteur // 2, largeur, hauteur)]
    moyennes = []
    for boite in quadrants:
        pixels = list(image.crop(boite).resize((40, 40)).getdata())
        moyennes.append(sum(0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in pixels) / len(pixels))

    return max(moyennes) - min(moyennes)


for argument in sys.argv[1:]:
    chemin = Path(argument)
    if not chemin.is_absolute():
        chemin = ASSETS / argument
    if not chemin.is_file():
        print(f"ABSENT {chemin}")
        continue
    brut = Image.open(chemin)
    alpha = "oui" if brut.mode in ("RGBA", "LA") else "non"
    transparents = 0.0
    if brut.mode == "RGBA":
        canal = list(brut.getchannel("A").getdata())
        transparents = 100 * sum(1 for a in canal if a < 250) / len(canal)
    image = brut.convert("RGB")
    largeur, hauteur = image.size
    carre = "carré" if largeur == hauteur else f"rapport {largeur / hauteur:.2f}"

    print(f"{chemin.name:22s} {largeur}x{hauteur} ({carre})  alpha : {alpha}"
          f"  pixels transparents : {transparents:.1f} %")
    if chemin.parent.name == "sol":
        print(f"{'':22s} tuile — écart de luminance entre quadrants : {regularite(image):.1f} points "
              f"({'régulière' if regularite(image) < 12 else 'IRRÉGULIÈRE'})")
        continue
    mesure = fond(image)
    print(f"{'':22s} fond : {mesure['magenta']:.1f} % de magenta sur les bords, teinte moyenne "
          f"{mesure['moyenne']}, dispersion {mesure['ecart']:.1f} "
          f"({'UNI' if mesure['ecart'] < 12 else 'NON UNI'})")
    couleur = MAGENTA if mesure["magenta"] > 50 else mesure["moyenne"]
    boite = sujet(image, couleur)
    print(f"{'':22s} sujet : {boite['largeur']:.0f} % de la largeur, {boite['hauteur']:.0f} % de la "
          f"hauteur ; marges {boite['marge_haut']:.0f} % en haut, {boite['marge_bas']:.0f} % en bas "
          f"({'cadrage plein' if boite['hauteur'] >= 65 else 'SUJET TROP PETIT'})")
