<?php
/**
 * USAGE
 *   php scripts/dev/trial-height-bands.php            feeds check-height-bands.php the subjects it must report and the ones it must ignore, and reports
 *   php scripts/dev/trial-height-bands.php -h|--help  this text
 *
 *   Writes one sample referential under var/tmp/ and reads nothing else. Exits non-zero as soon as one case answers the wrong way.
 *
 * INTENTION
 *   THE CASE THAT PRODUCED THE TOOL IS PINNED HERE WITH ITS REAL FIGURES, so it can never quietly stop being caught: TR-063 lost a row of cover on 2026-08-12
 *   and the band computed for the old cover stayed behind. Its canvas fell to 3,71 TY while the band still ran from 4,29 to 5,14 — the image kept coming back at
 *   the same height and kept being declared conforming, because the height check compares the image to the band and never the band to the subject.
 *
 *   THE EXTENT IS THE COVER, AND THAT HAS ITS OWN CASE, because reading the footprint instead is the one mistake that would look right on most subjects and be
 *   silently wrong on every tree: « TR-COVER » declares a band that FITS its footprint, so a checker reading the footprint stays quiet and only a checker reading
 *   the cover speaks. That is the fault TR-060 and TR-063 were wrongly accused of on 2026-08-10, in the other direction.
 *
 *   AND THE BOUNDARY IS INSIDE THE BAND. A flat piece declares 1,0 to 1,0 and its canvas is exactly 1,0 — every assembling piece of the park sits on that exact
 *   equality, so a comparison written strict would turn the whole network of paths and streams red at once.
 */

require_once dirname(__DIR__) . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$root = dirname(__DIR__, 2);
$directory = $root . '/var/tmp/trial-height-bands';
if (!is_dir($directory)) {
    mkdir($directory, 0777, true);
}

/**
 * The canvas figures below are the model's, not this file's: a canvas is its extent's rows plus its standing height foreshortened, so a subject 3 tiles tall on a
 * cover 2 rows deep comes to 3,71 TY. They are written as expectations, never as a computation — the model stays the only place that arithmetic exists.
 */
$sample = $directory . '/sample.json';
file_put_contents($sample, json_encode(['subjects' => [
    // The apple tree as it stands corrected: cover 3 × 2, height 3, canvas 3,71 TY, band 3,30 – 4,12. Contained.
    'TR-OK' => [
        'type' => 'tree',
        'footprint' => ['columns' => 1, 'rows' => 1],
        'cover' => ['columns' => 3, 'rows' => 2],
        'height' => 3,
        'variants' => [['ref' => 'principale', 'height_min_ty' => 3.3, 'height_max_ty' => 4.12]],
    ],
    // A flat assembling piece: no standing part at all, canvas exactly 1,0 TY, band 1,0 – 1,0. The boundary belongs to the band.
    'SOL-FLAT' => [
        'type' => 'ground',
        'footprint' => ['columns' => 1, 'rows' => 1],
        'height' => 0,
        'variants' => [['ref' => 'principale', 'height_min_ty' => 1.0, 'height_max_ty' => 1.0]],
    ],
    // THE DEFECT ITSELF: the same tree with the band computed for the cover it had BEFORE a row was removed. Canvas 3,71 against a floor of 4,29.
    'TR-STALE' => [
        'type' => 'tree',
        'footprint' => ['columns' => 1, 'rows' => 1],
        'cover' => ['columns' => 3, 'rows' => 2],
        'height' => 3,
        'variants' => [['ref' => 'principale', 'height_min_ty' => 4.29, 'height_max_ty' => 5.14]],
    ],
    // A band that fits the FOOTPRINT — 1 row instead of the cover's 2. Reading the footprint would call this right; reading the cover finds the canvas above the ceiling.
    'TR-COVER' => [
        'type' => 'tree',
        'footprint' => ['columns' => 1, 'rows' => 1],
        'cover' => ['columns' => 3, 'rows' => 2],
        'height' => 3,
        'variants' => [['ref' => 'principale', 'height_min_ty' => 2.29, 'height_max_ty' => 3.14]],
    ],
    // The other direction: a subject that grew tall under a band left low. Canvas 6,57 TY against a ceiling of 4,12.
    'TR-TALL' => [
        'type' => 'tree',
        'footprint' => ['columns' => 2, 'rows' => 2],
        'height' => 8,
        'variants' => [['ref' => 'principale', 'height_min_ty' => 3.3, 'height_max_ty' => 4.12]],
    ],
    // A variant carrying no band at all. Not a fault of this check — it is what the production command stops on — but it must be COUNTED, never silently skipped.
    'TR-NOBAND' => [
        'type' => 'tree',
        'footprint' => ['columns' => 1, 'rows' => 1],
        'height' => 3,
        'variants' => [['ref' => 'principale']],
    ],
]], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));

/** Runs the check in detail mode and gives back what it named, keyed by subject code. */
function finds(string $root, string $sample): array
{
    $command = sprintf('php %s %s -v', escapeshellarg($root . '/scripts/check-height-bands.php'), escapeshellarg($sample));
    exec($command, $output, $status);
    if ($status > 1) {
        throw new RuntimeException("le contrôle s'est arrêté sur une faute (code {$status}) : " . implode(' / ', $output));
    }
    $found = [];
    foreach ($output as $line) {
        if (preg_match('~^\s+(?:SANS FOURCHETTE\s+)?([A-Z]+-[A-Z]+|[A-Z]{2,3}-\d{3})\s*/~', $line, $match) === 1) {
            $found[$match[1]] = trim($line);
        }
    }

    return $found;
}

$found = finds($root, $sample);

$silent = ['TR-OK', 'SOL-FLAT'];
$reported = ['TR-STALE', 'TR-COVER', 'TR-TALL'];
// Counted rather than judged: it must appear, and it must appear as « sans fourchette », not as a band at fault.
$bandless = 'TR-NOBAND';

$failures = 0;
echo "Ce que le contrôle doit taire\n";
foreach ($silent as $code) {
    if (isset($found[$code])) {
        printf("  RATÉ  %s — aurait dû se taire, il signale « %s »\n", $code, $found[$code]);
        $failures++;
        continue;
    }
    printf("  OK    %s\n", $code);
}

echo "Ce que le contrôle doit signaler\n";
foreach ($reported as $code) {
    if (!isset($found[$code])) {
        printf("  RATÉ  %s — la fourchette ne contient plus la toile, il n'a rien dit\n", $code);
        $failures++;
        continue;
    }
    printf("  OK    %s — %s\n", $code, $found[$code]);
}

echo "Ce que le contrôle doit compter sans le juger\n";
if (!isset($found[$bandless]) || !str_contains($found[$bandless], 'SANS FOURCHETTE')) {
    printf("  RATÉ  %s — attendait « SANS FOURCHETTE », a rendu « %s »\n", $bandless, $found[$bandless] ?? 'rien');
    $failures++;
} else {
    printf("  OK    %s\n", $bandless);
}

echo "\n";
if ($failures === 0) {
    echo "Une fourchette qui a cessé de contenir la toile se signale, et celle qui la contient reste muette.\n";
    exit(0);
}
printf("%d cas répondent à l'envers.\n", $failures);
exit(1);
