# Agents — GateBeast

Dépôt du projet GateBeast (jeu original de collection de créatures). Règles pour tout agent :

- **Conception (la cible, source de vérité)** : `doc/conception/` — rapatriée ici depuis `conceptions/`, elle suit désormais le versionnage du projet. Chemin de reprise : la méthode (`~/projects/conceptions/methode/`), puis `doc/conception/vision.md`, `doc/conception/questions.md`, puis la descente jusqu'au nœud concerné en lisant ses ancêtres.
- **`SUIVI.md`** : où en est le travail — état courant, défauts constatés, outils. À lire en premier pour reprendre. **`PLAN-ACTION.md`** : le découpage en briques vers la 0.1. Ni l'un ni l'autre n'est de la conception : ils décrivent le chemin, jamais la cible.
- **`doc/`** : la documentation du projet. `doc/conception/` décrit la **cible** et fait foi ; le reste de `doc/` décrira l'existant.
- **`scripts/`** : l'outillage de production, **intégralement en anglais** (noms, contenu, commentaires). Le générateur d'images est l'agent Codex, enveloppé par `~/projects/conceptions/methode/outils/generate-image.php` (transverse, hors dépôt).
- **`assets/`** : les images produites. **Rien ne se jette** : une image écartée cesse d'être montrée, elle n'est pas supprimée.
- **`local/`** : répertoire de travail de l'agent (essais, mesures, brouillons) — jamais commité.
- **Git : aucune écriture d'historique sans ordre explicite du propriétaire** — `commit`, `commit --amend` et `push` compris. L'agent exécute lui-même les commandes git, mais seulement une fois l'ordre donné ; les commits restent occasionnels, pas un par étape. Dépôt distant : `git@github.com:Cartman34/gatebeast.git` (`origin`, branche `main`). **Jamais de ligne `Co-Authored-By` nommant Claude ou Anthropic** : le propriétaire est l'unique auteur de ses commits.
- **Publication** : les revues sont des artefacts Claude republiés à adresse stable (le paramètre `url` de l'outil Artifact conserve le lien). Les adresses en cours sont listées dans `SUIVI.md`.
- **Une seule génération par version, aucune relance sans accord** — sauf la reprise unique prévue par la chaîne de production des assets (`doc/conception/referentiels/visuel/assets/chaine-de-production.md`), qui ne vaut que pour elle.
- Méthode de travail commune : `~/projects/conceptions/methode/` — conception descendante, collaboration avec le propriétaire, principes d'exécution.
