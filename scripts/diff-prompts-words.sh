#!/usr/bin/env bash
# Usage: bash scripts/diff-prompts-words.sh <dossier de référence> — compares the current prompts to a reference set IGNORING line breaks, and reports only what changed in the words themselves.
#        bash scripts/diff-prompts-words.sh -h|--help — this text.
#
# Intention: some changes are meant to move whitespace and nothing else — folding a description to the project's width is exactly that. The ordinary comparison
# reports every one of those files as different, which drowns a real regression among them. This one normalises whitespace on both sides before comparing, so it
# answers the only question that matters after such a change: did any WORD move?
#
# It never replaces the ordinary comparison, it completes it: a change that alters the words must still be caught, and it is, by this very command.

set -u
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$(cd "$(dirname "$0")" && pwd)/tools.php" show "$(basename "$0")"
    exit 0
fi

reference="${1:-var/tmp/consignes-avant}"
current="var/tmp/consignes-courantes"
[ -d "$current" ] || { echo "Pas de consignes courantes — lancez d'abord scripts/diff-prompts.sh"; exit 1; }

gaps=0
for file in "$reference"/*.txt; do
    name=$(basename "$file")
    other="$current/$name"
    [ -f "$other" ] || { echo "ABSENTE des courantes : $name"; gaps=$((gaps + 1)); continue; }
    if ! diff -q <(tr -s '[:space:]' ' ' < "$file") <(tr -s '[:space:]' ' ' < "$other") > /dev/null; then
        echo "LES MOTS ONT CHANGÉ : $name"
        gaps=$((gaps + 1))
    fi
done

if [ "$gaps" -eq 0 ]; then
    echo "AUCUN MOT N'A BOUGÉ sur les $(ls -1 "$reference" | wc -l) consignes — seuls des espaces diffèrent."
else
    echo "$gaps consigne(s) dont les mots diffèrent."
fi
