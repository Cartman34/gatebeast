<?php
/**
 * USAGE
 *   php scripts/check-no-new-python.php             the verdict: how many Python files the repository carries that the roll does not allow
 *   php scripts/check-no-new-python.php -v          each new file, one per line
 *   php scripts/check-no-new-python.php --freeze    rewrites the roll from what is tracked today — ONLY on the operator's say-so, see below
 *   php scripts/check-no-new-python.php --dry-run   with --freeze, says what the roll would become and writes nothing
 *   php scripts/check-no-new-python.php -h|--help   this text
 *
 *   Exits 1 as soon as one Python file is new, 0 otherwise.
 *
 * INTENTION
 *   NO NEW PYTHON FILE, AND IT IS HELD BY A MACHINE RATHER THAN BY GOODWILL (opérateur, 2026-08-12). PHP is this repository's language for lasting tooling, and
 *   that was already written — but the rule as written let an agent justify an exception in its own file header, which is exactly what happened the day this was
 *   ordered: a check was written in Python and its intention explained why, properly, and it was still wrong. A justification documents a choice already
 *   granted; it does not grant a new one. Written down, the rule was argued with; held by a check, it is not.
 *
 *   WHAT IS FORBIDDEN IS ADDING, NEVER KEEPING. The Python already here stays and is not rewritten — « aucun remplacement brut n'est jamais prévu » (methode,
 *   execution.md): rewriting what works costs the corrections its round trips paid for, and buys nothing. So the roll is a list of what EXISTS, a file missing
 *   from it is refused, and a file that leaves it is not even mentioned. Python may shrink as much as it likes; it may not grow.
 *
 *   REFREEZING IS A GESTURE THE OPERATOR AUTHORISES, NOT A CONVENIENCE ONE GRANTS ONESELF. `--freeze` makes any new file legitimate in one command, so an agent
 *   that reaches for it to make its own addition pass has not respected the rule, it has erased it — and the erasure leaves no trace anyone would read. It is
 *   there for the day the operator decides the roll must change, and for no other day. That is why it is a named flag and not the default, and why the roll
 *   carries the date it was frozen: a roll refrozen without a decision behind it is a roll that guards nothing.
 *
 *   IT COUNTS WHAT IS TRACKED, NOT WHAT IS ON DISK. A file becomes part of the project when it is versioned; before that it is a draft in a working tree, and
 *   `local/` exists precisely so the agent can write and throw away. Refusing those would fire on what the repository explicitly allows.
 */

require_once __DIR__ . '/bootstrap.php';
require_once __DIR__ . '/PythonFreeze.php';

bootCommand($argv);

$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);
$dryRun = in_array('--dry-run', $argv, true);
$freeze = PythonFreeze::get();

if (in_array('--freeze', $argv, true)) {
    $present = $freeze->present();
    if ($dryRun) {
        printf("%d fichier(s) Python seraient figés dans %s — rien n'est écrit.\n", count($present), PythonFreeze::ROLL);
        exit(0);
    }
    $written = $freeze->freeze();
    printf("%d fichier(s) Python figés dans %s.\n", count($written), PythonFreeze::ROLL);
    exit(0);
}

$added = $freeze->added();
printf("%d fichier(s) Python versionné(s) : %d que le relevé n'autorise pas.\n", count($freeze->present()), count($added));

if (!$added) {
    exit(0);
}
if ($detail) {
    printf("\nFICHIERS PYTHON NEUFS — le langage de l'outillage est PHP\n");
    foreach ($added as $file) {
        printf("  %s\n", $file);
    }
} else {
    printf("« -v » les nomme.\n");
}
// UN REFUS NOMME LE GESTE QUI DÉBLOQUE (`S90 refus-avec-solution`), et celui-ci en a deux dont un seul appartient à l'agent — la distinction EST la solution.
printf("Solution — réécrire ce fichier en PHP : c'est le langage de l'outillage, et le Python décroît sans jamais croître.\n");
printf("  Le refiger au relevé — « php scripts/check-no-new-python.php --freeze » — est un geste que l'opérateur AUTORISE, jamais une commodité\n");
printf("  qu'on s'accorde pour faire passer son propre ajout : refigé sans décision derrière, le relevé ne garde plus rien.\n");
exit(1);
