<?php
/**
 * USAGE
 *   php scripts/dev/trial-footprints-rectangular.php — proves that check-footprints-rectangular.php catches the shapes the chain cannot express, and accepts
 *   the ones it can. Exit code 0 when every case is green, 1 otherwise.
 *   php scripts/dev/trial-footprints-rectangular.php -h|--help — this text.
 *
 * INTENTION
 *   THIS CHECK EXISTS TO FIRE ONCE, YEARS FROM NOW, ON A SUBJECT NOBODY HAS DRAWN YET. Run today it prints « la chaîne dit vrai » — which is also what a check
 *   that checks nothing prints. It will not be re-read before the day it matters, and on that day it must not be the first time anyone finds out whether it
 *   works. So its broken cases are held here, on a referential of the trial's own, and they are the shapes an L-shaped building would actually produce.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$work = $root . '/local/tmp/trial-footprints';
if (!is_dir($work) && !mkdir($work, 0o777, true) && !is_dir($work)) {
    fwrite(STDERR, "FAULT le répertoire d'essai « $work » ne se crée pas.\n");
    exit(1);
}

/** The check run against a referential of our own, and the code it returned — never against the project's. */
function verdictOf(string $path, array $subjects): int
{
    file_put_contents($path, json_encode(['format' => 'gatebeast-subjects', 'version' => 1, 'subjects' => $subjects],
        JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");
    $command = 'php ' . escapeshellarg(dirname(__DIR__) . '/check-footprints-rectangular.php') . ' ' . escapeshellarg($path) . ' 2>&1';
    exec($command, $output, $code);

    return $code;
}

$cases = [
    ['name' => 'un rectangle plein', 'subjects' => ['BT-000' => ['footprint' => ['columns' => 16, 'rows' => 10]]], 'expected' => 0],
    ['name' => 'un carré d\'une case', 'subjects' => ['CH-000' => ['footprint' => ['columns' => 1, 'rows' => 1]]], 'expected' => 0],
    ['name' => 'un commentaire souligné est toléré',
        'subjects' => ['BT-000' => ['footprint' => ['columns' => 4, 'rows' => 4, '_comment' => 'pourquoi']]], 'expected' => 0],
    // LES TROIS FORMES QU'UN BÂTIMENT EN L PRODUIRAIT, et c'est pour elles que ce contrôle existe.
    ['name' => 'une emprise en liste de cases', 'subjects' => ['BT-000' => ['footprint' => ['tiles' => ['0,0', '0,1']]]], 'expected' => 1],
    ['name' => 'un rectangle englobant plus des cases retirées',
        'subjects' => ['BT-000' => ['footprint' => ['columns' => 16, 'rows' => 10, 'removed' => ['8,9']]]], 'expected' => 1],
    ['name' => 'une dimension décimale', 'subjects' => ['BT-000' => ['footprint' => ['columns' => 16.5, 'rows' => 10]]], 'expected' => 1],
    ['name' => 'une dimension nulle', 'subjects' => ['BT-000' => ['footprint' => ['columns' => 0, 'rows' => 10]]], 'expected' => 1],
    ['name' => 'aucune emprise du tout', 'subjects' => ['BT-000' => ['height' => 3]], 'expected' => 1],
];

$red = 0;
foreach ($cases as $rank => $case) {
    $given = verdictOf($work . '/subjects-' . $rank . '.json', $case['subjects']);
    $green = $given === $case['expected'];
    $red += $green ? 0 : 1;
    printf("%s — %s : attendu %d, obtenu %d\n", $green ? 'VERT ' : 'ROUGE', $case['name'], $case['expected'], $given);
}

if ($red > 0) {
    printf("\n%d cas sur %d sont rouges.\n", $red, count($cases));
    exit(1);
}

printf("\nLes %d cas sont verts.\n", count($cases));
