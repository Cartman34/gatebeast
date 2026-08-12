#!/usr/bin/env python3
"""USAGE: python3 scripts/dev/show-type-batch.py <TYPE> [<TYPE>…] — le lot v0 que déclare chaque type nommé, une ligne par vue.

INTENTION: la clause d'orientation d'une consigne n'est écrite que si le type déclare PLUSIEURS orientations dans son lot v0. Savoir ce que le lot déclare
vraiment est donc la première question quand une consigne sort sans dire quelle vue elle demande.
"""
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_subjects', REPO / 'scripts' / 'check-subjects.py')
check_subjects = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_subjects)

data = check_subjects.load()
for name in sys.argv[1:]:
    declaration = data['types'].get(name)
    if declaration is None:
        print(f"{name} : type absent du référentiel")
        continue
    views = declaration.get('batch_v0', [])
    print(f"\n{name} — {len(views)} vue(s) au lot v0")
    for view in views:
        print(f"    {view.get('orientation')} · {view.get('action')} · {view.get('ref')}")
