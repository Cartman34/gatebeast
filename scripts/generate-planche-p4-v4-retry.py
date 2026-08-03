#!/usr/bin/env python3
"""Re-run plate P4 v4 with the EXACT SAME prompt, to a distinct output file.

Purpose: consistency test. The generator is not deterministic; the owner wants to see whether the same
prompt yields a genuinely different image or stays coherent. The prompt is read verbatim from the file
saved at generation time — nothing is recomposed.

Usage: python3 generate-planche-p4-v4-retry.py [suffix]   (default suffix: b, then c, d... per attempt)
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
TOOL = "conceptions/methode/outils/generate-image.php"
TARGET = "conceptions/gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

suffix = sys.argv[1] if len(sys.argv) > 1 else "b"
prompt = (ASSETS / "prompt-p4-marais-v4.txt").read_text(encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/planche-p4-marais-v4{suffix}.png", prompt], cwd=PROJECT
).returncode)
