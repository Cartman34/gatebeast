#!/usr/bin/env python3
"""USAGE: python3 scripts/dev/show-catalog-missing.py — dit, pour le catalogue réel, quels profils sont incomplets en v0 et ce qui leur manque.

INTENTION: check-catalog.py compare la liste des profils incomplets à une liste écrite en dur, et son échec ne dit pas laquelle des deux a bougé. Il faut voir
la liste réelle avant de décider si c'est le contrôle ou la donnée qui a tort.
"""
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('asset_catalog', REPO / 'scripts' / 'asset_catalog.py')
asset_catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(asset_catalog)

catalog = asset_catalog.load()
for code, profile in catalog.profiles.items():
    missing = profile.missing('v0')
    print(f"{code} ({profile.type}) : {len(missing)} manquant(s) en v0")
