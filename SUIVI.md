# Suivi des travaux — GateBeast

**Intention :** permettre à n'importe quel intervenant de reprendre le travail sans perte. Ce document dit **où on en est**, pas ce que le jeu doit être — la cible vit dans la conception, le
découpage en versions dans le [plan d'action](PLAN-ACTION.md).

Il se met à jour à chaque étape franchie. Il ne conserve pas d'historique : seul l'état courant compte (le versionnage garde le reste).

## L'ÉTAT COURANT — ce document ne contient que ça, et c'est délibéré

**CHAQUE DÉCISION VIT À SON FOYER, UNE SEULE FOIS**, et ce document y renvoie au lieu de la recopier : les règles de conduite aux [règles du dépôt](doc/regles-du-depot.md) et à la méthode commune,
la cible à `doc/conception/`, les mots au [glossaire](doc/glossaire.md), et tout ce qui concerne un point dans **sa description** — `php scripts/backlog.php show <REF>`. Élagué le 2026-08-11 : le
document empilait une section par séance, ce que sa propre première ligne interdit. **Ce qui en a été retiré n'est pas dans un diff, il est dans
[doc/journal-des-seances.md](doc/journal-des-seances.md)** — versionné, citable, et qui ne dit que le pourquoi des décisions passées, jamais l'état courant.

### OÙ ON EN EST AU 2026-08-17

**LE SEUL SUJET OUVERT EST `S97 consigne-propre`, ET IL SE TRAITE HORS DÉPILEMENT** (opérateur, 2026-08-17 : « ce sujet est sensible alors on arrête le
dépilement, tu traites ce sujet »). **On ne travaille plus en regénérant : on écrit une consigne propre de bout en bout en MODIFIANT le texte déjà généré, et on
ne reporte dans le code que ce qui fonctionne.** Le générateur est donc gelé — `scripts/asset_common.py` et `scripts/generate-sprite.py` sont à l'identique, et
la référence de `diff-prompts.sh` est refigée sur ce code. Tout l'état du sujet est à sa description, `php scripts/backlog.php show consigne-propre`.

**CE QU'ON PREND À LA REPRISE, EN PRIORITÉ 1 : `S1 suggestions-gen`.** L'agent générateur propose des corrections à la clause de caméra, dans
`local/projection-camera-prompt.diff`. Sa première suggestion était juste et est déjà appliquée en `v6`.

**LE BACKLOG NE SUIT PLUS, ET C'EST À TRAITER** (opérateur, 2026-08-17 : « le backlog lui n'est pas au courant de tant de détails, tu es coincé sur le même
sujet depuis trop longtemps et le backlog ne sert plus, c'est un problème »). `S97 consigne-propre` est ouvert depuis le 2026-08-13 et a absorbé toute la
séance : la source de l'atelier, le foyer des consignes, six versions, quatre outils de mesure. Rien de cela n'est dans sa description, et les points voisins —
`S94`, `S98`, `S99`, `Q1` — décrivent un état dépassé. **Un sujet qui dure une semaine cesse d'être un point de pile** : il faudra soit le découper en points
qui se ferment, soit lui donner un foyer à lui et le sortir de la pile.

**CE QUI N'A PAS ÉTÉ FAIT AUJOURD'HUI ET ATTEND** : reporter dans le code ce qui a été tenu (`S97`, dernière étape) ; les blocs de source `style`, `detourage`
et `reponse`, qui restent en texte plat ; l'état par édit affiché sur la page (`S98`) ; et la `v6`, écrite et **non générée**.

**L'ATELIER A SA PROPRE SOURCE DE VÉRITÉ, SÉPARÉE DE L'APPLICATION** (opérateur, 2026-08-17 : « on ne travaille que pour l'atelier de génération, on définit tout
bien et après on appliquera à l'application. Sinon tu vas faire les modifs à moitié et laisser des reliquats un peu partout »). Rien de `scripts/` ni de
`doc/conception/` n'est aligné dessus, et **c'est voulu** : on définit d'abord, en un lieu, on applique ensuite.

- **`review-server/workshop/source/` — les blocs de règle**, un par sujet : `projection`, `lumiere`, `dimensions`, `assise`. Chacun porte **l'explication et la
  clause exacte** qui part au générateur, dans le même fichier, pour qu'on ne puisse pas corriger l'une en oubliant l'autre.
- **`php review-server/workshop/check-source.php`** tient la cohérence **mécaniquement** : chaque bloc déclare en en-tête les mots qu'il **gouverne**, et aucun
  autre ne peut les employer. On ne gouverne que ce qu'on **énonce**, jamais le vocabulaire partagé — `TX`, `TY` et les cardinaux se définissent à la projection
  et s'emploient partout. La liste se sépare par des **points-virgules**, parce qu'une valeur gouvernée porte des décimales.
- **`php review-server/workshop/apply-source.php <SUJET> <bloc>`** est le seul chemin entre la source et une version. Il remplace une **section entière**, et
  **il écrit toujours dans la version en attente** — celle qui suit la dernière générée. Empiler une version par correction est mécaniquement impossible.

**LA CONSIGNE VIT SOUS `review-server/workshop/consignes/<SUJET>/`, VERSIONNÉE DE BOUT EN BOUT, RACINE COMPRISE.** Elle était à cheval sur deux répertoires dont
un jetable, et son identité était une date. Un fichier se nomme `<SUJET>.v<N>.<quoi>.<ext>` — `prompt`, `image`, `edits`, `generation`, `transmitted`,
`critiques` — parce qu'un nom doit dire de qui il est et ce qu'il est. Les trois incohérences qui restaient sont à `S99 consigne-structuree`.

**LA `v5` EST GÉNÉRÉE, LA `v6` EST EN ATTENTE.** Une version en attente se **modifie** tant qu'elle n'est pas générée ; une version qui porte une image est
close. **AUCUNE GÉNÉRATION NE PART SANS L'ACCORD DE L'OPÉRATEUR** — trois versions ont été empilées et une génération dépensée sans qu'il l'ait demandé.

**ET LA MESURE DE LA `v5` NE VAUT RIEN, CE QUI EST LE CONSTAT LE PLUS IMPORTANT DE LA SÉANCE.** Elle sort à 16,00 TX sur 13,30 TY, pile dans le contrat, marges
à 0,01 — et c'est faux. `php local/scripts/show-generator-calls.php <journal>` montre ce que l'agent exécute réellement : `src.crop(box).resize((1536,1120))`.
**Il détoure, recadre sur la matière, puis ÉTIRE l'image à nos dimensions.** L'encre remplit donc la toile par construction, et **aucune mesure sur l'encre ne
peut plus voir la déformation** — c'est l'erreur transparente que ce dépôt chasse, le contrôle rendant « tout va bien » sans avoir rien contrôlé. `Q1
remplissage-image` ne porte plus la bonne question : le sujet n'est pas le remplissage, c'est **l'étirement**.

**LES OUTILS DE MESURE** : `php scripts/check-parallel-projection.php <image>` chiffre la dérive de la silhouette rangée par rangée et rend un verdict — la `v5`
perd la projection sur 11 arêtes, la pire de 392 rangées à 0,112. `php local/scripts/measure-trial-image.php <image>` donne toile, encre et marges.
`review-server/lib/SpriteMeasures.php` porte les deux, partagé avec la page.

**LA GÉNÉRATION ENREGISTRE SA SESSION ET SA CONSIGNE TRANSMISE** : `php scripts/generate-version.php <SUJET.vN.prompt.txt>` écrit `<…>.generation.json`, et
`php review-server/workshop/extract-transmitted.php <SUJET> <rang>` sort du journal du générateur le texte qu'il a réellement envoyé à son modèle d'images —
il le rapportait depuis le début, personne ne le ramassait. **Aucun comptage phrase par phrase n'est affiché** : l'agent réécrit au lieu de relayer, donc tout
sortait « Disparue », y compris sur les sections qu'on lui demande de ne pas transmettre.

**LE QUADRILLAGE DE CASES SE MONTRE SUR TOUS LES OUTILS, HORS MAQUETTE**, et la règle est aux [règles du dépôt](doc/regles-du-depot.md). La feuille de la grille
a quitté la page des sprites pour vivre avec son service, `review-server/lib/footprint-grid.css` : les deux pages la chargent, aucune ne la redéclare. Et
`check-review-pages.php` lit maintenant **ce que la page charge**, au lieu d'une liste de fichiers tenue à la main — c'est cette liste qui a déclaré perdu un
comportement intact, une feuille plus loin.

**LA CONSIGNE A DES VERSIONS, ET LE DIFF SE FAIT D'UNE VERSION À LA SUIVANTE.** `v1` est le texte que la chaîne a produit, sous `var/generations/trials/` ; les
suivantes vivent à `review-server/critiques/<essai>/<consigne>.v<N>.txt`, avec leurs critiques sous le même nom de version. La page `/workshop` montre la version
active, son diff par lots de mots dans le texte, et les critiques ancrées sur la phrase qu'elles mettent en cause — rouge barré ce qui disparaît, vert ce qui
s'ajoute, souligné bleu la phrase critiquée, et une légende le dit. Une version se fabrique par
`php local/scripts/revise-consigne.php <source> <cible> <édits.json>`, qui refuse tout remplacement ne trouvant pas exactement une occurrence.

**LES VERDICTS DE L'OPÉRATEUR SONT UN PLAN DE TRAVAIL, ET ILS SE LISENT AVANT DE PRODUIRE QUOI QUE CE SOIT.** `php scripts/remarks.php list` les donne tous ;
`new` ne dit que ce qui a bougé, et s'arrêter à son « aucun verdict neuf » revient à ne jamais les lire. **Ce qui attend encore :** l'est, trois fois sur deux
sujets — `SP-001` (v4, v5, v6) regarde à gauche alors que l'est est la droite, et `HU-000-v5` revient déformé ; `CH-021`, le style de `v2` et aucun cours d'eau
sur l'image, en `ns` comme en `ew` ; `BT-002-v2`, moins de casse et un peu plus de saleté — sa description est déjà réécrite en comptes exacts, il reste à
produire ; `TR-060`, revenir à la `v5` avec un tronc plus fin.

**LA CAUSE DE LA VUE PARALLÈLE EST TROUVÉE, ET C'ÉTAIT UN MANQUE, PAS UNE CONTRADICTION.** Le socle disait « projection orthographique », « azimut zéro »,
« aucun point de fuite » — **or une isométrie satisfait tout cela**, sa profondeur partant simplement en diagonale. Rien ne fermait cette lecture. L'opérateur
l'a obtenu en discutant directement avec l'agent générateur (session `019ff7b5-874b-7f13-b999-eb15476ab0da`), qui a nommé le manque : « la profondeur du monde
se projette verticalement vers le HAUT de l'image, jamais en diagonale ». **Et deux des quatre puces que j'avais écrites le matin étaient FAUSSES** : elles
annonçaient un pignon en parallélogramme, alors qu'à azimut zéro il est vu par la tranche et se projette en segment — un parallélogramme est la signature d'une
isométrie, écrite au milieu de la clause censée la fermer.

**CE QUI REMPLACE LA PROSE : DEUX ÉGALITÉS.** Une arête debout monte tout droit, `Δx = 0` ; une profondeur au sol monte tout droit elle aussi, vers le haut,
`Δx = 0`. Une description s'interprète, une égalité se vérifie — et ces deux-là ne peuvent pas se confondre avec une isométrie, où `Δx ≠ 0` dans les deux cas.

**LE PREMIER ESSAI A ÉTÉ LANCÉ ET IL A RÉVÉLÉ LA MÉTHODE DU GÉNÉRATEUR.** `var/generations/trials/2026-08-13-BT-001/`. Le bâtiment revient enfin en vue
plongeante, sa cour visible. Mais en lisant ce que l'agent a **réellement exécuté** — `php local/scripts/show-generator-calls.php <journal>` — on découvre :

- **il travaille en plusieurs passes**, et la consigne qu'il nous rend est celle de la **dernière** seulement, celle du fond magenta ; celle qui a dessiné le
  bâtiment n'a jamais été rapportée. Notre demande, formulée au singulier, a récolté la dernière ;
- **il génère sur fond magenta puis détoure** avec `remove_chroma_key.py` — ce que l'opérateur avait annoncé ;
- **IL COMPLÈTE L'IMAGE POUR ATTEINDRE NOS DIMENSIONS** — `alpha_composite(im, (0,128))` — au lieu de dessiner à cette taille. Notre contrat de dimensions est
  donc satisfait par du remplissage, et la chaîne enregistrerait « hauteur tenue » sur une image complétée. **C'est l'erreur transparente la plus coûteuse
  trouvée cette semaine, et elle n'est pas de notre côté.** Deux décisions attendent l'opérateur : lui demander toutes ses passes dans l'ordre, et interdire le
  remplissage ou l'accepter en le mesurant.

**LA CONSIGNE EST DEVENUE LISIBLE ET TRAÇABLE.** Elle porte des titres Markdown à deux profondeurs, dix groupes thématiques et 24 sections, chacune annonçant
son **niveau** — `common`, `type`, `variant`, `description`, `parameters`, `call`, six identifiants anglais. Un découpage `<consigne>.parts.json` est écrit à
côté d'elle au moment où elle est figée, lié à son texte par une empreinte : `php scripts/show-prompt-parts.php <consigne.txt>` en donne le sommaire, et
`--grep "<phrase>"` répond **d'où vient cette phrase**, ce qui décide où porter un correctif. Preuve tenue à chaque passe : en retirant les titres, on retombe
**à l'octet** sur les consignes d'avant le chantier.

**LA CONSIGNE A DEUX REGISTRES, ET C'EST CE QUI REND TOUT CELA POSSIBLE** : ce qui doit atteindre l'image, et ce qui s'adresse à l'agent sans jamais parvenir à
son modèle. Le second ne peut pas être dessiné. **Mais il ne sert pas à lui sous-traiter des contrôles** — un contrôle mécanisable reste chez nous, sinon c'est
lui qui rendrait le verdict sur son propre travail, et on paierait en jetons ce qu'un script fait gratuitement.

**UNE RÉFÉRENCE EST FIXE ET NE SUIT PLUS LA DERNIÈRE VERSION.** Elle se déclare au référentiel sous la clé `reference`, et se fige le jour où une version est
jugée bonne. **Deux existent** : `TR-060-v12` et `TR-063-v19`, toutes deux validées le 2026-08-13.

**LA PAGE D'ATELIER EXISTE**, `/workshop` : l'image, la consigne section par section avec son niveau, et la place du diff avec la consigne transmise. Elle relit
et éprouve le découpage avant d'attribuer quoi que ce soit — empreinte et pavage — et dit qu'elle ne peut pas conclure plutôt que de deviner. Un essai vit sous
`var/generations/trials/`, n'entre à aucun référentiel et ne brûle aucune version.

**CE QUI RESTE EN CHANTIER, ET QUI A ÉTÉ ARRÊTÉ EN COURS** : la page d'atelier n'a ni diff ni critiques ancrées — sa structure complète est décrite au point
`S94 atelier-generation`, avec les quatre décisions déjà prises. La planche de projection (`php scripts/build-projection-plate.php`) est juste et lisible, mais
n'est référence de rien.

**CE QU'IL FAUT SAVOIR SUR L'INDEX** : il se construit depuis `review-server/artefacts.json` et **non** depuis le registre des pages. Une page servie peut donc
exister, répondre, et n'apparaître nulle part — c'est arrivé à `/workshop`. C'est `W2 pages-hors-index`.

**LEÇON DE MÉTHODE PAYÉE CE JOUR-LÀ, ET ELLE EST ÉCRITE À `execution.md`** : la conception se tranche **avant** de déléguer, jamais à travers l'assistant. Le
découpage de la consigne est parti en cinq ordres successifs pour un seul geste, chacun coûtant à l'assistant une relecture complète des règles et le rejeu de
ses preuves. La surconsommation d'un assistant est un défaut de son donneur d'ordre.

### Comment on démarre

**LA SESSION S'OUVRE DEPUIS `~/projects/gatebeast`, ET C'EST IMPÉRATIF** — pas depuis le dossier parent, sans quoi les hooks déclarés dans `.claude/settings.json` ne se chargent pas, le `GO` n'arme
rien et la fin de tour n'est jamais refusée.

**Le prompt de reprise, à donner tel quel à une session neuve :**

> Travaille dans ~/projects/gatebeast. Lis AGENTS.md, puis doc/regles-du-depot.md en entier, puis `~/projects/conceptions/methode/collaboration.md`, puis la
> première section de SUIVI.md — elle dit sur quoi on reprend et en quelle priorité, et elle contient tout le reste. Démarre le serveur de revue. Tu ne
> génères aucune image sans mon accord, et tu réponds à une question sans rien modifier. Annonce le mode et arrête-toi.

**LA REVUE SE REGARDE EN LOCAL** : `php review-server/serve.php`, puis l'adresse qu'il imprime — **elle est configurée dans `review-server/config.json`, et `php review-server/url.php` la dit**, le
port se changeant là et nulle part ailleurs. **Cinq pages** — l'Index, `/inventory` qui dit ce que chaque sujet **est**, `/backlog` qui porte les **points ouverts du projet** et reçoit les votes, le
suivi des sprites, la Maquette Campagne. Une page se
reconstruit par sa route : `php review-server/build.php /sprites`. **Ce serveur ne survit pas à la séance : il se ferme avant de la clore, par `php scripts/stop-review-server.php`** — laissé ouvert,
il tient le port et le démarrage de la séance suivante échoue sur « Address already in use ». Les remarques de l'opérateur sont dans `review-server/notes/`, lues directement.

**L'HABILLAGE D'UNE PAGE SE LIT DANS L'HISTORIQUE, JAMAIS DE MÉMOIRE** — deux fois le 2026-08-11, j'ai « restauré » ce qui était déjà là et affirmé à l'opérateur que c'était l'original.
`bash scripts/dev/list-page-themes.sh` sort la palette de la page des sprites à chaque commit qui l'a touchée, `list-page-fonts.sh` sa police. Ce qu'ils disent : `encre` à la migration du
2026-08-06, puis un thème `origine` écrit le 2026-08-08 **d'après le bloc sombre du constructeur Python** — le vert que l'opérateur a refusé. La page est revenue à `encre`, sans trame de fond et dans
la police du système. **Un thème neuf est demandé** : `S64 theme-moderne`.

**LES TÂCHES NE SONT PAS DANS CE DOCUMENT** : elles vivent dans `review-server/tasks.json`, et **une seule commande les lit et les écrit** : `php scripts/backlog.php`. `next` donne la première à
prendre, `list` les range — **les points `proposed` sortent à part, ils ne sont pas du travail en cours** —, `show <REF>` en ouvre un en entier, `add`, `set`, `describe`, `close` les modifient.
Toute écriture reconstruit la page `/backlog`. **Chaque point porte son analyse complète : `show` avant d'agir.** `describe <REF>` prend son texte par `@fichier`,
en argument ou sur l'entrée standard, et **refuse d'écrire quand il n'a rien reçu** — tapé sans texte pour relire un point, il en effaçait la description.

### Les outils

**LES CONTRÔLES, à lancer après avoir touché à ce qu'ils gardent :**

- `php scripts/check-text-width.php <fichiers>` — le standard de 200 caractères. Dans un fichier de code, seuls les commentaires sont jugés.
- `php scripts/check-subjects-against-inventory.php` — emprise, couvert et hauteur de chaque sujet contre sa ligne d'inventaire, et **il crie sur ce qu'il n'arrive pas à lire** au lieu de le sauter.
- `php scripts/check-review-pages.php` — les treize comportements de la page des sprites, les sept de la page Campagne.
- `php scripts/check-page-selectors.php` — chaque sélecteur qu'un script cherche existe-t-il dans son balisage ? Un sélecteur qui ne trouve rien ne lève rien : le bouton ne fait simplement plus rien.
- `php scripts/check-asset-theme.php` — aucun nom de thème hors de son module, et la complétude rapportée.
- `python3 scripts/check-subjects.py` — le référentiel contre les fichiers réellement livrés.
- `python3 scripts/check-code-language.py [fichiers]` — le vocabulaire technique français dans les **noms de fichiers** et les valeurs comparées. Balaie aussi `local/scripts/`. Il rend son
  **verdict** et le compte par répertoire ; `--detail` rouvre la liste. `bash scripts/dev/show-language-debt.sh` la donne pour le seul code versionné : **48 signalements**, le reste étant dans le
  jetable de l'agent.
- **LES VERDICTS NEUFS SE LISENT, ILS NE SE CHERCHENT PLUS** : `php scripts/remarks.php new` dit ce que l'opérateur a jugé ou écrit depuis la dernière lecture et rend 1 s'il y a quelque chose,
  `seen` marque le tout comme lu. **Le hook de fin de tour l'annonce tout seul**, sur chacune de ses sorties — il avertit, il ne refuse jamais pour ça.
- `bash scripts/diff-prompts.sh` — réassemble les consignes et dit ce qui a bougé depuis la référence figée. Ne dessine rien. `--freeze` refige.
- `python3 scripts/check-runes.py` — chaque rune déclarée au référentiel des créatures a sa forme, son tracé et sa couleur dans `assets/runes.json`, et réciproquement.
  **Les vingt formes se regardent** : `python3 scripts/dev/draw-runes-sheet.py` les dessine sur une planche, sous leur nom — une coordonnée ne se contrôle qu'à l'œil.
- `python3 scripts/set-rune-anchor.py --list` — les représentations de créature qui n'ont pas encore leur ancre de rune ; sans `--list`, elle se pose, et le point se lit sur la grille que
  `python3 scripts/dev/draw-anchor-grid.py <image>` dessine par-dessus la sprite grossie. **La rune posée se regarde** : `php scripts/dev/see-placed-rune.php [individu]` la trace sur la sprite à
  trois grossissements — c'est là qu'on voit si la forme, la couleur, la taille et l'ancre s'accordent, et que la taille ne suit pas celle du porteur.

**DEUX GÉNÉRATIONS DU MÊME VARIANT NE PARTENT PAS ENSEMBLE** : un verrou par variant sous `var/locks/`, pris avant tout le reste et rendu même sur échec, et
l'inscription au référentiel sérialisée par un verrou global. Éprouvé par `bash scripts/dev/trial-generation-lock.sh`, sans dépenser de génération.

**LES ESSAIS DES HOOKS** : `bash scripts/dev/trial-mot-ordre.sh` (la forme d'un ordre), `trial-hook-prompt.sh`, `trial-hook-stop.sh`, `trial-stop-transcrit.sh`, `test-stop-multiline.sh`. **Huit cas
de ce dernier sont rouges** : ils écrivent le `STOP` en entrée `user` du transcrit, soit la lecture d'ordres retirée le 2026-08-09, et non le porteur réel `queue-operation`. Ce sont des essais
d'agent, dans le répertoire de l'agent : ils se réécrivent au fil du dépilement, sans rien demander.

**LES SONDES, pour regarder au lieu de supposer** : `shoot-page.php` (la page telle qu'elle s'ouvre, fichier **ou adresse servie**), `probe-fsp.php`, `click-bouton.php`, `console-page.php`,
`probe-comparaison.php`, `probe-fermeture.php`, `probe-debordement.php`, `probe-drawer-path.php` (le chemin dans le tiroir), `probe-handled-remark.php` (une remarque classée ne s'affiche plus),
`probe-filter-state.php` (le compte sous les filtres), `probe-state-refresh.php` (l'état d'un sujet suit ses verdicts), `probe-theme-shot.php` (la page dans un thème forcé),
`probe-orphans.php` (la section hors modèle), `show-queue-operation.php` (les messages glissés en cours de tour).

**LE NAVIGATEUR DES SONDES NE S'ÉCRIT NULLE PART** : son chemin est la clé `browser` de `review-server/config.json`, et les trois gestes vivent dans le service `Browser` — `shot()` pour le tir
d'écran, `dom()` pour la page après exécution de son script, `console()` pour ce qu'elle a imprimé. Un navigateur absent le dit et nomme le chemin cherché.

**ET UNE SONDE N'ÉCRIT JAMAIS DANS LES DONNÉES DE L'OPÉRATEUR.** La page de revue enregistre chaque verdict sur le serveur au moment où on le coche : une sonde qui clique pour mesurer **écrit pour
de vrai**. Dix entrées vides ont ainsi été déposées dans `review-server/notes/sprites.json` le 2026-08-11, et il a fallu les retirer une à une. Toute sonde qui
clique neutralise l'envoi avant son premier clic. **Une sonde s'ajoute en fin de fichier, jamais avant `</body>`** : la page
construite n'en porte pas, donc un `str_replace` dessus ne change rien et la sonde rapporte un essai propre sur une page qu'elle n'a jamais touchée.

**ET UNE SONDE PASSE PAR LE SERVEUR, JAMAIS PAR LE FICHIER** (mesuré le 2026-08-11). La page appelle son style et son script par une adresse absolue, et lit ses verdicts par une requête : ouverte
depuis le disque, elle n'a ni style, ni script, ni état — tous ses boutons sont morts et toutes ses remarques vides. **Une sonde qui ouvre le fichier mesure la sonde**, et elle rapporte un défaut
qui n'existe pas. La copie sondée s'écrit sous `var/tmp/` et se charge par l'adresse du serveur, `…/var/tmp/…`, donc de la même origine que lui. C'est le point `W21 sondes-servies`.

**LES MESURES** : `python3 scripts/dev/list-off-band-sprites.py` (les boîtes hors fourchette), `measure-ink-off-band.py` (la hauteur de l'encre, pas de la boîte).

### CE QUI GOUVERNE UNE CONSIGNE — appris le 2026-08-12, au prix de vingt générations

**LA CAMÉRA APPARTIENT AU SOCLE, ET UNE SPRITE NE PEUT PAS LA CHANGER** (opérateur : « l'angle, c'est 60°, aucune sprite ne doit pouvoir changer ça, c'est défini
dans le socle »). Aucune fiche, aucun motif de reprise ne parle de prise de vue — même pour la confirmer : le générateur suit la clause la PLUS PROCHE du sujet,
donc une redite proche bat le socle. Trois échecs en viennent : un chêne basculé en vue de dessus par un motif de reprise, une créature dessinée à hauteur d'œil
parce que sa clause d'orientation disait « DE PROFIL », et un bâtiment en élévation parce que le socle disait « face avant, entière » sans dire ÉCRASÉE.

**LE GÉNÉRATEUR N'A AUCUNE MÉMOIRE, ET ON NE LUI PARLE JAMAIS DU PASSÉ** (opérateur, même jour). Ni « la version précédente », ni « c'est la faute à ne pas
refaire », ni la date d'un refus : il n'a rien vu de tout cela. Un motif de reprise est une PRESCRIPTION, placée en dernier parce que ce qui se lit en dernier
pèse le plus. L'historique va au commentaire du code, jamais dans la consigne.

**UN PARAMÈTRE SE DIT UNE FOIS, À SON NIVEAU** — socle, type, variante, fiche. Répété à deux niveaux, il se contredit dès que l'un gagne une précision : c'est
arrivé à la caméra, dite au socle et redite au rappel final dans d'autres mots. Quand un texte doit paraître deux fois, il est INTERPOLÉ depuis une seule
constante. **Et on reformule, on n'empile pas** : une clause qui a grossi se réécrit entière et plus courte.

**CE QU'ON ÉCRIT SE LIT DANS LA CONSIGNE ASSEMBLÉE, JAMAIS DANS LE FICHIER SOURCE** : `python3 scripts/generate-sprite.py <SUJET> <VARIANTE>` sans `--generate`
l'écrit sous `var/tmp/consignes/`. C'est là, et seulement là, que les contradictions se voient. Puis `bash scripts/diff-prompts.sh` dit ce qui a bougé sur les
soixante-quinze, et `--freeze` refige une fois le changement voulu. Tout est écrit à
[l'écriture des consignes](doc/conception/referentiels/visuel/assets/ecriture-des-consignes.md).

**ET TROUVER UNE CAUSE N'EST PAS AVOIR TROUVÉ LA CAUSE** : on relit la consigne entière une fois la première trouvée. Les paramètres que chaque type doit fixer
sont à [la grille des paramètres](doc/conception/referentiels/visuel/parametres-des-sujets.md), l'usure des bâtiments à
[son nœud](doc/conception/referentiels/visuel/usure-des-batiments.md), et `php scripts/check-subject-parameters.php -v` nomme ce qu'une fiche laisse non fixé.

### Ce qui est vrai du modèle, et qu'aucun fichier ne dit à lui seul

**AUCUNE RUNE N'EST TRACÉE SUR LA PAGE DE REVUE, ET AUCUNE ANCRE N'EST POSÉE** (opérateur, 2026-08-12) — un point posé sur la vue de face avait été recopié sur
les vues tournées, où il ne tombait nulle part. Les trois ancres sont retirées, `set-rune-anchor.py --list` redit vrai, et `runeMark()` rend une chaîne vide en
disant pourquoi. Le tracé revient en rappelant `Rune` depuis cette fonction ; ce qui attend est `S53 rune-creature`.

**LA RUNE SE TRACE AU RENDU, ET LES TROIS DONNÉES SONT EN PLACE** : la forme, la couleur et la taille (`size_tx`, un quart de case, constante) dans `assets/runes.json` ; l'**ancre** sur la
représentation, clé `rune_anchor_px` ; et **l'individu sur la case de la scène**, puisque la sprite est celle de l'espèce et qu'une rune désigne quelqu'un. La maquette la trace déjà.

**LES CLÉS SONT EN ANGLAIS, ET DEUX VOCABULAIRES DE TYPE COEXISTENT SANS SE CONFONDRE** : celui du référentiel (`assets/subjects.json`, onze types — `tree`,
`grass`, `bridge`…) et celui, plus grossier, du catalogue d'assets (`assets/catalogue.json`, lu par `asset_catalog.TYPE_LAYER` — `ground`, `path`, `fence`…).
**Le mot « sol » était un homonyme** : il nommait un type et un calque, et seul le type est devenu `ground` côté valeur — le calque porte le même mot en anglais
sans que ce soit la même notion. Ce qui reste en français, et attend `S80 dossiers-en-anglais` parce que ce sont des noms de répertoire : les clés
d'`asset_common.TYPES`.

**LA FOURCHETTE DE HAUTEUR SE DÉCLARE AU VARIANT**, en `TY`, clés `height_min_ty` et `height_max_ty`. Aucune formule ne la produit — aucun script ne sait qu'une herbe est courte et qu'un chêne est
grand. **Une fourchette absente arrête la commande**, sans repli. Les 69 fourchettes en place sont des **amorces reprises de l'ancienne formule et restent à relire**, sauf les 31 pièces
d'assemblage, fixées à la main à `1 TY` sans jeu.

**DEUX UNITÉS, `TX` ET `TY`, ET AUCUNE MESURE SANS LA SIENNE.** Tout est à `doc/conception/referentiels/technique/rendu-en-calques.md`.

**LA TOILE SE PREND SUR LE COUVERT**, pas sur l'emprise, quand le sujet en déclare un.

**LES RÉSEAUX NE SE FONT PAS MAINTENANT** (opérateur, deux fois le 2026-08-10) — formes manquantes **comme** reprises de pièces livrées. Refaire une pièce de `CH-019`, `CH-020` ou `OB-010` est une
génération de réseau, quel qu'en soit le motif. **Ne pas les reproposer.**

**UNE RÉFÉRENCE NE PRÊTE JAMAIS SA VUE**, et c'est ce qui faisait rater les vues tournées : la clause de référence disait « la référence fait foi pour la forme »
alors qu'elle montre le sud, pendant que la clause d'orientation demandait autre chose. Le générateur cherche maintenant le chemin de sa référence dans le
référentiel pour savoir quelle vue elle porte, et retire direction, pose et place des parties de ce qu'on lui emprunte quand elle diffère.

**UN ORDRE GLISSÉ EN COURS DE TOUR EST LU** — entrées `queue-operation` du transcrit, par `hook-stop.php` à la fin du tour et par
`php scripts/check-last-order.php <transcript.jsonl>` à la demande. Cette commande **arme sur un `GO` et désarme sur tout le reste** : c'est le dernier mot de
l'opérateur qui décide, jamais l'agent. Elle rend 0 si le dépilement est armé, 1 sinon. Ses essais : `bash scripts/dev/trial-last-order.sh`.

**LE HOOK DE BASE DE L'OPÉRATEUR EST BRANCHÉ** : `~/projects/local/hook/hook-pre-bash.sh`, en `PreToolUse` sur `Bash` seul. Il refuse les `;`, les `&&`, les `$(...)`, les redirections vers un
fichier, les chemins absolus dans le dépôt et le `sed -i`. **Sur `Write` ou `Edit` il enfermerait l'agent** — il lit leur charge comme une ligne de commande.

### Ce qui attend l'opérateur

- **Les sprites à juger**, sur la page de revue, toutes reprises le 2026-08-12 sur ses verdicts : `TR-063-v14` (le pommier revenu à la forme de sa v5),
  `TR-060-v9` (le chêne, tronc droit et fin, plus de racines évasées), `CH-021_shape-ns-v6` (le pont dans le style de sa v2), `SP-001-v5` (la créature à l'est,
  dans le bon sens), `HU-000-v6` (l'humain à l'est, redressé), `CH-021_shape-ew-v2`, et `BT-001-v13` avec ses propositions `p2-v7` et `p3-v7`.
- **Les quatre pages de revue portent le thème `graphite`**, sombre et unique, demandé le 2026-08-11 — à regarder et à dire s'il convient.
- **`BT-002 p2`** — la version abîmée du centre de soin, à écarter ; c'est un verdict, pas un dessin.
- **Les 66 fourchettes amorcées**, à relire.
- **LA PAGE `/backlog` NE MONTRE PLUS QUE CE QUI L'ATTEND** (2026-08-12 : « n'avoir que les topics qui ont besoin d'une réponse ») — un point `proposed`, une
  question, ou un point dont l'attente est sur lui. Le critère est au service, `Backlog::awaitsOperator()`. Le reste est compté et listé en une ligne, replié.
