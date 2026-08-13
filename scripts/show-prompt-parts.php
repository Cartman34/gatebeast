<?php
/**
 * USAGE
 *   php scripts/show-prompt-parts.php <consigne.txt> — le sommaire de la consigne : un bloc par ligne, avec le niveau qui l'a écrit et son titre.
 *   php scripts/show-prompt-parts.php <consigne.txt> --grep "<phrase>" — d'où vient cette phrase : les blocs qui la portent, et donc où se corrige ce qu'elle dit.
 *   php scripts/show-prompt-parts.php <consigne.txt> --level common — ne montrer que les blocs d'un niveau. Les niveaux sont des identifiants, donc anglais :
 *   common, type, variant, description, composed, call.
 *   php scripts/show-prompt-parts.php <consigne.txt> -v|--verbose — le texte entier de chaque bloc montré, et pas seulement sa première ligne.
 *   php scripts/show-prompt-parts.php -h|--help — ce texte, et rien n'est lu.
 *
 *   Le fichier attendu est une consigne assemblée — le brouillon sous var/tmp/consignes/, ou la consigne figée à côté d'un maître sous assets/. Son découpage
 *   se lit dans le « .parts.json » voisin, écrit en même temps qu'elle par scripts/generate-sprite.py.
 *
 * INTENTION
 *   QUAND UNE IMAGE REVIENT FAUSSE, LA QUESTION UTILE N'EST PAS « QUE DIT LA CONSIGNE » MAIS « QUEL NIVEAU A ÉCRIT CETTE PHRASE » (opérateur, 2026-08-13). C'est
 *   elle qui décide où porter le correctif, et se tromper coûte une génération à chaque fois : une clause corrigée à la description du sujet alors qu'elle venait du
 *   socle revient identique à la version suivante, et sur tous les autres sujets en plus. L'origine se devinait jusqu'ici en relisant le code qui assemble.
 *
 *   IL NE FAIT CONFIANCE À RIEN, ET C'EST TOUT SON INTÉRÊT. Un découpage qui a vieilli attribuerait des phrases au mauvais niveau sans que rien ne le signale —
 *   soit exactement la faute qu'il existe pour empêcher, en pire, puisqu'elle porterait l'autorité d'un outil. Trois contrôles avant d'afficher quoi que ce
 *   soit : l'empreinte du texte, le pavage des blocs bord à bord sur toute la consigne, et le titre relu dans le texte à la place que le découpage annonce.
 *   Un seul en défaut et la commande refuse, en disant comment refaire le découpage.
 */

$root = dirname(__DIR__);
require_once __DIR__ . '/Tools.php';

Tools::get()->helpIfAsked($argv, __FILE__);

/** Les deux profondeurs de titre. Elles valent celles de generate-sprite.py (GROUP_MARK, GROUPED_MARK) et doivent bouger avec elles. */
const GROUP_MARK = '## ';
const GROUPED_MARK = '### ';

/**
 * Les lignes de titre qui ouvrent un bloc, telles qu'elles sont ÉCRITES dans la consigne : le titre de son groupe quand il l'ouvre, puis le sien, suivi entre
 * parenthèses du niveau qui l'a écrit. Une section seule n'a pas de groupe et s'écrit d'un cran moins profond.
 *
 * Le niveau est donc dit deux fois — dans le texte que le générateur lit, et dans le découpage à côté — et c'est délibéré : deux énoncés du même fait qu'une
 * commande peut comparer attrapent une divergence qu'aucun des deux ne montrerait seul. Reconstruit ici plutôt que relu, pour que la comparaison porte.
 */
function headingOf(array $part, ?array $previous): string
{
    if ($part['group'] === null) {
        return GROUP_MARK . $part['title'] . ' (' . $part['level'] . ")\n";
    }
    // Le titre du groupe appartient au premier de ses blocs, et à lui seul : c'est ce qui garde le pavage plat, avec une seule somme à contrôler.
    $opens = $previous === null || ($previous['group'] ?? null) !== $part['group'];

    return ($opens ? GROUP_MARK . $part['group'] . "\n" : '') . GROUPED_MARK . $part['title'] . ' (' . $part['level'] . ")\n";
}

/** Le format que le fichier de découpage déclare. Un fichier qui ne le porte pas n'est pas un découpage, quel que soit son nom. */
const PARTS_FORMAT = 'gatebeast-prompt-parts';

/** Le geste qui répare, nommé dans chaque refus : sans lui, le lecteur sait qu'il est bloqué et pas comment en sortir. */
function howToRebuild(string $prompt): string
{
    return "Solution — refais le découpage en réassemblant la consigne : « python3 scripts/generate-sprite.py <SUJET> <VARIANTE> » sans --generate (elle "
        . "n'engage aucune image), ou « bash scripts/diff-prompts.sh » pour toutes. Le découpage attendu est « " . $prompt . " ».";
}

/**
 * Le découpage d'une consigne, relu et éprouvé — jamais rendu sur parole.
 *
 * Les trois contrôles sont cumulatifs et aucun ne remplace les autres : l'empreinte dit que c'est bien CE texte-là, le pavage dit qu'aucun caractère n'échappe
 * à un bloc ni n'appartient à deux, et le titre relu dans le texte dit que les décalages désignent réellement les blocs annoncés.
 */
function partsOf(string $promptPath): array
{
    // LE DÉCOUPAGE DONNÉ À LA PLACE DE LA CONSIGNE EST ACCEPTÉ, PAS REFUSÉ : les deux fichiers sont voisins et portent le même nom, se tromper de l'un pour
    // l'autre est la faute de frappe évidente, et refuser aurait demandé de retaper un chemin que la commande sait déduire.
    if (str_ends_with($promptPath, '.parts.json')) {
        $promptPath = substr($promptPath, 0, -strlen('.parts.json')) . '.txt';
    }
    if (!is_file($promptPath)) {
        throw new RuntimeException("FAULT « {$promptPath} » n'existe pas.\n  Solution — donne le chemin d'une consigne assemblée : un brouillon sous "
            . "var/tmp/consignes/, ou la consigne figée à côté d'un maître sous assets/.");
    }
    $partsPath = preg_replace('/\.txt$/', '', $promptPath) . '.parts.json';
    if (!is_file($partsPath)) {
        throw new RuntimeException("FAULT la consigne « {$promptPath} » n'a pas de découpage à côté d'elle : « {$partsPath} » est absent. Les consignes "
            . "assemblées avant que le découpage existe n'en portent pas, et cela ne se rattrape pas en l'inventant.\n  " . howToRebuild($partsPath));
    }
    $body = file_get_contents($promptPath);
    $split = json_decode(file_get_contents($partsPath), true, 512, JSON_THROW_ON_ERROR);
    if (($split['format'] ?? null) !== PARTS_FORMAT) {
        throw new RuntimeException("FAULT « {$partsPath} » ne déclare pas le format " . PARTS_FORMAT . " — ce n'est pas un découpage de consigne.\n  "
            . howToRebuild($partsPath));
    }

    $expected = 'sha256:' . hash('sha256', $body);
    if (($split['fingerprint'] ?? '') !== $expected) {
        throw new RuntimeException("FAULT le découpage ne correspond plus à cette consigne : il porte l'empreinte d'un autre texte. La consigne a été "
            . "réassemblée depuis, et attribuer ses phrases d'après ce découpage les rattacherait au mauvais niveau.\n  " . howToRebuild($partsPath));
    }
    $offset = 0;
    foreach ($split['parts'] as $rank => $part) {
        if ($part['offset'] !== $offset) {
            throw new RuntimeException("FAULT le découpage ne pave pas la consigne : le bloc « {$part['title']} » commence à l'octet {$part['offset']} "
                . "alors que le précédent s'arrête à {$offset}. Un trou ou un recouvrement veut dire qu'un morceau de texte n'appartient à aucun niveau, ou "
                . "à deux.\n  " . howToRebuild($partsPath));
        }
        $opening = headingOf($part, $rank > 0 ? $split['parts'][$rank - 1] : null);
        if (substr($body, $part['offset'], strlen($opening)) !== $opening) {
            throw new RuntimeException("FAULT le bloc de rang {$rank} devrait s'ouvrir par « " . rtrim($opening) . " » et le texte dit autre chose à cet "
                . "endroit — le découpage et la consigne ne s'accordent plus, ni sur les blocs ni sur le niveau qui les a écrits.\n  "
                . howToRebuild($partsPath));
        }
        $offset += $part['length'];
    }
    if ($offset !== strlen($body)) {
        throw new RuntimeException("FAULT le découpage recouvre {$offset} octets pour une consigne qui en fait " . strlen($body) . " : la fin de la "
            . "consigne n'appartient à aucun bloc.\n  " . howToRebuild($partsPath));
    }

    return [$body, $split['parts']];
}

/** Un texte complété jusqu'à une largeur de colonne, comptée en caractères affichés et non en octets. */
function padded(string $text, int $width): string
{
    return $text . str_repeat(' ', max(0, $width - mb_strlen($text)));
}

/** Le contenu d'un bloc, ses lignes de titre retirées — c'est ce que le générateur lit sous ce titre, et rien d'autre. */
function contentOf(string $body, array $part, ?array $previous): string
{
    $whole = substr($body, $part['offset'], $part['length']);

    return substr($whole, strlen(headingOf($part, $previous)));
}

$arguments = array_slice($argv, 1);
$verbose = in_array('-v', $arguments, true) || in_array('--verbose', $arguments, true);
$arguments = array_values(array_filter($arguments, static fn($token) => $token !== '-v' && $token !== '--verbose'));
$wanted = null;
$level = null;
$promptPath = null;
for ($index = 0; $index < count($arguments); $index++) {
    if ($arguments[$index] === '--grep') {
        $wanted = $arguments[++$index] ?? null;
    } elseif ($arguments[$index] === '--level') {
        $level = $arguments[++$index] ?? null;
    } else {
        $promptPath = $arguments[$index];
    }
}
if ($promptPath === null) {
    Tools::get()->helpIfAsked(['--help'], __FILE__);
}
if ($wanted === '' || $level === '') {
    throw new RuntimeException("FAULT --grep et --level attendent une valeur.\n  Solution — « --grep \"une phrase de la consigne\" » ou « --level common ».");
}

[$body, $parts] = partsOf($promptPath);

$levels = [];
foreach ($parts as $part) {
    $levels[$part['level']] = true;
}
if ($level !== null && !isset($levels[$level])) {
    throw new RuntimeException("FAULT aucun bloc de cette consigne n'est du niveau « {$level} ».\n  Solution — les niveaux qu'elle porte sont : "
        . implode(', ', array_keys($levels)) . '.');
}

$shown = 0;
$lines = [];
$announced = null;
foreach ($parts as $rank => $part) {
    $content = contentOf($body, $part, $rank > 0 ? $parts[$rank - 1] : null);
    if ($level !== null && $part['level'] !== $level) {
        continue;
    }
    if ($wanted !== null && !str_contains($content, $wanted)) {
        continue;
    }
    $shown++;
    // LE GROUPE S'ANNONCE UNE FOIS ET LES SIENS S'INDENTENT DESSOUS, mais avec --grep il s'écrit sur la ligne même du bloc : on ne cherche alors qu'une phrase,
    // et un titre de groupe posé seul au-dessus d'un résultat isolé se lit comme un second résultat. « groupe › sous-section » répond aux deux questions d'un
    // coup — de quoi ça parle, et où porter le correctif.
    if ($wanted === null && $part['group'] !== null && $part['group'] !== $announced) {
        $lines[] = padded('', 12) . ' ' . $part['group'];
    }
    $announced = $part['group'];
    $shownTitle = $wanted !== null && $part['group'] !== null ? $part['group'] . ' › ' . $part['title'] : $part['title'];
    $indent = $wanted === null && $part['group'] !== null ? '  ' : '';
    $first = strtok(trim($content), "\n");
    // Aligné sur la largeur AFFICHÉE, pas sur le nombre d'octets : « description » et « Caméra » pèsent plus d'octets qu'ils ne prennent de colonnes, et
    // sprintf compte les octets — les colonnes se décalaient d'un cran sur chaque ligne accentuée.
    $lines[] = padded($part['level'], 12) . ' ' . padded($indent . $shownTitle, 46) . ' '
        . ($verbose ? '' : mb_strimwidth((string) $first, 0, 78, '…'));
    if ($verbose) {
        $lines[] = rtrim($content) . "\n";
    }
}

echo implode("\n", $lines), "\n";
if ($wanted !== null && $shown === 0) {
    // Ne rien trouver n'est pas une panne, mais se taire ferait passer « absente » pour « trouvée quelque part » — et c'est sur cette phrase-là qu'on allait
    // porter un correctif.
    echo "AUCUN BLOC ne porte cette phrase — elle ne vient donc pas de cette consigne.\n",
         "  Solution — vérifie la casse et les accents, ou cherche un fragment plus court : la comparaison est exacte.\n";
    exit(1);
}
printf("%d bloc(s) sur %d\n", $shown, count($parts));
