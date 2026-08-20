#!/usr/bin/env bash
# Usage: bash scripts/dev/trial-pages-indexed.sh — proves that check-pages-indexed.php catches a served page missing from the index, and passes when it is there.
#
# Intention: A CHECK THAT HAS NEVER FAILED HAS NEVER BEEN PROVEN. Run on a healthy repository it prints "the two lists agree", which is exactly what a check that
# checks nothing would print too. The only way to tell them apart is to hand it a broken case and watch it refuse — so this trial removes one artifact from the
# registry, runs the check, and requires exit code 1 before putting the registry back.
#
# THE REGISTRY IS PUT BACK EVEN WHEN THE TRIAL FAILS: it is a versioned file of the project, and a trial that leaves the repository broken is worse than no trial.

set -u
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
fi
root=$(cd "$(dirname "$0")/../.." && pwd)
registry="$root/review-server/artefacts.json"
work="$root/local/tmp/trial-pages-indexed"
name="L'atelier de génération"
rm -rf "$work"
mkdir -p "$work"

restore() {
    if [ -f "$work/artefacts.original.json" ]; then
        cp "$work/artefacts.original.json" "$registry"
    fi
}
trap restore EXIT

echo "== Cas 1 : le dépôt tel quel — les deux listes s'accordent"
if ! php "$root/scripts/check-pages-indexed.php"; then
    echo "ROUGE : le contrôle refuse un dépôt sain."
    exit 1
fi
echo "VERT"

echo
echo "== Cas 2 : un artefact retiré du registre — le contrôle doit refuser"
cp "$registry" "$work/artefacts.original.json"
php "$root/scripts/dev/drop-artifact.php" "$registry" "$work/artefacts.json" "$name"
cp "$work/artefacts.json" "$registry"
php "$root/scripts/check-pages-indexed.php"
verdict=$?
restore

if [ "$verdict" -eq 1 ]; then
    echo "VERT : le contrôle a refusé, code 1."
else
    echo "ROUGE : le contrôle a laissé passer une page absente de l'index (code $verdict)."
    exit 1
fi

echo
echo "== Le registre est remis en place"
php "$root/scripts/check-pages-indexed.php"
