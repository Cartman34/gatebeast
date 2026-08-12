#!/usr/bin/env python3
"""USAGE
  python3 scripts/dev/list-to-produce.py       les variantes déclarées qu'aucune image ne sert encore, par sujet
  python3 scripts/dev/list-to-produce.py -h    ce texte

INTENTION
  « Les sprites DOIVENT avancer » (opérateur, 2026-08-12) : la première question est donc « laquelle produire ensuite », et rien ne la posait. Le contrôle du
  thème dit COMBIEN il en reste — vingt-deux —, jamais LESQUELLES, et le référentiel se lit variante par variante. Ce script les nomme, avec la référence qu'il
  faut passer au générateur, pour qu'un lot parte sans que personne ait à ouvrir le référentiel.
"""
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_subjects', REPO / 'scripts' / 'check-subjects.py')
check_subjects = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_subjects)

if '-h' in sys.argv or '--help' in sys.argv:
    print(__doc__.strip())
    raise SystemExit(0)

data = check_subjects.load()
waiting = 0
for code, subject in sorted(data['subjects'].items()):
    empty = [variant for variant in subject.get('variants', []) if not variant.get('representations')]
    if not empty:
        continue
    print(f"\n{code} — {subject.get('type')} · {len(empty)} variante(s) sans image")
    for variant in empty:
        waiting += 1
        print(f"    {variant.get('ref')}")

print(f"\n{waiting} variante(s) attendent une image.")
