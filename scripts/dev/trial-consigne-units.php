<?php
/**
 * USAGE
 *   php scripts/dev/trial-consigne-units.php            feeds check-consigne-units.php the lines it must report and the ones it must ignore, and reports
 *   php scripts/dev/trial-consigne-units.php -h|--help  this text
 *
 *   Writes two sample files under var/tmp/ and reads nothing else. Exits non-zero as soon as one case answers the wrong way.
 *
 * INTENTION
 *   THE SILENT HALF IS THE ONE NOBODY CAN SEE, so it is pinned first. A checker that looks for the two letters « px » instead of the unit reports « pixelisé »
 *   and « PXL-002 », and a checker cried wolf is a checker switched off — that is how the dead-path check learnt the same lesson, nine of its first twenty finds
 *   being Python attributes read as shell scripts. The other direction is worse still and costs nothing to notice: a sheet converting to pixels behind the rule's
 *   back looks exactly like a sheet that obeys it.
 *
 *   THE SAME TWO HALVES FOR THE IMAGE RATIO, whose silent side is where its one real risk sits: « carré » describes a thing of the world as often as a drawing —
 *   a square slab, a tile of one square metre — and is deliberately not matched, which line 7 of the sheet pins so nobody adds it back without reading why. What
 *   IS matched is the comparison, which no sheet has a legitimate reason to make about its own subject.
 *
 *   THE REFERENTIAL IS TRIED SEPARATELY BECAUSE IT IS NOT READ THE SAME WAY. Its consigne lives in values, so two families of key must stay quiet whatever they
 *   carry: a « _comment », written for whoever edits the file, and « representations », which holds what came BACK from a generation — paths, verdicts and the
 *   operator's own words, none of it ever sent to the generator.
 */

require_once dirname(__DIR__) . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$root = dirname(__DIR__, 2);
$directory = $root . '/var/tmp/trial-consigne-units';
if (!is_dir($directory)) {
    mkdir($directory, 0777, true);
}

// One case per line, so a line number IS the case. Keep the two lists below in step with it.
$sheet = $directory . '/sample.md';
file_put_contents($sheet, implode("\n", [
    'CE QUI DOIT RESTER MUET',
    'La porte occupe deux cases de large et monte à deux cases de haut.',
    'Le rendu est pixelisé, sans dégradé ni bord adouci.',
    'La texture pixellisée reste nette au plus fort agrandissement.',
    'Le sujet porte le code PXL-002 dans le référentiel.',
    'Une case et demie de haut, un quart de case d expansion.',
    'Le seuil est une dalle carrée d un demi-mètre de côté, et la case du monde est un carré.',
    'Aucune plaque de mousse n est plus large qu une demi-case.',
    'CE QUI DOIT ÊTRE SIGNALÉ',
    'La porte fait 96 pixels de haut.',
    'Largeur : 96px, bord à bord.',
    'Le faîte se tient 48 PIXELS au-dessus du sol.',
    'Une marge de 12 px sur chaque flanc.',
    'La profondeur au sol vaut 84 Pixel.',
    'La porte est deux fois plus haute que large, nettement.',
    'Le sapin est trois fois plus haut que large.',
    'Le corps de logis est plus large que haut.',
    'La tour se voit plus haute que large depuis la route.',
    'La façade est deux fois plus large que haute.',
]) . "\n");

// The referential is read by key, not by line: what must stay quiet is quiet BECAUSE of where it sits, not because of what it says.
$referential = $directory . '/sample.json';
file_put_contents($referential, json_encode([
    'types' => [
        'fence' => [
            '_prompt_comment' => 'la clause vaut 96 pixels par case — un commentaire, jamais envoyé au générateur',
            'extra_prompt' => 'une clôture occupe toute la largeur de sa case',
        ],
        'tree' => ['extra_prompt' => 'le tronc fait 12 px de large'],
        'building' => [
            '_height_comment' => 'la porte est deux fois plus haute que large — un commentaire, jamais envoyé au générateur',
            'extra_prompt' => 'la porte est deux fois plus haute que large',
        ],
    ],
    'subjects' => [
        'TR-060' => [
            'variants' => [[
                'action' => 'le houppier déborde de 96 pixels au-dessus de son emprise',
                'shape' => 'nesw',
                'representations' => [['path' => 'assets/sprites/tr-060-96px.png', 'operator_comment' => 'trop haut de 20 px, et plus large que haut']],
            ]],
        ],
    ],
], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));

/** Runs the check in detail mode and gives back what it named, one find per entry. */
function finds(string $root, string $path): array
{
    $command = sprintf('php %s %s -v', escapeshellarg($root . '/scripts/check-consigne-units.php'), escapeshellarg($path));
    exec($command, $output, $status);
    if ($status > 1) {
        throw new RuntimeException("le contrôle s'est arrêté sur une faute (code {$status}) : " . implode(' / ', $output));
    }

    return array_values(array_filter(array_map('trim', $output), fn (string $line): bool => str_contains($line, '«')));
}

$sheetFinds = [];
foreach (finds($root, $sheet) as $line) {
    if (preg_match('/:(\d+) —/', $line, $match) === 1) {
        $sheetFinds[(int) $match[1]] = $line;
    }
}
$referentialFinds = [];
foreach (finds($root, $referential) as $line) {
    if (preg_match('~— (/\S*) —~', $line, $match) === 1) {
        $referentialFinds[$match[1]] = $line;
    }
}

$silentLines = [2, 3, 4, 5, 6, 7, 8];
$reportedLines = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19];
$silentKeys = ['/types/fence/extra_prompt', '/subjects/TR-060/variants/0/shape'];
$reportedKeys = ['/types/tree/extra_prompt', '/types/building/extra_prompt', '/subjects/TR-060/variants/0/action'];
// The two families that must stay quiet BY POSITION: nothing of them may appear among the finds, whatever key they would have taken.
$forbiddenKeyParts = ['_prompt_comment', '_height_comment', 'representations'];

$failures = 0;
echo "Ce que le contrôle doit taire — la fiche\n";
foreach ($silentLines as $line) {
    if (isset($sheetFinds[$line])) {
        printf("  RATÉ  ligne %d — aurait dû se taire, il signale « %s »\n", $line, $sheetFinds[$line]);
        $failures++;
        continue;
    }
    printf("  OK    ligne %d\n", $line);
}

echo "Ce que le contrôle doit signaler — la fiche\n";
foreach ($reportedLines as $line) {
    if (!isset($sheetFinds[$line])) {
        printf("  RATÉ  ligne %d — attendait une mention d'unité, il n'a rien dit\n", $line);
        $failures++;
        continue;
    }
    printf("  OK    ligne %d\n", $line);
}

echo "Ce que le contrôle doit taire — le référentiel\n";
foreach (array_merge($silentKeys, $forbiddenKeyParts) as $key) {
    $guilty = array_filter(array_keys($referentialFinds), fn (string $found): bool => str_contains($found, $key));
    if ($guilty) {
        printf("  RATÉ  %s — aurait dû se taire, il signale « %s »\n", $key, implode(', ', $guilty));
        $failures++;
        continue;
    }
    printf("  OK    %s\n", $key);
}

echo "Ce que le contrôle doit signaler — le référentiel\n";
foreach ($reportedKeys as $key) {
    if (!isset($referentialFinds[$key])) {
        printf("  RATÉ  %s — attendait une mention d'unité, il n'a rien dit\n", $key);
        $failures++;
        continue;
    }
    printf("  OK    %s\n", $key);
}

echo "\n";
if ($failures === 0) {
    echo "Le pixel et le rapport d'image se signalent hors du socle, et ce qui décrit le monde reste muet.\n";
    exit(0);
}
printf("%d cas répondent à l'envers.\n", $failures);
exit(1);
