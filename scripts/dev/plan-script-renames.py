#!/usr/bin/env python3
"""USAGE: python3 scripts/dev/plan-script-renames.py — lists the files whose NAME carries a French word, with the name they would take, and says what would
have to be rewritten with them.

INTENTION: before writing a renaming script, know what it faces — how many files, whether two of them would land on the same name, and how many citations each
one has elsewhere in the repository. A rename that leaves a dead reference is worse than the French name it removed, and that is the only part of this job that
is not mechanical.
"""
import importlib.util
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_code_language', REPO / 'scripts' / 'check-code-language.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

# THE CANDIDATES ARE THE DIRECTORIES THE CHECKER SWEEPS, NOT WHAT GIT TRACKS — a first pass asked git for the list and answered « nothing to rename », which was
# false and would have closed the point: `local/` is deliberately unversioned, and it is precisely where the French names live.
candidates = [p.relative_to(REPO).as_posix() for directory in checker.SCANNED
              for p in (REPO / directory).rglob('*') if p.is_file()]

renames = {}
for relative in candidates:
    path = REPO / relative
    if path.suffix not in checker.SUFFIXES:
        continue
    stem = path.stem
    words = re.findall(r'[a-zà-ÿ]+', stem.lower())
    if not any(word in checker.FORBIDDEN_IN_NAMES for word in words):
        continue
    new = stem
    for word in words:
        if word in checker.FORBIDDEN_IN_NAMES:
            new = re.sub(word, checker.FORBIDDEN_IN_NAMES[word], new, flags=re.IGNORECASE)
    renames[relative] = str(Path(relative).with_name(new + path.suffix))

# TWO FILES LANDING ON ONE NAME IS THE ONLY THING THAT CANNOT BE AUTOMATED: it must be seen before anything moves.
landing = {}
for old, new in renames.items():
    landing.setdefault(new, []).append(old)
collisions = {new: olds for new, olds in landing.items() if len(olds) > 1}

# HOW OFTEN EACH NAME IS CITED ELSEWHERE: the rename has to carry those with it, in the same gesture. Both the versioned files — the tracking document, the pile,
# the documents — and the throwaway scripts themselves, which call one another.
searched = set(subprocess.run(['git', 'ls-files'], cwd=REPO, capture_output=True, text=True, check=True).stdout.split())
searched.update(candidates)
cited = {}
for old in renames:
    name = Path(old).name
    holders = []
    for relative in sorted(searched):
        if relative == old:
            continue
        path = REPO / relative
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            if name in path.read_text(encoding='utf-8', errors='ignore'):
                holders.append(relative)
        except OSError:
            continue
    if holders:
        cited[old] = holders

by_directory = {}
for old in renames:
    family = '/'.join(Path(old).parts[:2]) if Path(old).parts[0] == 'local' else Path(old).parts[0]
    by_directory[family] = by_directory.get(family, 0) + 1

print(f"{len(renames)} fichier(s) à renommer")
for family, count in sorted(by_directory.items(), key=lambda pair: -pair[1]):
    print(f"  {family}/ — {count}")
print(f"\n{len(collisions)} collision(s) de nom" + (' :' if collisions else '.'))
for new, olds in collisions.items():
    print(f"  {new} ← {', '.join(olds)}")
print(f"\n{len(cited)} fichier(s) cité(s) ailleurs, {sum(len(f) for f in cited.values())} citation(s) à réécrire :")
for old, files in sorted(cited.items()):
    print(f"  {Path(old).name} — {', '.join(files)}")
