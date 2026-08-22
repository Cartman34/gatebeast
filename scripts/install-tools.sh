#!/usr/bin/env bash
# Usage: bash scripts/install-tools.sh          — installs the Python libraries this project's tooling needs, and reports what was already there.
#        bash scripts/install-tools.sh --check  — only says what is missing, installs nothing. Exit 1 when something is.
#        bash scripts/install-tools.sh -h|--help — this text, and nothing is installed.
#
# Intention: A DEPENDENCY THAT IS NEEDED AND NEVER INSTALLED IS A TOOL THAT LIES. `scripts/check-axonometry.py` was written around `scikit-image`, which was
# asked for and never granted; without it the check reads only a sprite's outer silhouette, never its inner edges — so it concludes on 55 of the 186 delivered
# sprites and gives up on the other 131. This file is where a needed library is written down, so that granting it is one command instead of a conversation.
#
# IT IS IDEMPOTENT, AND ITS FIRST VERSION WAS NOT (operator, 2026-08-20: « le script d'install doit être idempotent, comme tous nos scripts, c'est le cas ? »).
# It derived the module name from the package name by swapping dashes for underscores, which gives `scikit_image` — a module that does not exist. The import
# would have failed forever, so every run would have reinstalled a library already there, and the check would have kept announcing it missing. THE MAPPING IS
# NOW WRITTEN OUT, package by package: `scikit-image` imports as `skimage`, `Pillow` as `PIL`, and no rule derives one from the other.
#
# IT CHECKS ITS RIGHTS BEFORE ASKING FOR THEM (same day: « il doit veiller aux droits nécessaires »). Installing into a system Python needs either root or the
# user scheme; pip refuses one way on a distribution-managed install and another way without write access. The script tries the user scheme first — which needs
# no privilege at all — and names the privileged command instead of running it: elevating is the operator's gesture, never the agent's.

set -u
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
fi
check_only=0
if [ "${1:-}" = "--check" ]; then
    check_only=1
fi

# THREE FIELDS: the package pip installs, the module Python imports, and what needs it. The first two differ often enough that deriving one from the other is
# how this script broke; the third is what makes a dependency removable — one nobody can attribute is one nobody dares touch.
libraries="numpy|numpy|les mesures d'image et le traitement de matrice (check-asset.py, export-asset.py)
Pillow|PIL|l'ouverture et l'écriture des PNG, partout
scipy|scipy|les gradients de check-axonometry.py, préférés à une bibliothèque de plus
scikit-image|skimage|les ARÊTES INTÉRIEURES d'une sprite, que check-axonometry.py ne sait pas lire sans elle"

missing=""
echo "== Ce dont l'outillage a besoin"
while IFS='|' read -r package module why; do
    [ -z "$package" ] && continue
    if python3 -c "import $module" 2>/dev/null; then
        echo "  PRÉSENT  $package (import $module) — $why"
    else
        echo "  MANQUANT $package (import $module) — $why"
        missing="$missing $package"
    fi
done <<LIBRARIES
$libraries
LIBRARIES

if [ -z "$missing" ]; then
    echo
    echo "Tout est là. Rien à installer, et relancer ce script ne fera rien de plus."
    exit 0
fi

echo
if [ "$check_only" -eq 1 ]; then
    echo "Manquant :$missing"
    echo "  Solution — « bash scripts/install-tools.sh » les installe."
    exit 1
fi

# THE USER SCHEME FIRST, BECAUSE IT NEEDS NO PRIVILEGE. `--break-system-packages` is required on a distribution that manages Python by its own packages; pip
# refuses to touch the system installation without it, and refuses again without write access. Both flags together install into the user's own directory, which
# is exactly where a tool used by this repository belongs.
echo "== Installation de :$missing"
echo "   dans l'espace utilisateur — aucun droit administrateur n'est demandé."
if python3 -m pip install --user --break-system-packages $missing; then
    echo
    echo "Installé. À faire ensuite :"
    echo "  1. « bash scripts/install-tools.sh --check » pour confirmer — il doit dire que tout est là."
    echo "  2. Constater les versions et les inscrire à doc/implemented/outside-tools.md : une version écrite est un constat daté, jamais une garantie."
    echo "  3. « python3 scripts/check-axonometry.py assets/cutout/*/*.png » pour voir combien de sprites il sait juger maintenant."
    exit 0
fi

# THE PRIVILEGED COMMAND IS NAMED, NEVER RUN. Elevating rights is the operator's decision, and a script that calls `sudo` by itself takes it for him — on a
# machine where he may have wanted a virtual environment instead.
echo
echo "L'installation dans l'espace utilisateur a échoué."
echo "  Solution 1, par les paquets de la distribution, et c'est la plus propre :"
echo "      sudo apt install python3-skimage python3-numpy python3-scipy python3-pil"
echo "  Solution 2, par pip avec les droits administrateur :"
echo "      sudo python3 -m pip install --break-system-packages$missing"
echo "  Solution 3, dans un environnement virtuel, si vous préférez isoler :"
echo "      python3 -m venv .venv && .venv/bin/pip install$missing"
echo "  Puis « bash scripts/install-tools.sh --check » pour confirmer."
exit 1
