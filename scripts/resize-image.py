#!/usr/bin/env python3
"""Resize PNG images for web use or for embedding into an artifact page.

Usage: python3 gatebeast/scripts/resize-image.py <maxWidth> <source.png> [<source2.png> ...]

Each source yields a sibling file suffixed with `-<maxWidth>`. A narrower image is copied as is.

Requirements: Pillow. PHP GD is not installed on this machine, hence Python for this single tool.
"""
import sys
from pathlib import Path

from PIL import Image

if len(sys.argv) < 3:
    sys.exit("Usage: python3 resize-image.py <maxWidth> <source.png> [...]")

max_width = int(sys.argv[1])
failures = 0

for argument in sys.argv[2:]:
    source = Path(argument)
    target = source.with_name(f"{source.stem}-{max_width}{source.suffix}")
    try:
        image = Image.open(source)
    except Exception as error:
        print(f"FAILED {source}: {error}", file=sys.stderr)
        failures += 1
        continue
    if image.width > max_width:
        height = round(image.height * max_width / image.width)
        image = image.resize((max_width, height), Image.LANCZOS)
    image.save(target, optimize=True)
    print(f"OK {target} {round(target.stat().st_size / 1024)} KB")

sys.exit(1 if failures else 0)
