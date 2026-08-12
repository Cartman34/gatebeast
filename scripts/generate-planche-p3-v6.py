#!/usr/bin/env python3
"""Plate P3 foothills, sixth pass — v5 kept its three structural wins (dry crevasse, walled pen with a
visible inside, dense forest across the foreground) and they are carried unchanged. Fixed here, from
the v5 report: the trees came out BROADLEAF instead of pines (described positively now, shape by shape),
the sheepfold rendered far under its eight tiles and open like a shed instead of pierced by a door, the
SP-016 pair had four legs instead of six, SP-005 came out as a dragonet, the left edge joint was barely
legible, and the plate was too dark (95.8 of luminance, 20.4% dark) — the shared base now carries the
light standard, and the rock is prescribed in its pale values here.

USAGE
  A FROZEN PLATE PROMPT — a historical document, not a command to run again. It produced
  assets/revue-da/planche-p3-contreforts-v6.png, and its prompt is frozen beside it in
  assets/revue-da/prompt-p3-contreforts-v6.txt. It is kept so the exact text sent to the generator can
  be read back next to the image it made. It takes no argument and answers no help: there is nothing
  to call it with. Running it would spend a generation on a plate that already exists.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import RAPPEL_FINAL_FR, preambule_fr, shoot

COMPOSITION = """
CONTRÔLE DE GRILLE — chaque élément est donné par ses coordonnées de case. Place-le EXACTEMENT à ces
cases, avec l'emprise annoncée, remplie jusqu'à ses bords. Un adulte debout fait deux cases : huit cases
valent QUATRE adultes bout à bout.

PLANCHE P3 — CONTREFORTS. Biome : pentes rocheuses de montagne vues d'en haut, BAIGNÉES DE SOLEIL.
LA ROCHE EST CLAIRE : parois gris perle et beige lumineux striées d'ocre chaud, éclairées sur toutes
leurs faces, arêtes vives en pleine lumière et creux simplement plus doux — jamais des masses grises et
mates. Herbe rase d'un VERT VIF ET SATURÉ, pinèdes d'un vert franc. La planche est PLEINE : entre les
parois, l'herbe porte rochers clairs, pierriers et fleurs de montagne.
IL N'Y A AUCUNE EAU DANS CETTE IMAGE : pas de ruisseau, pas de torrent, pas de mare, pas de flaque.

LES ARBRES SONT DE VRAIS PINS — décris-les forme par forme, c'est le point qui a échoué au passage
précédent : un pin a un TRONC NU ET DROIT, à l'écorce ROUSSE ET ÉCAILLEUSE en plaques, dégagé sur les
DEUX TIERS INFÉRIEURS de sa hauteur — on voit le tronc de loin. Au sommet, un HOUPPIER EN PARASOL : une
masse d'AIGUILLES fines, vert sombre bleuté, étalée en plateau LARGE ET PLAT, plus large que haute,
portée par quelques grosses branches coudées qui partent haut sur le tronc. Un pin de cette planche
ressemble à un pin parasol méditerranéen ou à un pin sylvestre adulte. Il n'a NI feuilles larges, NI
couronne ronde posée sur un tronc court, NI silhouette de cône vert descendant jusqu'au sol.

La roche d'abord — bandes de paroi abrupte vues d'en haut, dans leurs valeurs CLAIRES : en haut à gauche
(1,1)-(13,4) ; autour de la mine (16,1)-(19,9) ; en haut à droite (28,1)-(32,8) avec un ÉBOULIS en
dessous en (29,9)-(32,13). Rochers de tailles variées, gris pâle veiné de blanc, en (17,11)-(18,12),
(7,9)-(8,10), (23,17)-(24,18) et (12,16)-(13,17). Aucun ne touche un sentier.

RACCORDS DE BORD — deux sentiers pierreux d'une case de large, VISIBLEMENT coupés par leur bord :
1. Le long de la RANGÉE 8, atteignant le BORD GAUCHE en (1,8). SUR SES QUATRE DERNIÈRES CASES, de (4,8)
   à (1,8), le sentier court sur de l'HERBE RASE ET DÉGAGÉE, sans un rocher ni un pin autour : sa bande
   de pierres claires se détache franchement du vert et on la suit à l'œil jusqu'au bord de l'image.
2. Le long de la COLONNE 26, atteignant le BORD BAS en (26,24), TRAVERSANT LA FORÊT DE PINS de part en
   part : la forêt s'ouvre en une tranchée d'une case, et le sentier reste visible jusqu'au bord bas.

SENTIERS — en lacets, les SEULS chemins de l'image : de (1,8) à (10,8) ; colonne 10 de (10,8) à
(10,14) ; rangée 14 de (10,14) à (26,14) ; colonne 26 de (26,14) à (26,24). Branches : colonne 5 de
(5,9) à (5,11), s'arrêtant À la porte de la bergerie ; colonne 23 de (23,8) à (23,13), reliant la gueule
de la mine au sentier ; de (26,17) un pas vers (27,17) vers la tour en ruine. Aucun autre chemin.

LA CREVASSE — SÈCHE, PAS UN COURS D'EAU. Une entaille rocheuse étroite fend le sol le long des COLONNES
14 ET 15 SEULEMENT, de (14,5) à (15,15) : DEUX CASES DE LARGE, aux lèvres de roche vive et franches,
si étroite et si profonde qu'ON N'EN VOIT PAS LE FOND — l'intérieur descend dans une ombre brun-noir,
sans eau, sans reflet, sans végétation. C'est la SEULE zone sombre autorisée de la planche, et elle ne
fait que deux cases de large : tout le reste est en pleine lumière. Un gouffre réellement dangereux, à
pic. Herbe unie au-dessus et en dessous, la crevasse n'atteint AUCUN bord. Un PONT SUSPENDU couvre
(14,14)-(15,14) et porte le sentier de la rangée 14 par-dessus : planches et cordes, légèrement
affaissé, ses deux bouts posés sur le sentier. Aucun autre franchissement.

FORÊT DE PINS DENSE SUR LE DEVANT — le bas de l'image est une pinède serrée : houppiers en parasol qui
se touchent et se chevauchent, troncs roux nus bien visibles dessous, tapis d'aiguilles au sol éclairé
par taches de soleil. Une masse continue d'arbres, pas quelques arbres épars. DEUX ZONES :
(11,20)-(25,24) et (27,20)-(32,24), les deux atteignant le bord bas. Entre elles, la tranchée du sentier
de la colonne 26. Plusieurs pins déclarent une emprise au sol de deux cases sur deux, houppier plus
large encore ; tous diffèrent en hauteur, en inclinaison et en teinte d'aiguilles.

BÂTIMENTS — chaque porte NETTEMENT PLUS HAUTE qu'un adulte debout :
- BERGERIE, (2,12)-(9,19) : HUIT CASES SUR HUIT, et elle OCCUPE TOUTE CETTE EMPRISE — quatre adultes de
  large sur quatre de profond, un vrai bâtiment de ferme, pas un abri ni un hangar. Murs PLEINS de
  pierre sèche claire montant sur les quatre côtés, toit de bois à deux pentes couvrant les huit cases.
  Sur sa face haute, en (5,12), UNE VRAIE PORTE À DEUX BATTANTS DE BOIS, encadrée de pierre, percée
  dans le mur plein et NETTEMENT PLUS HAUTE qu'un adulte : le mur continue de part et d'autre. Aucune
  façade ouverte, aucun côté manquant. Le sentier d'accès s'arrête à cette porte. Foin visible par la
  porte entrouverte. Usée, entretenue.
- ENTRÉE DE MINE, (20,1)-(27,7) : gueule de galerie boisée taillée dans la paroi, poutres trapues,
  petite lanterne éteinte suspendue, rails sortant vers un CHARIOT DE MINE de deux cases en
  (21,9)-(22,9), à moitié plein de minerai.
- TOUR EN RUINE, (28,16)-(31,19) : tour de guet ronde brisée, effondrée d'un côté, mousse sur les
  pierres claires. Une ruine — pas de porte requise.

L'ENCLOS N'EST PAS UN BÂTIMENT, (2,20)-(9,23) : UNIQUEMENT DES MURS DE PIERRE SÈCHE, bas — un peu plus
haut que la moitié d'un adulte debout — bordant un rectangle de huit cases sur quatre. AUCUN TOIT,
aucune façade, aucune fenêtre : vu d'en haut, TOUT L'INTÉRIEUR EST VISIBLE ET EN PLEIN SOLEIL, herbe
rase piétinée, une auge de pierre, un tas de foin. Un portillon de bois dans le mur haut le relie à la
bergerie.

RAPPEL D'ÉCHELLE, AU MILIEU DE LA CONSIGNE : un adulte DEBOUT fait ENTRE 1,75 ET 2 CASES, moins d'un
douzième de la hauteur de l'image. Les humains SEMBLENT PETITS sur la pente, comme des figurines. La
façade de la bergerie fait QUATRE FOIS la hauteur d'un adulte debout.

VÉGÉTATION — hors de la pinède du devant : quatre pins isolés, de vrais pins comme décrits plus haut,
chacun d'une hauteur et d'une inclinaison différentes, en (4,6), (8,6), (18,18) et (30,14) ; herbe rase
de montagne partout ailleurs, semée de petites fleurs de montagne et de pierres claires dans la limite
d'habillage — la pente vit, elle n'est pas nue.

HABITANTS — chacun cité de sa fiche, dessiné EXACTEMENT ainsi, et chacun PETIT dans la scène :
- (5,15), DEBOUT — ENTRE 1,75 ET 2 CASES, pas plus — près de la bergerie, REGARDANT DROIT VERS LE BAS
  face caméra, visage bien visible : femme burinée d'une cinquantaine d'années, peau olive, cheveux gris
  tressés, épais châle tissé sur une robe de laine, bâton de bergère.
- (23,8), DEBOUT — ENTRE 1,75 ET 2 CASES — s'épongeant le front à la gueule de la mine, REGARDANT VERS
  LE BAS : homme trapu de la trentaine, peau brun moyen, casque de cuir à petite lampe éteinte, veste de
  toile poussiéreuse, gros gants à la ceinture.
- (12,14), DEBOUT — ENTRE 1,75 ET 2 CASES — s'engageant vers le pont suspendu vers la DROITE, tenant la
  corde : jeune femme à la peau claire tachée de son, cheveux roux, petit sac usé à couverture roulée,
  bonnes chaussures de marche, visage curieux.
- Dans l'enclos, broutant, bien visibles entre les murs bas : en (4,21) le plus grand, REGARDANT DROIT
  VERS LE BAS face caméra, et en (7,21) le plus petit et plus brun : deux individus de l'espèce SP-016 —
  créature ronde de pâture, couverte d'une laine dense VERT MOUSSE sur une peau gris ardoise, museau
  plat et amical, deux cornes enroulées vers l'arrière comme des coquilles d'escargot, PAS DE QUEUE.
  ELLE A SIX PATTES, ET LES SIX SE VOIENT : compte-les — trois de chaque côté, courtes et robustes,
  régulièrement espacées sous le corps, de l'épaule à la hanche. Quatre pattes, c'est faux. Le grand
  porte sa rune, un seul trait au front entre les cornes : une VOLUTE, jaune paille. Le petit, au même
  endroit : un DOUBLE ANNEAU LIÉ, jaune paille.
- (17,11), perché sur le rocher au-dessus de la crevasse, REGARDANT VERS LA GAUCHE : SP-007, créature
  fine gris argenté à la LONGUE QUEUE ANNELÉE portée en panache, grands yeux ronds, fourrure courte et
  dense, corps souple, museau court arrondi, petites oreilles rondes, pattes fines à larges doigts. Sa
  rune, un seul trait au bout de la queue : une GOUTTE, rose.
- (29,12), dressée sur ses pattes arrière dans l'éboulis : SP-005, petite créature bleu pâle À FOURRURE,
  corps mince, museau pointu, queue à pinceau, et de LONGUES OREILLES SOUPLES ET CHARNUES QUI RETOMBENT
  ET PENDENT LE LONG DU DOS comme deux rubans — des oreilles tombantes, jamais dressées. C'est un petit
  être de fourrure, doux et rond : PAS d'écailles, PAS de crête dorsale, PAS de museau de reptile, PAS
  d'ailes — rien d'un dragon. Sa rune, un seul trait à la base de l'oreille droite : un CHEVRON, orange.
- LA CRÉATURE MAJESTUEUSE, (21,10)-(22,11), DEUX CASES au sol, debout près du sentier de la mine,
  contemplant la vallée, REGARDANT VERS LE BAS : SP-014, puissante créature des montagnes aux plaques de
  pierre bleu ardoise CLAIRE le long du dos et des épaules, lourde tête calme à deux cornes couchées
  vers l'arrière, pattes épaisses à larges pieds, mousse dans les joints de ses plaques — comme un
  versant de colline qui aurait décidé de marcher. Sa rune, un seul trait sur l'avant-bras gauche : un
  ZIGZAG HORIZONTAL, vert mousse.
"""

FIN = "\nRien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.\n"

if __name__ == "__main__":
    sys.exit(shoot("p3-contreforts-v6", preambule_fr("UNE CASE SUR TROIS") + COMPOSITION
                   + RAPPEL_FINAL_FR + FIN))
