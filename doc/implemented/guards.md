# Les gardes

**Usage :** savoir ce qui empêche une faute de passer, et où. Deux familles bien distinctes : les **hooks**, qui tiennent la conduite de l'agent pendant son
tour, et les **contrôles**, qui tiennent l'état du dépôt et se lancent à la main ou en fin de séance.

**Intention :** qu'aucune de ces deux familles ne repose sur la mémoire d'un agent. Chaque garde de ce document est née d'une faute réelle, répétée après avoir
été écrite dans les règles — c'est le constat qui les a fait exister : **une règle qui dépend de la vigilance ne tient pas.**

**Ne couvre pas** ce que les règles disent ([regles-du-depot.md](../regles-du-depot.md)), ni ce que chaque contrôle vérifie en détail — chacun le dit dans son
bloc « Usage » et « Intention », et `php scripts/<nom> -h` le rend.

## Les hooks, et ce qui les branche

**`.claude/settings.json` FAIT FOI SUR CE QUI EST BRANCHÉ** — un hook présent dans `scripts/` mais absent de ce fichier ne tourne pas. **La session s'ouvre
depuis la racine du dépôt, sinon rien ne se charge.**

| Hook | Quand | Ce qu'il fait |
|---|---|---|
| `hook-pre-bash.sh` | `PreToolUse` sur `Bash` | de l'opérateur, hors dépôt : refuse `;`, `&&`, les sous-shells, les redirections vers un fichier, les `sed -i` |
| `scripts/hook-guard-dequeue.sh` | `PreToolUse` sur `Bash`, `Write`, `Edit` | refuse tout geste qui effacerait l'armement du dépilement — **ou cette garde elle-même** |
| `scripts/hook-guard-scopes.sh` | `PreToolUse` sur les outils d'écriture | refuse une écriture hors du dépôt ou sous `var/`, qui appartient à l'application |
| `scripts/hook-prompt.php` | `UserPromptSubmit` | arme ou désarme le dépilement sur le mot de l'opérateur — `GO`, `STOP` — et l'armement **expire seul** |
| `scripts/hook-stop.php` | `Stop` | refuse la fin de tour tant qu'un point reste à faire ou en cours |

**TROIS BRIQUES SERVENT CES HOOKS ET NE SE BRANCHENT PAS** : `scripts/hook-trace.php` tient l'état armé et la trace de chaque passage sous `var/hooks/` ;
`scripts/hook-word.php` lit les mots d'ordre dans un message ; `scripts/hook-transcript.php` rend les entrées du transcrit, dont les `queue-operation` par
lesquelles un message glissé en cours de tour se retrouve. **`scripts/check-last-order.php`** s'en sert pour dire quel est le dernier ordre reçu.

**LA GARDE DES PORTÉES VISE LES OUTILS D'ÉCRITURE, PAS `Bash`**, et cette asymétrie est la règle même : ce que l'agent écrit de sa main passe par `Write` ou
`Edit`, tandis que ce qu'un script écrit en tournant est exactement ce à quoi `var/` sert.

**`scripts/check-last-order.php` NE BOOTE PAS, ET IL NE DOIT PAS.** C'est un hook : transformer les avertissements en exceptions ferait cesser la garde au
moment précis où elle est consultée.

## Les contrôles

**TOUS RÉPONDENT À `-h`, TOUS SE LANCENT DEPUIS LA RACINE, ET TOUS ÉCHOUENT DE LA MÊME FAÇON** — `scripts/bootstrap.php` câble les fautes en exceptions et rend
la racine ; `scripts/Tools.php` porte ce que plusieurs commandes partagent, dont la réponse à `-h`.

| Contrôle | Ce qu'il refuse ou signale |
|---|---|
| `check-text-width.php` | une ligne au-delà de 200 caractères, ou un paragraphe replié plus court |
| `check-cited-paths.php` | un chemin cité dans un document et qui ne mène nulle part |
| `check-comment-language.php` | un commentaire de code en français |
| `check-code-language.py` | un nom ou une valeur comparée en français |
| `check-tools.php` | une commande sans bloc d'usage, sans aide, qui nomme un fichier disparu, ou qui refuse sans dire la solution |
| `check-implemented-coverage.php` | un fichier du dépôt que ce dossier ne nomme nulle part |
| `check-no-new-python.php` | un `.py` versionné absent du relevé `scripts/python-inventory.json` |
| `check-subjects.py` | un référentiel non conforme au modèle, ou en écart avec l'inventaire et le disque |
| `check-subjects-against-inventory.php` | un sujet du référentiel absent de l'inventaire |
| `check-subject-parameters.php` | une fiche qui laisse un paramètre de son type non fixé — **il signale, il ne refuse pas** |
| `check-footprints-rectangular.php` | le jour où une emprise cessera d'être un rectangle plein — **une veille, pas un défaut** |
| `check-piece-widths.php` | un jeu de pièces dont les largeurs ne s'accordent pas |
| `check-height-bands.php` | une hauteur dessinée hors de la fourchette que le sujet déclare |
| `check-asset-theme.php` | un asset qui s'écarte du style tenu |
| `check-axonometry.py` | une sprite hors projection — **trois états, et il dit quand il ne peut pas conclure** |
| `check-parallel-projection.php` | la dérive des verticales sur une sprite |
| `check-prompt-units.php` | une consigne qui mélange ses unités |
| `check-plate-prompts.py` | une consigne de planche fautive, avant génération |
| `check-plan-couverts.php` | un couvert de plan incohérent avec l'emprise |
| `check-pages-indexed.php` | une page servie absente de l'index |
| `check-page-selectors.php` | un sélecteur que la page n'expose plus |
| `check-review-pages.php` | une page de revue qui ne se reconstruit pas |
| `check-asset.py` | les mesures d'un asset : transparence, emprise, raccord, lumière |
| `check-asset-prompt.py` | la définition du maître, le contrat d'emprise, le socle de style et la cascade — **rien n'est généré** |
| `check-prompts.py` | que l'assemblage d'une consigne reproduit encore les consignes du POC, octet pour octet |
| `check-catalog.py` | le module de catalogue contre lui-même : adressage, lecture, repli, aller-retour |
| `check-runes.py` | que chaque rune déclarée a une forme, une couleur et un tracé |
| `check-witness-tile.py` | que la case témoin fait exactement une case, alignée sur la grille |
| `check-tool-paths.py` | qu'une constante de chemin dans `scripts/` mène à quelque chose de réel |

**CHAQUE CONTRÔLE A SON ESSAI** sous `scripts/dev/trial-*`, et un essai se lance après toute reprise du contrôle : c'est la seule manière de voir qu'une
commande perd son aide ou change de sortie.

## Ce que les gardes ne rattraperont jamais

**UNE ERREUR TRANSPARENTE EST INTERDITE, ET AUCUNE MACHINE NE LA VOIT** : une construction qui transforme une panne en fonctionnement normal ne lève rien,
n'affiche rien, et rend un résultat plausible. Elle se paie en outil — un contrôle qui compare deux choses qui devraient être égales —, jamais en vigilance.
`scripts/dev/trial-apply-source.php` en est l'exemple : il rejoue un journal d'édits et compare le texte obtenu à celui écrit, parce que rien d'autre ne
pouvait voir que les deux différaient.
