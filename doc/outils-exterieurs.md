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

**Toute version se reconstate avant de s'y fier** : une version écrite ici est un constat daté, pas une garantie.
