<?php
/**
 * USAGE
 *   php review-server/workshop/check-source.php — checks the workshop's source blocks: that each is well formed, and that no two of them speak of the same thing.
 *   php review-server/workshop/check-source.php -h|--help — this text.
 *
 *   Exits 1 on any fault, so it can gate an assembly.
 *
 * INTENTION
 *   LA COHÉRENCE SE TIENT PAR UNE MACHINE, PAS PAR LA VIGILANCE DE CELUI QUI ÉCRIT. La consigne s'est contredite quatre fois de suite sur la même chose — la
 *   projection dite en prose ici, en deux égalités là, en trois unités ailleurs — et chaque agent qui passait comblait ce qu'il croyait manquant en inventant une
 *   quatrième formulation. Aucune relecture n'attrape cela : les trois versions sont individuellement plausibles, et c'est leur coexistence qui est fausse.
 *
 *   CE QUI EST CONTRÔLÉ, ET C'EST LA RÈGLE « UN PARAMÈTRE SE DIT UNE FOIS, À SON NIVEAU » RENDUE MÉCANIQUE : chaque bloc de source déclare les mots qu'il
 *   GOUVERNE, et il est seul à avoir le droit de les employer. Un autre bloc qui parle d'azimut, de point de fuite ou de 96 pixels est refusé par son nom et par
 *   sa ligne — avant qu'une consigne assemblée ne parte au générateur avec deux versions de la même règle.
 *
 *   IL JUGE LA CLAUSE, PAS L'EXPLICATION. Un bloc de source porte les deux : la prose qui explique, destinée à nous, et le bloc « consigne » qui part au
 *   générateur. Deux blocs peuvent expliquer la même chose sans dommage — c'est ce qu'ils PRESCRIVENT qui ne doit jamais se dire deux fois.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

const SOURCE = 'review-server/workshop/source';
const REQUIRED = ['bloc', 'groupe', 'titre', 'niveau', 'gouverne'];
/** The levels a section may declare — the same six the consigne already names, and no seventh is invented here. */
const LEVELS = ['common', 'type', 'variant', 'description', 'parameters', 'call'];

$directory = "$root/" . SOURCE;
$paths = glob("$directory/*.md") ?: [];
if ($paths === []) {
    fwrite(STDERR, "FAULT aucun bloc de source sous « " . SOURCE . " ».\n");
    exit(1);
}

$faults = [];
$blocks = [];
foreach ($paths as $path) {
    $name = basename($path);
    $text = file_get_contents($path);

    if (!preg_match('/<!--\s*\n(.*?)\n-->/s', $text, $found)) {
        $faults[] = "$name — pas d'en-tête. Solution — ouvrir le fichier par un commentaire HTML portant " . implode(', ', REQUIRED) . '.';
        continue;
    }
    $header = [];
    foreach (explode("\n", $found[1]) as $line) {
        if (preg_match('/^\s*(\w+)\s*:\s*(.+?)\s*$/', $line, $pair)) {
            $header[$pair[1]] = $pair[2];
        }
    }
    foreach (REQUIRED as $key) {
        if (!isset($header[$key])) {
            $faults[] = "$name — l'en-tête ne déclare pas « $key ».";
        }
    }
    if (isset($header['niveau']) && !in_array($header['niveau'], LEVELS, true)) {
        $faults[] = "$name — niveau « {$header['niveau']} » inconnu. Les niveaux sont : " . implode(', ', LEVELS) . '.';
    }
    // LA CLAUSE EST OBLIGATOIRE ET UNIQUE : un bloc de source qui n'en porte pas n'assemble rien, et un bloc qui en porte deux laisse choisir l'assembleur.
    $clauses = preg_match_all('/^```consigne\n(.*?)^```$/ms', $text, $all);
    if ($clauses !== 1) {
        $faults[] = "$name — $clauses bloc(s) « ```consigne », il en faut exactement un : c'est lui qui part au générateur.";
        continue;
    }
    $blocks[$name] = ['header' => $header, 'clause' => $all[1][0]];
}

// LE CROISEMENT EST LE CŒUR DU CONTRÔLE : chaque mot gouverné est cherché dans la CLAUSE de tous les autres blocs.
//
// LA LISTE SE SÉPARE PAR DES POINTS-VIRGULES, ET C'EST NÉCESSAIRE : une valeur gouvernée est souvent un nombre, et le français écrit ses décimales avec une
// virgule. Séparée par des virgules, « 5,25 » se coupait en « 5 » et « 25 », qui attrapaient ensuite n'importe quel nombre d'une autre clause.
foreach ($blocks as $name => $block) {
    foreach (array_map('trim', explode(';', $block['header']['gouverne'] ?? '')) as $word) {
        if ($word === '') {
            continue;
        }
        foreach ($blocks as $other => $peer) {
            if ($other === $name) {
                continue;
            }
            // LES FRONTIÈRES DE MOT évitent que « 84 » attrape « 840 ». LA CASSE COMPTE POUR UN MOT ÉCRIT TOUT EN CAPITALES, et c'est nécessaire : les points
            // cardinaux s'écrivent « EST », « OUEST », et cherchés sans la casse ils attrapent le verbe « est » et le mot « ouest » de n'importe quelle prose —
            // la clause de la lumière a été refusée pour cinq « est exposé au ciel ». Un mot en minuscules, lui, se cherche dans les deux casses.
            $sensitive = $word === mb_strtoupper($word) && preg_match('/\p{L}/u', $word);
            if (preg_match('/(?<![\w-])' . preg_quote($word, '/') . '(?![\w-])/u' . ($sensitive ? '' : 'i'), $peer['clause'])) {
                $faults[] = "$other — sa clause emploie « $word », que « $name » gouverne. Solution — retirer la mention, ou déplacer le mot d'un en-tête à l'autre.";
            }
        }
    }
}

// DEUX BLOCS NE PEUVENT PAS OCCUPER LA MÊME PLACE dans la consigne assemblée : le second écraserait le premier sans que rien ne le dise.
$places = [];
foreach ($blocks as $name => $block) {
    $place = ($block['header']['groupe'] ?? '?') . ' › ' . ($block['header']['titre'] ?? '?');
    if (isset($places[$place])) {
        $faults[] = "$name — occupe la même place que « {$places[$place]} » : « $place ».";
    }
    $places[$place] = $name;
}

if ($faults) {
    fwrite(STDERR, count($faults) . " faute(s) dans la source de l'atelier :\n  " . implode("\n  ", $faults) . "\n");
    exit(1);
}

printf("%d bloc(s) de source : en-têtes complets, une clause chacun, et aucun mot gouverné employé deux fois.\n", count($blocks));
