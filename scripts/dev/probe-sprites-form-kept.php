<?php
/**
 * USAGE
 *   php scripts/dev/probe-sprites-form-kept.php [-v] [-h] — proves the sprites page keeps what is being typed: it hands the page a store as if it came back from
 *   a reload and reads what the form shows of it, then types a comment character by character and reads what the page would have sent and what it kept locally.
 *   Runs twice — server answering, then server silent — and gives a verdict; `-v` prints both measurements.
 *
 * INTENTION
 *   « Ta page de suivi de sprite a rafraîchi et ça a perdu ce que je notais alors qu'avant ça ne perdait jamais le formulaire et ce que je notais » (opérateur,
 *   2026-08-12). Le comportement tient à quatre mécanismes qui cassent séparément — restituer, enregistrer, n'enregistrer qu'une fois par pause, et garder en
 *   local ce que le serveur n'a pas reçu — et AUCUN ne se lit dans le code : ce qui compte est ce que le navigateur fait des quatre ensemble.
 *
 *   LE PENDANT DE `probe-form-kept.php`, QUI NE COUVRE QUE LA PAGE DE LA PILE. Celle-ci garde ses remarques dans le stockage du navigateur ; la page des sprites
 *   les envoie au serveur ET les double en local, donc les deux moitiés ne se mesurent pas au même endroit et une sonde ne vaut pas pour l'autre.
 *
 *   LE SERVEUR MUET EST LA MOITIÉ QUE PERSONNE NE MESURE : la page répond alors sur son seul filet local, et c'est exactement le cas où l'opérateur a perdu du
 *   texte. Il se simule en faisant répondre le module à vide, jamais en arrêtant le vrai serveur, qui sert la revue pendant ce temps.
 *
 *   ELLE N'ÉCRIT JAMAIS : `save` et `load` sont remplacés AVANT que le script de la page ne s'exécute, donc aucune frappe de cette sonde ne peut atteindre
 *   review-server/notes/sprites.json, qui porte les verdicts de l'opérateur.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Probe.php';
bootBuild();

if (in_array('-h', $argv, true) || in_array('--help', $argv, true)) {
    echo "php scripts/dev/probe-sprites-form-kept.php [-v]\n"
        . "  Vérifie que la page des sprites restitue ce qui est saisi, l'envoie une seule fois par pause, et le garde en local\n"
        . "  tant que le serveur ne l'a pas reçu. -v affiche les deux mesures ; sans lui, le verdict seul.\n";
    exit(0);
}
$verbose = in_array('-v', $argv, true) || in_array('--verbose', $argv, true);

const NET_KEY = 'gatebeast-suivi-sprites-attente';
const PLANTED = 'commentaire planté par la sonde';
const TYPED = 'tapé par la sonde';

/**
 * One run of the page, driven: what it restores, what it would send, what it keeps locally.
 *
 * THE STORE ANSWERS ASYNCHRONOUSLY, like the real one — the page raises its `ready` guard in that callback, and a synchronous answer would hide every fault that
 * depends on the order of the two, which is precisely where text was being lost.
 */
function measure(string $root, bool $mute): array
{
    $html = Probe::get()->page('/sprites');
    $scriptTag = '<script src="/review-server/suivi-sprites/page.js"></script>';
    if (!str_contains($html, $scriptTag)) {
        throw new RuntimeException('FAULT la page ne charge plus son script par la balise attendue — la sonde ne peut pas se placer avant lui.');
    }
    $planted = json_encode(PLANTED);
    $netKey = json_encode(NET_KEY);
    $stub = "<script>window.__sent = [];window.__planted = {$planted};"
        . "var first = document.querySelector('.comment').getAttribute('data-id');"
        . ($mute
            ? "try { var net = {}; net[first] = {approved: false, rework: true, discarded: false, comment: window.__planted};"
                . "localStorage.setItem({$netKey}, JSON.stringify(net)); } catch (error) {}"
            : "try { localStorage.removeItem({$netKey}); } catch (error) {}")
        . "window.gatebeastNotes = {"
        . "  load: function (section, next) {"
        . ($mute
            ? "    window.setTimeout(function () { next([]); }, 30); },"
            : "    var held = {}; held[first] = {approved: true, rework: false, discarded: false, comment: window.__planted};"
                . "    window.setTimeout(function () { next(held); }, 30); },")
        . "  save: function (section, notes) { window.__sent.push(notes); }"
        . "};</script>";

    // LA FRAPPE SE SIMULE CARACTÈRE PAR CARACTÈRE, ET C'EST TOUT L'INTÉRÊT : c'est la rafale qui produisait une requête par touche, donc la course qui tronquait
    // le texte au milieu d'un mot. Une frappe unique ne l'aurait jamais montrée.
    $typed = json_encode(TYPED);
    $probe = "<script>window.addEventListener('load', function () { window.setTimeout(function () {"
        . "  var out = document.body.appendChild(document.createElement('div')); out.id = 'sonde';"
        . "  var field = document.querySelector('.comment');"
        . "  var key = field.getAttribute('data-id');"
        . "  var zone = document.querySelector('.comment-zone[data-more=\"' + key + '\"]');"
        . "  var shown = field.value;"
        . "  var opened = Boolean(zone) && !zone.hidden;"
        . "  var typed = {$typed};"
        . "  for (var rank = 1; rank <= typed.length; rank += 1) {"
        . "    field.value = typed.slice(0, rank);"
        . "    field.dispatchEvent(new Event('input'));"
        . "  }"
        . "  window.setTimeout(function () {"
        . "    var last = window.__sent[window.__sent.length - 1];"
        . "    var net = {}; try { net = JSON.parse(localStorage.getItem({$netKey})) || {}; } catch (error) { net = {}; }"
        . "    out.textContent = JSON.stringify({key: key, restored: shown, opened: opened, strokes: typed.length,"
        . "      sends: window.__sent.length, sent: (last && last[key] ? last[key].comment : null),"
        . "      kept: (net[key] ? net[key].comment : null)});"
        . "  }, 900);"
        . "}, 300); });</script>";

    // LE SERVICE ÉCRIT LA COPIE ET LA FAIT SERVIR — et il y pose sa muselière, qui double le remplacement fait juste au-dessus : ici `save` est remplacé pour être
    // MESURÉ, là toute écriture est refusée au transport. Les deux disent la même chose, et la seconde tient même si la première change de forme.
    $address = Probe::get()->serve(str_replace($scriptTag, $stub . $scriptTag, $html), $probe, 'sonde-sprites-formulaire');
    $dom = Browser::get()->dom($address, 12000);
    if (preg_match('#<div id="sonde">(.*?)</div>#s', $dom, $found) !== 1) {
        throw new RuntimeException("FAULT la sonde n'a rien rapporté — la page ne s'est pas chargée jusqu'au bout : {$address}");
    }

    return json_decode(html_entity_decode(trim($found[1]), ENT_QUOTES), true, 512, JSON_THROW_ON_ERROR);
}

$answering = measure($root, false);
$silent = measure($root, true);

// CE QUI EST ATTENDU, DIT ICI ET PAS AILLEURS. Chaque ligne porte ce qu'elle vaudrait si elle cassait : c'est ce que lit celui qui vient de la casser.
$faults = [];
if ($answering['restored'] !== PLANTED) {
    $faults[] = 'Le dépôt répond et son texte n\'est pas reposé dans le champ : un rechargement montre un champ vide, et l\'opérateur croit sa remarque perdue.';
}
if (!$answering['opened']) {
    $faults[] = 'La zone reste repliée sur une remarque qui existe : un texte qu\'on ne voit pas est un texte perdu pour qui rouvre la page.';
}
if ($answering['sends'] !== 1) {
    $faults[] = sprintf('Une frappe de %d caractères a produit %d envois au lieu d\'un seul : les réponses ne reviennent pas dans l\'ordre, '
        . 'et un instantané de frappe écrit après le texte complet le tronque.', $answering['strokes'], $answering['sends']);
}
if ($answering['sent'] !== TYPED) {
    $faults[] = 'Ce qui part au dépôt n\'est pas ce qui a été tapé : ' . var_export($answering['sent'], true);
}
if ($answering['kept'] !== TYPED) {
    $faults[] = 'Rien n\'est gardé en local pendant la frappe : ce que le dépôt ne reçoit pas n\'existe alors nulle part.';
}
if ($silent['restored'] !== PLANTED) {
    $faults[] = 'Serveur muet : ce que le filet local portait n\'est pas revenu à l\'écran — c\'est exactement le cas où l\'opérateur perd son texte.';
}

if ($verbose) {
    printf("serveur qui répond : %s\n", json_encode($answering, JSON_UNESCAPED_UNICODE));
    printf("serveur muet       : %s\n", json_encode($silent, JSON_UNESCAPED_UNICODE));
}
if ($faults) {
    fwrite(STDERR, count($faults) . " perte(s) sur la saisie de la page des sprites :\n  " . implode("\n  ", $faults) . "\n");
    exit(1);
}
printf("La saisie survit : restituée, envoyée une seule fois par pause, gardée en local, et rendue même quand le serveur ne répond pas.\n");
