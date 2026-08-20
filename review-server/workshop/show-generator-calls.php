<?php
/**
 * USAGE
 *   php review-server/workshop/show-generator-calls.php <SUJET> <rang> — what the generator agent actually RAN for that version, one call per line.
 *   php review-server/workshop/show-generator-calls.php --journal <journal.jsonl> — the same, on a journal named directly.
 *   php review-server/workshop/show-generator-calls.php -h|--help — this text.
 *
 * INTENTION
 *   WHAT THE AGENT SAYS IT DID AND WHAT IT RAN ARE TWO DIFFERENT THINGS, AND ONLY THE SECOND IS EVIDENCE. Three of the most expensive findings of August came
 *   from reading these calls and from nothing else: that it works in several PASSES and reported only the last; that it draws on a magenta background and cuts
 *   it out afterwards; and that it used to CROP on the material then STRETCH the result to our dimensions — which made the ink fill the canvas by construction,
 *   so no measure on the ink could see the deformation any more.
 *
 *   THE SAME READING CLOSED THAT QUESTION ON 2026-08-19: since the `v7` there is no post-processing at all — the image is copied out as the model produced it,
 *   with no Python call in between. A behaviour that changed under us, that nothing announced, and that no measure on the image could have revealed.
 *
 *   IT WAS A THROWAWAY UNDER `local/scripts/`, AND IT SHOULD NOT HAVE BEEN. A tool that carries the proof behind three decisions is not a draft; left there it
 *   is invisible to whoever reprises the work, and it is cited by points that outlive it.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';
require_once $root . '/review-server/lib/Consignes.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$journal = null;
if (($argv[1] ?? null) === '--journal') {
    $journal = $argv[2] ?? null;
    if ($journal === null || !is_file($journal)) {
        fwrite(STDERR, "FAULT le journal « " . ($journal ?? '') . " » n'existe pas.\n");
        exit(1);
    }
} else {
    $subject = $argv[1] ?? null;
    $rank = $argv[2] ?? null;
    if ($subject === null || $rank === null) {
        fwrite(STDERR, "USAGE : php review-server/workshop/show-generator-calls.php <SUJET> <rang>\n");
        exit(2);
    }
    $rank = ltrim((string) $rank, 'vV');
    // THE JOURNAL'S NAME CHANGED WITH THE CHAIN, and the old ones are still there: the known forms are tried rather than imposing one that would erase the past.
    foreach (["$subject.v$rank.image", "$subject.v$rank", $subject] as $stem) {
        $path = "$root/var/generations/sprites/$stem-generateur.jsonl";
        if (is_file($path)) {
            $journal = $path;
            break;
        }
    }
    if ($journal === null) {
        fwrite(STDERR, "FAULT aucun journal de générateur pour « $subject » v$rank sous var/generations/sprites/.\n"
            . "  Solution — vérifier que cette version a bien été générée.\n");
        exit(1);
    }
}

$calls = 0;
foreach (file($journal, FILE_IGNORE_NEW_LINES) as $line) {
    $event = json_decode($line, true);
    if (($event['item']['type'] ?? null) !== 'command_execution') {
        continue;
    }
    $calls++;
    printf("%s\n\n", substr($event['item']['command'] ?? '', 0, 900));
}

// NO CALL AT ALL IS A RESULT, and the most telling one: it says the agent post-processed nothing, so the image is the one its model returned.
printf("%s — %d commande(s) exécutée(s) par l'agent générateur.\n", basename($journal), $calls);
