# L'angle de vue — le standard du projet

**Usage :** la définition unique de la prise de vue, pour tout ce qui se dessine — sprites et planches de référence. On la cite telle quelle dans une consigne, et on s'y réfère plutôt que de la
redécrire.

**Intention :** une prise de vue qui varie d'une image à l'autre rend le monde inassemblable. Ce document fixe **une** géométrie, en termes qu'un dessinateur peut appliquer et qu'une mesure peut
vérifier. Il ne couvre ni la lumière, ni le style, ni le cadrage : chacun a sa propre définition ([index visuel](index.md)).

## Les quatre règles, et elles sont indissociables

- **La projection est PARALLÈLE. Aucun point de fuite, aucune convergence.** Deux exemplaires du même sujet posés à deux endroits d'une image sont **strictement identiques** — c'est la formulation
  vérifiable de la règle, et c'est ce qu'une épreuve mesure. Une perspective centrale ferait dépendre le dessin de la position : le bâtiment de gauche montrerait sa face droite, celui de droite sa
  face gauche, et une sprite deviendrait fausse en changeant de case.
- **La caméra plonge de SOIXANTE DEGRÉS sous l'horizontale**, donc à trente degrés de la verticale. On voit largement le dessus des choses, et un peu leur face avant. Cet angle ne varie jamais ;
  seul le niveau de zoom change. Avec la projection parallèle ci-dessus, l'ensemble se dit **projection parallèle à 60 degrés de plongée (PA60)**, et c'est sous ce sigle que l'opérateur le demande.
  **Décision de l'opérateur, 2026-08-07, définitive et jamais à reposer** : la valeur était de soixante-dix degrés, elle est de soixante pour tout le projet et pour tout sujet.
- **Aucune rotation autour de la verticale.** On regarde droit dans l'axe de la grille : les murs suivent les axes de la carte, un bâtiment fait face à la caméra, jamais en biais. Ce n'est donc pas
  une vue isométrique — la grille reste un quadrillage droit, pas un losange.
- **Ce que la caméra écrase, et de combien.** Une longueur **au sol, en profondeur** se projette à quatre-vingt-sept centièmes de sa mesure. Une longueur **dressée** se projette à **cinquante
  centièmes** — elle s'écrase exactement de moitié. Une longueur **en largeur** ne s'écrase pas du tout. Ces trois facteurs sont les sinus et cosinus de l'angle, et ils vivent dans le
  service qui détient les tailles, jamais recalculés ailleurs.

## Ce qui doit se voir dans l'image, et qui se contrôle à l'œil

- Les arêtes **verticales** d'un volume restent **verticales** dans l'image, et **parallèles entre elles** — jamais convergentes.
- Les arêtes qui **fuient vers le fond** sont **parallèles entre elles**, sur toute l'image.
- **Pas d'horizon, pas de ciel** : le sol occupe tout le cadre.
- Un même sujet dessiné deux fois dans une image montre **les deux mêmes faces**, à la même inclinaison et à la même largeur apparente.

## Ce que ça change pour les planches de référence

**Les six planches actuelles ne respectent pas ce standard** : ce sont des scènes uniques, rendues avec un point de fuite, où les bâtiments de gauche montrent leur face droite et ceux de droite leur
face gauche. Elles restent la référence du **style, de la matière et de la lumière** — et cessent d'être celle de la prise de vue. Toute planche produite désormais applique ce document.

## Une planche du monde en référence RAMÈNE SA PERSPECTIVE — constaté le 2026-08-07

**Un sujet produit avec une planche du monde en référence converge**, même quand sa description lui interdit explicitement d'être vu de biais et que le socle de la consigne lui dit d'ignorer la
perspective de la scène. Constaté sur le centre de soin : ses deux ailes penchaient l'une vers l'autre, la clause de face était pourtant écrite dans sa fiche, et redite. **La planche montre un point
de fuite, et c'est ce qu'il reprend** — ce qu'il voit pèse plus lourd que ce qu'on lui écrit.

**Le même sujet produit avec SA PROPRE SPRITE en référence tient la projection parallèle.** Même description, même socle, seule la référence change : les arêtes verticales redeviennent parallèles.

**La règle qui en découle** : dès qu'un sujet a une image de lui-même, c'est elle qu'on lui donne en référence, jamais une planche du monde. La planche ne sert qu'au tout premier dessin d'un sujet,
quand rien n'existe encore de lui — et ce premier dessin se regarde sur sa projection avant d'être inscrit, précisément parce qu'il a été produit dans ces conditions-là.

## Ce qui est constaté, pas supposé

**Le générateur tient cette projection quand la consigne la lui demande en toutes lettres** — épreuve du 2026-08-06 : le même cabanon cubique répété cinq fois sur une rangée, les cinq copies montrant
les deux mêmes faces au même angle, silhouettes de 84 à 85 pixels de large pour 90 à 91 de haut. **Il ne redessine jamais deux fois la même chose à l'identique** : entre deux copies d'une même image,
un cinquième à un quart des pixels diffèrent. La cohérence d'un assemblage ne peut donc pas reposer sur la ressemblance de deux générations séparées.
