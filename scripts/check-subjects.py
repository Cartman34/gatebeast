#!/usr/bin/env python3
"""Validate assets/subjects.json and confront it with the inventory and the disk.

The referentiel (rendu-en-calques.md, decision 18) is the single source for types, sujets and their
variants: this script is its gate. It refuses a file that does not conform to the model decided in
sujets-et-variantes.md and rendu-en-calques.md, prints the RESOLVED passage of every sujet — level by
level, so the three-level inheritance (sujets-et-variantes.md, decision 16) is never invisible — and
cross-checks the referentiel against the two things it must never drift from: the inventory (a sujet's
code must actually be inscribed there) and the disk (a produced file must be claimed by a variant, or
it is invisible to the referentiel even while it sits on disk).

Generates nothing, writes nothing.
Usage: python3 check-subjects.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shape_vocab

REPOSITORY = Path(__file__).resolve().parents[1]
ASSETS = REPOSITORY / "assets"
SUBJECTS = ASSETS / "subjects.json"
INVENTAIRE = REPOSITORY / "doc" / "conception" / "referentiels" / "visuel" / "inventaire"
CREATURES = REPOSITORY / "doc" / "conception" / "referentiels" / "contenu" / "creatures-temoins.md"

# The passage is written at the four compass points today; diagonals are meant to join them later
# without rewriting anything (sujets-et-variantes.md, decision 14). EDGES is shape_vocab's, not a copy
# of its own: the passage rose and a shape's edges are the same four compass points, and this checker
# used to keep a second list of them next to shape_vocab's, which is exactly the defect that module was
# written to end.
EDGES = shape_vocab.EDGES
# The five layer families in their drawing order (rendu-en-calques.md, decision 11).
LAYERS = {"ground", "ground-decor", "world", "above", "interface"}
ORIENTATIONS = {"north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"}
CODE_PATTERN = re.compile(r"^[A-Z]{2,3}-\d{3}$")
# A representation's statut: the one shown to the player ("current"), or one kept for record
# ("previous"). The list order carries no meaning — statut is the only thing that says which is which.
STATUSES = {"current", "previous"}
# How many earlier versions the review page SHOWS beside the current one. The referentiel itself keeps
# every version an image has ever had, without limit: on garde tout, on versionne tout, on n'en affiche
# que trois (operator, 2026-08-05). This figure therefore bounds a display and nothing else — it was
# once enforced here as a ceiling on what the file may hold, which quietly dropped entries and left
# their images orphaned on disk.
SHOWN_PREVIOUS_REPRESENTATIONS = 2


class Fault(Exception):
    """A referentiel that does not conform to the decided model. Refused, never patched around."""


def load():
    if not SUBJECTS.is_file():
        raise Fault(f"missing {SUBJECTS}")
    try:
        return json.loads(SUBJECTS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise Fault(f"not valid JSON: {error}")


def save(data):
    """Write the referential back, in the ONE spelling every writer must share.

    THE FORM OF THE FILE IS A DECISION, AND IT BELONGS NEXT TO `load()`: two writers dumping it their own way rewrite the whole file
    against each other, and every real change is then buried in a diff of ten thousand reindented lines. Two writers already agreed
    on `indent=2` by having each been told so; a third would have made it a convention nobody holds.
    """
    SUBJECTS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# The validation of a shape NAME — bare edges, the fifteen combinations — is shape_vocab's alone (see
# that module for why). This checker is exactly where the copies were found and the reason the module
# now exists; it must not become one again by keeping its own valid_shape.


def check_variant(where, variant):
    # The ref is the variant's identifier — written, not computed. Without it a variant cannot be
    # designated at all: not by a tool, not in a file name, not in a sentence.
    if not variant.get("ref"):
        raise Fault(f"{where}: missing ref — a variant is designated by its ref, which is written")
    if variant.get("orientation") not in ORIENTATIONS:
        raise Fault(f"{where}: unknown or missing orientation {variant.get('orientation')!r}")
    if not variant.get("action"):
        raise Fault(f"{where}: missing action")
    if not shape_vocab.valid_shape(variant.get("shape", shape_vocab.DEFAULT_SHAPE)):
        raise Fault(f"{where}: invalid shape {variant.get('shape')!r}")


def has_unlabelled_single_representation(representations):
    """True for the one tolerated gap: a variant with exactly one representation and no statut yet.
    Treated as 'current' by default (there is nothing else it could be), but signalled — not silently
    accepted — until the referentiel is completed."""
    return len(representations) == 1 and "status" not in representations[0]


def check_representations(where, representations):
    """A variant's representations: several are allowed (a redraw keeps its predecessors, they are not
    a fault), but exactly one must carry statut 'current', and at most three may carry 'previous'.
    List order means nothing — statut is the only thing that decides which is shown. The one exception
    is a variant with a single representation and no statut at all: tolerated as an implicit 'current'
    (see has_unlabelled_single_representation), reported separately, never here."""
    if not representations or has_unlabelled_single_representation(representations):
        return
    for representation in representations:
        if representation.get("status") not in STATUSES:
            raise Fault(f"{where}: representation {representation.get('path')!r} has missing or "
                        f"invalid statut {representation.get('status')!r}")
    current = [r for r in representations if r["status"] == "current"]
    if len(current) != 1:
        raise Fault(f"{where}: expected exactly one representation with statut 'current', "
                    f"found {len(current)}")
    # No ceiling on how many earlier versions a variant holds: every one is kept and versioned.


def check_schema(data):
    """Structural conformance, checked top to bottom; raises Fault on the first thing that does not
    hold. Nothing here is fixed up — a caller sees exactly why the file was refused."""
    if data.get("format") != "gatebeast-subjects":
        raise Fault("missing or wrong format marker")
    types = data.get("types")
    subjects = data.get("subjects")
    if not isinstance(types, dict) or not types:
        raise Fault("no types declared")
    if not isinstance(subjects, dict):
        raise Fault("no sujets section")

    for name, type_ in types.items():
        if type_.get("layer") not in LAYERS:
            raise Fault(f"type {name}: unknown or missing layer {type_.get('layer')!r}")
        if type_.get("passage_default") not in ("open", "closed"):
            raise Fault(f"type {name}: passage_default must be exactly 'open' or 'closed'")
        # A type's lot says which variants it expects of its sujets; it names them by their ref, and by
        # nothing else — the ref is what will be produced, recorded and shown under that name.
        for variant in type_.get("batch_v0", []):
            if not variant.get("ref"):
                raise Fault(f"type {name} lot_v0: an expected variant carries no ref")
        compositions = type_.get("compositions")
        if compositions and compositions.get("default") not in compositions.get("values", []):
            raise Fault(f"type {name}: composition default is not one of its own values")

    for code, subject in subjects.items():
        if not CODE_PATTERN.match(code):
            raise Fault(f"sujet code not in the XX-nnn form: {code}")
        type_name = subject.get("type")
        if type_name not in types:
            raise Fault(f"{code}: type {type_name!r} is not declared among types")
        footprint = subject.get("footprint") or {}
        columns, rows = footprint.get("columns"), footprint.get("rows")
        if not isinstance(columns, int) or not isinstance(rows, int) or columns < 1 or rows < 1:
            raise Fault(f"{code}: emprise missing or not a positive number of tiles")
        if not subject.get("variants"):
            raise Fault(f"{code}: no variants")
        refs = [variant.get("ref") for variant in subject["variants"]]
        if len(set(refs)) != len(refs):
            raise Fault(f"{code}: two variants share a ref — a ref designates one variant and one only")
        for variant in subject["variants"]:
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
            gate = variant.get("gate")
            allowed_gates = (types[type_name].get("gates") or {}).get("values")
            if gate and (not allowed_gates or gate not in allowed_gates):
                raise Fault(f"{code}: portillon {gate!r} is not declared by type {type_name}")
        overrides = (subject.get("passage") or {}).get("cells", {})
        for cell in overrides:
            if not re.fullmatch(r"\d+,\d+", cell):
                raise Fault(f"{code}: passage cell key {cell!r} is not 'column,row'")
            column, row = (int(part) for part in cell.split(","))
            if column >= columns or row >= rows:
                raise Fault(f"{code}: passage cell {cell!r} falls outside its {columns}x{rows} emprise")
            for edge, value in overrides[cell].items():
                if edge not in EDGES or not isinstance(value, bool):
                    raise Fault(f"{code}: passage cell {cell!r} has a bad edge {edge!r}")


def resolve_passage(subject, type_):
    """Every cell of a sujet's footprint, every edge resolved with the level that decided it — the
    type's default, or the sujet's own override. Declared 'case par case', never deduced from the
    shape (sujets-et-variantes.md, decisions 13 and 16)."""
    columns, rows = subject["footprint"]["columns"], subject["footprint"]["rows"]
    default_open = type_["passage_default"] == "open"
    overrides = (subject.get("passage") or {}).get("cells", {})
    cells = []
    for row in range(rows):
        for column in range(columns):
            key = f"{column},{row}"
            override = overrides.get(key, {})
            resolved = {}
            for edge in EDGES:
                if edge in override:
                    resolved[edge] = (override[edge], "subject")
                else:
                    resolved[edge] = (default_open, f"type {subject['type']}")
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
    for subject in data["subjects"].values():
        for variant in subject["variants"]:
            for representation in variant.get("representations", []):
                claimed.add(representation["path"])
    return claimed


def variants_with_implicit_status(data):
    """Every variant tolerated under has_unlabelled_single_representation: its lone representation is
    treated as 'current' by default, but it is surfaced here so the gap does not stay invisible until
    the referentiel is completed with an explicit statut."""
    pending = []
    for code, subject in data["subjects"].items():
        for variant in subject["variants"]:
            representations = variant.get("representations") or []
            if has_unlabelled_single_representation(representations):
                pending.append((code, representations[0]["path"]))
    return pending


def probe_stems(outside_referential):
    """The file stems of the deliberately out-of-referentiel probes (subjects.json, _outside_referential):
    their files are expected on disk without any variant claiming them, so they must not be reported as
    unclaimed."""
    return set(outside_referential)


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


def main(verbose=False):
    try:
        data = load()
        check_schema(data)
    except Fault as fault:
        print(f"REFUSED: {fault}")
        return 1

    outside_referential = {key: value for key, value in data.get("_outside_referential", {}).items()
                        if key != "_comment"}
    print(f"{len(data['types'])} types, {len(data['subjects'])} sujets, "
          f"{len(outside_referential)} hors référentiel\n")

    # The passage of every cell of every sujet is thousands of lines — a building of sixteen by ten
    # alone prints a hundred and sixty. It is a detail one asks for; what this tool is run for is its
    # verdict. Kept behind --verbose, and summarised by default.
    print("PASSAGE — résolu niveau par niveau (type, puis sujet)")
    for code in sorted(data["subjects"]):
        subject = data["subjects"][code]
        type_ = data["types"][subject["type"]]
        resolved_cells = list(resolve_passage(subject, type_))
        if not verbose:
            redefined = sum(1 for _, resolved in resolved_cells
                            if any(state[1] != f"type {subject['type']}" for state in resolved.values()))
            print(f"  {code} ({subject['type']}, défaut du type : {type_['passage_default']}) — "
                  f"{len(resolved_cells)} case(s), {redefined} redéfinie(s)")
            continue
        print(f"  {code} ({subject['type']}, défaut du type : {type_['passage_default']})")
        for key, resolved in resolved_cells:
            state = "  ".join(f"{edge}={'ouvert' if resolved[edge][0] else 'fermé'}"
                              f"[{resolved[edge][1]}]" for edge in EDGES)
            print(f"    case {key} : {state}")

    print("\nINVENTAIRE — chaque code de sujet doit y être réellement inscrit")
    texts = inventory_text()
    absent = [code for code in sorted(data["subjects"]) if not code_in_inventory(code, texts)]
    if absent:
        for code in absent:
            print(f"  ABSENT DE L'INVENTAIRE : {code}")
    else:
        print(f"  les {len(data['subjects'])} sujets sont bien à l'inventaire")

    print("\nDISQUE — tout livrable sous assets/cutout/ doit être réclamé")
    claimed = claimed_paths(data)
    expected_probes = probe_stems(outside_referential)
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
            print(f"  {code} : {path} — à compléter d'un statut 'current' explicite")
    else:
        print("  chaque représentation porte un statut explicite")

    if outside_referential:
        print(f"\nHORS RÉFÉRENTIEL ({len(outside_referential)}) — sondes sans code ni emprise fabriqués")
        for code, reason in outside_referential.items():
            print(f"  {code} : {reason}")

    return 1 if absent or unclaimed else 0


if __name__ == "__main__":
    sys.exit(main("--verbose" in sys.argv[1:]))
