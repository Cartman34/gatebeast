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

/** True when a line looks like the middle of a hand-wrapped paragraph: prose that stops short and does not close a sentence. */
function continuesAParagraph(string $line): bool
{
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

    return (bool) preg_match('/[a-zA-ZÀ-ÿ0-9,;:]$/u', $trimmed) && !preg_match('/^\s*([-*+>#|]|\d+\.|```)/u', ltrim($trimmed));
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
        if (continuesAParagraph($line)) {
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
