<?php
/**
 * USAGE
 *   php scripts/dev/probe-form-kept.php — proves the pile artefact keeps a comment across loads: it plants one in the browser's storage before the page opens,
 *   then types another and reads what the storage holds. Reports both.
 *   php scripts/dev/probe-form-kept.php -h|--help — this text
 *
 * INTENTION
 *   « LE FORMULAIRE DOIT ÊTRE PRÉSERVÉ D'UN CHARGEMENT À L'AUTRE » (opérateur, 2026-08-12), et cela ne se lit pas dans le code : la moitié qui compte est ce que
 *   le navigateur rend APRÈS avoir relu son stockage. Une remarque retapée à chaque rechargement ne s'écrit pas deux fois — on renonce à l'écrire.
 *
 *   LES DEUX MOITIÉS SE MESURENT ENSEMBLE : restituer sans enregistrer donnerait une page qui montre à jamais le même vieux texte, enregistrer sans restituer
 *   donnerait une page qui perd tout à chaque ouverture. Une sonde qui ne vérifie qu'un sens ne peut pas échouer là où ça compte.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$page = $root . '/var/tmp/pile-artefact.html';
if (!is_file($page)) {
    throw new RuntimeException("FAULT l'artefact de la pile n'est pas construit — lancez php review-server/backlog/build.php var/tmp/pile-artefact.html --artefact.");
}
$html = file_get_contents($page);

// LE STOCKAGE SE REMPLIT AVANT QUE LA PAGE NE LE LISE : c'est le seul moyen de mesurer la restitution sans recharger deux fois.
$planted = 'commentaire planté par la sonde';
$before = "<script>localStorage.setItem('gatebeast-pile', JSON.stringify({'style-page-sprites': {comment: "
    . json_encode($planted) . "}}));</script>";
$probe = "<script>window.addEventListener('load', function () {"
    . "var out = document.body.appendChild(document.createElement('div')); out.id = 'sonde';"
    . "var champ = document.querySelector('.comment[data-id=\"style-page-sprites\"]');"
    . "var autre = document.querySelector('.comment[data-id=\"notes-en-face\"]');"
    . "var rendu = champ ? champ.value : 'CHAMP INTROUVABLE';"
    // La frappe se simule par l'événement que la page écoute vraiment : poser la valeur sans lui ne déclencherait rien, et la sonde mesurerait sa propre pose.
    . "autre.value = 'tapé par la sonde';"
    . "autre.dispatchEvent(new Event('input'));"
    . "setTimeout(function () {"
    . "  var garde = JSON.parse(localStorage.getItem('gatebeast-pile') || '{}');"
    . "  out.textContent = 'RESTITUÉ : [' + rendu + '] || ENREGISTRÉ : ['"
    . "    + ((garde['notes-en-face'] || {}).comment || 'RIEN') + ']';"
    . "}, 900);"
    . "});</script>";

$copy = $root . '/var/tmp/sonde-formulaire.html';
file_put_contents($copy, $before . $html . $probe);
$dom = Browser::get()->dom(ReviewServer::get()->urlFor('/var/tmp/' . basename($copy)), 9000);
if (preg_match('#<div id="sonde">(.*?)</div>#s', $dom, $found)) {
    echo trim($found[1]) . "\n";
    exit(0);
}
throw new RuntimeException("FAULT la sonde n'a rien rapporté — la page ne s'est pas chargée jusqu'au bout : {$copy}");
