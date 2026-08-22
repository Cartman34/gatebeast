# La chaîne de production

**Usage :** savoir ce qui se passe entre « ce sujet doit exister » et « cette sprite est livrée et inscrite », et par quelle commande.

**Intention :** qu'une image se commande d'une seule façon. Il y a eu deux commandes un temps — une pour les sujets posés bout à bout, une pour le reste — et
cette coupure n'a jamais été un fait du modèle : c'était l'habitude d'écrire une commande neuve à chaque besoin. Tout est une sprite posée sur la grille à côté
d'autres ; ce qui diffère est la **forme**, qui dit quels bords une pièce raccorde.

**Ne couvre pas** ce qu'un sujet doit être ([conception](../conception/vision.md)), la façon de corriger une consigne ([atelier](prompt-workshop.md)), ni les
contrôles qui jugent le résultat ([gardes](guards.md)).

## Le passage, dans l'ordre

**1. LE SUJET SE DÉCLARE** au référentiel `assets/subjects.json` et se décrit à l'inventaire — voir [le référentiel des sujets](subject-referential.md).
`asset_theme.py` dit dans quel jeu de sprites on dessine, `asset_catalog.py` ce qui existe, où et ce qui manque, `shape_vocab.py` ce qu'une forme veut dire.

**2. LA COMPOSITION SE DESSINE AVANT DE SE PRODUIRE** — voir [le plan de composition](composition-plan.md). Une faute de disposition doit coûter un plan,
jamais une génération.

**3. LA CONSIGNE S'ASSEMBLE, ET RIEN NE S'Y RETAPE.** `python3 scripts/generate-sprite.py <REF DU SUJET> <REF DU VARIANT>` lit tout au référentiel — emprise,
couvert, forme, et ce que le type déclare — et la description à l'inventaire, **citée mot pour mot**. Ce qui est propre à un sujet vit dans sa fiche, jamais
dans le code : une clause nommant poteaux et lisses sans condition est ce qui avait rendu cette commande inutilisable pour un chemin.

**Sans `--generate` elle s'arrête là**, en écrivant un brouillon sous `local/` : la consigne se lit avant que quoi que ce soit soit produit. Un fichier
`.parts.json` écrit à côté dit quel niveau a écrit chaque section — `common`, `type`, `variant`, `description`, `parameters`, `call` — et
`php scripts/show-prompt-parts.php --grep "<phrase>"` répond à la seule question utile devant une image fausse : **d'où vient cette phrase, donc où se porte le
correctif**.

**4. L'IMAGE SE PRODUIT.** `scripts/generate-image.php` enveloppe le générateur — l'agent Codex — et **ne s'appelle jamais à la main**.
`scripts/generate-version.php` fait la même chose pour une version de consigne de l'atelier. `production_report.py` chronomètre chaque étape et laisse un
rapport de validation à côté de l'image.

**5. ELLE SE MESURE, SE LIVRE ET S'INSCRIT.** `export-asset.py` redimensionne sans rien rogner et mesure l'emprise et le point de pose ; `record-asset.py`
enchaîne l'export et l'inscription au référentiel. `check-asset.py` mesure transparence, emprise, raccord et lumière. **`--generate` va jusqu'au bout et
republie la page des sprites** — une image qui existe sans y apparaître existe pour personne, et se reproduit.

**6. ELLE SE JUGE.** `set-asset-verdict.py` donne un verdict à une version et recalcule laquelle est courante ; `php scripts/remarks.php` tient les remarques
de l'opérateur. La **reprise unique** que la chaîne autorise est `--rework "<motif>"`, le motif exact du rejet cité en toutes lettres : il ne se donne qu'une
fois par version, une seconde reprise met l'image en défaut.

## Les outils de mesure et de regard

| Outil | Ce qu'il fait |
|---|---|
| `tile_scale.py` | **seul détenteur** des deux valeurs d'échelle : case d'écran à 24 px, finesse de livraison sur le zoom maximum |
| `plate_metrics.py` | la mesure d'une planche, à un seul endroit, pour que l'outil et le rapport s'accordent |
| `analyze-plate.py`, `build-plate-reports.py` | mesurer une planche, et en faire un rapport lisible |
| `stamp-witness-tile.py` | poser la case témoin sur une scène et vérifier le résultat |
| `tile-preview.py` | poser un sol côte à côte pour juger le raccord et le rythme de répétition |
| `set-rune-anchor.py` | poser le point où le moteur dessine la rune d'un individu |
| `resize-image.py`, `build-thumbnails.py` | rééchantillonner, et embarquer les sprites dans le catalogue d'images d'une page |
| `diff-prompts.sh`, `diff-prompts-words.sh` | réassembler toutes les consignes et les comparer à une référence — ce qui prouve qu'un renommage n'a rien changé |
| `build-ascii-plans.py`, `build-fence-geometry-svg.py`, `build-projection-plate.php` | rendre un plan en ASCII, la géométrie d'une clôture en vecteur, une planche de projection |
| `build-da-page.py`, `build-audio-page.py`, `build-calibration-page.py`, `build-planches-page.py` | les pages de revue publiées : direction artistique, sons, calibration, planches |
| `measure-calibration-v4.py` | la calibration v4 : deux rangées de huit silhouettes, debout et assises |
| `generate-usage-sample.py` | un exemple d'usage à partir d'un plan de composition |

## Ce qui n'est plus dans la chaîne

**`cut-asset.py`, `run-fence-campaign.py`, `sprite-queue.py` ET `list-variants.py` ONT ÉTÉ RETIRÉS** (`W23 outils-morts`). Une carte qui les nommait encore
envoyait un agent lancer une commande inexistante, et une carte fausse coûte plus cher qu'une carte absente.
