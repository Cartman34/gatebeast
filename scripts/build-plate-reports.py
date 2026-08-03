#!/usr/bin/env python3
"""Build one report per plate: what the numbers say, and what the eye saw.

The owner asked for a single readable score per plate, with the detail one click away. A report has two
halves:

- MECHANICAL — every measurement against its target, each one pass or fail. Computed here, never typed
  by hand, so it is replayed identically after every shot.
- CRITICAL PASS — the eye observations, which no measurement replaces: human scale, real animals, sheets
  honoured, plan honoured, edge joints, internal coherence. Those are recorded below per plate, and are
  the constats already written in the suivi — they are data, not prose to re-derive.

A report is written as rapport-<key>.json (read by the review page) and rapport-<key>.md (readable on
its own). Both are rewritten only for the keys handed to this script: a plate that is not re-shot keeps
its report untouched.

Usage: python3 build-plate-reports.py [key ...]   (default: the six current plates)
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from plate_metrics import ASSETS, DARK_MAX, LUMINANCE_MAX, LUMINANCE_MIN, REFERENCE, measure

# Load floor and ceiling per biome, RECALIBRATED on the measured plates rather than guessed.
#
# What the measurements showed, once every version was measured with the same metric: the figure tracks
# SURFACE TEXTURE far more than emptiness. Textured cobbles, a pine wood and marsh vegetation each read
# as load, so the five plates judged good by eye land between 75.8 and 95.3 — and nothing ever measured
# has looked cluttered. The high end therefore no longer discriminates: the ceiling is set at 100 and
# says so, and a plate that is too busy is caught by the eye in the critical pass, not by this number.
#
# The floor, on the other hand, does work: every plate judged too empty measured below it. Each floor
# below sits just under the LOWEST value of that biome that was judged acceptable, so the check keeps
# catching the real fault it was built for.
#
# Evidence per biome (value, verdict): p1 79.0 correct / 88.7 correct. p2 72.0 correct / 94.0 correct.
# p3 68.9 correct / 95.3 correct. p4 50.5 retained by the owner / 95.2 correct — a 45-point spread on
# one biome, both acceptable, which is the clearest proof the figure is not measuring fullness. p5 43.8
# TOO EMPTY / 75.8 correct. p6 38.9 and 36.8 both TOO EMPTY, no acceptable sample yet.
CHARGE = {
    "p1-campagne": (70.0, 100.0, "plafond non discriminant : la mesure suit la texture de surface, "
                                 "le fouillis se juge à l'œil"),
    "p2-bourg": (65.0, 100.0, "le pavage texturé compte comme de la charge ; plafond non discriminant"),
    "p3-contreforts": (62.0, 100.0, "la pinède compte comme de la charge ; plafond non discriminant"),
    "p4-marais": (48.0, 100.0, "de 50,5 à 95,2 sur ce biome, les deux jugées correctes : la mesure ne "
                               "dit rien du remplissage ici, seul le plancher garde un sens"),
    "p5-falaise": (60.0, 100.0, "plancher calé au-dessus du passage jugé trop vide (43,8)"),
    "p6-plage": (55.0, 100.0, "plancher provisoire : aucun passage de ce biome n'a encore été jugé "
                              "correct, les deux mesurés étaient trop vides"),
}
SATURATION_MIN = 60.0  # close to the reference (73), which no plate has reached since the recalibration

# Eye observations, per plate — the constats already established, carried as data.
CRITIQUE = {
    "p1-campagne-v8": [
        ("Échelle humaine", "ok", "fermier, porteuse, meunier et les deux enfants tous petits"),
        ("Aucun animal réel", "faute", "SP-010 reste un cerf réel, bois ramifiés compris ; SP-008 a "
                                       "viré au faon tacheté ; SP-001 frôle le renardeau"),
        ("Fiches respectées", "faute", "SP-010 et SP-008 s'écartent de leur fiche ; le duo SP-007 "
                                       "garde sa queue annelée mais un corps de lémurien"),
        ("Plan respecté", "ok", "route du sud et ru enfin parallèles à une case d'écart, tous deux "
                                "coupés par le bord bas — la faute majeure de v7 est corrigée"),
        ("Raccords de bord", "ok", "route principale de bord à bord, route du sud au bord bas"),
        ("Cohérence interne", "faute", "une voie court encore sous la chaumière jusqu'au bord bas ; "
                                       "un conifère de trop"),
        ("Corrections demandées", "ok", "sol prescrit surface par surface, cultures larges, chêne "
                                        "multi-cases, lumière et saturation les meilleures du lot"),
    ],
    "p5-falaise-v5": [
        ("Échelle humaine", "ok", "les cinq humains sont petits, y compris le pêcheur au sommet des "
                                  "marches"),
        ("Aucun animal réel", "faute", "SP-001 est rendu en renard réel — museau pointu, queue "
                                       "touffue à bout blanc"),
        ("Fiches respectées", "faute", "SP-001 hors fiche ; SP-002 dessinée en deux exemplaires alors "
                                       "qu'un seul est listé"),
        ("Plan respecté", "ok", "falaise sur tout le bas et sur le bord droit sous la moitié, mer en "
                                "contrebas, phare élancé à sa place"),
        ("Raccords de bord", "ok", "les trois raccords atteignent leur bord"),
        ("Cohérence interne", "ok", "L'ESCALIER EST LÀ : marches de granite et main courante de corde "
                                    "reliant sans interruption le chemin à la passerelle"),
        ("Corrections demandées", "ok", "escalier obtenu en lui donnant sa propre emprise ; plateau "
                                        "rempli par masses listées, charge de 43,8 à 75,8 %"),
    ],
    "p1-campagne-v7": [
        ("Échelle humaine", "ok", "les quatre humains sont petits, les portes plus hautes qu'eux"),
        ("Aucun animal réel", "faute", "la majestueuse SP-010 est un cerf réel, bois compris ; le duo "
                                       "SP-007 reste lapin ou chinchilla"),
        ("Fiches respectées", "faute", "SP-007 et SP-010 s'écartent de leur fiche"),
        ("Plan respecté", "faute", "le ru est tracé une à deux colonnes trop à gauche et la route du "
                                   "bord bas manque"),
        ("Raccords de bord", "ok", "la route traverse de bord à bord sur la rangée 16"),
        ("Cohérence interne", "faute", "la desserte de la chaumière se prolonge au-delà de sa porte "
                                       "jusqu'au bord ; un conifère surnuméraire"),
        ("Corrections demandées", "ok", "voies martelées, habillage plus riche, cultures agrandies et "
                                        "doublées, chêne multi-cases, majestueuse déplacée"),
    ],
    "p2-bourg-v6": [
        ("Échelle humaine", "ok", "les sept personnages font de l'ordre de deux cases — la régression "
                                  "de v5 est corrigée"),
        ("Aucun animal réel", "faute", "SP-011 tire au cheval, SP-005 est redevenue un lapin, SP-001 "
                                       "frôle le renardeau réel"),
        ("Fiches respectées", "faute", "corne de SP-011 courbée vers le haut au lieu de l'arrière ; "
                                       "oreilles de SP-005 dressées au lieu de tombantes"),
        ("Plan respecté", "ok", "tous les bâtiments, la place, les étals, le puits et la charrette "
                                "sont à leur case annoncée — la régression de v5 est corrigée"),
        ("Raccords de bord", "ok", "les trois rues atteignent leur bord"),
        ("Cohérence interne", "faute", "quelques bandes pavées ne correspondent à aucune voie ; place "
                                       "et maisons mitoyennes plus petites que leur emprise"),
        ("Corrections demandées", "ok", "maison du potier au nord et atelier bas au sud : aucun des "
                                        "deux n'en masque un autre"),
    ],
    "p2-bourg-v7": [
        ("Échelle humaine", "ok", "les sept personnages restent petits, portes plus hautes qu'eux"),
        ("Aucun animal réel", "remarque", "SP-001 et SP-005 sont enfin des créatures inventées ; "
                                          "SP-011 garde une carrure de quadrupède familier"),
        ("Fiches respectées", "faute", "SP-011 reste chevalin ou caprin malgré la corne redressée vers "
                                       "l'arrière ; SP-005 et SP-001 sont conformes"),
        ("Plan respecté", "ok", "bâtiments, place, fontaine, étals, puits et charrette à leur case"),
        ("Raccords de bord", "ok", "les trois rues atteignent leur bord"),
        ("Cohérence interne", "ok", "chaque bâtiment est ceinturé de pavés et relié au réseau, plus "
                                    "aucune bande pavée orpheline"),
        ("Corrections demandées", "ok", "règle des pavés appliquée, lumière dans la bande, place et "
                                        "mitoyennes à pleine emprise"),
    ],
    "p3-contreforts-v6": [
        ("Échelle humaine", "ok", "bergère, mineur et voyageuse tous petits"),
        ("Aucun animal réel", "ok", "aucun animal réel"),
        ("Fiches respectées", "faute", "les six pattes de SP-016 restent incertaines à l'œil ; "
                                       "SP-005 et SP-007 sont conformes"),
        ("Plan respecté", "ok", "crevasse, enclos, forêt du devant, mine, chariot et tour en place"),
        ("Raccords de bord", "faute", "le sentier de la rangée 8 n'atteint pas le bord gauche : la "
                                      "bergerie et son enclos occupent tout ce côté"),
        ("Cohérence interne", "faute", "la bergerie reste sous ses huit cases et son ouverture est une "
                                       "large baie plutôt qu'une porte percée dans le mur"),
        ("Corrections demandées", "ok", "DE VRAIS PINS enfin obtenus — tronc roux nu, houppier en "
                                        "parasol — et lumière dans la bande"),
    ],
    "p3-contreforts-v5": [
        ("Échelle humaine", "ok", "bergère, mineur et voyageuse sont petits"),
        ("Aucun animal réel", "remarque", "aucun animal réel franc ; les SP-016 approchent le mouton"),
        ("Fiches respectées", "faute", "les SP-016 n'ont que quatre pattes au lieu de six ; SP-005 est "
                                       "rendue en dragonnet"),
        ("Plan respecté", "ok", "crevasse, enclos, forêt du devant, mine, bergerie et tour sont en "
                                "place"),
        ("Raccords de bord", "remarque", "le sentier de la rangée 8 est peu lisible au bord gauche"),
        ("Cohérence interne", "faute", "la bergerie est bien plus petite que ses huit cases et ouverte "
                                       "en hangar au lieu d'être percée d'une porte"),
        ("Corrections demandées", "ok", "crevasse sèche sans fond visible, enclos en murs seuls à "
                                        "intérieur visible, forêt dense traversée par le sentier"),
    ],
    "p4-marais-v8": [
        ("Échelle humaine", "ok", "tourbier, pêcheuse et enfant accroupi tous petits"),
        ("Aucun animal réel", "ok", "aucun animal réel ; SP-009 tient sa forme à quatre pattes"),
        ("Fiches respectées", "faute", "SP-017 apparaît en plusieurs exemplaires alors que la "
                                       "composition n'en liste qu'un"),
        ("Plan respecté", "ok", "huttes, séchoir, mares et réseau de passerelles à leur place"),
        ("Raccords de bord", "ok", "colonne 12 au bord haut et rangée 12 au bord droit"),
        ("Cohérence interne", "ok", "l'escalier de la seconde hutte aboutit sur le tablier de la "
                                    "passerelle, plus une seule marche dans l'eau"),
        ("Corrections demandées", "ok", "lumière dans la bande pour la première fois, escalier "
                                        "corrigé, rappels de taille complets"),
    ],
    "p4-marais-v7": [
        ("Échelle humaine", "ok", "humains petits, standard calibré tenu"),
        ("Aucun animal réel", "ok", "plus aucun poisson, SP-009 conforme"),
        ("Fiches respectées", "ok", "séchoir à récoltes du marais, créatures conformes"),
        ("Plan respecté", "ok", "huttes sur pilotis les pieds dans l'eau"),
        ("Raccords de bord", "remarque", "le raccord droit de la rangée 12 reste à vérifier"),
        ("Cohérence interne", "faute", "un escalier de maison descend dans l'eau"),
        ("Corrections demandées", "ok", "eau claire et verdure abondante conciliées"),
    ],
    "p5-falaise-v4": [
        ("Échelle humaine", "ok", "cinq humains, tous petits"),
        ("Aucun animal réel", "ok", "aucun animal réel"),
        ("Fiches respectées", "remarque", "SP-001 est un peu grand"),
        ("Plan respecté", "ok", "falaise sur tout le bord bas, remontée du bord droit sous la moitié, "
                                "mer en contrebas, passerelle au-dessus de la mer au bord droit"),
        ("Raccords de bord", "ok", "les trois raccords atteignent leur bord"),
        ("Cohérence interne", "faute", "l'escalier taillé n'apparaît pas : le chemin rejoint la "
                                       "passerelle sans marches"),
        ("Corrections demandées", "ok", "géométrie de falaise, phare élancé, inspiration bretonne, "
                                        "peuplement enrichi"),
    ],
    "p6-plage-v5": [
        ("Échelle humaine", "faute", "le pêcheur de l'appontement reste trop grand : à genoux, il "
                                     "occupe presque toute la largeur du tablier"),
        ("Aucun animal réel", "faute", "SP-009 est redevenu poissonneux"),
        ("Fiches respectées", "faute", "SP-017 n'a pas été dessinée ; un ou deux palmiers surnuméraires"),
        ("Plan respecté", "remarque", "bâtiments, dunes et appontement en place, dunes peu marquées"),
        ("Raccords de bord", "ok", "les deux raccords atteignent leur bord sur les bons axes"),
        ("Cohérence interne", "faute", "chemins fantômes : de grands rectangles vides de sable damé"),
        ("Corrections demandées", "remarque", "lumière et massifs littoraux ont progressé, la densité "
                                              "et les chemins n'ont pas suivi"),
    ],
}

CURRENT = ["p1-campagne-v8", "p2-bourg-v7", "p3-contreforts-v6",
           "p4-marais-v8", "p5-falaise-v5", "p6-plage-v5"]


def racine(key: str) -> str:
    return key.rsplit("-v", 1)[0]


def prompt_check(key: str) -> tuple:
    """Run the extended standard check on this one prompt and turn it into a pass or fail."""
    result = subprocess.run([sys.executable, str(HERE / "check-plate-prompts.py"), key],
                            capture_output=True, text=True)
    faults = [line[len("FAULT "):] for line in result.stdout.splitlines()
              if line.startswith("FAULT ")]
    if result.returncode == 0:
        return "ok", "la consigne satisfait le standard courant"

    return "faute", " ; ".join(fault.split(": ", 1)[-1] for fault in faults) or "contrôle en échec"


def mecanique(key: str) -> list:
    path = ASSETS / f"planche-{key}.png"
    if not path.is_file():
        return [("Image produite", "faute", "aucune image pour cette clé", "", "")]
    m = measure(path)
    bas, haut, note = CHARGE.get(racine(key), (55.0, 85.0, ""))
    controles = [
        ("Luminance", "ok" if LUMINANCE_MIN <= m["luminance"] <= LUMINANCE_MAX else "faute",
         f"{m['luminance']:.1f}", f"{LUMINANCE_MIN:.0f} à {LUMINANCE_MAX:.0f}", ""),
        ("Part sombre", "ok" if m["part_sombre"] <= DARK_MAX else "faute",
         f"{m['part_sombre']:.1f} %", f"au plus {DARK_MAX:.0f} %", ""),
        ("Charge visuelle", "ok" if bas <= m["cases_chargees"] <= haut else "faute",
         f"{m['cases_chargees']:.1f} %", f"{bas:.0f} à {haut:.0f} % pour ce biome", note),
        ("Saturation", "ok" if m["saturation"] >= SATURATION_MIN else "faute",
         f"{m['saturation']:.1f} %", f"au moins {SATURATION_MIN:.0f} %, référence "
         f"{REFERENCE['saturation']:.0f} %", ""),
        ("Détail de surface", "ok" if m["energie_moyenne"] >= 20.0 else "faute",
         f"{m['energie_moyenne']:.1f}", f"référence {REFERENCE['energie_moyenne']:.1f}", ""),
        ("Format", "ok" if m["taille"] == "1536x1152" else "faute", m["taille"], "1536x1152", ""),
    ]
    verdict, detail = prompt_check(key)
    controles.append(("Contrôle de la consigne", verdict, detail, "standard courant", ""))

    return controles


def build(key: str) -> dict:
    controles = mecanique(key)
    observations = CRITIQUE.get(key, [])
    # A remark is neither a pass nor a fail: it informs without counting.
    notes = [c[1] for c in controles] + [o[1] for o in observations]
    total = sum(1 for note in notes if note in ("ok", "faute"))
    reussis = sum(1 for note in notes if note == "ok")

    return {
        "cle": key,
        "score": {"reussis": reussis, "total": total},
        "mecanique": [{"nom": n, "verdict": v, "mesure": mes, "cible": c, "note": note}
                      for n, v, mes, c, note in controles],
        "critique": [{"nom": n, "verdict": v, "note": note} for n, v, note in observations],
    }


def markdown(rapport: dict) -> str:
    marque = {"ok": "réussi", "faute": "ÉCHEC", "remarque": "remarque"}
    lignes = [f"# Rapport — {rapport['cle']}", "",
              f"**Score : {rapport['score']['reussis']} contrôles réussis sur "
              f"{rapport['score']['total']}.**", "",
              "## Vérification mécanique", "",
              "| Contrôle | Résultat | Mesure | Cible | Lecture |", "|---|---|---|---|---|"]
    for c in rapport["mecanique"]:
        lignes.append(f"| {c['nom']} | {marque[c['verdict']]} | {c['mesure']} | {c['cible']} | "
                      f"{c['note']} |")
    lignes += ["", "## Passe critique", "", "| Observation | Résultat | Détail |", "|---|---|---|"]
    for o in rapport["critique"]:
        lignes.append(f"| {o['nom']} | {marque[o['verdict']]} | {o['note']} |")

    return "\n".join(lignes) + "\n"


keys = sys.argv[1:] or CURRENT
for key in keys:
    rapport = build(key)
    (ASSETS / f"rapport-{key}.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    (ASSETS / f"rapport-{key}.md").write_text(markdown(rapport), encoding="utf-8")
    print(f"OK rapport-{key}: {rapport['score']['reussis']}/{rapport['score']['total']}")
print(f"{len(keys)} rapport(s) écrit(s)")
