#!/usr/bin/env bash
# Usage: declared as a Stop hook in .claude/settings.json. Reads the hook payload on stdin, and refuses the end of turn while work remains.
#
# Intention: the agent must not stop while the backlog still holds a task to do or in progress. The rule is written in three places and the agent broke it four
# times in one evening — a rule that depends on the agent remembering it at the end of every turn does not hold. This does not depend on him: exit code 2 refuses
# the end of turn, and what this writes on standard error comes back to him as the reason to carry on.
#
# TWO CONDITIONS, AND THE FIRST EXISTS ONLY TO PROVE THE SECOND WORKS. A sentinel word the agent writes on purpose lets the whole mechanism be tested in one turn,
# without waiting for the backlog to be in the right state. The real condition is the backlog itself.
#
# BLOCKED TASKS LET THE TURN END, on purpose: they wait on the operator, and refusing to stop on them would trap the agent on work he cannot advance.

#
# IT LEAVES A TRACE ON EVERY PATH, INCLUDING — ESPECIALLY — THE ONES THAT LET THE TURN THROUGH. This hook takes six different decisions and used to announce only
# two of them. The other four exited 0 in silence, and an exit 0 says nothing to the agent: on 2026-08-08 it let a turn end after five consecutive refusals, the
# operator asked why, and nothing anywhere could answer. A guard that decides without saying so cannot be trusted, and cannot be debugged either.
set -u
payload=$(cat)

GATEBEAST_HOOK_DIR="${GATEBEAST_HOOK_DIR:-$(dirname "$0")/../var/hooks}"
mkdir -p "$GATEBEAST_HOOK_DIR"
trace="$GATEBEAST_HOOK_DIR/stop-log"

# One line per decision, always, whatever the outcome. The word that follows the date is the decision itself, so the log reads as a column.
say() {
    printf '%s  %s\n' "$(date '+%F %T')" "$1" >> "$trace"
}

# THE DEQUEUE RESTS ON THE OPERATOR'S "GO", NOT ON THE PRESENCE OF THIS REPOSITORY. Without that condition, every session opened here took the refusal — a throwaway
# test session got trapped on 2026-08-07, ordered to pick up a task nobody had given it. The prompt hook arms this state on the word alone, and disarms it on STOP.
#
# AND IT EXPIRES. A GO given in the morning must not still hold at night: the pile will have moved, the operator will have gone on to something else, and the agent
# would be pushed back onto stale work. Past that delay the state is erased and the end of turn is free again — a fresh GO is then needed, which the repository rule
# asks for anyway.
EXPIRY_SECONDS=$((3 * 3600))
# UNDER var/, NEVER UNDER local/: local belongs to the agent and the tooling writes nothing there.
state="$GATEBEAST_HOOK_DIR/dequeue-armed"

if [ ! -f "$state" ]; then
    say "LAISSE PASSER — le dépilement n'est pas armé"
    exit 0
fi

# NO SILENT FALLBACK ON THE STATE. This read used to end in `|| echo 0`, so an unreadable file counted as armed at epoch zero — instantly stale, state erased, guard
# gone, and not a word said. An unreadable state is a fault, and it is reported as one.
if ! armed=$(cat "$state"); then
    say "LAISSE PASSER — état d'armement illisible, c'est une faute"
    echo "Le hook de fin de tour n'a pas pu lire l'état d'armement : la garde est inopérante. Trace : var/hooks/stop-log" >&2
    exit 0
fi
if [ $(( $(date +%s) - armed )) -gt "$EXPIRY_SECONDS" ]; then
    rm -f "$state"
    say "LAISSE PASSER — le GO a expiré, plus de trois heures"
    echo "Le dépilement a expiré : le GO date de plus de trois heures. Il en faut un neuf pour repartir." >&2
    exit 0
fi

# The guard's own guard: past this many consecutive refusals, the turn is let through. Without it, a task that genuinely cannot move would lock the agent in an
# endless loop, and the operator would be the one paying for it.
COUNTER="$GATEBEAST_HOOK_DIR/refusals"
CEILING=5

transcript=$(printf '%s' "$payload" | grep -o '"transcript_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')

# THE APPLICATION SAYS ITSELF WHEN IT HAS ALREADY BEEN BLOCKED, and it must be listened to: it caps consecutive refusals and takes over past that. On the self-test,
# one refusal is enough to prove the mechanism bites — insisting would prove nothing more and would burn the ceiling for nothing.
already_blocked=$(printf '%s' "$payload" | grep -o '"stop_hook_active"[[:space:]]*:[[:space:]]*true' || true)

# A STOP SENT WHILE THE AGENT WORKS DISARMS TOO, AND THAT IS THE WHOLE POINT OF READING THE TRANSCRIPT HERE. UserPromptSubmit only fires on a message that starts
# a turn: a message queued while the agent is running never reaches it, so the operator's STOP disarmed nothing and the guard kept refusing every end of turn —
# he had to say it again, at a moment when the agent happened to be idle. This hook, on the other hand, runs at the END of the turn, and by then the message IS in
# the transcript. So the last thing the operator said is read here, and STOP is honoured wherever it was sent.
if [ -n "$transcript" ] && [ -f "$transcript" ]; then
    dernier=$(python3 - "$transcript" <<'PY'
import json, sys

said = ""
with open(sys.argv[1], encoding="utf-8", errors="replace") as handle:
    for line in handle:
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("type") != "user":
            continue
        chunks = entry.get("message", {}).get("content", [])
        if isinstance(chunks, str):
            said = chunks
            continue
        # A tool result is also a "user" entry; only what the operator TYPED counts, which is the text blocks.
        text = [chunk.get("text", "") for chunk in chunks if isinstance(chunk, dict) and chunk.get("type") == "text"]
        if text:
            said = "\n".join(text)
print(said.strip())
PY
)
    mot=$(printf '%s' "$dernier" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')
    if [ "$mot" = "STOP" ]; then
        rm -f "$state"
        say "LAISSE PASSER — STOP lu dans le transcrit, le dépilement est désarmé"
        echo "Dépilement désarmé : ton STOP a été lu dans le transcrit, même envoyé pendant que je travaillais." >&2
        exit 0
    fi
fi

# LE MOT D'ÉPREUVE : l'agent l'écrit quand il veut vérifier que le hook mord. C'est la seule condition qu'il déclenche lui-même, et elle ne coûte rien à laisser
# en place — personne ne l'écrit par accident.
#
# ONLY THE AGENT'S LAST MESSAGE IS READ, AND THAT IS THE WHOLE POINT: reading the end of the file found the word in PREVIOUS turns, so the condition could never be
# satisfied again and the refusal replayed forever. Seen on the first self-test, 2026-08-07. A hook that questions a history instead of the current state never lets
# go.
if [ -n "$transcript" ] && [ -f "$transcript" ] && [ -z "$already_blocked" ]; then
    last=$(python3 - "$transcript" <<'PY'
import json, sys

text = ""
with open(sys.argv[1], encoding="utf-8", errors="replace") as handle:
    for line in handle:
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("type") != "assistant":
            continue
        chunks = entry.get("message", {}).get("content", [])
        if isinstance(chunks, str):
            text = chunks
            continue
        said = [chunk.get("text", "") for chunk in chunks if isinstance(chunk, dict) and chunk.get("type") == "text"]
        if said:
            text = "\n".join(said)
print(text)
PY
)
    if printf '%s' "$last" | grep -q 'EPREUVE-DU-HOOK'; then
        say "REFUSE — mot d'épreuve trouvé dans la dernière réponse"
        echo "ÉPREUVE DU HOOK : le mot déclencheur a été trouvé dans ta réponse, donc le refus fonctionne. Écris maintenant une phrase le confirmant, SANS ce mot, et le tour pourra se terminer." >&2
        exit 2
    fi
fi

# NO SILENT FALLBACK ON THE BACKLOG EITHER, AND THIS ONE WAS THE WORST. The listing used to be piped through `2>/dev/null`: a backlog that failed to read gave an
# empty count, the count read as zero, and the guard let every turn through — silently disabled by an unrelated fault, with nothing to say so.
if ! listing=$(cd "$(dirname "$0")/.." && php scripts/backlog.php list 2>&1); then
    say "LAISSE PASSER — la pile est illisible, c'est une faute"
    echo "Le hook de fin de tour n'a pas pu lire la pile : la garde est inopérante. Trace : var/hooks/stop-log" >&2
    exit 0
fi
remaining=$(printf '%s' "$listing" | grep -c -E '^\S+ +\(\S+ *\) p[0-9]+ +(todo|in-progress)')

if [ "${remaining:-0}" -eq 0 ]; then
    rm -f "$COUNTER"
    say "LAISSE PASSER — plus aucune tâche à faire ni en cours"
    exit 0
fi

refusals=$(cat "$COUNTER" 2>/dev/null || echo 0)
refusals=$((refusals + 1))
mkdir -p "$(dirname "$COUNTER")"
echo "$refusals" > "$COUNTER"

if [ "$refusals" -gt "$CEILING" ]; then
    rm -f "$COUNTER"
    # THIS IS THE ONE THAT COST A DAY. The ceiling is right — a task that truly cannot move must not lock the agent in a loop — but it used to announce itself on
    # standard error with exit 0, and an exit 0 shows the agent nothing: the guard simply went quiet, and neither the agent nor the operator could tell why.
    say "LAISSE PASSER — plafond de $CEILING refus consécutifs atteint, $remaining tâche(s) restaient"
    echo "Le hook a refusé $CEILING fins de tour d'affilée et laisse passer celle-ci : $remaining tâche(s) restent à faire ou en cours, et rien n'avance." >&2
    exit 0
fi

first=$(cd "$(dirname "$0")/.." && php scripts/backlog.php next 2>&1 | head -1)
say "REFUSE — refus n°$refusals sur $CEILING, $remaining tâche(s) restantes, première : $first"
echo "TU NE T'ARRÊTES PAS : $remaining tâche(s) sont encore à faire ou en cours. Reprends la première sans rendre la main :" >&2
echo "  $first" >&2
echo "Une tâche qui ne peut pas avancer sans l'opérateur se passe en « blocked » avec sa raison écrite, elle ne se laisse pas en « todo »." >&2
exit 2
