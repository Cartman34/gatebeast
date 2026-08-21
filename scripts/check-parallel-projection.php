<?php
/**
 * USAGE
 *   php scripts/check-parallel-projection.php <image.png>... — reports, for each image, whether its silhouette holds the parallel projection, and where it stops.
 *   php scripts/check-parallel-projection.php -h|--help — this text.
 *
 *   Exits 1 as soon as one image drifts, so it can gate a version before its corrections are carried back into the code.
 *
 *   THIS ONE MEASURES; `scripts/check-axonometry.py` JUDGES — said here so nobody merges them believing they are a duplicate (`Q26 doublon-projection`, settled
 *   on 2026-08-20 by measurement). This file returns a DRIFT IN FIGURES on any image whatever, which is what compares two versions of one sprite: 0.897 then
 *   0.100 says the correction worked. It reads the silhouette only, so it counts a gable's rake as drift — legitimately oblique, and its figures are inflated by
 *   it. The other returns a VERDICT — converging, parallel, or not enough structure — read on inner edges and straight segments, so it concludes where the
 *   outline says nothing: buildings and fences. Neither can do the other's work.
 *
 * INTENTION
 *   THIS IS THE DEFECT THE EYE ARGUES ABOUT AND A COLUMN OF FIGURES SETTLES. Under the socle's camera — orthographic, azimuth zero — every line running
 *   north-south projects VERTICAL, at ground level and at any height: a footprint edge, a wall foot, a roof eave. A silhouette boundary that drifts steadily as
 *   it descends is a vanishing point, which this projection forbids outright. Three sessions were spent looking at buildings and disagreeing about whether they
 *   leaned; this answers in one command, with a figure and the rows it was read on.
 *
 *   IT READS THE SILHOUETTE, NOT THE WALLS, and that is its limit rather than a flaw to fix later: above the eaves the boundary may be a roof rake, which slopes
 *   legitimately. So it says WHERE the boundary stops being vertical and BY HOW MUCH, and never names the part at fault — that reading belongs to whoever has
 *   the image in front of them. A drift on a long run low on the image is a wall and damning; the same drift on a short run at the top may be a gable.
 *
 *   The measuring itself lives in `review-server/lib/SpriteMeasures.php`, shared with the workshop page, which prints the same figures under each image.
 */

require_once __DIR__ . '/bootstrap.php';

$root = bootCommand($argv);
require_once $root . '/review-server/lib/SpriteMeasures.php';

$paths = array_slice($argv, 1);
if (!$paths) {
    fwrite(STDERR, "USAGE : php scripts/check-parallel-projection.php <image.png>...\n");
    exit(2);
}

$measures = SpriteMeasures::get();
$faults = 0;
foreach ($paths as $path) {
    $verdict = $measures->parallelism($path);
    if ($verdict['held']) {
        printf("%s — la projection parallèle TIENT : aucune arête de la silhouette ne dérive.\n", $path);
        continue;
    }
    $faults++;
    printf("%s — LA PROJECTION PARALLÈLE EST PERDUE, %d arête(s) dérivent :\n", $path, count($verdict['faults']));
    // ONLY THE FIRST FEW ARE PRINTED, AND THE REST IS COUNTED RATHER THAN DROPPED IN SILENCE: a building's silhouette holds dozens of short runs, and a page of
    // them buries the one long drift that matters. They are sorted by how much they carry, so the first line is always the worst.
    foreach (array_slice($verdict['faults'], 0, 4) as $run) {
        printf("  %-5s y %d → %d (%d rangées) : %+d px, soit %.3f px par pixel de descente — attendu 0\n",
            $run['side'] === 'west' ? 'ouest' : 'est', $run['from'], $run['to'], $run['span'], $run['end'] - $run['start'], $run['slope']);
    }
    if (count($verdict['faults']) > 4) {
        printf("  … et %d autre(s), plus courtes ou moins marquées.\n", count($verdict['faults']) - 4);
    }
}

echo $faults
    ? sprintf("%d image(s) sur %d perdent la projection parallèle.\n", $faults, count($paths))
    : sprintf("%d image(s) : la projection parallèle tient partout.\n", count($paths));
exit($faults ? 1 : 0);
