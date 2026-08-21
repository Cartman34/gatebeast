#!/usr/bin/env python3
"""Refuse French technical vocabulary in code: identifiers, data keys and the values compared against them.

Usage:
  python3 scripts/check-code-language.py [files...]   — checks the files given, or all of scripts/ and review-server/ when none are.
  python3 scripts/check-code-language.py -v           — the findings one by one; without it, the verdict and the count per directory.
  python3 scripts/check-code-language.py -h           — this text.
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

# A FRENCH WORD SOUGHT INSIDE FRENCH PROSE IS NOT A FRENCH VALUE, AND TRANSLATING IT WOULD BREAK THE SEARCH. These files hold needles, not data: they look for
# « largeur » or « poteau » in the subject descriptions, which are French by rule and will stay so. Rendered in English, the pattern would match nothing and the
# check that uses it would pass on everything — silently.
#
# THEY ARE NAMED HERE RATHER THAN LEFT TO BE REDISCOVERED. Counted as debt, they made this control report twenty findings that nobody could act on, which is how
# a control stops being run (`S88 valeurs-fr-restantes`, measured on 2026-08-20: of its twenty-three findings, most were needles).
SEARCHES_FRENCH_PROSE = {
    "scripts/check-subject-parameters.php",
    "scripts/dev/trial-height-bands.php",
    "local/scripts/dump-grid-history.sh",
    # These two LOOK FOR the French debt, so their patterns are made of it. Counting them as debt would mean the tools that measure a problem count as the
    # problem — and each word added to their search would raise the very number they exist to lower.
    "local/scripts/count-french-locals.sh",
    "local/scripts/list-french-locals.sh",
}
EXEMPT |= SEARCHES_FRENCH_PROSE

# A PREFIX THAT NAMES REAL FILES IS NOT A FRENCH VALUE, IT IS THEIR ADDRESS. Six plates live under `assets/revue-da/` as `planche-p1-campagne-v8.png` and the
# like, cited by name in `doc/conception/referentiels/visuel/planches-de-reference.md`. Code that builds those names must spell them as they are: renaming the
# prefix means renaming the assets AND rewriting the conception that quotes them, which is a decision, not a cleanup.
#
# THEY ARE DECLARED RATHER THAN SILENCED. Left in the count, five findings nobody can act on sat at the top of every listing, and a debt that cannot be paid
# hides the one that can — `S88 valeurs-fr-restantes` carries the decision, and this comment is what points at it.
NAMES_REAL_ASSETS = {
    "scripts/build-planches-page.py",
    "scripts/build-plate-reports.py",
    "scripts/build-projection-plate.php",
    "scripts/plate_common.py",
}
EXEMPT |= NAMES_REAL_ASSETS


def french_words(text):
    """The forbidden French words a text carries, camelCase included.

    A CAMELCASE NAME IS SEVERAL WORDS, AND THIS READ ONLY THE WHOLE. Lowercasing `$largeurDeLaPage` gives one token, `largeurdelapage`, which matches nothing —
    so every French word glued to another passed unseen, which is to say most of the names an agent writes. `$titreMien` was caught only because the check also
    reads `$titre` elsewhere in that same file. Splitting on the capitals first is what makes the rule bite where names are actually built.
    """
    split = re.sub(r"(?<=[a-zà-ÿ])(?=[A-ZÀ-Þ])", " ", text)

    return {word for word in re.findall(r"[A-Za-zÀ-ÿ_]+", split.lower()) if word in FORBIDDEN}


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


# A DELIMITED PATTERN CARRYING PATTERN SYNTAX, and both halves are required. The delimiters alone would swallow `'/planche-'`, which is a real path fragment and a
# real find; the escapes alone would fire on any string holding a backslash.
REGEX_DELIMITED = re.compile(r"^([/~#@%!])(?:\\.|(?!\1).)+\1[a-zA-Z]*$", re.S)
REGEX_SYNTAX = re.compile(r"\\[sdwbSDWB]|\(\?|\[\^|\{\d")


def is_regex(literal):
    """Whether a quoted literal is a PATTERN rather than a value the machine compares.

    A PATTERN THAT READS FRENCH PROSE MUST BE WRITTEN IN FRENCH, and reporting it asks for the impossible: the inventory writes « hauteur 8 cases » in the
    operator's language, so the expression that finds that line spells « hauteur » too. Translating it would not make the code more English — it would stop the
    expression matching anything at all, in silence, which is the exact failure this project forbids by name. So the word inside a pattern is data being read,
    never a name being written, and it is left alone.
    """
    return bool(REGEX_DELIMITED.match(literal)) and bool(REGEX_SYNTAX.search(literal))


def label_columns(tree):
    """The string constants that sit in a COLUMN OF LABELS, and are therefore shown rather than compared.

    A PLATE'S COMPOSITION IS A TABLE, AND ONE OF ITS COLUMNS IS FRENCH ON PURPOSE. `("road", 1, 12, 18, 12, "chemin")` names a kind in its first position — a
    value the machine compares, English, rightly guarded — and in its last the words written on the drawing for the operator to read. One-word labels wear none
    of the three signs that mark prose, so « chemin » was reported while « chemin du bord de falaise », three lines below and exactly the same thing, was not.

    THE COLUMN IS WHAT IS RECOGNISED, NEVER THE WORD. Among tuples of the same length gathered in one list, a position whose strings are MOSTLY prose is a label
    column, and the short ones sharing it are labels too. Nothing else in the file is exempted, and a table with no prose in it is not one — which is why the
    first position, holding `road` and `rock`, stays guarded.
    """
    labels = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.List, ast.Tuple)):
            continue
        rows = [row for row in node.elts if isinstance(row, ast.Tuple)]
        if len(rows) < 3 or len({len(row.elts) for row in rows}) != 1:
            continue
        for position in range(len(rows[0].elts)):
            cells = [row.elts[position] for row in rows]
            strings = [cell for cell in cells if isinstance(cell, ast.Constant) and isinstance(cell.value, str)]
            if len(strings) != len(cells):
                continue
            # AN EMPTY CELL IS NEITHER A LABEL NOR A COMPARED VALUE, so it votes on neither side.
            written = [cell for cell in strings if cell.value != ""]
            prose = [cell for cell in written if operator_text(cell.value) or len(cell.value.split()) > 2]
            # TWO SENTENCES ARE ENOUGH, AND A MAJORITY IS THE WRONG TEST. What separates the two kinds of column is not how many labels are long but whether the
            # column can hold a sentence AT ALL: a column of compared values — `road`, `rock`, `water` — never does, by construction, while a column of labels
            # does as soon as one thing needs more than a word to name it. Asking for a majority made the answer depend on how many short names a plate happened
            # to use: p5's column passed with fourteen sentences, p6's failed with fourteen of its own, and the two hold exactly the same kind of thing. Two
            # rather than one so that a single accident cannot open a column.
            if len(prose) >= 2:
                labels.update(id(cell) for cell in strings)
    return labels


def check_python(path, source):
    """Names and compared values only — a docstring or a displayed message is prose and stays French."""
    found = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return found
    labels = label_columns(tree)
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
            if id(node) in labels or is_regex(node.value):
                continue
            for word in french_words(node.value):
                found.append((node.lineno, repr(node.value), word))
    return found


def check_text(path, source):
    """For PHP, JavaScript and shell: identifiers and short quoted values, comments skipped.

    THE LITERALS COME OUT OF THE LINE FIRST, AND THAT IS THE WHOLE ORDER OF THIS FUNCTION. It used to capture quoted strings of up to thirty characters and scan
    the raw line for identifiers — so a longer message, which is precisely what a sentence addressed to the operator is, was never seen as a literal at all: its
    words were read one by one as if they were identifiers, and « FAUTE le fichier de remarques est illisible » was reported as a French symbol. Five of the
    five findings on scripts/remarks.php were of that family, all of them messages the rule explicitly keeps in French.

    A CONTROL THAT CRIES ON WHAT IT ANNOUNCES IT IGNORES SWITCHES ITSELF OFF — it is written above, it was paid for once already, and it had come back by
    two more doors, both closed here: a block comment read line by line, and a line of markup.
    """
    found = []
    line_comment = re.compile(r"^\s*(//|#)")
    # AN ESCAPED QUOTE DOES NOT CLOSE A STRING, and forgetting it left the tail of a message being read as code: « ...dit POURQUOI elle l\'est — consigne
    # corrigée » ended at the apostrophe, and « consigne » was reported as a symbol.
    literal = re.compile(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"")
    inside_block = False
    inside_html = False
    # A SHELL HEREDOC IS A PAYLOAD, NOT CODE. What a shell script sends to another command — a sample file, a JSON body, a fixture — is data written between two
    # markers, and reading it as code made a trial that feeds the checker French on purpose report its own fixture, five times. PHP heredocs are NOT skipped and
    # must not be: there the heredoc is markup a builder produces, and it interpolates real names the rule applies to.
    heredoc = None
    heredoc_opening = re.compile(r"<<-?\s*[\"']?([A-Za-z_][A-Za-z0-9_]*)[\"']?\s*$")
    for number, line in enumerate(source.splitlines(), 1):
        if heredoc is not None:
            if line.strip() == heredoc:
                heredoc = None
            continue
        if path.suffix == ".sh":
            opening = heredoc_opening.search(line)
            if opening:
                heredoc = opening.group(1)
                continue
        # A BLOCK COMMENT IS FOLLOWED FROM LINE TO LINE, NEVER RECOGNISED ONE LINE AT A TIME. Its continuation lines carry no marker of their own — a docblock
        # writes ` * `, but an ordinary `/* … */` paragraph just indents — so they were read as code, and any punctuation the French prose happened to contain
        # was enough to make them look like it. « Ce qui dépasse se parcourt en largeur ; … » held a semicolon, and « largeur » was reported as a symbol.
        code = line
        # THE TWO BLOCK COMMENTS ARE FOLLOWED SEPARATELY, and mixing them would be worse than not reading HTML at all: an unclosed `<!--` looking for a `*/`
        # would swallow the whole rest of the file, silently, and this control would pass on everything after it.
        if inside_html:
            closing = code.find("-->")
            if closing == -1:
                continue
            code = code[closing + 3:]
            inside_html = False
        if inside_block:
            closing = code.find("*/")
            if closing == -1:
                continue
            code = code[closing + 2:]
            inside_block = False
        code = re.sub(r"/\*.*?\*/", " ", code)
        opening = code.find("/*")
        if opening != -1:
            inside_block = True
            code = code[:opening]
        # AN HTML COMMENT IS PROSE TOO, AND IT WAS THE ONLY KIND LEFT UNREAD. A page builder writes `<!-- TOUTE PAGE DIT SON CHEMIN … -->` into the markup it
        # produces: that is a comment explaining the code, so it belongs to `check-comment-language.php` and not here — this file judges NAMES and VALUES, as
        # its own intention says. Three findings sat in the listing for that reason alone, and a finding nobody can act on is what makes a listing unread.
        code = re.sub(r"<!--.*?-->", " ", code)
        opening = code.find("<!--")
        if opening != -1:
            inside_html = True
            code = code[:opening]
        if line_comment.match(code):
            continue
        code = re.sub(r"(//|#).*$", "", code)
        for token in literal.findall(code):
            bare = token.strip("'\"")
            if len(bare.split()) > 2 or operator_text(bare) or is_regex(bare):
                continue
            for word in french_words(bare):
                found.append((number, token, word))
        # What is left once the strings are gone is code, and only code: names of variables, functions, classes, keys.
        # A LINE THAT CARRIES NO CODE AT ALL IS NOT SCANNED FOR NAMES. A page builder holds whole sentences of French prose inside a heredoc — markup, a
        # paragraph shown to the operator — and every word of them was being read as an identifier. The sign is mechanical and cheap: code punctuates, prose
        # does not. No `$`, no assignment, no call, no arrow, no brace: nothing here is a name.
        rest = literal.sub(' ', code)
        if not re.search(r"[$=(){}\[\];]|->|::", rest):
            continue
        # AND A LINE OF MARKUP IS READ FOR ITS CODE ONLY, never for its words. `<p class="lede">Ce que le monde contient, sujet par sujet …` keeps the `=` of its
        # attribute once the quoted value is gone, so the sentence behind the tag was read word by word as identifiers. What a tag encloses is shown to the
        # operator and stays French — but a builder does interpolate real names in there, so the line is not skipped outright: only what CARRIES THE MARKS OF
        # CODE is kept — a `$variable`, a `call(`, what follows `->` or `::`. Attribute values are literals and were already read as such just above.
        names = re.findall(r"\$?[A-Za-zÀ-ÿ_][A-Za-zÀ-ÿ_0-9]*", rest)
        if re.search(r"</[A-Za-z]|<[A-Za-z][\w-]*(\s[^<>]*)?/?>", rest):
            names = re.findall(r"\$[A-Za-zÀ-ÿ_]\w*|[A-Za-zÀ-ÿ_]\w*(?=\s*\()|(?<=->)\w+|(?<=::)\w+", rest)
        for token in names:
            for word in french_words(token.strip('$')):
                found.append((number, token, word))
    return found


def main(argv):
    # LE VERDICT D'ABORD, LE DÉTAIL SUR DEMANDE (methode/execution.md, « Une sortie qui inonde le contexte »). Six cent neuf lignes partaient dans le contexte de
    # l'appelant à chaque passage, tronquées avant la fin : l'outil ne disait même plus tout ce qu'il avait trouvé. Il rend maintenant son compte par répertoire,
    # ce qui suffit à savoir où est la dette, et `--detail` rouvre la liste entière.
    # THE OPTION IS THE ONE EVERYONE KNOWS, `-v` / `--verbose`, and never a name invented for the occasion (operator, 2026-08-12). It was `--detail` for half a
    # day: clear, and unfindable without reading the help, which is exactly what a universal convention gives for free.
    detail = "-v" in argv or "--verbose" in argv
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    argv = [a for a in argv if a not in ("-v", "--verbose")]
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
            print(f"\n{len(faults)} ligne(s) de détail tues — « -v » les rouvre.", file=sys.stderr)
        print("Les commentaires et les textes destinés à l'opérateur restent en français ; les noms et les valeurs comparées, jamais.", file=sys.stderr)
        return 1

    print(f"{len(targets)} fichier(s) : aucun vocabulaire technique en français.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
