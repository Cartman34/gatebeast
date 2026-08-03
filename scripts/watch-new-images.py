#!/usr/bin/env python3
"""Announce each new review image as soon as it is written.

There is no inotify tool on this machine, so this polls. One line per new file, nothing else, so the
agent is woken exactly once per image and can look at it, check it and republish the page.

Usage: python3 methode-less watch-new-images.py <pattern> [<expected-count>]
Example: python3 watch-new-images.py 'da-gb-*v7-*.png' 6
"""
import sys
import time
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"
pattern = sys.argv[1] if len(sys.argv) > 1 else "*.png"
expected = int(sys.argv[2]) if len(sys.argv) > 2 else 0

seen = set()
deadline = time.time() + 1800

while time.time() < deadline:
    for path in sorted(ASSETS.glob(pattern)):
        if path in seen:
            continue
        # A file being written is not a file ready to read: wait for its size to settle.
        size = path.stat().st_size
        time.sleep(1.5)
        if size != path.stat().st_size or size == 0:
            continue
        seen.add(path)
        print(f"PRET {path.name}", flush=True)
    if expected and len(seen) >= expected:
        break
    time.sleep(5)
