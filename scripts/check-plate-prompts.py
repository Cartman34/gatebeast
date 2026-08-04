#!/usr/bin/env python3
"""Pre-flight check of the CURRENT standard, run before every shot. A FAULT means no generation.

The operator's rule (2026-08-03): the standard applies to every plate without exception, and it is checked
mechanically, not by memory. This reads the prompt files actually saved next to the images — the exact
text that was or will be sent — and verifies, per prompt:

- the prompt is in French (no leftover English standard block);
- no pixel size anywhere except the image file dimension itself;
- the "humans must look small" block and the 1.75-2 tiles rule are both present;
- a size reminder sits next to EVERY human of the composition (counted against the humans listed);
- no fish, no real animal named as such;
- every (column,row) inside the 32x24 grid.

Usage: python3 check-plate-prompts.py [key ...]   (default: the six current plates)
"""
import re
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

# The current prompt of each plate — the last version written for it.
CURRENT = [
    "p1-campagne-v8", "p2-bourg-v7", "p3-contreforts-v6",
    "p4-marais-v8", "p5-falaise-v5", "p6-plage-v5",
]

# Words that betray the old English standard surviving in a prompt.
ENGLISH_MARKERS = ["A STANDING adult", "EVERY DOOR IS", "NO REAL ANIMALS EXIST", "FRAME AND SCALE",
                   "TWO MEASURED LIMITS", "EXHAUSTIVE — draw"]
# Real animals that must never be named as inhabitants. "chèvre" and friends included: the recurring
# collapse is the generator drawing a real animal, and naming one in the prompt guarantees it.
FORBIDDEN_ANIMALS = ["poisson", "fish", "mouton", "vache", "chien", "canard", "héron", "cheval",
                     "chèvre", "lapin réel", "oiseau réel"]
# A line that forbids or denies rather than prescribes: the animal names on it are the prohibition.
# "de la taille d'un grand chien" is a size comparison quoted from a sheet, not an animal to draw.
NEGATION = re.compile(r"\bni \b|\baucun|\bsans\b|\bjamais\b|\bpas de\b|\bplus de\b|N'EXISTE"
                      r"|de la taille d'un|longue comme|large comme|haute comme", re.IGNORECASE)
# Lines that count as a size reminder attached to an inhabitant.
SIZE_REMINDER = re.compile(
    r"entre 1,75 et 2 cases|PLUS PETIT|PLUS BAS|plus bas que debout|nettement plus petit",
    re.IGNORECASE)
# A human of the composition: a bullet whose text names a person rather than an SP- creature.
HUMAN_HINT = re.compile(
    r"\b(fermier|meunier|meunière|boulangère|forgeron|garde|potier|potière|marchand|marchande|"
    r"bergère|berger|mineur|voyageuse|voyageur|pêcheur|pêcheuse|gardienne|enfant|enfants|tourbier|"
    r"femme|homme|jeune)\b", re.IGNORECASE)


def bullets(prompt: str) -> list:
    """The inhabitant bullets: each starts with '- En (' in the Habitants section."""
    parts = re.split(r"\bHABITANTS\b", prompt, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) < 2:
        return []
    section = parts
    items, current = [], None
    for line in section[1].splitlines():
        if line.startswith("- ") or line.startswith("- LA CRÉATURE"):
            if current:
                items.append(current)
            current = line
        elif current is not None and line.startswith("  "):
            current += " " + line.strip()
        elif current and not line.strip():
            items.append(current)
            current = None
    if current:
        items.append(current)

    return items


def check(key: str) -> list:
    path = ASSETS / f"prompt-{key}.txt"
    if not path.is_file():
        return [f"{key}: prompt file missing — nothing to check"]
    prompt = path.read_text(encoding="utf-8")
    faults = []

    if "{" in prompt or "}" in prompt:
        faults.append(f"{key}: leftover braces — a sheet reference did not resolve")
    for marker in ENGLISH_MARKERS:
        if marker in prompt:
            faults.append(f"{key}: old English standard survives — '{marker}'")
    # Pixels: the image file dimension is the single allowed mention.
    for match in re.finditer(r"[^\n]*\b(pixels?|px)\b[^\n]*", prompt, re.IGNORECASE):
        line = match.group(0)
        if "1536 x 1152 pixels" in line:
            continue
        faults.append(f"{key}: pixel size for an element — '{line.strip()[:70]}'")
    if "LES HUMAINS DOIVENT SEMBLER PETITS" not in prompt:
        faults.append(f"{key}: the 'humans must look small' block is missing")
    if "ENTRE 1,75 ET 2 CASES" not in prompt.upper():
        faults.append(f"{key}: the 1.75-2 tiles rule is missing")
    # A real animal is only a fault when it is NAMED as something to draw. The standard's own
    # prohibition sentence lists them all ("ni chien, ni poisson…") and must not trip the check.
    for line in prompt.splitlines():
        if NEGATION.search(line):
            continue
        for animal in FORBIDDEN_ANIMALS:
            if re.search(rf"\b{animal}\b", line, re.IGNORECASE):
                faults.append(f"{key}: forbidden real animal named — '{animal}' in "
                              f"'{line.strip()[:70]}'")
    for column, row in re.findall(r"\((\d+),(\d+)\)", prompt):
        if not (1 <= int(column) <= 32 and 1 <= int(row) <= 24):
            faults.append(f"{key}: position ({column},{row}) outside the 32x24 grid")

    humans, reminded = 0, 0
    for item in bullets(prompt):
        if "SP-0" in item or "créature" in item.lower() and "MAJESTUEUSE" in item:
            continue
        if not HUMAN_HINT.search(item):
            continue
        humans += 1
        if SIZE_REMINDER.search(item):
            reminded += 1
    if humans and reminded < humans:
        faults.append(f"{key}: {humans - reminded} human(s) of {humans} without a size reminder "
                      f"next to them")
    print(f"{'FAULTY' if faults else 'OK'} {key}: {len(prompt)} characters, {humans} human(s), "
          f"{reminded} with a size reminder")

    return faults


keys = sys.argv[1:] or CURRENT
all_faults = []
for key in keys:
    all_faults += check(key)

if all_faults:
    for fault in all_faults:
        print(f"FAULT {fault}")
    raise SystemExit(1)
print(f"PRE-FLIGHT OK: {len(keys)} prompt(s) meet the current standard")
