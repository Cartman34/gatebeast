# Ce que le système fait aujourd'hui

**Usage :** savoir ce qui EXISTE et tourne, sans lire le code. C'est la contrepartie de [la conception](../conception/vision.md), qui dit la **cible** et fait
foi. Quand les deux se contredisent, ce n'est pas ce document qui a raison : c'est un écart à combler, dans un sens ou dans l'autre.

**Intention :** que l'état du système ait une adresse. Il ne se savait qu'en lisant le code ou en interrogeant un agent qui venait de le lire — et la règle du
dépôt l'écrivait au futur, « le reste de `doc/` **décrira** l'existant ». Écrit le 2026-08-22, sur demande de l'opérateur.

**Ne couvre pas** la cible ([conception](../conception/vision.md)), l'état d'avancement du travail (`SUIVI.md` et `php scripts/backlog.php`), ni le pourquoi
des décisions passées ([journal des séances](../journal-des-seances.md)).

## Ce que le projet produit, en une phrase

GateBeast dessine un monde en **sprites** : des pièces détourées qu'un moteur pose case par case sur une carte, en projection parallèle. Tout ce qui est
implémenté sert cette production — décrire un sujet, en commander l'image, la mesurer, la juger, et retrouver pourquoi elle est ce qu'elle est.

## Les nœuds

| Nœud | Ce qu'il couvre |
|---|---|
| [La chaîne de production](production-chain.md) | d'un sujet du référentiel à une sprite livrée et inscrite |
| [Le serveur de revue](review-server.md) | les pages servies en local, leurs constructeurs et leurs services |
| [L'atelier de consignes](prompt-workshop.md) | la chaîne de versions d'une consigne, ses blocs de source et ses mesures |
| [Les gardes](guards.md) | les hooks du tour d'agent et les contrôles du dépôt |
| [L'établi](dev-workbench.md) | `scripts/dev/` : essais, sondes, lecteurs et instruments |
| [Quel outil pour quel besoin](tools.md) | la carte à consulter avant d'écrire le moindre script |
| [Le référentiel des sujets](subject-referential.md) | `assets/subjects.json` : ce qui se dessine, et comment il se déclare |
| [Le plan de composition](composition-plan.md) | dessiner une composition avant de la produire |
| [Les outils extérieurs](outside-tools.md) | ce que le projet a validé, et les versions constatées |

## Ce qui est couvert en bloc, et pourquoi c'est écrit ici

**`php scripts/check-implemented-coverage.php` VÉRIFIE QUE CHAQUE FICHIER DU DÉPÔT EST NOMMÉ QUELQUE PART DANS CE DOSSIER.** Exiger 157 citations à la main
produirait un inventaire et non une documentation, donc certaines familles sont couvertes **en bloc** — et **le motif de chaque famille s'écrit ici**, jamais
dans le contrôle. Une exemption cachée dans l'outil est une exemption que personne ne relit.

| Famille | Motif | Pourquoi elle se couvre en bloc |
|---|---|---|
| Les essais | `scripts/dev/trial-*` | un essai appartient au contrôle qu'il tient, et le nommer deux fois n'apprend rien |
| Les sondes | `scripts/dev/probe-*` | une par question, décrites en bloc à [l'établi](dev-workbench.md) avec les trois règles qu'elles suivent |
| Les lecteurs de l'établi | `scripts/dev/show-*`, `scripts/dev/list-*`, `scripts/dev/dump-*`, `scripts/dev/find-*`, `scripts/dev/measure-*`, `scripts/dev/draw-*`, `scripts/dev/crop-*` | ils répondent à une question et n'écrivent rien : on les lance, on lit, on jette |
| Les passages à usage unique | `scripts/generate-planche-*.py`, `scripts/generate-humans-calibration-*.py` | un fichier par passage, qui ne se rejoue pas — la carte des outils le dit déjà |
| Les briques partagées | `scripts/*_common.py`, `scripts/plan_svg.py`, `scripts/tile_scale.py` | nommées par les commandes qui s'en servent, dans le nœud qui les décrit |
| Le socle des commandes | `scripts/bootstrap.php`, `scripts/Tools.php`, `scripts/Capture.php`, `scripts/PythonFreeze.php` | décrits aux [gardes](guards.md), qui sont leur seule raison d'être |

**UN FICHIER QUI N'EST NI NOMMÉ NI D'UNE DE CES FAMILLES FAIT ÉCHOUER LE CONTRÔLE**, et c'est voulu : c'est le jour où quelqu'un ajoute une commande sans dire
nulle part ce qu'elle fait que la documentation commence à mentir.
