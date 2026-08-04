#!/usr/bin/env python3
"""Verify every path constant in scripts/ resolves to something real, without generating anything.

Run from the workspace root: python3 gatebeast/local/check-tool-paths.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "gatebeast" / "scripts"
sys.path.insert(0, str(SCRIPTS))

failures = []

# 1. Module-level constants of the two shared bases, imported for real.
import asset_common
import plate_common

for module in (asset_common, plate_common):
    name = module.__name__
    if module.PROJECT != ROOT:
        failures.append(f"{name}.PROJECT = {module.PROJECT}, expected {ROOT}")
    if not (module.PROJECT / module.TOOL).is_file():
        failures.append(f"{name}.TOOL missing: {module.PROJECT / module.TOOL}")
    if not (module.PROJECT / module.TARGET).is_dir():
        failures.append(f"{name}.TARGET missing: {module.PROJECT / module.TARGET}")
    if module.ASSETS != module.PROJECT / module.TARGET:
        failures.append(f"{name}.ASSETS {module.ASSETS} != TARGET {module.PROJECT / module.TARGET}")
    print(f"{name}: PROJECT={module.PROJECT} TOOL ok TARGET={module.TARGET} ok")

# 2. Every other script: read its constants textually and check them the same way.
pattern_target = re.compile(r'^TARGET = "([^"]+)"', re.M)
pattern_tool = re.compile(r'^TOOL = "([^"]+)"', re.M)
pattern_project = re.compile(r'^PROJECT = Path\(__file__\)\.resolve\(\)\.parents\[(\d+)\]', re.M)

for script in sorted(SCRIPTS.glob("*.py")):
    text = script.read_text(encoding="utf-8")
    for match in pattern_project.finditer(text):
        resolved = script.resolve().parents[int(match.group(1))]
        if resolved != ROOT:
            failures.append(f"{script.name}: PROJECT resolves to {resolved}")
    for match in pattern_tool.finditer(text):
        if not (ROOT / match.group(1)).is_file():
            failures.append(f"{script.name}: TOOL missing {match.group(1)}")
    for match in pattern_target.finditer(text):
        if not (ROOT / match.group(1)).is_dir():
            failures.append(f"{script.name}: TARGET missing {match.group(1)}")

# 3. The ascii-plans output must land in the design tree.
text = (SCRIPTS / "build-ascii-plans.py").read_text(encoding="utf-8")
import importlib.util
spec = importlib.util.spec_from_file_location("build_ascii_plans", SCRIPTS / "build-ascii-plans.py")
# Not executed (it writes); the constant is checked textually instead.
if 'parent.parent / "doc" / "conception" / "referentiels"' not in text:
    failures.append("build-ascii-plans.py: OUTPUT not repointed to doc/conception/referentiels")
elif not (ROOT / "gatebeast" / "doc" / "conception" / "referentiels" / "visuel").is_dir():
    failures.append("build-ascii-plans.py: target directory missing")

if failures:
    print("\nFAILURES:")
    for failure in failures:
        print(f"  - {failure}")
    raise SystemExit(1)
print("\nall path constants resolve")
