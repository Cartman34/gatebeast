#!/usr/bin/env python3
"""USAGE: python3 scripts/dev/promote-and-prune-tools.py [--apply] — moves the tools a living document promises into scripts/dev/ under an English name,
rewrites every citation of them, and deletes everything left in local/scripts/.

INTENTION: « normalement, si un script est dans local/scripts, c'est qu'il est jetable » (opérateur, 2026-08-12), and before that « tu dois d'abord supprimer les
scripts qui étaient temporaires et qui ne sont plus utiles ». The directory holds no keepsakes: what deserves to survive is a project tool and belongs under
scripts/, versioned, in English — which also settles S59, since the eighty-nine French names all live here.

WHAT COUNTS AS PROMISED, AND WHY IT IS NOT « WHAT IS CITED ANYWHERE »: a living document — the tracking file, the repository rules, or code that calls it — tells
whoever reads it that the tool exists, so it must exist for them too. The seance journal and a closed task, on the other hand, RECORD what was done: their
sentences describe the past and stay true whether the script is there or not.

THE DELETION IS FINAL: local/ is unversioned by design, so nothing here comes back from the history. That is why the promotion happens FIRST and in the same
gesture — deleting before moving would break every reference the documents make.
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / 'local' / 'scripts'
DESTINATION = REPO / 'scripts' / 'dev'

# THE LIVING DOCUMENTS: what they name, the project owes. Anything else that mentions a script is a record of the past.
LIVING = ('SUIVI.md', 'doc/regles-du-depot.md')
LIVING_TREES = ('scripts/', 'review-server/')

# The French verbs these names carry, and their English word. Taken from the checker rather than invented, so one table decides both what is refused and what is
# written instead.
spec = importlib.util.spec_from_file_location('checker', REPO / 'scripts' / 'check-code-language.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

versioned = subprocess.run(['git', 'ls-files'], cwd=REPO, capture_output=True, text=True, check=True).stdout.split()
texts = {}
for relative in versioned:
    path = REPO / relative
    try:
        if path.is_file() and path.stat().st_size < 2_000_000:
            texts[relative] = path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        continue


def english(stem: str) -> str:
    """The same name with its French words replaced — the checker's own table decides, never a choice made here."""
    new = stem
    for word in re.findall(r'[a-zà-ÿ]+', stem.lower()):
        if word in checker.FORBIDDEN_IN_NAMES:
            new = re.sub(word, checker.FORBIDDEN_IN_NAMES[word], new, flags=re.IGNORECASE)

    return new


promote, drop = {}, []
for script in sorted(SCRIPTS.iterdir()):
    if not script.is_file():
        continue
    holders = [relative for relative, text in texts.items() if script.name in text]
    promised = [h for h in holders if h in LIVING or h.startswith(LIVING_TREES)]
    if promised:
        promote[script.name] = english(script.stem) + script.suffix
    else:
        drop.append(script.name)

print(f"{len(promote)} outil(s) à promouvoir sous scripts/dev/, {len(drop)} jetable(s) à supprimer\n")
for old, new in sorted(promote.items()):
    print(f'  {old}' + (f'  →  {new}' if old != new else '  (nom déjà anglais)'))

if '--apply' not in sys.argv:
    print('\nRien fait — relancez avec --apply.')
    sys.exit(0)

DESTINATION.mkdir(parents=True, exist_ok=True)
for old, new in promote.items():
    (SCRIPTS / old).rename(DESTINATION / new)
    subprocess.run(['git', 'add', f'scripts/dev/{new}'], cwd=REPO, check=True)

# EVERY CITATION FOLLOWS ITS TOOL, IN THE SAME GESTURE: a rename that leaves a dead reference is worse than the French name it removed. Both spellings are
# rewritten — the bare name and the full path — because documents use one or the other.
touched = 0
for relative in versioned:
    path = REPO / relative
    if relative not in texts:
        continue
    text = texts[relative]
    before = text
    for old, new in promote.items():
        text = text.replace(f'local/scripts/{old}', f'scripts/dev/{new}')
        text = text.replace(old, new)
    if text != before:
        path.write_text(text, encoding='utf-8')
        touched += 1

for name in drop:
    (SCRIPTS / name).unlink()

print(f'\n{len(promote)} outil(s) promu(s), {touched} fichier(s) réécrit(s), {len(drop)} jetable(s) supprimé(s).')
