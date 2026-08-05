#!/usr/bin/env python3
"""Validate assets/sujets.json and confront it with the inventory and the disk.

The referentiel (rendu-en-calques.md, decision 18) is the single source for types, sujets and their
variants: this script is its gate. It refuses a file that does not conform to the model decided in
sujets-et-variantes.md and rendu-en-calques.md, prints the RESOLVED passage of every sujet — level by
level, so the three-level inheritance (sujets-et-variantes.md, decision 16) is never invisible — and
cross-checks the referentiel against the two things it must never drift from: the inventory (a sujet's
code must actually be inscribed there) and the disk (a produced file must be claimed by a variant, or
it is invisible to the referentiel even while it sits on disk).

Generates nothing, writes nothing.
Usage: python3 check-sujets.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shape_vocab

REPOSITORY = Path(__file__).resolve().parents[1]
ASSETS = REPOSITORY / "assets"
SUJETS = ASSETS / "sujets.json"
INVENTAIRE = REPOSITORY / "doc" / "conception" / "referentiels" / "visuel" / "inventaire"
CREATURES = REPOSITORY / "doc" / "conception" / "referentiels" / "contenu" / "creatures-temoins.md"

# The passage is written at the four compass points today; diagonals are meant to join them later
# without rewriting anything (sujets-et-variantes.md, decision 14). EDGES is shape_vocab's, not a copy
# of its own: the passage rose and a shape's edges are the same four compass points, and this checker
# used to keep a second list of them next to shape_vocab's, which is exactly the defect that module was
# written to end.
EDGES = shape_vocab.EDGES
# The five layer families in their drawing order (rendu-en-calques.md, decision 11).
LAYERS = {"sol", "decor-au-sol", "monde", "dessus", "interface"}
ORIENTATIONS = {"north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"}
CODE_PATTERN = re.compile(r"^[A-Z]{2,3}-\d{3}$")
# A representation's statut: the one shown to the player ("courante"), or one kept for record
# ("anterieure"). The list order carries no meaning — statut is the only thing that says which is which.
STATUSES = {"courante", "anterieure"}
MAX_PREVIOUS_REPRESENTATIONS = 3


class Fault(Exception):
    """A referentiel that does not conform to the decided model. Refused, never patched around."""


def load():
    if not SUJETS.is_file():
        raise Fault(f"missing {SUJETS}")
    try:
        return json.loads(SUJETS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise Fault(f"not valid JSON: {error}")


# The validation of a shape NAME — bare edges, the fifteen combinations — is shape_vocab's alone (see
# that module for why). This checker is exactly where the copies were found and the reason the module
# now exists; it must not become one again by keeping its own valid_shape.


def check_variant(where, variant):
    if variant.get("orientation") not in ORIENTATIONS:
        raise Fault(f"{where}: unknown or missing orientation {variant.get('orientation')!r}")
    if not variant.get("action"):
        raise Fault(f"{where}: missing action")
    if not shape_vocab.valid_shape(variant.get("shape", shape_vocab.DEFAULT_SHAPE)):
        raise Fault(f"{where}: invalid shape {variant.get('shape')!r}")


def has_unlabelled_single_representation(representations):
    """True for the one tolerated gap: a variant with exactly one representation and no statut yet.
    Treated as 'courante' by default (there is nothing else it could be), but signalled — not silently
    accepted — until the referentiel is completed."""
    return len(representations) == 1 and "statut" not in representations[0]


def check_representations(where, representations):
    """A variant's representations: several are allowed (a redraw keeps its predecessors, they are not
    a fault), but exactly one must carry statut 'courante', and at most three may carry 'anterieure'.
    List order means nothing — statut is the only thing that decides which is shown. The one exception
    is a variant with a single representation and no statut at all: tolerated as an implicit 'courante'
    (see has_unlabelled_single_representation), reported separately, never here."""
    if not representations or has_unlabelled_single_representation(representations):
        return
    for representation in representations:
        if representation.get("statut") not in STATUSES:
            raise Fault(f"{where}: representation {representation.get('path')!r} has missing or "
                        f"invalid statut {representation.get('statut')!r}")
    current = [r for r in representations if r["statut"] == "courante"]
    if len(current) != 1:
        raise Fault(f"{where}: expected exactly one representation with statut 'courante', "
                    f"found {len(current)}")
    previous = [r for r in representations if r["statut"] == "anterieure"]
    if len(previous) > MAX_PREVIOUS_REPRESENTATIONS:
        raise Fault(f"{where}: {len(previous)} representations with statut 'anterieure', "
                    f"at most {MAX_PREVIOUS_REPRESENTATIONS} are kept")


def check_schema(data):
    """Structural conformance, checked top to bottom; raises Fault on the first thing that does not
    hold. Nothing here is fixed up — a caller sees exactly why the file was refused."""
    if data.get("format") != "gatebeast-sujets":
        raise Fault("missing or wrong format marker")
    types = data.get("types")
    sujets = data.get("sujets")
    if not isinstance(types, dict) or not types:
        raise Fault("no types declared")
    if not isinstance(sujets, dict):
        raise Fault("no sujets section")

    for name, type_ in types.items():
        if type_.get("layer") not in LAYERS:
            raise Fault(f"type {name}: unknown or missing layer {type_.get('layer')!r}")
        if type_.get("passage_default") not in ("open", "closed"):
            raise Fault(f"type {name}: passage_default must be exactly 'open' or 'closed'")
        for variant in type_.get("lot_v0", []):
            check_variant(f"type {name} lot_v0", variant)
        compositions = type_.get("compositions")
        if compositions and compositions.get("default") not in compositions.get("values", []):
            raise Fault(f"type {name}: composition default is not one of its own values")

    for code, sujet in sujets.items():
        if not CODE_PATTERN.match(code):
            raise Fault(f"sujet code not in the XX-nnn form: {code}")
        type_name = sujet.get("type")
        if type_name not in types:
            raise Fault(f"{code}: type {type_name!r} is not declared among types")
        footprint = sujet.get("emprise") or {}
        columns, rows = footprint.get("columns"), footprint.get("rows")
        if not isinstance(columns, int) or not isinstance(rows, int) or columns < 1 or rows < 1:
            raise Fault(f"{code}: emprise missing or not a positive number of tiles")
        if not sujet.get("variantes"):
            raise Fault(f"{code}: no variantes")
        for variant in sujet["variantes"]:
            check_variant(code, variant)
            if "representations" not in variant:
                raise Fault(f"{code}: a variant carries no representations list (empty is fine, "
                            f"absent is not — the referentiel must always be able to say there are "
                            f"none yet)")
            check_representations(code, variant["representations"])
            composition = variant.get("composition")
            allowed = (types[type_name].get("compositions") or {}).get("values")
            if composition and (not allowed or composition not in allowed):
                raise Fault(f"{code}: composition {composition!r} is not declared by type {type_name}")
            portillon = variant.get("portillon")
            allowed_gates = (types[type_name].get("portillons") or {}).get("values")
            if portillon and (not allowed_gates or portillon not in allowed_gates):
                raise Fault(f"{code}: portillon {portillon!r} is not declared by type {type_name}")
        overrides = (sujet.get("passage") or {}).get("cells", {})
        for cell in overrides:
            if not re.fullmatch(r"\d+,\d+", cell):
                raise Fault(f"{code}: passage cell key {cell!r} is not 'column,row'")
            column, row = (int(part) for part in cell.split(","))
            if column >= columns or row >= rows:
                raise Fault(f"{code}: passage cell {cell!r} falls outside its {columns}x{rows} emprise")
            for edge, value in overrides[cell].items():
                if edge not in EDGES or not isinstance(value, bool):
                    raise Fault(f"{code}: passage cell {cell!r} has a bad edge {edge!r}")


def resolve_passage(sujet, type_):
    """Every cell of a sujet's footprint, every edge resolved with the level that decided it — the
    type's default, or the sujet's own override. Declared 'case par case', never deduced from the
    shape (sujets-et-variantes.md, decisions 13 and 16)."""
    columns, rows = sujet["emprise"]["columns"], sujet["emprise"]["rows"]
    default_open = type_["passage_default"] == "open"
    overrides = (sujet.get("passage") or {}).get("cells", {})
    cells = []
    for row in range(rows):
        for column in range(columns):
            key = f"{column},{row}"
            override = overrides.get(key, {})
            resolved = {}
            for edge in EDGES:
                if edge in override:
                    resolved[edge] = (override[edge], "sujet")
                else:
                    resolved[edge] = (default_open, f"type {sujet['type']}")
            cells.append((key, resolved))
    return cells


def inventory_text():
    paths = sorted(INVENTAIRE.glob("*.md"))
    if CREATURES.is_file():
        paths.append(CREATURES)
    return {path: path.read_text(encoding="utf-8") for path in paths}


def code_in_inventory(code, texts):
    pattern = re.compile(rf"\*\*{re.escape(code)}\b")
    return any(pattern.search(text) for text in texts.values())


def scan_cutout():
    """The delivered files: a master from assets/poc/ resized to delivery definition. A variant's
    representations point here, never at assets/poc/ (rendu-en-calques.md) — this is the only tree the
    referentiel must fully claim."""
    base = ASSETS / "cutout"
    return sorted(base.rglob("*.png")) if base.is_dir() else []


def scan_poc():
    """The masters: a generator's raw render, kept next to its frozen consigne. Not what a variant
    claims — only its cutout export is."""
    base = ASSETS / "poc"
    return sorted(base.rglob("*.png")) if base.is_dir() else []


def claimed_paths(data):
    claimed = set()
    for sujet in data["sujets"].values():
        for variant in sujet["variantes"]:
            for representation in variant.get("representations", []):
                claimed.add(representation["path"])
    return claimed


def variants_with_implicit_status(data):
    """Every variant tolerated under has_unlabelled_single_representation: its lone representation is
    treated as 'courante' by default, but it is surfaced here so the gap does not stay invisible until
    the referentiel is completed with an explicit statut."""
    pending = []
    for code, sujet in data["sujets"].items():
        for variant in sujet["variantes"]:
            representations = variant.get("representations") or []
            if has_unlabelled_single_representation(representations):
                pending.append((code, representations[0]["path"]))
    return pending


def probe_stems(hors_referentiel):
    """The file stems of the deliberately out-of-referentiel probes (sujets.json, _hors_referentiel):
    their files are expected on disk without any variant claiming them, so they must not be reported as
    unclaimed."""
    return set(hors_referentiel)


def unexported_masters(poc_files):
    """A master under assets/poc/ whose delivered file is missing from assets/cutout/ at the same
    relative position — an export forgotten on the way to delivery. Advisory only: this never fails the
    check, it only surfaces a gap for a human to judge (a usage example or a reliquat never gets a
    cutout, and that is not a fault)."""
    missing = []
    for poc_path in poc_files:
        cutout_path = ASSETS / "cutout" / poc_path.relative_to(ASSETS / "poc")
        if not cutout_path.is_file():
            missing.append(poc_path)
    return missing


def main():
    try:
        data = load()
        check_schema(data)
    except Fault as fault:
        print(f"REFUSED: {fault}")
        return 1

    hors_referentiel = {key: value for key, value in data.get("_hors_referentiel", {}).items()
                        if key != "_comment"}
    print(f"{len(data['types'])} types, {len(data['sujets'])} sujets, "
          f"{len(hors_referentiel)} hors référentiel\n")

    print("PASSAGE — résolu niveau par niveau (type, puis sujet)")
    for code in sorted(data["sujets"]):
        sujet = data["sujets"][code]
        type_ = data["types"][sujet["type"]]
        print(f"  {code} ({sujet['type']}, défaut du type : {type_['passage_default']})")
        for key, resolved in resolve_passage(sujet, type_):
            state = "  ".join(f"{edge}={'ouvert' if resolved[edge][0] else 'fermé'}"
                              f"[{resolved[edge][1]}]" for edge in EDGES)
            print(f"    case {key} : {state}")

    print("\nINVENTAIRE — chaque code de sujet doit y être réellement inscrit")
    texts = inventory_text()
    absent = [code for code in sorted(data["sujets"]) if not code_in_inventory(code, texts)]
    if absent:
        for code in absent:
            print(f"  ABSENT DE L'INVENTAIRE : {code}")
    else:
        print(f"  les {len(data['sujets'])} sujets sont bien à l'inventaire")

    print("\nDISQUE — tout livrable sous assets/cutout/ doit être réclamé")
    claimed = claimed_paths(data)
    expected_probes = probe_stems(hors_referentiel)
    unclaimed = [path for path in scan_cutout()
                if path.relative_to(ASSETS).as_posix() not in claimed
                and path.stem not in expected_probes]
    if unclaimed:
        for path in unclaimed:
            print(f"  AUCUNE VARIANTE NE RÉCLAME : {path.relative_to(ASSETS).as_posix()}")
    else:
        print("  chaque livrable est réclamé par une variante")

    print("\nMAÎTRES — signalement, pas une faute : un maître de assets/poc/ sans livrable dans "
          "assets/cutout/")
    missing_exports = unexported_masters(scan_poc())
    if missing_exports:
        for path in missing_exports:
            print(f"  AUCUN LIVRABLE POUR CE MAÎTRE : {path.relative_to(ASSETS).as_posix()}")
    else:
        print("  chaque maître a son livrable")

    print("\nSTATUT IMPLICITE — signalement, pas une faute : variante à une seule représentation, "
          "sans statut, traitée comme courante")
    implicit_status = variants_with_implicit_status(data)
    if implicit_status:
        for code, path in implicit_status:
            print(f"  {code} : {path} — à compléter d'un statut 'courante' explicite")
    else:
        print("  chaque représentation porte un statut explicite")

    if hors_referentiel:
        print(f"\nHORS RÉFÉRENTIEL ({len(hors_referentiel)}) — sondes sans code ni emprise fabriqués")
        for code, reason in hors_referentiel.items():
            print(f"  {code} : {reason}")

    return 1 if absent or unclaimed else 0


if __name__ == "__main__":
    sys.exit(main())
