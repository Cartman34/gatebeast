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
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# `local/scripts` IS SCANNED LIKE THE REST, AND IT IS WHERE THE FRENCH ACTUALLY LIVES. The rule holds everywhere — a technical name is English, `local/` included
# (operator, 2026-08-10) — but the sweep stopped at the versioned tooling, so a hundred throwaway scripts grew French names while the control declared everything
# clean. A directory left out of a check is a directory where the rule does not exist.
SCANNED = ("scripts", "review-server", "local/scripts")
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

# THE VERBS A FILE NAME STARTS WITH, AND THEY ARE CHECKED ONLY THERE. A script is named for what it does, so its French shows up in its verb — `montrer-`,
# `tirer-`, `mesurer-` — and never in the schema vocabulary above. The rule has always said « noms, contenu, commentaires » ; only the content was ever checked,
# which is why `local/scripts/` filled with French names while the control declared everything clean (operator, 2026-08-10 : « je mets en place des process et ils
# ne sont pas respectés »).
#
# A DENYLIST IS A WEAK GUARD, AND IT IS SAID HERE RATHER THAN DISCOVERED LATER: it catches the words it knows and nothing else, so a French name built on a verb
# absent from this list passes. It is the strongest guard available without leaving the project — an outside dictionary would be a dependency nobody validated,
# on a machine where it exists and on every other where it does not. Each new offender met is added here rather than renamed in silence.
FORBIDDEN_IN_NAMES = {
    "montrer": "show",
    "tirer": "shoot",
    "cliquer": "click",
    "mesurer": "measure",
    "voir": "see",
    "lister": "list",
    "compter": "count",
    "ajouter": "add",
    "corriger": "fix",
    "declarer": "declare",
    "nommer": "name",
    "renommer": "rename",
    "poser": "place",
    "migrer": "migrate",
    "essai": "trial",
    "sonde": "probe",
    "verifier": "verify",
    "reprendre": "resume",
    "produire": "produce",
    "comparer": "compare",
    "decouper": "cut",
    "extraire": "extract",
    "figer": "freeze",
    "nettoyer": "clean",
    "ranger": "tidy",
    "supprimer": "delete",
    "remplacer": "replace",
    "retirer": "remove",
    "zoomer": "zoom",
    "dessiner": "draw",
    "ecrire": "write",
    "rendre": "render",
    "angliciser": "anglicise",
    "requalifier": "requalify",
    "slugger": "slug",
    "recoudre": "stitch",
    "redresser": "straighten",
    "remonter": "raise",
    "degager": "clear",
    "casser": "break",
    "replier": "wrap",
    "reattacher": "reattach",
    "reevaluer": "reassess",
    "regarder": "look",
    "peser": "weigh",
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


def operator_text(literal):
    """Whether a quoted literal is a message meant for the operator, which stays French, rather than a value the machine compares.

    THE CONTROL WAS COUNTING EXACTLY WHAT IT ANNOUNCED IT DID NOT COUNT, and that is why nobody ran it: 126 findings, nearly all of them labels and messages —
    « Chemin », « Vue principale », « Hauteur déclarée ». A control that cries on what it says it ignores switches itself off, and the rule it guards stops being
    applied (operator, 2026-08-10 : « je mets en place des process et ils ne sont pas respectés »).

    THREE SIGNS, AND THEY ARE THE ONES A COMPARED VALUE NEVER HAS: a capital letter, an accent, or a space. Keys, statuses and slugs are written in lowercase
    ASCII without spaces — `courante`, `sujets`, `planche-` — precisely so that the machine can compare them. Anything wearing one of those three signs is
    addressed to a human. It is a heuristic, not a proof: `'Chemin'` as a data key would slip through, and the answer to that is to fix the key, not the check.
    """
    return any(character.isupper() for character in literal) or " " in literal or any(character in "àâçéèêëîïôûùüÿœæ" for character in literal.lower())


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
            if node.value in docstrings or len(node.value.split()) > 2 or operator_text(node.value):
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
            quoted = token[0] in "'\""
            if len(bare.split()) > 2 or (quoted and operator_text(bare)):
                continue
            for word in french_words(bare):
                found.append((number, token, word))
    return found


def main(argv):
    # LE VERDICT D'ABORD, LE DÉTAIL SUR DEMANDE (methode/execution.md, « Une sortie qui inonde le contexte »). Six cent neuf lignes partaient dans le contexte de
    # l'appelant à chaque passage, tronquées avant la fin : l'outil ne disait même plus tout ce qu'il avait trouvé. Il rend maintenant son compte par répertoire,
    # ce qui suffit à savoir où est la dette, et `--detail` rouvre la liste entière.
    detail = "--detail" in argv
    argv = [a for a in argv if a != "--detail"]
    if argv:
        targets = [pathlib.Path(a).resolve() for a in argv]
    else:
        targets = [p for directory in SCANNED for p in (ROOT / directory).rglob("*") if p.suffix in SUFFIXES]

    faults = []
    by_directory = collections.Counter()
    for path in sorted(targets):
        if not path.is_file() or path.suffix not in SUFFIXES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXEMPT:
            continue
        # THE NAME IS CHECKED BEFORE THE CONTENT, because a file whose own name breaks the rule teaches it to everything that cites it.
        # LE RÉPERTOIRE DE TÊTE PORTE LE COMPTE, parce que c'est lui qui dit à qui la dette appartient : `local/scripts/` est le jetable de l'agent, `scripts/`
        # est l'outillage du projet, et confondre les deux fait paraître énorme une dette qui, pour l'essentiel, se supprime avec ses fichiers.
        parts = relative.split("/")
        family = "/".join(parts[:2]) if parts[0] == "local" else parts[0]
        for word in re.findall(r"[a-zà-ÿ]+", path.stem.lower()):
            if word in FORBIDDEN_IN_NAMES:
                faults.append(f"  {relative} — le NOM porte « {word} », à écrire « {FORBIDDEN_IN_NAMES[word]} »")
                by_directory[family] += 1

        source = path.read_text(encoding="utf-8", errors="replace")
        found = check_python(path, source) if path.suffix == ".py" else check_text(path, source)
        for number, token, word in found:
            faults.append(f"  {relative}:{number} — « {token} » porte « {word} », à écrire « {FORBIDDEN[word]} »")
            by_directory[family] += 1

    if faults:
        print(f"{len(faults)} valeur(s) technique(s) en français dans le code, sur {len(targets)} fichier(s) lus :", file=sys.stderr)
        for family, count in by_directory.most_common():
            print(f"  {family}/ — {count}", file=sys.stderr)
        if detail:
            print("\n".join(faults), file=sys.stderr)
        else:
            print(f"\n{len(faults)} ligne(s) de détail tues — « --detail » les rouvre.", file=sys.stderr)
        print("Les commentaires et les textes destinés à l'opérateur restent en français ; les noms et les valeurs comparées, jamais.", file=sys.stderr)
        return 1

    print(f"{len(targets)} fichier(s) : aucun vocabulaire technique en français.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
