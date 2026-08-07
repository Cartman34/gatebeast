<?php
/**
 * Usage: php review-server/build.php [route]   — rebuilds one served page, named by its route; with no route, rebuilds them all.
 *
 *   php review-server/build.php /maquette-campagne
 *   php review-server/build.php
 *
 * Intention: a page took three commands with long paths and an easily-forgotten empty argument, and rebuilding it meant reading the declaration to find them. The declaration already carries those
 * commands — this runs them. One page, one command, and no incantation to remember.
 *
 * IT RUNS WHAT THE DECLARATION SAYS, and nothing it invents: the commands stay written where they are read by everyone, including the home page that shows them. A builder that held its own copy of
 * them would drift from what the page announces the day one of them changes.
 */

require_once __DIR__ . '/bootstrap.php';
bootBuild();

$root = dirname(__DIR__);
$pages = require __DIR__ . '/pages.php';
$wanted = $argv[1] ?? null;

$chosen = [];
foreach ($pages as $page) {
    if ($wanted === null || $page['route'] === $wanted) {
        $chosen[] = $page;
    }
}
if (!$chosen) {
    $routes = [];
    foreach ($pages as $page) {
        $routes[] = $page['route'];
    }

    throw new RuntimeException("no page is served at route '{$wanted}' — served routes are: " . implode(', ', $routes));
}

foreach ($chosen as $page) {
    printf("== %s (%s)\n", $page['title'], $page['route']);
    foreach (explode("\n", $page['build']) as $command) {
        // Every command runs from the repository root, since that is what the paths in the declaration are written against.
        passthru('cd ' . escapeshellarg($root) . ' && ' . $command, $status);
        if ($status !== 0) {
            throw new RuntimeException("command '{$command}' failed ({$status}) — page '{$page['title']}' is not up to date");
        }
    }
}
