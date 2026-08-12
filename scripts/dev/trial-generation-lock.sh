#!/usr/bin/env bash
# USAGE
#   bash scripts/dev/trial-generation-lock.sh — éprouve le verrou par variant SANS dépenser une seule génération : il pose le verrou à la main, lance la
#   commande, et vérifie qu'elle refuse. Rend 0 si le refus tombe et si le verrou survit à l'essai.
#   bash scripts/dev/trial-generation-lock.sh -h|--help — this text
#
# INTENTION
#   « TU DOIS AVOIR UN LOCK ENTRE DES LANCEMENTS CONCURRENTS DE GÉNÉRATION D'UN MÊME VARIANT » (opérateur, 2026-08-12), après six générations lancées ensemble
#   dont quatre se sont écrasées. Un verrou ne se vérifie pas en le lisant : il se vérifie en essayant de passer outre. Et l'essai ne peut pas lancer deux vraies
#   générations pour le prouver — ce serait payer le défaut une seconde fois.
set -u

repo="$(cd "$(dirname "$0")/../.." && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$repo/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

code="TR-063"
variant="orientation-south_action-idle_frame-01"
verrou="$repo/var/locks/${code}_${variant}.lock"

mkdir -p "$repo/var/locks"
printf '999999 essai\n' > "$verrou"

sortie="$(cd "$repo" && python3 scripts/generate-sprite.py "$code" "$variant" --generate 2>&1)"
etat=$?

echec=0
if [ "$etat" -eq 0 ]; then
  echo "PERDU — la commande est partie alors que le verrou etait pose"
  echec=1
else
  case "$sortie" in
    *"est déjà en cours"*) echo "OK — la seconde commande refuse et nomme le verrou" ;;
    *) echo "PERDU — elle a echoue pour une autre raison : $sortie"; echec=1 ;;
  esac
fi

if [ -f "$verrou" ]; then
  echo "OK — le verrou d un autre n est pas retire par la commande qui le rencontre"
else
  echo "PERDU — la commande refusee a retire le verrou qu elle ne tenait pas"
  echec=1
fi
rm -f "$verrou"

exit "$echec"
