<?php
/**
 * USAGE
 *   php review-server/workshop/check-transmitted.php <SUJET> <rang> — every numeric constraint of the consigne has an equivalent in what the agent transmitted.
 *   php review-server/workshop/check-transmitted.php -h|--help — this text.
 *
 * INTENTION
 *   THE MEASURE ITSELF LIVES IN `review-server/lib/TransmittedNumbers.php`, WHICH SAYS WHY IT COUNTS NUMBERS AND NOT WORDS. This command is its terminal face;
 *   the workshop page is its other reader, and both must give the same verdict — written twice, the two would drift and the page would contradict the command.
 *
 *   IT RENDS 1 ON A LOSS, so it can be run in a session's checks and refuse out loud. A constraint that vanishes between our text and the agent's is invisible
 *   otherwise: the image simply comes back wrong, and one looks for the fault in the clause rather than in its journey.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';
require_once $root . '/review-server/lib/Consignes.php';
require_once $root . '/review-server/lib/TransmittedNumbers.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$subject = $argv[1] ?? null;
$rank = $argv[2] ?? null;
if ($subject === null || $rank === null) {
    fwrite(STDERR, "USAGE : php review-server/workshop/check-transmitted.php <SUJET> <rang>\n");
    exit(2);
}
$rank = (int) ltrim((string) $rank, 'vV');

$consignes = Consignes::get();
$promptPath = $consignes->file($subject, $rank, 'prompt');
$transmittedPath = $consignes->file($subject, $rank, 'transmitted');
if (!is_file($promptPath)) {
    fwrite(STDERR, "FAULT la version « $subject v$rank » n'a pas de consigne.\n");
    exit(1);
}
if (!is_file($transmittedPath)) {
    fwrite(STDERR, "FAULT la version « $subject v$rank » n'a pas de consigne transmise.\n"
        . "  Solution — php review-server/workshop/extract-transmitted.php $subject $rank, une fois la version générée.\n");
    exit(1);
}

$verdict = TransmittedNumbers::get()->compare(file_get_contents($promptPath), file_get_contents($transmittedPath));

printf("%s v%d — %d nombre(s) dans la consigne, %d dans ce qui a été transmis.\n", $subject, $rank, $verdict['wanted'], $verdict['given']);
if ($verdict['lost'] === []) {
    printf("Aucune contrainte chiffrée n'a été perdue à la transmission.\n");
    exit(0);
}
printf("\n%d CONTRAINTE(S) CHIFFRÉE(S) PERDUE(S) — le nombre n'apparaît nulle part dans ce que l'agent a envoyé :\n", count($verdict['lost']));
foreach ($verdict['lost'] as $number => $line) {
    printf("  « %s » — %s\n", $number, mb_strimwidth($line, 0, 150, '…'));
}
exit(1);
