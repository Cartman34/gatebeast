<?php
/**
 * USAGE
 *   php scripts/check-last-order.php <transcript.jsonl>
 *
 *   Reads the LAST thing the operator said in that transcript — whether it opened a turn or was slipped in while the agent worked — and puts the dequeue in the
 *   state that word calls for: a GO arms it, anything else disarms it. Says what it found either way, and exits 0 when it armed, 1 when it disarmed.
 *
 *   php scripts/check-last-order.php -h|--help — this text
 *
 * INTENTION
 *   THE AGENT MUST BE ABLE D'OBÉIR SANS RIEN DÉCIDER (operator, 2026-08-11, then 2026-08-12: « il faut rendre générique la commande que tu utilises pour vérifier
 *   qu'un stop a été donné pour qu'elle accepte aussi le go — ainsi tu seras capable de vérifier toi-même quand un go ou un stop a été donné et d'actualiser le
 *   statut de la queue »). The rule forbidding the agent to touch his own armament exists because an armament he can write is an order he gives himself. **This
 *   command does not lift that rule, it keeps it** : the agent cannot tell it what to do — it goes and reads the transcript, and the transcript is the operator's
 *   word, not his. It arms on a GO for the same reason it disarms on anything else: because that is what the operator's last word says.
 *
 *   WHY IT IS NEEDED AT ALL, GIVEN THE HOOKS READ THE SAME THING: a hook only fires when a turn OPENS or ENDS. A word slipped mid-turn is read by nobody until
 *   then, and the state says « armed » while it no longer is — or the reverse. This closes that window in both directions.
 *
 *   ONLY THE LAST WORD COUNTS. A STOP followed by a GO is not a stop; a GO from an earlier turn is spent. Reading the last one, and nothing else, is what keeps
 *   this from becoming the 2026-08-09 regression where an old word re-armed the dequeue at every end of turn.
 */

require_once __DIR__ . '/Tools.php';
require_once __DIR__ . '/hook-trace.php';
require_once __DIR__ . '/hook-transcript.php';
require_once __DIR__ . '/hook-word.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$path = $argv[1] ?? '';
if ($path === '' || !is_file($path)) {
    throw new RuntimeException("FAUTE usage : php scripts/check-last-order.php <transcript.jsonl> — « {$path} » n'est pas un fichier.");
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
// UN GO ARME, ET C'EST LA MOITIÉ QUI MANQUAIT (opérateur, 2026-08-12). La commande ne faisait que désarmer : un GO glissé en cours de tour était donc obéi par
// l'agent mais invisible à la garde, qui continuait de dire « pas armé » jusqu'au tour suivant. Elle arme désormais sur le mot de l'opérateur, exactement comme
// elle désarme sur le sien — dans les deux cas c'est le transcrit qui décide, jamais l'agent.
if ($order === 'GO') {
    $already = $trace->armedAt() !== null;
    $trace->arm();
    $trace->write('stop-log', 'CONTRÔLE À LA DEMANDE — le dernier message porte un GO, dépilement armé');
    printf("Le dernier message du transcrit porte un GO : le dépilement est armé%s.\n", $already ? ' (il l\'était déjà)' : '');
    exit(0);
}

$reason = $order === 'STOP' ? 'un STOP' : 'aucun ordre, ce qui vaut arrêt';
$trace->disarm();
$trace->write('stop-log', "CONTRÔLE À LA DEMANDE — le dernier message porte {$reason}, dépilement désarmé");
echo "Le dernier message du transcrit porte {$reason} : le dépilement est désarmé.\n";
// LA SORTIE DIT L'ÉTAT, PAS LE SUCCÈS : 0 quand le dépilement est armé, 1 quand il ne l'est pas. Une commande qui rendrait toujours 0 obligerait à lire son texte
// pour savoir ce qu'elle a fait, et rien ne pourrait s'enchaîner dessus.
exit(1);
