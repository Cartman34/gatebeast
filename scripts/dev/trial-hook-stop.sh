#!/usr/bin/env bash
# Usage: bash scripts/dev/trial-hook-stop.sh — walks the end-of-turn hook through each of its decisions and checks it refuses, lets through, AND traces, every time.
#        bash scripts/dev/trial-hook-stop.sh -h|--help — this text
#
# Intention: THE SIX DECISIONS WERE INVISIBLE, AND ONE OF THEM COST A DAY. The hook lets the turn through after five consecutive refusals — a sound guard against
# a loop — but it announced that on standard error with exit 0, which shows the agent nothing: the guard simply went quiet, and neither the agent nor the operator
# could tell why. Every path now writes a line; this checks that it does, because a trace nobody verifies is a trace that stops being written.
#
# It writes its own state, never the real one: trying these by hand would arm or disarm the actual dequeue, which the agent is forbidden to touch.

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$(cd "$(dirname "$0")/../.." && pwd)/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

hook="$(dirname "$0")/../../scripts/hook-stop.php"
export GATEBEAST_HOOK_DIR="$(cd "$(dirname "$0")/../.." && pwd)/var/tmp/essai-hooks-stop"
rm -rf "$GATEBEAST_HOOK_DIR"
mkdir -p "$GATEBEAST_HOOK_DIR"
failures=0

run() {
    printf '{"transcript_path":"","stop_hook_active":false}' | php "$hook" 2>/dev/null
    printf '%s' "$?"
}

expect() {
    local what="$1" wanted="$2" got="$3"
    if [ "$got" != "$wanted" ]; then
        printf 'RATÉ — %s : code %s attendu, %s obtenu\n' "$what" "$wanted" "$got"
        failures=$((failures + 1))
    else
        printf 'OK — %s\n' "$what"
    fi
}

expect "sans armement, la fin de tour passe" 0 "$(run)"

date +%s > "$GATEBEAST_HOOK_DIR/dequeue-armed"
expect "armé et la pile pleine, la fin de tour est refusée" 2 "$(run)"

# LE PLAFOND EST LA DÉCISION QUI A COÛTÉ UNE JOURNÉE : au sixième refus consécutif, le hook laisse passer. C'est voulu, et ça doit se voir.
echo 5 > "$GATEBEAST_HOOK_DIR/refusals"
expect "au-delà du plafond de refus, la fin de tour passe" 0 "$(run)"

date +%s > "$GATEBEAST_HOOK_DIR/dequeue-armed"
echo 0 > "$GATEBEAST_HOOK_DIR/refusals"
echo "0" > "$GATEBEAST_HOOK_DIR/dequeue-armed"
expect "un GO vieux de plus de trois heures laisse passer" 0 "$(run)"

if [ -f "$GATEBEAST_HOOK_DIR/dequeue-armed" ]; then
    printf 'RATÉ — un armement expiré doit être effacé\n'
    failures=$((failures + 1))
else
    printf 'OK — un armement expiré est effacé\n'
fi

lines=$(grep -c '' "$GATEBEAST_HOOK_DIR/stop-log" 2>/dev/null || echo 0)
if [ "$lines" -lt 4 ]; then
    printf 'RATÉ — %s ligne(s) de trace pour quatre décisions : un chemin ne dit rien\n' "$lines"
    failures=$((failures + 1))
else
    printf 'OK — chaque décision a laissé sa trace (%s lignes)\n' "$lines"
fi

if [ "$failures" -gt 0 ]; then
    printf '\n%d essai(s) en échec.\n' "$failures"
    exit 1
fi
printf '\nLe hook de fin de tour refuse, laisse passer, expire — et le dit à chaque fois.\n'
