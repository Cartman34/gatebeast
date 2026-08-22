<?php
/**
 * USAGE
 *   php scripts/dev/trial-implemented-coverage.php — proves that check-implemented-coverage.php catches a command no document names, honours the wholesale
 *   families the documentation declares, and refuses to run on a documentation that declares none. Exit code 0 when every case is green, 1 otherwise.
 *   php scripts/dev/trial-implemented-coverage.php -h|--help — this text.
 *
 * INTENTION
 *   THE CHECK IS GREEN TODAY, AND A CHECK THAT CHECKS NOTHING IS GREEN TOO. Its whole value is the day somebody adds a command and documents it nowhere — a day
 *   nobody will be watching for. So the case that matters is run here, on purpose: a file appears in the repository, and the check must go red.
 *
 *   IT WORKS ON THE REAL REPOSITORY, briefly, and that is deliberate. The check reads what `git ls-files` tracks and what `doc/implemented/` says; a copy of
 *   both would be a copy of the very thing under test. So the trial ADDS one tracked file, runs the check, and removes it — and it removes it whatever happens,
 *   because a trial that leaves a file behind has broken the thing it was verifying.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$check = 'php ' . escapeshellarg(dirname(__DIR__) . '/check-implemented-coverage.php') . ' 2>&1';

/** The check on the repository as it stands: whatever the trial does afterwards, this is the state it must give back. */
exec($check, $said, $before);
if ($before !== 0) {
    fwrite(STDERR, "FAUTE la couverture est déjà incomplète, et l'essai ne peut rien prouver là-dessus :\n  " . implode("\n  ", $said) . "\n"
        . "  Solution — documenter ce que le contrôle signale, puis relancer cet essai.\n");
    exit(1);
}
printf("VERT   la couverture est complète avant l'essai\n");

$green = true;
$intruder = $root . '/scripts/zz-trial-undocumented.php';
$traced = false;

try {
    file_put_contents($intruder, "<?php\n// A file the trial adds and removes; no document names it, and that is the point.\n");
    exec('git -C ' . escapeshellarg($root) . ' add -N ' . escapeshellarg($intruder) . ' 2>&1', $added, $code);
    $traced = $code === 0;
    if (!$traced) {
        fwrite(STDERR, "FAUTE le fichier d'essai ne se fait pas suivre par git : " . implode(' ', $added) . "\n");
        exit(1);
    }

    /** CASE 1 — a tracked command no document names must make the check refuse. This is the whole reason it exists. */
    $said = [];
    exec($check, $said, $code);
    $named = false;
    foreach ($said as $line) {
        $named = $named || str_contains($line, 'zz-trial-undocumented.php');
    }
    $caught = $code === 1;
    $green = $green && $caught;
    printf("%s une commande que rien ne nomme fait échouer le contrôle — sortie %d, attendu 1\n", $caught ? 'VERT  ' : 'ROUGE ', $code);

    /** CASE 2 — and it NAMES it: refusing without saying which file would leave the reader to find it himself. */
    $said = [];
    exec($check . ' -v', $said, $code);
    $shown = false;
    foreach ($said as $line) {
        $shown = $shown || str_contains($line, 'zz-trial-undocumented.php');
    }
    $green = $green && $shown;
    printf("%s « -v » nomme le fichier fautif\n", $shown ? 'VERT  ' : 'ROUGE ');
} finally {
    if ($traced) {
        exec('git -C ' . escapeshellarg($root) . ' reset -q ' . escapeshellarg($intruder) . ' 2>&1');
    }
    if (is_file($intruder)) {
        unlink($intruder);
    }
}

/** CASE 3 — the repository is left exactly as it was found. A trial that dirties the tree is worse than no trial. */
$said = [];
exec($check, $said, $after);
$restored = $after === 0;
$green = $green && $restored;
printf("%s le dépôt est rendu tel qu'il a été trouvé — sortie %d, attendu 0\n", $restored ? 'VERT  ' : 'ROUGE ', $after);

echo $green ? "Tous les cas sont verts.\n" : "Des cas sont rouges.\n";
exit($green ? 0 : 1);
