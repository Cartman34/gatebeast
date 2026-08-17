# Les règles du dépôt — GateBeast

**Usage :** ce que lit et applique tout agent qui **construit** le projet, avant d'agir — les règles de tenue du dépôt et les renvois vers ce qui fait foi. On y arrive par
[AGENTS.md](../AGENTS.md), qui oriente chaque agent selon son rôle et dit à qui ces règles s'adressent. Dépôt du projet GateBeast, jeu original de collection de créatures.

**Intention :** réunir ce qu'un agent doit savoir pour ne pas nuire, et rien de plus. **Ce fichier n'est pas un fourre-tout** : une règle qui dit ce que le jeu doit être va à la conception, une règle
sur le contenu d'un document va dans ce document, une règle de conduite valable au-delà de GateBeast va à la méthode commune. Ne reste ici que ce qui n'a pas d'autre foyer — et ce qui s'en trouve un
déménage. Il ne couvre ni la cible du jeu, ni l'état des travaux, ni le vocabulaire : chacun a son document.

**Le générateur d'images n'est pas concerné par une seule ligne de ce document**, et il ne le charge plus : son enveloppe coupe la lecture automatique des instructions du dépôt. Une règle écrite ici
ne l'atteindra jamais — ce qui doit lui parvenir s'écrit dans sa consigne, jamais ici.

## Comment on respecte les règles

Cette section commande toutes les autres : elle ne dit pas quoi faire, elle dit comment les règles s'appliquent quand elles rencontrent la réalité du dépôt.

- **UNE RÈGLE ÉCRITE PRIME SUR L'EXISTANT, TOUJOURS.** Ce qui entoure le fichier qu'on modifie n'est **jamais** une référence : du code, du texte ou une convention qui contredisent une règle définie
  sont un **écart à corriger**, pas un exemple à suivre. On ne s'inspire de l'existant **que** là où aucune règle n'est écrite. Un agent qui aligne son travail sur ce qu'il voit autour de lui applique
  un standard que personne n'a décidé, et le propage : c'est ainsi qu'une faute d'un agent devient « le standard du projet » au bout de trois reprises. **Un standard se définit, il ne se déduit
  jamais**, et l'existant fautif se corrige au fil de l'eau, à mesure qu'on le croise.
- **LA LARGEUR DE LIGNE DU PROJET EST DE 200 CARACTÈRES, et l'outil qui la contrôle est `php scripts/check-text-width.php <fichiers>`**, à lancer sur tout fichier touché avant de le montrer. **La
  règle elle-même est montée à la méthode commune** (`~/projects/conceptions/methode/execution.md`, « Un seul standard de longueur de ligne ») le 2026-08-12 : qu'il n'y ait qu'un standard, qu'il
  remplace et annule tous les autres, que tout texte cherche à l'atteindre, et que replier plus court soit une substitution interdite. Ne restent ici que le chiffre et le nom de l'outil.

## Ce qui passe devant, et il n'y a qu'une exception

**LES SPRITES SONT LE CŒUR MÉTIER, ET RIEN NE PASSE DEVANT SAUF UN BLOCAGE** (opérateur, 2026-08-12 : « je veux ABSOLUMENT que les sprites avancent !! […] je veux que tu arrêtes de mettre en prio
des trucs devant !!! Le seul truc plus prio, c'est un blocage de l'app/maquette »). L'ordre est celui-ci, et il ne se rediscute pas séance par séance :

1. **Un blocage de l'application ou de la maquette** — ce qui empêche de produire ou de juger.
2. **Les sprites** : les produire, les faire juger, et **déboguer les consignes** quand une image revient fausse.
3. **Tout le reste**, dette technique comprise.

**ET LA DETTE SE DÉLÈGUE PLUTÔT QUE DE PASSER DEVANT.** Une passe de renommage, une aide à écrire, un commentaire à traduire : c'est du volume, pas du jugement — ça part à un sous-agent avec un
cadre fermé pendant que l'agent principal tient les sprites. L'inverse est admis si le sujet de sprite est lui-même mécanique et la dette délicate, mais **les deux ne s'arrêtent jamais tous les
deux**.

**Ce que ça coûte quand on l'oublie** : une séance entière peut passer en outillage, en tri et en règles — chacun de ces gestes étant juste pris isolément — sans qu'une seule sprite avance. C'est
arrivé le 2026-08-12, et c'est ce qui a fait écrire cette règle.

## Le système se change quand il gêne, il ne se subit pas

**QUAND L'ORGANISATION NE CONVIENT PAS À L'OPÉRATEUR, L'AGENT S'ADAPTE DE LUI-MÊME** (opérateur, 2026-08-12 : « tu dois t'adapter tout seul, tu dois être malléable […] tu te bases trop sur le
système en place alors qu'il faut faire des améliorations, aucun système ne sera parfait, surtout si on ne fait aucune amélioration »). Les règles de ce dépôt sont un outil, pas une excuse : un rituel
qui coûte à l'opérateur se **corrige**, il ne se sert pas une fois de plus en disant qu'il est écrit.

**Ce que ça veut dire concrètement, et c'est ce qui a été payé le 2026-08-12 :**

- **Décider plutôt que demander.** Une question dont l'agent a déjà toutes les informations n'est pas une question, c'est un report. Quatre l'ont été le même jour, sur un tri dont le rapport portait
  déjà chaque élément de réponse. Ce qui se demande, c'est ce qui engage l'opérateur — un arbitrage, un coût, une direction —, jamais ce qui se déduit d'une analyse qu'on vient de faire. **Le test
  qui tranche est monté à la méthode commune** (`collaboration.md`, « Comment l'agent s'organise » et « Un lot que l'agent qualifie lui-même de "sans ambiguïté" ») : il ne se recopie pas ici.
- **Envoyer plutôt que rendre compte.** Un compte rendu qui précède l'action alors que l'action était possible fait attendre deux fois. **Et une question d'assistant ne se transfère jamais à
  l'opérateur** — c'est l'agent principal qui y répond (`execution.md`, « Des assistants persistants »).
- **Changer la règle qui gêne, dans la foulée.** Le format d'une question, le récapitulatif de fin de message, l'ordre de la pile : quand l'un d'eux ralentit au lieu d'aider, il se réécrit ici, tout
  de suite, avec la raison. Une règle qu'on applique en sachant qu'elle nuit est une faute d'agent, pas une obéissance.

**Intention :** un cadre ne vaut que par ce qu'il rend possible. Figé, il devient l'endroit où l'on se réfugie pour ne pas juger — et l'opérateur se retrouve à piloter une organisation au lieu de
piloter son projet.

## Les modes de travail et la conduite

- **Deux modes de travail, et l'opérateur seul les fixe.** Un **mode** dit qui décide de l'avancée entre deux gestes de l'agent — lui-même, ou l'opérateur.
  - **Dépilement continu** — l'agent prend la pile du `SUIVI.md` dans son ordre et traite les sujets les uns après les autres sans rien demander. Il ne s'arrête que si le sujet porte une question, un
    inconnu, une incohérence, ou s'il veut proposer quelque chose ; sinon il fait, et il rend compte quand c'est fini. C'est le mode **par défaut**.
  - **Lot** — l'agent n'exécute rien avant d'avoir annoncé ce qu'il compte faire et reçu la validation de l'opérateur. Ce qui remonte remonte groupé, jamais sujet par sujet, et l'opérateur tranche en
    bloc. Y vont sans qu'il ait à le redire : toute proposition, toute génération d'image, tout verdict à demander.
- **Le mode s'annonce avant de commencer, et l'agent s'arrête sur cette annonce** — à commencer par son démarrage, où c'est le mode par défaut qui s'applique et où il doit donc l'annoncer comme les
  autres : l'opérateur confirme, et l'agent part. Une annonce sans arrêt ne sert à rien, elle passe dans le flux et l'opérateur découvre le mode au résultat.
- **LA FORME D'UN ORDRE, ET ELLE EST LA MÊME POUR LES DEUX MOTS** (opérateur, 2026-08-11 : « il doit avoir les mêmes règles »). Un ordre **ouvre sa ligne**, s'écrit **en capitales**, et se termine
  par **un caractère blanc ou la fin de la ligne** — rien ne lui est collé. Donc `STOP` compte, `STOP regarde plutôt ça` compte, et ne comptent pas : `stop`, `Stop`, `STOPPE`, `STOP!`, ni un mot
  glissé au milieu d'une phrase. Les capitales sont le geste délibéré qui distingue l'ordre de la conversation : `stop` et `go` sont trop courants en français ordinaire pour engager la garde. Éprouvé
  cas par cas : `bash scripts/dev/trial-mot-ordre.sh`.
- **`GO` et `STOP` sont les deux seuls mots qui lancent et arrêtent le dépilement, et ils sont stricts.** Rien d'autre ne vaut reprise : aucune phrase ne s'interprète comme un feu vert, et le silence
  encore moins. **Tout arrêt met fin au `GO`** — une question de l'opérateur, un ordre ponctuel, une interruption : dès que l'agent s'arrête, l'autorisation est consommée et ne se reprend pas d'elle-
  même une fois la parenthèse refermée. Il en faut une neuve, donnée explicitement.
- **UN `GO` OU UN `STOP` ENVOYÉ PENDANT QUE L'AGENT TRAVAILLE VAUT COMME ORDRE, MAIS N'ARME NI NE DÉSARME RIEN.** `UserPromptSubmit` ne se déclenche que sur un message qui **ouvre** un tour :
  un message glissé en cours de tour est bien reçu et bien lu par l'agent, mais aucun hook ne le voit. Mesuré le 2026-08-08 — deux `GO` en cours de tour n'ont rien armé, le même `GO` en ouverture de
  tour a armé dans la seconde. **L'agent obéit à l'ordre, dit que l'état ne le reflète pas, et n'y touche pas** ; à l'opérateur de renvoyer le mot en ouverture de tour s'il veut la garde armée.
- **UN ORDRE REÇU EN COURS DE TOUR SE FAIT LIRE PAR LA COMMANDE, IMMÉDIATEMENT — CE N'EST PAS FACULTATIF** (opérateur, 2026-08-12 : « j'ai lancé un stop mais tu
  n'as pas appelé la commande de check, tu dois le faire », puis « il faut rendre générique la commande pour qu'elle accepte aussi le go »).
  `php scripts/check-last-order.php <transcrit.jsonl>`, le transcrit étant le `.jsonl` le plus récent sous `~/.claude/projects/-home-sowapps-projects-gatebeast/`.
  **Elle lit le DERNIER mot de l'opérateur et met la garde dans l'état qu'il commande** : un `GO` arme, tout le reste désarme. Elle rend 0 quand le dépilement est
  armé, 1 quand il ne l'est pas. **Elle ne viole pas la règle suivante, elle la tient** : l'agent ne peut rien lui dicter — c'est le transcrit qui décide, et le
  transcrit est la parole de l'opérateur. Sans elle, un mot glissé en cours de tour n'est lu par personne avant le tour suivant, et l'état ment dans un sens comme
  dans l'autre. Ses essais : `bash scripts/dev/trial-last-order.sh`.
- **L'ÉTAT D'ARMEMENT DU DÉPILEMENT N'APPARTIENT PAS À L'AGENT, ET IL N'A JAMAIS À Y TOUCHER — NI POUR L'EFFACER, NI POUR L'ÉCRIRE.** `var/hooks/dequeue-armed` est écrit par le hook du prompt, et par
  lui seul : le `GO` de l'opérateur l'arme, son `STOP` le désarme, il expire seul au bout de trois heures. Une garde qu'on peut retirer soi-même n'est pas une garde, et un armement qu'on peut écrire
  soi-même est un ordre qu'on se donne à la place de l'opérateur. **Les deux gestes ont été faits le 2026-08-08**, et chacun tenait à une confusion que voici levée :
  - **La règle d'arrêt ci-dessus est une règle de conduite, elle ne décrit pas un fichier.** « Tout arrêt met fin au `GO` » dit à l'agent de ne pas repartir de lui-même. Elle ne lui demande pas de
    mettre l'état à jour pour le refléter — c'est cette lecture qui a fait supprimer le fichier, en croyant bien faire.
  - **Un hook qui n'arme pas est un défaut à constater, pas à compenser.** Il s'inscrit à la pile avec ce qui a été observé. Le suppléer à la main donne une page qui a l'air juste et une garde qui ne
    garde rien — soit exactement l'inconvénient qu'on croyait corriger, en pire, puisqu'il ne se voit plus.
  - **L'empêchement est mécanique, pas moral** : `scripts/hook-guard-dequeue.sh`, déclaré en `PreToolUse`, refuse toute commande et toute écriture qui touche à cet état ou à la garde elle-même. La
    lecture reste libre — l'agent doit pouvoir dire si le dépilement est armé. Ses essais : `bash scripts/dev/trial-garde-depilement.sh`.
  - **`.claude/settings.json` n'est PAS dans la liste des fichiers gardés, et c'est délibéré** (opérateur, 2026-08-08). Débrancher la garde en modifiant le fichier qui la déclare serait le chemin de
    contournement évident, mais toute modification de ce fichier demande systématiquement l'autorisation de l'opérateur : la barrière existe déjà, en amont, et elle est humaine. L'y ajouter
    coûterait plus qu'elle ne protège — l'agent ne pourrait plus déclarer aucun hook sans passer par l'opérateur. **Ne pas le reproposer.**
- **Tant que le dépilement n'est pas lancé, l'agent ne modifie que le `SUIVI.md`** — aucun autre fichier, quelle qu'en soit l'évidence. Ce qui survient avant le `GO` entre dans la pile et y attend.
- **UNE DÉCISION S'ENREGISTRE TOUJOURS, ET UNE SEULE FOIS, LÀ OÙ ELLE S'APPLIQUE** (opérateur, 2026-08-11 : « tu dois toujours enregistrer les décisions, tu dois avoir une organisation propre et qui
  te permet de n'avoir aucune perte d'info et pourtant être optimisée en termes de perf et de token »). Chaque foyer est connu et il n'y a pas d'hésitation à avoir : une **règle de conduite** va aux
  règles du dépôt ou à la méthode commune ; ce que le **jeu doit être** va à la conception ; un **mot** va au glossaire ; ce qui concerne **un point** va dans sa description. **Le suivi ne reçoit
  qu'une chose : où en est le travail**, et il renvoie au foyer au lieu de recopier.
- **ON NE RETIRE RIEN AVANT D'AVOIR VÉRIFIÉ QUE LE FOYER EXISTE, ET « C'EST DANS GIT » N'EST PAS UN FOYER.** Un diff de deux mille lignes est techniquement récupérable et pratiquement perdu :
  personne ne l'ouvre en reprenant. Ce qu'on élague se **déplace** vers un fichier versionné qui a un nom et une adresse — c'est ce qu'est
  [le journal des séances](journal-des-seances.md) —, jamais vers l'historique seul. Écrit le 2026-08-11, après avoir supprimé deux mille lignes en **affirmant**
  que tout vivait ailleurs, sans l'avoir établi.
- **CE QUI COÛTE, C'EST LA COPIE, PAS L'ÉCRITURE.** Une décision recopiée dans deux endroits se contredit au premier changement, et elle se relit deux fois à chaque reprise — c'est là que partent les
  jetons. Une décision écrite une fois, à son foyer, ne se perd pas pour autant : elle se retrouve **parce qu'on sait où chercher**, pas parce qu'elle est partout.
- **LE SUIVI NE GARDE PAS D'HISTORIQUE, ET IL LE DIT LUI-MÊME EN TÊTE** — « seul l'état courant compte ». Empiler une section par séance le contredit : ce qui est fait, décidé et rangé ailleurs sort
  du suivi quand la séance se ferme, et ce qui reste tient dans l'état du moment. Un suivi qui grossit à chaque séance devient le document que personne ne relit en entier, donc celui où l'on perd.
- **Le suivi est le support de l'agent** : il l'écrit quand il veut, sans demander, et il doit permettre à tout moment d'être coupé et relancé de zéro **sans aucune perte**. Ce qui n'y est pas écrit
  n'existe pas.
- **CE QUE L'OPÉRATEUR DEMANDE S'AJOUTE ; CE QUE L'AGENT VOIT SE PROPOSE** (opérateur, 2026-08-12 : « y'a pas mal de topics qui ont été demandés et tu en as fait
  des propositions au lieu de les ajouter, du coup la demande est redondante »). Une demande formulée **est** la validation : la remettre en proposition la lui
  fait valider une seconde fois, et elle attend pendant ce temps. Le doute se tranche à la source : **s'il l'a dit, c'est une task ; si c'est moi qui l'ai vu,
  c'est une proposition.**
- **UNE RÉGRESSION SE CORRIGE SANS DEMANDER** (même relevé) — « les régressions doivent être corrigées sans demander. Sauf si ça impacte ou risque une autre
  régression ou si une décision fonctionnelle est à prendre ». Les deux exceptions sont les siennes et elles sont étroites : un correctif qui menace autre chose,
  ou un choix de fonctionnement à faire. Hors de là, ce qui marchait et ne marche plus se répare, point.
- **CE QUI EST DEMANDÉ SUR LA PAGE DE REVUE DES SPRITES SE FAIT SANS REDEMANDER** (même relevé) — « ce que je demande avec la page de review sprite doit être fait
  sans le demander, c'est moi qui te l'ai demandé ». Une remarque posée sur une image est un ordre déjà donné : elle ne se refait pas valider en conversation.
- **LA PILE SE RELIT, ET CE QUI N'A PLUS D'OBJET SE FERME** (même relevé : « pas mal de topics sont obsolètes aussi »). Une task dont le motif a disparu reste
  sinon à encombrer chaque lecture, et fait passer pour du travail dû ce qui n'existe plus.
- **MAIS UN SUJET NEUF SE FAIT VALIDER — L'AGENT N'EN OUVRE PAS DE LUI-MÊME** (opérateur, 2026-08-08). Tenir le suivi et décider de ce sur quoi le projet travaille sont deux choses : l'agent écrit,
  met à jour, décrit et ferme librement, et il ajoute sans demander **ce que l'opérateur lui dit d'ajouter**. Ouvrir un sujet que personne n'a demandé, non : « tu risques de t'enfoncer dans une
  mauvaise pratique sans vérification ». Un point ouvert oriente le travail de toutes les séances suivantes, et un agent qui remplit lui-même sa propre pile finit par travailler sur ce qu'il a décidé
  seul, en croyant suivre le projet.
- **LA PRIORITÉ DIT LA NATURE DU POINT, PAS SON URGENCE RESSENTIE — QUATRE TRANCHES, ET ELLES SONT FERMÉES** (opérateur, 2026-08-13 : « ce qui est hotfix doit être de prio 0X, ce qui est sprite doit
  être 2X, le reste est 3X 4X 5X… 1X n'est pas utilisé pour le moment »).
  - **0 à 9 — un hotfix** : ce qui empêche de produire ou de juger. C'est la seule tranche qui passe devant les sprites, et c'est exactement l'exception que « ce qui passe devant » définit plus haut.
  - **10 à 19 — inutilisée**, gardée libre par l'opérateur. On n'y range rien tant qu'il ne dit pas ce qu'elle porte.
  - **20 à 29 — une sprite** : la produire, la faire juger, déboguer sa consigne.
  - **30 et au-delà — tout le reste**, dette technique comprise, les dizaines servant à ordonner entre eux.
  **Cette tranche remplace la réserve des priorités 1 à 10**, qui datait du 2026-08-08 : le rang ne dit plus qui l'a décidé, il dit de quoi il s'agit. L'agent classe donc lui-même un point dans sa
  tranche, et il n'a plus à commencer à 11 — ce qu'il **ouvre** de sa propre initiative reste, lui, une proposition à valider, ce qui est une autre règle.
- **CE QUI SE FAIT À LA PLACE : on le fait, ou on le propose.** Un défaut trouvé en chemin se corrige dans la foulée — c'est déjà la règle, « ce qui manque se fait ». Ce qui est trop gros pour être
  fait dans la foulée se **propose** à l'opérateur, avec ce qu'il coûte, et n'entre à la pile qu'une fois validé. Un défaut qu'on ne peut ni faire ni proposer tout de suite se dit dans le compte
  rendu, il ne s'inscrit pas de force.
- **UN POINT SE CITE PAR SON CODE ET SA REF, ET LE CODE PORTE TOUJOURS SON NOMBRE — POUR TOUTES LES SÉRIES** (opérateur, 2026-08-11 : « comme pour les questions, comme pour tout »). La forme est
  `S59 noms-scripts-fr`, jamais « S noms-scripts-fr » : une lettre collée sur une ref **ressemble** à un code sans en être un, et l'opérateur ne peut pas répondre avec. `php scripts/backlog.php list`
  donne le code de chaque point ; il se lit **avant** de citer le point, jamais après coup. La faute a été commise sur une question, corrigée, puis refaite trois messages plus tard sur un sujet.
- **Tout point ouvert porte un code et un numéro**, pour que l'opérateur réponde par lui seul : **Q** une question, **P** une proposition, **S** un sujet, **T** un test, **W** une alerte. Les séries
  sont indépendantes, continues tant qu'un point reste ouvert, et repartent à 1 quand la série se vide. Un point ouvert vit dans le suivi, jamais dans la conversation.
- **CE QUI VIT DANS LE SUIVI, C'EST LE POINT — PAS LA QUESTION. UNE QUESTION SE POSE EN ENTIER, DANS LE MESSAGE.** Le code sert à répondre, il ne remplace pas ce qu'on demande : posée, une question
  dit **ce qui est demandé**, **les options** quand il y en a, **ce qui dépend de la réponse** et **ce que l'agent recommande**. Ce qu'elle n'a pas à redire, c'est l'analyse — elle reste au point, et
  `show <REF>` l'ouvre. Énumérer des libellés numérotés n'est pas poser des questions : un titre nomme un sujet, il n'appelle pas de réponse, et l'opérateur ne peut que demander à l'ouvrir — un
  aller-retour de plus pour chaque point, ce que la numérotation existait justement pour éviter (constaté le 2026-08-08). Le format « code et trois mots » ne vaut que pour les **deux lignes de
  récapitulatif** ; l'appliquer au corps du message revient à n'avoir rien demandé.
- **UNE QUESTION A UN FORMAT, ET IL EST OBLIGATOIRE** (opérateur, 2026-08-09 : « le formatage des questions est une obligation »). Cinq éléments, dans cet ordre, et **rien d'autre** :
  1. **Un code de la série `Q`, et lui seul** — `Q9`, `Q10`. Une question porte un numéro de question, jamais celui d'une proposition ni d'un sujet : c'est par ce
     code que l'opérateur répond, et un code emprunté à une autre série rend la réponse ambiguë. **Toutes les questions ouvertes se posent, à chaque fois.**
  2. **UNE LIGNE DE CONTEXTE, AVANT LA QUESTION, ET ELLE EST OBLIGATOIRE** (opérateur, 2026-08-11 : « quand tu poses une question, tu dois absolument donner le contexte en une ligne avant, sinon ça
     n'a juste aucun sens »). Elle dit **de quoi on parle** — le sujet, l'état, ce qui a produit la question —, en une seule ligne. Sans elle, l'opérateur reçoit des options sans savoir sur quoi
     elles portent, et doit ouvrir le point pour comprendre ce qu'on lui demande : c'est l'aller-retour que le format existe pour éviter. **Une ligne, pas un exposé** — le diagnostic reste au point.
  3. **Une phrase** qui dit ce qui est demandé.
  4. **Les réponses possibles, repérées `A`, `B`, `C`, une ligne chacune** : ce qu'on fait, puis ce que ça coûte, dans la même ligne. **Jamais numérotées** — les
     chiffres sont pris par les questions, et « 1 » ne dit alors plus si l'on parle de la première question ou de la première réponse.
  5. **Une ligne de recommandation** : laquelle, et pourquoi en quelques mots.
  6. **Rien de plus.** Pas de rappel du contexte, pas d'exposé de la cause, pas de récit de ce qui a été trouvé — tout cela vit au point, et `show <RÉF>` l'ouvre.
- **CE QUE LE FORMAT INTERDIT, ET C'EST LUI QUI COÛTE** : noyer la question dans ce qui l'a produite. Une question qui commence par expliquer le défaut, ses causes et ce qui a déjà été corrigé oblige
  l'opérateur à lire une page pour trouver la ligne qui appelle sa réponse — et il la relit deux fois pour être sûr de n'avoir rien manqué. **Le diagnostic n'est pas la question.** Une question qui
  dépasse une dizaine de lignes n'est pas mal écrite : elle contient autre chose qu'une question, et c'est cet autre chose qui doit sortir.
- **UN MESSAGE DIT LE RÉSULTAT ET CE QUI ATTEND L'OPÉRATEUR, JAMAIS LE CHEMIN QUI Y MÈNE** (opérateur, 2026-08-13 : « pourquoi tu m'envoies des pavés ? c'est
  interdit »). Ce qui vaut pour une question vaut pour un compte rendu : au-delà d'une dizaine de lignes, un message contient autre chose qu'un message, et c'est
  cet autre chose qui doit sortir. **L'analyse vit au point, et `show <REF>` l'ouvre** — la recopier dans le message fait relire deux fois et noie la ligne qui
  appelle une réponse. Trois messages de trente à cinquante lignes sont partis le 2026-08-13 alors que leur diagnostic était déjà écrit à son foyer.
- **ET UNE RÈGLE QUE L'OPÉRATEUR DONNE S'ÉCRIT DANS LA FOULÉE, À SON FOYER** (même jour : « pourquoi tu ne l'écris pas directement plutôt que de créer un
  document encore plus lourd pour te dire de faire plus tard ce que tu dois faire maintenant ? »). L'inscrire à la pile pour plus tard ajoute un point à relire,
  laisse la règle inappliquée entre-temps, et fait payer deux fois le même geste. **Cela prime sur l'attente du `GO`** : ce qui est dicté n'attend pas d'être
  dépilé, il est déjà décidé.
- **Chaque message se termine par deux lignes de récapitulatif** : ce qui attend l'opérateur, ce qui attend l'agent. Code et trois mots par point, quatre points par ligne au plus, un compteur au-delà.
- **L'OPÉRATEUR N'ATTEND QUE DEUX CHOSES DE L'AGENT : UN `GO` À DONNER, OU DES QUESTIONS À TRANCHER** (opérateur, 2026-08-11 : « y'a que deux types de choses que tu attends de moi : un go ou des
  questions »). La ligne « attente opérateur » ne porte donc que l'un ou l'autre, et **rien d'autre n'y figure** : ce qui attend vraiment une réponse se pose comme question, au format, dans le corps
  du message ; le reste sort du récapitulatif. Un sujet nommé en trois mots dans cette ligne **ressemble** à une demande sans en être une — l'opérateur ne peut pas y répondre, et il doit demander ce
  qu'on attend de lui, soit exactement l'aller-retour que le récapitulatif existe pour éviter. Ce qui se juge sur la page de revue s'y juge : ce n'est pas une attente de message.
- **LE SERVEUR DE REVUE SE FERME AVANT DE CLORE LA SÉANCE, ET C'EST L'AGENT QUI LE FAIT** (opérateur, 2026-08-12 : « en fin de session, il faut que tu fermes le serveur »). Une commande :
  `php scripts/stop-review-server.php`. Laissé ouvert, il tient le port, et le démarrage de la séance suivante échoue sur « Address already in use » — c'est arrivé le 2026-08-12, sur un serveur qui
  écoutait depuis dix heures et demie. Le geste va avec la mise à jour du suivi et la proposition de commit : c'est la même fin de séance.
- **UN SOUS-AGENT CONTRÔLE PAR COMMANDES NUES, ET SEULEMENT CE QU'IL A TOUCHÉ** (opérateur, 2026-08-12 : « attention avec xargs »). Un tube, un `find`, un `xargs` ne s'analysent pas : la garde
  redemande l'autorisation à chaque appel, et l'interruption tombe au milieu du travail. `php -l <fichier>` fichier par fichier, `php scripts/check-text-width.php <liste>` en une seule commande. Et le
  balayage d'un répertoire entier pour contrôler dix-sept fichiers élargit le périmètre sans le dire : un exécutant contrôle **ce qu'il a modifié**, nommément. Cela s'écrit dans sa consigne.
- **Toute génération d'image part en tâche de fond** — on ne l'attend jamais. Plus généralement, tout ce dont l'agent n'a pas besoin pour continuer part en tâche de fond et rend la main aussitôt.
- **On dépile, on ne commente pas la pile.** Constater ce qui manque et le dire n'est pas un travail : ce qui manque se fait. Une tâche ne remonte à l'opérateur que si elle est finie, ou si elle est
  bloquée par une décision qui lui appartient. **Ce qui fait sortir un sujet du dépilement, et rien d'autre : une question, un inconnu, une incohérence, ou quelque chose que l'agent veut proposer.**
  Tout le reste se fait — l'ordre de la pile ne se redemande pas.
- **On travaille par lots, jamais un sujet à la fois.** Plusieurs générations partent ensemble, l'opérateur ne repasse qu'une fois sur le lot entier et tranche en bloc. Un sujet traité seul
  consomme un aller-retour complet pour un seul verdict.
- **On ne s'arrête que pour une question dont la réponse change ce qui va être construit** — jamais pour demander l'autorisation d'avancer sur ce qui est déjà décidé. Les questions se posent
  **numérotées**, groupées, et l'opérateur y répond par leur numéro.
- **Tout ce que l'opérateur dit entre dans la pile du `SUIVI.md`, immédiatement et avant d'être traité.** Une demande, une capture, un défaut relevé en passant : rien ne reste dans la conversation. Le
  contexte se résume et se perd, la pile non — une remarque perdue se paie en la faisant redire. Une capture s'écrit **en toutes lettres**, puisque l'image ne survit pas au résumé alors que sa
  description oui. Quand elle ne suffit pas à savoir quoi faire, la ligne le dit : ce que je vois, mon appréciation, et ce qui me manque. Repérer le manque et le nommer est le travail de l'agent ;
  trancher est celui de l'opérateur.
- **On regarde son propre résultat avant de le montrer.** Une image produite se regarde, une page publiée s'ouvre, et ce qui cloche se dit **avant** que l'opérateur ait à le signaler. Trois tentatives
  sur le même sapin, une popin sans ses valeurs, un bouton étalé sur toute la largeur : chaque fois le défaut était visible et c'est lui qui l'a vu. Livrer sans regarder transforme chaque sujet en
  trois allers-retours au lieu d'un.
- **Une demande dont la réponse échoue deux fois se relit à la source avant d'être retentée.** Trois sapins identiques sont sortis parce que la description disait l'inverse du modèle : la troisième
  relance aurait dû être une relecture. Regarder la référence soi-même vaut mieux que faire attendre l'opérateur.

## Où vit quoi

- **`doc/conception/` — la cible, et elle fait foi.** Rapatriée ici depuis `conceptions/`, elle suit désormais le versionnage du projet. Chemin de reprise : la méthode
  (`~/projects/conceptions/methode/`), puis `doc/conception/vision.md`, `doc/conception/questions.md`, puis la descente jusqu'au nœud concerné en lisant ses ancêtres.
- **`doc/` — la documentation du projet.** `doc/conception/` décrit la **cible** et fait foi ; le reste de `doc/` décrira l'existant.
- **`SUIVI.md` — où en est le travail** : état courant, points ouverts, défauts constatés, outils. À lire en premier pour reprendre. **`PLAN-ACTION.md` — le découpage en briques vers la 0.1.** Ni l'un
  ni l'autre n'est de la conception : ils décrivent le chemin, jamais la cible.
- **`scripts/` — l'outillage de production, INTÉGRALEMENT EN ANGLAIS AMÉRICAIN : noms, contenu, commentaires.** C'est figé et inchangeable (opérateur, 2026-08-08). **Un nom technique est anglais et le
  reste même quand on en parle en français** — on dit « le `drawer` », jamais « le tiroir » ; le français ne sert qu'à l'expliquer. Cela vaut pour tout ce que la machine lit ou compare : fichiers,
  fonctions, variables, classes, clés de données, noms de composants. **Seuls les textes destinés à l'opérateur restent en français** — messages affichés, libellés, descriptions.
- **`assets/` — les images produites.** **Rien ne se jette** : une image écartée cesse d'être montrée, elle n'est pas supprimée.
- **ET L'ARCHIVE COMPLÈTE DES IMAGES VIT HORS DU DÉPÔT, DANS `~/projects/gatebeast-assets/`** — elle contient **tout** ce qui a été produit depuis le début, versions dépassées comprises, et c'est
  elle qui rend vraie la phrase « rien n'est jamais perdu ». Le dépôt, lui, ne versionne que les images **vivantes** : les assets du POC et les planches courantes. Constat retrouvé le 2026-08-11 en
  auditant le journal des séances, où il était le seul à le porter : **une information que seul un document de séance porte est une information qu'on perdra**, et c'est exactement ce que l'élagage
  aurait effacé.
- **LA RACINE DE `local/` APPARTIENT À L'OPÉRATEUR, ET À LUI SEUL.** On n'y trouve que ses fichiers, et un agent **n'y touche jamais** — il ne les modifie pas, ne les déplace pas, ne les supprime pas
  et ne les lit pas. Tout ce qu'un agent produit descend dans un **sous-dossier** : `local/scripts/` pour ses scripts jetables, `local/extraits/` pour ses découpes d'images, et ainsi de suite. Une
  racine où tout traîne cesse d'être utilisable : on ne distingue plus ce qui est en cours de ce qui reste d'avant-hier, et les fichiers de l'opérateur s'y noient.
- **`local/` — le répertoire de travail de l'agent** : essais, mesures, extraits, scripts jetables, jamais commité. **L'OUTILLAGE N'Y ÉCRIT JAMAIS RIEN** : ce répertoire appartient à l'agent, et un
  fichier qu'un script y dépose n'a plus de propriétaire — trente-cinq brouillons de consigne s'y étaient accumulés sans que personne sache qui les produisait ni s'ils servaient encore (opérateur,
  2026-08-06). Toute trace d'exécution va sous `var/`, avec les rapports et les journaux.
- **DEUX PORTÉES, ET ELLES SONT FIGÉES : `local/` EST À L'AGENT, `var/` EST À L'APPLICATION.** C'est le seul critère, et il ne se discute pas au cas par cas (opérateur, 2026-08-08). **Tout fichier
  que l'agent produit pour lui-même vit sous `local/`** — brouillons, essais, mesures, extraits, scripts jetables, rédactions en attente d'être injectées ailleurs. **`var/` ne reçoit que ce qu'un
  programme écrit en tournant** : rapports de production, journaux, traces d'exécution. Un brouillon écrit à la main n'est pas une trace d'exécution, même s'il est jetable : **c'est l'auteur qui
  décide de la portée, jamais la durée de vie**. La formulation précédente donnait `var/tmp/` pour « un brouillon de consigne » — c'est ce qui a fait ranger sous `var/` des rédactions d'agent.
- **`local/tmp/` EST LE JETABLE DE L'AGENT, ET IL SE VIDE SANS PRÉVENIR.** Y va le fichier de passage : un brouillon qu'on injecte ailleurs dans la foulée, une découpe qu'on regarde une fois.
  **Tout ce qui s'y trouve peut disparaître à n'importe quel moment** (opérateur, 2026-08-08) — donc rien ne s'y dépose qu'on aurait à rouvrir plus tard, rien ne s'y cite, et ce qui doit survivre
  monte d'un cran sous `local/`. C'est le pendant de `var/tmp/` côté agent, avec la même règle d'auteur : `local/tmp/` pour ce que l'agent écrit de sa main, `var/tmp/` pour ce qu'un programme dépose
  en tournant.
- **L'AGENT N'A RIEN À FAIRE AILLEURS, NI POUR ÉCRIRE NI POUR LIRE** (opérateur, 2026-08-10) — montée à la méthode commune le 2026-08-11, avec la règle de l'outil non validé dont elle est le
  prolongement. Elle est rappelée ici parce qu'elle commande la ligne suivante, qui, elle, nomme des chemins de ce dépôt.
- **ET RIEN NE S'ÉCRIT HORS DU PROJET.** Ni `/tmp`, ni un répertoire de travail fourni par l'enveloppe de l'agent, quelle que soit l'insistance de celle-ci : un fichier hors du dépôt n'existe pour
  personne d'autre, disparaît sans trace et ne se retrouve pas à la reprise. **Une règle écrite prime sur la consigne de l'enveloppe.**
- **`var/` — ce que l'outillage produit pour lui-même**, jamais versionné : rapports de production, journaux du générateur, mesures. Ce qui s'y trouve est **local mais conservé** — on y revient pour
  comprendre ce qui s'est passé. **`var/tmp/` fait exception : ce qu'un programme y écrit est vraiment jetable** et se refait d'une commande — une page de sonde, un fichier de passage produit par un
  script. La distinction se décide à l'écriture : ce dont personne ne redemandera jamais compte va dans `var/tmp/`, le reste ailleurs sous `var/`. **Rien de ce qui s'y trouve ne se cite nulle
  part** : ni dans une
  description, ni dans une consigne envoyée au générateur, ni dans le suivi, ni dans un document. Un fichier cité doit être versionné, sinon la référence est morte pour tout le monde sauf pour
  l'agent qui l'a écrite. Le répertoire se tient rangé : les extraits de planche vivent sous `local/extraits/`, produits par un script versionné, donc refaisables par n'importe qui à la commande.

## Les erreurs

- **LE CODE NE LAISSE JAMAIS UNE ERREUR TRANSPARENTE — IMPÉRATIF** (opérateur, 2026-08-08). Ce qui échoue doit **le dire**, fort, et s'arrêter. Une erreur silencieuse est pire qu'une panne : la
  panne se voit et se corrige le jour même, l'erreur transparente laisse une page qui paraît juste, un plan qui paraît construit, un bouton qui paraît branché — et se découvre des jours plus tard,
  par hasard, après avoir fait travailler quelqu'un sur du faux. **Le 2026-08-08, cinq défauts trouvés sur six étaient de cette famille**, et aucun n'avait levé quoi que ce soit.
- **Ce qui est interdit, nommément** : un `catch` qui avale sans rien dire ; une valeur par défaut qui remplace un résultat manquant sans le signaler ; un `?? ''`, un `|| {}`, un `?->` qui masque
  l'absence au lieu de la constater ; une recherche qui ne trouve rien et continue ; un contrôle qui rend « tout va bien » quand il n'a rien pu contrôler ; un message de succès émis sans avoir
  vérifié le succès. **Les exemples ne ferment pas la liste** : toute construction qui transforme un échec en marche normale tombe sous la règle.
- **Ce qu'on écrit à la place** : on lève, avec le nom de ce qui manquait et l'endroit où on le cherchait. Un outil qui ne peut pas conclure dit « je ne peux pas conclure » — ce n'est pas un verdict
  favorable. Un repli n'est légitime que s'il est **décidé, écrit et annoncé** : la page qui n'enregistre rien quand le serveur est absent le dit dans son commentaire et dans le suivi, et c'est ce
  qui la distingue d'une page qui perd les données en silence.
- **CE QUI A DÉJÀ MARCHÉ SE REPREND À SA SOURCE, JAMAIS DE MÉMOIRE** (opérateur, 2026-08-12 : « je ne comprends pas que tu développes un truc qui fonctionne et
  quand tu dois le refaire, tu refais les mêmes erreurs et ça ne fonctionne pas — tu dois éviter de refaire encore et encore les mêmes erreurs »). Un mécanisme
  retiré vit dans l'historique : `git show <commit>:<fichier>` le rend intact, avec les corrections que ses allers-retours avaient payées. **Réécrit de mémoire,
  il revient avec les fautes d'origine et sans les correctifs** — c'est le même coût que la règle « migrer, c'est déplacer » chiffre déjà, appliqué au temps au
  lieu de l'espace. Payé le jour même : le relevé, retiré le matin et réécrit l'après-midi, est revenu cassé.
- **ET UN ÉCHAPPEMENT NE SE DEVINE PAS DANS UN HEREDOC INTERPOLÉ.** `<<<'JS'` (avec quotes) livre le texte tel quel ; `<<<JS` (sans quotes) fait lire à PHP les
  séquences d'échappement, si bien qu'un `\n` destiné à une chaîne JavaScript devient un **vrai saut de ligne** au milieu de cette chaîne : le script cesse de
  s'analyser, la page perd tout son comportement, et **rien ne le dit** — le bouton est là et ne fait rien. Un saut de ligne pour le JavaScript s'écrit `\\n`, et
  ce qui produit du script se contrôle en l'ouvrant, jamais en le relisant.
- **Un défaut de cette famille se paie en outil, pas en vigilance.** Il ne se voit pas : aucun relecteur ne peut l'attraper à l'œil, puisqu'il n'y a rien à voir. À chaque fois qu'on en trouve un,
  on se demande quel contrôle mécanique l'aurait vu, et on l'écrit — c'est ainsi que sont nés `check-page-selectors.php` et `diff-prompts.sh`.

## L'outillage

- **Le bloc « Usage » et « Intention » en tête de tout script est monté à la méthode commune** (`~/projects/conceptions/methode/execution.md`), le 2026-08-11 : il ne doit rien à GateBeast.
- **LE LANGAGE DE L'OUTILLAGE EST PHP, ET AUCUN FICHIER PYTHON NEUF NE S'AJOUTE** (opérateur, 2026-08-12). La règle générale — un langage par défaut, un autre admis là où il apporte ce qui n'existe
  que là — est montée à la méthode commune (`execution.md`) ; ce dépôt ferme ici la seconde moitié : **il n'y a plus de langage de second choix, et une intention qui justifie le Python ne l'autorise
  plus**. Une justification documente un choix déjà admis, elle n'en ouvre pas un neuf — c'est le jour même où l'interdit a été donné qu'un contrôle est né en Python, dûment justifié en tête, et
  c'était une faute.
- **CE QUI EST INTERDIT, C'EST D'AJOUTER, JAMAIS DE GARDER.** Le Python déjà là reste et **ne se réécrit pas** : « aucun remplacement brut n'est jamais prévu » (méthode) — réécrire ce qui marche perd
  les correctifs que ses allers-retours ont payés et n'achète rien. Le Python **décroît, il ne croît pas** : un fichier supprimé ne se signale même pas.
- **ET C'EST UNE MACHINE QUI LE TIENT, PAS LA BONNE VOLONTÉ DES AGENTS** : `php scripts/check-no-new-python.php` refuse tout `.py` versionné absent du relevé `scripts/python-inventory.json`, lui-même
  produit du dépôt et jamais tenu à la main. **Le refiger — `--freeze` — est un geste que l'opérateur autorise**, jamais une commodité qu'on s'accorde pour faire passer son propre ajout : refigé sans
  décision derrière, le relevé ne garde plus rien. Ses essais : `php scripts/dev/trial-no-new-python.php`.
- **La liste des outils validés de ce dépôt** — Python pour l'outillage, PHP pour l'enveloppe du générateur, Codex comme générateur d'images, `rsvg-convert` pour regarder un SVG produit — est tenue
  à [doc/outils-exterieurs.md](outils-exterieurs.md), à lire là plutôt qu'à recopier ici. Elle vivait dans `SUIVI.md`, et l'élagage du 2026-08-11 a rendu ce renvoi mort avant qu'on le corrige.
  **La règle qui dit qu'un outil non validé se demande au lieu de s'essayer** est montée à la méthode commune, avec l'interdit d'aller chercher hors du dépôt.
- **UNE VALEUR OBSOLÈTE NE S'ÉCRIT JAMAIS DANS DU CODE NEUF — ET EN AVOIR BESOIN, C'EST LE MOMENT DE LA CHANGER PARTOUT.** Règle de l'opérateur, 2026-08-08. Un nom ou une valeur qu'on sait fautif
  n'est toléré que dans **l'existant qu'on ne touche pas** : dès qu'on ajoute ou qu'on modifie du code qui s'en sert, on le corrige **dans tout le dépôt**, données et lecteurs dans le même geste.
  **Il est strictement interdit d'écrire une ligne neuve avec la valeur fautive**, même pour « rester cohérent avec ce qui l'entoure » — c'est exactement ainsi qu'une faute devient le standard du
  projet. Le besoin est le signal : si la valeur ressert, sa migration est due, et elle ne se met pas en pile pour plus tard.
- **UN COMMENTAIRE DE CODE EST EN ANGLAIS AMÉRICAIN, PARTOUT — pas seulement sous `scripts/`.** `review-server/` est du code au même titre, et un commentaire y est
  du code qui explique le code. La règle vaut pour tout ce qu'un développeur lit : commentaires, blocs d'usage et d'intention, noms. **Seuls les textes destinés à
  l'opérateur restent en français** — messages affichés, libellés, descriptions, et les citations de sa parole, qui se rapportent mot pour mot. L'existant qu'on ne
  touche pas est toléré ; ce qu'on écrit ou modifie, jamais (opérateur, 2026-08-08).
- **Les clés des fichiers de données sont en anglais** — règle montée à la méthode commune le 2026-08-12, sous « Tout le code est en anglais ». Reste propre à ce dépôt : l'anglais est **américain**,
  comme partout ailleurs (`doc/glossaire.md`), et les textes qui restent en français comprennent **les consignes de génération**.

## La production d'images

- **Le générateur d'images est l'agent Codex, enveloppé par `scripts/generate-image.php`** (versionné avec le projet). Personne ne l'appelle directement : un seul outil commande un sprite de bout en
  bout ([chaîne de production](doc/conception/referentiels/visuel/assets/chaine-de-production.md)).
- **Trois barrières séparent le générateur d'images des règles du dépôt, et elles se couvrent l'une l'autre.** `AGENTS.md` ne porte plus aucune règle et se contente d'orienter, en
  lui disant explicitement que rien d'ici ne le concerne ; son enveloppe coupe la lecture automatique des instructions du dépôt, à l'appel ; et la consigne qu'il reçoit le lui redit en toutes lettres.
  Constaté le 2026-08-06 : deux
  générations ont répondu « mode lot : cette génération nécessite votre validation » au lieu de dessiner, parce que la règle des modes venait d'être écrite dans le fichier qu'il chargeait. Ce qui doit
  parvenir au rôle `illustrator` s'écrit **dans sa consigne**, jamais dans un document du dépôt.
- **Une seule génération par version, aucune relance sans accord** — sauf la reprise unique prévue par la chaîne de production des assets
  ([chaîne de production](doc/conception/referentiels/visuel/assets/chaine-de-production.md)), qui ne vaut que pour elle.
- **Toute sprite générée est inscrite à son sujet et l'artefact de suivi est republié — sans exception** ([chaîne de production](doc/conception/referentiels/visuel/assets/chaine-de-production.md)).
  Une image qui existe sans être inscrite n'existe pour personne : elle n'apparaît nulle part, personne ne peut la juger, et elle se refait.

## L'écriture et les libellés

- **QUAND UN MOT EST AMBIGU, PLUS AUCUNE PAGE NE LE PORTE — PAS MÊME CELLE QUI L'EMPLOIE À BON DROIT** (opérateur, 2026-08-12 : « quand y'a ambiguïté, tu ne dois nommer AUCUNE page avec le terme
  ambigu, c'est le seul moyen d'éviter ça »). Renommer une seule des deux ne suffit pas : celui qui lit garde le mot en tête et retourne sur l'autre. **Payé le 2026-08-12** — « sujet » nommait à la
  fois les points du projet et les choses du monde, l'opérateur a cherché des boutons de vote sur la page des points, et il a fallu trois allers-retours pour découvrir qu'on ne parlait pas de la même
  page. Le mot ambigu se retire des **deux** noms, et chacune prend un nom qui ne se confond avec rien.
- **Tout libellé et tout titre affiché commence par une majuscule** — « Vue principale », jamais « vue principale ». Une seule majuscule, celle du début : elle ne se répète pas à chaque mot. Les codes
  et les adresses techniques gardent leur casse exacte, celle des fichiers (`OB-010`, `cutout/cloture/...`), aucune majuscule ajoutée. Une interface où la casse varie d'un libellé à l'autre donne
  l'impression que personne ne l'a relue — c'est le genre de détail qui se corrige une fois par page tant que la règle n'existe pas.
- **TOUTE PAGE PORTE UN TITRE, UNE FAVICON, ET DIT SON CHEMIN D'ACCÈS JUSQU'À L'INDEX** (opérateur, 2026-08-17 : « toute page référence son arbo d'accès et
  chaque page est accessible par l'index »). **L'arborescence a deux niveaux au plus pour l'instant, l'index étant le premier**, et chaque page est joignable
  depuis lui. Une page servie qui n'affiche ni son nom ni d'où elle vient ne s'atteint que par son adresse : on y arrive par un lien, on ne sait plus remonter,
  et elle finit oubliée — c'est ce qui est arrivé à `/workshop`, servie et absente de tout index. **Un onglet sans titre ni favicon ne se retrouve pas non plus**
  quand cinq pages de revue sont ouvertes côte à côte.
- **UNE SPRITE MONTRÉE PAR UN OUTIL PORTE TOUJOURS SON QUADRILLAGE DE CASES, ET LA MAQUETTE EST LA SEULE EXCEPTION** (opérateur, 2026-08-17 : « on doit voir les
  cases représentées. ça doit toujours être le cas sur les outils, hors maquette »). Sans lui, une image se juge dans le vide : rien ne dit ce qu'elle occupe au
  sol, ce que son volume déborde, ni où tombent ses axes. La maquette échappe à la règle parce qu'on y regarde la sprite **dans** une scène au lieu de la
  mesurer. **Rien ne se redessine pour cela** : `review-server/lib/FootprintGrid.php` porte le pavage, le balisage et la réserve, `footprint-grid.css` son
  style, et toute page qui montre une sprite les appelle — **et un outil se corrige pour s'y conformer** (même relevé : « les outils doivent pouvoir être
  amélioré s'il faut »).
- **ON PARLE EN CASES, JAMAIS EN PIXELS** (opérateur, 2026-08-10). Toute mesure adressée à l'opérateur — message, question, compte rendu, libellé de page — se dit dans l'unité du jeu : « une case et
  demie », pas « 132 px ». Le pixel reste ce que le code calcule et ce que l'échelle fait foi ; il n'est pas ce dont on parle. Un chiffre en pixels oblige son lecteur à refaire la division pour savoir
  de quoi il s'agit, et deux hauteurs comparées en pixels ne se comparent plus dès que la finesse du maître change.
- **Tout rapport destiné à être lu est en Markdown** — règle montée à la méthode commune le 2026-08-12 (`execution.md`), sans rien qui reste propre à ce dépôt.

## Le versionnage et la publication

- **Aucune écriture d'historique sans ordre explicite** — règle montée à la méthode commune le 2026-08-12 (`execution.md`), avec l'interdit de toute ligne `Co-Authored-By` nommant l'agent. Reste
  propre à ce dépôt : **le distant est `git@github.com:Cartman34/gatebeast.git`** (`origin`, branche `main`).
- **Publication** : les revues sont des artefacts Claude republiés à adresse stable (le paramètre `url` de l'outil Artifact conserve le lien). **Les adresses vivent dans le registre
  `review-server/artefacts.json`, et ses règles dans [doc/artefacts.md](artefacts.md)** — plus jamais dans `SUIVI.md`, qui se réécrit sans cesse et n'a rien à faire en source de données. Cette ligne
  y renvoyait encore ; corrigé le 2026-08-11 en auditant le journal des séances.
- **AVANT TOUTE PUBLICATION, ON LISTE LES ARTEFACTS EXISTANTS**, sans exception : l'inventaire du suivi ne suffit pas, il peut être incomplet. Publier sans lister a créé le 2026-08-06 une adresse
  neuve pour une page qui en avait déjà une — **et les remarques que l'opérateur y avait posées ont été perdues avec l'ancienne page**, puisqu'elles vivent dans le navigateur, attachées à l'adresse
  qui les a reçues. **Un doublon se supprime, et c'est l'opérateur qui le fait**, depuis le menu de l'artefact ; l'agent, lui, ne peut que republier par-dessus. En attendant, il y republie un avis
  disant que la page est un doublon et où vit le bon artefact, et l'inscrit à l'inventaire comme « à ne pas rouvrir » — une adresse laissée avec son ancien contenu finit par être reprise pour la
  bonne. Une fois la suppression faite, la ligne et l'avis disparaissent à leur tour.
- **Une page, une adresse, et une adresse par sujet** — le plan de composition et la maquette montée sont deux sujets, donc deux adresses ; d'autres maquettes viendront, chacune avec la sienne.

## La méthode commune

Méthode de travail commune : `~/projects/conceptions/methode/` — conception descendante, collaboration avec l'opérateur, principes d'exécution. Elle vaut au-delà de GateBeast et prime sur
les habitudes d'un agent, exactement comme ce document.
