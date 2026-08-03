#!/usr/bin/env python3
"""Re-run the DA reference image with the EXACT SAME prompt, to a distinct output file.

Same consistency test as the plates: the prompt that produced the current reference
(da-b4-r15-scene.png) is read verbatim from the file saved at generation time; each attempt gets its own
file, nothing is ever overwritten.

Usage: python3 generate-da-reference-retry.py [suffix]   (default: b, then c, d... per attempt)
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
TOOL = "conceptions/methode/outils/generate-image.php"
TARGET = "conceptions/gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

suffix = sys.argv[1] if len(sys.argv) > 1 else "b"
prompt = (ASSETS / "prompt-b4-r15-scene.txt").read_text(encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/da-b4-r15-scene-{suffix}.png", prompt], cwd=PROJECT
).returncode)
