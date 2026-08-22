# L'établi

**Usage :** savoir ce que `scripts/dev/` contient et ce qui l'en distingue. Rien ici ne produit de livrable : ce sont les **instruments** avec lesquels on
regarde, on mesure et on éprouve.

**Intention :** qu'un agent sans yeux puisse quand même constater. Une page servie ne se lit pas en ouvrant son fichier — la moitié de ce qu'elle montre est
calculée au chargement —, un SVG ne se regarde pas, et « je crois que ça marche » n'est pas un constat. Ces instruments transforment une impression en mesure.

**Ne couvre pas** ce que les instruments observent — la [chaîne de production](production-chain.md), le [serveur de revue](review-server.md) — ni les contrôles
et les hooks, qui sont des [gardes](guards.md) et non des instruments.

## Les essais

**`scripts/dev/trial-*` TIENT UN CONTRÔLE, ET SE LANCE APRÈS TOUTE REPRISE DE CELUI-CI.** Un essai n'est pas nommé une seconde fois dans cette documentation :
il appartient au contrôle qu'il tient, et le [nœud des gardes](guards.md) les nomme tous.

**LEURS CAS CASSÉS VIVENT DANS L'ESSAI, jamais sur les données du projet.** Un essai qui s'appuie sur `assets/subjects.json` devient vert le jour où le défaut
est corrigé — et cesse alors de prouver quoi que ce soit.

## Les sondes

**`scripts/dev/probe-*` OUVRE UNE PAGE SERVIE ET RAPPORTE CE QU'ELLE FAIT** : un bouton cliqué, un tiroir ouvert, un état lu, une capture prise. Une par
question, parce qu'une sonde qui répond à deux questions n'en instruit aucune.

**TROIS RÈGLES, ET CHACUNE A ÉTÉ PAYÉE :**

- **Une sonde regarde la page SERVIE, jamais sa copie sur le disque** — `review-server/lib/Probe.php` le tient. Une sonde qui ouvre le fichier rend compte de
  quelque chose que personne ne voit.
- **Une sonde n'écrit jamais dans les données de l'opérateur.** Deux l'ont fait — l'une a posé « validé » sur une tuile d'herbe, l'autre a laissé une remarque
  — et elles prennent désormais une empreinte du fichier qu'elles restaurent.
- **Une sonde est muselée** : ce qu'elle imprime est son rapport, pas le bavardage de la page.

## Les lecteurs

**`show-*`, `list-*`, `dump-*`, `find-*`, `measure-*`, `draw-*`, `crop-*` RÉPONDENT À UNE QUESTION ET N'ÉCRIVENT RIEN** dans le dépôt. Ils disent ce que le
référentiel déclare, ce qui reste à produire, ce qu'une image mesure réellement, ce qu'un transcrit contient. On les lance, on lit, on jette.

## Les instruments qui durent

| Instrument | Ce qu'il fait |
|---|---|
| `shoot-page.php` | capture une page de revue telle qu'elle s'ouvre — la seule façon pour un agent de la voir |
| `console-page.php` | ouvre une page construite et rend ce que sa console dit, y compris ses fautes |
| `click-bouton.php` | copie la page, clique un sélecteur, et rapporte ce qui a changé |
| `compare-images.php` | pose des images côte à côte pour qu'un écart se voie au lieu de se raconter |
| `trim-to-ceiling.php` | replie les lignes qui dépassent le plafond de largeur, de peu |
| `rename-asset-folders.php` | déplace des dossiers d'assets **et réécrit tous les chemins inscrits**, avec un `--dry-run` |
| `plan-script-renames.py` | liste les fichiers dont le NOM porte un mot français, avec le nom proposé |
| `promote-and-prune-tools.py` | déplace vers `scripts/` les outils qu'un document vivant promet, et retire ce qui n'existe plus |
| `drop-artifact.php` | écrit une copie du registre des artefacts sans l'un d'eux |
| `test-stop-multiline.sh` | nourrit les deux hooks d'une série de `STOP` et de `GO` qui ne diffèrent que par leur mise en forme |
| `see-placed-rune.php` | sert une page montrant la sprite d'une créature avec sa rune posée |
| `show-language-debt.sh` | la dette de langue de l'outillage versionné, en entier |
| `show-last-orders.php`, `show-queue-operation.php` | les derniers messages de l'opérateur, et les opérations de file d'un transcrit |

## Ce qui n'a pas sa place ici

**`local/scripts/` EST POUR LE JETABLE**, ce qui sert une fois et ne se rejoue pas — et **rien de versionné ne doit en dépendre**. Un essai versionné qui
appelle un script de `local/` est vert sur cette machine et absent sur toute autre ; la faute a été faite le 2026-08-22 et corrigée avant d'être montrée.
