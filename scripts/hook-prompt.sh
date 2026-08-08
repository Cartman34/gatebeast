#!/usr/bin/env bash
# Usage: declared as a UserPromptSubmit hook in .claude/settings.json. Reads the hook payload on stdin and arms or disarms the dépilement on the operator's word.
#
# Intention: the Stop hook must not hold every session opened in this repository — a throwaway test session got trapped on 2026-08-07, ordered to pick up a task
# nobody had given it. What holds the agent is the operator's GO, and nothing else: the repository rules already say GO and STOP are the only two words that start
# and stop the dépilement, and that any pause consumes the GO. This puts that rule where it cannot be forgotten.
#
# IT EXPIRES ON ITS OWN. A GO given this morning must not still hold tonight: the agent would be pushed back onto a pile the operator has since moved on from.
# The armed state carries the moment it was given, and the Stop hook ignores it once it is stale.

set -u
payload=$(cat)
# UNDER var/, NEVER UNDER local/: local belongs to the agent and the tooling writes nothing there — a file a script drops there has no owner any more. Every trace
# of an execution goes under var/, which is local but kept, and never versioned.
state="$(dirname "$0")/../var/hooks/dequeue-armed"

# The prompt as it was written. GO is not looked for inside a sentence: "we'll see later, go easy" is not an order to dequeue, and the repository rule is explicit
# — no sentence is read as a green light, only the word on its own counts.
prompt=$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null || true)
word=$(printf '%s' "$prompt" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')

if [ "$word" = "GO" ]; then
    mkdir -p "$(dirname "$state")"
    date +%s > "$state"
    echo "Dépilement armé : tant qu'il reste une tâche à faire ou en cours, la fin de tour sera refusée. Un STOP le désarme, et il expire seul." >&2
    exit 0
fi

if [ "$word" = "STOP" ]; then
    rm -f "$state"
    echo "Dépilement désarmé." >&2
    exit 0
fi

exit 0
