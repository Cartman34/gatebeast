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
- **Ce qu'on vient d'écrire se contrôle avant d'être montré** : `php scripts/check-text-width.php <fichiers>` sur tout fichier touché. La vigilance seule ne tient pas — le pli d'origine d'un agent
  revient dès qu'il ne le contrôle pas explicitement, et c'est au contrôle mécanique de l'arrêter, pas à sa mémoire.
- **200 caractères par ligne, et c'est le SEUL standard de longueur du projet — impératif.** Il **remplace et annule tous les autres**, sans exception et quelle que soit leur provenance.
  **Les exemples qui suivent ne forment PAS une liste fermée** — ils illustrent, ils ne délimitent pas : les 79 de PEP 8, les 88 d'un formateur Python, les 120 d'un style PHP, les 80 d'un usage
  Markdown, les 72 d'un message de commit, et toute habitude d'agent. Tout autre standard de longueur, nommé ici ou non, tombe de la même façon. Un agent qui replie son
  texte plus court applique un standard qu'il s'est apporté lui-même : c'est cette substitution qui est interdite, pas seulement le dépassement.
- **Le plafond de 200 vaut partout, et TOUT texte cherche à l'atteindre.** « Tout » se prend au pied de la lettre : **tout fichier texte du projet, quel qu'il soit**, et ce qui suit n'en est qu'un
  échantillon, jamais la liste complète — documents, `SUIVI.md`, descriptions, notes, **commentaires et documentation embarquée dans le code**, **messages de commit**, **le texte que le code porte et
  produit, soit toute chaîne de caractères écrite dans un fichier de code : message de faute, message d'avancement, libellé, fragment de consigne assemblé**, consignes de génération, fichiers de
  configuration, scripts. Un support absent de cette énumération suit la même règle : aucun n'a de règle à lui. Seules les **instructions** — le code exécutable lui-même — n'ont rien à remplir : elles
  restent aussi courtes que la lisibilité le demande, avec pour seule obligation de ne pas franchir le plafond.
- **Une ligne repliée à quatre-vingts caractères double le nombre de lignes sans rien ajouter** et rallonge chaque relecture ; un texte replié court se rediffe entièrement au premier mot changé.
  Ce qui est déjà écrit ne se reprend pas pour cette seule raison ; ce qui s'écrit maintenant respecte la convention.

## Les modes de travail et la conduite

- **Deux modes de travail, et l'opérateur seul les fixe.** Un **mode** dit qui décide de l'avancée entre deux gestes de l'agent — lui-même, ou l'opérateur.
  - **Dépilement continu** — l'agent prend la pile du `SUIVI.md` dans son ordre et traite les sujets les uns après les autres sans rien demander. Il ne s'arrête que si le sujet porte une question, un
    inconnu, une incohérence, ou s'il veut proposer quelque chose ; sinon il fait, et il rend compte quand c'est fini. C'est le mode **par défaut**.
  - **Lot** — l'agent n'exécute rien avant d'avoir annoncé ce qu'il compte faire et reçu la validation de l'opérateur. Ce qui remonte remonte groupé, jamais sujet par sujet, et l'opérateur tranche en
    bloc. Y vont sans qu'il ait à le redire : toute proposition, toute génération d'image, tout verdict à demander.
- **Le mode s'annonce avant de commencer, et l'agent s'arrête sur cette annonce** — à commencer par son démarrage, où c'est le mode par défaut qui s'applique et où il doit donc l'annoncer comme les
  autres : l'opérateur confirme, et l'agent part. Une annonce sans arrêt ne sert à rien, elle passe dans le flux et l'opérateur découvre le mode au résultat.
- **`GO` et `STOP` sont les deux seuls mots qui lancent et arrêtent le dépilement, et ils sont stricts.** Rien d'autre ne vaut reprise : aucune phrase ne s'interprète comme un feu vert, et le silence
  encore moins. **Tout arrêt met fin au `GO`** — une question de l'opérateur, un ordre ponctuel, une interruption : dès que l'agent s'arrête, l'autorisation est consommée et ne se reprend pas d'elle-
  même une fois la parenthèse refermée. Il en faut une neuve, donnée explicitement.
- **UN `GO` OU UN `STOP` ENVOYÉ PENDANT QUE L'AGENT TRAVAILLE VAUT COMME ORDRE, MAIS N'ARME NI NE DÉSARME RIEN.** `UserPromptSubmit` ne se déclenche que sur un message qui **ouvre** un tour :
  un message glissé en cours de tour est bien reçu et bien lu par l'agent, mais aucun hook ne le voit. Mesuré le 2026-08-08 — deux `GO` en cours de tour n'ont rien armé, le même `GO` en ouverture de
  tour a armé dans la seconde. **L'agent obéit à l'ordre, dit que l'état ne le reflète pas, et n'y touche pas** ; à l'opérateur de renvoyer le mot en ouverture de tour s'il veut la garde armée.
- **L'ÉTAT D'ARMEMENT DU DÉPILEMENT N'APPARTIENT PAS À L'AGENT, ET IL N'A JAMAIS À Y TOUCHER — NI POUR L'EFFACER, NI POUR L'ÉCRIRE.** `var/hooks/dequeue-armed` est écrit par le hook du prompt, et par
  lui seul : le `GO` de l'opérateur l'arme, son `STOP` le désarme, il expire seul au bout de trois heures. Une garde qu'on peut retirer soi-même n'est pas une garde, et un armement qu'on peut écrire
  soi-même est un ordre qu'on se donne à la place de l'opérateur. **Les deux gestes ont été faits le 2026-08-08**, et chacun tenait à une confusion que voici levée :
  - **La règle d'arrêt ci-dessus est une règle de conduite, elle ne décrit pas un fichier.** « Tout arrêt met fin au `GO` » dit à l'agent de ne pas repartir de lui-même. Elle ne lui demande pas de
    mettre l'état à jour pour le refléter — c'est cette lecture qui a fait supprimer le fichier, en croyant bien faire.
  - **Un hook qui n'arme pas est un défaut à constater, pas à compenser.** Il s'inscrit à la pile avec ce qui a été observé. Le suppléer à la main donne une page qui a l'air juste et une garde qui ne
    garde rien — soit exactement l'inconvénient qu'on croyait corriger, en pire, puisqu'il ne se voit plus.
  - **L'empêchement est mécanique, pas moral** : `scripts/hook-guard-dequeue.sh`, déclaré en `PreToolUse`, refuse toute commande et toute écriture qui touche à cet état ou à la garde elle-même. La
    lecture reste libre — l'agent doit pouvoir dire si le dépilement est armé. Ses essais : `bash local/scripts/essai-garde-depilement.sh`.
  - **`.claude/settings.json` n'est PAS dans la liste des fichiers gardés, et c'est délibéré** (opérateur, 2026-08-08). Débrancher la garde en modifiant le fichier qui la déclare serait le chemin de
    contournement évident, mais toute modification de ce fichier demande systématiquement l'autorisation de l'opérateur : la barrière existe déjà, en amont, et elle est humaine. L'y ajouter
    coûterait plus qu'elle ne protège — l'agent ne pourrait plus déclarer aucun hook sans passer par l'opérateur. **Ne pas le reproposer.**
- **Tant que le dépilement n'est pas lancé, l'agent ne modifie que le `SUIVI.md`** — aucun autre fichier, quelle qu'en soit l'évidence. Ce qui survient avant le `GO` entre dans la pile et y attend.
- **Le suivi est le support de l'agent** : il l'écrit quand il veut, sans demander, et il doit permettre à tout moment d'être coupé et relancé de zéro **sans aucune perte**. Ce qui n'y est pas écrit
  n'existe pas.
- **MAIS UN SUJET NEUF SE FAIT VALIDER — L'AGENT N'EN OUVRE PAS DE LUI-MÊME** (opérateur, 2026-08-08). Tenir le suivi et décider de ce sur quoi le projet travaille sont deux choses : l'agent écrit,
  met à jour, décrit et ferme librement, et il ajoute sans demander **ce que l'opérateur lui dit d'ajouter**. Ouvrir un sujet que personne n'a demandé, non : « tu risques de t'enfoncer dans une
  mauvaise pratique sans vérification ». Un point ouvert oriente le travail de toutes les séances suivantes, et un agent qui remplit lui-même sa propre pile finit par travailler sur ce qu'il a décidé
  seul, en croyant suivre le projet.
- **LES PRIORITÉS 1 À 10 SONT RÉSERVÉES À L'OPÉRATEUR** (2026-08-08). Elles disent ce qui est urgent, important ou de grande priorité **selon lui**, et lui seul les attribue. Ce que l'agent propose
  ou ouvre commence à **11** : sans cette réserve, ce qu'il juge pressant se mélange à ce que l'opérateur juge pressant, et la tête de pile cesse de dire la volonté de quelqu'un.
- **CE QUI SE FAIT À LA PLACE : on le fait, ou on le propose.** Un défaut trouvé en chemin se corrige dans la foulée — c'est déjà la règle, « ce qui manque se fait ». Ce qui est trop gros pour être
  fait dans la foulée se **propose** à l'opérateur, avec ce qu'il coûte, et n'entre à la pile qu'une fois validé. Un défaut qu'on ne peut ni faire ni proposer tout de suite se dit dans le compte
  rendu, il ne s'inscrit pas de force.
- **Tout point ouvert porte un code et un numéro**, pour que l'opérateur réponde par lui seul : **Q** une question, **P** une proposition, **S** un sujet, **T** un test, **W** une alerte. Les séries
  sont indépendantes, continues tant qu'un point reste ouvert, et repartent à 1 quand la série se vide. Un point ouvert vit dans le suivi, jamais dans la conversation.
- **CE QUI VIT DANS LE SUIVI, C'EST LE POINT — PAS LA QUESTION. UNE QUESTION SE POSE EN ENTIER, DANS LE MESSAGE.** Le code sert à répondre, il ne remplace pas ce qu'on demande : posée, une question
  dit **ce qui est demandé**, **les options** quand il y en a, **ce qui dépend de la réponse** et **ce que l'agent recommande**. Ce qu'elle n'a pas à redire, c'est l'analyse — elle reste au point, et
  `show <REF>` l'ouvre. Énumérer des libellés numérotés n'est pas poser des questions : un titre nomme un sujet, il n'appelle pas de réponse, et l'opérateur ne peut que demander à l'ouvrir — un
  aller-retour de plus pour chaque point, ce que la numérotation existait justement pour éviter (constaté le 2026-08-08). Le format « code et trois mots » ne vaut que pour les **deux lignes de
  récapitulatif** ; l'appliquer au corps du message revient à n'avoir rien demandé.
- **Chaque message se termine par deux lignes de récapitulatif** : ce qui attend l'opérateur, ce qui attend l'agent. Code et trois mots par point, quatre points par ligne au plus, un compteur au-delà.
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
- **Un défaut de cette famille se paie en outil, pas en vigilance.** Il ne se voit pas : aucun relecteur ne peut l'attraper à l'œil, puisqu'il n'y a rien à voir. À chaque fois qu'on en trouve un,
  on se demande quel contrôle mécanique l'aurait vu, et on l'écrit — c'est ainsi que sont nés `check-page-selectors.php` et `diff-prompts.sh`.

## L'outillage

- **Tout script s'ouvre par un bloc de commentaire « Usage » et « Intention », en anglais** — quel que soit son langage, PHP, Python, shell, JavaScript ou autre. L'**usage** dit à quoi il sert et
  comment on l'appelle ; l'**intention** dit pourquoi il existe et pourquoi il fait ainsi plutôt qu'autrement. Un script Python ajoute à son intention **pourquoi il est en Python et non en PHP** : la
  bibliothèque ou l'outil qui n'existe que là, nommé. Sans cette phrase, le choix se relit comme une habitude et se reproduit sans raison.
- **PHP est le langage par défaut de l'outillage pérenne**, et la transition y va progressivement. Tout script durable neuf s'écrit en PHP. Python reste admis là où il apporte une bibliothèque ou un
  outil qui n'existe qu'en Python — mesure d'image, traitement de matrice —, et ce choix se justifie en tête du fichier. **Aucun remplacement brut n'est prévu** : ce qui tourne en Python et fait son
  travail y reste jusqu'à ce qu'une raison propre le fasse bouger ; réécrire pour réécrire est proscrit.
- **Un outil non validé se demande, il ne s'essaie pas.** Le projet a une liste d'outils validés — Python pour l'outillage, PHP pour l'enveloppe du générateur, Codex comme générateur d'images,
  `rsvg-convert` pour regarder un SVG produit (liste tenue à jour au tableau « Outils extérieurs et versions constatées » de `SUIVI.md`, à lire là plutôt qu'à recopier ici). Aucun autre langage, outil
  ou bibliothèque ne s'emploie sans l'accord de l'opérateur : un agent qui pense en avoir besoin **exprime le besoin et attend**, il n'essaie pas « juste pour voir ». Chaque outil introduit
  devient une dépendance que quelqu'un devra installer, comprendre et maintenir, sur toutes les machines où le projet tourne — ça ne se décide pas au détour d'un dépannage.
- **UNE VALEUR OBSOLÈTE NE S'ÉCRIT JAMAIS DANS DU CODE NEUF — ET EN AVOIR BESOIN, C'EST LE MOMENT DE LA CHANGER PARTOUT.** Règle de l'opérateur, 2026-08-08. Un nom ou une valeur qu'on sait fautif
  n'est toléré que dans **l'existant qu'on ne touche pas** : dès qu'on ajoute ou qu'on modifie du code qui s'en sert, on le corrige **dans tout le dépôt**, données et lecteurs dans le même geste.
  **Il est strictement interdit d'écrire une ligne neuve avec la valeur fautive**, même pour « rester cohérent avec ce qui l'entoure » — c'est exactement ainsi qu'une faute devient le standard du
  projet. Le besoin est le signal : si la valeur ressert, sa migration est due, et elle ne se met pas en pile pour plus tard.
- **UN COMMENTAIRE DE CODE EST EN ANGLAIS AMÉRICAIN, PARTOUT — pas seulement sous `scripts/`.** `review-server/` est du code au même titre, et un commentaire y est
  du code qui explique le code. La règle vaut pour tout ce qu'un développeur lit : commentaires, blocs d'usage et d'intention, noms. **Seuls les textes destinés à
  l'opérateur restent en français** — messages affichés, libellés, descriptions, et les citations de sa parole, qui se rapportent mot pour mot. L'existant qu'on ne
  touche pas est toléré ; ce qu'on écrit ou modifie, jamais (opérateur, 2026-08-08).
- **Les clés des fichiers de données sont en anglais**, au même titre que le code — ce sont les mêmes noms que le code manipule. Une clé française oblige tout lecteur à mélanger les deux langues dans
  la même expression, et le mélange se propage par imitation au fichier suivant. Ne vaut que pour les clés : valeurs et textes destinés à l'opérateur — consignes de génération comprises — restent en
  français. Anglais américain, comme partout ailleurs (`doc/glossaire.md`).

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

- **Tout libellé et tout titre affiché commence par une majuscule** — « Vue principale », jamais « vue principale ». Une seule majuscule, celle du début : elle ne se répète pas à chaque mot. Les codes
  et les adresses techniques gardent leur casse exacte, celle des fichiers (`OB-010`, `cutout/cloture/...`), aucune majuscule ajoutée. Une interface où la casse varie d'un libellé à l'autre donne
  l'impression que personne ne l'a relue — c'est le genre de détail qui se corrige une fois par page tant que la règle n'existe pas.
- **Tout rapport destiné à être lu est en Markdown — règle générale.** Un rapport se relit, se cite, se colle dans une conversation et s'affiche dans une page : le Markdown lui donne titres, tableaux
  et blocs de code sans rien coûter, là où le texte brut oblige chaque lecteur à refaire la mise en forme dans sa tête. Ne vaut que pour ce qui se lit : ce qui se relit par machine — évaluations,
  mesures, catalogues — reste du JSON, et les deux coexistent plutôt que l'un n'imite l'autre.

## Le versionnage et la publication

- **Git : aucune écriture d'historique sans ordre explicite de l'opérateur** — `commit`, `commit --amend` et `push` compris. L'agent exécute lui-même les commandes git, mais seulement une fois l'ordre
  donné ; les commits restent occasionnels, pas un par étape. Dépôt distant : `git@github.com:Cartman34/gatebeast.git` (`origin`, branche `main`). **Jamais de ligne `Co-Authored-By` nommant Claude ou
  Anthropic** : l'opérateur est l'unique auteur de ses commits.
- **Publication** : les revues sont des artefacts Claude republiés à adresse stable (le paramètre `url` de l'outil Artifact conserve le lien). Les adresses en cours sont listées dans `SUIVI.md`.
- **AVANT TOUTE PUBLICATION, ON LISTE LES ARTEFACTS EXISTANTS**, sans exception : l'inventaire du suivi ne suffit pas, il peut être incomplet. Publier sans lister a créé le 2026-08-06 une adresse
  neuve pour une page qui en avait déjà une — **et les remarques que l'opérateur y avait posées ont été perdues avec l'ancienne page**, puisqu'elles vivent dans le navigateur, attachées à l'adresse
  qui les a reçues. **Un doublon se supprime, et c'est l'opérateur qui le fait**, depuis le menu de l'artefact ; l'agent, lui, ne peut que republier par-dessus. En attendant, il y republie un avis
  disant que la page est un doublon et où vit le bon artefact, et l'inscrit à l'inventaire comme « à ne pas rouvrir » — une adresse laissée avec son ancien contenu finit par être reprise pour la
  bonne. Une fois la suppression faite, la ligne et l'avis disparaissent à leur tour.
- **Une page, une adresse, et une adresse par sujet** — le plan de composition et la maquette montée sont deux sujets, donc deux adresses ; d'autres maquettes viendront, chacune avec la sienne.

## La méthode commune

Méthode de travail commune : `~/projects/conceptions/methode/` — conception descendante, collaboration avec l'opérateur, principes d'exécution. Elle vaut au-delà de GateBeast et prime sur
les habitudes d'un agent, exactement comme ce document.
