#!/usr/bin/env python3
"""Give a verdict to one produced version of a variant, and recompute which version is current.

Usage:
  python3 scripts/set-asset-verdict.py --code BT-001 --variant p2 --version v4 --verdict discarded \\
      [--comment "..."] [--dry-run]
  python3 scripts/set-asset-verdict.py --code BT-001 --variant p2 --list

  --variant matches a variant by its proposition value ("p2"), its ref, or its label; "main"
  picks the main view. --version matches the tail of the delivered path ("v4", or the file name).
  --verdict is one of approved, rework, discarded. Repeat --version to judge several at once.
  -h|--help prints this text and writes nothing.

Intention:
  NOTHING WROTE THESE TWO FIELDS, AND THEY DECIDE WHAT THE NEXT GENERATION COPIES. The command picks
  its own reference from the current version of the variant, so a version wrongly left current is
  reproduced into every later one — that is exactly how the care centre's proposition 2 lost its
  palette on 2026-08-08, and setting it right meant editing the referential by hand, which the design
  forbids ("le catalogue s'écrit à l'entrée, jamais à la main"). A hand-kept file and the disk diverge
  within a week; a tool does not.

  IT NEVER DELETES AN IMAGE. A discarded version stops being shown, it is not removed — the
  repository rule is explicit. Only the two fields move: the verdict is recorded on the version, and
  the newest version that has not been discarded becomes current. That second half is the point: a
  verdict alone would leave a discarded image current, which is the failure this exists to end.

  AND IT REPUBLISHES THE REVIEW PAGE, because it has just changed what that page shows. Without it the
  page lies behind the command: on 2026-08-12 the oak's current version went back to v12 in the data
  while the page still displayed v14, and the operator saw it first. Every write that changes what is
  given to judge republishes, or nobody judges on what is displayed.

  Python rather than PHP because it reads and rewrites the same referential as record-asset.py, its
  only other writer, and the two must agree on how the file is loaded and dumped.
"""

import argparse
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REFERENTIAL = ROOT / "assets" / "subjects.json"
VERDICTS = ("approved", "rework", "discarded")

# THE REPUBLICATION IS TAKEN WHERE IT ALREADY LIVES, IT IS NOT COPIED. It belongs to the production command, which writes the same referential this one does and
# which holds the lock keeping two concurrent rebuilds of that one page apart. Rewriting it here would give two versions of it, diverging at the first fix — and
# the page's route has already changed once. The file is loaded by path because its name is hyphenated: this is the mechanism record-asset.py and
# generate-sprite.py already use for check-subjects.py.
GENERATE_SPRITE = pathlib.Path(__file__).resolve().parent / "generate-sprite.py"
spec = importlib.util.spec_from_file_location("generate_sprite", GENERATE_SPRITE)
generate_sprite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_sprite)


def find_subject(data, code):
    subjects = data["subjects"]
    if isinstance(subjects, dict):
        subject = subjects.get(code)
    else:
        subject = next((s for s in subjects if s.get("code") == code), None)
    if subject is None:
        raise SystemExit(f"FAULT le subject « {code} » n'est pas au référentiel.")
    return subject


def find_variant(subject, wanted):
    variants = subject.get("variants", [])
    if wanted in ("main", "principal"):
        found = [v for v in variants if v.get("main")]
    else:
        found = [
            v for v in variants
            if wanted in (v.get("proposition"), v.get("ref"), v.get("label"))
        ]
    if not found:
        known = ", ".join(str(v.get("proposition") or v.get("label")) for v in variants)
        raise SystemExit(f"FAULT le variant « {wanted} » n'existe pas — connus : {known}.")
    if len(found) > 1:
        raise SystemExit(f"FAULT le variant « {wanted} » en désigne {len(found)} — précise sa ref.")
    return found[0]


def stem(representation):
    return pathlib.Path(representation.get("path", "")).stem


def match_version(representation, wanted):
    """A version is named by the tail of its file: "v4" matches BT-001_proposition-p2-v4."""
    name = stem(representation)
    return name == wanted or name.endswith("-" + wanted) or name == pathlib.Path(wanted).stem


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--code", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--version", action="append", default=[])
    parser.add_argument("--verdict", choices=VERDICTS)
    parser.add_argument("--comment")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(REFERENTIAL.read_text(encoding="utf-8"))
    subject = find_subject(data, args.code)
    variant = find_variant(subject, args.variant)
    representations = variant.get("representations", [])

    if args.list:
        print(f"{args.code} — variant « {variant.get('label', args.variant)} »")
        for representation in representations:
            print("  %-46s %-11s %s" % (
                stem(representation),
                representation.get("status", "?"),
                representation.get("verdict", "") or "",
            ))
        return 0

    if not args.version or not args.verdict:
        raise SystemExit("FAULT il faut --version et --verdict, ou --list.")

    touched = []
    for wanted in args.version:
        found = [r for r in representations if match_version(r, wanted)]
        if not found:
            known = ", ".join(stem(r) for r in representations)
            raise SystemExit(f"FAULT la version « {wanted} » n'existe pas — connues : {known}.")
        for representation in found:
            representation["verdict"] = args.verdict
            if args.comment:
                representation["operator_comment"] = args.comment
            touched.append(stem(representation))

    # THE NEWEST VERSION NOT DISCARDED BECOMES CURRENT. The list is kept newest-first by the tool that
    # writes it, so the first survivor wins; if every version is discarded, none is current, and the
    # variant reads as having nothing to show rather than silently keeping a rejected image.
    # A DISCARDED VERSION STAYS "previous", IT GETS NO STATUS OF ITS OWN. The referential knows two
    # statuses and two only — the one shown, and the ones kept for record — and a discarded image is
    # kept for record like any other: the repository rule says it stops being shown, not that it is
    # removed. Inventing a third status looked cleaner and was refused by check-subjects.py on the spot,
    # which is the right answer: a schema grows at the design, never as a side effect of a fix.
    promoted = None
    for representation in representations:
        if representation.get("verdict") == "discarded":
            representation["status"] = "previous"
            continue
        representation["status"] = "current" if promoted is None else "previous"
        if promoted is None:
            promoted = stem(representation)

    print("Jugées : " + ", ".join(touched) + f" → {args.verdict}")
    print("Courante : " + (promoted or "AUCUNE — toutes les versions sont écartées"))

    if args.dry_run:
        print("Essai à blanc — le référentiel n'est pas écrit.")
        return 0

    REFERENTIAL.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{REFERENTIAL.relative_to(ROOT)} écrit.")
    # THE VERDICT IS WRITTEN, THAT MUCH IS ACQUIRED: a failed republication reports itself and the command still returns 0 — it does not undo the verdict and
    # does not stop here. It comes AFTER the write, never before: rebuilding the page on data not yet laid down would display the state from before it.
    generate_sprite.republish_review_page()

    return 0


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        raise SystemExit(0)
    sys.exit(main())
