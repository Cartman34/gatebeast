#!/usr/bin/env bash
# Usage: bash scripts/dev/trial-cited-paths.sh — proves that check-cited-paths.php sweeps every Markdown document it finds, whatever its name.
#
# Intention: THE LIST OF DOCUMENTS USED TO BE WRITTEN BY HAND, AND IT WAS WRONG (operator, 2026-08-19: « aucun fichier n'est à analyser en dur, ça n'a aucun
# sens »). It named `CLAUDE.md`, deleted the same day, and it would have swept a document that no longer exists — silently, since an absent file was not a fault.
# A document added tomorrow would never have been swept at all.
#
# The only way to prove the sweep is by DISCOVERY, not by list, is to drop a document the check has never heard of and require it to be caught. This trial writes
# one at the repository root, cites a path that does not exist inside it, and requires the check to refuse — then removes it, even if the trial fails.

set -u
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
fi
root=$(cd "$(dirname "$0")/../.." && pwd)
witness="$root/ESSAI-TEMOIN-CITED-PATHS.md"

cleanup() {
    rm -f "$witness"
}
trap cleanup EXIT

echo "== Cas 1 : le dépôt tel quel"
php "$root/scripts/check-cited-paths.php"
before=$?
echo "code $before"

echo
echo "== Cas 2 : un document neuf, jamais nommé nulle part, citant un fichier absent"
printf '# Témoin\n\nCe document cite `scripts/ce-fichier-nexiste-pas.php`, qui ne mène nulle part.\n' > "$witness"
php "$root/scripts/check-cited-paths.php" -v | grep -q 'ESSAI-TEMOIN-CITED-PATHS.md'
found=$?
cleanup

if [ "$found" -eq 0 ]; then
    echo "VERT : le document neuf a été balayé et sa citation morte signalée."
else
    echo "ROUGE : un document que la liste ne nommait pas n'a pas été balayé."
    exit 1
fi

echo
echo "== Le dépôt est remis en état"
php "$root/scripts/check-cited-paths.php" || true
exit 0
