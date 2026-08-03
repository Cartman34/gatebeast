# Assets

**Intention :** transformer la direction artistique validée et l'inventaire des éléments en **images réellement posables dans le jeu**, à un coût maîtrisé et de façon rejouable. Sans ce nœud, chaque besoin d'image rouvre la question du cadrage, de la taille, du nombre de vues et du contrôle — et le jeu se peuple d'images qui ne s'assemblent pas.

Ce nœud couvre ce qu'est un asset livrable, les lots attendus par famille et la chaîne qui les fabrique et les contrôle. Il exclut le style lui-même ([visuel](../index.md)), la composition d'une scène ([format de composition](../format-de-composition.md)), l'empilement à l'écran ([rendu en calques](../../technique/rendu-en-calques.md)) et la description des éléments ([inventaire](../inventaire/README.md)).

## Décisions

- **Rien ne se produit sans fiche** — une image ne se demande que pour un **profil** inscrit à l'[inventaire](../inventaire/README.md), avec son code stable et sa description de référence. Un profil absent de l'inventaire s'y écrit d'abord. Écarté : produire d'après une description improvisée (le profil n'est ni reproductible, ni adressable, ni réutilisable).
- **Un asset livrable est une image détourée, mesurée et inscrite** — le livrable n'est pas ce que rend le générateur : c'est une image **à fond transparent**, rognée à la silhouette, accompagnée de son **emprise au sol** et de son **point de pose** mesurés, et inscrite au **catalogue**. Le fond de fabrication magenta est un intermédiaire interne, jamais un livrable. Écarté : livrer l'image brute du générateur (ni transparente, ni mesurée, inutilisable telle quelle — [capacités constatées](../../technique/index.md)).
- **La taille produite se constate, elle ne se commande pas** — le générateur décide seul des dimensions de son image ; la conception n'en dit rien et ne raisonne jamais en pixels. Ce qui fait foi est l'emprise en cases, et c'est le rendu qui met à l'échelle. Écarté : imposer une taille de sortie (constaté sans effet) ; définir les assets en pixels (les rend dépendants d'un moteur et d'un écran).
- **La vue principale d'abord, les autres en cascade** — la vue principale d'un profil est produite et validée avant toute autre variante, puis fournie comme référence visuelle à chacune. C'est la règle de cohérence déjà établie pour les planches ([visuel](../index.md)), et la dépendance qui structure la chaîne. Écarté : produire toutes les variantes d'un profil en parallèle et à l'aveugle (elles divergent entre elles).
- **Deux périmètres tenus en parallèle, jamais confondus** — la **cible** est le jeu complet : tous les types, les orientations, les actions d'animation et d'évènement. La **v0** est un sous-ensemble volontairement pauvre : un seul profil de créature réutilisé partout, le lot minimal de chaque type ([lots de variantes](lots-de-variantes.md)). Le catalogue étant le contrat, le moteur se développe contre des profils au lot partiel et les images définitives s'y substituent sans toucher au code. Écarté : attendre un jeu d'assets complet avant de développer (immobilise le moteur pour des mois).
- **Ce qu'un contrôle mécanique ne voit pas se contrôle par jugement** — le fond, le cadrage, la taille et la régularité se mesurent ; l'angle de caméra, la conformité au style et la fidélité à la fiche ne se mesurent pas, et ce sont précisément les écarts constatés sur les premières sondes. La chaîne porte donc les deux contrôles, dans cet ordre ([chaîne de production](chaine-de-production.md)). Écarté : s'en remettre aux seules mesures (elles déclarent bonne une image hors direction artistique).

- **Un sujet isolé se voit sous la vue standard des sprites** — moins plongeante que la carte, c'est celle sous laquelle les six planches de référence ont été produites, et celle qui permet à une sprite de se poser sur le monde sans paraître collée. Décision du propriétaire, constatée conforme sur les premières sondes.

## Questions ouvertes

Aucune à ce niveau.

## Sous-niveaux

- [sujets-et-variantes.md](sujets-et-variantes.md) — le vocabulaire précis : sujet, type, profil, variante, orientation et directions, et le repli.
- [lots-de-variantes.md](lots-de-variantes.md) — ce que chaque type doit livrer, en cible et en v0.
- [chaine-de-production.md](chaine-de-production.md) — de la fiche au catalogue : les étapes, les contrôles, la reprise et le rendu au propriétaire.
