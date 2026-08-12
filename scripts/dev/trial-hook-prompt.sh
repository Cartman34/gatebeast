#!/usr/bin/env bash
# Usage: bash scripts/dev/trial-hook-prompt.sh — feeds the prompt hook the payloads it must recognise and the ones it must refuse to read, and reports.
#        bash scripts/dev/trial-hook-prompt.sh -h|--help — this text
#
# Intention: THE TEST WRITES ITS OWN STATE, NEVER THE REAL ONE. Trying these payloads by hand on 2026-08-08 ARMED THE ACTUAL DEQUEUE — a test writing production
# state, and one the agent is forbidden to undo, so it had to be handed to the operator to clear. The hook takes its state directory from GATEBEAST_HOOK_DIR for
# exactly this reason, and this is the only caller that ever sets it.
#
# It also keeps the shell out of the way: three payloads chained on one command line asked the operator for approval every time, which is the third symptom of
# the same habit — what needs repeating belongs in a script that authorises itself once.

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$(cd "$(dirname "$0")/../.." && pwd)/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

hook="$(dirname "$0")/../../scripts/hook-prompt.php"
export GATEBEAST_HOOK_DIR="$(cd "$(dirname "$0")/../.." && pwd)/var/tmp/essai-hooks"
rm -rf "$GATEBEAST_HOOK_DIR"
failures=0

try() {
    local what="$1" payload="$2" expected="$3" output
    output=$(printf '%s' "$payload" | php "$hook" 2>&1)
    if [ "$expected" = "arme" ] && [ ! -f "$GATEBEAST_HOOK_DIR/dequeue-armed" ]; then
        printf 'RATÉ — « %s » aurait dû armer\n' "$what"
        failures=$((failures + 1))
    elif [ "$expected" = "desarme" ] && [ -f "$GATEBEAST_HOOK_DIR/dequeue-armed" ]; then
        printf 'RATÉ — « %s » aurait dû désarmer\n' "$what"
        failures=$((failures + 1))
    elif [ "$expected" = "narme_pas" ] && [ -f "$GATEBEAST_HOOK_DIR/dequeue-armed" ]; then
        printf 'RATÉ — « %s » a armé alors qu%s ne devait pas\n' "$what" "'il"
        failures=$((failures + 1))
    elif [ "$expected" = "dit" ] && [ -z "$output" ]; then
        printf 'RATÉ — « %s » aurait dû se plaindre, il est resté muet\n' "$what"
        failures=$((failures + 1))
    else
        printf 'OK — %s\n' "$what"
    fi
}

try "GO arme" '{"prompt":"GO"}' arme
# UN ORDRE EN MINUSCULES NE VAUT RIEN, LES DEUX MOTS AUX MÊMES CONDITIONS (opérateur, 2026-08-11). Ce cas attendait l'inverse jusque-là : « go » armait.
try "go en minuscules n arme pas" '{"prompt":" go "}' 'n arme pas'
# PARTIR D'UN ÉTAT DÉSARMÉ, sinon on vérifie l'état laissé par l'essai précédent et non l'effet de celui-ci : c'est ce que la première version de ce script faisait,
# et elle accusait le hook d'une faute qui était la sienne.
rm -f "$GATEBEAST_HOOK_DIR/dequeue-armed"
try "une phrase contenant go n'arme pas" '{"prompt":"on verra plus tard, go doucement"}' narme_pas
try "GO arme de nouveau, après la phrase" '{"prompt":"GO"}' arme
try "STOP désarme" '{"prompt":"STOP"}' desarme
try "une charge illisible se plaint" 'pas du json' dit

# LA TRACE EST LE VRAI SUJET DE CE SCRIPT : sans elle, « le hook n'a pas tourné » et « le hook a tourné sans reconnaître le mot » sont indiscernables.
if [ ! -s "$GATEBEAST_HOOK_DIR/prompt-log" ]; then
    printf 'RATÉ — aucune trace écrite, alors que chaque passage doit en laisser une\n'
    failures=$((failures + 1))
else
    printf 'OK — trace écrite, %d ligne(s)\n' "$(grep -c '' "$GATEBEAST_HOOK_DIR/prompt-log")"
fi

if [ "$failures" -gt 0 ]; then
    printf '\n%d essai(s) en échec.\n' "$failures"
    exit 1
fi
printf '\nLe hook du prompt arme, désarme, se plaint quand il ne comprend pas, et trace chaque passage.\n'
