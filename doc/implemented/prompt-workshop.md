# L'atelier de consignes

**Usage :** savoir comment une consigne se corrige sans se réécrire, où vivent ses versions, et ce qui mesure l'effet d'une correction.

**Intention :** qu'on ne travaille plus en régénérant, mais **en modifiant ce qui a été généré** (opérateur, 2026-08-13). Retaper treize mille caractères pour
changer six clauses est la façon la plus sûre pour une version de gagner une différence que personne n'a décidée.

**Ne couvre pas** ce qu'une consigne doit dire ([conception](../conception/vision.md)), ni la commande qui produit une sprite ([chaîne de
production](production-chain.md)).

## Où vivent les versions

**SOUS `var/generations/prompts/<SUJET>/`, ET RIEN N'Y EST VERSIONNÉ.** Un fichier s'y nomme `<SUJET>.v<N>.<pièce>.<extension>`, et les pièces sont closes :
`prompt`, `image`, `edits`, `generation`, `transmitted`, `critiques`, `parts`.

**`review-server/lib/Prompts.php` CALCULE CES CHEMINS, ET LUI SEUL.** Quatre lecteurs en tenaient chacun leur copie ; le jour où le dossier a bougé, un seul a
été corrigé — l'application d'une source refusait tout sujet, l'extraction écrivait à côté d'un dossier disparu, et la page annonçait « aucune critique » sur
sept critiques présentes. **Aucune de ces trois pannes ne levait quoi que ce soit.**

**IL N'Y A JAMAIS QU'UNE VERSION EN ATTENTE** : celle qui suit la dernière **générée**. La page et les commandes désignent la même, parce que le calcul vit à un
seul endroit.

## Comment une version se corrige

**PAR UN BLOC DE SOURCE, ET C'EST LE SEUL CHEMIN.** `review-server/workshop/source/` porte quatre blocs — `projection.md`, `dimensions.md`, `assise.md`,
`lumiere.md` —, chacun déclarant les mots qu'il **gouverne** et que nul autre n'emploie. Tant qu'une clause est recopiée à la main dans une version, les deux
divergent au premier changement.

| Commande | Ce qu'elle fait |
|---|---|
| `apply-source.php <SUJET> <bloc>` | remplace une section entière par la clause du bloc, **et l'inscrit au journal d'édits** |
| `check-source.php` | en-têtes complets, une clause par bloc, aucun mot gouverné employé deux fois |
| `extract-transmitted.php` | ramasse la consigne que le générateur dit avoir réellement transmise |
| `check-transmitted.php` | mesure ce que la transmission a perdu |
| `set-edit-state.php` | fixe l'état d'un édit — et **refuse « tenue » sans observation** |
| `report-edit.php` | reporte un édit vers le code, et **refuse un édit qui n'est pas « tenue »**, en exigeant de dire OÙ |
| `show-generator-calls.php` | ce que l'agent a réellement lancé, qui n'est pas ce qu'il dit avoir fait |

**UNE SECTION SE REMPLACE ENTIÈRE, JAMAIS PAR MORCEAUX.** Substituer phrase à phrase laisse des restes de l'ancienne rédaction entre les nouvelles — c'est
exactement ainsi qu'une consigne s'est mise à dire deux fois la même chose dans deux styles.

**LE JOURNAL D'ÉDITS SE REJOUE, ET C'EST UNE GARANTIE, PAS UNE COMMODITÉ** : rejouer le journal d'une version sur la précédente doit redonner cette version
octet pour octet. C'est ce qui assure qu'elle n'a rien gagné en chemin. `scripts/dev/trial-apply-source.php` le vérifie, parce que rien d'autre ne pouvait voir
que les deux différaient.

## Ce que la page montre

**`/workshop` MET LA CONSIGNE ET L'IMAGE EN REGARD**, version par version. Elle n'offre d'onglet que pour les versions **générées** : la version à venir ne se
voit pas, elle apparaît le jour où elle porte une image. Le diff d'une version regarde **vers l'avant** — l'image de la `vN` avec le texte de la `vN+1` —, si
bien qu'une fois une version générée, ni son texte ni son diff ne se touchent plus.

**LA COLONNE DE LA CONSIGNE EST BORNÉE EN HAUTEUR** : sans cela on défile longtemps sans jamais voir ce qui part réellement au générateur.

**UN ESSAI DE CONSIGNE N'EST PAS UN LIVRABLE** : il n'entre à aucun référentiel et ne brûle aucune version de sujet.
