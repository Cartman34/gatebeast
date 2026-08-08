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

set -u
payload=$(cat)

# THE DEQUEUE RESTS ON THE OPERATOR'S "GO", NOT ON THE PRESENCE OF THIS REPOSITORY. Without that condition, every session opened here took the refusal — a throwaway
# test session got trapped on 2026-08-07, ordered to pick up a task nobody had given it. The prompt hook arms this state on the word alone, and disarms it on STOP.
#
# AND IT EXPIRES. A GO given in the morning must not still hold at night: the pile will have moved, the operator will have gone on to something else, and the agent
# would be pushed back onto stale work. Past that delay the state is erased and the end of turn is free again — a fresh GO is then needed, which the repository rule
# asks for anyway.
EXPIRY_SECONDS=$((3 * 3600))
# UNDER var/, NEVER UNDER local/: local belongs to the agent and the tooling writes nothing there.
state="$(dirname "$0")/../var/hooks/dequeue-armed"

if [ ! -f "$state" ]; then
    exit 0
fi

armed=$(cat "$state" 2>/dev/null || echo 0)
if [ $(( $(date +%s) - armed )) -gt "$EXPIRY_SECONDS" ]; then
    rm -f "$state"
    echo "Le dépilement a expiré : le GO date de plus de trois heures. Il en faut un neuf pour repartir." >&2
    exit 0
fi

# The guard's own guard: past this many consecutive refusals, the turn is let through. Without it, a task that genuinely cannot move would lock the agent in an
# endless loop, and the operator would be the one paying for it.
COUNTER="$(dirname "$0")/../var/hooks/refusals"
CEILING=5

transcript=$(printf '%s' "$payload" | grep -o '"transcript_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')

# THE APPLICATION SAYS ITSELF WHEN IT HAS ALREADY BEEN BLOCKED, and it must be listened to: it caps consecutive refusals and takes over past that. On the self-test,
# one refusal is enough to prove the mechanism bites — insisting would prove nothing more and would burn the ceiling for nothing.
already_blocked=$(printf '%s' "$payload" | grep -o '"stop_hook_active"[[:space:]]*:[[:space:]]*true' || true)

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
        echo "ÉPREUVE DU HOOK : le mot déclencheur a été trouvé dans ta réponse, donc le refus fonctionne. Écris maintenant une phrase le confirmant, SANS ce mot, et le tour pourra se terminer." >&2
        exit 2
    fi
fi

remaining=$(cd "$(dirname "$0")/.." && php scripts/backlog.php list 2>/dev/null | grep -c -E '^\S+ +\(\S+ *\) p[0-9]+ +(todo|in-progress)')

if [ "${remaining:-0}" -eq 0 ]; then
    rm -f "$COUNTER"
    exit 0
fi

refusals=$(cat "$COUNTER" 2>/dev/null || echo 0)
refusals=$((refusals + 1))
mkdir -p "$(dirname "$COUNTER")"
echo "$refusals" > "$COUNTER"

if [ "$refusals" -gt "$CEILING" ]; then
    rm -f "$COUNTER"
    echo "Le hook a refusé $CEILING fins de tour d'affilée et laisse passer celle-ci : $remaining tâche(s) restent à faire ou en cours, et rien n'avance." >&2
    exit 0
fi

first=$(cd "$(dirname "$0")/.." && php scripts/backlog.php next 2>/dev/null | head -1)
echo "TU NE T'ARRÊTES PAS : $remaining tâche(s) sont encore à faire ou en cours. Reprends la première sans rendre la main :" >&2
echo "  $first" >&2
echo "Une tâche qui ne peut pas avancer sans l'opérateur se passe en « blocked » avec sa raison écrite, elle ne se laisse pas en « todo »." >&2
exit 2
