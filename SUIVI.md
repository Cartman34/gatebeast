# Suivi des travaux — GateBeast

**Intention :** permettre à n'importe quel intervenant de reprendre le travail sans perte. Ce document dit **où on en est**, pas ce que le jeu doit être — la cible vit dans la conception, le découpage en versions dans le [plan d'action](PLAN-ACTION.md).

Il se met à jour à chaque étape franchie. Il ne conserve pas d'historique : seul l'état courant compte (le versionnage garde le reste).

## Où en est le projet (2026-08-04)

**La direction artistique est VALIDÉE** (*toon volume*, figée sur les six planches de référence — décision et termes de l'opérateur dans [visuel/index.md](doc/conception/referentiels/visuel/index.md)). **La conception est close** : [questions.md](doc/conception/questions.md) est vide. **Le POC est engagé** : le chemin vers la 0.1 est découpé en briques B0–B8 dans le [plan d'action](PLAN-ACTION.md), avec les décisions déjà prises — B0 maquette à sprites publiée en artefact Claude (hébergement du POC), B1 dépôt `git@github.com:Cartman34/gatebeast.git`, B3 moteur CSS, générateur d'images = agent Codex via le wrapper (capacités au [référentiel technique](doc/conception/referentiels/technique/index.md), limites des artefacts incluses).

**Fait — les capacités du générateur sont constatées** : il rend **exactement la définition demandée** ; il rend un **vrai canal alpha**, vides encerclés compris, dès qu'on le demande — le fond magenta et le détourage ont donc été **abandonnés** ; l'angle obtenu est le bon, c'est la vue standard des sprites. **Deux limites** : le traitement varie d'un sujet à l'autre, et surtout il **n'exploite pas l'image de référence** qu'on lui fournit (voir ci-dessous).

**MAJEUR — la cascade ne fonctionne pas.** La règle de cohérence du projet veut qu'un variant se produise **à partir de la vue principale validée**, fournie comme référence visuelle. Le mécanisme est en place et l'image est bien déposée dans le répertoire de travail du générateur ; mais deux essais sur la clôture nord-sud, dont un avec une consigne disant en toutes lettres « exactement la clôture de l'image de référence, vue tournée d'un quart de tour », ont rendu **une autre clôture**. Deux générations de la même fiche donnent aussi deux chênes nettement différents. Ces images n'ont pas été soumises à l'opérateur : le jugement ci-dessus est celui de l'agent principal, pas un verdict de l'opérateur. Conséquence : rien ne garantit aujourd'hui la cohérence entre les variants d'un même sujet — les huit pièces de clôture, les quatre orientations d'un personnage, les poses d'une marche. **Décision à prendre avec l'opérateur avant toute production de variants.**

**Fait — la couche assets est conçue** (2026-08-03) : modèle sujet / type / profil / variant, orientation dans le repère du monde, action, et une direction par partie qui pointe dans le repère du sujet (`north` = droit devant), images numérotées en dessous, repli déclaré, empilement à l'écran, lots par type, chaîne de production. Voir [rendu en calques](doc/conception/referentiels/technique/rendu-en-calques.md), [assets](doc/conception/referentiels/visuel/assets/index.md), [sujets et variants](doc/conception/referentiels/visuel/assets/sujets-et-variantes.md) et le [lexique](doc/lexique.md) enrichi du vocabulaire de production (anglais américain).

**Fait — le projet a son dépôt** (2026-08-03) : la conception a quitté `conceptions/` et vit ici, dans `doc/conception/`, sous versionnage. **Les images ont une archive complète hors dépôt, `~/projects/gatebeast-assets/` : elle contient TOUT ce qui a été produit (403 Mo), rien n'est jamais perdu.** Le dépôt ne versionne que les images vivantes — les assets du POC et les six planches courantes ; les versions dépassées et les pages de revue reconstructibles restent dans l'archive seule. **À faire avant tout tir : les outils pointent encore vers l'ancien emplacement** (`conceptions/gatebeast/…`) et doivent être réajustés.

**Fait — la chaîne est outillée** (2026-08-03) : chemins des outils réparés après le déménagement (35 outils, plus deux pannes trouvées au passage : un générateur appelé sous un nom disparu, et une planche de référence déplacée qui cassait toute la mesure) ; **catalogue** écrit avec son module unique d'écriture, adressage et repli conformes à la conception ; **détourage** vers de la vraie transparence, rogné à la silhouette, avec mesure du point de pose ; **mesures étendues** (transparence effective, emprise mesurée contre emprise annoncée, raccord bord à bord, lumière). Validé sur les trois images du POC : détourage parfait, aucun magenta résiduel, silhouettes intactes. **Deux constats à traiter** : la tuile d'herbe **ne se raccorde pas** (jointure visible — elle a été produite sans contrainte de raccord) ; et les codes provisoires des trois sondes ne suivent pas les familles de l'inventaire.

**État image par image (2026-08-03, fin de session)** — tout est dans `assets/poc/`, chaque image ayant sa consigne figée à côté d'elle.

| Image | État |
|---|---|
| `CH-001` herbe rase | **validée par l'opérateur**. Première du projet à tenir le raccord bord à bord (bords opposés identiques au pixel près). Réserves non bloquantes : teinte vive et un peu citronnée, rythme de répétition perceptible sur les grandes étendues. |
| `OB-010_shape-ew` clôture est-ouest | **validée par l'opérateur**. Fond transparent, halo contenu, lumière dans la bande. |
| `OB-010_shape-ns_posts-1` clôture nord-sud | Produite avec **l'exemple d'usage en référence** et un seul poteau. Les deux tentatives précédentes ont été **supprimées sur ordre de l'opérateur** (elles restent dans l'historique). Pas encore jugée. |
| `usage-OB-010` et `-v2` — exemple d'usage | Deux versions, la seconde suivant mieux le plan après correction de la consigne (énumération en coordonnées, plan SVG fourni, interdiction de symétriser). **La v2 fixe le style des bûches** (décision de l'opérateur) : l'est-ouest validée et la nord-sud sont donc à refaire dans ce style. |
| `TR-060` grand chêne, `TR-062` herbe haute | **regénérées sur fond transparent, ni jugées ni inscrites au catalogue**. Le chêne montre beaucoup trop de racines apparentes — c'est **sa fiche** qui les demande, pas la consigne ; l'opérateur l'accepte pour l'instant. |
| `TR-061` bosquet de sapins, `TR-063` pommier, `CH-019` chemin de terre battue, `BT-001` centre de soin | **à produire**. Le pommier et le bosquet de sapins ont été **renommés et entièrement réécrits** le 2026-08-04 : leurs anciennes fiches décrivaient un « petit arbre » et un « bosquet dense » sans essence. |

**Décisions du 2026-08-04, toutes écrites dans la conception.** On dit **opérateur**, jamais « propriétaire » (terme banni, [glossaire de la méthode](../conceptions/methode/glossaire.md)). Les **types sont fins** — un type regroupe ce qui s'échange sans incohérence : herbe, arbre, bosquet d'arbres, clôture, chemin, et non « végétation ». Le **passage** d'un sujet se déclare **côté par côté**, jamais il ne se déduit d'une forme : tout se traverse par défaut, un type peut renverser cette valeur, et **trois niveaux** — type, sujet, variant — se surchargent en ne portant que ce qu'ils définissent ; fermer deux côtés adjacents ferme ce qui est entre eux ; l'inventaire se revalide à chaque ajout. Le **catalogue est gelé** : un fichier neuf le remplacera, construit autour des **types, sujets, variants et représentations** — la sprite n'étant qu'une représentation parmi d'autres. Le **lexique** a quitté la conception pour `doc/lexique.md`, **biome** y est défini, et les **humains** sont réunis à l'inventaire sous `HU-nnn` — il n'y a pas de sujet « personnage-joueur ».

**Nouvel outil — le plan de composition** ([sa fiche](doc/outils/plan-de-composition.md)) : `scripts/build-composition-plan.py` rend un plan à plat depuis un JSON déclaratif qui *est* le plan, avec des contrôles qui bloquent. Le moteur partagé est `scripts/composition_plan.py`. Premier plan produit : `assets/poc/cloture/plan-composition-OB-010-usage.json` — carré fermé, croix centrale, quatre antennes, les quinze formes de tracé exercées.

**Les deux dettes sont soldées** (2026-08-04) : le **catalogue** est **gelé** — ni lu, ni écrit, ni supprimé — et remplacé par `assets/sujets.json`, le référentiel des sujets ; la **page de suivi des sprites** part désormais du disque, montre toute image existante, et pèse 0,47 Mo au lieu de 10,3.

**La chaîne tient de bout en bout** (2026-08-04) : plan de composition déclaratif et contrôlé → consigne assemblée par outil, jamais à la main → génération → **export** à la définition de livraison → référentiel des sujets → suivi publié. Le **rognage est abandonné** : on corrige la consigne, jamais l'image.

**Fait — deux fautes de méthode de l'agent principal, corrigées** : une image **validée** a été écartée sous un nom la faisant passer pour ratée, puis remplacée par une moins bonne — les noms sont rétablis ; et plusieurs correctifs ont été appliqués sans validation préalable, alors que le protocole impose de proposer et d'attendre.

**Décisions de conception prises dans la journée, toutes écrites** : fond demandé **transparent** et **sans halo** (le magenta et le détourage sont abandonnés) ; un **tracé** — clôture, chemin, cours d'eau, mur — se décrit par **l'ensemble des bords qu'il relie** (`shape-ns`, `shape-ne`…), passe par le centre de sa case, et sa consigne dit qu'il est **une pièce d'assemblage** dont les éléments atteignent exactement ces bords ; la **consigne d'une image est figée** dès que l'image existe, un brouillon ne l'écrase jamais ; la **lumière** appartient au socle commun des consignes et les outils de correction **ne s'appliquent jamais d'office** ; la **définition demandée** est celle du maître, calculée par le service de conversion (double de la livraison, plafond 1536) ; **une case vaut 48 pixels**, seule valeur en pixels du projet, détenue par un **service unique** avec ses opérations. Vocabulaire : on dit **génération d'image**, jamais « tir ».

**Attention reprise : l'assistant « atelier-planches » a été perdu en cours de session** — son fil a disparu et il n'était plus joignable ; tout son acquis vit dans les fichiers. Leçon inscrite : un travail de fond se contrôle **à ses produits**, jamais à son silence.

**En cours — B0/B4.** La chaîne est outillée de bout en bout et tourne. Reste à produire le lot v0 de la scène de référence, puis à composer le parc. B2/B3 peuvent avancer en parallèle. **Le personnage-joueur n'est pas un sujet à part** : il n'y a que des humains, et il pourrait être n'importe lequel (opérateur, 2026-08-04).

## Ce qui a changé le 2026-08-05 dans le modèle et l'outillage

**Une seule commande produit une sprite** : `scripts/generate-sprite.py <ref du sujet> <ref du variant>`. Les deux commandes précédentes n'en font plus qu'une — celle qui ne savait produire que la vue principale est supprimée, et le mot **tracé** est banni : la notion n'a jamais existé, c'était un dessin SVG qui ne passait pas par le générateur.

**Un variant se désigne par sa ref**, écrite dans le référentiel et jamais recomposée : `OB-010 / orientation-south_action-idle_shape-ew_gate-open_frame-01`. Tous les outils s'y réfèrent par elle. Le mot **adresse** est banni pour cet usage.

**On ne parle au générateur qu'en cases.** La correspondance — une case vaut 96 pixels dans le fichier, 24 à l'écran — est donnée une fois dans le socle des consignes, et ces deux valeurs sont écrites une fois dans la conception et une fois dans le code. Le doublement en trop est supprimé : le maître se produit à 96 par case, plus 192.

**Toute génération va jusqu'au bout** : consigne, génération, export, inscription au référentiel, rapport. Plus rien ne peut être produit puis oublié.

**Les traces d'exécution ont quitté `assets/`** : rapports et journaux du générateur vivent sous `var/generations/sprites/` et `var/generations/subjects/`, non versionnés.

**Toutes les versions sont gardées et versionnées ; la page n'en montre que trois** — la courante et les deux précédentes.

## Relevé du propriétaire — 2026-08-05, second passage

**Validées, cinq** : `TR-060` grand chêne, `BT-001` centre de soin en vue principale, `BT-002` maison de ferme en vue principale et ses propositions `p2` et `p3`.

**À reprendre, six** : les trois portillons `OB-010` — est-ouest fermé, est-ouest ouvert, nord-sud fermé —, le sapin `TR-065`, le bosquet `TR-061`, l'herbe clairsemée `TR-064` en densité `dense`.

| Sujet | Ce que dit l'opérateur | Ce que j'en fais |
|---|---|---|
| `OB-010` est-ouest, fermé et ouvert | « Y'a pas d'herbe en bas des poteaux mais sinon ok » | Clair : ajouter l'herbe au pied des poteaux, ne toucher à rien d'autre. |
| `OB-010` nord-sud fermé | « Il est raté » | **Zone d'ombre** : rien ne dit sur quel point. À demander avant de relancer. |
| `TR-063` pommier | « 4 pommes max sur ce variant » | Clair : la fiche disait « une dizaine tout au plus », elle dira quatre au plus. |
| `TR-065` sapin | « Ce n'est toujours pas ce que j'ai demandé, si tu ne comprends pas, demande-moi. Je t'ai donné les exemples. » | **Zone d'ombre, et c'est la troisième tentative** : à demander plutôt qu'à retenter à l'aveugle. |
| `TR-061` bosquet | Premier passage : « il faut des buissons qui correspondent à ce qu'on voit en forêt, n'invente pas une masse […] des fougères et/ou des ronces ». Après la reprise : **« Un peu trop dense, pas assez inquiétant encore »** | La fiche a gagné ses fougères et ses ronces ; il reste à **desserrer** le sous-bois et à **accentuer l'inquiétant** — l'un ne vient pas de l'autre, c'est un sous-bois plus ouvert mais plus sombre qu'il faut. |
| `TR-062` herbe haute | « Bien mais propose 2 autres herbes hautes (nouveaux sujets) » | Clair : deux sujets à créer à l'inventaire, puis à produire. |
| `TR-064` herbe clairsemée | « En fait, variante avec x4 herbes ! » | Clair : une variante à quatre touffes. |
| `BT-001` centre de soin | « Il est très bien mais je veux que tu fasses des variants juste pour avoir 3-4 propositions. Donc une qui revient aux couleurs de la version précédente » (réf. `assets/revue-da/da-b4-r15-scene.png`) | Fait : `p2` et `p3` produites ; reste à trancher entre elles. |

## Relevé sur le plan du parc — 2026-08-05, second passage

| Case | Ce que dit l'opérateur | Ce que j'en fais |
|---|---|---|
| (25,1) | « Ajouter un bosquet ici » | Un bosquet de sapins de plus dans la ligne du fond. |
| (35,11) à (64,7) | Le cours d'eau continue : points 4 à 11 — (35,11), (40,11), (40,10), (45,10), (45,9), (55,9), (55,7), (64,7). « Cette barrière et celles au-dessus sautent » | Prolonger le tracé point par point jusqu'au bord est, et **supprimer les barrières que le cours d'eau traverse ainsi que celles au-dessus**. |
| (56,35) | « Y'a une bande hor de vide à compléter par ici » | Une bande nue à combler — semis d'herbe comme le reste du parc. |
| (24,46) | « Ajouter pommier ici » | Un pommier de plus. |
| (28,7) | « J'ai dit de l'herbe autour du cours d'eau mais 2 cases pleines, ça fait beaucoup, faut garder un peu d'aléatoire. Par contre, un peu plus d'herbe haute par occasion » | Les berges se desserrent : plus de bande continue de deux cases, un tirage aléatoire — et **plus d'herbe haute** dans ce qui reste. |
| (21,45) | « La zone d'herbes hautes est coupée par la barrière, c'est ok mais en dessous de la barrière, il faut enlever cette partie de zone d'herbes hautes et revenir à un pattern normal » | Sous la barrière, la nappe cesse : on revient au semis ordinaire. |

## Fait le 2026-08-05, en fin de séance

**La maquette du parc est montée** : `artefacts/parc/monter.php` lit le plan, demande au référentiel l'image courante de chaque sujet **selon la forme que la case déclare**, et pose tout à l'échelle du monde. Le sol de la cellule par défaut est carrelé sur toute la scène. Trois boutons font varier la case entre 24, 32 et 48 pixels — le zoom ne change que cette valeur, jamais les images. L'outil de revue y est le même que sur le plan, dupliqué et adapté puisque la scène est posée en pixels et non dans un repère SVG ; **les deux doivent converger un jour**.

**Les calques existent** : un plan accepte désormais deux sujets sur une même case tant que l'un des deux se pose **à plat** — sol, chemin, herbe, cours d'eau. Deux sujets qui se dressent restent refusés. C'est ce qui permet à un chemin de passer sous un bâtiment et d'atteindre une porte qui ne tombe jamais sur le bord bas de sa sprite.

**Le contrôle des couverts est écrit** : `scripts/check-plan-couverts.php`, indépendant, lancé à la main après un nouveau plan ou une grosse modification, et **il ne bloque rien**. Il nomme le type de chacun des deux sujets en cause, ce qui permet de juger si le constat est réel — c'est ce qui manquait quand il a fait déplacer une rivière pour préserver un chêne.

**Le sapin et le pommier** ont vu leurs fiches corrigées en profondeur ; le chemin aussi, sa couleur passant du sable doré à un **ocre brun terreux** — la fiche disait terre battue et décrivait du sable.

## La pile — ce qui reste à faire, dans l'ordre où je le dépile

**C'est ici que tout entre.** Une demande de l'opérateur, un défaut que je constate, une remarque en passant : rien ne reste dans la conversation. Le contexte se résume et se perd ; cette liste, non. Tant qu'une ligne est ici, elle est due.

**Une capture d'écran s'écrit avant d'être traitée, toujours** : ce que j'y vois est noté en toutes lettres, même si l'image parle d'elle-même — une image ne survit pas au résumé du contexte, sa description si. Et **quand ce qu'elle montre ne suffit pas à savoir quoi faire, je le dis dans la ligne** : j'écris ce que je vois, puis mon appréciation et ce qui me manque pour agir. C'est à l'opérateur de trancher, pas à moi de deviner — mais c'est à moi de repérer le manque et de le nommer, plutôt que de partir sur une hypothèse et de produire à côté.

### Production

1. **Les quatre arbres relancés le 2026-08-05**, à juger : `TR-060` chêne `v5`, `TR-063` pommier `v6`, `TR-065` sapin `v8`, `TR-061` bosquet `v7`. Tous produits avec la planche de campagne en référence.
2. **`BT-002` maison de ferme `p3`** — trois tentatives, trois fois la même silhouette. La référence de scène impose son pignon ; à relancer sans elle.
3. **`BT-001` centre de soin** — `p2` et `p3` sortis face à la caméra ; reste à trancher la palette, `p3` étant sortie verte alors que sa fiche demande une palette chaude.
4. **`OB-010` portillons** — « pas d'herbe en bas des poteaux mais sinon ok » : l'herbe au pied manque, le reste est bon.
5. **`TR-062` herbe haute** — deux nouveaux sujets d'herbe haute à créer à l'inventaire, puis à produire.
6. **`TR-064` herbe clairsemée** — une variante à quatre herbes est demandée.
7. **`CH-019` chemin** — couleur encore trop jaune ; sa fiche dit « terre battue » et décrit du sable clair, à trancher.
8. **`CH-020` cours d'eau** — angle de caméra à reprendre, fiche pas encore revue.

### Page des sprites — défauts en attente

**Capture du 2026-08-05** : sur une image commentée, la barre d'actions ne montre que « À reprendre », « Écarter » et « + ». **Le bouton de validation a disparu.** L'opérateur : « je ne peux pas valider un variant quand j'ai fait une remarque dessus, peut-être que la condition est autre, mais le bouton ne doit jamais être bloqué ». Les actions offertes dépendent aujourd'hui de l'état courant — l'image est à reprendre, donc la validation n'est pas proposée. À corriger : **toutes les actions restent toujours offertes**, l'opérateur change d'avis quand il veut.

**Capture du 2026-08-05, second point** : le bouton « + » qui déplie le commentaire reste rose une fois replié, ce qui signale bien qu'un texte est écrit dessous — mais **rien ne permet d'effacer ce texte d'un clic**. L'opérateur veut une solution **sans perte** : effacer doit rester rattrapable, pas détruire ce qu'il vient d'écrire.

**Le plan d'usage du chemin sort à plat, et on sait enfin pourquoi** (échange de l'opérateur avec l'agent générateur, 2026-08-05). Deux causes, toutes deux dans la fiche :

1. **La fiche dit « une bande de terre battue » là où le sujet est un CHEMIN de terre battue.** Le générateur dessine ce qu'on nomme : on lui demande une bande, il rend une bande — « on obtient une brioche au lieu d'un chemin » (opérateur). Le nom du sujet ne se paraphrase pas.
2. **Deux clauses contredisent frontalement la caméra** : « ABSOLUMENT PLATE […] aucune épaisseur, aucune tranche visible » et « aucune perspective, aucun point de fuite, aucun rétrécissement des rangées du fond ». Le générateur les a lues comme une commande de vue orthographique verticale, et a aplati la matière au lieu de garder la projection à 70°. Il l'a dit lui-même. L'intention de ces clauses reste juste — un chemin n'est pas un objet posé en relief — mais elle doit s'écrire sans nier l'angle de prise de vue.

**Capture du 2026-08-05, la page prend trop de place.** Un type entier — « Sol », un seul sujet, une seule image validée — occupe la hauteur d'un écran : titre du type, carte du sujet, emprise et couvert, la variante, son état écrit deux fois, ses boutons. **Deux demandes de l'opérateur :** un sujet dont tout est validé doit se réduire à une vignette dans une **grille compacte de sujets** ; et même déplié, l'ensemble doit tenir dans beaucoup moins de hauteur.

**L'écart entre l'entrée d'un bâtiment et le bas de sa sprite — vaut pour TOUS les bâtiments** (opérateur, 2026-08-05, capture du centre de soin). La porte ne tombe pas sur le bord bas de l'image : le porche, les massifs et le socle descendent en dessous d'elle. Un chemin posé au ras de la sprite s'arrête donc à une ou deux cases de la porte, et rien ne les relie.

**Solution retenue par l'opérateur** : autoriser des cases de chemin **sous le bâtiment**. Le sol se dessine d'abord, le bâtiment se pose par-dessus, et le chemin peut alors remonter jusqu'à la porte quelle que soit la hauteur à laquelle elle se trouve dans l'image.

**Ce que ça implique, et qui n'existe pas encore** : un plan refuse aujourd'hui deux sujets sur une même case — c'est même son seul contrôle d'occupation. Il faudra que la déclaration porte des **calques** : une case peut avoir un sol ET un volume posé dessus. Le rendu en calques est déjà la façon dont le jeu affiche la carte, donc la conception ne s'y oppose pas ; c'est le format du plan qui est à étendre. **Rien n'est engagé là-dessus.**

**LA CLAUSE D'UN VARIANT N'ARRIVE PAS AU GÉNÉRATEUR — défaut d'outillage, constaté le 2026-08-05 en fin de séance.** Vérifié sur la consigne réellement envoyée pour `TR-064` en densité `dense` (`var/generations/sprites/TR-064_densite-dense-v4-rapport.md`) : elle ne porte **aucun mot** de la description propre à `dense`, seulement la description de base du sujet. Les trois tentatives successives ne pouvaient donc que redonner une herbe clairsemée, quelle que soit la fiche.

**Ce que ça invalide** : chaque fois qu'une variante est sortie « identique à la précédente », la cause a pu être celle-là et non le modèle ni la formulation — les propositions `p2` et `p3` des bâtiments sont à re-vérifier sous cet angle. **C'est le premier point à traiter à la reprise** : sans lui, toute variante produite est en réalité une vue principale.

### Outillage

9. **Le score n'est pas encore relié à un verdict** : il mesure, il s'affiche, mais rien n'en découle automatiquement.
10. **L'évaluation ne couvre que ce qui se compte** — fond, emprise, lumière, raccord, régularité. Ce qui relève du jugement reste à l'œil de l'opérateur depuis que l'agent qui jugeait a été débranché.
11. **`scripts/check-asset-prompt.py` est en panne** : il s'arrête sur un fichier absent. À remettre en marche.

### Défauts de la page des sprites, signalés et corrigés le 2026-08-05

Le bouton d'information sans son mot, le champ de commentaire qui s'ouvre sur deux lignes et grandit jusqu'à quatre, le score revenu à sa source, la pastille réduite à deux mots, le détail des critères passé en popin avec mesure et attendu. **Tous corrigés et publiés.**

## Registre des sujets

**Le suivi guide, il ne fait pas foi : la vérité est sur le disque** (opérateur, 2026-08-05). Tout sujet donné par l'opérateur entre ici avec son numéro, sa référence, son titre et son statut ; le registre se met à jour à chaque échange.

| N° | Référence | Titre | Statut |
|---|---|---|---|
| 1 | `outil-production-datee` | Génération horodatée, étapes datées et chronométrées, rapport de validation écrit à côté de l'image | fait — `scripts/production_report.py`, câblé au générateur de tracés |
| 2 | `consigne-supplementaire-sujet` | Consigne supplémentaire par sujet, fiche et référentiel, les deux au rapport | fait |
| 3 | `formulaire-revue-image` | Le formulaire de revue se vide quand l'image change | fait |
| 4 | `commentaire-quatre-lignes` | Champ de commentaire jusqu'à quatre lignes puis défilement | fait |
| 5 | `portillon-deux-poteaux` | Portillons à deux poteaux, est-ouest, fermé et grand ouvert à 135° | produits, en attente de verdict |
| 6 | `angle-camera-perdu` | L'angle de caméra manque aux générations | rappel de caméra ajouté ; sans effet sur le chemin |
| 7 | `hauteur-a-l-inventaire` | Hauteur totale obligatoire à l'inventaire, règle à écrire dans la conception | à écrire |
| 8 | `maquette-parc` | Maquette du parc, 64 × 48 cases, centre de soin | trois plans de composition proposés le 2026-08-05, un seul à retenir |
| 9 | `sprite-principal-en-tete` | Le sprite principal d'un sujet se démarque et passe en tête de liste | à faire |
| 10 | `ch-019-matiere` | La fiche du chemin dit « terre battue » et décrit du sable clair | à trancher |
| 11 | `bt-001-toit` | Centre de soin trop austère, décor de toit à proposer (puits de lumière ?) | à proposer |
| 12 | `bt-002-maison-ferme` | Maison de ferme d'après `da-b4-r15-scene.png` | à produire |
| 13 | `sapins-tronc-visible` | Sapin isolé et bosquet : tronc visible exigé | fiches à corriger |
| 14 | `tr-060-racines` | Trop de racines apparentes sur le grand chêne | fiche à corriger |
| 15 | `tr-063-herbe` | Le pommier arrive avec de l'herbe au sol ; le sol seul l'apporte | fiche à corriger |
| 16 | `tr-064-case-carree` | L'herbe clairsemée rend une case ronde au lieu d'une case carrée | consigne à corriger |
| 17 | `tr-062-herbe-moins-touffue` | Ajouter un sujet d'herbe moins touffu | sujet à créer, décision de l'opérateur |
| 18 | `ob-010-nw-deux-lisses` | L'angle nord-ouest montre deux lisses à la verticale au lieu d'une | consigne à corriger |
| 19 | `reference-laissee-dans-assets` | Une planche de référence reste copiée dans le dossier des assets après génération | à corriger |
| 20 | `record-asset-casse` | L'inscription au référentiel s'arrête en erreur : elle réclame des mesures du rognage abandonné | fait |
| 21 | `couvert-du-sujet` | Emprise au sol et couvert : deux étendues distinctes, le couvert valant l'emprise par défaut | fait — écrit dans la conception, porté au référentiel et à la page |
| 22 | `modele-de-generation` | Choix du modèle de génération, bout en bout, inscrit au rapport | fait — `gpt-5.6-terra` en service |
| 23 | `session-du-generateur` | Identifiant de session du générateur remonté au rapport, avec le dossier pour la rouvrir | fait |
| 24 | `generateur-recursif` | Le générateur exécutait l'outillage du dépôt au lieu de dessiner | fait — consigne d'illustrateur ajoutée |
| 25 | `puc-invisible` | L'exemple d'usage du chemin ne s'affiche pas dans la visionneuse | **en défaut** — tout est en place côté page, la cause est à voir en console |
| 26 | `icone-info` | L'icône d'information s'affiche comme un carré vide | **en défaut** — redessinée deux fois, à reconstater |
| 27 | `mot-axe-banni` | Le mot banni vit encore dans le code et dans le référentiel, en anglais | à trancher — le renommage touche plusieurs outils et le fichier des sujets |
| 28 | `sprites-orphelins` | Trois premières versions gardées sur le disque mais retirées du référentiel par la limite de trois antérieures | à trancher — « rien ne se jette » contre « aucun livrable orphelin » |
| 29 | `sapin-v6-non-inscrit` | Le sapin `v6` a été produit et jamais inscrit | à faire — simple oubli, aucun arbitrage |
| 30 | `variants-demandees` | Trois densités d'herbe et trois propositions par bâtiment, déclarées et décrites, jamais produites | densités `medium` et `dense` et propositions `p2` produites le 2026-08-05 |
| 31 | `sapin-couleur-perdue` | Ma correction du sapin a éclairci la couleur que la version précédente avait obtenue | fiche à reprendre |
| 32 | `referentiel-ecrase-en-parallele` | Deux générations lancées ensemble s'effacent l'une l'autre au référentiel | proposé, en attente de décision |
| 33 | `couvert-non-lu-a-l-export` | La génération demande la largeur du couvert, l'export vérifie celle de l'emprise | proposé, en attente de décision |

## Suivi des sprites, sujet par sujet (2026-08-05)

**Verdicts de l'opérateur, portés au référentiel et lisibles sur la page.**

| Sujet | Où il en est | Ce qui reste |
|---|---|---|
| `CH-001` herbe rase | validée | écart avec l'ébauche sur les fleurs, à trancher |
| `CH-019` chemin | produite, en attente de verdict | son exemple d'usage ne s'affiche pas ; couleur encore jaune |
| `CH-020` cours d'eau | à reprendre | l'angle de caméra ; fiche pas encore revue |
| `OB-010` clôture | six formes validées, deux portillons est-ouest validés | herbe au pied des poteaux ; portillons nord-sud et angle nord-ouest à juger |
| `TR-060` grand chêne | à reprendre | couvert à augmenter pour retrouver le chêne de la référence |
| `TR-061` bosquet de sapins | `v6` produite le 2026-08-05, inscrite | en attente de verdict |
| `TR-062` herbe haute | validée | un second sujet d'herbe moins touffue, décision de l'opérateur |
| `TR-063` pommier | produite, en attente de verdict | couvert 3 × 3 en place |
| `TR-064` herbe clairsemée | densités `medium` et `dense` produites le 2026-08-05, inscrites | en attente de verdict ; la densité `sparse` reste à juger |
| `TR-065` sapin | **génération perdue** | l'image est bien sortie, l'export l'a refusée — voir « Deux défauts constatés le 2026-08-05 » |
| `BT-001` centre de soin | proposition `p2` produite le 2026-08-05, inscrite | en attente de verdict |
| `BT-002` maison de ferme | proposition `p2` produite le 2026-08-05, inscrite | en attente de verdict |

## Relevé du propriétaire du 2026-08-05 — verdicts et commentaires, rien n'est encore engagé

**Un défaut de la page est signalé au passage, et il est bloquant** : sur `BT-002` variant `p2`, l'opérateur ne peut plus valider l'image. À reproduire et à corriger avant tout autre travail sur cette page.

**À produire** — `BT-001` proposition `p3`, `BT-002` proposition `p3`. **Validée** — `BT-002` proposition `p2`.

**À reprendre**, neuf : les deux portillons est-ouest de `OB-010` (ouvert et fermé), le grand chêne `TR-060`, le pommier `TR-063`, le sapin `TR-065`, le bosquet `TR-061`, l'herbe clairsemée `TR-064` en densité `dense`, le centre de soin `BT-001` en version principale et en proposition `p2`.

Les commentaires, sujet par sujet, tels que donnés :

| Sujet | Ce que dit l'opérateur |
|---|---|
| `OB-010` portillons fermé et ouvert | « Y'a pas d'herbe en bas des poteaux mais sinon ok » — le reste est bon, seule l'herbe au pied manque. |
| `TR-060` grand chêne | « Il doit être grand, faut augmenter son couvert ! » |
| `TR-063` pommier | « Tu as perdu la notion du nombre de pommes, on avait dit quelques pommes […] Une consigne ne doit pas annuler une autre ! » — régression déjà constatée, la règle est écrite à la conception des assets. |
| `TR-065` sapin | « Ma demande n'a pas été respectée ! J'ai demandé un arbre COMME celui de `assets/revue-da/planche-p1-campagne-v8.png` (en haut à gauche) » — un aperçu avait été fourni pour s'en inspirer. |
| `TR-061` bosquet | « ça a régressé, c'est moins bien qu'avant. Ma demande n'a pas été respectée !! » |
| `TR-062` herbe haute | « Bien mais propose 2 autres herbes hautes (nouveaux sujets) » — deux sujets à créer à l'inventaire. |
| `TR-064` herbe clairsemée | « En fait, variante avec x4 herbes ! » |
| `BT-001` centre de soin | « Il est très bien mais je veux que tu fasses des variants juste pour avoir 3-4 propositions. Donc une qui revient aux couleurs de la version précédente » (réf. `assets/revue-da/da-b4-r15-scene.png`). |
| `BT-001` proposition `p2` | « L'orientation est mauvaise mais le style est bon. » |
| `BT-001` proposition `p3` | « Le centre de soin doit faire face à la caméra, adapte la description. Le style doit se rapprocher de `cutout/batiment/BT-001-v2.png` mais avec les mêmes contraintes de toiture que les autres. » |
| `BT-002` maison de ferme | « Elle est très bien mais je veux que tu fasses des variants juste pour avoir 3-4 propositions. Donc une qui revient aux couleurs de la version réf. DA `assets/revue-da/da-b4-r15-scene.png` » + **le défaut de validation ci-dessus**. |
| `BT-002` proposition `p2` | « Bien mais en terme de forme, c'est trop proche de la première. » |
| `BT-002` proposition `p3` | « proposer une autre forme ! » |

## Deux défauts constatés le 2026-08-05, aucun correctif appliqué

Six générations ont été lancées **en parallèle**. Cinq sont allées jusqu'à l'inscription ; la sixième, le sapin, a
échoué à l'export. Les deux défauts qui suivent sont des **propositions**, rien n'a été touché.

1. **Deux générations qui tournent ensemble peuvent s'effacer l'une l'autre au référentiel.** Chaque inscription
   relit `assets/sujets.json` en entier au moment où elle démarre, puis le réécrit en entier quand elle finit : tout
   ce qui a été écrit entre-temps — par une autre génération ou à la main — disparaîtrait sans un mot. **Rien de tel
   n'a été constaté** : les cinq inscriptions du 2026-08-05 sont toutes en place. C'est un risque du mécanisme, pas
   un dégât observé — j'ai d'abord cru le couvert du sapin perdu ainsi, il ne l'était pas. **Proposition :** relire
   le fichier au moment d'écrire, et non au démarrage, pour ne réécrire que l'entrée concernée.
2. **La dimension demandée et la dimension vérifiée ne sont pas lues au même endroit.** La génération demande la
   largeur du **couvert** — ce que le volume surplombe —, tandis que l'export vérifie la largeur de l'**emprise** —
   ce qui touche le sol. Tout sujet dont le volume déborde de son pied échoue donc systématiquement, alors que
   l'image reçue est juste. **Proposition :** faire lire le couvert à l'export, exactement comme la génération.

**Conséquence immédiate :** le sapin doit être relancé une fois le second point tranché. Son couvert de 2 × 2 est
bien déclaré et son image est sortie juste, à 192 px de large ; c'est l'export qui l'a refusée en la mesurant
contre l'emprise de 1 × 1, et rien ne l'a donc inscrite.

## Le plan de composition du parc — trois propositions écrites le 2026-08-05

**La scène est neuve, décidée par l'opérateur** : format paysage, bosquets de sapins dans le fond, centre de soin
dans le coin bas-droit, son entrée face à la caméra et prolongée de **trois cases de chemin — le seul chemin du
parc**, aucun autre. Le reste est de l'herbe et des arbres **épars, irrégulièrement placés**. Aucun enclos n'a été
demandé, aucun n'a été posé. Trois plans ont été écrits, vérifiés et dessinés ; **aucun n'est retenu, la décision
appartient à l'opérateur**.

**Le plan A est retenu** (opérateur, 2026-08-05) : *le semis clairsemé*, les arbres dispersés sur toute la surface,
sans zone privilégiée. Il vit en `assets/maquette/plan-composition-parc-a.json` et son dessin à côté. Les deux
autres propositions — *la grande pelouse* et *les bosquets* — sont écartées et ne sont plus produites : garder deux
plans écartés, c'est laisser croire qu'il reste un choix à faire.

**Communs aux trois** : 64 × 48 cases, herbe rase `CH-001` en cellule par défaut, **enceinte `OB-010` sur les quatre
bords** ouverte d'une case là où le chemin sort, bosquets `TR-061` **dehors, derrière la barrière**, en deux bandes
décalées, centre de soin `BT-001` au coin bas-droit et ses trois cases d'entrée dessous, butant exactement sur la
barrière. Les trois passent le contrôle de cohérence : **dix dessins à produire** compte tenu des rotations, deux
pour le chemin et huit pour la barrière.

**L'ouverture est un trou dans la clôture, pas un portillon.** Le portillon existe et est validé, mais c'est un
**variant** de la barrière, et un plan ne déclare aujourd'hui que des sujets et leurs raccords — il n'a pas de quoi
désigner un variant. Poser une case pleine là où l'on passe serait faux ; laisser le trou dit exactement ce qui s'y
trouve. **Porter le variant au format des plans reste à décider.**

**Les trois plans se lisent sur l'artefact « Le parc »**, et sur lui seul. Ils vivent sous `assets/maquette/` et
**non sous `assets/poc/`** : ce dossier-là est balayé par la galerie des plans d'usage des sujets, où la maquette
du parc n'a rien à faire.

La chaîne est toujours la même, et c'est une règle : **la ressource est produite par un script, puis incluse telle
quelle dans la page — jamais fabriquée à la volée par la page.** La déclaration en JSON est lue par
`scripts/build-composition-plan.py`, qui la vérifie et en produit le dessin ; puis `artefacts/parc/build.php` part
de cette même déclaration — pour découvrir les plans, leur titre, leur grille et leurs notes — et **inclut le
dessin déjà produit sans jamais le redessiner**. Un plan déclaré mais jamais dessiné arrête la construction de la
page au lieu de passer inaperçu.

**La page est le plan** : il s'y étale en pleine largeur, ajustable à sa taille réelle. **Un clic sur une case
attache une remarque à cette case** — elle se marque en rouge sur le dessin, et un bouton donne le récapitulatif
sous la forme `(12,30) : enlève le chêne`, à coller tel quel dans la conversation. C'est par là que passent
désormais les demandes de retouche du parc.

**Écarté : la popin.** Cette page vit dans un cadre qui grandit avec son contenu, où « toute la hauteur » vaut
toute la hauteur du document : le dessin sortait de l'écran et la molette faisait défiler le fond derrière lui.
Avec un seul plan à regarder, le défilement de la page suffit et il n'y a plus de hauteur à deviner.

**Aucun arbre n'est aligné sur un autre** : les positions sont tirées une à une par un générateur à graine fixe,
et toute position déjà occupée est abandonnée. Le parc paraît non planté, et il se reproduit à l'identique d'une
reconstruction à l'autre — c'est ce qui permet de comparer, corriger et rejouer une proposition.

**Ce que les trois plans réclament et qui n'existe pas encore** : le chemin `CH-019` n'a qu'une version dont la
couleur est encore jaune, et le sapin `TR-065` n'a pas de version courante inscrite depuis l'échec du 2026-08-05.

Les plans sont écrits par un script à usage unique, `local/scripts/build-park-plans.php`, jamais commité : la
disposition y est déclarée en quelques lignes — une bande de fond, le bâtiment et ses trois cases d'entrée, une
règle de semis — et le script l'étend en refusant tout chevauchement.

## Pourquoi il a fallu attendre une décision avant de l'écrire

L'outil existe et attend : `scripts/build-composition-plan.py` sait déjà lire un plan déclaré case par case, y
poser des sujets qui occupent plusieurs cases, vérifier que chaque raccord est annoncé des deux côtés, et en
sortir le dessin. Trois plans tournent déjà avec (chemin, cours d'eau, clôture). Ce n'est donc pas l'outillage
qui bloque.

**Ce qui manque est la description du parc lui-même.** La conception ne décrit qu'une chose : la **scène de
référence**, sur 32 × 24 (le format de composition), avec ses chemins, sa rivière, son centre de soin, sa
maison, sa tour de guet et ses personnages, chacun à une case précise. Le parc, lui, est annoncé sur
**64 × 48** — quatre fois cette surface — et **rien nulle part ne dit ce qui occupe la différence**. Écrire
le plan revenait donc à inventer les trois quarts du parc, ce qui est une décision de conception et n'appartient
pas à l'agent. **L'opérateur a tranché le 2026-08-05** en décrivant une scène neuve, ce qui a débloqué les trois
propositions ci-dessus. La conception, elle, ne décrit toujours que la scène de référence : le parc n'y est pas
écrit et devra l'être une fois le plan retenu.

## Trois décisions attendent l'opérateur — rien ne se produit avant

1. **Retirer du socle de consigne la contrainte « quatre cinquièmes de la hauteur »** ([`asset_common.CADRAGE_CUTOUT`](scripts/asset_common.py)). Elle contredit la clause de caméra : pour remplir quatre cinquièmes de la hauteur, un sujet doit être dressé et vu de face, alors que la plongée à 70° l'écrase. Le générateur suit la plus concrète des deux, d'où les vues frontales du pommier et du bosquet. **Constaté en relisant la consigne figée, pas déduit.**
2. **Inscrire la hauteur à l'inventaire** comme élément descriptif obligatoire, au même titre que l'emprise. Valeurs proposées, en cases : grand chêne 6, bosquet de sapins 6, pommier 3, herbe haute 0,5, clôture 0,9, centre de soin 8, matières de sol 0.
3. **Lancer les reprises** : bosquet (emprise passée à 2 × 2, son maître de 192 px est refusé par l'export qui en exige 384), pommier, clôture nord-sud, clôture en angle.

**Ce qu'un rejet ne doit PAS produire** : on ne renvoie jamais au générateur le motif du rejet. Il n'a pas vu l'image précédente, et le lui décrire en négatif ne l'aide pas — **ce qu'il faut, c'est une meilleure consigne** (opérateur, 2026-08-04). Une clause de reprise avait été ajoutée aux outils puis retirée pour cette raison.

## Ce qui reste en défaut

**Relevé par l'opérateur en fin de journée du 2026-08-04, tout est en cours de traitement :**

- **Régression sur la page de suivi** : les sprites s'affichent à la taille de leur fichier au lieu de **24 pixels par case d'emprise en largeur**, la hauteur suivant librement l'image. Le bouton œil vit **dans l'encart du variant**, jamais sur l'image ; l'image s'ouvre en grand au clic sur elle ou sur l'œil. *Confié à l'assistant « page de suivi ».*
- **Un variant n'a qu'une version active** : la dernière. Les antérieures (trois au plus) ne s'affichent plus dans le flux, elles s'atteignent par une **popin de comparaison**, sur le modèle de celle des planches de référence. Constaté sur la clôture nord-sud et est-ouest. *Même assistant.*
- **La parallélisation est fausse** : un script qui enchaîne plusieurs générations n'est pas parallèle. **Un processus système par génération**, et la file les mène de front. `run-fence-campaign.py` groupait ses travaux : c'est la faute. *Confié au codeur Python.*
- **Le pommier n'avait pas de pomme** : la fiche ne les demandait pas. Fiche entièrement réécrite le 2026-08-04, le fruit y est explicite et visible. **À regénérer.**
- **Le bosquet de sapins est mal décrit** : ce n'est pas une multitude de petits arbres, mais **deux à quatre arbres à la proportion juste** qui forment ensemble une masse infranchissable. Et une case infranchissable de ce genre **se remplit et se joint à ses voisines de même nature** — la géométrie exacte attend une réponse de l'opérateur avant réécriture.
- **Les plans de composition n'étaient visibles nulle part** : celui du chemin `CH-019` existe depuis le 2026-08-04 et n'était jamais remonté à l'opérateur. Un artefact dédié leur est ouvert. *Confié à un assistant.*
- **Le reste des variants de clôture est à produire.**

## Leçon de la nuit : ne pas paralléliser ce qui ne se découpe pas

Six assistants ont travaillé en parallèle sur un même sujet — le portillon touchait l'inventaire, le référentiel, deux outils et la page. Chaque décision devait traverser quatre propriétaires dans le bon ordre, par messages. **Un sujet qu'un seul agent aurait réglé en une passe a coûté vingt allers-retours.**

Ce qui marche : **la génération d'images en parallèle**, parce qu'aucune image ne dépend d'une autre. Ce qui ne marche pas : découper un travail qui se tient, par fichier plutôt que par sujet.

Deux façons de faire qui ont coûté cher, et qu'il faut abandonner :
- **Les clauses d'exploration** — « vérifie que rien d'autre n'a le même défaut », « signale-moi ce que tu croises » — transforment une demande de trois lignes en inspection du dépôt.
- **Corriger un assistant quinze fois** : tout s'empile dans sa mémoire. Celui du référentiel a vécu la conception du portillon quatre fois. Mieux vaut l'arrêter au deuxième revirement et en relancer un avec la décision arrêtée.

**Pour la suite : un sujet, un agent, du début à la fin. La parallélisation réservée à la production d'images. Et rien de délégué dont la définition n'est pas arrêtée.**

## Où on en est vraiment, fin de la nuit du 2026-08-04

**Produit et exporté depuis la reprise** : le pommier, le bosquet, les trois angles de clôture, la ligne est-ouest à un puis à deux poteaux, le centre de soin refait vu de dessus, le sapin, l'herbe clairsemée, et les sprites principaux du chemin et du cours d'eau. Les deux exemples d'usage du chemin et du cours d'eau sont produits mais **ratés** — rendus à plat, sans la caméra du projet ; leur consigne est corrigée depuis, ils sont à refaire.

**Les quatre portillons attendent** : leur outil insère encore d'office une phrase sur le poteau unique, qui n'a aucun sens pour un portillon. Les quatre premières images ont été gâchées pour cette raison et sont écartées.

**Le rendement de la nuit est mauvais, et il faut en tirer la leçon.** Beaucoup de temps est parti dans des allers-retours sur des détails de modèle — le portillon devenu forme puis axe, la composition, les libellés — alors que la production, elle, avançait peu. Ce qui a réellement coûté : des chantiers ouverts sans qu'on les demande, des correctifs lancés avant tout diagnostic, et des questions reposées alors que la réponse était déjà donnée. Les règles écrites cette nuit dans la méthode visent exactement ça.

**Le référentiel est sain et son contrôleur passe au vert** : douze sujets déclarés, aucun fichier orphelin, aucun maître manquant. Le modèle porte désormais le statut de version, le **verdict de l'opérateur** qui ne s'y confond pas, le maître, le numéro d'image et une place pour les mesures — encore vide, l'outil de mesure n'y écrit pas. Deux règles nouvelles y vivent avec leurs raisons : un axe peut **définir la nature** d'une pièce, et un axe peut en **rendre un autre inapplicable**.

**Attendent ton verdict** : la reprise de la ligne est-ouest à deux poteaux, le chemin, le ruisseau, le centre de soin refait, le sapin et l'herbe clairsemée.

**La destination d'une image ne se déduit plus de sa référence.** C'était la cause de deux sprites allés se ranger dans les planches de référence — remis en place à la main. Un seul outil portait le défaut, il est corrigé et éprouvé : la destination ne dépend que du code du sujet, et la référence peut vivre n'importe où. Les trois outils qui acceptent une référence sont éprouvés : la destination est identique avec une référence lointaine et sans référence.

**Trois pièges à connaître avant de toucher à la chaîne** : le référentiel des sujets est édité en direct par plusieurs mains, une lecture peut tomber pendant une écriture ; une clause qui a l'air générale peut cacher un mot valable pour un seul type — on ne les trouve qu'en lisant la consigne produite en entier, jamais en survolant le code ; et les chemins d'images du référentiel sont relatifs au dossier des images, jamais à la racine du dépôt.

**Le catalogue gelé est débranché** : les deux outils vivants lisent désormais le référentiel des sujets, et l'enregistrement d'une image **ajoute une version** au lieu d'écraser. Les deux modules du catalogue n'ont plus aucun lecteur ; ils ne sont pas supprimés.

**Ce qui reste en vol, à reprendre :**

1. **La page de suivi n'affiche pas le centre de soin.** Elle embarque chaque sprite en pleine définition alors qu'elle ne les montre qu'à vingt-quatre pixels par case : un livrable de seize cases pèse 1,7 Mo pour 384 pixels affichés. Un plafond de 500 ko a été posé en garde-fou, il montre « image trop volumineuse » au lieu d'un cadre vide — mais **la vraie réponse est de fabriquer une vignette à la taille d'affichage**, ce qui fait tomber le poids pour toutes les images et rend le plafond inatteignable. Le bouton œil doit continuer d'ouvrir l'image entière.
2. **Le constructeur de la page échoue en fin de course** : `NameError: name 'UNREADABLE_IMAGES' is not defined`, dans l'étape même qui devait signaler les anomalies au lanceur. La page est pourtant écrite avant l'échec.
3. **Le libellé d'un variant de portillon doit commencer par le portillon**, pas par « Ligne » : ce qui change la nature de la pièce mène le libellé. Un poteau de plus ou de moins, non — une ligne reste une ligne. La règle générale reste à écrire.
4. **Quatre reprises ne sont pas déclarées au référentiel** : `TR-063-v3`, `TR-061-v3`, `OB-010_shape-nw_posts-1-v2`, `OB-010_shape-ew_posts-1-v2`. Chacune devient courante, celle qu'elle remplace passe en antérieure, **et repart sans verdict**. Le pommier et le bosquet atteignent la troisième version : le plafond de trois antérieures se pose, et rien ne se supprime du disque.
5. **Les lots des tracés sont complétés** : cinq dessins à produire — extrémité, ligne, angle, trois branches, croisement —, quinze configurations couvertes par rotation. La distinction est écrite dans le type : ce qu'il faut **dessiner** n'est pas ce qu'une case doit **savoir accepter**. La clôture, qui ne pivote pas, garde ses six formes, plus les quatre variants de portillon qui sont à produire eux aussi.
   **Le cours d'eau `CH-020` n'est pas sur la maquette du parc, mais son exemple d'usage se produit quand même** (opérateur, 2026-08-04) : le sujet est déjà dessiné dans les références de direction artistique, il n'y a donc rien à inventer. Ne pas confondre « absent de la maquette » et « à ne pas produire ».
6. **Le catalogue gelé n'est pas débranché.** La correspondance ligne à ligne est faite et le feu vert donné : `check-asset.py` et `record-asset.py` doivent lire le référentiel des sujets. Deux changements assumés au passage — l'enregistrement **ajoute une version** au lieu d'écraser, et le type se valide contre les types déclarés par le référentiel. `asset_catalog.py` et `check-catalog.py` ne se suppriment pas sans ordre.
7. **La chaumière de l'ébauche est devenue `BT-002` maison de ferme** (toit de tuiles orange, pas de chaume). **La tour de guet reste hors inventaire** — décision de l'opérateur, elle n'appartient pas au parc du POC ; elle est dessinée dans l'ébauche et pourra être inventoriée le jour où une scène en aura besoin. Le potager clôturé et ses cultures, également dessinés, attendent la même décision.
8. **Écart constaté sur `CH-001`** : l'ébauche montre un sol semé de petites fleurs blanches, roses et violettes, alors que la fiche — validée par l'opérateur — décrit une étendue uniquement herbeuse. À trancher : texture de la tuile, ou sujets posés par-dessus ?

## L'inventaire ne couvre pas les planches de référence (audit du 2026-08-04)

Les six planches sont des références **documentées** : chacune a sa fiche, et le texte de production de chacune donne les coordonnées et les emprises exactes. Confronté à l'inventaire, l'écart est massif — il ne se comble pas au coup par coup.

**Dix fiches se contredisent avec leur planche sur l'emprise ou la hauteur** : le grand chêne (2×2 contre 3×3), la bergerie (8×5 contre 8×8), l'entrée de mine (5×3 contre 8×7), la tour en ruine (5×5 contre 4×4), la hutte sur pilotis (5×4 contre 12×10), le phare (5×5 hauteur 10 contre 4×4 hauteur d'environ 24), le cabanon de pêcheur (4×3 contre 8×8), la cabane de plage (5×4 contre 8×8), la barque échouée (4×2 contre 2 cases), et l'appontement, dont la fiche décrit une jetée sur pilotis là où la planche montre un tablier plat posé sur la plage.

**Une fiche contredit une règle déjà écrite** : le séchoir `BT-031` nomme et décrit des poissons, alors que les planches posent qu'un monde sans poissons n'en sèche pas — c'est un séchoir à récoltes du marais.

**Des pans entiers du monde n'ont aucun code** : les **cultures** (champ de blé, potager, verger) n'existent nulle part ; la planche du bourg n'a **aucun** de ses bâtiments inventorié (halle, lavoir, boulangerie, forge, auberge, maisons, atelier) ; manquent aussi le moulin, la grange, la chaumière de chaume, plusieurs essences (bouleau, arbres fruitiers, mangrove, nénuphar, bruyère, palmier), des reliefs que le format distingue explicitement (crevasse, enclos, dunes), une dizaine d'objets (puits, charrette, meules, tonneaux, fontaine, étals, murets de pierre sèche, coquillages) et au moins un humain.

**Ce que ça change** : l'inventaire a été écrit avant les planches et n'a jamais été confronté à elles. Rien n'est urgent pour le POC — le parc n'emploie qu'une poignée de sujets — mais **toute production hors du parc partira de fiches fausses** tant que ce n'est pas repris. Et **aucun sujet ne se crée sans l'opérateur** : la liste est une proposition, pas un chantier lancé.

**Contradiction en attente d'arbitrage** : le sapin. L'opérateur le veut « nettement plus petit que les six cases du bosquet », mais la fiche du bosquet dit que chacun de ses sapins est « à la taille d'un sapin ». Les deux ne peuvent être vrais. Sa fiche n'est pas écrite tant que ce n'est pas tranché.

**Chantiers ouverts en fin de journée du 2026-08-04 :**

- **Les clés de données passent en anglais.** La règle est écrite dans `AGENTS.md` pour que le français cesse de s'étendre ; la migration elle-même est **à faire**, l'opérateur l'a repoussée. Relevé complet : dans le référentiel des sujets — `sujets`, `variantes`, `emprise`, `hauteur`, `passage`, `passage_default`, `profil`, `statut`, `composition`/`compositions` ; dans les jugements — `jugements`, `nom`, `criteres`, `tenu`, `sur`, `rapport`. **Deux points à trancher** : les identifiants de type, employés comme clés (`sol`, `chemin`, `cloture`, `arbre`, `bosquet-arbres`, `herbe`, `batiment`, `humain`), et le mot `note`, identique dans les deux langues mais employé ici au sens français de remarque.
- **Les descriptions d'inventaire passent en français.** Ordre de l'opérateur : toute consigne envoyée au générateur est en français, or la description du sujet y était citée en anglais — le seul fragment qui restait. La règle du README est déjà retournée ; la réécriture d'une centaine de fiches est en cours. Ce n'est pas une traduction mot à mot : le texte doit être aussi concret en français, sans rien perdre ni rien ajouter, en prescription positive.
- **Le catalogue gelé doit être débranché**, pas seulement cessé d'être écrit. Il porte encore tout l'adressage dont dépendent deux outils vivants — `check-asset.py` et `record-asset.py`. Le débranchement ne se fait **qu'après** une correspondance ligne à ligne prouvant que le référentiel des sujets fournit tout ce qu'ils y prennent ; s'il manque quoi que ce soit, c'est le référentiel qui est incomplet, et le compléter est une décision de conception.
- **Le vocabulaire des formes est recopié en dur dans cinq outils**, et cette copie vit dans le module du catalogue gelé. Un détenteur unique le remplace, les autres l'importent — comme les tailles en pixels, qui n'ont plus jamais divergé depuis qu'elles en ont un.
- **Une forme peut porter une qualification** devant ses bords — `gate-ew`, `gate-ns` — parce que deux pièces peuvent relier les mêmes bords sans être le même dessin. Règle écrite dans la conception et au lexique.
- **La toile demandée au générateur épouse la forme réelle du sujet.** Elle se calculait sur le seul sol : un pommier haut de trois cases recevait un carré et s'écrasait. La profondeur au sol se projette presque en vraie grandeur, la hauteur s'écrase au tiers — la caméra est à soixante-dix degrés **sous l'horizontale**, donc près de la verticale. Cette convention est la source d'une erreur commise et corrigée aujourd'hui : elle est désormais écrite noir sur blanc dans le service qui détient les tailles.

- **Le portillon** `OB-010_shape-ew-avec-portillon.png` est **rattaché** au référentiel le 2026-08-04, sur un axe `ouverture` proposé. Deux points attendent l'opérateur : le nom de l'axe, et **le passage** — un portillon se traverse, ce qui renverse la fermeture du type sur les deux côtés reliés.
- **`check-sujets.py` a deux défauts** : il réclame qu'un variant revendique aussi les **maîtres** de `assets/poc/`, alors qu'un variant ne pointe que le livrable de `assets/cutout/` ; et il compte en faute les sondes pourtant déclarées `_hors_referentiel`. Il sort donc en erreur alors que le référentiel est sain.
- **`reference-OB-010.png`** est une copie de la clôture est-ouest, déposée par l'ancien mécanisme de cascade. Elle traîne au recensement ; proposé de l'exclure comme les `usage-*`.
- **Le bouton œil a disparu** de la page au lieu d'être déplacé hors de l'image ; tout l'encart est devenu la cible. À confirmer ou à rétablir.
- **`cut-asset.py`** existe encore mais n'est plus appelé — le rognage est abandonné.
- **`build-fence-geometry-svg.py`** écraserait la géométrie dessinée à la main s'il était relancé : à neutraliser.
- La **fiche `CH-001`** est écrite en interdits ; l'analyse conclut que ses quatre interdits ne sont pas redondants et qu'une réécriture positive devrait passer par une clause d'exclusivité, à tester avant bascule.
- La plupart des **fiches de créatures n'ont pas d'emprise** écrite.

**Attention reprise : les assistants sont liés à leur session** et se recréent à chaque fois, avec tout leur contexte dans leur consigne. Trois rôles ont fait leurs preuves le 2026-08-04, tous en **Sonnet** — le mécanique ne demande pas un modèle fort :

- **la page de suivi** : construire et reconstruire `artefacts/suivi-sprites/build.py` ;
- **le jugement** : noter les sprites sur critères écrits et écrire `assets/jugements.json`, **dont il est le seul auteur** ;
- **le codeur Python** : bridé sur Python seul, on lui donne les signatures d'entrée et de sortie et ce que le script doit rendre, il écrit le corps. On lui confie de préférence un **script neuf** plutôt qu'un script déjà en service.

**Un fichier n'a qu'un seul agent propriétaire.** Deux agents lancés sur `build.py` le même après-midi l'ont cassé en s'écrasant l'un l'autre.

## La chaîne, telle qu'elle tourne aujourd'hui

Plan de composition déclaratif et contrôlé → consigne assemblée par outil, jamais à la main → génération → **export** à la définition de livraison → **jugement noté** → référentiel des sujets → suivi publié. Le **rognage est abandonné** : on corrige la consigne, jamais l'image.

**Un exemple d'usage** est une image unique montrant les pièces d'un sujet assemblées ; elle sert de **référence de style** aux pièces produites ensuite, et ce mécanisme-là fonctionne — les trois pièces de clôture du 2026-08-04 se ressemblent enfin. Ce n'est pas une sprite et elle ne se découpe pas.

**La géométrie d'un sujet qui s'assemble se dessine à la main**, en SVG, à côté de son plan : `assets/poc/cloture/plan-composition-OB-010-usage-geometrie.svg`. Ses cotes ont été **mesurées sur l'image produite**, jamais supposées, et les quatre règles qu'elle établit sont écrites en tête du fichier — un contour fermé par lisse, jamais de section entière sur une lisse, section à peine arquée à l'horizontale, un seul fût pour une portée nord-sud. Elles serviront au chemin, au mur et au cours d'eau.

**Leçon payée cher** : une géométrie se met au point **sur une jointure seule, en grand**. Sur la figure entière, un défaut de deux unités est invisible et se valide à tort — cinq versions successives l'ont prouvé.

## Organisation du travail

Un assistant persistant **« atelier-planches »** (Opus) exécute la production (consignes, tirs, mesures, rapports, page, publication) ; l'agent principal pilote (consignes de l'opérateur, contrôle, redirection) — rôles et partage des acquis posés dans [methode/execution.md](../conceptions/methode/execution.md). Règles qui coûtent cher si on les oublie : une seule génération par version (garde-fou anti-doublon dans le code) ; aucune relance sans accord explicite ; publication planche par planche ; les questions ouvertes se reposent à chaque message ; une définition de l'opérateur se transcrit telle quelle ; devant un écart, situer la faute (consigne ou production) en citant le texte exact.

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

## Améliorations individuelles en réserve (hors chemin du POC, décision de l'opérateur)

- **Fiches créatures qui dérivent vers l'animal réel** malgré les durcissements de consigne : SP-005, SP-007, SP-010, SP-011, SP-015 (+ dédoublements de SP-002/SP-017). Deux voies documentées : durcir les fiches elles-mêmes (révision refusée une première fois) ou corriger au cas par cas.
- **Saturation** sous la référence (52–62 contre 73) sur P2/P3/P5 — jamais attaquée de front ; P1 v8 (77,1) montre que c'est atteignable.
- **P6** restée en v5.
- **Contradiction non arbitrée** : l'image de référence DA mesure 103,5 de luminance — hors de la bande 115–130 exigée des planches ; une planche ne peut pas à la fois la reproduire et tenir la bande.

## Les outils

**Aucun outil ne se réinvente : on cherche ici d'abord.** Le tableau dit, pour chaque besoin, l'outil à employer. Tous les scripts sont dans `scripts/`, en anglais, exécutables depuis la racine du dépôt.

### Ce qu'il faut employer, par usage

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
| Détourer un asset | `cut-asset.py` |
| Mesurer un asset | `check-asset.py` (transparence, emprise, raccord, lumière) |
| Mesurer une planche | `analyze-plate.py` (mesures + verdict lumière) |
| Convertir case ↔ pixels, dimensionner | `tile_scale.py` — **seul détenteur** des deux valeurs : case d'écran à 24 px, finesse de livraison dimensionnée sur le zoom maximum |
| Exporter un livrable | `export-asset.py` — redimensionne, ne rogne rien, mesure l'emprise et le point de pose |
| Lire ou contrôler le référentiel des sujets | `check-sujets.py` — affiche la valeur résolue du passage, niveau par niveau |
| Commander une sprite, quelle qu'elle soit | `generate-sprite.py <ref du sujet> <ref du variant>` — tout est lu au référentiel ; elle exporte, inscrit et écrit son rapport |
| Commander tout un jeu de pièces | `run-fence-campaign.py` — une seule campagne, une seule référence |
| Commander un exemple d'usage | `generate-usage-sample.py` depuis un plan de composition |
| Enfiler des demandes de sprite et les traiter au fil de l'eau | `sprite-queue.py` — file à `local/sprite-queue.jsonl`, reconstruction de la page sérialisée |
| Rééchantillonner une image | `resize-image.py` |
| Construire une page de revue | `build-planches-page.py`, `build-calibration-page.py`, et `artefacts/suivi-sprites/build.py` pour le suivi des sprites |
| Regarder un SVG que j'ai produit | `rsvg-convert` vers un PNG dans `local/` — un agent ne sait pas lire un SVG, il lit une image matricielle |

Les `generate-planche-*.py` et `generate-humans-calibration-*.py` sont conservés tels quels : un fichier par passage, ils ne se rejouent pas.

### Outils extérieurs et versions constatées

| Outil | Version | Usage |
|---|---|---|
| Codex (`codex`) | codex-cli 0.146.0 | le générateur d'images, enveloppé par `generate-image.php` |
| PHP | 8.4.24 | le wrapper du générateur |
| Python | 3.12.3 | tout le reste de l'outillage |
| `rsvg-convert` | 2.58.0 | SVG → PNG, pour que l'agent puisse regarder ce qu'il produit |

Toute version se reconstate avant de s'y fier : une version écrite ici est un constat daté, pas une garantie.

## Les deux pages de suivi du POC

Décidées avec l'opérateur ; elles remplacent les comptes rendus en conversation dès que la matière devient visuelle.

- **Le suivi des sprites** — tous les sujets groupés par type, chaque profil, chaque variant attendu avec son état (prévu, en production, produit, en défaut), un panneau de comptes en tête, et des actions par variant qui alimentent un récapitulatif copiable. C'est l'unique endroit où se lit l'état de la production.
- **Le parc** — le plan de composition en haut, la maquette montée en dessous, sur une seule page. Cible : pouvoir **sélectionner une zone** sur l'un ou l'autre et commenter cette zone, le commentaire partant au récapitulatif avec la zone désignée ([méthode](../conceptions/methode/revue-visuelle.md)).

## Les revues publiées

**Quatre états, et seuls ces quatre-là.** **Vivant** : on s'en sert, il se republie. **Archivé** : il n'est plus actif, mais il reste consultable et son adresse reste valable — archiver n'est pas supprimer. **Clos** : son sujet est tranché, il ne bougera plus. **À ne pas rouvrir** : un doublon créé par erreur, sur lequel on ne republie jamais.

**Règle absolue : on ne crée jamais un artefact nouveau quand un artefact dédié existe déjà.** On republie sur son adresse. Cet inventaire est **exhaustif** et se tient à jour dans le même geste que toute publication — une adresse non consignée est une adresse perdue, et le suivant crée un doublon. Avant toute publication : lire cet inventaire, puis lister les artefacts existants pour vérifier qu'il n'en manque aucun.

| Artefact | Adresse | État |
|---|---|---|
| **Index des artefacts** — la porte d'entrée vers tous les autres, bâtie sur ce tableau même (`artefacts/index/`) | https://claude.ai/code/artifact/cf3f2ac3-903c-43fb-ac91-c8e0129ab949 | vivant, ouvert le 2026-08-04 |
| **Audit de l'inventaire** — les écarts avec les six planches, à arbitrer ligne par ligne (`artefacts/audit-inventaire/`) | https://claude.ai/code/artifact/a15caa68-3b52-4cab-a92e-4b0829b172aa | vivant, en attente d'arbitrage |
| **Suivi des sprites** — l'unique endroit où se lit l'état de la production | https://claude.ai/code/artifact/844640e3-8d10-47d5-b74d-aca74b99f63c | vivant, republié le 2026-08-04 |
| **Plans de composition** — tout plan déclaré sous `assets/poc/`, découverte automatique (`artefacts/plans-de-composition/`) | https://claude.ai/code/artifact/21dd8a3a-aea2-484d-9202-3749e24cb8b9 | vivant, ouvert le 2026-08-04 |
| **Tour de nettoyage** — 31 éléments relevés, un verdict par ligne (`artefacts/nettoyage/`) | https://claude.ai/code/artifact/8598d3c2-a037-4edf-af42-f2fb4447498c | archivé |
| **Planches de référence** — chaque planche avec son rapport noté | https://claude.ai/code/artifact/12a098f0-aecb-4326-8d4a-e60c80802413 | archivé |
| **Calibration de l'échelle humaine** | https://claude.ai/code/artifact/044dfac1-998d-4b36-87a5-639059ddba40 | archivé |
| **Direction artistique** (historique de la revue) | https://claude.ai/code/artifact/f5b1e6f7-ad28-4f72-9c41-f0a2cdfd38c5 | clos — DA validée |
| **Son** (essais, plafond constaté) | https://claude.ai/code/artifact/e0c55e5f-f179-4ef7-9338-9d2b2cc341b8 | clos — synthèse abandonnée |
| **Le parc** — plans de composition, maquette montée, commentaire par zone (`artefacts/parc/`) | https://claude.ai/code/artifact/5f9bb2af-9126-44e6-b953-59afb7ab4e28 | vivant, ouvert le 2026-08-05 avec les trois plans ; la maquette montée et le commentaire par zone restent à ajouter |

## Ce qui attend l'opérateur

- L'arbitrage du **lot v0** de la maquette B0.
- À terme : l'arbitrage de la contradiction lumière référence/bande, et le sort des fiches créatures dérivantes — tous deux hors chemin du POC.
