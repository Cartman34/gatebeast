#!/usr/bin/env bash
# Usage: bash scripts/diff-prompts-words.sh <dossier de référence> — compares the current prompts to a reference set IGNORING line breaks, and reports only what changed in the words themselves.
#
# Intention: some changes are meant to move whitespace and nothing else — folding a description to the project's width is exactly that. The ordinary comparison
# reports every one of those files as different, which drowns a real regression among them. This one normalises whitespace on both sides before comparing, so it
# answers the only question that matters after such a change: did any WORD move?
#
# It never replaces the ordinary comparison, it completes it: a change that alters the words must still be caught, and it is, by this very command.

set -u
reference="${1:-var/tmp/consignes-avant}"
courant="var/tmp/consignes-courantes"
[ -d "$courant" ] || { echo "Pas de consignes courantes — lancez d'abord scripts/diff-prompts.sh"; exit 1; }

ecarts=0
for fichier in "$reference"/*.txt; do
    nom=$(basename "$fichier")
    autre="$courant/$nom"
    [ -f "$autre" ] || { echo "ABSENTE des courantes : $nom"; ecarts=$((ecarts + 1)); continue; }
    if ! diff -q <(tr -s '[:space:]' ' ' < "$fichier") <(tr -s '[:space:]' ' ' < "$autre") > /dev/null; then
        echo "LES MOTS ONT CHANGÉ : $nom"
        ecarts=$((ecarts + 1))
    fi
done

if [ "$ecarts" -eq 0 ]; then
    echo "AUCUN MOT N'A BOUGÉ sur les $(ls -1 "$reference" | wc -l) consignes — seuls des espaces diffèrent."
else
    echo "$ecarts consigne(s) dont les mots diffèrent."
fi
