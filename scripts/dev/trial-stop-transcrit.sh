#!/usr/bin/env bash
# USAGE
#   bash scripts/dev/trial-stop-transcrit.sh            runs the trial and stops on the first case that fails
#   bash scripts/dev/trial-stop-transcrit.sh -h|--help  this text
#
#   Works on a throwaway hook directory under var/tmp/, never on the real armament state.
#
# INTENTION
# Vérifie qu'un STOP glissé PENDANT le tour désarme le dépilement, et qu'un STOP d'un tour précédent ne fait rien.
#
# Le second cas est le plus important des deux : c'est la régression du 2026-08-09, où lire tout le transcrit retrouvait toujours un vieux mot. La borne est
# positionnelle — la dernière entrée qui ouvre un tour — et c'est elle que ce script éprouve.

set -u
racine="$(cd "$(dirname "$0")/../.." && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$racine/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

export GATEBEAST_HOOK_DIR="$racine/var/tmp/essai-stop"

echoue() {
    printf 'RATÉ — %s\n' "$1"
    exit 1
}

# CAS 1 — le STOP est glissé pendant le tour courant : il est après la dernière entrée qui ouvre un tour, donc il compte.
rm -rf "$GATEBEAST_HOOK_DIR"
mkdir -p "$GATEBEAST_HOOK_DIR"
date +%s > "$GATEBEAST_HOOK_DIR/dequeue-armed"
transcrit="$GATEBEAST_HOOK_DIR/transcrit.jsonl"
printf '%s\n' '{"type":"user","message":{"content":[{"type":"text","text":"GO"}]}}' > "$transcrit"
printf '%s\n' '{"type":"assistant","message":{"content":[{"type":"text","text":"je travaille"}]}}' >> "$transcrit"
printf '%s\n' '{"type":"queue-operation","operation":"enqueue","content":"STOP"}' >> "$transcrit"
printf '%s\n' '{"type":"queue-operation","operation":"remove","content":"STOP"}' >> "$transcrit"

sortie=$(printf '{"transcript_path":"%s","stop_hook_active":false}' "$transcrit" | php "$racine/scripts/hook-stop.php" 2>&1)
code=$?
[ "$code" -ne 0 ] && echoue "cas 1 : la fin de tour aurait dû passer, code $code"
[ -f "$GATEBEAST_HOOK_DIR/dequeue-armed" ] && echoue "cas 1 : le STOP du tour aurait dû désarmer"

# CAS 2 — le STOP appartient à un tour PRÉCÉDENT : une entrée qui ouvre un tour le suit, donc la borne le met hors de portée.
rm -rf "$GATEBEAST_HOOK_DIR"
mkdir -p "$GATEBEAST_HOOK_DIR"
date +%s > "$GATEBEAST_HOOK_DIR/dequeue-armed"
transcrit="$GATEBEAST_HOOK_DIR/transcrit.jsonl"
printf '%s\n' '{"type":"queue-operation","operation":"enqueue","content":"STOP"}' > "$transcrit"
printf '%s\n' '{"type":"user","message":{"content":[{"type":"text","text":"GO"}]}}' >> "$transcrit"
printf '%s\n' '{"type":"assistant","message":{"content":[{"type":"text","text":"je travaille"}]}}' >> "$transcrit"

printf '{"transcript_path":"%s","stop_hook_active":false}' "$transcrit" | php "$racine/scripts/hook-stop.php" > /dev/null 2>&1
[ -f "$GATEBEAST_HOOK_DIR/dequeue-armed" ] || echoue "cas 2 : un STOP d'un tour précédent a désarmé — la borne ne tient pas"

printf 'OK — un STOP glissé pendant le tour désarme ; celui d un tour précédent ne fait rien\n'
printf '     %s\n' "$sortie"
