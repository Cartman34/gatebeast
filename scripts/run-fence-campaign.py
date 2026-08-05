#!/usr/bin/env python3
"""Order a whole set of trace pieces in one campaign, all from the same style reference.

USAGE
  python3 scripts/run-fence-campaign.py            # lists what would be queued, queues nothing
  python3 scripts/run-fence-campaign.py --generate

  Queuing is not generating: after --generate, the requests sit in the sprite queue as "pending" until
  someone drains it with
    python3 scripts/sprite-queue.py run [--workers N]
  which is what actually launches the generations, in parallel.

INTENTION
  The pieces of an assembling subject only hold together if they were drawn against the SAME
  reference: produced one by one over days, they drift. So the whole set is ordered in a single
  campaign, every request naming the same reference image.

  This script does not talk to the generator at all — it only decides WHICH pieces are wanted and
  hands them, one by one, to scripts/sprite-queue.py. The queue is what turns each one into its own
  process and runs several of them at once; grouping several pieces into a single generator call here
  would defeat that, so this script never does.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shape_vocab

REPO = Path(__file__).resolve().parent.parent
SPRITE_QUEUE = REPO / "scripts" / "sprite-queue.py"

CODE = "OB-010"
REFERENCE = REPO / "assets" / "poc" / "cloture" / "usage-OB-010-v2.png"

# The fifteen shapes of the model — shape_vocab's, not a copy of its own. A north-south run carries ONE
# post only (sheet decision: seen from above, two posts in depth would nearly overlap), so every shape
# joining north or south takes one.
SHAPES = shape_vocab.edge_combinations()

# A wave of THREE, not the whole set: the chain grows by widening waves, and a wave only opens if
# the one before gave what was expected. These three are the three natures of piece — a rail seen
# broadside, a rail seen end-on, and a change of direction. If the same reference holds across all
# three, the twelve others follow without surprise; if it does not, the mistake cost three images.
WANTED = [("ew", 1), ("ns", 1), ("es", 1)]


def main(generate: bool) -> int:
    if not REFERENCE.exists():
        print(f"FAULT la référence {REFERENCE.name} est absente")
        return 1
    invalid = [shape for shape, _ in WANTED if not shape_vocab.valid_shape(shape)]
    if invalid:
        print(f"FAULT forme(s) invalide(s) dans WANTED : {invalid}")
        return 1

    print(f"campagne {CODE} · {len(WANTED)} pièces · référence {REFERENCE.name}")
    for shape, posts in WANTED:
        print(f"  {CODE}_shape-{shape}_posts-{posts}")
    if not generate:
        print("\nrien mis en file — ajouter --generate pour les ordonner")
        return 0

    # One request per piece, handed to the queue as its own row — never batched into one call. The
    # queue is what decides how many of them run at once (its own --workers) and what "one process per
    # generation" actually means; this script's only job is to name the pieces.
    requests = [
        {"kind": "trace", "code": CODE, "shape": shape, "posts": posts,
         "reference": str(REFERENCE.relative_to(REPO))}
        for shape, posts in WANTED
    ]
    requests_file = REPO / "local" / f"campaign-{CODE}-requests.json"
    requests_file.parent.mkdir(exist_ok=True)
    requests_file.write_text(json.dumps(requests, ensure_ascii=False, indent=2), encoding="utf-8")

    added = subprocess.run(["python3", str(SPRITE_QUEUE), "add", str(requests_file)],
                            cwd=REPO.parent)
    if added.returncode:
        return added.returncode

    print(f"\n{len(requests)} pièce(s) mise(s) en file — lancer "
          f"'python3 scripts/sprite-queue.py run' pour les générer en parallèle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--generate" in sys.argv))
