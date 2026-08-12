#!/usr/bin/env python3
"""Print the variant lot the character types expect, and what their subjects actually declare.

USAGE
  python3 scripts/dev/show-character-lots.py — for the human and creature types: the lot the type asks for, and, per subject, the variants already declared.

INTENTION
  « Pour les personnages (hu+créature), il faudrait ajouter les autres postures de base en variant » (operator, 2026-08-12). Adding them means knowing which lot
  is expected — the type declares it — and which ones a subject already has, so that nothing is declared twice and nothing invented. Read before writing.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REFERENTIAL = REPO / "assets/subjects.json"

data = json.loads(REFERENTIAL.read_text(encoding="utf-8"))
for name in ("humain", "creature"):
    declaration = data["types"].get(name)
    if declaration is None:
        raise SystemExit(f"FAULT le type « {name} » n'est pas au référentiel.")
    expected = [entry.get("ref") for entry in declaration.get("batch_v0", [])]
    print(f"\n== TYPE {name} — lot attendu ({len(expected)}) :")
    for ref in expected:
        print(f"   {ref}")
    for code, subject in data["subjects"].items():
        if subject.get("type") != name:
            continue
        held = [variant.get("ref") for variant in subject.get("variants", [])]
        print(f"   SUJET {code} — {len(held)} variante(s) déclarée(s) :")
        for ref in held:
            print(f"      {ref}")
        missing = [ref for ref in expected if ref not in held]
        print(f"      MANQUENT : {', '.join(missing) if missing else 'aucune'}")
