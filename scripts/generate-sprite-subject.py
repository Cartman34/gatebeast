#!/usr/bin/env python3
"""Order one sprite of a subject that stands on its own, from its inventory code to the image.

USAGE
  python3 scripts/generate-sprite-subject.py <CODE> [--ref <image>] [--generate]
  e.g.  generate-sprite-subject.py TR-063 --generate

  Without --generate it stops after assembling the prompt, writing a draft under local/ so it can be
  read before anything is produced. Nothing else is ever done by hand: the design forbids addressing
  the generator directly, and this tool is the single path from a code to a sprite.

INTENTION
  For a tree, a thicket, a building — anything that is not laid end to end — the whole prompt comes
  from three places and nowhere else: the shared style base, the subject's INVENTORY SHEET quoted
  word for word, and the definition calculated from its footprint.

  It reads the sheet from the inventory itself, never from a copy kept in code. The older tool holds
  its own copies, which is why it does not know the subjects rewritten this morning: a copied sheet
  goes stale the day the real one changes, and nothing says so.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_common
import plate_common
import tile_scale

REPO = Path(__file__).resolve().parent.parent
SHEETS = [REPO / "doc" / "conception" / "referentiels" / "visuel" / "inventaire",
          REPO / "doc" / "conception" / "referentiels" / "contenu"]


def sheet_of(code: str) -> tuple:
    """The label, the description, the footprint and the height, read from the inventory entry itself
    — never from a copy kept in code, so a rewritten sheet is picked up unchanged."""
    for folder in SHEETS:
        for path in sorted(folder.glob("*.md")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.startswith(f"- **{code} "):
                    continue
                label = line.split("**")[1].replace(code, "").strip()
                after = line.split("** — ", 1)[-1]
                size = re.search(r"(\d+)\s*×\s*(\d+)", after)
                if not size:
                    raise SystemExit(f"FAULT {code} n'a pas d'emprise écrite — elle est obligatoire.")
                height = re.search(r"hauteur\s+(\d+(?:[.,]\d+)?)\s*cases?", after)
                if not height:
                    raise SystemExit(f"FAULT {code} n'a pas de hauteur écrite — elle est obligatoire.")
                # Everything before the description belongs to the precisions; everything from the
                # description onward — the description itself, and any "Description propre à ..." that
                # follows it for one particular form or value — never does.
                description, start = asset_common.sheet_description(after, code)
                detail = after[:start].replace("**", "").replace("`", "")

                return (label, description, " ".join(detail.split()).strip(" .—,"),
                        (int(size.group(1)), int(size.group(2))),
                        float(height.group(1).replace(",", ".")))
    raise SystemExit(f"FAULT {code} n'est pas à l'inventaire — rien ne se produit sans fiche.")


def build(code: str, reference: Path, generate: bool) -> int:
    label, description, detail, footprint, height = sheet_of(code)
    master = tile_scale.master_definition(*footprint, height=height)

    clause = ""
    if reference:
        clause = f"""
RÉFÉRENCE — le fichier ./{reference.name} est présent dans ton répertoire de travail. Il montre le
style, la matière et la lumière à reprendre. Le sujet demandé est celui décrit ci-dessous, pas celui
de l'image : la référence donne le traitement, la fiche donne le sujet.
"""

    # No retry clause here, on purpose: one was tried and removed on the operator's word — the
    # generator never saw the rejected image, so describing its fault in negative terms does not help
    # it, what helps it is a better sheet. A rejection motive is not for the generator: it goes back
    # into the SHEET, never into this prompt.
    prompt = f"""{plate_common.STYLE_FR}

{asset_common.CAMERA_FR}

ASSET DE JEU — {label}, SEUL SUJET DE L'IMAGE, destiné à être posé comme sprite sur une carte vue de
dessus.

DÉFINITION ATTENDUE : {master['width']} × {master['height']} pixels.

{asset_common.CADRAGE_CUTOUT}

{asset_common.emprise_clause(footprint)}

{asset_common.taille_clause(footprint, height)}
{clause}
{asset_common.REGLES_FR}
CE QUE SA FICHE PRÉCISE :
{detail}

LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :
{code} : {description}
"""

    draft = REPO / "local" / f"prompt-{code}.txt"
    draft.parent.mkdir(exist_ok=True)
    draft.write_text(prompt, encoding="utf-8")
    print(f"{code} — {label} · emprise {footprint[0]} × {footprint[1]} · "
          f"{master['width']} × {master['height']} px")
    print(f"brouillon écrit : {draft.relative_to(REPO)}")

    if not generate:
        return 0

    folder = REPO / "assets" / "poc" / asset_common.CODE_FOLDER.get(code[:2], "divers")
    folder.mkdir(parents=True, exist_ok=True)
    # One generation per version, nothing overwritten.
    version, image = 1, folder / f"{code}.png"
    while image.exists():
        version += 1
        image = folder / f"{code}-v{version}.png"
    image.with_suffix(".txt").write_text(prompt, encoding="utf-8")

    print(f"consigne figée : {image.with_suffix('.txt').relative_to(REPO)}")
    # This tool generates, and stops there. Exporting the master and rebuilding the review page
    # belong to the queue (scripts/sprite-queue.py), which owns the ordering: chained from here, two
    # generations finishing at once would rebuild the page simultaneously, and the queue could not
    # prevent it.
    print(f"génération vers {image.relative_to(REPO)}")

    with asset_common.working_reference(reference, folder):
        return subprocess.run(["php", str(REPO / "scripts" / "generate-image.php"),
                               str(image), prompt], cwd=REPO.parent).returncode


if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        raise SystemExit(2)
    ref = Path(argv[argv.index("--ref") + 1]).resolve() if "--ref" in argv else None
    raise SystemExit(build(argv[0], ref, "--generate" in argv))
