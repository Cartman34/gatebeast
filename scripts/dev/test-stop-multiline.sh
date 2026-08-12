#!/usr/bin/env bash
# Usage: bash scripts/dev/test-stop-multiline.sh — feeds both hooks a series of STOP and GO messages whose only difference is their line breaks, and reports for
# each one whether the dequeue ended up armed or disarmed. Takes no argument and writes only under var/tmp/, never on the real armed state.
#        bash scripts/dev/test-stop-multiline.sh -h|--help — this text
#
# Intention: the operator's lead on 2026-08-08 — « ça arrive en plusieurs lignes et t'as mal géré le multiligne » — had never been tried. The only test that existed
# fed a bare STOP on a single line, which proves the code runs on what it is handed, not that it recognises the word the way it actually reaches it. Both hooks
# collapse the message with `tr -d '[:space:]'` before comparing, so line breaks are exactly where they can be right or wrong, and it is the same code twice.
#
# It covers both hooks on purpose: they read the word from two different places — the prompt payload for one, the transcript for the other — and a lead that blames
# multiline handling has to be answered on each, or it stays half open.

set -u
root="$(cd "$(dirname "$0")/../.." && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$root/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

export GATEBEAST_HOOK_DIR="$root/var/tmp/test-stop-multiline"
state="$GATEBEAST_HOOK_DIR/dequeue-armed"
transcript="$GATEBEAST_HOOK_DIR/transcript.jsonl"
failures=0

# Puts the dequeue back to armed before each case. Every case must start from the same state, otherwise a case that changes nothing looks identical to one that
# disarms after a previous case already did.
arm() {
    rm -rf "$GATEBEAST_HOOK_DIR"
    mkdir -p "$GATEBEAST_HOOK_DIR"
    date +%s > "$state"
}

# Reports one case. $1 the hook name, $2 what the message looks like, $3 the expected outcome — "désarmé" or "armé" —, $4 what was observed.
report() {
    if [ "$3" = "$4" ]; then
        printf '  OK    %-8s %-42s %s\n' "$1" "$2" "$4"
    else
        printf '  RATÉ  %-8s %-42s attendu %s, obtenu %s\n' "$1" "$2" "$3" "$4"
        failures=$((failures + 1))
    fi
}

observed() {
    if [ -f "$state" ]; then printf 'armé'; else printf 'désarmé'; fi
}

# Leaves the dequeue disarmed before a case. The GO cases need it: started from an armed state, a GO that arms and a word the hook ignores both leave the file in
# place, and the case would pass without proving anything.
strip() {
    rm -rf "$GATEBEAST_HOOK_DIR"
    mkdir -p "$GATEBEAST_HOOK_DIR"
}

# The prompt hook receives the message as a JSON field, so the line breaks reach it escaped. python builds the payload rather than printf, which would have to
# escape them by hand — and getting that escaping wrong would test the test instead of the hook.
try_prompt() {
    arm
    python3 -c 'import json,sys; print(json.dumps({"prompt": sys.argv[1]}))' "$2" \
        | php "$root/scripts/hook-prompt.php" > /dev/null 2>&1
    report "prompt" "$1" "$3" "$(observed)"
}

# Same hook, started from a disarmed state — the only way a GO case says anything.
try_go() {
    strip
    python3 -c 'import json,sys; print(json.dumps({"prompt": sys.argv[1]}))' "$2" \
        | php "$root/scripts/hook-prompt.php" > /dev/null 2>&1
    report "prompt" "$1" "$3" "$(observed)"
}

# The stop hook reads the last thing the operator typed in the transcript, so the case has to be written as a transcript: a GO, the agent working, then the message
# under test. Same shape as a real turn where the operator speaks while the agent runs.
try_stop() {
    arm
    python3 - "$transcript" "$2" <<'PY'
import json, sys

path, said = sys.argv[1], sys.argv[2]
lines = [
    {"type": "user", "message": {"content": [{"type": "text", "text": "GO"}]}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "je travaille"}]}},
    {"type": "user", "message": {"content": [{"type": "text", "text": said}]}},
]
with open(path, "w", encoding="utf-8") as handle:
    for line in lines:
        handle.write(json.dumps(line) + "\n")
PY
    python3 -c 'import json,sys; print(json.dumps({"transcript_path": sys.argv[1], "stop_hook_active": False}))' "$transcript" \
        | php "$root/scripts/hook-stop.php" > /dev/null 2>&1
    report "stop" "$1" "$3" "$(observed)"
}

printf 'Le STOP tel qu il arrive, ligne par ligne\n'
try_prompt 'STOP seul'                  'STOP'                                  'désarmé'
try_stop   'STOP seul'                  'STOP'                                  'désarmé'
try_prompt 'STOP suivi d un saut'       'STOP
'                                                                               'désarmé'
try_stop   'STOP suivi d un saut'       'STOP
'                                                                               'désarmé'
try_prompt 'STOP précédé d un saut'     '
STOP'                                                                           'désarmé'
try_stop   'STOP précédé d un saut'     '
STOP'                                                                           'désarmé'
try_prompt 'STOP suivi d une ligne vide' 'STOP

'                                                                               'désarmé'
try_stop   'STOP suivi d une ligne vide' 'STOP

'                                                                               'désarmé'
try_prompt 'stop en minuscules'         'stop'                                  'désarmé'
try_stop   'stop en minuscules'         'stop'                                  'désarmé'

printf 'Le STOP qui ne doit rien désarmer\n'
try_prompt 'STOP au milieu d une phrase' 'attends, stop ça et regarde plutôt'   'armé'
try_stop   'STOP au milieu d une phrase' 'attends, stop ça et regarde plutôt'   'armé'

printf 'Le cas que la piste de l opérateur désigne : STOP puis la suite, en plusieurs lignes\n'
try_prompt 'STOP puis une consigne'     'STOP

Regarde plutôt ce que je viens de coller.'                                               'désarmé'
try_stop   'STOP puis une consigne'     'STOP

Regarde plutôt ce que je viens de coller.'                                               'désarmé'

# The case measured for real on 2026-08-09: the operator says STOP, the agent stops, the operator then says something else. Reading only the last message made the
# order evaporate — « J'ai dit STOP, ça aurait dû stop. » Only a GO lifts a STOP.
try_stop_then() {
    arm
    python3 - "$transcript" "$2" "$3" <<'PY'
import json, sys

path, order, after = sys.argv[1], sys.argv[2], sys.argv[3]
lines = [
    {"type": "user", "message": {"content": [{"type": "text", "text": "GO"}]}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "je travaille"}]}},
    {"type": "user", "message": {"content": [{"type": "text", "text": order}]}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "arrêté"}]}},
    {"type": "user", "message": {"content": [{"type": "text", "text": after}]}},
]
with open(path, "w", encoding="utf-8") as handle:
    for line in lines:
        handle.write(json.dumps(line) + "\n")
PY
    python3 -c 'import json,sys; print(json.dumps({"transcript_path": sys.argv[1], "stop_hook_active": False}))' "$transcript" \
        | php "$root/scripts/hook-stop.php" > /dev/null 2>&1
    report "stop" "$1" "$4" "$(observed)"
}

# A MESSAGE SENT WHILE THE AGENT WORKS IS IN THE TRANSCRIPT, AND ITS SHAPE IS THE WHOLE DIFFICULTY. The entry's top-level type is `attachment`; the text sits two
# LE PORTEUR RÉEL EST `queue-operation`, MESURÉ LE 2026-08-11, et ce script en fabriquait un autre — `attachment.queued_command` —, qui n'existe pas dans cette
# version du client. Un essai qui invente sa charge n'éprouve que lui-même : il a déclaré le mot introuvable pendant deux jours alors qu'il était dans le fichier.
# Chaque message en file y apparaît deux fois, `enqueue` puis `remove` ; les deux sont écrits ici pour que le compte à un seul ordre soit éprouvé aussi.
# levels down, under `attachment.prompt`, next to `attachment.type = queued_command`. A reader that only knew `user` entries found nothing and concluded the word
# had never arrived — a whole morning of 2026-08-09 spent on that. The shape below is copied from the real file, not imagined.
try_queued() {
    arm
    python3 - "$transcript" "$2" <<'PY'
import json, sys

path, said = sys.argv[1], sys.argv[2]
lines = [
    {"type": "user", "message": {"content": [{"type": "text", "text": "GO"}]}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "je travaille"}]}},
    {"type": "queue-operation", "operation": "enqueue", "content": said},
    {"type": "queue-operation", "operation": "remove", "content": said},
]
with open(path, "w", encoding="utf-8") as handle:
    for line in lines:
        handle.write(json.dumps(line) + "\n")
PY
    python3 -c 'import json,sys; print(json.dumps({"transcript_path": sys.argv[1], "stop_hook_active": False}))' "$transcript" \
        | php "$root/scripts/hook-stop.php" > /dev/null 2>&1
    report "stop" "$1" "$3" "$(observed)"
}

# A GO sent the same way must arm, or the operator's order to carry on vanishes — asked and measured on 2026-08-09.
try_queued_from_disarmed() {
    strip
    python3 - "$transcript" "$2" <<'PY'
import json, sys

path, said = sys.argv[1], sys.argv[2]
lines = [
    {"type": "user", "message": {"content": [{"type": "text", "text": "bonjour"}]}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "je travaille"}]}},
    {"type": "queue-operation", "operation": "enqueue", "content": said},
    {"type": "queue-operation", "operation": "remove", "content": said},
]
with open(path, "w", encoding="utf-8") as handle:
    for line in lines:
        handle.write(json.dumps(line) + "\n")
PY
    python3 -c 'import json,sys; print(json.dumps({"transcript_path": sys.argv[1], "stop_hook_active": False}))' "$transcript" \
        | php "$root/scripts/hook-stop.php" > /dev/null 2>&1
    report "stop" "$1" "$3" "$(observed)"
}

printf 'Le message glissé pendant que l agent travaille\n'
try_queued 'STOP en cours de travail'   'STOP'                        'désarmé'
try_queued 'phrase en cours de travail' 'regarde plutôt ce fichier'   'armé'
# A GO READ FROM THE TRANSCRIPT MUST NOT ARM, and this case guards a correction that was itself a mistake: the hook reads the whole conversation, so an old GO —
# spent long ago, as every rule of this repository says a GO is — would re-arm the dequeue at every end of turn. Only the prompt hook arms.
try_queued_from_disarmed 'GO en cours de travail'     'GO'                        'désarmé'
try_queued_from_disarmed 'phrase sans ordre'         'reprends le point suivant' 'désarmé'

printf 'Un ordre tient tant qu un autre ne le remplace pas\n'
try_stop_then 'STOP puis une remarque'     'STOP' 'tu ne réfléchis pas aux conséquences' 'désarmé'
try_stop_then 'STOP puis une question'     'STOP' 'et pourquoi tu as fait ça ?'          'désarmé'
try_stop_then 'STOP puis un GO'            'STOP' 'GO'                                   'armé'

printf 'Le GO, pour que la symétrie soit éprouvée elle aussi\n'
try_go 'GO seul'                        'GO'                                    'armé'
try_go 'GO suivi d un saut'             'GO
'                                                                               'armé'
try_go 'GO puis une consigne'           'GO

Commence par le premier point.'                                                 'armé'
try_go 'GO au milieu d une phrase'      'vas-y go pour la suite'                'désarmé'

rm -rf "$GATEBEAST_HOOK_DIR"
if [ "$failures" -ne 0 ]; then
    printf '%d cas RATÉS\n' "$failures"
    exit 1
fi
printf 'Tous les cas passent\n'
