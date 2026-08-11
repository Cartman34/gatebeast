<?php
/**
 * USAGE
 *   php scripts/check-stop-order.php <transcript.jsonl>
 *
 *   Reads the LAST thing the operator said in that transcript — whether it opened a turn or was slipped in while the agent worked — and disarms the dequeue if,
 *   and only if, that last word is a STOP. Says what it found either way. Exits 0 when it disarmed, 1 when it did not.
 *
 * INTENTION
 *   THE AGENT MUST BE ABLE TO OBEY A STOP WITHOUT DECIDING ANYTHING (operator, 2026-08-11). The rule that forbids him to touch his own armament exists because an
 *   armament he can write is an order he gives himself. This command does not lift that rule — it keeps it. The agent cannot tell it to disarm: it goes and reads
 *   the transcript, and the transcript is the operator's word, not his. If the word is not there, nothing happens and it says so.
 *
 *   WHY IT IS NEEDED AT ALL, GIVEN THE STOP HOOK NOW READS THE SAME THING: the hook only runs when a turn ENDS. A turn can be long, and between the moment the
 *   operator writes STOP and the moment the hook fires, the state says the dequeue is armed while it no longer is in fact. This closes that window, and it lets
 *   the agent answer « the guard is disarmed » instead of « the guard has not seen it yet ».
 *
 *   ONLY THE LAST WORD COUNTS, AND ONLY IF IT IS STOP. A STOP followed by a GO is not a stop; a STOP from an earlier turn is spent. Reading the last one, and
 *   refusing to act on anything else, is what keeps this from becoming the 2026-08-09 regression where an old word re-armed the dequeue at every end of turn.
 */

require_once __DIR__ . '/hook-trace.php';
require_once __DIR__ . '/hook-transcript.php';
require_once __DIR__ . '/hook-word.php';

$path = $argv[1] ?? '';
if ($path === '' || !is_file($path)) {
    throw new RuntimeException("FAUTE usage : php scripts/check-stop-order.php <transcript.jsonl> — « {$path} » n'est pas un fichier.");
}

$transcript = HookTranscript::get();
// THE LAST MESSAGE, NOT THE LAST ORDER — and the difference is the whole safety of this command (operator, 2026-08-11 : « je croyais que ça regardait uniquement
// le dernier message »). Keeping the last ORDER found means walking the entire history and remembering a word from three hours ago: a STOP followed by ten
// sentences carrying no order would still disarm, which is the stale-word regression of 2026-08-09 coming back through another door. Only what the operator just
// said counts, and if it carries no order, nothing happens.
$said = array_merge($transcript->operatorMessages($path), $transcript->queuedThisTurn($path));
$lastMessage = $said === [] ? '' : (string) end($said);
$order = HookWord::get()->order($lastMessage);

// SEUL UN GO MAINTIENT L'ARMEMENT ; TOUT LE RESTE Y MET FIN, Y COMPRIS UN MESSAGE QUI NE PORTE AUCUN ORDRE (operator, 2026-08-11 : « si pas de GO et pas de STOP,
// c'est un STOP, ça n'a jamais été armé »). Ce n'est pas une règle neuve, c'est celle du dépôt : « tout arrêt met fin au GO — une question de l'opérateur, un
// ordre ponctuel, une interruption ». Une question posée à l'agent l'arrête, donc elle consomme l'autorisation, exactement comme un STOP explicite. Chercher un
// STOP et ne désarmer que sur lui laissait armée toute reprise consécutive à une simple remarque.
$trace = HookTrace::get();
if ($order === 'GO') {
    $trace->write('stop-log', 'CONTRÔLE À LA DEMANDE — le dernier message porte un GO, l\'armement est maintenu');
    fwrite(STDERR, "Le dernier message du transcrit porte un GO : le dépilement reste armé.\n");
    exit(1);
}

$reason = $order === 'STOP' ? 'un STOP' : 'aucun ordre, ce qui vaut arrêt';
$trace->disarm();
$trace->write('stop-log', "CONTRÔLE À LA DEMANDE — le dernier message porte {$reason}, dépilement désarmé");
echo "Le dernier message du transcrit porte {$reason} : le dépilement est désarmé.\n";
exit(0);
