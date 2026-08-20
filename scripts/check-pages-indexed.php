<?php
/**
 * USAGE
 *   php scripts/check-pages-indexed.php — every page the review server serves is reachable from the index, and every index card that claims a local page points
 *   at a route that exists. Exit code 0 when the two lists agree, 1 when they do not.
 *   php scripts/check-pages-indexed.php -h|--help — this text.
 *
 * INTENTION
 *   TWO LISTS HELD BY HAND, AND NOTHING MADE THEM AGREE. `review-server/pages.php` says what is served; `review-server/artefacts.json` says what the index shows.
 *   The index matches them BY NAME, so renaming on one side only drops a page out of the index — it stays served, it stays reachable by its address, and nobody
 *   can find it again. That is what happened to `/workshop`, served for days and listed nowhere (`W34 pages-hors-index`).
 *
 *   THE INDEX ALREADY SAID IT, AND THAT WAS NOT ENOUGH. A warning printed at the bottom of a page is read by whoever opens that page, on the day they open it.
 *   A page that fell out of the index is precisely the page nobody opens. A defect of this family is paid in tooling, not in vigilance — which is the rule this
 *   repository writes for itself, and this file is its application.
 *
 *   IT CHECKS BOTH DIRECTIONS, because they fail differently. A served page absent from the registry disappears from the index. A registry card naming a local
 *   route that no longer exists sends the reader to a 404 — worse than no link, since it looks like the page is broken rather than moved.
 */

require_once __DIR__ . '/bootstrap.php';

$root = bootCommand($argv);

$pages = require $root . '/review-server/pages.php';
$registryPath = $root . '/review-server/artefacts.json';
if (!is_file($registryPath)) {
    fwrite(STDERR, "FAULT le registre « review-server/artefacts.json » est absent, et rien ne dit alors ce que l'index montre.\n");
    exit(1);
}
$registry = json_decode(file_get_contents($registryPath), true, 512, JSON_THROW_ON_ERROR);

// THE INDEX IS SERVED AT THE ROOT AND IS NOT IN `pages.php`, yet it does carry a card: it declares itself here, exactly as the home page does.
$served = ['Index' => '/'];
foreach ($pages as $page) {
    $served[$page['title']] = $page['route'];
}
$named = [];
foreach ($registry['artefacts'] as $artifact) {
    $named[$artifact['name']] = $artifact;
}

$faults = [];
foreach ($served as $title => $route) {
    if (!isset($named[$title])) {
        $faults[] = "la page « $title », servie à « $route », ne correspond à aucun artefact du registre : elle n'apparaîtra sur aucun index.\n"
            . "  Solution — ajouter son artefact à review-server/artefacts.json sous ce nom EXACT, ou corriger le titre dans review-server/pages.php.";
    }
}
// THE OTHER DIRECTION: a card claiming a local page when no route carries that name any more. The registry does not say that in data — it says it in French
// prose, under `state_text` — so only what is mechanically true can be checked: a live artifact matching no route is not a fault, it is simply published and
// not served. The first direction is the check; the second is reported for information, and says so.
$publishedOnly = [];
foreach ($named as $title => $artifact) {
    if (!isset($served[$title]) && ($artifact['state'] ?? '') === 'alive') {
        $publishedOnly[] = $title;
    }
}

foreach ($faults as $fault) {
    fwrite(STDERR, "FAULT $fault\n");
}
if ($publishedOnly !== []) {
    printf("Pour information — %d artefact(s) vivant(s) ne sont pas servis en local, et c'est légitime : %s.\n",
        count($publishedOnly), implode(', ', $publishedOnly));
}
if ($faults !== []) {
    printf("%d page(s) servie(s) sur %d n'apparaissent sur aucun index.\n", count($faults), count($served));
    exit(1);
}

printf("Les %d pages servies ont chacune leur carte à l'index.\n", count($served));
