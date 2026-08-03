# Format de composition d'une planche

**Intention :** décrire une planche assez rigoureusement pour qu'elle soit **reproductible** et **vérifiable**. Une description en prose produit une image différente à chaque tentative ; une composition dans ce format décrit un plan, pas une ambiance.

Ce format est une convention interne. Il se lit de haut en bas : ce qui est écrit en premier est posé en premier, et rien de ce qui suit ne le contredit.

## Règles de placement

- La planche est une grille de **32 colonnes sur 24 rangées**. **Une case vaut un mètre.**
- **Échelle de référence : un adulte debout fait entre 1,75 et 2 cases de haut.** C'est une fourchette, pas une valeur exacte — mais jamais au-dessus de 2 cases ni en dessous de 1,75. Assis, accroupi ou penché, il occupe proportionnellement moins de haut. Il occupe **une seule case au sol** — qu'il ne remplit d'ailleurs pas entièrement. C'est la mesure qui vérifie tout le reste ; elle a dérivé à chaque tour et se contrôle en premier, grille affichée.
- **Aucune créature ni aucun humain ne se décrit librement dans une consigne** : chaque habitant cite sa fiche — [créatures témoins](../contenu/creatures-temoins.md), [personnages témoins](../contenu/personnages-temoins.md) — mot pour mot. Une scène qui a besoin d'une espèce ou d'un personnage nouveau commence par sa fiche.
- Une créature de base occupe une case au sol et **une case de haut** environ ; les grandes créatures dépassent.
- **Une porte se franchit** : au moins **deux cases et demie de haut** et une case de large, faute de quoi le bâtiment est faux quelle que soit son emprise. Toute ouverture praticable respecte cette règle.
- **Aucun bâtiment n'est étroit** : une construction habitable fait au moins **huit cases dans sa plus petite dimension**. Une maison de deux ou trois cases de large n'existe pas, quelle que soit sa longueur : personne ne bâtit un couloir de deux mètres de large.
- **Une construction humaine fait forcément plus d'une case.** Une case fait un mètre : on ne peut pas y tenir un étal, un appentis ou tout ouvrage bâti. Dans une case, on peut mettre des sacs, une chaise, un tonneau — pas un étal. Demander l'impossible dans une composition produit une image incohérente avec son plan : chaque emprise se vérifie contre ce que sa taille réelle permet.
- **Toute créature au contact de l'eau voit sa relation à l'eau précisée** : *sous l'eau*, *nageant en surface*, *pattes dans l'eau touchant le fond*, *sur la berge*, *survolant l'eau*. Sans cette mention, une créature aquatique finit posée sur la surface comme sur un sol.
- **Une surface habitable est réaliste** : l'emprise au sol se lit directement en mètres carrés. Un bâtiment de deux cases sur deux fait quatre mètres carrés — personne n'y habite. Une maison familiale ne descend pas sous une centaine de mètres carrés au sol. Il ne s'agit pas de bâtir des palais, mais l'espace se voit dans le jeu : il doit être crédible.
- Une position s'écrit `(colonne,rangée)`, l'origine `(1,1)` étant en haut à gauche.
- Une **emprise** s'écrit `(c1,r1)-(c2,r2)` et décrit le **sol occupé**. Elle est **pleine** : la silhouette atteint les bords de son rectangle.
- **Un arbre peut faire plusieurs cases** — décision du propriétaire : les arbres ne sont pas limités à une case au sol ; un grand arbre déclare son emprise multi-cases comme un bâtiment, en plus de sa projection de houppier.
- **Un enclos n'est pas un bâtiment** : ce sont juste des murs — on voit ce qu'il y a dedans. Il se décrit et se représente différemment d'un bâtiment (murs et portillon, intérieur visible), sur les plans comme dans les consignes.
- **Un ravin n'est pas une source d'eau, et ce n'est pas un ruisseau : c'est une crevasse** — une entaille profonde et rocheuse dans le sol, réellement dangereuse, qu'on ne franchit que par un pont. Il peut être sec ou porter un torrent tout au fond, mais il se lit d'abord comme un gouffre, jamais comme un cours d'eau posé sur le sol. Et tout cours d'eau, où qu'il soit, vient de quelque part et va quelque part : il entre par un bord, sort par un bord, ou naît d'une source explicite.
- **Pin ≠ sapin** : les deux essences se nomment et se décrivent distinctement ; demander l'une ne doit pas produire l'autre.
- **Rien n'empiète sur les cases voisines vers le bas, la gauche ou la droite.** Seule la hauteur déborde vers le haut de l'écran, puisqu'un bâtiment haut se dresse au-dessus de son emprise et masque ce qui est derrière.
- Tout est **droit** : bâtiments, clôtures et cultures suivent les axes de la grille. Deux éléments voisins peuvent s'accorder — un appentis contre un mur, une haie le long d'un champ — sans jamais se chevaucher.

## Structure d'une composition

1. **Biome** — le code `BI-nnn`.
2. **Raccords de bord** — pour chaque bord concerné : le côté, la rangée ou la colonne, la largeur en cases, la nature du sol. Un raccord touche franchement le bord.
3. **Voies** — chemins et cours d'eau, tracés en premier, avec leur code de sol, leur largeur, leur parcours de case en case, et pour l'eau son sens d'écoulement.
4. **Ouvrages d'eau** — ponts, gués, passerelles : emprise, et le chemin auquel chaque extrémité aboutit.
5. **Bâtiments** — code, emprise, orientation de la façade, position de la porte, et le chemin qui la dessert. **Règle globale, toutes planches : tout bâtiment est connecté au réseau de chemins** — un chemin relie sa porte au réseau, sans exception ; un bâtiment isolé sans desserte n'existe pas. (En bourg s'ajoute la règle locale : tout bâtiment non mitoyen est entouré de pavés.)
6. **Aménagements** — clôtures, cultures, enclos : emprise et contenu.
7. **Végétation** — code, position, et **état chiffré** (voir ci-dessous).
8. **Objets** — code et position.
9. **Habitants** — humains, animaux, créatures : code, position, ce qu'ils font, où ils regardent, où ils vont.

**Les angles de vue varient.** Défaut récurrent constaté sur toutes les images : les humains ne regardent jamais vers le bas, et les créatures qui le font le font toujours en diagonale. Chaque composition varie donc les orientations sur l'ensemble de ses habitants — dont, explicitement, des humains regardant vers le bas (face caméra) et des créatures de face, pas seulement en diagonale.

## L'état chiffré : ne jamais nommer un élément sans le qualifier

Demander « un pommier » laisse tout ouvert. Chaque élément vivant ou périssable porte donc un **état mesuré**, exprimé en proportion ou par un mot d'une échelle fermée :

- **Fructification** — `fruits 0 %`, `30 %`, `80 %`, `100 %` : proportion des branches portant des fruits.
- **Saison de floraison** — `en fleurs`, `défleuri`, `nu`.
- **Feuillage** — `dense`, `clairsemé`, `nu`.
- **Maturité** — `jeune`, `adulte`, `vieux`, `mort`.
- **Entretien** — `soigné`, `négligé`, `envahi`.
- **État d'ouvrage** — `neuf`, `usé`, `abîmé`, `en ruine`.
- **Remplissage** — pour un contenant, un champ, un séchoir : `vide`, `au tiers`, `à moitié`, `plein`.

La règle vaut au-delà des exemples : si une propriété peut varier et se voir, elle se déclare.

## Variété imposée

- **Les arbres fruitiers ne sont jamais d'une seule espèce.** Un verger mêle pommiers, poiriers, pruniers, cerisiers, cognassiers, figuiers selon le biome, à des états de fructification différents.
- **Deux individus d'une même espèce ne sont pas identiques** : taille, teinte, port, âge, posture varient, comme entre deux chiens d'une même race. Cela vaut pour les arbres, les animaux et les créatures.
- **Aucun animal réel n'existe dans ce monde — règle absolue.** Ni mouton, ni vache, ni chien, ni canard, ni héron, ni oiseau, ni insecte reconnaissable. Le vivant animal, c'est **les créatures**, et rien d'autre. Une image qui contient un animal réel est fausse, quelle que soit sa qualité par ailleurs.
- **Une créature peut s'inspirer d'un animal réel**, jamais le copier ni le reprendre tel quel : l'inspiration donne une silhouette lointainement familière, la copie donne un animal repeint. Une créature reste une invention.
- **Une créature s'inspire de ce qu'on veut** — faune réelle, créatures fantastiques, plantes, minéraux, objets, ou rien du tout. Aucune obligation de ressemblance avec le vivant réel ; l'invention prime.

## Le dénombrable et l'habillage

La composition est **exhaustive sur le dénombrable** : personnages, créatures, bâtiments, ouvrages, véhicules, arbres, objets. Ce qui n'y figure pas ne doit pas apparaître — un élément surnuméraire fausse le compte, l'échelle et la cohérence, et rend la planche irreproductible.

Elle ne l'est pas sur l'**habillage** : touffes d'herbe, fleurs des champs, cailloux, mousses, brindilles, rides de sable, feuilles au sol. Cette matière de fond ne se compte pas une à une — mais sa quantité, elle, est **chiffrée** : **au plus une case sur cinq porte de l'habillage**, les quatre autres restant en surface unie. La direction artistique est simple : de larges surfaces unies, un habillage qui ponctue au lieu de couvrir. Un sol semé de touffes et de fleurs partout devient un fouillis qui écrase les éléments qui comptent. **En cas de doute, on en met moins.** Une fleur est de l'habillage ; un arbre fruitier n'en est pas.

Le mot « épars » ne suffit pas : employé seul, il a produit tantôt le vide, tantôt un tapis continu. La proportion se donne toujours en chiffres.
