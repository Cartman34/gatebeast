<?php
/**
 * USAGE
 *   php scripts/check-text-width.php <file>...
 *
 *   Reports every line that breaks the project's single width standard, on any file given: a line over the ceiling, and a run of text lines folded far below it. Prints a verdict and nothing else when
 *   the files are clean; exits 1 as soon as one line is at fault, so it can gate a commit or a hand-off. Run it on whatever was just written, before showing it to anyone.
 *
 *   php scripts/check-text-width.php -h|--help — this text
 *
 * INTENTION
 *   The ceiling is 200 characters and it is the project's ONLY length standard (`doc/regles-du-depot.md`). Agents break it in one direction far more often than
 *   the other: they fold their text to eighty or a hundred characters, because that is the habit they arrive with and because the file they are editing is
 *   already folded that way. Both reasons are forbidden — a rule that is written outranks anything the
 *   surrounding file happens to do — and neither is fixed by asking an agent to be careful: the habit returns the moment attention lapses. So the rule gets a machine that enforces it.
 *
 *   A FOLDED RUN is what catches that habit, and it cannot be caught line by line: one short line proves nothing (a title, a list item, a closing sentence). What proves folding is a RUN of
 *   consecutive text lines that all stop well short of the ceiling while the paragraph clearly continues — the line does not end a sentence, and the next one carries it on. Below FOLD_RUN such a run
 *   is ordinary prose; at or above it, the text was wrapped by hand to a width nobody chose.
 *
 *   In PHP because it is the project's default language for durable tooling, and this needs no library that only Python has.
 */

require_once __DIR__ . '/bootstrap.php';

bootCommand($argv);

const CEILING = 200;
const FOLD_WIDTH = 150;
const FOLD_RUN = 3;

/**
 * Les extensions dont le contenu est du CODE. Dans un de ces fichiers, la seule prose est le commentaire ; tout le reste est instruction, et une instruction n'a
 * rien à remplir. Ailleurs — Markdown, texte — tout est prose.
 */
const CODE_EXTENSIONS = ['php', 'py', 'sh', 'js', 'css', 'json'];

/**
 * True when a line is PROSE in this file — the only thing the folding rule judges.
 *
 * IN A CODE FILE, ONLY A COMMENT IS PROSE (opérateur, 2026-08-07 : « les règles de longueur ne s'appliquent qu'aux commentaires »). Everything else is a
 * statement, and a statement is exempt whatever its width. Trying to tell a folded sentence from a short statement by its punctuation, or by a list of keywords,
 * was a losing game: five includes in a row were reported as a paragraph, then three shell commands were, and each miss teaches everyone to ignore the tool.
 * The comment marker is the one signal that is neither guessed nor fragile.
 */
function isProse(string $line, string $path): bool
{
    if (!in_array(strtolower(pathinfo($path, PATHINFO_EXTENSION)), CODE_EXTENSIONS, true)) {
        return true;
    }
    // Les marques de commentaire des langages du projet : deux barres, un bloc et sa continuation, un dièse. Une ligne qui n'en porte pas est du code.
    return (bool) preg_match('#^\s*(//|/\*|\*|\#)#u', $line);
}

/**
 * True when the line is a JSON string value — the third kind of line that CANNOT be folded, for exactly the reason the two others cannot.
 *
 * JSON HAS NO LINE CONTINUATION: a string value carrying a paragraph is one line by construction, and the only way to shorten it is to shorten the TEXT, which
 * is an editorial choice and never a wrap — the very criterion this file already applies to a Markdown table row and to an inventory entry. The data files of
 * the project hold prose in such values: the critiques of a consigne, the intention of an edit. Reported, they teach everyone to ignore the tool; and the fix
 * an agent would reach for — cutting the sentence — is the forbidden substitution the common method names.
 *
 * THE EXEMPTION IS THE VALUE, NOT THE FILE: a long line of nested JSON on one row stays reported, because that one folds.
 */
function isJsonStringValue(string $line, string $path): bool
{
    if (strtolower(pathinfo($path, PATHINFO_EXTENSION)) !== 'json') {
        return false;
    }

    return (bool) preg_match('/^\s*"[^"]*"\s*:\s*".*",?\s*$/u', $line);
}

/** True when a line looks like the middle of a hand-wrapped paragraph: prose that stops short and does not close a sentence. */
function continuesAParagraph(string $line, string $path = ''): bool
{
    if ($path !== '' && !isProse($line, $path)) {
        return false;
    }
    $trimmed = rtrim($line);
    if ($trimmed === '' || mb_strlen($trimmed) >= FOLD_WIDTH) {
        return false;
    }
    // A line closing on a sentence mark, a list item, a heading, a table row or a fenced block is a line that CHOSE to be short — never evidence of folding. An INSTRUCTION is exempt whatever its
    // width (`doc/regles-du-depot.md`), and it gives itself away by punctuation prose does not use: an assignment, a call, a bracket, a sigil. Without this, every short
    // statement of a script counted as folded prose.
    if (preg_match('/[=(){}\[\]$]/u', $trimmed)) {
        return false;
    }
    // A LINE ENDING IN A SEMICOLON IS A STATEMENT, and several in a row are a block of them — never a hand-wrapped paragraph. Without this, five `require_once` lines one after another were reported
    // as folded prose, on a file where the rule exempts instructions outright. Prose that ends a folded line on a semicolon does exist and will now go unreported; missing one is worth far less than
    // crying wolf on every script of the project, which teaches everyone to ignore the tool.
    if (str_ends_with($trimmed, ';')) {
        return false;
    }
    // A « clé: valeur » LINE IS A DECLARATION, AND A RUN OF THEM IS A HEADER — never a folded paragraph. A header is one key per line by construction: joining
    // two of them would destroy the data, which is precisely what this rule exists never to ask for. Without it, the five-line header of a source block was
    // reported as a paragraph wrapped too short.
    if (preg_match('/^[a-zA-ZÀ-ÿ_][\w-]*\s*:\s*\S/u', $trimmed)) {
        return false;
    }

    return (bool) preg_match('/[a-zA-ZÀ-ÿ0-9,:]$/u', $trimmed) && !preg_match('/^\s*([-*+>#|]|\d+\.|```)/u', ltrim($trimmed));
}

$paths = array_slice($argv, 1);
if (!$paths) {
    fwrite(STDERR, "USAGE : php scripts/check-text-width.php <fichier>...\n");
    exit(2);
}

$faults = 0;
foreach ($paths as $path) {
    if (!is_file($path)) {
        fwrite(STDERR, "ABSENT : {$path}\n");
        $faults++;
        continue;
    }
    $lines = explode("\n", file_get_contents($path));
    $run = [];
    // UN BLOC DE CODE CLÔTURÉ EST DU CONTENU VERBATIM, ET SE REPLIER N'A AUCUN SENS DEDANS. Ce qu'il porte est reproduit tel quel — une commande, un extrait, la
    // clause exacte qu'un générateur va lire —, et rejoindre deux de ses lignes changerait la chose reproduite. C'est la même raison que la ligne de tableau
    // Markdown, déjà exemptée du plafond : le seul « correctif » possible serait de réécrire le contenu, ce qui est un choix éditorial et jamais un repli.
    $fenced = false;
    foreach ($lines as $index => $line) {
        $number = $index + 1;
        $width = mb_strlen($line);
        // Two kinds of line CANNOT be folded, and reporting them is pure noise — the only answer would be a shorter text, an editorial choice, never a wrap:
        // a Markdown table row, whose row ends at the line break, and an inventory entry, which the tooling reads whole by its « - **CODE » opening. Exempt
        // from the ceiling, and from it alone.
        if (preg_match('/^\s*```/', $line)) {
            $fenced = !$fenced;
        }
        $unbreakable = (bool) preg_match('/^\s*\||^- \*\*[A-Z]{2,3}-\d{3} /u', $line) || isJsonStringValue($line, $path) || $fenced;
        if ($width > CEILING && !$unbreakable) {
            echo "{$path}:{$number} : {$width} caractères, plafond " . CEILING . "\n";
            $faults++;
        }
        if (!$fenced && continuesAParagraph($line, $path)) {
            $run[] = $number;
            continue;
        }
        if (count($run) >= FOLD_RUN) {
            echo "{$path}:{$run[0]}-" . end($run) . " : " . count($run) . " lignes repliées sous " . FOLD_WIDTH . " alors que le paragraphe continue — le texte vise " . CEILING . "\n";
            $faults++;
        }
        $run = [];
    }
    if (count($run) >= FOLD_RUN) {
        echo "{$path}:{$run[0]}-" . end($run) . " : " . count($run) . " lignes repliées sous " . FOLD_WIDTH . " alors que le paragraphe continue — le texte vise " . CEILING . "\n";
        $faults++;
    }
}

if ($faults === 0) {
    echo count($paths) . " fichier(s) au standard.\n";
    exit(0);
}
// UN REFUS NOMME LE GESTE QUI DÉBLOQUE (`S90 refus-avec-solution`, opérateur du 2026-08-12 : « une erreur doit TOUJOURS être affichée avec ses solutions, au
// moins une »). Celui-ci a refusé quatre fois dans la même séance en disant seulement « 2 écarts », pendant que l'outil qui replie le texte au plafond
// dormait, versionné, à un répertoire de là — et il a été refait à la main les quatre fois. Le remède n'est pas la mémoire du lecteur, c'est la sortie.
echo "{$faults} écart(s) au standard de largeur.\n";
echo "  Solution, pour une ligne TROP LONGUE — « php scripts/dev/trim-to-ceiling.php <fichiers> » replie celles qui dépassent le plafond de peu.\n";
echo "  Pour un paragraphe REPLIÉ TROP COURT, aucun outil : ses lignes se rejoignent à la main, le texte visant " . CEILING . " et non la largeur d'origine.\n";
exit(1);
