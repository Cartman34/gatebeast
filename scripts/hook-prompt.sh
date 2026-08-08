#!/usr/bin/env bash
# Usage: declared as a UserPromptSubmit hook in .claude/settings.json. Reads the hook payload on stdin and arms or disarms the dépilement on the operator's word.
#
# Intention: the Stop hook must not hold every session opened in this repository — a throwaway test session got trapped on 2026-08-07, ordered to pick up a task
# nobody had given it. What holds the agent is the operator's GO, and nothing else: the repository rules already say GO and STOP are the only two words that start
# and stop the dépilement, and that any pause consumes the GO. This puts that rule where it cannot be forgotten.
#
# IT EXPIRES ON ITS OWN. A GO given this morning must not still hold tonight: the agent would be pushed back onto a pile the operator has since moved on from.
# The armed state carries the moment it was given, and the Stop hook ignores it once it is stale.

#
# IT LEAVES A TRACE ON EVERY SINGLE RUN, and that is not debugging left behind: without it, "the hook did not run" and "the hook ran and did not recognise the
# word" are indistinguishable — both leave nothing at all. On 2026-08-08 three GO given mid-turn armed nothing while the same GO opening a turn armed within the
# second, and the question could not be settled: nothing recorded whether the hook had even been called. The trace answers it, costs one line per prompt, and is
# the only thing that can tell a hook that is not wired from a hook that is wired and mistaken.
set -u
payload=$(cat)
trace_dir_default="$(dirname "$0")/../var/hooks"
# UNDER var/, NEVER UNDER local/: local belongs to the agent and the tooling writes nothing there — a file a script drops there has no owner any more. Every trace
# of an execution goes under var/, which is local but kept, and never versioned.
# THE STATE DIRECTORY CAN BE OVERRIDDEN, AND ONLY A TEST EVER DOES IT. Trying the hook on a few payloads used to ARM THE REAL DEQUEUE — a test writing production
# state, and one the agent is forbidden to undo, so it had to be reported to the operator to be cleared. A test says where it writes; production never sets this.
GATEBEAST_HOOK_DIR="${GATEBEAST_HOOK_DIR:-$trace_dir_default}"
mkdir -p "$GATEBEAST_HOOK_DIR"
state="$GATEBEAST_HOOK_DIR/dequeue-armed"
trace="$GATEBEAST_HOOK_DIR/prompt-log"

# The prompt as it was written. GO is not looked for inside a sentence: "we'll see later, go easy" is not an order to dequeue, and the repository rule is explicit
# — no sentence is read as a green light, only the word on its own counts.
# NO SILENT FALLBACK HERE ANY MORE. This line used to end in `2>/dev/null || true`: a payload it could not parse left `prompt` empty, the hook did nothing, and
# it said nothing — a GO could be lost without a single sign. What cannot be read is now reported and traced; the hook still exits 0, because refusing the
# operator's prompt over a hook fault would be worse, but it no longer pretends the prompt was empty.
if ! prompt=$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>&1); then
    printf '%s  CHARGE ILLISIBLE : %s\n' "$(date '+%F %T')" "$prompt" >> "$trace"
    echo "Le hook du prompt n'a pas pu lire sa charge — un GO ou un STOP passerait inaperçu. Trace : var/hooks/prompt-log" >&2
    exit 0
fi
word=$(printf '%s' "$prompt" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')
# The trace names what was seen, never the whole prompt: it is a log, not a copy of the conversation.
printf '%s  mot vu « %.20s » (%d caractères de prompt)\n' "$(date '+%F %T')" "$word" "${#prompt}" >> "$trace"

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
