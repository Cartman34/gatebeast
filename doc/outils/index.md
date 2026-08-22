# Quel outil pour quel besoin

**Usage :** avant d'écrire le moindre script, chercher ici. **Aucun outil ne se réinvente** : le tableau dit, pour chaque besoin, l'outil à employer. Tous les scripts sont dans `scripts/`, en
anglais, exécutables depuis la racine du dépôt, et chacun répond à `-h`.

**Intention :** que cette carte ait une adresse à elle. Elle vivait dans [le journal des séances](../journal-des-seances.md), un document qui ne fait pas foi et que personne ne rouvre — et elle y
avait dérivé : elle nommait encore `cut-asset.py`, `run-fence-campaign.py` et `sprite-queue.py`, trois outils retirés du dépôt. **Une carte que les règles disent de consulter est une donnée, pas
un récit de séance.**

**Ne couvre pas** les outils extérieurs et leurs versions ([outils-exterieurs.md](../outils-exterieurs.md)), ni la façon de se servir d'un outil donné — chacun porte son bloc « Usage » et
« Intention » en tête, et deux d'entre eux ont leur document ici : [le plan de composition](plan-de-composition.md) et [le référentiel des sujets](referentiel-des-sujets.md).

## Le tableau

| Besoin | Outil à employer |
|---|---|
| **Dessiner un plan de composition** (avant toute génération) | `plan_svg.py` — le moteur unique : plan **à plat vu de dessus**, grille, emprises colorées, tracés, habitants, légende, contrôles bloquants. Ne jamais redessiner un plan à la main ni en perspective. |
| Plan de composition d'une planche de référence | `build-plan-svg.py` (32 × 24) |
| Rendre un plan de composition depuis son JSON déclaratif | `build-composition-plan.py <plan.json>` — générique, contrôles bloquants |
| Vérifier la cohérence d'un tracé (formes, raccords) | `plan_svg.check_traces()` — par calcul, jamais à l'œil |
| Assembler une consigne de planche | `plate_common.py` (socle français, fiches témoins, `shoot()` anti-doublon) |
| Assembler une consigne d'asset | `asset_common.py`, via `generate-asset.py` |
| Contrôler une consigne avant génération | `check-plate-prompts.py` — bloque en cas de faute |
| Générer une image | `generate-image.php` — **jamais appelé à la main**, la chaîne passe par `generate-asset.py` |
| Mesurer un asset | `check-asset.py` (transparence, emprise, raccord, lumière) |
| Mesurer une planche | `analyze-plate.py` (mesures + verdict lumière) |
| Juger la projection d'une sprite | `check-axonometry.py` — trois états, et **il dit quand il ne peut pas conclure** |
| Vérifier qu'un jeu de pièces raccorde | `check-piece-widths.php` — compare les pièces **entre elles**, écarte les coins et les clôtures, et le dit |
| Convertir case ↔ pixels, dimensionner | `tile_scale.py` — **seul détenteur** des deux valeurs : case d'écran à 24 px, finesse de livraison dimensionnée sur le zoom maximum |
| Exporter un livrable | `export-asset.py` — redimensionne, ne rogne rien, mesure l'emprise et le point de pose |
| Lire ou contrôler le référentiel des sujets | `check-subjects.py` — affiche la valeur résolue du passage, niveau par niveau |
| Commander une sprite, quelle qu'elle soit | `generate-sprite.py <ref du sujet> <ref du variant>` — tout est lu au référentiel ; elle exporte, inscrit et écrit son rapport |
| Commander un exemple d'usage | `generate-usage-sample.py` depuis un plan de composition |
| Rééchantillonner une image | `resize-image.py` |
| Construire une page de revue | `build-planches-page.py`, `build-calibration-page.py`, et `review-server/suivi-sprites/build.php` pour le suivi des sprites |
| Lire ou écrire les points ouverts | `backlog.php` — **la seule commande** qui lit et écrit `review-server/tasks.json` |
| Regarder un SVG que j'ai produit | `rsvg-convert` vers un PNG dans `local/` — un agent ne sait pas lire un SVG, il lit une image matricielle |

Les `generate-planche-*.py` et `generate-humans-calibration-*.py` sont conservés tels quels : un fichier par passage, ils ne se rejouent pas.

## Ce qui a été retiré, et pourquoi c'est écrit ici

**`cut-asset.py`, `run-fence-campaign.py`, `sprite-queue.py` et `list-variants.py` ne sont plus dans le dépôt** — retirés par `W23 outils-morts`, le second lot le 2026-08-20. Un tableau qui les
nommait encore envoyait un agent lancer une commande inexistante, et une carte fausse coûte plus cher qu'une carte absente. **Un outil retiré se note ici le jour où il l'est**, sinon la carte
redérive.
