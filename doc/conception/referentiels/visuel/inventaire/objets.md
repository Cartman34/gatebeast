# Objets — `OB`

Voir les [règles de l'inventaire](README.md). Mobilier, outillage et aménagements. Emprise en cases quand elle dépasse une case.

## Clôtures et murs — campagne et parc

Sujets qui s'assemblent bout à bout : leur type déclare ses formes, et chaque forme se dessine dans chacune de ses orientations, parce qu'un volume ne se pivote pas ([lots de variants](../assets/lots-de-variantes.md)).

- **OB-010 barrière en rondins** — `log-fence-01`, type clôture, 1 × 1, hauteur 0,9 case, infranchissable. **Trois compositions de poteaux**, toutes avec les **deux lisses** qui traversent la case d'un bord à l'autre : `posts-2` deux poteaux plantés **au tiers et aux deux tiers** de la case, de sorte que le vide à gauche, le vide du milieu et le vide à droite soient égaux ; `posts-1` un seul poteau au centre ; `posts-0` aucun poteau, les lisses seules. Elles existent pour qu'une portée ne double pas ses poteaux à chaque jointure : on alterne les compositions pour espacer les poteaux régulièrement. **Les formes nord-sud ne portent qu'un seul poteau** — décision de l'opérateur : vue de dessus, une pièce enfilée en profondeur montrerait deux poteaux presque superposés. **Pour la même raison, elles ne montrent qu'une seule lisse** : vue de dessus, la profondeur de la pièce aligne ses deux lisses horizontales dans l'axe du regard, si bien qu'elles se superposent exactement l'une sur l'autre. Les lisses sont à la même hauteur et à la même épaisseur dans les trois, sinon elles ne se prolongent pas. **Un second axe, propre aux lignes `ns` et `ew`, porte trois valeurs** : `gate-none` la clôture pleine, `gate-closed` le portillon fermé, `gate-open` le portillon ouvert — combinées aux deux orientations, cela fait quatre variants de portillon (est-ouest fermé, est-ouest ouvert, nord-sud fermé, nord-sud ouvert). Cet axe existe parce qu'un portillon change ce que la case laisse passer : fermé, il ferme comme le reste de la clôture ; ouvert, il laisse entrer sur la case. Formes : les lignes `ns` et `ew`, et les quatre angles `ne`, `es`, `sw`, `nw`. *Une clôture à hauteur de taille faite de rondins fendus, deux lisses horizontales chevillées entre des poteaux ronds et robustes, l'écorce encore présente sur le bois et argentée par les intempéries. AU PIED DE CHAQUE POTEAU, DE L'HERBE, ET C'EST L'ÉLÉMENT LE PLUS SOUVENT OUBLIÉ : des touffes d'herbe haute poussent serrées contre le bois, à la base de chaque poteau, et débordent en touffes plus basses le long des lisses — de la mousse s'accroche aussi au bas des poteaux. Sans elles la clôture paraît posée sur du vide, et c'est le seul reproche que l'opérateur lui ait fait.* Description propre à la valeur `gate-closed` : *la même clôture, sa travée centrale remplacée par un portillon bas et battant fait des mêmes rondins fendus, suspendu par des pivots de fer chevillés dans le poteau qui le porte, avec de la mousse au pied de chaque poteau et l'herbe poussée haute contre la clôture comme sur le reste du sujet, fermé et dans l'alignement exact de la clôture, sa lisse supérieure au même niveau que les lisses de part et d'autre.* Description propre à la valeur `gate-open` : *la même clôture, sa travée centrale ouverte sur un portillon bas et battant fait des mêmes rondins fendus, suspendu par des pivots de fer chevillés dans le poteau qui le porte, avec de la mousse au pied de chaque poteau et l'herbe poussée haute contre la clôture comme sur le reste du sujet ; sa lisse supérieure est au même niveau que les lisses de part et d'autre. Le battant est GRAND OUVERT, pivoté de cent trente-cinq degrés vers l'intérieur, si bien qu'il forme un angle net avec la ligne de la clôture au lieu de rester dans son alignement ; le passage est dégagé sur toute la largeur de la travée, l'herbe et le sol visibles à travers l'ouverture.*

## Montagne

- **OB-020 cairn** — hauteur 1,4 case. *Un empilement de pierres plates à hauteur d'épaule, signalant un chemin, légèrement penché, du lichen sur ses pierres basses.*
- **OB-021 abreuvoir de pierre** — hauteur 0,5 case. *Un abreuvoir de pierre creusé, alimenté par une mince source, l'eau débordant par un bord usé, de la mousse autour de sa base.*
- **OB-022 wagonnet de mine** — hauteur 0,7 case. *Un petit wagonnet à minerai rouillé sur un court tronçon de rail, une roue grippée, à moitié rempli de roche grise.*
- **OB-023 corde et poulie** — hauteur 2 cases. *Une corde patinée passée sur une poulie de fer boulonnée à une poutre, son extrémité libre pendant avec un crochet.*

## Marais

- **OB-030 barque à fond plat** — 3 × 1, hauteur 0,4 case. *Une barque à fond plat de planches sombres, amarrée à un pieu, une perche posée en travers, un doigt d'eau dans son fond.*
- **OB-031 nasse à anguilles** — hauteur 0,5 case. *Une nasse à anguilles en osier tressé, conique, à moitié immergée et attachée à un pieu.*
- **OB-032 pieu d'amarrage** — hauteur 0,8 case. *Un unique pieu d'amarrage patiné, planté dans la vase, une corde enroulée autour, la ligne de flottaison tachée de vert.*
- **OB-033 planche pourrie** — hauteur 0,1 case. *Une planche brisée, à moitié couchée dans l'eau, son extrémité éclatée et noircie par la pourriture.*

## Littoral

- **OB-040 casier à homards** — hauteur 0,4 case. *Un casier à homards en bois à claire-voie, avec une corde et un petit flotteur, empilé ou couché sur le côté.*
- **OB-041 filet à sécher** — hauteur 1,2 case. *Un large filet de pêche étendu sur un cadre de bois pour sécher, lesté de flotteurs le long de son bord.*
- **OB-042 barque échouée** — 4 × 2, hauteur 0,6 case. *Une petite barque à clins tirée sur le sable, sa peinture écaillée, des rames rangées à l'intérieur.*
- **OB-043 bouée de verre** — hauteur 0,2 case. *Un flotteur de verre vert pris dans un filet de corde, posé dans le sable.*
- **OB-044 bois flotté** — hauteur 0,3 case. *Une bille de bois flotté pâle et blanchie, lissée et fendillée par le sel.*
- **OB-045 borne d'amarrage** — hauteur 0,5 case. *Une courte bitte d'amarrage en fer sur un ponton, une corde lovée à son pied, la rouille coulant le long de son flanc.*
