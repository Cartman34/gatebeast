#!/usr/bin/env bash
# Usage: bash scripts/dev/trial-install-tools.sh — proves that install-tools.sh recognises what is already installed, so that running it twice does nothing.
#
# Intention: IDEMPOTENCE HERE IS A NAME MAPPING, AND IT IS WHERE THE SCRIPT BROKE. Its first version derived the module name from the package name by swapping
# dashes for underscores, which gives `scikit_image` — a module that does not exist. The import would have failed forever: every run would have reinstalled a
# library already present, and `--check` would have kept announcing it missing. That is not a rare edge, it is the ordinary second run.
#
# So this trial does not install anything. It asserts that every package the script declares imports under the module name the script declares FOR IT — which is
# the only thing that decides whether a second run is a no-op. A package genuinely absent is reported as such and is not a failure of this trial.

set -u
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
fi
root=$(cd "$(dirname "$0")/../.." && pwd)
script="$root/scripts/install-tools.sh"

echo "== Chaque paquet déclaré s'importe-t-il sous le module déclaré ?"
red=0
absent=0
# The pairs are read FROM THE SCRIPT ITSELF, never copied here: a copy would agree with itself while the script drifted.
pairs=$(sed -n '/^libraries="/,/^[a-z-]*|[a-z]*|.*"$/p' "$script" | sed 's/^libraries="//' | sed 's/"$//' | grep -E '^[A-Za-z0-9_-]+\|[A-Za-z0-9_]+\|')
while IFS='|' read -r package module why; do
    [ -z "$package" ] && continue
    if python3 -c "import $module" 2>/dev/null; then
        echo "  VERT  $package s'importe sous « $module »"
    elif python3 -m pip show "$package" >/dev/null 2>&1; then
        echo "  ROUGE $package EST INSTALLÉ mais ne s'importe PAS sous « $module » — le script le croira manquant à chaque lancement."
        red=$((red + 1))
    else
        echo "  ?     $package n'est pas installé : cette paire ne peut pas être éprouvée ici."
        absent=$((absent + 1))
    fi
done <<PAIRS
$pairs
PAIRS

echo
echo "== Le script dit-il « rien à faire » quand tout est là ?"
if [ "$absent" -eq 0 ]; then
    if bash "$script" --check >/dev/null 2>&1; then
        echo "  VERT  --check sort en 0 et n'installe rien."
    else
        echo "  ROUGE --check refuse alors que tout s'importe."
        red=$((red + 1))
    fi
else
    echo "  ?     $absent paquet(s) absent(s) : ce cas ne peut être éprouvé qu'après installation."
fi

echo
if [ "$red" -gt 0 ]; then
    echo "$red cas rouge(s) — le script n'est pas idempotent."
    echo "  Solution — corriger la paire paquet|module dans scripts/install-tools.sh : c'est elle, et elle seule, qui décide."
    exit 1
fi
echo "Aucun cas rouge. Les paires installées s'importent bien sous le nom déclaré."
