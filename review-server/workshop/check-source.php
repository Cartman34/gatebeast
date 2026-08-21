<?php
/**
 * USAGE
 *   php review-server/workshop/check-source.php — checks the workshop's source blocks: that each is well formed, and that no two of them speak of the same thing.
 *   php review-server/workshop/check-source.php -h|--help — this text.
 *
 *   Exits 1 on any fault, so it can gate an assembly.
 *
 * INTENTION
 *   CONSISTENCY IS HELD BY A MACHINE, NEVER BY THE VIGILANCE OF WHOEVER WRITES. The prompt contradicted itself four times running on the same thing — the
 *   projection stated as prose here, as two equalities there, as three units elsewhere — and every agent who passed filled what he believed missing by inventing
 *   a fourth wording. No re-reading catches that: each version is plausible on its own, and it is their coexistence that is wrong.
 *
 *   WHAT IS CHECKED, AND IT IS « un paramètre se dit une fois, à son niveau » MADE MECHANICAL: every source block declares the words it GOVERNS, and it alone
 *   may use them. Another block speaking of yaw, of a vanishing point or of 96 pixels is refused by name and by line — before an assembled prompt reaches the
 *   generator carrying two versions of one rule.
 *
 *   IT JUDGES THE CLAUSE, NOT THE EXPLANATION. A source block holds both: the prose that explains, addressed to us, and the « consigne » block that goes to the
 *   generator. Two blocks may explain the same thing without harm — it is what they PRESCRIBE that must never be said twice.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

const SOURCE = 'review-server/workshop/source';
const REQUIRED = ['bloc', 'groupe', 'titre', 'niveau', 'gouverne'];
/** The levels a section may declare — the same six the consigne already names, and no seventh is invented here. */
const LEVELS = ['common', 'type', 'variant', 'description', 'parameters', 'call'];

$directory = "$root/" . SOURCE;
$paths = glob("$directory/*.md") ?: [];
if ($paths === []) {
    fwrite(STDERR, "FAULT aucun bloc de source sous « " . SOURCE . " ».\n");
    exit(1);
}

$faults = [];
$blocks = [];
foreach ($paths as $path) {
    $name = basename($path);
    $text = file_get_contents($path);

    if (!preg_match('/<!--\s*\n(.*?)\n-->/s', $text, $found)) {
        $faults[] = "$name — pas d'en-tête. Solution — ouvrir le fichier par un commentaire HTML portant " . implode(', ', REQUIRED) . '.';
        continue;
    }
    $header = [];
    foreach (explode("\n", $found[1]) as $line) {
        if (preg_match('/^\s*(\w+)\s*:\s*(.+?)\s*$/', $line, $pair)) {
            $header[$pair[1]] = $pair[2];
        }
    }
    foreach (REQUIRED as $key) {
        if (!isset($header[$key])) {
            $faults[] = "$name — l'en-tête ne déclare pas « $key ».";
        }
    }
    if (isset($header['niveau']) && !in_array($header['niveau'], LEVELS, true)) {
        $faults[] = "$name — niveau « {$header['niveau']} » inconnu. Les niveaux sont : " . implode(', ', LEVELS) . '.';
    }
    // THE CLAUSE IS REQUIRED AND UNIQUE: a source block carrying none assembles nothing, and one carrying two leaves the choice to the assembler.
    $clauses = preg_match_all('/^```consigne\n(.*?)^```$/ms', $text, $all);
    if ($clauses !== 1) {
        $faults[] = "$name — $clauses bloc(s) « ```consigne », il en faut exactement un : c'est lui qui part au générateur.";
        continue;
    }
    $blocks[$name] = ['header' => $header, 'clause' => $all[1][0]];
}

// THE CROSS-CHECK IS THE HEART OF THIS CONTROL: every governed word is looked for in the CLAUSE of every other block.
//
// THE LIST IS SEPARATED BY SEMICOLONS, AND IT HAS TO BE: a governed value is often a number, and French writes its decimals with a comma. Separated by commas,
// « 5,25 » was cut into « 5 » and « 25 », which then matched any number in any other clause.
foreach ($blocks as $name => $block) {
    foreach (array_map('trim', explode(';', $block['header']['gouverne'] ?? '')) as $word) {
        if ($word === '') {
            continue;
        }
        foreach ($blocks as $other => $peer) {
            if ($other === $name) {
                continue;
            }
            // WORD BOUNDARIES keep « 84 » from matching « 840 ». CASE MATTERS FOR A WORD WRITTEN ALL IN CAPITALS, and it has to: the cardinal points are
            // written « EST », « OUEST », and searched case-blind they match the French verb « est » and the ordinary word « ouest » in any prose — the light
            // clause was once refused over five « est exposé au ciel ». A lowercase word, on the other hand, is searched in both cases.
            $sensitive = $word === mb_strtoupper($word) && preg_match('/\p{L}/u', $word);
            if (preg_match('/(?<![\w-])' . preg_quote($word, '/') . '(?![\w-])/u' . ($sensitive ? '' : 'i'), $peer['clause'])) {
                $faults[] = "$other — sa clause emploie « $word », que « $name » gouverne. Solution — retirer la mention, ou déplacer le mot d'un en-tête à l'autre.";
            }
        }
    }
}

// TWO BLOCKS CANNOT OCCUPY THE SAME PLACE in the assembled prompt: the second would overwrite the first with nothing to say so.
$places = [];
foreach ($blocks as $name => $block) {
    $place = ($block['header']['groupe'] ?? '?') . ' › ' . ($block['header']['titre'] ?? '?');
    if (isset($places[$place])) {
        $faults[] = "$name — occupe la même place que « {$places[$place]} » : « $place ».";
    }
    $places[$place] = $name;
}

if ($faults) {
    fwrite(STDERR, count($faults) . " faute(s) dans la source de l'atelier :\n  " . implode("\n  ", $faults) . "\n");
    exit(1);
}

printf("%d bloc(s) de source : en-têtes complets, une clause chacun, et aucun mot gouverné employé deux fois.\n", count($blocks));
