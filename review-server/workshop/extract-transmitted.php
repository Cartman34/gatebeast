<?php
/**
 * USAGE
 *   php review-server/workshop/extract-transmitted.php <SUJET> <rang> — extrait du journal du générateur la ou les consignes qu'il a transmises à son modèle
 *   d'images, et les écrit en « <SUJET>.v<rang>.transmitted.txt » à côté de la version.
 *   php review-server/workshop/extract-transmitted.php -h|--help — ce texte.
 *
 * INTENTION
 *   LE GÉNÉRATEUR RAPPORTE SA CONSIGNE, ET PERSONNE NE LA RAMASSAIT. La clause « Ce que tu nous rapportes » lui demande de terminer par le texte exact qu'il a
 *   envoyé à son propre modèle, entre deux marqueurs. Il obéit — c'est dans son journal —, mais rien n'extrayait ce texte, si bien que la page d'atelier
 *   affichait « l'agent ne l'a pas rapportée », ce qui était faux, et que le cœur de la page — comparer notre texte au sien — n'a jamais pu fonctionner.
 *
 *   IL LES PREND TOUTES, DANS L'ORDRE. L'agent travaille en plusieurs passes ; la clause réclame chacune d'elles, et les rendre toutes est le seul moyen de
 *   distinguer la passe qui a dessiné de celle qui a détouré.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/scripts/Tools.php';
require_once $root . '/review-server/lib/Prompts.php';

Tools::get()->helpIfAsked($argv, __FILE__);

const OPENS = '<<<CONSIGNE-TRANSMISE-DEBUT>>>';
const CLOSES = '<<<CONSIGNE-TRANSMISE-FIN>>>';

$subject = $argv[1] ?? null;
$rank = $argv[2] ?? null;
if ($subject === null || $rank === null) {
    fwrite(STDERR, "USAGE : php review-server/workshop/extract-transmitted.php <SUJET> <rang>\n");
    exit(2);
}
$rank = ltrim((string) $rank, 'vV');

// LE NOM DU JOURNAL A CHANGÉ AVEC LA CHAÎNE, et les anciens sont encore là : on essaie les formes connues plutôt que d'en imposer une qui effacerait le passé.
$journal = null;
foreach (["$subject.v$rank.image", "$subject.v$rank", $subject] as $stem) {
    $path = "$root/var/generations/sprites/$stem-generateur.jsonl";
    if (is_file($path)) {
        $journal = $path;
        break;
    }
}
if ($journal === null) {
    fwrite(STDERR, "FAULT aucun journal de générateur pour « $subject » v$rank sous var/generations/sprites/.\n"
        . "  Solution — vérifier que cette version a bien été générée.\n");
    exit(1);
}

/** Toutes les chaînes que porte un événement, à n'importe quelle profondeur : le marqueur peut vivre dans un message, un résumé ou une sortie de commande. */
function strings(mixed $value): array
{
    if (is_string($value)) {
        return [$value];
    }
    if (!is_array($value)) {
        return [];
    }
    $found = [];
    foreach ($value as $item) {
        $found = [...$found, ...strings($item)];
    }

    return $found;
}

$blocks = [];
foreach (file($journal, FILE_IGNORE_NEW_LINES) as $line) {
    $event = json_decode($line, true);
    if ($event === null) {
        continue;
    }
    foreach (strings($event) as $text) {
        $at = 0;
        while (($opens = strpos($text, OPENS, $at)) !== false) {
            $closes = strpos($text, CLOSES, $opens);
            if ($closes === false) {
                break;
            }
            $blocks[] = trim(substr($text, $opens + strlen(OPENS), $closes - $opens - strlen(OPENS)));
            $at = $closes + strlen(CLOSES);
        }
    }
}
// LE MÊME BLOC PEUT PARAÎTRE DEUX FOIS dans le journal — l'événement de l'agent et son écho —, et deux copies identiques ne sont pas deux passes.
$blocks = array_values(array_unique($blocks));

if ($blocks === []) {
    fwrite(STDERR, "FAULT le journal « " . basename($journal) . " » ne porte aucune consigne transmise entre ses marqueurs.\n"
        . "  Solution — vérifier que la clause « Ce que tu nous rapportes » était bien dans la consigne de cette version.\n");
    exit(1);
}

$prompts = Prompts::get();
if (!is_dir($prompts->homeOf($subject))) {
    fwrite(STDERR, "FAULT le sujet « $subject » n'a pas de foyer sous " . Prompts::HOME . "/, et rien ne s'écrit à côté d'un dossier absent.\n");
    exit(1);
}
$target = $prompts->file($subject, (int) $rank, 'transmitted');
$written = count($blocks) === 1
    ? $blocks[0] . "\n"
    : implode("\n", array_map(fn (int $rank, string $block) => "===== PASSE " . ($rank + 1) . " =====\n$block\n", array_keys($blocks), $blocks));
file_put_contents($target, $written);

printf("%s — %d consigne(s) transmise(s) extraite(s) de %s, %d caractères.\n",
    basename($target), count($blocks), basename($journal), strlen($written));
