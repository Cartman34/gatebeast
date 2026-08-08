<?php
/**
 * USAGE
 *   php scripts/check-text-width.php <file>...
 *
 *   Reports every line that breaks the project's single width standard, on any file given: a line over the ceiling, and a run of text lines folded far below it. Prints a verdict and nothing else when
 *   the files are clean; exits 1 as soon as one line is at fault, so it can gate a commit or a hand-off. Run it on whatever was just written, before showing it to anyone.
 *
 * INTENTION
 *   The ceiling is 200 characters and it is the project's ONLY length standard (AGENTS.md). Agents break it in one direction far more often than the other: they fold their text to eighty or a hundred
 *   characters, because that is the habit they arrive with and because the file they are editing is already folded that way. Both reasons are forbidden — a rule that is written outranks anything the
 *   surrounding file happens to do — and neither is fixed by asking an agent to be careful: the habit returns the moment attention lapses. So the rule gets a machine that enforces it.
 *
 *   A FOLDED RUN is what catches that habit, and it cannot be caught line by line: one short line proves nothing (a title, a list item, a closing sentence). What proves folding is a RUN of
 *   consecutive text lines that all stop well short of the ceiling while the paragraph clearly continues — the line does not end a sentence, and the next one carries it on. Below FOLD_RUN such a run
 *   is ordinary prose; at or above it, the text was wrapped by hand to a width nobody chose.
 *
 *   In PHP because it is the project's default language for durable tooling, and this needs no library that only Python has.
 */

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
    // width (AGENTS.md), and it gives itself away by punctuation prose does not use: an assignment, a call, a bracket, a sigil. Without this, every short
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
    foreach ($lines as $index => $line) {
        $number = $index + 1;
        $width = mb_strlen($line);
        // Two kinds of line CANNOT be folded, and reporting them is pure noise — the only answer would be a shorter text, an editorial choice, never a wrap:
        // a Markdown table row, whose row ends at the line break, and an inventory entry, which the tooling reads whole by its « - **CODE » opening. Exempt
        // from the ceiling, and from it alone.
        $unbreakable = (bool) preg_match('/^\s*\||^- \*\*[A-Z]{2,3}-\d{3} /u', $line);
        if ($width > CEILING && !$unbreakable) {
            echo "{$path}:{$number} : {$width} caractères, plafond " . CEILING . "\n";
            $faults++;
        }
        if (continuesAParagraph($line, $path)) {
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

echo $faults ? "{$faults} écart(s) au standard de largeur.\n" : count($paths) . " fichier(s) au standard.\n";
exit($faults ? 1 : 0);
