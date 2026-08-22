<?php
/**
 * USAGE
 *   php scripts/dev/trial-piece-widths.php — proves that check-piece-widths.php refuses a set whose pieces disagree, accepts a coherent one, and stays silent
 *   on what it cannot read. Exit code 0 when every case is green, 1 otherwise.
 *   php scripts/dev/trial-piece-widths.php -h|--help — this text.
 *
 * INTENTION
 *   THE CHECK ALREADY CRIED WRONGLY ONCE, AND THAT IS WHY THIS EXISTS. Its first version judged fences too, read a post's height as a band's width, and
 *   reported `OB-010` at 151 % of a tile — a defect that was not there. A check that cries wrongly is a check somebody switches off, so what has to be held is
 *   not only that it catches a real gap, but that it stays quiet on a coherent set and on the shapes it admits it cannot read.
 *
 *   THE BROKEN CASES ARE HELD HERE, on a referential of the trial's own. The day `CH-019` is redrawn the check will go green on the project — and that is
 *   exactly when a trial resting on the project's data would stop proving anything.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$work = $root . '/local/tmp/trial-piece-widths';
if (!is_dir($work) && !mkdir($work, 0o777, true) && !is_dir($work)) {
    fwrite(STDERR, "FAUTE le répertoire d'essai « $work » ne se crée pas.\n");
    exit(1);
}

/** One piece, as the referential shapes it: a variant carrying its shape and one sprite whose measures hold the two extents the check reads. */
function piece(string $shape, int $contact, int $height): array
{
    return ['shape' => $shape, 'representations' => [['path' => "cutout/ground/$shape.png",
        'measures' => ['contact_px' => ['width' => $contact], 'silhouette_px' => ['height' => $height]]]]];
}

/** The check run against a referential of our own, never the project's, and the code it returned with what it said. */
function verdictOf(string $path, array $subjects, array &$said): int
{
    file_put_contents($path, json_encode(['format' => 'gatebeast-subjects', 'version' => 1, 'subjects' => $subjects],
        JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");
    $said = [];
    exec('php ' . escapeshellarg(dirname(__DIR__) . '/check-piece-widths.php') . ' ' . escapeshellarg($path) . ' 2>&1', $said, $code);

    return $code;
}

// 64 px of 96 is two thirds across; 56 px of 84 is two thirds down. A set drawn at those two figures is coherent whatever the axis.
$cases = [
    ['name' => 'un jeu cohérent — toutes les pièces aux deux tiers',
        'subjects' => ['CH-000' => ['type' => 'path', 'variants' => [piece('ns', 64, 84), piece('n', 64, 84), piece('ew', 96, 56), piece('e', 96, 56)]]],
        'expected' => 0],
    ['name' => 'un jeu cohérent à une autre largeur — la moitié partout',
        'subjects' => ['CH-000' => ['type' => 'path', 'variants' => [piece('ns', 48, 84), piece('n', 48, 84), piece('ew', 96, 42)]]],
        'expected' => 0],
    ['name' => 'LE DÉFAUT DE CH-019 — l\'extrémité nord au quart, la ligne aux deux tiers',
        'subjects' => ['CH-000' => ['type' => 'path', 'variants' => [piece('ns', 64, 84), piece('n', 23, 84)]]],
        'expected' => 1],
    // CH-019'S REAL FIGURES: 61 px of 84 is 72.6 %, 40 px is 47.6 % — a spread of exactly 25 points, which the original ceiling let through.
    ['name' => 'deux extrémités opposées qui ne s\'accordent pas — les chiffres réels de CH-019',
        'subjects' => ['CH-000' => ['type' => 'path', 'variants' => [piece('e', 96, 61), piece('w', 96, 40)]]],
        'expected' => 1],
    ['name' => 'un écart sous le plafond ne fait pas refuser',
        'subjects' => ['CH-000' => ['type' => 'path', 'variants' => [piece('ns', 64, 84), piece('n', 58, 84)]]],
        'expected' => 0],
    ['name' => 'une clôture n\'est pas une bande, et n\'est pas jugée',
        'subjects' => ['OB-000' => ['type' => 'fence', 'variants' => [piece('ns', 64, 84), piece('e', 96, 127)]]],
        'expected' => 0],
    ['name' => 'une pièce seule n\'a rien avec quoi s\'accorder',
        'subjects' => ['CH-000' => ['type' => 'path', 'variants' => [piece('ns', 24, 84)]]],
        'expected' => 0],
    ['name' => 'un ruisseau est jugé comme un chemin',
        'subjects' => ['CH-000' => ['type' => 'stream', 'variants' => [piece('ns', 64, 84), piece('n', 14, 84)]]],
        'expected' => 1],
];

$green = true;
$said = [];
foreach ($cases as $case) {
    $code = verdictOf($work . '/subjects.json', $case['subjects'], $said);
    $ok = $code === $case['expected'];
    $green = $green && $ok;
    printf("%s %s — sortie %d, attendu %d\n", $ok ? 'VERT  ' : 'ROUGE ', $case['name'], $code, $case['expected']);
    if (!$ok) {
        fwrite(STDERR, '  ' . implode("\n  ", $said) . "\n");
    }
}

/** AND IT SAYS WHAT IT DOES NOT JUDGE: a corner left out in silence would read, from a green line, as a corner found correct. */
verdictOf($work . '/subjects.json', ['CH-000' => ['type' => 'path', 'variants' => [piece('ns', 64, 84), piece('nw', 11, 84)]]], $said);
$named = false;
foreach ($said as $line) {
    $named = $named || str_contains($line, 'coin(s) écarté(s)');
}
$green = $green && $named;
printf("%s le coin écarté est nommé dans la sortie\n", $named ? 'VERT  ' : 'ROUGE ');

array_map('unlink', glob($work . '/*') ?: []);
rmdir($work);
echo $green ? "Tous les cas sont verts.\n" : "Des cas sont rouges.\n";
exit($green ? 0 : 1);
