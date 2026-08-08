#!/usr/bin/env bash
# Usage: declared as a Stop hook in .claude/settings.json. Reads the hook payload on stdin, and refuses the end of turn while work remains.
#
# Intention: the agent must not stop while the backlog still holds a task to do or in progress. The rule is written in three places and the agent broke it four
# times in one evening — a rule that depends on the agent remembering it at the end of every turn does not hold. This does not depend on him: exit code 2 refuses
# the end of turn, and what this writes on standard error comes back to him as the reason to carry on.
#
# TWO CONDITIONS, AND THE FIRST EXISTS ONLY TO PROVE THE SECOND WORKS. A sentinel word the agent writes on purpose lets the whole mechanism be tested in one turn,
# without waiting for the backlog to be in the right state. The real condition is the backlog itself.
#
# BLOCKED TASKS LET THE TURN END, on purpose: they wait on the operator, and refusing to stop on them would trap the agent on work he cannot advance.

set -u
payload=$(cat)

# LE DÉPILEMENT SE TIENT SUR LE « GO » DE L'OPÉRATEUR, PAS SUR LA PRÉSENCE DE CE DÉPÔT. Sans cette condition, toute session ouverte ici subissait le refus — une
# session d'essai s'est retrouvée prise au piège le 2026-08-07, sommée de reprendre une tâche que personne ne lui avait confiée. C'est le hook du prompt qui arme
# cet état sur le mot seul, et le désarme sur STOP.
#
# ET IL EXPIRE. Un GO donné le matin ne doit pas tenir le soir : la pile aura bougé, l'opérateur sera passé à autre chose, et l'agent serait renvoyé sur un travail
# périmé. Passé ce délai, l'état est effacé et la fin de tour redevient libre — il faut alors un GO neuf, ce que la règle du dépôt demande déjà de toute façon.
EXPIRY_SECONDS=$((3 * 3600))
# SOUS var/, JAMAIS SOUS local/ : local appartient à l'agent et l'outillage n'y écrit rien.
etat="$(dirname "$0")/../var/hooks/dequeue-armed"

if [ ! -f "$etat" ]; then
    exit 0
fi

arme=$(cat "$etat" 2>/dev/null || echo 0)
if [ $(( $(date +%s) - arme )) -gt "$EXPIRY_SECONDS" ]; then
    rm -f "$etat"
    echo "Le dépilement a expiré : le GO date de plus de trois heures. Il en faut un neuf pour repartir." >&2
    exit 0
fi

# Le garde-fou du garde-fou : au-delà de ce nombre de refus d'affilée, on laisse passer. Sans lui, une tâche qui ne peut réellement pas avancer enfermerait
# l'agent dans une boucle sans fin, et c'est l'opérateur qui la paierait.
COMPTEUR="$(dirname "$0")/../var/hooks/refusals"
PLAFOND=5

transcript=$(printf '%s' "$payload" | grep -o '"transcript_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')

# L'APPLICATION DIT ELLE-MÊME QUAND ELLE A DÉJÀ ÉTÉ BLOQUÉE, et il faut l'écouter : elle plafonne les refus consécutifs et reprend la main au-delà. Sur l'épreuve,
# un seul refus suffit à prouver que le mécanisme mord — s'entêter ne prouverait rien de plus et userait le plafond pour rien.
deja_bloque=$(printf '%s' "$payload" | grep -o '"stop_hook_active"[[:space:]]*:[[:space:]]*true' || true)

# LE MOT D'ÉPREUVE : l'agent l'écrit quand il veut vérifier que le hook mord. C'est la seule condition qu'il déclenche lui-même, et elle ne coûte rien à laisser
# en place — personne ne l'écrit par accident.
#
# ON NE LIT QUE LE DERNIER MESSAGE DE L'AGENT, ET C'EST TOUT L'ENJEU : lire la fin du fichier retrouvait le mot dans les tours PRÉCÉDENTS, si bien que la condition
# ne pouvait plus jamais être satisfaite et que le refus se rejouait à l'infini. Constaté à la première épreuve, le 2026-08-07. Un hook qui interroge un historique
# au lieu de l'état courant ne se relâche jamais.
if [ -n "$transcript" ] && [ -f "$transcript" ] && [ -z "$deja_bloque" ]; then
    dernier=$(python3 - "$transcript" <<'PY'
import json, sys

texte = ""
with open(sys.argv[1], encoding="utf-8", errors="replace") as fichier:
    for ligne in fichier:
        try:
            entree = json.loads(ligne)
        except ValueError:
            continue
        if entree.get("type") != "assistant":
            continue
        morceaux = entree.get("message", {}).get("content", [])
        if isinstance(morceaux, str):
            texte = morceaux
            continue
        dits = [m.get("text", "") for m in morceaux if isinstance(m, dict) and m.get("type") == "text"]
        if dits:
            texte = "\n".join(dits)
print(texte)
PY
)
    if printf '%s' "$dernier" | grep -q 'EPREUVE-DU-HOOK'; then
        echo "ÉPREUVE DU HOOK : le mot déclencheur a été trouvé dans ta réponse, donc le refus fonctionne. Écris maintenant une phrase le confirmant, SANS ce mot, et le tour pourra se terminer." >&2
        exit 2
    fi
fi

restant=$(cd "$(dirname "$0")/.." && php scripts/backlog.php list 2>/dev/null | grep -c -E '^\S+ +\(\S+ *\) p[0-9]+ +(todo|in-progress)')

if [ "${restant:-0}" -eq 0 ]; then
    rm -f "$COMPTEUR"
    exit 0
fi

refus=$(cat "$COMPTEUR" 2>/dev/null || echo 0)
refus=$((refus + 1))
mkdir -p "$(dirname "$COMPTEUR")"
echo "$refus" > "$COMPTEUR"

if [ "$refus" -gt "$PLAFOND" ]; then
    rm -f "$COMPTEUR"
    echo "Le hook a refusé $PLAFOND fins de tour d'affilée et laisse passer celle-ci : $restant tâche(s) restent à faire ou en cours, et rien n'avance." >&2
    exit 0
fi

premiere=$(cd "$(dirname "$0")/.." && php scripts/backlog.php next 2>/dev/null | head -1)
echo "TU NE T'ARRÊTES PAS : $restant tâche(s) sont encore à faire ou en cours. Reprends la première sans rendre la main :" >&2
echo "  $premiere" >&2
echo "Une tâche qui ne peut pas avancer sans l'opérateur se passe en « blocked » avec sa raison écrite, elle ne se laisse pas en « todo »." >&2
exit 2
