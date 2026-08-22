<?php
/**
 * USAGE
 *   php scripts/check-piece-widths.php — every set of pieces meant to join tile to tile shares one band width. Exit code 0 while that holds, 1 otherwise.
 *   php scripts/check-piece-widths.php -v — each set with the share every one of its pieces measures.
 *   php scripts/check-piece-widths.php <referential.json> — the same, on that file: this is what its trial hands over.
 *   php scripts/check-piece-widths.php -h|--help — this text.
 *
 * INTENTION
 *   PIECES THAT JOIN MUST SHARE A WIDTH, AND NOTHING COMPARED THEM (`S102 largeur-des-chemins`). A path is delivered as a set — a north-south line, an
 *   east-west line, four ends, a crossing — and the map lays them side by side. Each one was judged ALONE, against its own sheet, so a set where the north end
 *   is a quarter of a tile and the line it continues is two thirds passed every check there was: each piece is fine, the set is broken, and the break shows as
 *   a step at every junction.
 *
 *   IT COMPARES PIECES TO EACH OTHER, NEVER TO A NUMBER. The two thirds a sheet asks for is one sheet's business and would have to be read from prose; what
 *   makes a set false is INTERNAL disagreement, and that is arithmetic. A set drawn at half a tile throughout is coherent and this check says nothing about it.
 *
 *   THE WIDTH IS READ ON THE AXIS THAT CARRIES THE BAND, and this is the whole subtlety. A piece running north to south is a band down the tile: its width is
 *   its contact across. A piece running east to west runs across: its width is its silhouette DOWN, its horizontal extent being the whole tile by construction.
 *   Reading both on one axis compares a width to a length — the first version of this measure did exactly that and found a defect that was not there.
 *
 *   IT REFUSES, WHERE THE FOOTPRINT CHECK ONLY SIGNALS. A footprint that is not a rectangle is an event nobody has caused yet; a set of pieces that disagree is
 *   a defect already delivered, and letting it through is how it got delivered.
 */

require_once __DIR__ . '/bootstrap.php';

$root = bootCommand($argv);
$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);
$given = null;
foreach (array_slice($argv, 1) as $argument) {
    if (!str_starts_with($argument, '-')) {
        $given = $argument;
    }
}

const TX = 96;
const TY = 84;
/**
 * THE TOLERANCE IS 15 POINTS OF A TILE between the widest and the narrowest piece — about fourteen pixels, wide enough that a hand-drawn edge does not cry.
 *
 * IT WAS 25 AND THAT WAS TOO LOOSE, found by the trial rather than by reasoning: `CH-019`'s east and west ends measure 72,6 % and 47,6 %, a step of exactly
 * 25 points at every junction between them. The set was caught anyway, by its north end at 24 % — so the ceiling hid its own weakness behind a coarser defect,
 * which is the kind of luck a check must never depend on.
 */
const SPREAD = 0.15;
/**
 * THE SHAPES THIS CHECK CAN READ, AND THEY ARE NOT ALL OF THEM. A band's width is only measurable on the axis it does NOT run along, so a shape is judged only
 * where that axis is unambiguous: pieces running north to south are read across the tile, pieces running east to west are read down it. The crossing belongs to
 * the first list — its measured contact is that of its north-south arm.
 *
 * CORNERS ARE LEFT OUT, AND SAID SO. A piece turning from north to west carries a band in two directions at once: neither axis measures its width, and the
 * number that comes out is the extent of a bend, not of a band. Judging them would report defects that are not there — and a check that cries wrongly is a
 * check somebody switches off.
 */
const DOWN_TILE = ['ns', 'n', 's', 'nesw'];
const ACROSS_TILE = ['ew', 'e', 'w'];
/**
 * Types delivered as a set of BANDS joining tile to tile. A fence joins too, and it is deliberately absent: its silhouette measures its posts, so the check read
 * 151 % of a tile height on `OB-010` and called it a defect. What makes a fence's set coherent is post height and rail spacing — another measure, another check.
 */
const JOINED = ['path', 'stream'];

$path = $given ?? $root . '/assets/subjects.json';
if (!is_file($path)) {
    fwrite(STDERR, "FAUTE le référentiel « $path » est absent. Solution — donner le chemin d'un référentiel existant, ou aucun pour celui du dépôt.\n");
    exit(1);
}
$referential = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);

$sets = [];
$unreadable = [];
$skipped = [];
foreach ($referential['subjects'] ?? [] as $code => $subject) {
    if (!in_array($subject['type'] ?? '', JOINED, true)) {
        continue;
    }
    foreach ($subject['variants'] ?? [] as $variant) {
        $shape = $variant['shape'] ?? null;
        $sprites = $variant['representations'] ?? [];
        // THE CURRENT VERSION IS THE FIRST, as the referential orders them: judging an old version would report a defect already corrected.
        $measures = $sprites === [] ? null : ($sprites[0]['measures'] ?? null);
        if ($shape === null || $measures === null) {
            continue;
        }
        if (!in_array($shape, DOWN_TILE, true) && !in_array($shape, ACROSS_TILE, true)) {
            $skipped[$code][] = $shape;
            continue;
        }
        $extent = in_array($shape, ACROSS_TILE, true)
            ? ($measures['silhouette_px']['height'] ?? null)
            : ($measures['contact_px']['width'] ?? null);
        if ($extent === null) {
            // A PIECE WHOSE MEASURE IS ABSENT IS NOT A PIECE THAT PASSES: it is one this check cannot judge, and it says so rather than quietly leaving it out.
            $unreadable[] = sprintf('%s %s — %s', $code, $shape, basename($sprites[0]['path'] ?? '?'));
            continue;
        }
        $sets[$code][$shape] = $extent / (in_array($shape, ACROSS_TILE, true) ? TY : TX);
    }
}

$broken = [];
foreach ($sets as $code => $pieces) {
    if (count($pieces) < 2) {
        continue;
    }
    $spread = max($pieces) - min($pieces);
    if ($spread > SPREAD) {
        $broken[$code] = $spread;
    }
    if ($detail) {
        printf("\n%s — écart %.0f points entre la plus large et la plus étroite\n", $code, 100 * $spread);
        arsort($pieces);
        foreach ($pieces as $shape => $share) {
            printf("  %-6s %5.1f %% de case\n", $shape, 100 * $share);
        }
    }
}

// WHAT IS NOT JUDGED IS NAMED. A check that silently narrows what it looks at reads, from its green line, as a check that looked at everything.
foreach ($skipped as $code => $shapes) {
    printf("%s — %d coin(s) écarté(s), une bande qui tourne n'a pas de largeur sur un seul axe : %s\n", $code, count($shapes), implode(', ', $shapes));
}

if ($unreadable !== []) {
    printf("\n%d pièce(s) ILLISIBLES, non jugées — leur mesure manque au référentiel :\n  %s\n", count($unreadable), implode("\n  ", $unreadable));
}

printf("\n%d jeu(x) de pièces lu(s) : %d dont les largeurs ne s'accordent pas.\n", count($sets), count($broken));
foreach ($broken as $code => $spread) {
    printf("  %s — %.0f points d'écart, plafond %.0f\n", $code, 100 * $spread, 100 * SPREAD);
}
if ($broken !== []) {
    echo "  Solution — reprendre les pièces qui s'écartent du reste du jeu, puis relancer ce contrôle : ce sont elles qui font la marche à chaque raccord.\n";
    if (!$detail) {
        echo "  « -v » donne la largeur de chaque pièce.\n";
    }
}

exit($broken === [] ? 0 : 1);
