#!/usr/bin/env bash
# Usage: bash scripts/install-tools.sh          — installs the Python libraries this project's tooling needs, and reports what was already there.
#        bash scripts/install-tools.sh --check  — only says what is missing, installs nothing.
#        bash scripts/install-tools.sh -h|--help — this text, and nothing is installed.
#
# Intention: A DEPENDENCY THAT IS NEEDED AND NEVER INSTALLED IS A TOOL THAT LIES. `scripts/check-axonometry.py` was written around `scikit-image`, which was
# asked for and never granted; without it the check reads only a sprite's outer silhouette, never its inner edges — so it concludes on 55 of the 186 delivered
# sprites and gave up on the other 131. This file is where a needed library is written down, so that granting it is one command instead of a conversation.
#
# INSTALLING IS THE OPERATOR'S GESTURE, NOT THE AGENT'S (règles du dépôt: an unvalidated tool is asked for, never tried). This script is what he runs; the agent
# only ever adds a line to it and says so. That is why it prints what it would do before doing it, and why `--check` exists at all.
#
# THE VERSIONS ARE NOT PINNED HERE. `doc/outils-exterieurs.md` records the version CONSTATED, which is a dated observation and not a guarantee — pinning would
# turn one machine's observation into a rule for every other.

set -u
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
fi
check_only=0
if [ "${1:-}" = "--check" ]; then
    check_only=1
fi

# One line per library, with what needs it — a dependency nobody can attribute is a dependency nobody dares remove.
libraries="numpy:les mesures d'image et le traitement de matrice (check-asset.py, export-asset.py)
Pillow:l'ouverture et l'écriture des PNG, partout
scipy:les gradients de check-axonometry.py, préférés à une bibliothèque de plus
scikit-image:les ARÊTES INTÉRIEURES d'une sprite, que check-axonometry.py ne sait pas lire sans elle"

missing=""
echo "== Ce dont l'outillage a besoin"
while IFS=: read -r library why; do
    [ -z "$library" ] && continue
    module=$(echo "$library" | tr '-' '_' | tr '[:upper:]' '[:lower:]')
    if [ "$module" = "pillow" ]; then
        module="PIL"
    fi
    if python3 -c "import $module" 2>/dev/null; then
        echo "  PRÉSENT  $library — $why"
    else
        echo "  MANQUANT $library — $why"
        missing="$missing $library"
    fi
done <<LIBRARIES
$libraries
LIBRARIES

if [ -z "$missing" ]; then
    echo
    echo "Tout est là. Rien à installer."
    exit 0
fi

echo
if [ "$check_only" -eq 1 ]; then
    echo "Manquant :$missing"
    echo "  Solution — « bash scripts/install-tools.sh » les installe."
    exit 1
fi

echo "== Installation de :$missing"
# --break-system-packages : sur une distribution qui gère Python par ses paquets, pip refuse d'écrire dans l'installation du système sans ce drapeau. Il est
# écrit ici plutôt que découvert au premier refus, et il reste le geste de l'opérateur.
if ! python3 -m pip install --break-system-packages $missing; then
    echo
    echo "L'installation a échoué."
    echo "  Solution — installer par les paquets de la distribution, par exemple « sudo apt install python3-skimage », puis relancer avec « --check »."
    exit 1
fi

echo
echo "Installé. À faire ensuite :"
echo "  1. « bash scripts/install-tools.sh --check » pour confirmer."
echo "  2. Constater les versions et les inscrire à doc/outils-exterieurs.md — une version écrite est un constat daté, jamais une garantie."
echo "  3. « python3 scripts/check-axonometry.py assets/cutout/*/*.png » pour voir combien de sprites il sait juger maintenant."
