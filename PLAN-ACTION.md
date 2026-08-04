# Plan d'action — GateBeast

**Intention :** dire dans quel ordre la cible se rejoint. Ce document n'est pas la conception : il n'invente rien, il découpe la cible en versions livrables et stables. Il change à chaque livraison, la conception non.

Règle de version héritée du [référentiel technique](doc/conception/referentiels/technique/index.md) : une version reste en `1.0.*` tant qu'aucun ajout majeur n'y entre. Les versions **0.x** précèdent le jeu proprement dit : ce sont des preuves de concept, pas des versions jouables au sens plein.

## 0.1 — La preuve de concept

**Objet :** éprouver le rendu, l'ambiance, l'échelle et le socle technique. Ce n'est pas un jeu : rien ne s'y gagne, rien ne s'y garde. On regarde si le monde tient debout et si s'y promener est agréable.

**Contient :** une carte **bornée**, bâtie sur une grille invisible ; le personnage-joueur, qui **sort du centre de soin** au démarrage — aucun menu, aucun écran titre ; le déplacement fluide au clavier ; une caméra en suivi continu ; des créatures et des personnages non joueurs qui vivent, se croisent et interagissent entre eux, **en nombre** — la preuve de concept assume une population dense, pour éprouver le rendu et la vie du monde ; **rarement et irrégulièrement**, un personnage non joueur sort une créature de sa gateball ou l'y fait rentrer — juste assez pour intriguer, jamais assez pour devenir un spectacle ; un seul moteur de rendu.

**Ne contient pas :** la sauvegarde, la possession — le joueur ne possède rien —, l'interaction avec les personnages non joueurs, le cycle jour-nuit et la météo (lumière fixe de fin d'après-midi, celle de la direction artistique), le combat, la capture, la progression, l'inventaire, le multijoueur, les comptes, le second moteur de rendu, l'audio (les deux essais de synthèse ont montré que le résultat desservirait la version, voir le [constat technique](doc/conception/referentiels/technique/index.md)), et les passages bâtis, qui relèvent de l'histoire du joueur ([contenu](doc/conception/referentiels/contenu/index.md)).

**Pourquoi ce découpage :** le combat est le sujet le plus ouvert du projet ; le figer avant d'avoir éprouvé le rendu et l'échelle coûterait plus cher que d'attendre. Cette version vaut aussi preuve que l'architecture hexagonale tient sur un cas réel.

**Réussite :** on se promène avec plaisir pendant plusieurs minutes, sans bug bloquant, la carte se traverse de bout en bout, et le monde paraît vivant sans qu'aucune mécanique n'existe.

## Chemin vers la 0.1 — briques ordonnées (dérivé le 2026-08-03, DA validée)

Chaque brique laisse un état stable et démontrable. Les dépendances vont de haut en bas ; B3 et B4 peuvent avancer en parallèle après B2.

- **B0 — La maquette statique.** Une scène **fixe**, composée de **vraies sprites** assemblées d'après un plan de composition, publiée **en artefact Claude** — c'est l'hébergement du POC (décision de l'opérateur) et la maquette sert aussi à **constater les limites des artefacts** (taille, animation, entrées clavier, performance), qui s'écrivent au référentiel technique. Sujet de la scène, décidé par l'opérateur : la scène de référence de la direction artistique, avec son centre de soin, dans un cadre fermé. Elle n'est pas un préalable au moteur : elle est la **première livraison de la chaîne d'assets**, et B2/B3 avancent en parallèle.
- **B1 — Dépôt et squelette du projet.** Dépôt : `git@github.com:Cartman34/gatebeast.git` (décision de l'opérateur). Squelette TypeScript, outillage de base ; la conception déménage dans `doc/` du dépôt (règle de méthode).
- **B2 — Cœur hexagonal minimal.** État du monde (grille invisible, carte bornée, entités positionnées), horloge de jeu, ports définis par contrat : rendu, entrées, temps. Aucune dépendance au navigateur dans le cœur ; tests du cœur purs.
- **B3 — Moteur de rendu du POC : CSS** (décision de l'opérateur — « on peut commencer par CSS », précédé de la maquette B0). Implémentation du port de rendu ; affiche la carte et les entités à l'échelle de la DA (case, caméra 70°, lumière fixe de fin d'après-midi). Contrainte d'hébergement : tourne dans un artefact Claude, dans les limites constatées en B0.
- **B4 — Chaîne d'assets.** La méthode est arbitrée et écrite ([assets](doc/conception/referentiels/visuel/assets/index.md)) ; reste à l'outiller et à la faire tourner. Outils à écrire : le **catalogue** (format et écriture automatique), le **détourage**, l'extension des **mesures** (emprise mesurée contre emprise annoncée, raccord bord à bord, luminance), le **jugement** sur critères écrits avec sa note, la **planche-contact** publiée, et la **composition d'une scène** depuis le catalogue et un plan. Contenu à compléter d'abord : l'inventaire n'a **aucun bâtiment de campagne** — centre de soin, maison, tour de guet, point de passage, ponts, clôtures —, et la fiche du personnage-joueur n'est qu'un brouillon logé dans un script, à transcrire parmi les personnages de référence. Livre les lots v0, puis les lots cibles au fil des jalons.
- **B5 — La carte 0.1.** Carte bornée composée au format de composition (les six biomes des planches comme matière), vérifiée par les contrôles existants (cohérence, dessertes, raccords).
- **B6 — Le joueur en promenade.** Sortie du centre de soin au démarrage, déplacement fluide au clavier, collisions, caméra en suivi continu. Premier critère de réussite éprouvable : la carte se traverse de bout en bout.
- **B7 — Le monde vivant.** Personnages et créatures en nombre, déambulations et interactions entre eux, l'évènement gateball rare et irrégulier.
- **B8 — Stabilité et livraison.** Tenue en performance avec la population dense, corrections, livraison 0.1 sous le protocole de version minimal.

## Jalons suivants

Non ordonnés tant que la 0.1 n'a pas été jouée — c'est elle qui informera la suite : la sauvegarde et la possession, la rencontre et la capture, le combat, la progression et l'évolution, la collection, puis le multijoueur léger.

## Questions ouvertes

Aucune en propre.
