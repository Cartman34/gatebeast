#!/usr/bin/env bash
# USAGE
#   bash scripts/dev/trial-mot-ordre.sh            runs the trial and reports how many cases failed
#   bash scripts/dev/trial-mot-ordre.sh -h|--help  this text
#
#   Reads nothing and writes nothing: it feeds sample lines to the order-word reader and compares what
#   comes back. Exits non-zero as soon as one case reads a word the rule does not give it.
#
# INTENTION
# Éprouve la règle du mot d'ordre elle-même : premier mot de sa ligne, suivi d'un caractère blanc ou de rien, la casse n'important pas.
#
# Ce script n'éprouve QUE la lecture du mot — pas qu'il arrive, pas ce que la garde en fait. C'est délibéré : les deux questions sont distinctes, et les avoir
# mélangées est ce qui a fait croire pendant deux jours qu'un STOP n'arrivait jamais alors qu'il était mal lu.

set -u
racine="$(cd "$(dirname "$0")/../.." && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$racine/scripts/tools.php" show "$(basename "$0")"
    exit 0
fi

rates=0

essai() {
    attendu="$2"
    obtenu=$(printf '%s' "$1" | php -r 'require "'"$racine"'/scripts/hook-word.php"; echo HookWord::get()->order(stream_get_contents(STDIN)) ?? "aucun";')
    if [ "$obtenu" = "$attendu" ]; then
        printf '  OK    %-34s %s\n' "$3" "$obtenu"
    else
        printf '  RATÉ  %-34s attendu %s, obtenu %s\n' "$3" "$attendu" "$obtenu"
        rates=$((rates + 1))
    fi
}

printf 'Le mot ouvre sa ligne\n'
essai 'STOP'                    'STOP'  'STOP seul'
essai 'STOP regarde plutôt ça'  'STOP'  'STOP puis une phrase'
essai 'GO'                      'GO'    'GO seul'
essai 'GO fais le maintenant'   'GO'    'GO puis une phrase'

printf 'Les deux ordres exigent leurs capitales, aux mêmes conditions\n'
essai 'stop'                    'aucun' 'stop en minuscules'
essai 'Stop'                    'aucun' 'Stop capitalisé'
essai 'stop attends une seconde' 'aucun' 'stop minuscule puis une phrase'
essai 'go'                      'aucun' 'go en minuscules'
essai 'Go'                      'aucun' 'Go capitalisé'
essai 'go fais le maintenant'   'aucun' 'go minuscule puis une phrase'

printf 'Rien ne doit être collé au mot\n'
essai 'STOPPE'                  'aucun' 'STOPPE, un mot plus long'
essai 'STOP!'                   'aucun' 'STOP suivi d une ponctuation'
essai 'GO2'                     'aucun' 'GO suivi d un chiffre'

printf 'Le mot doit ouvrir la ligne\n'
essai 'attends, stop ça'        'aucun' 'stop au milieu d une phrase'
essai 'je dis GO'               'aucun' 'GO en fin de phrase'

printf 'Plusieurs lignes : le dernier ordre gagne\n'
essai 'STOP
regarde plutôt ce fichier'      'STOP'  'STOP puis une consigne'
essai 'STOP
GO'                             'GO'    'STOP puis un GO'

if [ "$rates" -ne 0 ]; then
    printf '%d cas RATÉS\n' "$rates"
    exit 1
fi
printf 'OK — le mot est lu quand il ouvre sa ligne, et seulement là\n'
