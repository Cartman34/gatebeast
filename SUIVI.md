# Suivi des travaux — GateBeast

**Intention :** permettre à n'importe quel intervenant de reprendre le travail sans perte. Ce document dit **où on en est**, pas ce que le jeu doit être — la cible vit dans la conception, le découpage en versions dans le [plan d'action](PLAN-ACTION.md).

Il se met à jour à chaque étape franchie. Il ne conserve pas d'historique : seul l'état courant compte (le versionnage garde le reste).

## Où en est le projet (2026-08-03)

**La direction artistique est VALIDÉE** (*toon volume*, figée sur les six planches de référence — décision et termes du propriétaire dans [visuel/index.md](doc/conception/referentiels/visuel/index.md)). **La conception est close** : [questions.md](doc/conception/questions.md) est vide. **Le POC est engagé** : le chemin vers la 0.1 est découpé en briques B0–B8 dans le [plan d'action](PLAN-ACTION.md), avec les décisions déjà prises — B0 maquette à sprites publiée en artefact Claude (hébergement du POC), B1 dépôt `git@github.com:Cartman34/gatebeast.git`, B3 moteur CSS, générateur d'images = agent Codex via le wrapper (capacités au [référentiel technique](doc/conception/referentiels/technique/index.md), limites des artefacts incluses).

**Fait — les 3 sondes d'assets sont tirées, mesurées, regardées et les constats écrits** au [référentiel technique](doc/conception/referentiels/technique/index.md) : le générateur rend un PNG carré de 1254 pixels, **sans transparence** (détourage obligatoire), avec un fond magenta uni à 99,9 % et un sujet plein cadre — donc parfaitement détourable ; une tuile de sol ressort régulière. L'angle obtenu est le bon — la vue standard des sprites, celle des six planches. **Un écart que la mesure ne voit pas** : le traitement varie d'un sujet à l'autre (créature en volume, humain en illustration).

**Fait — la couche assets est conçue** (2026-08-03) : modèle sujet / type / profil / variante, orientation dans le repère du monde, action, et une direction par partie qui pointe dans le repère du sujet (`north` = droit devant), images numérotées en dessous, repli déclaré, empilement à l'écran, lots par type, chaîne de production. Voir [rendu en calques](doc/conception/referentiels/technique/rendu-en-calques.md), [assets](doc/conception/referentiels/visuel/assets/index.md), [sujets et variantes](doc/conception/referentiels/visuel/assets/sujets-et-variantes.md) et le [lexique](doc/conception/referentiels/contenu/lexique.md) enrichi du vocabulaire de production (anglais américain).

**Fait — le projet a son dépôt** (2026-08-03) : la conception a quitté `conceptions/` et vit ici, dans `doc/conception/`, sous versionnage. **Les images ont une archive complète hors dépôt, `~/projects/gatebeast-assets/` : elle contient TOUT ce qui a été produit (403 Mo), rien n'est jamais perdu.** Le dépôt ne versionne que les images vivantes — les assets du POC et les six planches courantes ; les versions dépassées et les pages de revue reconstructibles restent dans l'archive seule. **À faire avant tout tir : les outils pointent encore vers l'ancien emplacement** (`conceptions/gatebeast/…`) et doivent être réajustés ; le générateur d'images, lui, reste hors dépôt (`~/projects/conceptions/methode/outils/generate-image.php`).

**En cours — B0/B4.** Reste à faire, dans l'ordre : compléter l'inventaire des bâtiments de campagne et transcrire la fiche du personnage-joueur ; outiller la chaîne (catalogue, détourage, mesures étendues, jugement noté, planche-contact, composition depuis le catalogue) ; produire le lot v0 de la scène de référence. B2/B3 peuvent avancer en parallèle.

**Attention reprise : les assistants sont liés à leur session.** L'assistant « atelier-planches » de la session précédente n'est pas joignable depuis une nouvelle session : celle-ci crée le sien (même nom, même rôle, standard de [methode/execution.md](../conceptions/methode/execution.md)) et lui transmet tout l'acquis — qui vit intégralement dans les fichiers (scripts, consignes sauvegardées, rapports, ce suivi). Rien ne dépend de la mémoire d'un assistant.

## Organisation du travail

Un assistant persistant **« atelier-planches »** (Opus) exécute la production (consignes, tirs, mesures, rapports, page, publication) ; l'agent principal pilote (consignes du propriétaire, contrôle, redirection) — rôles et partage des acquis posés dans [methode/execution.md](../conceptions/methode/execution.md). Règles qui coûtent cher si on les oublie : une seule génération par version (garde-fou anti-doublon dans le code) ; aucune relance sans accord explicite ; publication planche par planche ; les questions ouvertes se reposent à chaque message ; une définition du propriétaire se transcrit telle quelle ; devant un écart, situer la faute (consigne ou production) en citant le texte exact.

## Standards de production en vigueur

Tous portés par la conception et le socle de code — ne pas les redécouvrir ici :

- **Format de composition** ([format-de-composition.md](doc/conception/referentiels/visuel/format-de-composition.md)) : grille 32×24, échelle debout 1,75–2 cases, desserte de tout bâtiment (règle globale), enclos = murs à intérieur visible, ravin = crevasse, arbres multi-cases, pin ≠ sapin, rien de construit en une case.
- **Socle de consigne** (`scripts/plate_common.py`, `PREAMBULE_FR` + rappel final) : consignes en français, style défini en texte (l'image d'aide ne fait autorité ni sur l'échelle ni sur la lumière), tailles en cases et rapports — jamais de pixels, humains « petits », rappel de taille près de chaque humain, fiches témoins citées mot pour mot, **prescription positive plutôt qu'interdit** (règle de rédaction par défaut, prouvée trois fois).
- **Lumière** : cible 115–130 de luminance, ≤ 10 % de sombre, toutes planches ([planches-de-reference.md](doc/conception/referentiels/visuel/planches-de-reference.md)).
- **Contrôles mécaniques** : `check-plate-prompts.py` (standard des consignes, bloque le tir), `build-plan-svg.py` (cohérence des plans), `analyze-plate.py` (mesures + verdict lumière), rapport noté par planche (score replié / détail déplié) affiché sur la revue — chaîne d'une planche : contrôle → tir → mesure → rapport → page → publication → suivi.
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
| `check-plate-prompts.py` | Contrôle du standard des consignes ; bloque le tir en cas de faute. |
| `analyze-plate.py` | Mesures + verdict lumière contre les cibles. |
| `build-plan-svg.py` | Plans SVG des compositions + contrôle de cohérence (obstacles, dessertes). |
| `build-planches-page.py` | Page de revue (planches, plans, consignes, rapports, mobile). |
| `build-calibration-page.py` | Page des essais de calibration de l'échelle humaine. |
| `generate-humans-calibration-*.py` | Les quatre essais de calibration, conservés. |
| `measure-calibration*.py` | Mesure des figures des calibrations. |

Le générateur d'images est **l'agent Codex**, enveloppé par `../methode/outils/generate-image.php` (transverse).

## Les revues publiées

- **Planches de référence** (avec rapports par planche) — https://claude.ai/code/artifact/12a098f0-aecb-4326-8d4a-e60c80802413
- **Calibration de l'échelle humaine** — https://claude.ai/code/artifact/044dfac1-998d-4b36-87a5-639059ddba40
- Direction artistique (historique de la revue) — https://claude.ai/code/artifact/f5b1e6f7-ad28-4f72-9c41-f0a2cdfd38c5
- Son (essais, plafond constaté) — https://claude.ai/code/artifact/e0c55e5f-f179-4ef7-9338-9d2b2cc341b8

## Ce qui attend le propriétaire

- L'arbitrage du **lot v0** de la maquette B0.
- L'**envoi du dépôt vers GitHub** : l'enregistrement initial est fait en local, rien n'a été poussé.
- À terme : l'arbitrage de la contradiction lumière référence/bande, et le sort des fiches créatures dérivantes — tous deux hors chemin du POC.
