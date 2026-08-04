# Suivi des travaux — GateBeast

**Intention :** permettre à n'importe quel intervenant de reprendre le travail sans perte. Ce document dit **où on en est**, pas ce que le jeu doit être — la cible vit dans la conception, le découpage en versions dans le [plan d'action](PLAN-ACTION.md).

Il se met à jour à chaque étape franchie. Il ne conserve pas d'historique : seul l'état courant compte (le versionnage garde le reste).

## Où en est le projet (2026-08-03)

**La direction artistique est VALIDÉE** (*toon volume*, figée sur les six planches de référence — décision et termes du propriétaire dans [visuel/index.md](doc/conception/referentiels/visuel/index.md)). **La conception est close** : [questions.md](doc/conception/questions.md) est vide. **Le POC est engagé** : le chemin vers la 0.1 est découpé en briques B0–B8 dans le [plan d'action](PLAN-ACTION.md), avec les décisions déjà prises — B0 maquette à sprites publiée en artefact Claude (hébergement du POC), B1 dépôt `git@github.com:Cartman34/gatebeast.git`, B3 moteur CSS, générateur d'images = agent Codex via le wrapper (capacités au [référentiel technique](doc/conception/referentiels/technique/index.md), limites des artefacts incluses).

**Fait — les capacités du générateur sont constatées** : il rend **exactement la définition demandée** ; il rend un **vrai canal alpha**, vides encerclés compris, dès qu'on le demande — le fond magenta et le détourage ont donc été **abandonnés** ; l'angle obtenu est le bon, c'est la vue standard des sprites. **Deux limites** : le traitement varie d'un sujet à l'autre, et surtout il **n'exploite pas l'image de référence** qu'on lui fournit (voir ci-dessous).

**MAJEUR — la cascade ne fonctionne pas.** La règle de cohérence du projet veut qu'une variante se produise **à partir de la vue principale validée**, fournie comme référence visuelle. Le mécanisme est en place et l'image est bien déposée dans le répertoire de travail du générateur ; mais deux essais sur la clôture nord-sud, dont un avec une consigne disant en toutes lettres « exactement la clôture de l'image de référence, vue tournée d'un quart de tour », ont rendu **une autre clôture**. Deux générations de la même fiche donnent aussi deux chênes nettement différents. Ces images n'ont pas été soumises au propriétaire : le jugement ci-dessus est celui de l'agent principal, pas un verdict du propriétaire. Conséquence : rien ne garantit aujourd'hui la cohérence entre les variantes d'un même sujet — les huit pièces de clôture, les quatre orientations d'un personnage, les poses d'une marche. **Décision à prendre avec le propriétaire avant toute production de variantes.**

**Fait — la couche assets est conçue** (2026-08-03) : modèle sujet / type / profil / variante, orientation dans le repère du monde, action, et une direction par partie qui pointe dans le repère du sujet (`north` = droit devant), images numérotées en dessous, repli déclaré, empilement à l'écran, lots par type, chaîne de production. Voir [rendu en calques](doc/conception/referentiels/technique/rendu-en-calques.md), [assets](doc/conception/referentiels/visuel/assets/index.md), [sujets et variantes](doc/conception/referentiels/visuel/assets/sujets-et-variantes.md) et le [lexique](doc/conception/referentiels/contenu/lexique.md) enrichi du vocabulaire de production (anglais américain).

**Fait — le projet a son dépôt** (2026-08-03) : la conception a quitté `conceptions/` et vit ici, dans `doc/conception/`, sous versionnage. **Les images ont une archive complète hors dépôt, `~/projects/gatebeast-assets/` : elle contient TOUT ce qui a été produit (403 Mo), rien n'est jamais perdu.** Le dépôt ne versionne que les images vivantes — les assets du POC et les six planches courantes ; les versions dépassées et les pages de revue reconstructibles restent dans l'archive seule. **À faire avant tout tir : les outils pointent encore vers l'ancien emplacement** (`conceptions/gatebeast/…`) et doivent être réajustés.

**Fait — la chaîne est outillée** (2026-08-03) : chemins des outils réparés après le déménagement (35 outils, plus deux pannes trouvées au passage : un générateur appelé sous un nom disparu, et une planche de référence déplacée qui cassait toute la mesure) ; **catalogue** écrit avec son module unique d'écriture, adressage et repli conformes à la conception ; **détourage** vers de la vraie transparence, rogné à la silhouette, avec mesure du point de pose ; **mesures étendues** (transparence effective, emprise mesurée contre emprise annoncée, raccord bord à bord, lumière). Validé sur les trois images du POC : détourage parfait, aucun magenta résiduel, silhouettes intactes. **Deux constats à traiter** : la tuile d'herbe **ne se raccorde pas** (jointure visible — elle a été produite sans contrainte de raccord) ; et les codes provisoires des trois sondes ne suivent pas les familles de l'inventaire.

**État image par image (2026-08-03, fin de session)** — tout est dans `assets/poc/`, chaque image ayant sa consigne figée à côté d'elle.

| Image | État |
|---|---|
| `CH-001` herbe rase | **validée par le propriétaire**. Première du projet à tenir le raccord bord à bord (bords opposés identiques au pixel près). Réserves non bloquantes : teinte vive et un peu citronnée, rythme de répétition perceptible sur les grandes étendues. |
| `OB-010_shape-ew` clôture est-ouest | **validée par le propriétaire**. Fond transparent, halo contenu, lumière dans la bande. |
| `OB-010_shape-ns` clôture nord-sud | Produite deux fois, **non soumise au propriétaire, aucun verdict de sa part**. L'agent principal la juge non conforme : elle ne ressemble pas à l'est-ouest. Versions conservées : `-v1` (première tentative) et `-avec-portillon` (essai est-ouest où un portillon est apparu). |
| `TR-060` chêne, `TR-062` herbe haute | **regénérées sur fond transparent, ni jugées ni inscrites au catalogue**. Le chêne montre beaucoup trop de racines apparentes — c'est **sa fiche** qui les demande, pas la consigne ; le propriétaire l'accepte pour l'instant. |
| `TR-061` bosquet, `TR-063` petit arbre, `CH-019` chemin, `BT-001` centre de soin | **à produire**. |

**Deux dettes à traiter** : le **catalogue** référence encore des fichiers supprimés et n'a pas été réécrit depuis la bascule vers la transparence ; la **page de suivi des sprites** (adresse ci-dessous) n'a pas été mise à jour depuis, et son vocabulaire dit encore « tir » au lieu de « génération d'image ».

**Fait — deux fautes de méthode de l'agent principal, corrigées** : une image **validée** a été écartée sous un nom la faisant passer pour ratée, puis remplacée par une moins bonne — les noms sont rétablis ; et plusieurs correctifs ont été appliqués sans validation préalable, alors que le protocole impose de proposer et d'attendre.

**Décisions de conception prises dans la journée, toutes écrites** : fond demandé **transparent** et **sans halo** (le magenta et le détourage sont abandonnés) ; un **tracé** — clôture, chemin, cours d'eau, mur — se décrit par **l'ensemble des bords qu'il relie** (`shape-ns`, `shape-ne`…), passe par le centre de sa case, et sa consigne dit qu'il est **une pièce d'assemblage** dont les éléments atteignent exactement ces bords ; la **consigne d'une image est figée** dès que l'image existe, un brouillon ne l'écrase jamais ; la **lumière** appartient au socle commun des consignes et les outils de correction **ne s'appliquent jamais d'office** ; la **définition demandée** est celle du maître, calculée par le service de conversion (double de la livraison, plafond 1536) ; **une case vaut 48 pixels**, seule valeur en pixels du projet, détenue par un **service unique** avec ses opérations. Vocabulaire : on dit **génération d'image**, jamais « tir ».

**Attention reprise : l'assistant « atelier-planches » a été perdu en cours de session** — son fil a disparu et il n'était plus joignable ; tout son acquis vit dans les fichiers. Leçon inscrite : un travail de fond se contrôle **à ses produits**, jamais à son silence.

**En cours — B0/B4.** Reste à faire, dans l'ordre : trancher la question de la cascade ; compléter l'inventaire des bâtiments de campagne et transcrire la fiche du personnage-joueur ; outiller la chaîne (catalogue, détourage, mesures étendues, jugement noté, planche-contact, composition depuis le catalogue) ; produire le lot v0 de la scène de référence. B2/B3 peuvent avancer en parallèle.

**Attention reprise : les assistants sont liés à leur session.** L'assistant « atelier-planches » de la session précédente n'est pas joignable depuis une nouvelle session : celle-ci crée le sien (même nom, même rôle, standard de [methode/execution.md](../conceptions/methode/execution.md)) et lui transmet tout l'acquis — qui vit intégralement dans les fichiers (scripts, consignes sauvegardées, rapports, ce suivi). Rien ne dépend de la mémoire d'un assistant.

## Organisation du travail

Un assistant persistant **« atelier-planches »** (Opus) exécute la production (consignes, tirs, mesures, rapports, page, publication) ; l'agent principal pilote (consignes du propriétaire, contrôle, redirection) — rôles et partage des acquis posés dans [methode/execution.md](../conceptions/methode/execution.md). Règles qui coûtent cher si on les oublie : une seule génération par version (garde-fou anti-doublon dans le code) ; aucune relance sans accord explicite ; publication planche par planche ; les questions ouvertes se reposent à chaque message ; une définition du propriétaire se transcrit telle quelle ; devant un écart, situer la faute (consigne ou production) en citant le texte exact.

## Standards de production en vigueur

Tous portés par la conception et le socle de code — ne pas les redécouvrir ici :

- **Format de composition** ([format-de-composition.md](doc/conception/referentiels/visuel/format-de-composition.md)) : grille 32×24, échelle debout 1,75–2 cases, desserte de tout bâtiment (règle globale), enclos = murs à intérieur visible, ravin = crevasse, arbres multi-cases, pin ≠ sapin, rien de construit en une case.
- **Socle de consigne** (`scripts/plate_common.py`, `PREAMBULE_FR` + rappel final) : consignes en français, style défini en texte (l'image d'aide ne fait autorité ni sur l'échelle ni sur la lumière), tailles en cases et rapports — jamais de pixels, humains « petits », rappel de taille près de chaque humain, fiches témoins citées mot pour mot, **prescription positive plutôt qu'interdit** (règle de rédaction par défaut, prouvée trois fois).
- **Lumière** : cible 115–130 de luminance, ≤ 10 % de sombre, toutes planches ([planches-de-reference.md](doc/conception/referentiels/visuel/planches-de-reference.md)).
- **Contrôles mécaniques** : `check-plate-prompts.py` (standard des consignes, bloque la génération), `build-plan-svg.py` (cohérence des plans), `analyze-plate.py` (mesures + verdict lumière), rapport noté par planche (score replié / détail déplié) affiché sur la revue — chaîne d'une planche : contrôle → génération → mesure → rapport → page → publication → suivi.
- **Fourchettes de charge par biome** (recalées sur mesures ; le plafond ne discrimine plus, porté à 100 — le trop-chargé se juge à l'œil) : P1 ≥ 70, P2 ≥ 65, P3 ≥ 62, P4 ≥ 48, P5 ≥ 60, P6 ≥ 55 (provisoire).

## Les six planches — versions courantes et scores

| Planche | Version | Score | À retenir |
|---|---|---|---|
| P1 campagne | v8 | 11/14 | meilleures mesures du lot, saturation 77,1 |
| P2 bourg | v7 | 12/13 | règle des ceintures pavées passée telle quelle |
| P3 contreforts | v6 | 10/14 | vrais pins obtenus ; bergerie encore sous emprise, raccord gauche absent |
| P4 marais | v8 | 13/14 | meilleur score ; escalier posé sur la passerelle |
| P5 falaise | v5 | 11/14 | escalier taillé enfin dessiné, charge remontée à 75,8 |
| P6 plage | v5 | 6/12 | un cran derrière (trop vide, chemins fantômes) — assumé |

Les cinq premières tiennent la cible de lumière et l'échelle humaine. Détail par planche : les **rapports** sous chaque planche de la revue.

## Améliorations individuelles en réserve (hors chemin du POC, décision propriétaire)

- **Fiches créatures qui dérivent vers l'animal réel** malgré les durcissements de consigne : SP-005, SP-007, SP-010, SP-011, SP-015 (+ dédoublements de SP-002/SP-017). Deux voies documentées : durcir les fiches elles-mêmes (révision refusée une première fois) ou corriger au cas par cas.
- **Saturation** sous la référence (52–62 contre 73) sur P2/P3/P5 — jamais attaquée de front ; P1 v8 (77,1) montre que c'est atteignable.
- **P6** restée en v5.
- **Contradiction non arbitrée** : l'image de référence DA mesure 103,5 de luminance — hors de la bande 115–130 exigée des planches ; une planche ne peut pas à la fois la reproduire et tenir la bande.

## Les outils

Tous dans `scripts/`, en anglais, exécutables depuis la racine du dépôt de travail.

| Script | Ce qu'il fait |
|---|---|
| `generate-planche-*.py` | Un fichier par passage de planche, conservés ; s'appuient sur `plate_common.py`. |
| `plate_common.py` | Socle de consigne français, fiches témoins, `shoot()` avec anti-doublon. |
| `check-plate-prompts.py` | Contrôle du standard des consignes ; bloque la génération en cas de faute. |
| `analyze-plate.py` | Mesures + verdict lumière contre les cibles. |
| `build-plan-svg.py` | Plans SVG des compositions + contrôle de cohérence (obstacles, dessertes). |
| `build-planches-page.py` | Page de revue (planches, plans, consignes, rapports, mobile). |
| `build-calibration-page.py` | Page des essais de calibration de l'échelle humaine. |
| `generate-humans-calibration-*.py` | Les quatre essais de calibration, conservés. |
| `measure-calibration*.py` | Mesure des figures des calibrations. |

Le générateur d'images est **l'agent Codex**, enveloppé par `scripts/generate-image.php`, désormais versionné avec le projet.

## Les deux pages de suivi du POC

Décidées avec le propriétaire ; elles remplacent les comptes rendus en conversation dès que la matière devient visuelle.

- **Le suivi des sprites** — tous les sujets groupés par type, chaque profil, chaque variante attendue avec son état (prévue, en production, produite, en défaut), un panneau de comptes en tête, et des actions par variante qui alimentent un récapitulatif copiable. C'est l'unique endroit où se lit l'état de la production.
- **Le parc** — le plan de composition en haut, la maquette montée en dessous, sur une seule page. Cible : pouvoir **sélectionner une zone** sur l'un ou l'autre et commenter cette zone, le commentaire partant au récapitulatif avec la zone désignée ([méthode](../conceptions/methode/revue-visuelle.md)).

## Les revues publiées

- **Planches de référence** (avec rapports par planche) — https://claude.ai/code/artifact/12a098f0-aecb-4326-8d4a-e60c80802413
- **Calibration de l'échelle humaine** — https://claude.ai/code/artifact/044dfac1-998d-4b36-87a5-639059ddba40
- Direction artistique (historique de la revue) — https://claude.ai/code/artifact/f5b1e6f7-ad28-4f72-9c41-f0a2cdfd38c5
- Son (essais, plafond constaté) — https://claude.ai/code/artifact/e0c55e5f-f179-4ef7-9338-9d2b2cc341b8

## Ce qui attend le propriétaire

- L'arbitrage du **lot v0** de la maquette B0.
- L'**envoi du dépôt vers GitHub** : l'enregistrement initial est fait en local, rien n'a été poussé.
- À terme : l'arbitrage de la contradiction lumière référence/bande, et le sort des fiches créatures dérivantes — tous deux hors chemin du POC.
