#!/usr/bin/env bash
# Usage: bash scripts/diff-prompts.sh [dossier de référence] — reassembles every declared variant's prompt and reports what changed against the reference set.
#        bash scripts/diff-prompts.sh --freeze <dossier>     — writes the reference set instead of comparing.
#
# Intention: a prompt is what the generator actually receives, and it is assembled from a dozen places — the base, the camera, the subject's description, its type's
# extra clause, its footprint, its height band. Change any one of them and the effect on the prompt is invisible until an image comes out wrong, two minutes and
# one generation later. This reassembles all of them and shows the difference, so a behaviour change is judged on its text before it is judged on a picture
# (opérateur, 2026-08-07: voir la consigne pour l'apprécier, en tout cas après modification d'un comportement).
#
# It generates nothing and costs no image: the assembling command stops before drawing when it is not told to draw.

set -u
mode="compare"
dossier="${1:-var/tmp/consignes-avant}"
if [ "${1:-}" = "--freeze" ]; then
    mode="freeze"
    dossier="${2:-var/tmp/consignes-avant}"
fi

courant="var/tmp/consignes-courantes"
cible="$dossier"
[ "$mode" = "freeze" ] && cible="$dossier"
[ "$mode" = "compare" ] && cible="$courant"
rm -rf "$cible"
mkdir -p "$cible"

python3 - <<'PY' > var/tmp/variants.txt
import json
data = json.load(open('assets/subjects.json'))
for code, subject in data['subjects'].items():
    for variant in subject['variants']:
        print(code, variant['ref'])
PY

echecs=0
while read -r code ref; do
    if python3 scripts/generate-sprite.py "$code" "$ref" > /dev/null 2>&1; then
        brouillon=$(ls -t var/tmp/consignes/*.txt 2>/dev/null | head -1)
        [ -n "$brouillon" ] && cp "$brouillon" "$cible/${code}_${ref}.txt"
    else
        echecs=$((echecs + 1))
        echo "REFUSÉE : $code $ref"
    fi
done < var/tmp/variants.txt

if [ "$mode" = "freeze" ]; then
    echo "$(ls -1 "$cible" | wc -l) consigne(s) figée(s) dans $cible, $echecs refusée(s)"
    exit 0
fi

echo
if diff -rq "$dossier" "$courant" > var/tmp/consignes-diff.txt 2>&1; then
    echo "AUCUN CHANGEMENT — les $(ls -1 "$courant" | wc -l) consignes sont identiques à la référence."
else
    echo "CE QUI A CHANGÉ depuis la référence $dossier :"
    cat var/tmp/consignes-diff.txt
    echo
    echo "Le détail ligne à ligne : diff -r $dossier $courant"
fi
