<?php
/**
 * USAGE
 *   php scripts/check-subjects-against-inventory.php
 *
 *   Reads every subject declared in `assets/subjects.json`, finds its line in `doc/conception/referentiels/visuel/inventaire/`, and reports every figure that differs:
 *   footprint, cover, height. Exits non-zero as soon as one differs, or as soon as a subject has no readable line. Read-only — it changes nothing.
 *
 *   php scripts/check-subjects-against-inventory.php -h|--help — this text
 *
 * INTENTION
 *   THE INVENTORY IS AUTHORITATIVE AND THE REFERENTIEL IS A COPY OF IT, so the two drift and nothing said so. Found on 2026-08-10: the oak TR-060 carried height 6
 *   against the inventory's 8, the fir TR-065 carried 6 against 4, and BOTH quoted the inventory as saying the wrong figure — a citation that names its source and
 *   misquotes it cannot be caught by re-reading the referentiel, because it looks checked. Worse, the apple tree TR-063 and the fir had lost their cover entirely,
 *   and the canvas is taken from the cover: a missing cover orders an image three times too narrow, and the height check then calls the drawing wrong. Two
 *   generations were nearly spent redrawing images that were right.
 *
 *   NOTHING HERE IS SKIPPED IN SILENCE. A subject whose line cannot be found, or whose line carries no readable figure, is reported as loudly as a mismatch: a
 *   control that quietly passes over what it could not read reports "all clear" on the very subjects it never looked at.
 */

$root = dirname(__DIR__);
require_once __DIR__ . '/bootstrap.php';

bootCommand($argv);

$inventoryDirectory = $root . '/doc/conception/referentiels/visuel/inventaire';

$subjects = json_decode(file_get_contents($root . '/assets/subjects.json'), true, 512, JSON_THROW_ON_ERROR)['subjects'];

// Every inventory line that opens with a code, indexed by that code. The inventory spells its figures in French prose, and this is the only place that reads it.
$lines = [];
foreach (glob($inventoryDirectory . '/*.md') as $file) {
    foreach (file($file, FILE_IGNORE_NEW_LINES) as $number => $line) {
        if (preg_match('/^- \*\*([A-Z]{2,3}-\d{3})\b/u', $line, $found)) {
            $lines[$found[1]] = ['text' => $line, 'source' => basename($file) . ':' . ($number + 1)];
        }
    }
}

/**
 * The head of an inventory line — where its figures live. Everything before it is the bold title, everything after is the italic description, and BOTH carry
 * numbers that are not the subject's own: the title's `**` opens with an asterisk, and the description says things like « hauteur d'épaule » or « 1 case » about
 * something else entirely. A first attempt cut the line at the first « *» and always landed on the title's own bold marker, so every figure came back unreadable —
 * a control that reads nothing and says so, rather than one that reads the wrong thing and passes.
 */
function head(string $text): string
{
    $withoutTitle = preg_replace('/^- \*\*[^*]+\*\*/u', '', $text);

    return preg_split('/\s\*/u', $withoutTitle)[0];
}

/** The two figures of a spread, as the inventory writes them: « 2 × 2 », « couvert 6 × 6 ». Returns null when the head carries none. */
function spread(string $text, ?string $after = null): ?array
{
    $text = head($text);
    if ($after !== null) {
        $position = mb_strpos($text, $after);
        if ($position === false) {
            return null;
        }
        $text = mb_substr($text, $position + mb_strlen($after));
    }
    if (!preg_match('/(\d+)\s*×\s*(\d+)/u', $text, $found)) {
        return null;
    }

    return ['columns' => (int) $found[1], 'rows' => (int) $found[2]];
}

/**
 * The height in tiles, the inventory writing its decimals with a comma: « hauteur 0,9 case », « hauteur 8 cases ». A HEIGHT CAN BE NEGATIVE — the stream digs its
 * bed instead of standing up, « hauteur -0,3 case » — and a pattern that refuses the sign reports the line as unreadable rather than as it is.
 */
function height(string $text): ?float
{
    if (!preg_match('/hauteur\s+(-?[\d]+(?:,\d+)?)\s+cases?/u', head($text), $found)) {
        return null;
    }

    return (float) str_replace(',', '.', $found[1]);
}

$faults = [];

foreach ($subjects as $code => $subject) {
    if (!isset($lines[$code])) {
        $faults[] = "{$code} : aucune ligne à l'inventaire — le sujet est au référentiel et nulle part dans la cible.";
        continue;
    }
    $text = $lines[$code]['text'];
    $source = $lines[$code]['source'];

    $declaredCover = spread($text, 'couvert');
    // The footprint is the FIRST spread of the line, and the cover comes after the word that names it. Reading the first match blindly would take « couvert 6 × 6 »
    // for the footprint on any line whose footprint is missing, and report the subject as consistent while comparing two different things.
    $withoutCover = preg_replace('/couvert\s*\d+\s*×\s*\d+/u', '', $text);
    $declaredFootprint = spread($withoutCover);
    $declaredHeight = height($text);

    $footprint = $subject['footprint'] ?? null;
    if ($declaredFootprint === null) {
        $faults[] = "{$code} : l'inventaire ne dit aucune emprise lisible ({$source}).";
    } elseif ($footprint === null) {
        $faults[] = "{$code} : le référentiel ne porte aucune emprise, l'inventaire en donne "
            . "{$declaredFootprint['columns']} × {$declaredFootprint['rows']} ({$source}).";
    } elseif ((int) $footprint['columns'] !== $declaredFootprint['columns'] || (int) $footprint['rows'] !== $declaredFootprint['rows']) {
        $faults[] = "{$code} : emprise {$footprint['columns']} × {$footprint['rows']} au référentiel, "
            . "{$declaredFootprint['columns']} × {$declaredFootprint['rows']} à l'inventaire ({$source}).";
    }

    $cover = $subject['cover'] ?? null;
    if ($declaredCover !== null && $cover === null) {
        $faults[] = "{$code} : l'inventaire déclare un couvert {$declaredCover['columns']} × {$declaredCover['rows']} que le référentiel ne porte pas — "
            . "la toile se prend sur le couvert, donc l'image commandée sera trop étroite ({$source}).";
    } elseif ($declaredCover !== null
        && ((int) $cover['columns'] !== $declaredCover['columns'] || (int) $cover['rows'] !== $declaredCover['rows'])) {
        $faults[] = "{$code} : couvert {$cover['columns']} × {$cover['rows']} au référentiel, "
            . "{$declaredCover['columns']} × {$declaredCover['rows']} à l'inventaire ({$source}).";
    } elseif ($declaredCover === null && $cover !== null) {
        $faults[] = "{$code} : le référentiel porte un couvert {$cover['columns']} × {$cover['rows']} dont l'inventaire ne dit rien ({$source}).";
    }

    // NO FLOOR IS CHECKED ON THE DECLARED HEIGHT, AND THAT WAS A MISTAKE MADE HERE ON 2026-08-10. The floor of one tile belongs to the IMAGE — a sprite fills its
    // tile — and applying it to the subject's declared height forced every ground, path and tuft of grass to rise half a tile above its own case, which is to say
    // it abolished flat subjects. The declared height is a game datum: what the thing measures in the world. What the image must measure is declared per variant.
    $subjectHeight = $subject['height'] ?? null;
    if ($declaredHeight === null) {
        $faults[] = "{$code} : l'inventaire ne dit aucune hauteur lisible ({$source}).";
    } elseif ($subjectHeight === null) {
        $faults[] = "{$code} : le référentiel ne porte aucune hauteur, l'inventaire en donne {$declaredHeight} case(s) ({$source}).";
    } elseif (abs((float) $subjectHeight - $declaredHeight) > 0.001) {
        $faults[] = "{$code} : hauteur {$subjectHeight} au référentiel, {$declaredHeight} à l'inventaire ({$source}).";
    }
}

if ($faults === []) {
    printf("%d sujet(s) contrôlés, aucun écart avec l'inventaire.\n", count($subjects));
    exit(0);
}

foreach ($faults as $fault) {
    echo '  ' . $fault . "\n";
}
printf("\n%d écart(s) entre le référentiel et l'inventaire, sur %d sujet(s) contrôlés.\n", count($faults), count($subjects));
// UN REFUS NOMME LE GESTE QUI DÉBLOQUE (`S90 refus-avec-solution`). Ici il y a un choix à faire, et le refus doit le dire : les deux côtés sont écrits à la
// main, donc aucun des deux n'a raison par construction — c'est la CIBLE qui tranche, et la cible est l'inventaire de la conception.
echo "  Solution — l'inventaire de « doc/conception/ » dit ce que le sujet EST : c'est lui qui fait foi, et le référentiel se corrige pour s'y conformer.\n";
echo "  Si c'est l'inventaire qui est faux, il se corrige d'abord, et sa correction est une décision de conception, pas un alignement de données.\n";
exit(1);
