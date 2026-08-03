#!/usr/bin/env python3
"""Wait until the third art direction round has produced its six images.

A file is only considered ready once its size has stopped changing between two checks: the generator
writes progressively, so an existing path is not proof of a complete image.
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "revue-da"
KEYS = ["b1v3", "b2v3", "b4v3"]
EXPECTED = [ASSETS / f"da-gb-{key}-{kind}.png" for key in KEYS for kind in ("creature", "scene")]
INTERVAL = 20
TIMEOUT = 45 * 60


def sizes():
    return {path: path.stat().st_size if path.exists() else None for path in EXPECTED}


start = time.time()
previous = sizes()
while time.time() - start < TIMEOUT:
    time.sleep(INTERVAL)
    current = sizes()
    stable = [path for path, size in current.items() if size and size == previous[path]]
    missing = [path.name for path in EXPECTED if path not in stable]
    print(f"{len(stable)}/{len(EXPECTED)} stable — missing: {', '.join(missing) or 'none'}", flush=True)
    if not missing:
        print("READY")
        sys.exit(0)
    previous = current

print("TIMEOUT")
sys.exit(1)
