<?php
/**
 * USAGE
 *   Declared as a Stop hook in .claude/settings.json. Reads the hook payload on standard input, and refuses the end of turn while work remains.
 *
 * INTENTION
 *   The agent must not stop while the backlog still holds a task to do or in progress. The rule is written in three places and the agent broke it four times in
 *   one evening — a rule that depends on the agent remembering it at the end of every turn does not hold. This does not depend on him: exit code 2 refuses the
 *   end of turn, and what this writes on standard error comes back to him as the reason to carry on.
 *
 *   TWO CONDITIONS, AND THE FIRST EXISTS ONLY TO PROVE THE SECOND WORKS. A sentinel word the agent writes on purpose lets the whole mechanism be tested in one
 *   turn, without waiting for the backlog to be in the right state. The real condition is the backlog itself.
 *
 *   BLOCKED TASKS LET THE TURN END, on purpose: they wait on the operator, and refusing to stop on them would trap the agent on work he cannot advance.
 *
 *   IT LEAVES A TRACE ON EVERY PATH, INCLUDING — ESPECIALLY — THE ONES THAT LET THE TURN THROUGH. This hook takes several different decisions and used to announce
 *   only two of them. The others exited 0 in silence, and an exit 0 says nothing to the agent: on 2026-08-08 it let a turn end after five consecutive refusals,
 *   the operator asked why, and nothing anywhere could answer. A guard that decides without saying so cannot be trusted, and cannot be debugged either.
 *
 *   IN PHP, AND NOT IN SHELL: the repository makes PHP the default language of durable tooling. The shell version called python3 to read its own payload and its
 *   transcript — three languages in one file for what json_decode does natively (operator, 2026-08-09).
 */

require_once __DIR__ . '/hook-word.php';
require_once __DIR__ . '/hook-trace.php';
require_once __DIR__ . '/hook-transcript.php';

/** A GO given in the morning must not still hold at night: the pile will have moved, and the agent would be pushed back onto stale work. */
const EXPIRY_SECONDS = 3 * 3600;
/** The guard's own guard: past this many consecutive refusals, the turn is let through, so a task that cannot move never locks the agent in a loop. */
const CEILING = 5;
/** The sentinel the agent writes when he wants to check that the hook still bites. Nobody writes it by accident. */
const SELF_TEST_WORD = 'EPREUVE-DU-HOOK';

/**
 * Says, on the way out, what the operator has judged since the agent last looked — and says nothing when there is nothing.
 *
 * THE AGENT IS TOLD, IT NO LONGER HAS TO THINK OF ASKING (operator, 2026-08-11: « toi tu n'es pas encore notifié apparemment, tu ne vois pas les modifs »). He
 * judges on the page while the agent works, and the data landed in the repository without anything pointing at it: on 2026-08-11 three images were judged and
 * the agent found out an hour later, opening the file for another reason — two of those verdicts overturned a written rule.
 *
 * IT ANNOUNCES, IT NEVER REFUSES. The end of a turn is already refused for one reason, and a second one would make this hook the thing that never lets go. A
 * notice on the way out is enough: what it writes comes back to the agent, which is all that was missing.
 */
function announceFreshVerdicts(): void
{
    $said = [];
    $status = 0;
    exec(sprintf('php %s new 2>&1', escapeshellarg(__DIR__ . '/remarks.php')), $said, $status);
    if ($status === 1 && $said) {
        fwrite(STDERR, implode("\n", $said) . "\n");
    }
}

$payload = stream_get_contents(STDIN);
$trace = HookTrace::get();
$decoded = json_decode($payload, true);
if (!is_array($decoded)) {
    $trace->write('stop-log', 'LAISSE PASSER — charge illisible, c\'est une faute');
    fwrite(STDERR, "Le hook de fin de tour n'a pas pu lire sa charge : la garde est inopérante. Trace : var/hooks/stop-log\n");
    exit(0);
}

$transcriptPath = (string) ($decoded['transcript_path'] ?? '');
$alreadyBlocked = ($decoded['stop_hook_active'] ?? false) === true;

// THE ORDERS COME FROM THE PROMPT, AND FROM NOWHERE ELSE (operator, 2026-08-09 : « tu ne devais pas utiliser le transcrit, ça n'a jamais été convenu, tu dois
// utiliser le prompt »). Reading the conversation to find a standing order was an idea of the agent's own, and it went wrong twice in one morning: a GO given
// hours before and long since spent re-armed the dequeue at every end of turn, and the reading itself kept missing the shapes the client actually writes. The
// prompt hook sees what the operator types when he types it, and that is the whole of it.
//
// WHAT IT COSTS, SAID PLAINLY: a STOP slipped in while the agent works reaches no hook at all. The agent obeys it — that is a rule of conduct — but the guard
// keeps refusing the end of turn until its ceiling. The word sent again at the start of a turn disarms immediately.

// NO SILENT FALLBACK ON THE STATE. This read used to end in « or zero », so an unreadable file counted as armed at epoch zero — instantly stale, state erased,
// guard gone, and not a word said. An unreadable state is a fault, and it is reported as one.
try {
    $armedAt = $trace->armedAt();
} catch (RuntimeException $fault) {
    $trace->write('stop-log', 'LAISSE PASSER — état d\'armement illisible, c\'est une faute');
    fwrite(STDERR, "Le hook de fin de tour n'a pas pu lire l'état d'armement : la garde est inopérante. Trace : var/hooks/stop-log\n");
    exit(0);
}

// THE DEQUEUE RESTS ON THE OPERATOR'S GO, NOT ON THE PRESENCE OF THIS REPOSITORY. Without that condition, every session opened here took the refusal — a throwaway
// test session got trapped on 2026-08-07, ordered to pick up a task nobody had given it.
if ($armedAt === null) {
    $trace->write('stop-log', 'LAISSE PASSER — le dépilement n\'est pas armé');
    exit(0);
}

if (time() - $armedAt > EXPIRY_SECONDS) {
    $trace->disarm();
    $trace->write('stop-log', 'LAISSE PASSER — le GO a expiré, plus de trois heures');
    fwrite(STDERR, "Le dépilement a expiré : le GO date de plus de trois heures. Il en faut un neuf pour repartir.\n");
    exit(0);
}

// A STOP SLIPPED IN WHILE THE AGENT WORKED IS READ HERE, AND NOWHERE ELSE COULD READ IT (operator, 2026-08-11, after having to repeat the word five times). Such a
// message never opens a turn, so the prompt hook — which fires on turn opening — never sees it; it goes into a queue, and the only trace of it is a
// `queue-operation` entry in the transcript. This guard runs at the end of every turn, receives `transcript_path`, and already reads that file: it is the only
// place where the word can be caught at the moment it matters, which is the very moment this guard is about to refuse.
//
// ONLY « STOP », NEVER « GO », AND THAT IS WHAT KEEPS THE 2026-08-09 REGRESSION CLOSED. Reading orders here was removed that day because a GO left over in the
// conversation re-armed a dequeue nobody had asked for. A word that can only ever RELEASE the guard cannot arm anything, so the stale GO is harmless — it is not
// read at all.
//
// AND THE READING IS BOUNDED TO THE CURRENT TURN, which is the other half of that same regression: see HookTranscript::queuedThisTurn.
if ($transcriptPath !== '' && is_file($transcriptPath)) {
    foreach (HookTranscript::get()->queuedThisTurn($transcriptPath) as $queued) {
        if (HookWord::get()->order($queued) === 'STOP') {
            $trace->disarm();
            $trace->write('stop-log', 'LAISSE PASSER — STOP glissé en cours de tour, lu dans le transcrit');
            fwrite(STDERR, "Le STOP envoyé pendant le tour a été lu dans le transcrit : le dépilement est désarmé.\n");
            exit(0);
        }
    }
}

// THE APPLICATION SAYS ITSELF WHEN IT HAS ALREADY BEEN BLOCKED, and it must be listened to. On the self-test, one refusal is enough to prove the mechanism bites —
// insisting would prove nothing more and would burn the ceiling for nothing.
if (!$alreadyBlocked && $transcriptPath !== '' && is_file($transcriptPath)
    && str_contains(HookTranscript::get()->lastAgentText($transcriptPath), SELF_TEST_WORD)) {
    $trace->write('stop-log', 'REFUSE — mot d\'épreuve trouvé dans la dernière réponse');
    fwrite(STDERR, "ÉPREUVE DU HOOK : le mot déclencheur a été trouvé dans ta réponse, donc le refus fonctionne. Écris maintenant une phrase le confirmant, SANS ce mot,"
        . " et le tour pourra se terminer.\n");
    exit(2);
}

// NO SILENT FALLBACK ON THE BACKLOG EITHER, AND THIS ONE WAS THE WORST. The listing used to be piped through a discard: a backlog that failed to read gave an
// empty count, the count read as zero, and the guard let every turn through — silently disabled by an unrelated fault, with nothing to say so.
$listing = [];
$status = 0;
exec(sprintf('php %s list 2>&1', escapeshellarg(__DIR__ . '/backlog.php')), $listing, $status);
if ($status !== 0) {
    $trace->write('stop-log', 'LAISSE PASSER — la pile est illisible, c\'est une faute');
    fwrite(STDERR, "Le hook de fin de tour n'a pas pu lire la pile : la garde est inopérante. Trace : var/hooks/stop-log\n");
    exit(0);
}
$remaining = 0;
foreach ($listing as $line) {
    if (preg_match('/^\S+ +\(\S+ *\) +p\d+ +(todo|in-progress)\b/', $line) === 1) {
        $remaining++;
    }
}

$counter = $trace->path('refusals');
if ($remaining === 0) {
    if (is_file($counter)) {
        unlink($counter);
    }
    $trace->write('stop-log', 'LAISSE PASSER — plus aucune tâche à faire ni en cours');
    announceFreshVerdicts();
    exit(0);
}

$refusals = is_file($counter) ? (int) trim((string) file_get_contents($counter)) : 0;
$refusals++;
file_put_contents($counter, (string) $refusals);

if ($refusals > CEILING) {
    unlink($counter);
    // THIS IS THE ONE THAT COST A DAY. The ceiling is right — a task that truly cannot move must not lock the agent in a loop — but it used to announce itself on
    // standard error with exit 0, and an exit 0 shows the agent nothing: the guard simply went quiet, and nobody could tell why.
    $trace->write('stop-log', sprintf('LAISSE PASSER — plafond de %d refus consécutifs atteint, %d tâche(s) restaient', CEILING, $remaining));
    fwrite(STDERR, sprintf("Le hook a refusé %d fins de tour d'affilée et laisse passer celle-ci : %d tâche(s) restent à faire ou en cours, et rien n'avance.\n", CEILING, $remaining));
    announceFreshVerdicts();
    exit(0);
}

$next = [];
exec(sprintf('php %s next 2>&1', escapeshellarg(__DIR__ . '/backlog.php')), $next);
$first = $next[0] ?? '(la pile ne rend aucune tâche prenable)';
$trace->write('stop-log', sprintf('REFUSE — refus n°%d sur %d, %d tâche(s) restantes, première : %s', $refusals, CEILING, $remaining, $first));
fwrite(STDERR, sprintf("TU NE T'ARRÊTES PAS : %d tâche(s) sont encore à faire ou en cours. Reprends la première sans rendre la main :\n", $remaining));
fwrite(STDERR, '  ' . $first . "\n");
fwrite(STDERR, "Une tâche qui ne peut pas avancer sans l'opérateur se passe en « blocked » avec sa raison écrite, elle ne se laisse pas en « todo ».\n");
// AND ON THIS PATH TOO, WHICH IS THE MOST TRODDEN ONE: a verdict given while the agent works must reach it whatever the hook decides about the turn.
announceFreshVerdicts();
exit(2);
