# Planches de référence

Ces planches ne sont pas le monde du jeu : elles **figent la direction artistique** sur beaucoup de contenu, pour qu'elle soit reproductible ensuite. La direction est **validée par le propriétaire (2026-08-03)** sur les six planches en l'état — imperfections assumées, améliorées individuellement plus tard, hors du chemin du POC.

**Intention :** une seule scène ne suffit pas à fixer un style. Six planches de biomes différents, sans aucun élément commun, montrent comment la direction se comporte sur des matières, des architectures et des lumières variées.

## Disposition d'ensemble

Six planches, chacune de 1536 × 1152 pixels et 32 × 24 cases, disposées en deux rangées de trois :

| | colonne 1 | colonne 2 | colonne 3 |
|---|---|---|---|
| **rangée haute** | P1 campagne boisée | P2 bourg | P3 contreforts |
| **rangée basse** | P4 marais | P5 falaise | P6 plage |

**Raccords : chaque planche se raccorde à toutes ses voisines.** Un raccord se fait toujours à la **même rangée ou colonne des deux côtés**, sur **une case de large**, et **touche franchement le bord** de l'image. Le **revêtement peut changer d'un biome à l'autre** — une route de terre devient passerelle en entrant dans le marais, rue pavée en entrant en ville : c'est même souhaitable. Seuls la position et le fait d'atteindre le bord se raccordent.

| Raccord | Sortie | Entrée |
|---|---|---|
| P1 ↔ P2 | P1, bord droit, rangée 16 | P2, bord gauche, rangée 16 |
| P2 ↔ P3 | P2, bord droit, rangée 8 | P3, bord gauche, rangée 8 |
| P4 ↔ P5 | P4, bord droit, rangée 12 | P5, bord gauche, rangée 12 |
| P5 ↔ P6 | P5, bord droit, rangée 20 | P6, bord gauche, rangée 20 |
| P1 ↕ P4 | P1, bord bas, colonne 12 | P4, bord haut, colonne 12 |
| P2 ↕ P5 | P2, bord bas, colonne 18 | P5, bord haut, colonne 18 |
| P3 ↕ P6 | P3, bord bas, colonne 26 | P6, bord haut, colonne 26 |

**Une créature majestueuse par planche.** Chaque planche montre **une** créature rare, remarquable par son allure plus que par sa taille. Au repos, **deux cases au sol** suffisent ; certaines espèces montent plus haut, et une envergure déployée — ailes, membranes, panache — peut occuper davantage sans que l'emprise au sol change. Elle porte sa rune comme les autres. C'est le pendant des créatures rares du genre : elle donne à chaque lieu une raison d'être exploré. Écarté : une créature géante systématique (elle écrase la scène et banalise la rareté).

**Toutes les planches sont également et fortement lumineuses** — décision du propriétaire : la luminosité ne varie pas d'un biome à l'autre et ne baisse jamais d'une version à l'autre. Cible chiffrée, vérifiée à la mesure après chaque tir : **luminance entre 115 et 130, part sombre au plus 10 %**. La lumière se prescrit positivement : soleil franc, ombres courtes et pâles, toits et façades éclairés — jamais par le seul interdit du sombre.

**Pas plus d'une case sur sept sombre, l'eau comprise.** La contrainte porte sur la planche entière et compte l'eau comme le reste : c'est l'eau, en couvrant de grandes surfaces, qui a fait basculer la mesure. Une planche qui dépasse ce seuil est fautive quelle que soit sa composition.

**Le plancher de charge visuelle dépend du biome.** Une plage ou un plateau rocheux sont naturellement plus vides qu'un bourg ou un marais. La consigne donne donc une **fourchette par biome**, jamais un simple maximum : une planche trop vide est aussi fautive qu'une planche fouillie.

## Règles communes à toutes les planches

Cadre, caméra, lumière, ombres, netteté, échelle et emprises : voir la [scène de référence](scene-de-reference.md), qui fait foi. Direction artistique unique, identique sur les six.

- **Variété maximale, répétition minimale** : essences d'arbres différentes, natures de chemins différentes (terre, pavés, planches, pierres, sable damé), bâtiments tous distincts — y compris deux maisons entre elles.
- **Humanité réelle** : toutes origines, tous genres, métiers visibles et variés.
- **Créatures nombreuses et différentes**, chacune portant sa rune selon les règles établies.
- **Cohérence interne, sans exception** : rien ne se termine dans le vide. Un pont aboutit à un chemin, ou bien il est cassé et le chemin s'interrompt aussi. Une porte donne sur un accès, un escalier mène quelque part, une barque est amarrée ou tirée sur le sable.
- **Le monde a vécu** : usure, mousse, lichen, végétation qui reprend ses droits.

## Contenu par planche

- **P1 campagne boisée** — fermes, moulin, vergers, clairières, haies, mare, chemins de terre.
- **P2 bourg** — rues pavées, place, halle couverte, échoppes, ateliers, maisons mitoyennes toutes différentes, fontaine. Parmi les habitants : le forgeron, la boulangère et le garde de la première version, qui ne doivent pas se perdre. **Les pavés joignent les bâtiments** : tout bâtiment non mitoyen est **entouré de pavés**, et un chemin pavé le **connecte toujours au réseau** des rues ; la verdure occupe les espaces entre ces abords pavés, jamais la place ni les rues.
- **P3 contreforts** — pentes rocheuses, pins (de vrais pins, pas des sapins), **forêt plus dense**, bergerie avec son enclos représenté en murs à intérieur visible, entrée de mine, pont suspendu sur un torrent qui traverse la planche de bord en bord, ruines, sentiers en lacets.
- **P4 marais** — **eaux claires**, fond visible par transparence, passerelles de bois, huttes sur pilotis, arbres tordus. **Ni eau brune, ni brume au sol** : une eau sombre couvrant une large part de la planche fait chuter luminance et saturation d'un coup, et la brume grise tout le reste. **Chargée en verdure autant que le premier passage du marais** (`planche-p4-marais.png`) : plus d'algues, plus de roseaux, plus de plantes, plus d'arbres de mangrove et plus de grands arbres — l'eau claire ne signifie pas une planche vide ou pâle. Le séchoir est un **séchoir à récoltes du marais** (algues, joncs) : un monde sans poissons ne sèche pas de poissons, et une consigne n'emploie jamais le mot *fish*.
- **P5 falaise** — plateau herbeux, escalier taillé, phare (élancé, pas bulbeux), cabanons, filets à sécher, à-pic vers la mer ; **inspiration : la Bretagne**. Peuplée : davantage de créatures et d'humains, et du fouillis de bord de mer (rochers, ajoncs, bois flotté). Le plan doit lever toute ambiguïté sur l'emprise de la falaise.
- **P6 plage** — sable, dunes, appontement, cabanes de pêcheurs, barques, casiers, rochers, écume. Végétation présente : palmiers, Malcolmie des côtes (*Malcolmia littorea*) et d'autres plantes ; des coquillages sur le bord de l'eau.

## État

P1 et P2 produites en premier, pour éprouver le raccord et la tenue de la direction sur deux biomes très différents. Les quatre autres suivront une fois celles-ci validées.
