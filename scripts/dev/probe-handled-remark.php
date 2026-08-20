<?php
/**
 * USAGE
 *   php scripts/dev/probe-handled-remark.php — loads the served sprites page, waits for the stored verdicts to come back, and reports three things: a pending
 *   remark on a current version, and — for a version whose predecessor was commented — what the current card announces of it.
 *   php scripts/dev/probe-handled-remark.php -h|--help — this text
 *
 * INTENTION
 *   A remark that has been dealt with must leave the interface while staying in the store (operator, 2026-08-11), AND must stay findable there (same operator,
 *   same day: « je dois pouvoir retrouver les commentaires d'une version dans l'interface »). The two together are the whole rule, and only the page can answer:
 *   the state is fetched from the server after the page opens, so reading the code shows nothing.
 *
 *   THE PAIR IT USED TO NAME HAD DRIFTED, and the probe went on printing a verdict about it: it called SP-001 « filed » when the store holds neither a comment
 *   nor a filing for it, and asked for BT-001-v11, a version no longer current, whose field simply does not exist any more. A probe naming a state that has moved
 *   answers a question nobody is asking — so what it names is now what the store actually holds, and it says so when it finds nothing.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Probe.php';
bootBuild();

require_once dirname(__DIR__) . '/Tools.php';
Tools::get()->helpIfAsked($argv, __FILE__);

$html = Probe::get()->page('/sprites');

// The images are named rather than discovered: the probe answers a question about THESE states, and a discovered set would silently change meaning the day their
// verdicts change. They are the ones the store actually holds — a pending remark on a current version, and a current version whose predecessor was commented then
// filed.
// AUCUNE REMARQUE EN ATTENTE NE PORTE AUJOURD'HUI SUR UNE VERSION COURANTE — toutes celles du dépôt ont été reprises depuis, ce qui est précisément la situation
// que l'annonce ci-dessous existe pour rendre lisible. Le cas « en attente » se rabat donc sur une version courante sans commentaire : il ne prouve plus qu'un
// texte s'affiche, il prouve que la boîte d'une carte courante est là, ouverte à l'écriture, et non verrouillée par erreur.
$pending = 'cutout/creature/SP-001.png';
$retaken = 'cutout/vegetation/TR-063-v12.png';

$probe = "<script>window.addEventListener('load', function () {"
    . "var out = document.body.appendChild(document.createElement('div')); out.id = 'sonde';"
    . "function dire(id) {"
    . "  var field = document.querySelector('.comment[data-id=\"' + id + '\"]');"
    . "  if (!field) { return id + ' : CHAMP INTROUVABLE'; }"
    . "  var zone = document.querySelector('.comment-zone[data-more=\"' + id + '\"]');"
    . "  var opener = document.querySelector('.open-comment[data-open=\"' + id + '\"]');"
    . "  return id + ' — TEXTE : [' + field.value.slice(0, 40) + '] — ZONE : ' + (zone && zone.hidden ? 'MASQUEE' : 'OUVERTE')"
    . "    + ' — SAISIE : ' + (field.readOnly ? 'VERROUILLEE' : 'LIBRE')"
    . "    + ' — CLASSEE : ' + (opener ? opener.getAttribute('data-handled') : 'SANS BOUTON');"
    . "}"
    // UNE VERSION ANTÉRIEURE PORTE SES PROPRES NOTES DEPUIS LE 2026-08-12, dans son panneau : la ligne qui les annonçait sur la carte courante a disparu avec son
    // objet. Ce qui se mesure n'est donc plus une annonce, c'est le champ de l'aînée elle-même — et le texte qu'il porte.
    . "function aine(id) {"
    . "  var champ = document.querySelector('.comment[data-id=\"' + id + '\"]');"
    . "  if (!champ) { return id + ' : CHAMP INTROUVABLE'; }"
    . "  return id + ' — SES NOTES : [' + champ.value.slice(0, 60) + ']';"
    . "}"
    // The state arrives by XHR after load: the report is written once that answer has been laid down, not before, or it would describe an empty page.
    . "setTimeout(function () {"
    . "  out.textContent = 'EN ATTENTE — ' + dire(" . json_encode($pending) . ") + ' || REPRISE — ' + aine(" . json_encode($retaken) . ");"
    . "}, 5000);"
    . "});</script>";

// THE PROBE PAGE IS OPENED THROUGH THE SERVER, NOT FROM THE DISK, and that is the whole reason this care is taken: the page reads its verdicts by XHR, and a
// document opened from file:// has the origin « null », so the browser refuses that call before it leaves. The page then shows every remark empty — which looks
// exactly like the defect one is trying to measure.
//
// AND IT GOES THROUGH `Probe::serve()` RATHER THAN WRITING ITS OWN COPY (`W21 sondes-servies`): the service serves it from the same origin AND muzzles it, so
// this probe cannot write into the operator's notes while looking at them. Rolled by hand, the copy was served but never muzzled — which is how a probe that
// only meant to look left ten empty verdicts behind on 2026-08-11.
$dom = Browser::get()->dom(Probe::get()->serve($html, $probe, 'remarque-traitee'), 12000);
if (preg_match('#<div id="sonde">(.*?)</div>#s', $dom, $found)) {
    echo trim($found[1]) . "\n";
    exit(0);
}
throw new RuntimeException("FAULT la sonde n'a rien rapporté — la page ne s'est pas chargée jusqu'au bout : {$copy}");
