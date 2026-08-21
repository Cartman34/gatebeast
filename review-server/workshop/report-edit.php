<?php
/**
 * USAGE
 *   php review-server/workshop/report-edit.php <SUJET> — lists the edits of every version, saying which may be carried back into the code and which may not.
 *   php review-server/workshop/report-edit.php <SUJET> <rang> <édit> <où> — marks one edit as carried back, naming WHERE. Refuses unless it is « tenue ».
 *   php review-server/workshop/report-edit.php -h|--help — this text.
 *
 * INTENTION
 *   ONLY WHAT HELD IS OWED TO THE CODE, and until now nothing enforced it (`S98 suivi-tests-consigne`). Each version carries a handful of corrections; some are
 *   proven by its image, some are not observable on that essai, and carrying them ALL back is how a correction that never worked enters the socle — where it
 *   will be recopied into every subject that follows.
 *
 *   THE STATE IS NOT ENOUGH BY ITSELF; THE DOOR IS. `set-edit-state.php` already refuses a verdict with no observation behind it, so a « tenue » means a measure
 *   was taken. What was missing is the second half: something that reads that state at the moment of the report and says no. A tracking nobody consults is a
 *   display, not a guarantee.
 *
 *   AND IT RECORDS WHERE THE CORRECTION WENT, which is what makes the trail worth keeping: a source block, a code file, a rule. Three weeks later, « reportée »
 *   without a destination is a claim nobody can check — the same fault as a verdict without its observation, one step further down the chain.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';
require_once $root . '/review-server/lib/Prompts.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$subject = $argv[1] ?? null;
if ($subject === null) {
    fwrite(STDERR, "USAGE : php review-server/workshop/report-edit.php <SUJET> [<rang> <édit> <où>]\n");
    exit(2);
}
$prompts = Prompts::get();
if (!is_dir($prompts->homeOf($subject))) {
    fwrite(STDERR, "FAULT le sujet « $subject » n'a pas de foyer sous " . Prompts::HOME . "/.\n"
        . "  Solution — vérifier le code du sujet ; « php review-server/build.php /workshop » liste ceux qui existent.\n");
    exit(1);
}

$rank = $argv[2] ?? null;
$wanted = $argv[3] ?? null;
$where = $argv[4] ?? null;

// LISTING IS THE DEFAULT MODE, deliberately: one asks what may be carried back BEFORE carrying anything, never the other way round.
if ($rank === null) {
    $reportable = 0;
    $blocked = 0;
    foreach ($prompts->ranksOf($subject) as $each) {
        $journal = $prompts->editsOf($subject, $each);
        if ($journal['edits'] === []) {
            continue;
        }
        printf("\nv%d\n", $each);
        foreach ($journal['edits'] as $edit) {
            $state = $edit['test'] ?? 'non testée';
            $done = $edit['reported'] ?? null;
            if ($done !== null) {
                printf("  DÉJÀ REPORTÉ  %s → %s\n", $edit['id'], $done);
                continue;
            }
            if ($state === 'tenue') {
                printf("  REPORTABLE    %s\n", $edit['id']);
                $reportable++;
                continue;
            }
            printf("  NON           %s — « %s »\n", $edit['id'], $state);
            $blocked++;
        }
    }
    printf("\n%d édit(s) reportable(s), %d qui ne le sont pas.\n", $reportable, $blocked);
    printf("  Un édit se reporte par « php review-server/workshop/report-edit.php %s <rang> <édit> <où> ».\n", $subject);
    exit(0);
}

if ($wanted === null || $where === null || trim($where) === '') {
    fwrite(STDERR, "FAULT reporter un édit demande de dire OÙ il a été porté.\n"
        . "  Solution — quatrième argument : le bloc de source, le fichier ou la règle qui le porte désormais.\n");
    exit(1);
}
$rank = (int) ltrim((string) $rank, 'vV');
$path = $prompts->file($subject, $rank, 'edits');
$journal = $prompts->editsOf($subject, $rank);
if ($journal['fault'] !== null) {
    fwrite(STDERR, "FAULT {$journal['fault']}\n");
    exit(1);
}

$found = null;
foreach ($journal['edits'] as $edit) {
    if (($edit['id'] ?? null) === $wanted) {
        $found = $edit;
    }
}
if ($found === null) {
    $known = array_map(static fn (array $edit): string => $edit['id'] ?? '?', $journal['edits']);
    fwrite(STDERR, "FAULT aucun édit ne se nomme « $wanted » dans la « v$rank ». Les siens : " . implode(', ', $known) . ".\n");
    exit(1);
}
$state = $found['test'] ?? 'non testée';
if ($state !== 'tenue') {
    fwrite(STDERR, "FAULT « $wanted » est « $state » : il ne se reporte pas dans le code.\n"
        . "  Seule une correction TENUE est due au code — reportée sans l'être, elle entre au socle et se recopie dans tout ce qui suit.\n"
        . "  Solution — l'éprouver sur une image, puis « php review-server/workshop/set-edit-state.php $subject $rank $wanted tenue \"<ce qui a été mesuré>\" ».\n");
    exit(1);
}

$raw = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
foreach ($raw['edits'] as $index => $edit) {
    if (($edit['id'] ?? null) === $wanted) {
        $raw['edits'][$index]['reported'] = trim($where);
    }
}
file_put_contents($path, json_encode($raw, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n");

printf("%s — « %s » est reporté dans « %s ».\n", basename($path), $wanted, trim($where));
