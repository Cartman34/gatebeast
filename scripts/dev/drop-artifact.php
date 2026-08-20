<?php
/**
 * USAGE
 *   php scripts/dev/drop-artifact.php <registre.json> <sortie.json> <nom> — writes a copy of the registry with that one artifact removed.
 *   php scripts/dev/drop-artifact.php -h|--help — this text.
 *
 * INTENTION
 *   A TRIAL NEEDS A BROKEN CASE, AND IT MUST NOT BUILD IT BY HAND. `trial-pages-indexed.sh` proves that the index check catches a served page absent from the
 *   registry; to do that it needs a registry with one entry missing. Editing JSON inside a shell script means quoting French names full of apostrophes, which is
 *   how the trial itself broke on its first run.
 *
 *   IT REFUSES WHEN THE NAME IS ABSENT, because a trial that removes nothing would then declare the check sound while having tested nothing at all.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$source = $argv[1] ?? null;
$target = $argv[2] ?? null;
$name = $argv[3] ?? null;
if ($source === null || $target === null || $name === null) {
    fwrite(STDERR, "USAGE : php scripts/dev/drop-artifact.php <registre.json> <sortie.json> <nom>\n");
    exit(2);
}
if (!is_file($source)) {
    fwrite(STDERR, "FAULT le registre « $source » est absent.\n");
    exit(1);
}
$registry = json_decode(file_get_contents($source), true, 512, JSON_THROW_ON_ERROR);
$kept = [];
foreach ($registry['artefacts'] as $artifact) {
    if ($artifact['name'] !== $name) {
        $kept[] = $artifact;
    }
}
if (count($kept) === count($registry['artefacts'])) {
    fwrite(STDERR, "FAULT aucun artefact ne se nomme « $name » : cet essai ne prouverait rien.\n");
    exit(1);
}
$registry['artefacts'] = $kept;
file_put_contents($target, json_encode($registry, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n");

printf("%s — écrit sans l'artefact « %s », %d restants.\n", basename($target), $name, count($kept));
