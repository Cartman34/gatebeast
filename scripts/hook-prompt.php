<?php
/**
 * USAGE
 *   Declared as a UserPromptSubmit hook in .claude/settings.json. Reads the hook payload on standard input and arms or disarms the dépilement on the operator's
 *   word.
 *
 * INTENTION
 *   The Stop hook must not hold every session opened in this repository — a throwaway test session got trapped on 2026-08-07, ordered to pick up a task nobody
 *   had given it. What holds the agent is the operator's GO, and nothing else: the repository rules already say GO and STOP are the only two words that start and
 *   stop the dépilement, and that any pause consumes the GO. This puts that rule where it cannot be forgotten.
 *
 *   IT EXPIRES ON ITS OWN. A GO given this morning must not still hold tonight: the agent would be pushed back onto a pile the operator has since moved on from.
 *   The armed state carries the moment it was given, and the Stop hook ignores it once it is stale.
 *
 *   IT LEAVES A TRACE ON EVERY SINGLE RUN, and that is not debugging left behind: without it, « the hook did not run » and « the hook ran and did not recognise
 *   the word » are indistinguishable — both leave nothing at all. On 2026-08-08 three GO given mid-turn armed nothing while the same GO opening a turn armed
 *   within the second, and the question could not be settled: nothing recorded whether the hook had even been called.
 *
 *   IN PHP, AND NOT IN SHELL: the repository makes PHP the default language of durable tooling, and a hook runs on every single prompt. The shell version had to
 *   call python3 just to read its own JSON payload — three languages in one file for what json_decode does in one line (operator, 2026-08-09).
 */

require_once __DIR__ . '/hook-word.php';
require_once __DIR__ . '/hook-trace.php';

$payload = stream_get_contents(STDIN);
$trace = HookTrace::get();

// NO SILENT FALLBACK. An unreadable payload used to leave the prompt empty, so the hook did nothing and said nothing — a GO could be lost without a single sign.
// What cannot be read is reported and traced; the hook still exits 0, because refusing the operator's prompt over a hook fault would be worse.
$decoded = json_decode($payload, true);
if (!is_array($decoded)) {
    $trace->write('prompt-log', 'CHARGE ILLISIBLE : ' . json_last_error_msg());
    fwrite(STDERR, "Le hook du prompt n'a pas pu lire sa charge — un GO ou un STOP passerait inaperçu. Trace : var/hooks/prompt-log\n");
    exit(0);
}
$prompt = (string) ($decoded['prompt'] ?? '');

// The message as it arrived, whole, before anything is decided about it. And the payload itself beside it: reading the code told nobody where the operator's word
// was hiding — only the object the client actually sends did (operator, 2026-08-09 : « tu dois pouvoir analyser tout l'objet envoyé par ton client, quitte à log
// cet objet »).
$trace->record('prompt', $prompt);
$trace->write('payload-log', $payload);

$word = HookWord::get()->order($prompt);
// The trace names the order that was recognised and how long the prompt was, never the prompt itself: it is a log, not a copy of the conversation. It says
// « aucun » rather than nothing at all, so a prompt that carried no order stays distinguishable from a hook that did not run.
$trace->write('prompt-log', sprintf('ordre lu « %s » (%d caractères de prompt)', $word ?? 'aucun', mb_strlen($prompt)));

// THE PROBE ANSWERS AND CHANGES NOTHING. It says, on the record, that this hook ran and what it received — the only way to tell « the hook never fired » from
// « the hook fired and did not recognise the word », and the only way to do it without arming or disarming anything.
if (HookWord::get()->probes($prompt) > 0) {
    $trace->write('prompt-log', 'SONDE — le hook du prompt a reçu le mot, il ne change rien');
    fwrite(STDERR, "SONDE : ce hook a bien reçu ton message en ouverture de tour. L'armement du dépilement n'a pas bougé.\n");
    exit(0);
}

if ($word === 'GO') {
    $trace->arm();
    fwrite(STDERR, "Dépilement armé : tant qu'il reste une tâche à faire ou en cours, la fin de tour sera refusée. Un STOP le désarme, et il expire seul.\n");
    exit(0);
}

if ($word === 'STOP') {
    $trace->disarm();
    fwrite(STDERR, "Dépilement désarmé.\n");
    exit(0);
}

exit(0);
