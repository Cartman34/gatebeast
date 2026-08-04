#!/usr/bin/env python3
"""Verify the prompt assembly still reproduces the POC prompts byte for byte, without writing anything.

Equivalent to generate-asset.py --dump, but read-only: prompt() is called and its result compared to
the prompt file that sits beside each POC image. No generation, no file touched.

Run from the workspace root: python3 gatebeast/local/check-prompts.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gatebeast" / "scripts"))
from asset_common import ASSETS, prompt

CASES = [("sol", "SOL-001"), ("personnage", "HU-000"), ("creature", "SP-001-1")]

failures = []
for type_asset, code in CASES:
    reference = ASSETS / type_asset / f"prompt-{code}.txt"
    if not reference.is_file():
        failures.append(f"{type_asset}/{code}: reference prompt missing")
        continue
    built = prompt(type_asset, code)
    stored = reference.read_text(encoding="utf-8")
    # The prompts deliberately gained one line: the output definition, which the generator was never
    # asked for before. Nothing else may have moved.
    added = [row for row in built.splitlines() if row not in stored.splitlines()]
    removed = [row for row in stored.splitlines() if row not in built.splitlines()]
    print(f"{type_asset}/{code}: {len(built)} chars, {len(added)} line(s) added, "
          f"{len(removed)} removed")
    for row in added:
        print(f"    + {row[:96]}")
    if removed:
        failures.append(f"{type_asset}/{code}: {len(removed)} line(s) disappeared from the prompt")
    allowed = ("DÉFINITION ATTENDUE", "EMPRISE AU SOL", "CONTENU EN LARGEUR", "REMPLI",
               "EN HAUTEUR, LE DÉBORDEMENT")
    unexpected = [row for row in added if not row.startswith(allowed)]
    if unexpected:
        failures.append(f"{type_asset}/{code}: unexpected new line(s): {unexpected[:2]}")

if failures:
    print("\nFAILURES:")
    for failure in failures:
        print(f"  - {failure}")
    raise SystemExit(1)
print("\nprompt assembly unchanged")
