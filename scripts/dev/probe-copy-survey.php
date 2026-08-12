<?php
/**
 * USAGE
 *   php scripts/dev/probe-copy-survey.php — clicks the survey's copy button in the pile artefact and reports what actually happened: what the button says
 *   afterwards, whether the fallback field appeared, and every console message the page emitted.
 *   php scripts/dev/probe-copy-survey.php -h|--help — this text
 *
 * INTENTION
 *   L'OPÉRATEUR DIT QUE LA COPIE NE MARCHE PAS, ET LIRE LE CODE A DÉJÀ DONNÉ TROIS DIAGNOSTICS FAUX EN UNE SOIRÉE sur cette famille de défauts. Un bouton mort est
 *   la signature d'une erreur JavaScript levée avant que son écouteur ne soit posé — le navigateur nomme le fichier et la ligne, le code non.
 *
 *   LA CONSOLE EST RAPPORTÉE AVEC LE RESTE, et c'est le point : si le script a levé au chargement, le bouton n'a jamais eu d'écouteur, et tout le reste de la
 *   mesure ne dirait que « rien ne s'est passé » sans dire pourquoi.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$page = $root . '/var/tmp/pile-artefact.html';
if (!is_file($page)) {
    throw new RuntimeException("FAULT l'artefact de la pile n'est pas construit.");
}

// L'ÉCOUTEUR D'ERREURS SE POSE EN TÊTE DE PAGE, PAS EN QUEUE, ET C'EST LA LEÇON DU 2026-08-12 : posé après, il ne voit pas l'erreur d'analyse du script qu'il
// devait attraper. La sonde a alors rapporté « CONSOLE : rien » sur une page dont le script entier n'avait jamais tourné — un contrôle qui rassure à tort.
$guard = "<script>window.__dits = [];"
    . "window.addEventListener('error', function (e) { window.__dits.push('ERREUR ' + e.message + ' (' + e.filename + ':' + e.lineno + ')'); });</script>";

$probe = "<script>"
    . "window.addEventListener('load', function () {"
    . "  var out = document.body.appendChild(document.createElement('div')); out.id = 'sonde';"
    . "  var bouton = document.querySelector('.releve-copier');"
    . "  if (!bouton) { out.textContent = 'BOUTON INTROUVABLE || ' + window.__dits.join(' | '); return; }"
    . "  var champ = document.querySelector('.comment');"
    . "  if (champ) { champ.value = 'sonde'; champ.dispatchEvent(new Event('input')); }"
    . "  setTimeout(function () {"
    . "    bouton.click();"
    . "    setTimeout(function () {"
    . "      var repli = document.querySelector('.releve-texte');"
    . "      out.textContent = 'BOUTON DIT : [' + bouton.textContent + '] || REPLI : '"
    . "        + (repli ? '[' + repli.value.slice(0, 60) + ']' : 'ABSENT')"
    . "        + ' || CONSOLE : ' + (window.__dits.length ? window.__dits.join(' | ') : 'rien');"
    . "    }, 600);"
    . "  }, 700);"
    . "});</script>";

$copy = $root . '/var/tmp/sonde-copie.html';
file_put_contents($copy, $guard . file_get_contents($page) . $probe);
$dom = Browser::get()->dom(ReviewServer::get()->urlFor('/var/tmp/' . basename($copy)), 9000);
if (preg_match('#<div id="sonde">(.*?)</div>#s', $dom, $found)) {
    echo trim($found[1]) . "\n";
    exit(0);
}
throw new RuntimeException("FAULT la sonde n'a rien rapporté : {$copy}");
