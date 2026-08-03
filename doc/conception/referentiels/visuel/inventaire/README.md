# Inventaire des éléments

**Statut : esquisse.** L'inventaire se construit ; rien n'y est validé tant que le propriétaire n'a pas vu l'élément rendu.

**Intention :** pouvoir **désigner** et **reproduire** n'importe quel élément du monde. Sans inventaire, chaque image réinvente ses arbres, ses maisons et ses passants, et rien n'est réutilisable. Avec lui, une image se compose en citant des codes.

## Le code

`XX-nnn` : deux lettres de famille, trois chiffres. Le code est **stable à vie** — il ne change jamais, même si l'élément est renommé, redessiné, ou retiré. C'est lui que citent les consignes de production, les fichiers et le code du jeu.

| Famille | Code | Ce qu'elle contient |
|---|---|---|
| Créatures | `SP-nnn` | Espèces, avec leurs individus `SP-nnn-i` — voir [créatures](../../contenu/creatures-temoins.md) |
| Bâtiments | `BT-nnn` | Constructions habitables ou fonctionnelles — [batiments.md](batiments.md) |
| Végétation | `TR-nnn` | Arbres, arbustes, cultures, herbes — [vegetation.md](vegetation.md) |
| Sols et chemins | `CH-nnn` | Revêtements, sentiers, sols naturels — [sols-et-chemins.md](sols-et-chemins.md) |
| Objets | `OB-nnn` | Mobilier, outillage, aménagements, épaves — [objets.md](objets.md) |
| Personnages | `PR-nnn` | Humains, par silhouette et métier — [personnages.md](personnages.md) |
| Biomes | `BI-nnn` | Ambiances de terrain — [biomes.md](biomes.md) |

## Ce que porte chaque entrée

- **Code et nom français** — le nom sert à nous, le code fait foi.
- **Description en anglais** — reprise **mot pour mot** dans les consignes de production. C'est elle qui garantit la reproductibilité.
- **Emprise** en cases, pour tout ce qui occupe le sol.
- **Où il apparaît** — les biomes ou planches concernés.

## Élément, instance et situation

Une entrée décrit un **type**, jamais une apparition précise. Une apparition est une **instance**, notée `CODE @ planche (colonne,rangée)`, avec ce qu'elle fait et son orientation. Les instances vivent dans la fiche de la planche, jamais ici : un même type se retrouve dans dix situations sans être décrit dix fois.

Une **variante** d'un type reçoit son propre code, jamais un suffixe : deux maisons différentes sont deux entrées, parce qu'on doit pouvoir les demander séparément.

## Règles de tenue

- Une famille par fichier ; si un fichier dépasse deux cents lignes, il se scinde par sous-famille et le README l'indique.
- Les numéros ne se réutilisent jamais, même après retrait. Un élément retiré reste listé avec la mention **retiré** et la raison.
- Un élément n'entre dans l'inventaire qu'avec sa description anglaise complète : une entrée sans description ne sert à rien, puisqu'elle n'est pas reproductible.
