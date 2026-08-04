#!/usr/bin/env python3
"""Embed every deliverable sprite PNG into the tracking page's image catalogue.

The tracking page is the operator's only window onto sprites: they work at a terminal, where nothing
renders. Only assets/cutout/ — the deliverable — is embedded here, at its own native resolution, byte
for byte, no resampling, no re-encoding: the page shows exactly what the file holds, transparency
included. assets/poc/ is the source that produced it, not itself a sprite, and stays off the page — it
is also what made the page heavy before this cut. The page is still expected to be sizeable; that is
accepted.

Generates no image: it only reads and base64-encodes files that already exist.
Run from the workspace root: python3 gatebeast/scripts/build-thumbnails.py
"""
import base64
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "gatebeast" / "assets"
OUT = Path(__file__).resolve().parent / "thumbnails.json"


def scan(base):
    return sorted(base.rglob("*.png")) if base.is_dir() else []


catalogue = {}
for path in scan(ASSETS / "cutout"):
    relative = path.relative_to(ASSETS).as_posix()
    # The key is the path itself, extension dropped: it is unique by construction (two files cannot
    # share one path), unlike a bare code, which a poc and a cutout version of the same subject share.
    key = relative[:-len(".png")]
    data = path.read_bytes()
    with Image.open(path) as probe:
        size = probe.size
    catalogue[key] = {
        "uri": f"data:image/png;base64,{base64.b64encode(data).decode('ascii')}",
        "size": size,
        "bytes": len(data),
        "path": relative,
    }
    print(f"{relative}: {size[0]}x{size[1]}, {len(data) / 1024:.1f} kB")

OUT.write_text(json.dumps(catalogue), encoding="utf-8")
total = sum(len(entry["uri"]) for entry in catalogue.values())
print(f"{len(catalogue)} images, total after base64: {total / 1024:.1f} kB")
