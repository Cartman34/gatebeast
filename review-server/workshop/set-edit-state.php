<?php
/**
 * USAGE
 *   php review-server/workshop/set-edit-state.php <SUJET> <rang> <édit> <état> [observation] — records whether one correction of a version held.
 *   The states are: tenue, « non tenue », « non observable sur cet essai », « non testée ». An observation is REQUIRED by the first three.
 *   php review-server/workshop/set-edit-state.php -h|--help — this text.
 *
 * INTENTION
 *   A TEST STATE IS NEVER WRITTEN BY THE AGENT WHO HOPES. « Tenue » is posted on a measure or on the operator's verdict, never on an impression from re-reading
 *   the text — an agent judging his own correction by looking at it finds it good every time. The journal was edited by hand, which made exactly that possible;
 *   this command is the door, and it REFUSES a verdict with nothing behind it.
 *
 *   ONLY « NON TESTÉE » NEEDS NO OBSERVATION, because it claims nothing. Every other state asserts something about the image or about a measure, and what was
 *   seen is written with it: three weeks later, a state without its observation is a verdict nobody can re-examine — and it is on those states that a correction
 *   is reported into the code.
 *
 *   IT WRITES UNDER `var/`, WHICH THE AGENT MAY NOT WRITE BY HAND — `scripts/hook-guard-scopes.sh` refuses Write and Edit there, and rightly: var/ takes what a
 *   PROGRAM writes while running. A verdict decided by hand and applied by a program is exactly the asymmetry that guard describes.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';
require_once $root . '/review-server/lib/Consignes.php';

Tools::get()->helpIfAsked($argv, __FILE__);

/** The states an edit can carry, and what each one claims. « non testée » is the only one that claims nothing. */
const STATES = [
    'tenue' => 'la correction a porté, et la mesure ou le verdict le dit',
    'non tenue' => 'la correction n\'a pas porté, et la mesure ou le verdict le dit',
    'non observable sur cet essai' => 'cet essai ne permet pas d\'en juger',
    'non testée' => 'rien ne l\'a encore éprouvée',
];

$subject = $argv[1] ?? null;
$rank = $argv[2] ?? null;
$wanted = $argv[3] ?? null;
$state = $argv[4] ?? null;
$observation = $argv[5] ?? null;
if ($subject === null || $rank === null || $wanted === null || $state === null) {
    fwrite(STDERR, "USAGE : php review-server/workshop/set-edit-state.php <SUJET> <rang> <édit> <état> [observation]\n");
    exit(2);
}
$rank = (int) ltrim((string) $rank, 'vV');
if (!isset(STATES[$state])) {
    fwrite(STDERR, "FAULT « $state » n'est pas un état connu. Les états sont : " . implode(', ', array_keys(STATES)) . ".\n");
    exit(1);
}
if ($state !== 'non testée' && ($observation === null || trim($observation) === '')) {
    fwrite(STDERR, "FAULT l'état « $state » affirme quelque chose sur l'image, et il exige donc son observation.\n"
        . "  Solution — donner en cinquième argument ce qui a été MESURÉ ou jugé, pas ce qu'on pense du texte.\n");
    exit(1);
}

$consignes = Consignes::get();
$path = $consignes->file($subject, $rank, 'edits');
if (!is_file($path)) {
    fwrite(STDERR, "FAULT la version « $subject v$rank » n'a pas de journal d'édits.\n");
    exit(1);
}
$journal = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
$touched = false;
foreach ($journal['edits'] as $index => $edit) {
    if (($edit['id'] ?? null) !== $wanted) {
        continue;
    }
    $journal['edits'][$index]['test'] = $state;
    if ($state === 'non testée') {
        unset($journal['edits'][$index]['observation']);
    } else {
        $journal['edits'][$index]['observation'] = trim($observation);
    }
    $touched = true;
}
if (!$touched) {
    $known = array_map(static fn (array $edit): string => $edit['id'] ?? '?', $journal['edits']);
    fwrite(STDERR, "FAULT aucun édit ne se nomme « $wanted » dans la « v$rank ». Les siens : " . implode(', ', $known) . ".\n");
    exit(1);
}
file_put_contents($path, json_encode($journal, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n");

printf("%s — « %s » est « %s ».\n", basename($path), $wanted, $state);
