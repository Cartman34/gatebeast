#!/usr/bin/env bash
# USAGE
#   bash scripts/dev/trial-last-order.sh — éprouve `scripts/check-last-order.php` dans les deux sens : un GO arme, un STOP désarme, un message sans ordre
#   désarme aussi. Rend 0 si les trois cas répondent comme attendu.
#   bash scripts/dev/trial-last-order.sh -h|--help — this text
#
# INTENTION
#   LA COMMANDE ARME MAINTENANT, ET PAS SEULEMENT DÉSARME (opérateur, 2026-08-12). Une commande qui touche l'état d'armement dans les deux sens doit être éprouvée
#   dans les deux sens : celle qui ne désarmait que sur un STOP avait laissé passer, le 2026-08-09, un vieux mot qui réarmait à chaque fin de tour. Les transcrits
#   d'essai sont fabriqués ici, jamais pris sur une vraie session : on ne mesure pas une garde sur les ordres réels de l'opérateur.
set -u

repo="$(cd "$(dirname "$0")/../.." && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$repo/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

essais="$repo/var/tmp/essais-ordre"
rm -rf "$essais"
mkdir -p "$essais"

ecrire() {
  printf '{"type":"user","message":{"role":"user","content":"%s"}}\n' "$1" > "$2"
}

echec=0
verifier() {
  local nom="$1" attendu="$2" obtenu="$3"
  if [ "$attendu" = "$obtenu" ]; then
    echo "OK — $nom"
  else
    echo "PERDU — $nom : attendu $attendu, obtenu $obtenu"
    echec=1
  fi
}

ecrire "GO" "$essais/go.jsonl"
php "$repo/scripts/check-last-order.php" "$essais/go.jsonl" > /dev/null
verifier "un GO arme" "0" "$?"
[ -f "$repo/var/hooks/dequeue-armed" ] || { echo "PERDU — un GO arme : l état n existe pas"; echec=1; }

ecrire "STOP" "$essais/stop.jsonl"
php "$repo/scripts/check-last-order.php" "$essais/stop.jsonl" > /dev/null
verifier "un STOP desarme" "1" "$?"
[ -f "$repo/var/hooks/dequeue-armed" ] && { echo "PERDU — un STOP desarme : l etat existe encore"; echec=1; }

ecrire "regarde plutot ca" "$essais/rien.jsonl"
php "$repo/scripts/check-last-order.php" "$essais/rien.jsonl" > /dev/null
verifier "un message sans ordre desarme" "1" "$?"

exit "$echec"
