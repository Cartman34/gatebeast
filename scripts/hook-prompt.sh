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
# SOUS var/, JAMAIS SOUS local/ : local appartient à l'agent et l'outillage n'y écrit rien — un fichier qu'un script y dépose n'a plus de propriétaire. Toute trace
# d'exécution va sous var/, qui est local mais conservé, et jamais versionné.
etat="$(dirname "$0")/../var/hooks/dequeue-armed"

# Le prompt tel qu'il a été écrit. On ne cherche pas GO au milieu d'une phrase : « on verra plus tard, go doucement » n'est pas un ordre de dépilement, et la règle
# du dépôt est explicite — aucune phrase ne s'interprète comme un feu vert, seul le mot seul compte.
prompt=$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null || true)
mot=$(printf '%s' "$prompt" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')

if [ "$mot" = "GO" ]; then
    mkdir -p "$(dirname "$etat")"
    date +%s > "$etat"
    echo "Dépilement armé : tant qu'il reste une tâche à faire ou en cours, la fin de tour sera refusée. Un STOP le désarme, et il expire seul." >&2
    exit 0
fi

if [ "$mot" = "STOP" ]; then
    rm -f "$etat"
    echo "Dépilement désarmé." >&2
    exit 0
fi

exit 0
