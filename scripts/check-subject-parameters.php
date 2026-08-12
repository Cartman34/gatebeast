<?php
/**
 * USAGE
 *   php scripts/check-subject-parameters.php        the verdict: how many subject sheets leave a parameter of their type unfixed
 *   php scripts/check-subject-parameters.php -v     each sheet with the parameters it never mentions
 *   php scripts/check-subject-parameters.php -h     this text
 *
 * INTENTION
 *   A PARAMETER A SHEET DOES NOT FIX IS A PARAMETER THE GENERATOR CHOOSES, differently at every call, and the reproach made to the image has then no ground. The
 *   closed grid lives in the design — doc/conception/referentiels/visuel/parametres-des-sujets.md — and this reads the sheets against it.
 *
 *   IT SIGNALS, IT NEVER REFUSES, and that is a decision rather than a weakness: refusing would stop production on a sheet written before the grid existed, and
 *   production is what moves the project. What it owes is to make the gap VISIBLE, so it gets filled the next time the sheet is touched.
 *
 *   HOW IT LOOKS, AND WHAT THAT COSTS: each parameter carries the words a sheet uses when it fixes it, and the sheet is searched for any of them. A sheet may
 *   therefore fix a parameter in words nobody listed, and be reported wrongly — the answer is to add the word here, and the check stays useful. The opposite
 *   error, understanding too much, would let a real gap through in silence, which is the one thing a check must never do.
 */

$root = dirname(__DIR__);
$detail = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);
if (in_array('-h', $argv, true) || in_array('--help', $argv, true)) {
    $usage = file($root . '/scripts/check-subject-parameters.php', FILE_IGNORE_NEW_LINES);
    foreach (array_slice($usage, 2, 4) as $line) {
        echo trim(preg_replace('~^\s*\*\s?~', '', $line)), "\n";
    }
    exit(0);
}

/**
 * THE GRID, IN THE WORDS A SHEET USES. The design document holds the parameters and their reasons; what lives here is only how to RECOGNISE that a sheet fixes
 * one — the two are not the same thing, and a sheet is prose, not a form. Nine common parameters first, then what each type adds.
 */
const COMMON = [
    'la matière' => ['pierre', 'bois', 'tuile', 'feuillage', 'eau', 'poil', 'crépi', 'torchis', 'herbe', 'terre', 'écorce', 'rondin', 'galet', 'brin'],
    'la couleur' => ['couleur', 'vert', 'brun', 'gris', 'orange', 'bleu', 'beige', 'jaune', 'rouge', 'blanc', 'ambre', 'clair', 'sombre'],
    'le rapport au sol' => ['sol', 'terre', 'pied', 'sous-bassement', 'soubassement', 'planté', 'posé', 'creus', 'lit', 'enjambe', 'affleur'],
    'ce qui pousse à son pied' => ['herbe', 'mousse', 'touffe', 'fougère', 'ronce', 'lichen', 'aucune herbe', 'rien'],
];
/**
 * WHAT GROWS AT ITS FOOT IS ASKED OF WHAT IS FIXED TO THE GROUND, AND OF NOTHING ELSE. A human and a creature walk: they carry no tuft of grass with them, and
 * asking the question of them was the check crying on what it announces it ignores — the failure that switches a check off.
 */
const ROOTED_ONLY = ['ce qui pousse à son pied'];
const WALKS = ['human', 'creature'];
const BY_TYPE = [
    'ground' => ['le grain de la surface' => ['grain', 'texture', 'brin', 'relief'], 'le raccord bord à bord' => ['bord', 'raccord', 'côte à côte']],
    'path' => ['la largeur du tracé' => ['largeur', 'tiers', 'case de large'], 'aucune épaisseur' => ['épaisseur', 'bombé', 'ombre portée'],
               'les bords longs' => ['bords', 'rongé', 'irrégul'], 'ce qui affleure' => ['caillou', 'trace', 'affleur']],
    'stream' => ['la profondeur du lit' => ['lit', 'creuse', 'retrait', 'profondeur'], 'le courant' => ['courant', 'ride', 'écoulement', 'remous'],
                 'la surface' => ['surface', 'vague', 'reflet'], 'les rives' => ['rive', 'berge', 'galet'], 'le raccord aux bords' => ['bord', 'prolonge', 'raccord']],
    'bridge' => ['la forme de l\'ouvrage' => ['arche', 'tablier', 'ouvrage'], 'l\'appareillage' => ['moellon', 'assise', 'claveau', 'joint'],
                 'les parapets' => ['parapet', 'garde-corps'], 'ce qu\'il enjambe' => ['enjambe', 'eau', 'vide'], 'le raccord aux bords' => ['bord', 'touche', 'raccord']],
    'fence' => ['la hauteur des poteaux' => ['hauteur', 'dixième', 'poteau'], 'les lisses' => ['lisse', 'barre', 'traverse'], 'l\'espacement' => ['espac', 'écart', 'intervalle'],
                'le débord du poteau' => ['dépass', 'débord', 'sommet'], 'la végétation au pied' => ['herbe', 'mousse', 'touffe'], 'le portillon' => ['portillon', 'battant', 'aucun portillon']],
    'building' => ['le programme' => ['abrite', 'sert', 'accueille', 'habitation', 'ferme', 'centre'], 'la volumétrie' => ['corps', 'aile', 'volume', 'pignon'],
                   'les toitures' => ['toit', 'toiture', 'pente', 'versant'], 'les ouvertures' => ['porte', 'fenêtre', 'lucarne', 'ouverture'],
                   'l\'échelle sur la porte' => ['porte', 'case de haut', 'échelle'], 'les matériaux de mur' => ['mur', 'crépi', 'pierre', 'maçonnerie', 'torchis'],
                   'l\'usure, temps et nature' => ['usure', 'usé', 'temps', 'mousse', 'lierre', 'fissure', 'écaill', 'neuf'],
                   'les abords immédiats' => ['seuil', 'bac', 'appentis', 'perron', 'abord']],
    'tree' => ['la couronne' => ['couronne', 'houppier', 'masse', 'feuillage'], 'couronne contre pied' => ['pied', 'tronc', 'largeur', 'fois'],
               'le tronc' => ['tronc', 'fût', 'évase'], 'la feuille' => ['feuille', 'lobée', 'aiguille', 'ton'], 'ce qu\'il porte' => ['fruit', 'fleur', 'pomme', 'aucun fruit']],
    'grove' => ['le nombre d\'arbres' => ['trois', 'quatre', 'arbres', 'sapins'], 'la bande de troncs' => ['tronc', 'fût', 'dixième'],
                'le sous-bois' => ['sous-bois', 'fougère', 'ronce', 'buisson'], 'l\'aération' => ['aéré', 'espacé', 'trouée', 'ombre'],
                'le raccord aux bords' => ['bord', 'rejoign', 'continu']],
    'grass' => ['la hauteur des brins' => ['hauteur', 'genou', 'haute', 'rase'], 'le port' => ['arqu', 'dressé', 'retomb', 'courbé'],
                'la densité' => ['densité', 'dense', 'clairsem', 'serré'], 'ce qui la ponctue' => ['épi', 'fleur', 'sec', 'blanchi']],
    'human' => ['la morphologie' => ['carrure', 'silhouette', 'morpholog', 'âge', 'adulte'], 'l\'origine' => ['peau', 'carnation', 'cheveux', 'origine'],
                'le vêtement' => ['veste', 'pantalon', 'tee-shirt', 'botte', 'vêtement', 'tunique'], 'ce qu\'il porte' => ['sac', 'porte', 'main', 'rien en main'],
                'la posture' => ['debout', 'appui', 'assis', 'posture'], 'la vue selon l\'orientation' => ['orientation', 'profil', 'dos', 'face']],
    'creature' => ['l\'espèce et sa silhouette' => ['silhouette', 'espèce', 'corps'], 'la taille en cases' => ['case', 'taille', 'haut'],
                   'le pelage' => ['pelage', 'poil', 'fourrure', 'peau', 'écaille'], 'les traits distinctifs' => ['oreille', 'queue', 'museau', 'patte', 'œil'],
                   'la posture' => ['debout', 'assis', 'posture', 'dressé'], 'la vue selon l\'orientation' => ['orientation', 'profil', 'dos', 'face']],
];

$referential = json_decode(file_get_contents($root . '/assets/subjects.json'), true, 512, JSON_THROW_ON_ERROR);
$gaps = [];
$read = 0;
foreach ($referential['subjects'] as $code => $subject) {
    $sheet = $root . '/assets/descriptions/' . $code . '.md';
    if (!is_file($sheet)) {
        $gaps[$code] = ['AUCUNE FICHE — ce sujet n\'a pas de description'];
        continue;
    }
    $read++;
    $text = mb_strtolower((string) file_get_contents($sheet));
    $missing = [];
    foreach (array_merge(COMMON, BY_TYPE[$subject['type']] ?? []) as $parameter => $words) {
        if (in_array($parameter, ROOTED_ONLY, true) && in_array($subject['type'], WALKS, true)) {
            continue;
        }
        foreach ($words as $word) {
            if (str_contains($text, mb_strtolower($word))) {
                continue 2;
            }
        }
        $missing[] = $parameter;
    }
    if ($missing) {
        $gaps[$code] = $missing;
    }
}

$total = array_sum(array_map('count', $gaps));
printf("%d fiche(s) lue(s) : %d laissent %d paramètre(s) de leur type non fixé(s).\n", $read, count($gaps), $total);
if ($detail) {
    foreach ($gaps as $code => $missing) {
        printf("\n%s — %s\n", $code, $referential['subjects'][$code]['type'] ?? '?');
        foreach ($missing as $parameter) {
            printf("  %s\n", $parameter);
        }
    }
} elseif ($gaps) {
    echo "« -v » les nomme.\n";
}

// IT NEVER REFUSES: the exit code says « something is missing » for whoever wants to test it, and blocks nobody. The design says why.
exit(0);
