#!/usr/bin/env python3
"""Order a whole set of trace pieces in one campaign, all from the same style reference.

USAGE
  python3 scripts/run-fence-campaign.py            # lists what would be ordered, produces nothing
  python3 scripts/run-fence-campaign.py --generate

INTENTION
  The pieces of an assembling subject only hold together if they were drawn against the SAME
  reference: produced one by one over days, they drift. So the whole set is ordered in a single
  campaign, every prompt naming the same reference image, and the generator runs them in parallel.

  Nothing here is written by hand: each prompt is assembled by build-trace-piece-prompt.py from the
  inventory sheet and the shared style base. This script only decides WHICH pieces are wanted.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "scripts" / "generate-sprite-trace.py"

CODE = "OB-010"
REFERENCE = REPO / "assets" / "poc" / "cloture" / "usage-OB-010-v2.png"

# The fifteen shapes of the model. A north-south run carries ONE post only (sheet decision: seen from
# above, two posts in depth would nearly overlap), so every shape joining north or south takes one.
SHAPES = ["n", "e", "s", "w", "ns", "ew", "ne", "es", "sw", "nw",
          "nes", "esw", "nsw", "new", "nesw"]

# A wave of THREE, not the whole set: the chain grows by widening waves, and a wave only opens if
# the one before gave what was expected. These three are the three natures of piece — a rail seen
# broadside, a rail seen end-on, and a change of direction. If the same reference holds across all
# three, the twelve others follow without surprise; if it does not, the mistake cost three images.
WANTED = [("ew", 1), ("ns", 1), ("es", 1)]


def main(generate: bool) -> int:
    if not REFERENCE.exists():
        print(f"FAULT la référence {REFERENCE.name} est absente")
        return 1

    print(f"campagne {CODE} · {len(WANTED)} pièces · référence {REFERENCE.name}")
    for shape, posts in WANTED:
        print(f"  {CODE}_shape-{shape}_posts-{posts}")
    if not generate:
        print("\nrien produit — ajouter --generate pour lancer")
        return 0

    # Every prompt is assembled first, then ALL of them are handed to the generator in one call: it
    # runs a dozen at once. Ordering them one by one would take hours of wall clock for no reason.
    jobs = []
    for shape, posts in WANTED:
        name = f"{CODE}_shape-{shape}_posts-{posts}"
        result = subprocess.run(["python3", str(TOOL), CODE, shape, "--posts", str(posts),
                                 "--ref", str(REFERENCE)], cwd=REPO.parent, capture_output=True)
        if result.returncode:
            print(f"FAULT consigne refusée pour {name}")
            return 1
        prompt = (REPO / "local" / f"prompt-{name}.txt").read_text(encoding="utf-8")

        # One generation per version, nothing overwritten: an existing piece keeps its place.
        version, image = 1, REFERENCE.parent / f"{name}.png"
        while image.exists():
            version += 1
            image = REFERENCE.parent / f"{name}-v{version}.png"
        image.with_suffix(".txt").write_text(prompt, encoding="utf-8")
        jobs += [str(image), prompt]
        print(f"  prêt {image.name}")

    print(f"\n{len(jobs) // 2} générations lancées en parallèle")

    return subprocess.run(["php", str(REPO / "scripts" / "generate-image.php"), *jobs],
                          cwd=REPO.parent).returncode


if __name__ == "__main__":
    raise SystemExit(main("--generate" in sys.argv))
