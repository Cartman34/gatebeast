# L'angle de vue — le standard du projet

**Usage :** la définition unique de la prise de vue, pour tout ce qui se dessine — sprites et planches de référence. On la cite telle quelle dans une consigne, et on s'y réfère plutôt que de la
redécrire.

**Intention :** une prise de vue qui varie d'une image à l'autre rend le monde inassemblable. Ce document fixe **une** géométrie, en termes qu'un dessinateur peut appliquer et qu'une mesure peut
vérifier. Il ne couvre ni la lumière, ni le style, ni le cadrage : chacun a sa propre définition ([index visuel](index.md)).

## Les quatre règles, et elles sont indissociables

- **La projection est PARALLÈLE. Aucun point de fuite, aucune convergence.** Deux exemplaires du même sujet posés à deux endroits d'une image sont **strictement identiques** — c'est la formulation
  vérifiable de la règle, et c'est ce qu'une épreuve mesure. Une perspective centrale ferait dépendre le dessin de la position : le bâtiment de gauche montrerait sa face droite, celui de droite sa
  face gauche, et une sprite deviendrait fausse en changeant de case.
- **La caméra plonge de SOIXANTE-DIX DEGRÉS sous l'horizontale**, donc à vingt degrés de la verticale. On voit largement le dessus des choses, et un peu leur face avant. Cet angle ne varie jamais ;
  seul le niveau de zoom change.
- **Aucune rotation autour de la verticale.** On regarde droit dans l'axe de la grille : les murs suivent les axes de la carte, un bâtiment fait face à la caméra, jamais en biais. Ce n'est donc pas
  une vue isométrique — la grille reste un quadrillage droit, pas un losange.
- **Ce que la caméra écrase, et de combien.** Une longueur **au sol, en profondeur** se projette à quatre-vingt-quatorze centièmes de sa mesure — presque en vraie grandeur. Une longueur **dressée**
  se projette à trente-quatre centièmes — elle s'écrase au tiers. Une longueur **en largeur** ne s'écrase pas du tout. Ces trois facteurs sont les sinus et cosinus de l'angle, et ils vivent dans le
  service qui détient les tailles, jamais recalculés ailleurs.

## Ce qui doit se voir dans l'image, et qui se contrôle à l'œil

- Les arêtes **verticales** d'un volume restent **verticales** dans l'image, et **parallèles entre elles** — jamais convergentes.
- Les arêtes qui **fuient vers le fond** sont **parallèles entre elles**, sur toute l'image.
- **Pas d'horizon, pas de ciel** : le sol occupe tout le cadre.
- Un même sujet dessiné deux fois dans une image montre **les deux mêmes faces**, à la même inclinaison et à la même largeur apparente.

## Ce que ça change pour les planches de référence

**Les six planches actuelles ne respectent pas ce standard** : ce sont des scènes uniques, rendues avec un point de fuite, où les bâtiments de gauche montrent leur face droite et ceux de droite leur
face gauche. Elles restent la référence du **style, de la matière et de la lumière** — et cessent d'être celle de la prise de vue. Toute planche produite désormais applique ce document.

## Ce qui est constaté, pas supposé

**Le générateur tient cette projection quand la consigne la lui demande en toutes lettres** — épreuve du 2026-08-06 : le même cabanon cubique répété cinq fois sur une rangée, les cinq copies montrant
les deux mêmes faces au même angle, silhouettes de 84 à 85 pixels de large pour 90 à 91 de haut. **Il ne redessine jamais deux fois la même chose à l'identique** : entre deux copies d'une même image,
un cinquième à un quart des pixels diffèrent. La cohérence d'un assemblage ne peut donc pas reposer sur la ressemblance de deux générations séparées.
