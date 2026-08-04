#!/usr/bin/env python3
"""List every variant the built page carries: profile, caption, address, state and scope.

A read-only look at the produced file, to check the addressing by eye after a model change.
Run from the workspace root: python3 gatebeast/local/list-variants.py
"""
import re
from pathlib import Path

page = (Path(__file__).resolve().parent / "revue-sprites.html").read_text(encoding="utf-8")

slot = re.compile(
    r'<li class="slot slot--(?P<scope>\w+)" data-slot="(?P<id>[^"]+)" data-status="(?P<status>\w+)">'
    r'.*?slot-caption">(?P<caption>[^<]*)<'
    r'.*?slot-address">(?P<address>[^<]*)<',
    re.S)

current = None
for match in slot.finditer(page):
    code = match.group("id").split("|")[0]
    if code != current:
        print(f"\n{code}")
        current = code
    scope = "" if match.group("scope") == "park" else f"  [{match.group('scope')}]"
    print(f"  {match.group('caption'):24s} {match.group('address'):58s} "
          f"{match.group('status')}{scope}")

trial = re.compile(r'<article class="trial" data-slot="(?P<id>[^"]+)" data-status="(?P<status>\w+)"'
                   r'.*?slot-address">(?P<address>[^<]*)<', re.S)
print("\nessais")
for match in trial.finditer(page):
    print(f"  {match.group('id').split('|')[0]:24s} {match.group('address'):58s} "
          f"{match.group('status')}")
