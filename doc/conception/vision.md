# GateBeast — vision

**Intention :** offrir le plaisir du genre « créatures à collectionner » — découvrir, capturer, faire progresser et affronter de petites créatures — dans un univers entièrement original qui nous appartient.

Ce que le projet est : **GateBeast**, un jeu original de collection de créatures, conçu pour évoluer longtemps. Ce qu'il n'est pas : une copie de Pokémon — aucun nom, créature, visuel ou texte de cette licence n'est réutilisé ; l'inspiration porte sur le genre, jamais sur l'œuvre.

## Décisions

- **Univers 100 % original** — impératif de droits et d'identité : tout ce qui se voit, se lit et s'entend est créé pour ce jeu ; l'inspiration se limite aux mécaniques du genre. Écarté : toute réutilisation d'éléments sous licence.
- **Évolution par versions stables** — le jeu évoluera beaucoup : la cible se rejoint par versions intermédiaires pleinement fonctionnelles et stables. Le protocole de version (nommer, faire évoluer, déployer) est un besoin de la cible technique ; le contenu de chaque version relève du plan d'action, hors conception.
- **Un lore proportionné** — l'histoire et le background ne s'écrivent que pour les personnages et lieux qui en ont l'utilité ; pas de lore pour le lore.
- **Trois langues, trois usages** — le **nom du jeu et le code** sont en anglais : le premier pour la portée internationale, le second par règle d'exécution. L'**interface et le contenu de la 0.x sont en français** : la preuve de concept s'adresse au propriétaire, traduire à ce stade serait du travail perdu. Une portée internationale reste visée : l'interface ne doit donc jamais figer la langue dans le code, et les **termes importants sont fixés en anglais et en français dès leur création** ([lexique](referentiels/contenu/lexique.md)), pour qu'aucune traduction ne se décide après coup. La conception reste rédigée en français. Écarté : un nom sur base française ; une interface anglaise dès la preuve de concept (coût sans bénéfice).
- **Cœur du jeu indépendant de toute interface — architecture hexagonale** — la logique et les données du jeu ne dépendent d'aucune interface ni d'aucune infrastructure ; chaque interface est un adaptateur interchangeable. Premier adaptateur cible : le **navigateur web** (jouable partout, outillage existant) ; des adaptateurs Android, iOS ou bureau pourront s'ajouter sans toucher au cœur. Écarté : lier le jeu à une plateforme.
- **Solo, plus multijoueur léger** — le cœur du jeu se joue seul ; la cible inclut les échanges et affrontements entre joueurs, et l'architecture le prévoit dès l'origine pour ne pas se refaire. Écarté : solo pur (coûteux à rouvrir ensuite), monde partagé central (ambition disproportionnée).
- **Public familial, tous âges** — la norme du genre : ton accessible, direction artistique ronde et colorée ; la conformité se traite en conséquence (mineurs concernés). Écarté : publics restreints.
- **Quatre mécaniques du genre en socle, sans restriction de genre** — capture et collection, combat, progression et évolution, exploration et quêtes forment le socle. Le genre est un point de départ, pas une limite : le jeu s'étend par expérimentation — une mécanique nouvelle (par exemple une part de gestion) entre dans la cible sous statut expérimentation, et n'y reste que si elle fonctionne. Écarté : figer le gameplay au périmètre du genre.

- **Un monde traversé par un plan parallèle** — les créatures émergent d'un autre plan par des points de passage. Ce choix justifie nativement l'évolutivité du jeu (de nouvelles vagues amènent créatures, zones et mécaniques nouvelles), porte une trame à mystère, et donne à la direction artistique ses deux tonalités : le monde familier et le plan étrange. **Son existence reste implicite : rien ne l'annonce au début — ni dans le jeu, ni dans le discours de marque — elle se révèle progressivement.** Écarté : deux règnes seuls (n'explique pas l'évolutivité), écosystème étendu (coût de contenu élevé sans ce bénéfice), toute annonce frontale du multi-monde.
- **Quatre critères de réussite** — prise en main familiale (un nouveau joueur capture sa première créature en moins de 10 minutes sans aide) ; jalons stables (chaque version publiée se joue de bout en bout sans bug bloquant) ; boucle complète à terme — la boucle de jeu s'entend : explorer le monde, rencontrer une créature, la capturer, la faire progresser, combattre avec elle, et repartir explorer plus loin ; son détail relève des parcours fonctionnels. **Elle n'est pas exigée de la première version** : la 1.0 est une version d'exploration sans interaction, dont l'objet est d'éprouver le rendu, l'ambiance et le socle technique avant d'engager les mécaniques — le combat est le sujet le plus ouvert du projet et le figer trop tôt coûterait plus que d'attendre. Écarté : exiger la boucle complète dès la première version publique (revient à décider le combat sans rien avoir éprouvé). Extensibilité mesurable (ajouter une créature ou une zone est un pur ajout de contenu, zéro modification du cœur).

- **Le jeu s'appelle GateBeast** — 2 syllabes, base anglaise originale, la porte entre les mondes plus la créature : le nom porte l'univers ; les créatures se nomment collectivement les *gatebeasts*. Sous réserve d'une recherche d'antériorité formelle (marques, classes jeux) avant tout usage public — la vérification web de premier niveau est passée. Écarté : toute base française (langue du jeu), les noms en « -mon » dont Vixmon (créature Digimon quasi homonyme, suffixe dérivatif contraire à l'identité originale), Beastlings (désigne déjà des créatures de jeux majeurs), Riftkin (sens du suffixe refusé), BeastGate (« X-gate » se lit comme un scandale en anglais).

## Questions ouvertes

Aucune : la couche vision est close.

## Nomenclature

- **créature** : les petites créatures du jeu — même nom côté référentiels (fiches, lore, assets) et côté fonctionnel (données, mécaniques) ; en anglais dans le jeu : *gatebeast(s)*.
- **joueur** : la personne qui joue ; son personnage dans le jeu est le **personnage-joueur**.
- **bestiaire** : l'ensemble des fiches de créatures (identité, description, visuels) ; leurs valeurs de jeu vivent côté fonctionnel, dans les données.
- **plan parallèle** : l'autre monde d'où émergent les créatures (son nom propre relève du lore) ; un **point de passage** est un lieu où il touche le monde, une **émergence** est une arrivée de créatures par un passage.
- **boucle de jeu** : explorer, rencontrer, capturer, faire progresser, combattre, repartir explorer.

## Où en est le travail

Voir [suivi.md](../../SUIVI.md) — état courant, défauts constatés, corrections proposées et outils. À lire en premier pour reprendre le travail.

## Sous-niveaux

- [referentiels/](referentiels/index.md) — la matière du jeu : marque, visuel, audio, contenu, technique, conformité.
- [fonctionnel/](fonctionnel/index.md) — le comportement du jeu : acteurs, mécaniques, parcours, données, échanges, exigences.
