# Suivi des travaux — GateBeast

**Intention :** permettre à n'importe quel intervenant de reprendre le travail sans perte. Ce document dit **où on en est**, pas ce que le jeu doit être — la cible vit dans la conception, le
découpage en versions dans le [plan d'action](PLAN-ACTION.md).

Il se met à jour à chaque étape franchie. Il ne conserve pas d'historique : seul l'état courant compte (le versionnage garde le reste).

## L'ÉTAT COURANT — ce document ne contient que ça, et c'est délibéré

**CHAQUE DÉCISION VIT À SON FOYER, UNE SEULE FOIS**, et ce document y renvoie au lieu de la recopier : les règles de conduite aux [règles du dépôt](doc/regles-du-depot.md) et à la méthode commune,
la cible à `doc/conception/`, les mots au [glossaire](doc/glossaire.md), et tout ce qui concerne un point dans **sa description** — `php scripts/backlog.php show <REF>`. Élagué le 2026-08-11 : le
document empilait une section par séance, ce que sa propre première ligne interdit. **Ce qui en a été retiré n'est pas dans un diff, il est dans
[doc/journal-des-seances.md](doc/journal-des-seances.md)** — versionné, citable, et qui ne dit que le pourquoi des décisions passées, jamais l'état courant.

### Comment on démarre

**LA SESSION S'OUVRE DEPUIS `~/projects/gatebeast`, ET C'EST IMPÉRATIF** — pas depuis le dossier parent, sans quoi les hooks déclarés dans `.claude/settings.json` ne se chargent pas, le `GO` n'arme
rien et la fin de tour n'est jamais refusée.

**Le prompt de reprise, à donner tel quel à une session neuve :**

> Travaille dans ~/projects/gatebeast. Lis AGENTS.md, puis doc/regles-du-depot.md en entier, puis la première section de SUIVI.md — elle contient tout le reste. Mode dépilement continu, annonce-le
> et arrête-toi.

**LA REVUE SE REGARDE EN LOCAL** : `php review-server/serve.php`, puis `http://localhost:8080/`. Quatre pages — l'Index, le suivi des sujets, le suivi des sprites, la Maquette Campagne. Une page se
reconstruit par sa route : `php review-server/build.php /sprites`. **Ce serveur ne survit pas à la séance.** Les remarques de l'opérateur sont dans `review-server/notes/`, lues directement.

**LES TÂCHES NE SONT PAS DANS CE DOCUMENT** : elles vivent dans `review-server/tasks.json`, et **une seule commande les lit et les écrit** : `php scripts/backlog.php`. `next` donne la première à
prendre, `list` les range — **les points `proposed` sortent à part, ils ne sont pas du travail en cours** —, `show <REF>` en ouvre un en entier, `add`, `set`, `describe`, `close` les modifient.
Toute écriture reconstruit la page `/sujets`. **Chaque point porte son analyse complète : `show` avant d'agir.**

### Les outils

**LES CONTRÔLES, à lancer après avoir touché à ce qu'ils gardent :**

- `php scripts/check-text-width.php <fichiers>` — le standard de 200 caractères. Dans un fichier de code, seuls les commentaires sont jugés.
- `php scripts/check-subjects-against-inventory.php` — emprise, couvert et hauteur de chaque sujet contre sa ligne d'inventaire, et **il crie sur ce qu'il n'arrive pas à lire** au lieu de le sauter.
- `php scripts/check-review-pages.php` — les quatorze comportements de la page des sprites, les sept de la page Campagne.
- `php scripts/check-page-selectors.php` — chaque sélecteur qu'un script cherche existe-t-il dans son balisage ? Un sélecteur qui ne trouve rien ne lève rien : le bouton ne fait simplement plus rien.
- `php scripts/check-asset-theme.php` — aucun nom de thème hors de son module, et la complétude rapportée.
- `python3 scripts/check-subjects.py` — le référentiel contre les fichiers réellement livrés.
- `python3 scripts/check-code-language.py [fichiers]` — le vocabulaire technique français dans les **noms de fichiers** et les valeurs comparées. Balaie aussi `local/scripts/`.
- `bash scripts/diff-prompts.sh` — réassemble les consignes et dit ce qui a bougé depuis la référence figée. Ne dessine rien. `--freeze` refige.

**LES ESSAIS DES HOOKS** : `bash local/scripts/essai-mot-ordre.sh` (la forme d'un ordre), `essai-hook-prompt.sh`, `essai-hook-stop.sh`, `essai-stop-transcrit.sh`, `test-stop-multiline.sh`.

**LES SONDES, pour regarder au lieu de supposer** : `tirer-page.php` (la page telle qu'elle s'ouvre), `probe-fsp.php`, `cliquer-bouton.php`, `console-page.php`, `probe-comparaison.php`,
`probe-fermeture.php`, `probe-debordement.php`, `montrer-queue-operation.php` (les messages glissés en cours de tour). **Une sonde s'ajoute en fin de fichier, jamais avant `</body>`** : la page
construite n'en porte pas, donc un `str_replace` dessus ne change rien et la sonde rapporte un essai propre sur une page qu'elle n'a jamais touchée.

**LES MESURES** : `python3 local/scripts/list-off-band-sprites.py` (les boîtes hors fourchette), `measure-ink-off-band.py` (la hauteur de l'encre, pas de la boîte).

### Ce qui est vrai du modèle, et qu'aucun fichier ne dit à lui seul

**LA FOURCHETTE DE HAUTEUR SE DÉCLARE AU VARIANT**, en `TY`, clés `height_min_ty` et `height_max_ty`. Aucune formule ne la produit — aucun script ne sait qu'une herbe est courte et qu'un chêne est
grand. **Une fourchette absente arrête la commande**, sans repli. Les 69 fourchettes en place sont des **amorces reprises de l'ancienne formule et restent à relire**, sauf les 31 pièces
d'assemblage, fixées à la main à `1 TY` sans jeu.

**DEUX UNITÉS, `TX` ET `TY`, ET AUCUNE MESURE SANS LA SIENNE.** Tout est à `doc/conception/referentiels/technique/rendu-en-calques.md`.

**LA TOILE SE PREND SUR LE COUVERT**, pas sur l'emprise, quand le sujet en déclare un.

**LES RÉSEAUX NE SE FONT PAS MAINTENANT** (opérateur, deux fois le 2026-08-10) — formes manquantes **comme** reprises de pièces livrées. Refaire une pièce de `CH-019`, `CH-020` ou `OB-010` est une
génération de réseau, quel qu'en soit le motif. **Ne pas les reproposer.**

**LE `STOP` GLISSÉ EN COURS DE TOUR EST LU** — entrées `queue-operation` du transcrit, par `hook-stop.php` à la fin du tour et par `php scripts/check-stop-order.php <transcript.jsonl>` à la demande.
Seul un `GO` maintient l'armement ; tout le reste vaut arrêt.

**LE HOOK DE BASE DE L'OPÉRATEUR EST BRANCHÉ** : `~/projects/local/hook/hook-pre-bash.sh`, en `PreToolUse` sur `Bash` seul. Il refuse les `;`, les `&&`, les `$(...)`, les redirections vers un
fichier, les chemins absolus dans le dépôt et le `sed -i`. **Sur `Write` ou `Edit` il enfermerait l'agent** — il lit leur charge comme une ligne de commande.

### Ce qui attend l'opérateur

- **Trois sprites à juger** : `TR-060-v7` (chêne), `TR-063-v12` (pommier), `CH-021_shape-ns-v4` (pont nord-sud).
- **`BT-002 p2`** — la version abîmée du centre de soin, à écarter ; c'est un verdict, pas un dessin.
- **Les 66 fourchettes amorcées**, à relire.
- **Neuf points `proposed`**, à valider ou à classer, et `Q12 stop-mi-tour`, caduque, à classer.
- **Huit cas rouges de `test-stop-multiline.sh`** : ils testent la lecture d'ordres retirée le 2026-08-09. Supprimer des cas d'essai est une décision, pas un nettoyage.
