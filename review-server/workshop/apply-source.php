<?php
/**
 * USAGE
 *   php review-server/workshop/apply-source.php <SUJET> <bloc> — writes the next version of a consigne, its section replaced by what the source block prescribes.
 *   php review-server/workshop/apply-source.php -h|--help — this text.
 *
 * INTENTION
 *   UNE SOURCE QUI NE S'APPLIQUE PAS N'EST PAS UNE SOURCE. `review-server/workshop/source/projection.md` définit la projection et porte la clause exacte que le
 *   générateur doit lire ; tant que cette clause est recopiée à la main dans une version, les deux divergent au premier changement et l'on retombe sur ce que
 *   toute cette organisation existe pour supprimer. Ce script est le seul chemin entre la source et une version.
 *
 *   IL REMPLACE UNE SECTION ENTIÈRE, JAMAIS DES MORCEAUX. Une section de la consigne va de son titre au titre suivant ; c'est cette étendue-là que la clause du
 *   bloc remplace, d'un bloc. Substituer phrase à phrase laisserait des restes de l'ancienne rédaction entre les nouvelles, et c'est exactement ainsi que la
 *   consigne s'est mise à dire deux fois la même chose dans deux styles.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';
require_once $root . '/review-server/lib/Consignes.php';

Tools::get()->helpIfAsked($argv, __FILE__);

$subject = $argv[1] ?? null;
$wanted = $argv[2] ?? null;
if ($subject === null || $wanted === null) {
    fwrite(STDERR, "USAGE : php review-server/workshop/apply-source.php <SUJET> <bloc>\n");
    exit(2);
}

$consignes = Consignes::get();
$home = $consignes->homeOf($subject);
if (!is_dir($home)) {
    fwrite(STDERR, "FAULT le sujet « $subject » n'a pas de foyer sous " . Consignes::HOME . "/.\n");
    exit(1);
}

// LE BLOC EST CHERCHÉ PAR SON NOM DÉCLARÉ, jamais par son nom de fichier : c'est l'en-tête qui fait foi, et lui seul est contrôlé par check-source.php.
$block = null;
foreach (glob("$root/review-server/workshop/source/*.md") ?: [] as $path) {
    $text = file_get_contents($path);
    if (!preg_match('/<!--\s*\n(.*?)\n-->/s', $text, $header) || !preg_match('/^\s*bloc\s*:\s*(\S+)/m', $header[1], $named)) {
        continue;
    }
    if ($named[1] !== $wanted) {
        continue;
    }
    if (!preg_match('/^```consigne\n(.*?)^```$/ms', $text, $clause)) {
        fwrite(STDERR, "FAULT le bloc « $wanted » ne porte pas de clause « ```consigne ».\n");
        exit(1);
    }
    preg_match('/^\s*titre\s*:\s*(.+?)\s*$/m', $header[1], $title);
    preg_match('/^\s*niveau\s*:\s*(.+?)\s*$/m', $header[1], $level);
    preg_match('/^\s*apres\s*:\s*(.+?)\s*$/m', $header[1], $after);
    $block = ['titre' => $title[1] ?? null, 'niveau' => $level[1] ?? null, 'apres' => $after[1] ?? null,
        'clause' => rtrim($clause[1], "\n")];
}
if ($block === null) {
    fwrite(STDERR, "FAULT aucun bloc de source ne se nomme « $wanted ».\n");
    exit(1);
}

// THERE IS ONLY EVER ONE PENDING VERSION, and `Consignes` names it: the one that follows the last GENERATED. The computation lives there because the page and
// this script must name the same one, and two loops written side by side end up disagreeing.
if ($consignes->ranksOf($subject) === []) {
    fwrite(STDERR, "FAULT le sujet « $subject » ne porte aucune version.\n");
    exit(1);
}
$generated = $consignes->generatedRank($subject);
$rank = $consignes->pendingRank($subject);
$target = $consignes->file($subject, $rank, 'prompt');
// La source est la version en attente si elle existe déjà — on la reprend —, sinon la dernière générée, dont elle sera le premier écart.
$source = is_file($target) ? $target : $consignes->file($subject, $generated, 'prompt');
$body = file_get_contents($source);

// LA SECTION VA DE SON TITRE AU TITRE SUIVANT, quel qu'en soit le niveau de titre : c'est le découpage que la consigne annonce elle-même dans sa première
// section, et le seul qui ne dépende d'aucune convention inventée ici.
$heading = sprintf('### %s (%s)', $block['titre'], $block['niveau']);
$opens = strpos($body, $heading . "\n");
if ($opens === false) {
    // LA SECTION PEUT NE PAS ENCORE EXISTER, et le bloc dit alors derrière laquelle il se pose : c'est ainsi que la lumière est sortie de la clause de caméra,
    // où elle vivait sans lui appartenir. Sans ce « apres », un bloc neuf n'aurait aucune place et il faudrait l'insérer à la main — donc au hasard.
    if ($block['apres'] === null) {
        fwrite(STDERR, "FAULT la « v$rank » ne porte pas la section « $heading », et le bloc ne déclare pas « apres ».\n");
        exit(1);
    }
    if (!preg_match('/^### ' . preg_quote($block['apres'], '/') . ' \(\w+\)$/m', $body, $found, PREG_OFFSET_CAPTURE)) {
        fwrite(STDERR, "FAULT la section « {$block['apres']} », derrière laquelle ce bloc se pose, est absente de la « v$rank ».\n");
        exit(1);
    }
    $behind = $found[0][1] + strlen($found[0][0]) + 1;
    $stops = preg_match('/^#{2,3} /m', $body, $end, PREG_OFFSET_CAPTURE, $behind) ? $end[0][1] : strlen($body);
    $written = substr($body, 0, $stops) . "$heading\n" . $block['clause'] . "\n" . substr($body, $stops);
    file_put_contents($target, $written);
    printf("%s — section « %s » CRÉÉE derrière « %s » depuis le bloc « %s » (%d caractères).\n",
        basename($target), $block['titre'], $block['apres'], $wanted, strlen($written));
    exit(0);
}
$from = $opens + strlen($heading) + 1;
$next = preg_match('/^#{2,3} /m', $body, $found, PREG_OFFSET_CAPTURE, $from) ? $found[0][1] : strlen($body);

$written = substr($body, 0, $from) . $block['clause'] . "\n" . substr($body, $next);
file_put_contents($target, $written);

printf("%s — section « %s » remplacée par le bloc « %s » (%d caractères).\n", basename($target), $block['titre'], $wanted, strlen($written));
