#!/usr/bin/env python3
"""Refuse French technical vocabulary in code: identifiers, data keys and the values compared against them.

Usage:
  python3 scripts/check-code-language.py [files...]   — checks the files given, or all of scripts/ and review-server/ when none are.
  Exits non-zero on any find, naming the file, the line and the word.

Intention:
  THE OPERATOR SIGNALLED THIS THREE TIMES AND IT CAME BACK THREE TIMES (2026-08-08): « des codes, des ref, des valeurs techniques, tout ça doit ABSOLUMENT être
  en anglais dans le code ». Three repeats of the same fault is not forgetfulness, it is a missing check — the repository already applies that reasoning to its
  text width, and for the same reason: an agent rewriting code cannot miss what nothing tells it about, and its own habit comes back the moment it stops watching
  for it explicitly.

  IT JUDGES CODE, NOT PROSE. Comments and operator-facing strings stay French — that is the rule, not an exception to it: only what the machine reads and compares
  must be English. So a word is reported when it is used as a NAME or as a compared VALUE, and left alone inside a comment or a displayed message. The separation
  is crude on purpose: a checker that tried to understand every string would be wrong quietly, where this one is wrong loudly and gets corrected.

  THE KNOWN-BAD LIST IS DELIBERATELY SHORT. It carries the words the project actually got wrong, not a dictionary — a long list would fire on French prose and be
  switched off within a week. It grows one word at a time, each time something slips through.

  Python rather than PHP because it walks Python sources with the ast module, which alone tells a string used as a value from a string sitting in a docstring;
  a regular expression over the text cannot make that distinction, and that distinction is the whole check.
"""

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCANNED = ("scripts", "review-server")
SUFFIXES = (".py", ".php", ".js", ".sh")

# The French technical vocabulary the project actually wrote, and what it should read instead. Kept short on purpose: each entry earned its place by being found
# in the code, and the message names the replacement so the fix does not need a second look.
FORBIDDEN = {
    "statut": "status",
    "courante": "current",
    "anterieure": "previous",
    "ecartee": "discarded",
    "ecarter": "discard",
    "mesures": "measures",
    "libelle": "label",
    "principale": "main",
    "sujets": "subjects",
    "sujet": "subject",
    "variante": "variant",
    "consigne": "prompt",
    "brouillon": "draft",
    "planche": "plate",
    "emprise": "footprint",
    "hauteur": "height",
    "largeur": "width",
    "chemin": "path",
    "fichier": "file",
    "verdict": None,
}
FORBIDDEN = {word: better for word, better in FORBIDDEN.items() if better}

# What the referential already carries is not the code's fault and is covered by its own point in the pile; flagging it here would drown the new finds under
# hundreds of old ones and the check would be switched off. These files speak the schema until the schema is migrated.
EXEMPT = {
    "scripts/check-subjects.py",
    "scripts/record-asset.py",
    "scripts/set-asset-verdict.py",
    "scripts/asset_common.py",
    "scripts/generate-sprite.py",
    "scripts/check-code-language.py",
}


def french_words(text):
    return {word for word in re.findall(r"[A-Za-zÀ-ÿ_]+", text.lower()) if word in FORBIDDEN}


def check_python(path, source):
    """Names and compared values only — a docstring or a displayed message is prose and stays French."""
    found = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return found
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                docstrings.add(doc)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Name, ast.arg)):
            name = node.id if isinstance(node, ast.Name) else node.arg
            for word in french_words(name):
                found.append((node.lineno, name, word))
        elif isinstance(node, ast.Attribute):
            for word in french_words(node.attr):
                found.append((node.lineno, node.attr, word))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            # A STRING COUNTS ONLY IF IT LOOKS LIKE A VALUE, NOT A SENTENCE: one or two words, no space beyond a hyphen. « Il faut une consigne » is a message to
            # the operator and stays French; "courante" is a value the machine compares and must not.
            if node.value in docstrings or len(node.value.split()) > 2:
                continue
            for word in french_words(node.value):
                found.append((node.lineno, repr(node.value), word))
    return found


def check_text(path, source):
    """For PHP, JavaScript and shell: identifiers and short quoted values, comments skipped by line."""
    found = []
    comment = re.compile(r"^\s*(//|#|\*|/\*)")
    for number, line in enumerate(source.splitlines(), 1):
        if comment.match(line):
            continue
        code = re.sub(r"(//|#).*$", "", line)
        for token in re.findall(r"\$?[A-Za-zÀ-ÿ_][A-Za-zÀ-ÿ_0-9]*|'[^']{0,30}'|\"[^\"]{0,30}\"", code):
            bare = token.strip("'\"$")
            if len(bare.split()) > 2:
                continue
            for word in french_words(bare):
                found.append((number, token, word))
    return found


def main(argv):
    if argv:
        targets = [pathlib.Path(a).resolve() for a in argv]
    else:
        targets = [p for directory in SCANNED for p in (ROOT / directory).rglob("*") if p.suffix in SUFFIXES]

    faults = []
    for path in sorted(targets):
        if not path.is_file() or path.suffix not in SUFFIXES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXEMPT:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        found = check_python(path, source) if path.suffix == ".py" else check_text(path, source)
        for number, token, word in found:
            faults.append(f"  {relative}:{number} — « {token} » porte « {word} », à écrire « {FORBIDDEN[word]} »")

    if faults:
        print(f"{len(faults)} valeur(s) technique(s) en français dans le code :", file=sys.stderr)
        print("\n".join(faults), file=sys.stderr)
        print("\nLes commentaires et les textes destinés à l'opérateur restent en français ; les noms et les valeurs comparées, jamais.", file=sys.stderr)
        return 1

    print(f"{len(targets)} fichier(s) : aucun vocabulaire technique en français.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
