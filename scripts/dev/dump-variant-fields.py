#!/usr/bin/env python3
"""USAGE: python3 scripts/dev/dump-variant-fields.py — lists every variant field each type declares,
with its values and whether it carries `defines_kind`.

INTENTION: one-shot diagnostic for the variant-clause defect — it says which fields would be skipped by
a rule keyed on `defines_kind`. In Python because the referentiel is read by the Python tooling that
owns this chain, and json is right there.
"""
import json
from pathlib import Path

data = json.loads((Path(__file__).resolve().parents[2] / "assets" / "subjects.json").read_text(encoding="utf-8"))
for name, type_ in data["types"].items():
    fields = {key: (value.get("values"), value.get("defines_kind"))
              for key, value in type_.items() if isinstance(value, dict) and "values" in value}
    print(name, fields)
