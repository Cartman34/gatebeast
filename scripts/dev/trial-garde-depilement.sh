#!/usr/bin/env bash
# Usage: bash scripts/dev/trial-garde-depilement.sh — feeds the dequeue guard the payloads it exists to refuse, plus the ones it must let through, and reports.
#        bash scripts/dev/trial-garde-depilement.sh -h|--help — this text
#
# Intention: a guard is only worth what it refuses, and this one was written straight after the agent removed the armed state by itself. Declaring it in the
# settings proves nothing — the settings are read at session start, so the guard cannot be exercised in the session that writes it. Feeding it the payloads
# directly says today whether it bites, instead of finding out tomorrow that a regex never matched.

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$(cd "$(dirname "$0")/../.." && pwd)/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

guard="$(dirname "$0")/../../scripts/hook-guard-dequeue.sh"
failures=0

try() {
    local expected="$1" what="$2" payload="$3" output status
    output=$(printf '%s' "$payload" | bash "$guard" 2>&1)
    status=$?
    if [ "$expected" = "refuse" ] && [ "$status" -ne 2 ]; then
        printf 'RATÉ — « %s » aurait dû être refusé, sortie %d\n' "$what" "$status"
        failures=$((failures + 1))
    elif [ "$expected" = "laisse" ] && [ "$status" -ne 0 ]; then
        printf 'RATÉ — « %s » aurait dû passer, sortie %d : %s\n' "$what" "$status" "$output"
        failures=$((failures + 1))
    else
        printf 'OK — %s\n' "$what"
    fi
}

try refuse "supprimer l'armement" \
    '{"tool_name":"Bash","tool_input":{"command":"rm -f var/hooks/dequeue-armed"}}'
try refuse "l'armer à la main" \
    '{"tool_name":"Bash","tool_input":{"command":"date +%s > var/hooks/dequeue-armed"}}'
try refuse "le déplacer" \
    '{"tool_name":"Bash","tool_input":{"command":"mv var/hooks/dequeue-armed /tmp/ailleurs"}}'
try refuse "vider le répertoire" \
    '{"tool_name":"Bash","tool_input":{"command":"rm -rf var/hooks/"}}'
try refuse "réécrire la garde elle-même" \
    '{"tool_name":"Write","tool_input":{"file_path":"/home/x/gatebeast/scripts/hook-guard-dequeue.sh"}}'
try refuse "écrire l'armement par l'outil d'édition" \
    '{"tool_name":"Write","tool_input":{"file_path":"/home/x/gatebeast/var/hooks/dequeue-armed"}}'

try laisse "lire l'armement" \
    '{"tool_name":"Bash","tool_input":{"command":"cat var/hooks/dequeue-armed"}}'
try laisse "lister le répertoire" \
    '{"tool_name":"Bash","tool_input":{"command":"ls -la var/hooks/"}}'
try laisse "une commande sans rapport" \
    '{"tool_name":"Bash","tool_input":{"command":"rm -f var/tmp/probe.png"}}'
try laisse "éditer un fichier sans rapport" \
    '{"tool_name":"Write","tool_input":{"file_path":"/home/x/gatebeast/SUIVI.md"}}'

if [ "$failures" -gt 0 ]; then
    printf '\n%d essai(s) en échec.\n' "$failures"
    exit 1
fi
printf '\nLa garde du dépilement refuse ce qu%s doit et laisse passer le reste.\n' "'elle"
