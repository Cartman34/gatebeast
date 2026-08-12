<?php
/**
 * USAGE
 *   php scripts/dev/console-page.php <fichier html> — opens a built page in the browser and prints what its console says, errors first.
 *   php scripts/dev/console-page.php -h|--help — this text.
 *
 * INTENTION
 *   Three display failures in one evening were diagnosed by reading the source and all three diagnoses were wrong; each was found in seconds by looking. A dead
 *   button is the signature of a JavaScript error thrown before its listener was attached — and the browser names the file and the line. Reading the code cannot.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Probe.php';
require_once $root . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

// UNE ADRESSE EST ACCEPTÉE AUTANT QU'UN FICHIER, et c'est devenu nécessaire le 2026-08-08 : la page des sprites enregistre désormais ses verdicts sur le serveur,
// donc ouverte en fichier elle ne fait qu'une moitié de son travail. Ce qu'on veut regarder, c'est la page telle qu'elle est servie.
$page = $argv[1] ?? null;
if ($page === null) {
    throw new RuntimeException('FAULT usage : php scripts/dev/console-page.php <fichier html | adresse http>');
}
// CE QU'ON OUVRE EST TOUJOURS UNE COPIE SERVIE, JAMAIS L'ORIGINAL (point W21). Un fichier ouvert en `file://` sort nu — ni style, ni script —, donc sans la
// moitié qui produit justement les erreurs qu'on vient lire ; et la page servie, elle, ÉCRIT toute seule au chargement. Le service rend une copie muselée, de la
// même origine : tout se charge, rien ne part.
$lines = explode("\n", Browser::get()->console(Probe::get()->copyOf($page, 'sonde-console')));

$interesting = array_filter($lines, fn (string $l) => stripos($l, 'error') !== false || stripos($l, 'uncaught') !== false
    || stripos($l, 'CONSOLE') !== false || stripos($l, 'SyntaxError') !== false);
if (!$interesting) {
    echo "La console ne dit rien : aucune erreur au chargement.\n";
    exit(0);
}
foreach (array_slice($interesting, 0, 25) as $line) {
    echo $line . "\n";
}
