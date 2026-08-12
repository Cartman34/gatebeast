#!/usr/bin/env bash
# Usage: bash scripts/dev/trial-garde-portees.sh — feeds the scope guard the payloads it exists to refuse, plus the ones it must let through, and reports.
#        bash scripts/dev/trial-garde-portees.sh -h|--help — this text
#
# Intention: the guard was written right after the agent drifted out of scope twice in one session, and a guard is only worth what it refuses. Declaring it in
# the settings proves nothing on its own; feeding it the payloads says today whether it bites.

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$(cd "$(dirname "$0")/../.." && pwd)/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

guard="$(dirname "$0")/../../scripts/hook-guard-scopes.sh"
export CLAUDE_PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
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

try refuse "un brouillon dans le scratchpad du harnais" \
    '{"tool_name":"Write","tool_input":{"file_path":"/tmp/claude-1002/x/scratchpad/q7.md"}}'
try refuse "un brouillon sous var/tmp/" \
    "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$CLAUDE_PROJECT_DIR/var/tmp/redactions/q7.md\"}}"
try refuse "une note sous var/" \
    "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$CLAUDE_PROJECT_DIR/var/notes.md\"}}"
try refuse "une édition sous var/" \
    "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$CLAUDE_PROJECT_DIR/var/hooks/etat\"}}"

try laisse "un brouillon sous local/redactions/" \
    "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$CLAUDE_PROJECT_DIR/local/redactions/q7.md\"}}"
try laisse "un script sous local/scripts/" \
    "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$CLAUDE_PROJECT_DIR/local/scripts/sonde.php\"}}"
try laisse "un document du dépôt" \
    "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$CLAUDE_PROJECT_DIR/SUIVI.md\"}}"
try laisse "la méthode commune, autre dépôt déclaré" \
    '{"tool_name":"Edit","tool_input":{"file_path":"/home/sowapps/projects/conceptions/methode/execution.md"}}'
try laisse "une commande bash, qui ne regarde pas cette garde" \
    "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"php build.php > $CLAUDE_PROJECT_DIR/var/rapport.json\"}}"

if [ "$failures" -gt 0 ]; then
    printf '\n%d essai(s) en échec.\n' "$failures"
    exit 1
fi
printf '\nLa garde des portées refuse ce qu%s doit et laisse passer le reste.\n' "'elle"
