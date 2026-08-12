#!/usr/bin/env bash
# Usage: bash scripts/diff-prompts.sh [dossier de référence] — reassembles every declared variant's prompt and reports what changed against the reference set.
#        bash scripts/diff-prompts.sh --freeze <dossier>     — writes the reference set instead of comparing.
#        bash scripts/diff-prompts.sh -h|--help              — this text, and nothing is assembled.
#
# Intention: a prompt is what the generator actually receives, and it is assembled from a dozen places — the base, the camera, the subject's description, its type's
# extra clause, its footprint, its height band. Change any one of them and the effect on the prompt is invisible until an image comes out wrong, two minutes and
# one generation later. This reassembles all of them and shows the difference, so a behaviour change is judged on its text before it is judged on a picture
# (opérateur, 2026-08-07: voir la consigne pour l'apprécier, en tout cas après modification d'un comportement).
#
# It generates nothing and costs no image: the assembling command stops before drawing when it is not told to draw.

set -u
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    php "$(cd "$(dirname "$0")" && pwd)/tools.php" show "$(basename "$0")"
    exit 0
fi

mode="compare"
folder="${1:-var/tmp/consignes-avant}"
if [ "${1:-}" = "--freeze" ]; then
    mode="freeze"
    folder="${2:-var/tmp/consignes-avant}"
fi

current="var/tmp/consignes-courantes"
target="$folder"
[ "$mode" = "freeze" ] && target="$folder"
[ "$mode" = "compare" ] && target="$current"
rm -rf "$target"
mkdir -p "$target"

python3 - <<'PY' > var/tmp/variants.txt
import json
data = json.load(open('assets/subjects.json'))
for code, subject in data['subjects'].items():
    for variant in subject['variants']:
        print(code, variant['ref'])
PY

failures=0
while read -r code ref; do
    if python3 scripts/generate-sprite.py "$code" "$ref" > /dev/null 2>&1; then
        draft=$(ls -t var/tmp/consignes/*.txt 2>/dev/null | head -1)
        [ -n "$draft" ] && cp "$draft" "$target/${code}_${ref}.txt"
    else
        failures=$((failures + 1))
        echo "REFUSÉE : $code $ref"
    fi
done < var/tmp/variants.txt

if [ "$mode" = "freeze" ]; then
    echo "$(ls -1 "$target" | wc -l) consigne(s) figée(s) dans $target, $failures refusée(s)"
    exit 0
fi

echo
if diff -rq "$folder" "$current" > var/tmp/consignes-diff.txt 2>&1; then
    echo "AUCUN CHANGEMENT — les $(ls -1 "$current" | wc -l) consignes sont identiques à la référence."
else
    echo "CE QUI A CHANGÉ depuis la référence $folder :"
    cat var/tmp/consignes-diff.txt
    echo
    echo "Le détail ligne à ligne : diff -r $folder $current"
fi
