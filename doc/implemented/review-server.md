# Le serveur de revue

**Usage :** savoir ce que le serveur local sert, ce qui construit chaque page, et où vivent les choses que plusieurs pages partagent.

**Intention :** que montrer un état ne coûte plus une publication. Les comptes rendus en conversation ne tiennent pas dès que la matière devient visuelle, et un
artefact publié doit être republié à chaque changement. Une page servie en local se reconstruit d'une commande et garde son adresse.

**Ne couvre pas** ce qu'on met sur ces pages ([conception](../conception/vision.md)), ni les revues publiées à adresse stable ([artefacts](../artefacts.md)).

## Le service

**`php review-server/serve.php` DÉMARRE, `php scripts/stop-review-server.php` ARRÊTE.** Le port est une configuration du projet — `review-server/config.json`,
lu par `Config.php` et rendu par `ReviewServer.php` — pour qu'il change à un seul endroit.

**`router.php` AIGUILLE, `pages.php` DÉCLARE.** Chaque page a une **route courte** qui ne dépend pas du nom du fichier qui la porte, si bien qu'une page se
renomme ou se scinde sans que l'adresse bouge — c'est tout l'intérêt de servir plutôt que de publier. `pages.php` porte, pour chaque page, sa route, son titre,
le fichier produit **et la commande exacte qui le produit**, parce que cette commande n'était écrite nulle part. `index.php` en fait la page d'accueil et
`url.php` fabrique les adresses.

## Les pages servies

| Route | Ce qu'elle montre | Constructeur |
|---|---|---|
| `/backlog` | les points ouverts par priorité | `review-server/backlog/build.php` |
| `/inventory` | ce qu'un sujet EST | `review-server/inventory/build.php` |
| `/sprites` | où en sont les images d'un sujet, variant par variant | `review-server/suivi-sprites/build.php` |
| `/workshop` | une chaîne de versions de consigne, ses images et ses mesures | `review-server/workshop/build.php` |
| `/maquette-campagne` | le plan de composition et la maquette montée, sur une page | `review-server/parc/build.php`, `review-server/parc/monter.php`, puis `review-server/maquette-campagne/build.php` |

**L'INVENTAIRE ET LA PAGE DES SPRITES SONT DEUX PAGES PARCE QUE CE SONT DEUX QUESTIONS** — ce qu'un sujet est, et où en sont ses images. **`/parc` et
`/parc/maquette` sont archivées** depuis le 2026-08-07 : leurs constructeurs restent, puisque la page Campagne est produite par eux.

## Les briques partagées

**ELLES EXISTENT PARCE QUE LA RÉPÉTITION EST LA FAUTE.** Chaque fois qu'une même chose a été écrite deux fois, les deux copies ont divergé — c'est ce constat,
et pas l'élégance, qui a fait sortir chacune de ces briques.

| Brique | Ce qu'elle tient |
|---|---|
| `Config.php` | un seul lecteur du fichier de configuration |
| `ReviewServer.php` | le port et l'adresse du service |
| `Faults.php` | **une seule façon d'échouer**, et un seul endroit qui l'affiche |
| `Layout.php`, `Theme.php`, `Favicon.php` | un format d'écran, un jeu de variables de couleur, une icône — les mêmes sur toutes les pages |
| `Reload.php` | une page servie se recharge quand elle est reconstruite |
| `Browser.php` | ouvrir une page dans le navigateur de l'opérateur |
| `Backlog.php` | lire et écrire les points, et **calculer le prochain numéro de chaque série** |
| `Inventory.php` | lire `assets/subjects.json` |
| `Notes.php`, `Remarks.php`, `Survey.php` | les remarques de l'opérateur, versionnées dans le dépôt et non dans son navigateur |
| `Critiques.php` | une critique, qui n'est pas une note en marge |
| `Prompts.php` | **tous les chemins de la chaîne de consignes**, calculés à un seul endroit |
| `PromptParts.php` | quel niveau a écrit chaque phrase d'une consigne |
| `PromptDiff.php`, `WordDiff.php` | ce qui change d'une version de consigne à la suivante, mot à mot |
| `TransmittedNumbers.php` | ce que la transmission a perdu, mesuré sur les **nombres** et non sur les mots |
| `SpriteMeasures.php` | les deux égalités du socle, qui ne se tranchent qu'à la mesure |
| `FootprintGrid.php` | la même grille d'emprise sur les deux pages qui montrent une sprite |
| `Thumbnail.php` | une image du disque rendue portable par une page |
| `Rune.php` | applique le référentiel des runes, ne décide rien |
| `Trials.php` | un essai n'est pas un livrable |
| `Probe.php` | une sonde regarde la page **servie**, jamais sa copie sur le disque |

**`Probe.php` MÉRITE SON EXPLICATION** : une sonde qui ouvre le fichier plutôt que la page rend compte de quelque chose que personne ne voit. Et une sonde
n'écrit jamais dans les données de l'opérateur — deux l'ont fait, et elles prennent désormais une empreinte qu'elles restaurent.
