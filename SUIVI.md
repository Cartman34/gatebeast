# Suivi des travaux — GateBeast

**Intention :** permettre à n'importe quel intervenant de reprendre le travail sans perte. Ce document dit **où on en est**, pas ce que le jeu doit être — la cible vit dans la conception, le découpage en versions dans le [plan d'action](PLAN-ACTION.md).

Il se met à jour à chaque étape franchie. Il ne conserve pas d'historique : seul l'état courant compte (le versionnage garde le reste).

## Où en est le projet (2026-08-04)

**La direction artistique est VALIDÉE** (*toon volume*, figée sur les six planches de référence — décision et termes de l'opérateur dans [visuel/index.md](doc/conception/referentiels/visuel/index.md)). **La conception est close** : [questions.md](doc/conception/questions.md) est vide. **Le POC est engagé** : le chemin vers la 0.1 est découpé en briques B0–B8 dans le [plan d'action](PLAN-ACTION.md), avec les décisions déjà prises — B0 maquette à sprites publiée en artefact Claude (hébergement du POC), B1 dépôt `git@github.com:Cartman34/gatebeast.git`, B3 moteur CSS, générateur d'images = agent Codex via le wrapper (capacités au [référentiel technique](doc/conception/referentiels/technique/index.md), limites des artefacts incluses).

**Fait — les capacités du générateur sont constatées** : il rend **exactement la définition demandée** ; il rend un **vrai canal alpha**, vides encerclés compris, dès qu'on le demande — le fond magenta et le détourage ont donc été **abandonnés** ; l'angle obtenu est le bon, c'est la vue standard des sprites. **Deux limites** : le traitement varie d'un sujet à l'autre, et surtout il **n'exploite pas l'image de référence** qu'on lui fournit (voir ci-dessous).

**MAJEUR — la cascade ne fonctionne pas.** La règle de cohérence du projet veut qu'une variante se produise **à partir de la vue principale validée**, fournie comme référence visuelle. Le mécanisme est en place et l'image est bien déposée dans le répertoire de travail du générateur ; mais deux essais sur la clôture nord-sud, dont un avec une consigne disant en toutes lettres « exactement la clôture de l'image de référence, vue tournée d'un quart de tour », ont rendu **une autre clôture**. Deux générations de la même fiche donnent aussi deux chênes nettement différents. Ces images n'ont pas été soumises à l'opérateur : le jugement ci-dessus est celui de l'agent principal, pas un verdict de l'opérateur. Conséquence : rien ne garantit aujourd'hui la cohérence entre les variantes d'un même sujet — les huit pièces de clôture, les quatre orientations d'un personnage, les poses d'une marche. **Décision à prendre avec l'opérateur avant toute production de variantes.**

**Fait — la couche assets est conçue** (2026-08-03) : modèle sujet / type / profil / variante, orientation dans le repère du monde, action, et une direction par partie qui pointe dans le repère du sujet (`north` = droit devant), images numérotées en dessous, repli déclaré, empilement à l'écran, lots par type, chaîne de production. Voir [rendu en calques](doc/conception/referentiels/technique/rendu-en-calques.md), [assets](doc/conception/referentiels/visuel/assets/index.md), [sujets et variantes](doc/conception/referentiels/visuel/assets/sujets-et-variantes.md) et le [lexique](doc/lexique.md) enrichi du vocabulaire de production (anglais américain).

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

**Décisions du 2026-08-04, toutes écrites dans la conception.** On dit **opérateur**, jamais « propriétaire » (terme banni, [glossaire de la méthode](../conceptions/methode/glossaire.md)). Les **types sont fins** — un type regroupe ce qui s'échange sans incohérence : herbe, arbre, bosquet d'arbres, clôture, chemin, et non « végétation ». Le **passage** d'un sujet se déclare **côté par côté**, jamais il ne se déduit d'une forme : tout se traverse par défaut, un type peut renverser cette valeur, et **trois niveaux** — type, sujet, variante — se surchargent en ne portant que ce qu'ils définissent ; fermer deux côtés adjacents ferme ce qui est entre eux ; l'inventaire se revalide à chaque ajout. Le **catalogue est gelé** : un fichier neuf le remplacera, construit autour des **types, sujets, variantes et représentations** — la sprite n'étant qu'une représentation parmi d'autres. Le **lexique** a quitté la conception pour `doc/lexique.md`, **biome** y est défini, et les **humains** sont réunis à l'inventaire sous `HU-nnn` — il n'y a pas de sujet « personnage-joueur ».

**Nouvel outil — le plan de composition** ([sa fiche](doc/outils/plan-de-composition.md)) : `scripts/build-composition-plan.py` rend un plan à plat depuis un JSON déclaratif qui *est* le plan, avec des contrôles qui bloquent. Le moteur partagé est `scripts/composition_plan.py`. Premier plan produit : `assets/poc/cloture/plan-composition-OB-010-usage.json` — carré fermé, croix centrale, quatre antennes, les quinze formes de tracé exercées.

**Les deux dettes sont soldées** (2026-08-04) : le **catalogue** est **gelé** — ni lu, ni écrit, ni supprimé — et remplacé par `assets/sujets.json`, le référentiel des sujets ; la **page de suivi des sprites** part désormais du disque, montre toute image existante, et pèse 0,47 Mo au lieu de 10,3.

**La chaîne tient de bout en bout** (2026-08-04) : plan de composition déclaratif et contrôlé → consigne assemblée par outil, jamais à la main → génération → **export** à la définition de livraison → référentiel des sujets → suivi publié. Le **rognage est abandonné** : on corrige la consigne, jamais l'image.

**Fait — deux fautes de méthode de l'agent principal, corrigées** : une image **validée** a été écartée sous un nom la faisant passer pour ratée, puis remplacée par une moins bonne — les noms sont rétablis ; et plusieurs correctifs ont été appliqués sans validation préalable, alors que le protocole impose de proposer et d'attendre.

**Décisions de conception prises dans la journée, toutes écrites** : fond demandé **transparent** et **sans halo** (le magenta et le détourage sont abandonnés) ; un **tracé** — clôture, chemin, cours d'eau, mur — se décrit par **l'ensemble des bords qu'il relie** (`shape-ns`, `shape-ne`…), passe par le centre de sa case, et sa consigne dit qu'il est **une pièce d'assemblage** dont les éléments atteignent exactement ces bords ; la **consigne d'une image est figée** dès que l'image existe, un brouillon ne l'écrase jamais ; la **lumière** appartient au socle commun des consignes et les outils de correction **ne s'appliquent jamais d'office** ; la **définition demandée** est celle du maître, calculée par le service de conversion (double de la livraison, plafond 1536) ; **une case vaut 48 pixels**, seule valeur en pixels du projet, détenue par un **service unique** avec ses opérations. Vocabulaire : on dit **génération d'image**, jamais « tir ».

**Attention reprise : l'assistant « atelier-planches » a été perdu en cours de session** — son fil a disparu et il n'était plus joignable ; tout son acquis vit dans les fichiers. Leçon inscrite : un travail de fond se contrôle **à ses produits**, jamais à son silence.

**En cours — B0/B4.** La chaîne est outillée de bout en bout et tourne. Reste à produire le lot v0 de la scène de référence, puis à composer le parc. B2/B3 peuvent avancer en parallèle. **Le personnage-joueur n'est pas un sujet à part** : il n'y a que des humains, et il pourrait être n'importe lequel (opérateur, 2026-08-04).

## Trois décisions attendent l'opérateur — rien ne se produit avant

1. **Retirer du socle de consigne la contrainte « quatre cinquièmes de la hauteur »** ([`asset_common.CADRAGE_CUTOUT`](scripts/asset_common.py)). Elle contredit la clause de caméra : pour remplir quatre cinquièmes de la hauteur, un sujet doit être dressé et vu de face, alors que la plongée à 70° l'écrase. Le générateur suit la plus concrète des deux, d'où les vues frontales du pommier et du bosquet. **Constaté en relisant la consigne figée, pas déduit.**
2. **Inscrire la hauteur à l'inventaire** comme élément descriptif obligatoire, au même titre que l'emprise. Valeurs proposées, en cases : grand chêne 6, bosquet de sapins 6, pommier 3, herbe haute 0,5, clôture 0,9, centre de soin 8, matières de sol 0.
3. **Lancer les reprises** : bosquet (emprise passée à 2 × 2, son maître de 192 px est refusé par l'export qui en exige 384), pommier, clôture nord-sud, clôture en angle.

**Ce qu'un rejet ne doit PAS produire** : on ne renvoie jamais au générateur le motif du rejet. Il n'a pas vu l'image précédente, et le lui décrire en négatif ne l'aide pas — **ce qu'il faut, c'est une meilleure consigne** (opérateur, 2026-08-04). Une clause de reprise avait été ajoutée aux outils puis retirée pour cette raison.

## Ce qui reste en défaut

**Relevé par l'opérateur en fin de journée du 2026-08-04, tout est en cours de traitement :**

- **Régression sur la page de suivi** : les sprites s'affichent à la taille de leur fichier au lieu de **24 pixels par case d'emprise en largeur**, la hauteur suivant librement l'image. Le bouton œil vit **dans l'encart de la variante**, jamais sur l'image ; l'image s'ouvre en grand au clic sur elle ou sur l'œil. *Confié à l'assistant « page de suivi ».*
- **Une variante n'a qu'une version active** : la dernière. Les antérieures (trois au plus) ne s'affichent plus dans le flux, elles s'atteignent par une **popin de comparaison**, sur le modèle de celle des planches de référence. Constaté sur la clôture nord-sud et est-ouest. *Même assistant.*
- **La parallélisation est fausse** : un script qui enchaîne plusieurs générations n'est pas parallèle. **Un processus système par génération**, et la file les mène de front. `run-fence-campaign.py` groupait ses travaux : c'est la faute. *Confié au codeur Python.*
- **Le pommier n'avait pas de pomme** : la fiche ne les demandait pas. Fiche entièrement réécrite le 2026-08-04, le fruit y est explicite et visible. **À regénérer.**
- **Le bosquet de sapins est mal décrit** : ce n'est pas une multitude de petits arbres, mais **deux à quatre arbres à la proportion juste** qui forment ensemble une masse infranchissable. Et une case infranchissable de ce genre **se remplit et se joint à ses voisines de même nature** — la géométrie exacte attend une réponse de l'opérateur avant réécriture.
- **Les plans de composition n'étaient visibles nulle part** : celui du chemin `CH-019` existe depuis le 2026-08-04 et n'était jamais remonté à l'opérateur. Un artefact dédié leur est ouvert. *Confié à un assistant.*
- **Le reste des variantes de clôture est à produire.**

## Leçon de la nuit : ne pas paralléliser ce qui ne se découpe pas

Six assistants ont travaillé en parallèle sur un même sujet — le portillon touchait l'inventaire, le référentiel, deux outils et la page. Chaque décision devait traverser quatre propriétaires dans le bon ordre, par messages. **Un sujet qu'un seul agent aurait réglé en une passe a coûté vingt allers-retours.**

Ce qui marche : **la génération d'images en parallèle**, parce qu'aucune image ne dépend d'une autre. Ce qui ne marche pas : découper un travail qui se tient, par fichier plutôt que par sujet.

Deux façons de faire qui ont coûté cher, et qu'il faut abandonner :
- **Les clauses d'exploration** — « vérifie que rien d'autre n'a le même défaut », « signale-moi ce que tu croises » — transforment une demande de trois lignes en inspection du dépôt.
- **Corriger un assistant quinze fois** : tout s'empile dans sa mémoire. Celui du référentiel a vécu la conception du portillon quatre fois. Mieux vaut l'arrêter au deuxième revirement et en relancer un avec la décision arrêtée.

**Pour la suite : un sujet, un agent, du début à la fin. La parallélisation réservée à la production d'images. Et rien de délégué dont la définition n'est pas arrêtée.**

## Où on en est vraiment, fin de la nuit du 2026-08-04

**Produit et exporté depuis la reprise** : le pommier, le bosquet, les trois angles de clôture, la ligne est-ouest à un puis à deux poteaux, le centre de soin refait vu de dessus, le sapin isolé, l'herbe clairsemée, et les sprites principaux du chemin et du cours d'eau. Les deux exemples d'usage du chemin et du cours d'eau sont produits mais **ratés** — rendus à plat, sans la caméra du projet ; leur consigne est corrigée depuis, ils sont à refaire.

**Les quatre portillons attendent** : leur outil insère encore d'office une phrase sur le poteau unique, qui n'a aucun sens pour un portillon. Les quatre premières images ont été gâchées pour cette raison et sont écartées.

**Le rendement de la nuit est mauvais, et il faut en tirer la leçon.** Beaucoup de temps est parti dans des allers-retours sur des détails de modèle — le portillon devenu forme puis axe, la composition, les libellés — alors que la production, elle, avançait peu. Ce qui a réellement coûté : des chantiers ouverts sans qu'on les demande, des correctifs lancés avant tout diagnostic, et des questions reposées alors que la réponse était déjà donnée. Les règles écrites cette nuit dans la méthode visent exactement ça.

**Le référentiel est sain et son contrôleur passe au vert** : douze sujets déclarés, aucun fichier orphelin, aucun maître manquant. Le modèle porte désormais le statut de version, le **verdict de l'opérateur** qui ne s'y confond pas, le maître, le numéro d'image et une place pour les mesures — encore vide, l'outil de mesure n'y écrit pas. Deux règles nouvelles y vivent avec leurs raisons : un axe peut **définir la nature** d'une pièce, et un axe peut en **rendre un autre inapplicable**.

**Attendent ton verdict** : la reprise de la ligne est-ouest à deux poteaux, le chemin, le ruisseau, le centre de soin refait, le sapin isolé et l'herbe clairsemée.

**La destination d'une image ne se déduit plus de sa référence.** C'était la cause de deux sprites allés se ranger dans les planches de référence — remis en place à la main. Un seul outil portait le défaut, il est corrigé et éprouvé : la destination ne dépend que du code du sujet, et la référence peut vivre n'importe où. Les trois outils qui acceptent une référence sont éprouvés : la destination est identique avec une référence lointaine et sans référence.

**Trois pièges à connaître avant de toucher à la chaîne** : le référentiel des sujets est édité en direct par plusieurs mains, une lecture peut tomber pendant une écriture ; une clause qui a l'air générale peut cacher un mot valable pour un seul type — on ne les trouve qu'en lisant la consigne produite en entier, jamais en survolant le code ; et les chemins d'images du référentiel sont relatifs au dossier des images, jamais à la racine du dépôt.

**Le catalogue gelé est débranché** : les deux outils vivants lisent désormais le référentiel des sujets, et l'enregistrement d'une image **ajoute une version** au lieu d'écraser. Les deux modules du catalogue n'ont plus aucun lecteur ; ils ne sont pas supprimés.

**Ce qui reste en vol, à reprendre :**

1. **La page de suivi n'affiche pas le centre de soin.** Elle embarque chaque sprite en pleine définition alors qu'elle ne les montre qu'à vingt-quatre pixels par case : un livrable de seize cases pèse 1,7 Mo pour 384 pixels affichés. Un plafond de 500 ko a été posé en garde-fou, il montre « image trop volumineuse » au lieu d'un cadre vide — mais **la vraie réponse est de fabriquer une vignette à la taille d'affichage**, ce qui fait tomber le poids pour toutes les images et rend le plafond inatteignable. Le bouton œil doit continuer d'ouvrir l'image entière.
2. **Le constructeur de la page échoue en fin de course** : `NameError: name 'UNREADABLE_IMAGES' is not defined`, dans l'étape même qui devait signaler les anomalies au lanceur. La page est pourtant écrite avant l'échec.
3. **Le libellé d'une variante de portillon doit commencer par le portillon**, pas par « Ligne » : ce qui change la nature de la pièce mène le libellé. Un poteau de plus ou de moins, non — une ligne reste une ligne. La règle générale reste à écrire.
4. **Quatre reprises ne sont pas déclarées au référentiel** : `TR-063-v3`, `TR-061-v3`, `OB-010_shape-nw_posts-1-v2`, `OB-010_shape-ew_posts-1-v2`. Chacune devient courante, celle qu'elle remplace passe en antérieure, **et repart sans verdict**. Le pommier et le bosquet atteignent la troisième version : le plafond de trois antérieures se pose, et rien ne se supprime du disque.
5. **Les lots des tracés sont complétés** : cinq dessins à produire — extrémité, ligne, angle, trois branches, croisement —, quinze configurations couvertes par rotation. La distinction est écrite dans le type : ce qu'il faut **dessiner** n'est pas ce qu'une case doit **savoir accepter**. La clôture, qui ne pivote pas, garde ses six formes, plus les quatre variantes de portillon qui sont à produire elles aussi.
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

**Contradiction en attente d'arbitrage** : le sapin isolé. L'opérateur le veut « nettement plus petit que les six cases du bosquet », mais la fiche du bosquet dit que chacun de ses sapins est « à la taille d'un sapin isolé ». Les deux ne peuvent être vrais. Sa fiche n'est pas écrite tant que ce n'est pas tranché.

**Chantiers ouverts en fin de journée du 2026-08-04 :**

- **Les clés de données passent en anglais.** La règle est écrite dans `AGENTS.md` pour que le français cesse de s'étendre ; la migration elle-même est **à faire**, l'opérateur l'a repoussée. Relevé complet : dans le référentiel des sujets — `sujets`, `variantes`, `emprise`, `hauteur`, `passage`, `passage_default`, `profil`, `statut`, `composition`/`compositions` ; dans les jugements — `jugements`, `nom`, `criteres`, `tenu`, `sur`, `rapport`. **Deux points à trancher** : les identifiants de type, employés comme clés (`sol`, `chemin`, `cloture`, `arbre`, `bosquet-arbres`, `herbe`, `batiment`, `humain`), et le mot `note`, identique dans les deux langues mais employé ici au sens français de remarque.
- **Les descriptions d'inventaire passent en français.** Ordre de l'opérateur : toute consigne envoyée au générateur est en français, or la description du sujet y était citée en anglais — le seul fragment qui restait. La règle du README est déjà retournée ; la réécriture d'une centaine de fiches est en cours. Ce n'est pas une traduction mot à mot : le texte doit être aussi concret en français, sans rien perdre ni rien ajouter, en prescription positive.
- **Le catalogue gelé doit être débranché**, pas seulement cessé d'être écrit. Il porte encore tout l'adressage dont dépendent deux outils vivants — `check-asset.py` et `record-asset.py`. Le débranchement ne se fait **qu'après** une correspondance ligne à ligne prouvant que le référentiel des sujets fournit tout ce qu'ils y prennent ; s'il manque quoi que ce soit, c'est le référentiel qui est incomplet, et le compléter est une décision de conception.
- **Le vocabulaire des formes est recopié en dur dans cinq outils**, et cette copie vit dans le module du catalogue gelé. Un détenteur unique le remplace, les autres l'importent — comme les tailles en pixels, qui n'ont plus jamais divergé depuis qu'elles en ont un.
- **Une forme peut porter une qualification** devant ses bords — `gate-ew`, `gate-ns` — parce que deux pièces peuvent relier les mêmes bords sans être le même dessin. Règle écrite dans la conception et au lexique.
- **La toile demandée au générateur épouse la forme réelle du sujet.** Elle se calculait sur le seul sol : un pommier haut de trois cases recevait un carré et s'écrasait. La profondeur au sol se projette presque en vraie grandeur, la hauteur s'écrase au tiers — la caméra est à soixante-dix degrés **sous l'horizontale**, donc près de la verticale. Cette convention est la source d'une erreur commise et corrigée aujourd'hui : elle est désormais écrite noir sur blanc dans le service qui détient les tailles.

- **Le portillon** `OB-010_shape-ew-avec-portillon.png` est **rattaché** au référentiel le 2026-08-04, sur un axe `ouverture` proposé. Deux points attendent l'opérateur : le nom de l'axe, et **le passage** — un portillon se traverse, ce qui renverse la fermeture du type sur les deux côtés reliés.
- **`check-sujets.py` a deux défauts** : il réclame qu'une variante revendique aussi les **maîtres** de `assets/poc/`, alors qu'une variante ne pointe que le livrable de `assets/cutout/` ; et il compte en faute les sondes pourtant déclarées `_hors_referentiel`. Il sort donc en erreur alors que le référentiel est sain.
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
| Commander la sprite d'un sujet isolé | `generate-sprite-subject.py <code>` — lit la fiche à l'inventaire, jamais une copie |
| Commander la sprite d'une pièce de tracé | `generate-sprite-trace.py <code> <forme>` (composition, référence) |
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

- **Le suivi des sprites** — tous les sujets groupés par type, chaque profil, chaque variante attendue avec son état (prévue, en production, produite, en défaut), un panneau de comptes en tête, et des actions par variante qui alimentent un récapitulatif copiable. C'est l'unique endroit où se lit l'état de la production.
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
| *Suivi des sprites — doublon créé par erreur* | https://claude.ai/code/artifact/ddefc8b7-0f50-45ef-ad51-68c64b5ef1bd | **à supprimer par l'opérateur — ne jamais republier dessus** |
| **Le parc** — plan de composition et maquette montée, commentaire par zone | *pas encore créé* | à ouvrir avec la maquette B0 |

## Ce qui attend l'opérateur

- L'arbitrage du **lot v0** de la maquette B0.
- À terme : l'arbitrage de la contradiction lumière référence/bande, et le sort des fiches créatures dérivantes — tous deux hors chemin du POC.
