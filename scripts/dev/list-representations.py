#!/usr/bin/env python3
"""USAGE: python3 scripts/dev/list-representations.py <CODE> [<CODE>…] — pour chaque sujet nommé, ses variantes, leurs représentations, leur version, leur
statut et leur verdict.

INTENTION: savoir ce qui existe déjà d'un sujet avant d'en commander une image. `check-subjects.py` déverse tout le référentiel et ne répond pas à cette
question-là ; l'ouvrir à la main coûte des milliers de lignes de JSON pour trois valeurs.
"""
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_subjects', REPO / 'scripts' / 'check-subjects.py')
check_subjects = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_subjects)

data = check_subjects.load()
for code in sys.argv[1:]:
    subject = data['subjects'].get(code)
    if subject is None:
        print(f"{code} : absent du référentiel")
        continue
    print(f"\n{code} — {subject.get('type')}")
    for variant in subject.get('variants', []):
        print(f"  variante {variant.get('ref')}")
        for representation in variant.get('representations', []):
            print(f"    v{representation.get('version')} · {representation.get('status')} · "
                  f"verdict {representation.get('verdict') or '—'} · {representation.get('path')}")
