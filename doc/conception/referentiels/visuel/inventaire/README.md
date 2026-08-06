# Inventaire des éléments

**Statut : esquisse.** L'inventaire se construit ; rien n'y est validé tant que l'opérateur n'a pas vu l'élément rendu.

**Intention :** pouvoir **désigner** et **reproduire** n'importe quel élément du monde. Sans inventaire, chaque image réinvente ses arbres, ses maisons et ses passants, et rien n'est réutilisable. Avec lui, une image se compose en citant des codes.

## Le code

`XX-nnn` : deux lettres de famille, trois chiffres. Le code est **stable à vie** — il ne change jamais, même si l'élément est renommé, redessiné, ou retiré. C'est lui que citent les consignes de production, les fichiers et le code du jeu.

| Famille | Code | Ce qu'elle contient |
|---|---|---|
| Créatures | `SP-nnn` | Espèces, avec leurs individus `SP-nnn-i` — voir [créatures](../../contenu/creatures-temoins.md) |
| Bâtiments | `BT-nnn` | Constructions habitables ou fonctionnelles — [batiments.md](batiments.md) |
| Végétation | `TR-nnn` | Arbres, arbustes, cultures, herbes — [vegetation.md](vegetation.md) |
| Sols et chemins | `CH-nnn` | Revêtements, sentiers, sols naturels — [sols-et-chemins.md](sols-et-chemins.md) |
| Objets | `OB-nnn` | Mobilier, outillage, aménagements, épaves — [objets.md](objets.md) |
| Personnages | `PR-nnn` | Humains, par silhouette et métier — [personnages.md](personnages.md) |
| Biomes | `BI-nnn` | Ambiances de terrain — [biomes.md](biomes.md) |

## Ce que porte chaque entrée

- **Code** `XX-nnn` — il fait foi, et ne change jamais.
- **Libellé** — le nom du sujet en mots humains, court et clair : « herbe verte avec rosée », « barrière en rondins ». Il ne sert **jamais** à la génération : il sert à reconnaître le sujet d'un coup d'œil, dans l'inventaire comme dans une conversation. **Il ne nomme jamais un lieu** — « chêne de parc » est proscrit, le même chêne servira ailleurs. Mentionner un **biome** reste possible, sans être attendu : cela ne se justifie que si le sujet est vraiment propre à ce biome.
- **L'essence, l'espèce ou la matière est nommée** dès qu'elle existe : on écrit « pommier », « bosquet de sapins », jamais « petit arbre » ni « bosquet dense ». Un sujet qu'on ne sait pas nommer n'est pas encore décrit.
- **Nom de profil** — l'identifiant construit, en anglais américain, minuscules, de la forme `sorte-nn` : `oak-01`, `log-fence-01`. C'est lui que portent les dossiers et les adresses d'images.
- **Type** — la sorte de chose dont il s'agit, qui décide de son lot de variants et de son calque ([sujets et variants](../assets/sujets-et-variantes.md)).
- **Description en français** — reprise **mot pour mot** dans les consignes de production. C'est elle qui garantit la reproductibilité, et elle seule décrit ce qui se dessine. **Une espèce qui naît ou qui change reçoit une description entièrement réécrite** : on peut s'inspirer de ce qui a déjà été produit, jamais reprendre le texte d'une autre fiche — un texte hérité traîne ses défauts, ses tournures négatives et ses traits qui ne valaient que pour l'ancien sujet.
- **Une description ne laisse aucune ambiguïté — sans exception et en toute circonstance.** Ce qui se dessine est **nommé**, jamais suggéré : la couleur, la forme, les proportions chiffrées, ce qui est visible et ce qui ne l'est pas. Une description qui laisse le choix laisse le générateur choisir, et il choisit ce qu'il connaît plutôt que ce qu'on lui demande. Deux tournures à proscrire parce qu'elles n'engagent rien : « quelques », « une sorte de ».
- **Une image de référence se donne au générateur AVEC la description**, jamais à sa place — elle porte la matière, la couleur et la lumière, la description porte ce qu'il faut dessiner. Les deux ne se contredisent jamais : si elles divergent, c'est la description qui est à corriger, puisque c'est elle qu'on écrit.
- **Une référence se regarde avant d'être décrite.** Ce qu'on écrit d'une image est ce qu'elle montre, jamais ce qu'on sait du sujet en général. Constaté : un sapin décrit de mémoire a reçu une jupe de branches balayant le sol, là où la planche montre un tronc nu sur un cinquième de la hauteur et une couronne basse qui se raccourcit. Trois générations n'ont pas rattrapé la description fausse. Regarder de près — un extrait agrandi — coûte quelques secondes.
- **Description propre à une valeur ou une forme** — optionnelle : une fiche peut réécrire sa description pour une valeur ou une forme précise (le portillon d'une clôture, par exemple), introduite par la formule fixe « Description propre à la valeur `X` » ou « Description propre à la forme `X` », suivie de sa propre description en italique. Cette formule est un repère de mise en forme de la fiche, jamais un mot que la description choisit : c'est elle, et elle seule, qui distingue une description à citer pour cette valeur précise d'un texte explicatif ordinaire.
- **Emprise** en cases, **toujours écrite, sans exception ni valeur par défaut**. C'est un élément descriptif nécessaire au même titre que la description : sans elle, on ne sait ni quelle place le sujet prend au sol, ni quelle définition demander au générateur, et chaque outil devine à sa façon. Une emprise qu'on ne lit que chez les sujets qui s'écartent de l'ordinaire est une règle implicite portée par ses exceptions — donc une règle qui se perd. **Un arbre de taille normale occupe une case** ; au-delà, c'est un grand arbre, et son libellé le dit.
- **Hauteur** en cases, **toujours écrite, sans exception ni valeur par défaut**, au même titre que l'emprise. L'emprise dit la place prise au sol, la hauteur dit ce qui se dresse au-dessus — et c'est elle qui fixe la proportion de l'image demandée au générateur. Sans elle, la consigne impose une hauteur arbitraire, et le sujet arrive écrasé ou étiré. Elle s'exprime dans la même unité que l'emprise, décimales comprises : un sapin fait six cases de haut, une clôture n'en fait pas une, une matière de sol n'en fait aucune. L'échelle humaine sert de repère — un humain debout mesure 1,75 à 2 cases.
- **Où il apparaît** — les biomes ou planches concernés.

## Élément, instance et situation

Une entrée décrit un **type**, jamais une apparition précise. Une apparition est une **instance**, notée `CODE @ planche (colonne,rangée)`, avec ce qu'elle fait et son orientation. Les instances vivent dans la fiche de la planche, jamais ici : un même type se retrouve dans dix situations sans être décrit dix fois.

Un **variant** d'un type reçoit son propre code, jamais un suffixe : deux maisons différentes sont deux entrées, parce qu'on doit pouvoir les demander séparément.

## Règles de tenue

- Une famille par fichier ; si un fichier dépasse deux cents lignes, il se scinde par sous-famille et le README l'indique.
- Les numéros ne se réutilisent jamais, même après retrait. Un élément retiré reste listé avec la mention **retiré** et la raison.
- Un élément n'entre dans l'inventaire qu'avec sa description anglaise complète : une entrée sans description ne sert à rien, puisqu'elle n'est pas reproductible.
