# Outils extérieurs et versions constatées

**Usage :** la liste des outils que le projet a validés, avec la version qui a été constatée. C'est elle que désignent les [règles du dépôt](regles-du-depot.md) quand elles disent qu'un outil non
validé se demande au lieu de s'essayer.

**Intention :** que cette liste ait une adresse à elle. Elle vivait dans `SUIVI.md`, qui se réécrit à chaque séance et qui a été élagué le 2026-08-11 : la règle a alors pointé vers un tableau qui
n'y était plus, et la seule copie restante était dans le journal des séances, un fichier qui ne fait pas foi. **Une liste que le code et les règles citent est une donnée, pas un état d'avancement.**

| Outil | Version | Usage |
|---|---|---|
| Codex (`codex`) | codex-cli 0.147.0 | le générateur d'images, enveloppé par `generate-image.php` |
| PHP | 8.4.24 | le wrapper du générateur, et l'outillage pérenne |
| Python | 3.12.3 | la mesure d'image et le traitement de matrice |
| `rsvg-convert` | 2.58.0 | SVG → PNG, pour que l'agent puisse regarder ce qu'il produit |

**LES BIBLIOTHÈQUES PYTHON ONT LEUR SCRIPT, ET C'EST LUI QUI FAIT FOI** : `bash scripts/install-tools.sh` dit ce qui est présent, ce qui manque, **et ce qui
réclame chacune** — une dépendance que personne ne peut attribuer est une dépendance que personne n'ose retirer. Il installe dans l'espace utilisateur, sans
droit administrateur, et **nomme** la commande privilégiée au lieu de la lancer. Versions constatées le 2026-08-20 :

| Bibliothèque | Version | Ce qui la réclame |
|---|---|---|
| `numpy` | 1.26.4 | les mesures d'image et le traitement de matrice |
| `Pillow` | 10.2.0 | l'ouverture et l'écriture des PNG, partout |
| `scipy` | 1.11.4 | les gradients de `check-axonometry.py` |
| `scikit-image` | 0.26.0 | les **segments droits** d'une sprite, par transformée de Hough — accordé le 2026-08-20, après des semaines de demande |

**CE QUE `scikit-image` A DÉBLOQUÉ, ET C'EST MESURÉ** : `check-axonometry.py` jugeait **4 clôtures sur 38**, parce que la silhouette d'une clôture est un peigne
qu'aucune droite n'épouse. En lisant ses **poteaux** comme des segments, il en juge **18**. Rien n'a bougé ailleurs : un feuillage n'a pas d'arête droite et
n'en aura jamais.

**Toute version se reconstate avant de s'y fier** : une version écrite ici est un constat daté, pas une garantie.
