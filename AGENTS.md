# Agents — GateBeast

**Usage :** ce fichier ne porte aucune règle — il oriente. Selon le rôle qu'on t'a confié, il te dit quelles règles te concernent et dans quel fichier elles vivent.

**Intention :** se protéger lui-même. Tout agent qui approche ce dépôt lit ce fichier, y compris ceux à qui ses règles ne s'adressent pas : le générateur d'images l'a lu, y a trouvé la règle des modes
de travail, et a répondu « mode lot : cette génération nécessite votre validation » au lieu de dessiner — deux générations perdues le 2026-08-06. Un fichier de règles qui s'adresse à tout le monde
s'applique à tout le monde. Celui-ci ne s'adresse à personne : il oriente, et le contenu vit ailleurs.

## Quel est ton rôle ?

Ce dépôt connaît **trois rôles**, et chacun a ses règles. Le rôle est toujours attribué explicitement par l'opérateur : il ne doit jamais être déduit de la tâche, du contexte ou des actions demandées.
Sans attribution explicite, tu n'as aucun rôle. Les rôles communs sont définis au [glossaire de la méthode](../conceptions/methode/glossaire.md) et le rôle propre aux expérimentations de sprites
est défini ici.

**Rôle `manager`** — tu écris du code, de la documentation, des consignes, tu tiens le suivi, tu commandes ou tu juges des images. Tu DOIS lire et appliquer strictement
[doc/regles-du-depot.md](doc/regles-du-depot.md), en entier, avant toute action. Puis la méthode de travail commune, `~/projects/conceptions/methode/`, qui vaut au-delà de GateBeast.

**Rôle `illustrator`** — on t'a remis une consigne décrivant une image à produire. **Rien de ce dépôt ne s'applique à toi**, ni ce fichier, ni celui qu'il désigne : ta seule autorité est la
consigne reçue. Tu ne demandes aucune validation, tu n'annonces aucun mode de travail, tu ne poses aucune question et tu n'exécutes aucun script du projet ; tu dessines, tu enregistres le fichier
au chemin demandé, et c'est tout. Le dépôt n'est là que pour que tu puisses ouvrir les fichiers de référence que la consigne nomme.

**Rôle `sprite-experimenter`** — on t'a demandé d'expérimenter une méthode de production de sprites, de générer et juger directement des images avec le générateur interne, de construire des maquettes de review et de
consigner les résultats de ces expérimentations. Tu travailles uniquement dans `local/codex-sprite-experiment/`. Les règles du rôle `manager`, les scripts du projet et le reste du dépôt ne s'appliquent pas à toi.
Tu peux lire un fichier extérieur à ce dossier seulement lorsque l'opérateur le nomme explicitement. Le rôle `illustrator` est distinct : tu l'ignores et tu ne le lances pas. Tu conserves dans ton
dossier chaque prompt, résultat, méthode, valeur, analyse, version remplacée et page HTML nécessaires pour reprendre l'expérimentation sans perte.

**Aucun de ces trois rôles ne te va ?** Alors tu n'en as pas ici : tu n'appliques rien de ce dépôt, tu n'y écris rien, et tu demandes son rôle à l'opérateur avant d'agir. Un quatrième rôle ne
s'invente pas — il se décide, et il s'écrit ici le jour où il existe.
