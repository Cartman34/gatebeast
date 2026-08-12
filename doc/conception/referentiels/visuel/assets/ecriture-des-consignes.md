# Comment s'écrit une consigne

**Usage :** ce que lit qui s'apprête à modifier une consigne de génération — le socle partagé de `scripts/asset_common.py`, les clauses assemblées par
`scripts/generate-sprite.py`, ou la fiche d'un sujet sous `assets/descriptions/`. Il dit où chaque chose s'écrit, ce qu'une clause doit porter, et ce qui n'a
rien à y faire.

**Intention :** une consigne se modifie sous le coup d'une image ratée, donc dans l'urgence et sans que rien ne dise pourquoi la clause d'à côté existe. Deux
conséquences, payées le 2026-08-12 : la clause de caméra a grossi par empilement — trois formulations du même ordre, chacune ajoutée après un échec, si bien
que plus personne ne savait laquelle commandait ; et une clause écrite pour corriger un défaut en a créé un autre parce que son but n'était écrit nulle part.
**Sans ce document, la modification suivante annule la précédente** : c'est la demande de l'opérateur, « faut que ce soit documenté AVANT de faire des modifs,
sinon la prochaine fois tu fais la modif inverse car tu n'as pas expliqué le but, pourquoi ce paramètre, ce qui est attendu, son usage ».

**Ce qu'il ne couvre pas :** ce qu'une consigne doit DIRE d'un sujet — c'est la grille des [paramètres d'un sujet](../parametres-des-sujets.md). Ici, on ne
parle que de la façon de l'écrire.

## Où s'écrit quoi — quatre niveaux, et un seul par chose

- **Le socle** (`asset_common.py`) porte ce qui est vrai de TOUTE image du monde : le style, la caméra, le fond, le cadrage, les unités. Une clause y est écrite
  parce qu'elle vaudrait à l'identique pour n'importe quel sujet.
- **Le type** (`assets/subjects.json`, clé `extra_prompt`) porte ce qui est vrai de tous les sujets d'une même famille et faux pour les autres — qu'un chemin
  n'a aucun volume, qu'une créature se présente autrement selon la vue.
- **La variante** porte ce qui change d'une pièce à l'autre du même sujet : sa forme, son orientation, sa composition.
- **La fiche du sujet** (`assets/descriptions/`) porte ce qui n'est vrai que de lui.

**UNE CHOSE S'ÉCRIT À UN SEUL NIVEAU.** La même contrainte répétée à deux niveaux se contredit dès que l'un des deux gagne une précision : c'est ce qui est
arrivé à la caméra, dite au socle et redite au rappel final dans d'autres mots. Quand un texte doit paraître deux fois — un rappel en fin de consigne, par
exemple —, il est **interpolé depuis un seul endroit**, jamais recopié.

## LA CAMÉRA APPARTIENT AU SOCLE, ET AUCUNE SPRITE NE PEUT LA CHANGER

**Règle de l'opérateur, 2026-08-12 : « l'angle, c'est 60°, aucune sprite ne doit pouvoir changer ça, c'est défini dans le socle. La vue caméra ne dépend PAS du
sprite ! »** Elle est la plus dure de ce document, et elle vaut pour tout ce qui décrit une prise de vue : l'angle, la projection, ce qu'on voit d'en haut,
ce qui est écrasé.

**CE QUI EST DONC INTERDIT** dans une fiche de sujet comme dans un motif de reprise : parler de la caméra, même pour la confirmer. Une phrase qui la répète
la déplace — « le dessus de sa couronne domine l'image » a suffi à faire basculer un chêne en vue de dessus, alors que le socle demandait soixante degrés. Le
générateur lit la clause la plus proche du sujet, et une redite proche bat un socle lointain.

**CE QU'ON ÉCRIT À LA PLACE** : ce qui appartient au sujet, et rien d'autre — sa forme, ses proportions, sa matière. Un défaut d'angle sur une image ne se
corrige JAMAIS dans sa fiche : il se corrige au socle, où il vaut pour tous les sujets à la fois, ou il ne se corrige pas.

## Ce qu'une clause doit porter — quatre choses, et elles sont toutes obligatoires

Ce sont les quatre que l'opérateur nomme, et l'ordre importe peu :

1. **Le but** — ce que la clause obtient. « L'image se pose sur une case sans se rattraper. »
2. **Pourquoi ce paramètre existe** — ce qui casse sans lui. C'est ce qui empêche la modification inverse six semaines plus tard.
3. **Ce qui est attendu**, en termes vérifiables sur l'image finie : un nombre, une proportion, une chose qu'on voit ou qu'on ne voit pas.
4. **Son usage** — à quels sujets elle s'applique, et à quels sujets elle ne s'applique pas.

**LES QUATRE NE VONT PAS AU MÊME ENDROIT, ET C'EST LE POINT LE PLUS SOUVENT MANQUÉ.** Ce que le générateur lit, c'est **ce qui est attendu**, et rien d'autre.
Le but, la raison et l'usage s'écrivent en **commentaire du code** qui assemble la clause, ou dans ce référentiel. Une consigne qui raconte pourquoi elle
existe est une consigne plus longue, moins claire, et qui décrit un échec passé au lieu de prescrire une image.

## Ce qui ne s'écrit JAMAIS dans une consigne

- **L'historique d'un échec.** « Trois versions ont répondu en dessinant une élévation, refusé par l'opérateur le 11 » n'apprend rien à qui dessine : il lui
  faut la prescription, pas le procès-verbal. L'historique va au commentaire du code, ou au journal des séances.
- **Une justification.** « Parce que sinon le bâtiment paraît flotter » double la longueur sans changer ce qu'il faut dessiner.
- **Un renforcement.** Répéter une clause en majuscules, la redire plus bas « pour être sûr », ajouter « et c'est impératif » : cela n'ajoute pas de contrainte,
  cela ajoute du texte à contredire. **Un ordre est dit une fois, à sa place, positivement.**
- **Une interdiction seule.** « Ne dessine pas de perspective » laisse ouvert ce qu'il faut faire ; « les arêtes verticales restent parallèles » le ferme. Une
  interdiction n'est utile qu'accolée à la prescription qui la remplace.

## Comment on modifie une consigne

1. **On lit la consigne ASSEMBLÉE avant de la changer** — `python3 scripts/generate-sprite.py <SUJET> <VARIANTE>` sans `--generate` l'écrit sous `var/tmp/`. Une
   clause se juge dans le texte que le générateur reçoit, jamais dans le fichier où elle est écrite : c'est là, et seulement là, que les contradictions se
   voient.
2. **On cherche d'abord si la contrainte existe déjà**, à un autre niveau et dans d'autres mots. Si elle existe, on la reformule au bon endroit ; on n'en ajoute
   pas une seconde.
3. **On reformule, on n'empile pas.** Si la clause a grossi, on la réécrit entière et plus courte, en gardant chaque contrainte distincte qu'elle portait.
4. **On mesure ce qui a bougé partout** — `bash scripts/diff-prompts.sh` compare les soixante-quinze consignes à leur référence figée et dit lesquelles ont
   changé. Une modification au socle touche tout le monde : c'est ce qu'on veut savoir avant de dépenser une génération.
5. **On refige la référence** — `bash scripts/diff-prompts.sh --freeze` — une fois le changement voulu et vérifié, pour que la prochaine dérive involontaire se
   voie.

**ET TROUVER UNE CAUSE N'EST PAS AVOIR TROUVÉ LA CAUSE** (opérateur, 2026-08-12 : « ce n'est pas parce que tu as trouvé une cause qu'il n'y en a pas
d'autres »). Une image fausse peut l'être pour trois raisons à la fois, et corriger la première laisse les deux autres produire le même symptôme au tour
suivant. On lit la consigne assemblée EN ENTIER, une fois la cause trouvée, avant de relancer.
