<?php
/**
 * Usage: php review-server/backlog/build.php [sortie.html] — builds the open-points page of the review server (RS), served at /backlog.
 *
 * Intention: what is left to do had no page. It lived as prose in SUIVI.md, where nothing could sort it or count it, and the operator had to read a long document to know what came next. The data
 * lives in review-server/subjects.json now, written only by scripts/backlog.php; this page is its reading, in priority order, open points first.
 *
 * The long description is Markdown and is rendered as such — a point that cannot say what it means in more than a label is a point nobody can pick up cold.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Backlog.php';
bootBuild();

$outputPath = $argv[1] ?? __DIR__ . '/page.html';
/**
 * L'ARTEFACT EST LA MÊME PAGE SANS SERVEUR (opérateur, 2026-08-12 : « je n'aurai que le mobile, il faut donc le système de relevé »). Publiée, elle ne peut ni
 * lire ni écrire sur le serveur de revue : les votes tiennent dans le navigateur, et le relevé redevient le seul canal qui les fait sortir de l'appareil.
 */
$standalone = in_array('--artefact', $argv, true);
$backlog = new Backlog($root);
$theme = Theme::get();
$favicon = Favicon::get();
$reload = Reload::get();

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/**
 * Le Markdown d'une description, rendu au strict nécessaire : gras, code, titres de niveau trois, listes et paragraphes.
 *
 * ÉCRIT ICI PLUTÔT QU'EMPRUNTÉ : PHP n'embarque pas de lecteur Markdown, et en installer un est une dépendance à poser sur toute machine où le projet tourne — ce qui appartient à l'opérateur. Ce
 * qu'on écrit dans une description tient dans ces cinq marques ; le jour où ça déborde, c'est une bibliothèque qu'il faudra demander, pas une marque de plus à bricoler ici.
 */
function markdown(string $text): string
{
    $blocks = preg_split('/\n{2,}/', trim($text));
    $html = '';
    foreach ($blocks as $block) {
        $block = escape(trim($block));
        $block = preg_replace('/\*\*(.+?)\*\*/s', '<strong>$1</strong>', $block);
        $block = preg_replace('/`(.+?)`/s', '<code>$1</code>', $block);
        if (str_starts_with($block, '### ')) {
            $html .= '<h3>' . substr($block, 4) . "</h3>\n";
            continue;
        }
        if (preg_match('/^[-*] /', $block)) {
            $items = preg_split('/\n[-*] /', preg_replace('/^[-*] /', '', $block));
            $html .= "<ul>\n" . implode('', array_map(fn (string $i) => '<li>' . nl2br($i) . "</li>\n", $items)) . "</ul>\n";
            continue;
        }
        $html .= '<p>' . nl2br($block) . "</p>\n";
    }

    return $html;
}

/**
 * LA PAGE NE PORTE QUE CE QUI ATTEND UNE RÉPONSE DE LUI (opérateur, 2026-08-12 : « actualise la page “la pile” pour n'avoir que les topics qui ont besoin d'une
 * réponse »). Le critère n'est pas écrit ici : il est au service, `Backlog::awaitsOperator()`, avec les états qui le définissent. Ce qui reste est du travail
 * dû, dont il a déjà dit ce qu'il voulait — il est COMPTÉ et nommé en une ligne, jamais caché : une page qui montre trois cartes sans dire qu'elle en tait
 * quatorze se lit comme une pile vide, et c'est le seul malentendu qu'un filtre peut créer.
 */
$openAll = $backlog->ordered(true);
$open = array_values(array_filter($openAll, fn (array $p) => $backlog->awaitsOperator($p)));
$mine = array_values(array_filter($openAll, fn (array $p) => !$backlog->awaitsOperator($p)));

/**
 * Les deux votes d'une task, toujours offerts et toujours retirables.
 *
 * L'OPÉRATEUR VOTE SUR CE QUE L'AGENT DOIT FAIRE (2026-08-12 : « je veux voter pour les topics à travailler »). C'est la seule chose qu'on vient faire ici : la
 * pile dit ce qu'il reste, lui dit ce qu'il en veut.
 *
 * ET LE SECOND ACTE EST UN REJET, PAS UN REPORT (opérateur, le même jour : « tu as une option pour remettre plus tard un topic alors que je t'avais demandé
 * simplement le rejeter, je dois pouvoir rejeter un topic de la pile »). « Plus tard » ne tranche rien : la task reste, et elle repasse devant lui à chaque
 * lecture. Rejeter la sort. C'est le statut `dismissed` que la pile porte déjà — le vote emploie donc son mot, il n'en invente pas un second.
 */
function votes(string $ref): string
{
    $markup = '';
    foreach (['wanted' => 'À travailler', 'dismissed' => 'Rejeter'] as $key => $label) {
        $markup .= sprintf('<label class="act act--%s"><input type="checkbox" data-id="%s" data-act="%s"><span>%s</span></label>',
            $key, escape($ref), $key, escape($label));
    }

    return $markup;
}

/** Une carte de task : sa référence, son libellé, ses métadonnées, sa description en entier, et le vote de l'opérateur en bas. */
function card(array $point, int $rank = null): string
{
    return sprintf(
        '  <article class="point" data-statut="%s">' . "\n"
        . '    <p class="point-tete"><span class="point-ref">%s</span><span class="point-statut">%s</span>'
        . '<span class="point-prio">priorité %d</span><span class="point-attend">attend : %s</span>%s</p>' . "\n"
        . '    <h2>%s</h2>' . "\n"
        // LA DESCRIPTION EST REPLIÉE, ET LE VOTE PASSE DEVANT ELLE. Dépliée, elle enterre le vote sous plusieurs écrans — sur un mobile, il devient
        // inatteignable, et c'est le seul geste qu'on vient faire ici. Elle reste entière d'un clic : c'est elle qui dit ce que la task engage.
        . '    <details class="point-corps"><summary>Ce que ça engage</summary>%s</details>' . "\n"
        . '    <div class="acts" data-id="%s">%s</div>' . "\n"
        // LE COMMENTAIRE EST TOUJOURS LÀ, PAS DERRIÈRE UN BOUTON (opérateur, 2026-08-12 : « je dois pouvoir ajouter un commentaire ») : un vote sans motif se
        // relit sans savoir pourquoi il a été donné, et un champ qu'il faut d'abord ouvrir ne se remplit jamais.
        . '    <textarea class="comment" data-id="%s" rows="2" placeholder="Ce que tu veux dire là-dessus."></textarea>' . "\n"
        . '    <p class="point-pied">Créé le %s · repris le %s</p>' . "\n"
        . "  </article>\n",
        escape($point['status']),
        escape($point['ref']),
        // L'ATTENDU SE LIT AVEC LE STATUT : une carte « en attente » qui ne dit pas de quoi oblige à ouvrir la description pour savoir si elle réclame quelque chose de l'opérateur.
        escape((Backlog::STATUS_LABELS[$point['status']] ?? $point['status']) . (isset($point['waits_on']) ? ' : ' . $point['waits_on'] : '')),
        $point['priority'], escape($point['waiting'] === Backlog::WAITING_OPERATOR ? 'opérateur' : 'agent'),
        $rank !== null ? sprintf('<span class="point-rang">%s</span>', $rank === 1 ? 'le prochain' : (string) $rank) : '',
        escape($point['label']), markdown($point['description']),
        escape($point['ref']), votes($point['ref']), escape($point['ref']),
        escape($point['created']), escape($point['updated'])
    );
}

$openMarkup = '';
foreach ($open as $index => $point) {
    $openMarkup .= card($point, $index + 1);
}
// CE QUI NE T'ATTEND PAS SE DIT EN UNE LIGNE, PAS EN CARTES : la ref et le libellé suffisent à savoir sur quoi je pars, et une carte entière par task
// ramènerait la page à ce qu'elle était.
$mineMarkup = '';
foreach ($mine as $point) {
    $mineMarkup .= sprintf("    <li><span class=\"point-ref\">%s</span> %s</li>\n", escape($point['ref']), escape($point['label']));
}

$page = <<<'HTML'
<title>La pile</title>
{$favicon}

<style>
{$theme}
{$layout}
  body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.55 ui-sans-serif, system-ui, sans-serif; }
  /* LA LARGEUR VIENT DU FORMAT COMMUN, ET LES POINTS SE POSENT EN GRILLE (opérateur, 2026-08-12 : « y'a toujours une colonne collée à gauche et l'espace n'est
     pas occupé »). Une seule colonne à sa mesure de lecture laissait les trois quarts d'un grand écran vides — la mesure protège la ligne, elle ne dit pas
     combien de colonnes tiennent à côté. La colonne d'un point est plus large que celle d'une carte de sujet : un point porte de la prose, pas quatre faits. */
  .grid { --card-min: 520px; align-items: start; }
  .lede, .tally { max-width: var(--measure); }
  h1 { margin: 0 0 4px; font-size: 1.6rem; }
  .lede { margin: 0 0 8px; color: var(--muted); max-width: 90ch; }
  .compte { margin: 0 0 24px; font-family: ui-monospace, monospace; font-size: .8rem; color: var(--muted); }
  .point { margin: 0 0 10px; padding: 12px 14px; background: var(--card); border: 1px solid var(--line); border-radius: 4px; }
  .point h2 { margin: 6px 0 8px; font-size: 1.05rem; font-weight: 600; }
  .point-tete { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; margin: 0;
                font-family: ui-monospace, monospace; font-size: 10px; letter-spacing: .03em; color: var(--muted); }
  .point-ref { padding: 2px 7px; background: var(--bg); border: 1px solid var(--line); border-radius: 2px; color: var(--ink); font-weight: 700; }
  .point-rang { margin-left: auto; padding: 2px 7px; border: 1px solid var(--accent); border-radius: 2px; color: var(--accent); }
  .point-corps { font-size: .92rem; }
  .point-corps summary { cursor: pointer; color: var(--accent); font-size: .82rem; }
  .point-corps > *:not(summary) { margin-top: 8px; }
  .point-corps p { margin: 0 0 8px; }
  .point-corps ul { margin: 0 0 8px; padding-left: 20px; }
  .point-corps code { font-family: ui-monospace, monospace; font-size: .85em; color: var(--accent); }
  .point-pied { margin: 8px 0 0; font-size: .72rem; color: var(--muted); }
  /* LE STATUT SE VOIT AVANT D'ÊTRE LU : une pile où tout se ressemble oblige à lire chaque carte pour savoir laquelle bouge. */
  .point[data-statut="in-progress"] { border-left: 3px solid var(--accent); }
  .point[data-statut="pending-decision"] { border-left: 3px solid var(--state-rework-edge); }
  .point[data-statut="pending-dependency"] { border-left: 3px solid var(--muted); }
  .point[data-statut="waiting-external"] { border-left: 3px solid var(--state-dismissed-edge); }
  .point[data-statut="done"], .point[data-statut="dismissed"] { opacity: .55; }
  .clos { margin-top: 40px; }
  .clos summary { cursor: pointer; color: var(--muted); font-size: .9rem; }
  .mien { margin: 12px 0 0; padding-left: 18px; color: var(--muted); font-size: .9rem; }
  .mien li { margin: 4px 0; }
  .mien .point-ref { margin-right: 8px; }
  /* LE VOTE EST EN BAS DE CHAQUE CARTE, TOUJOURS VISIBLE : c'est le seul geste que l'opérateur vient faire ici, il ne se cherche pas. */
  .acts { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 0; }
  .act input { position: absolute; opacity: 0; pointer-events: none; }
  .act span { display: inline-block; padding: 6px 12px; background: var(--bg); border: 1px solid var(--line); border-radius: 4px;
              font-size: 13px; color: var(--muted); cursor: pointer; }
  .act span:hover { border-color: var(--accent); color: var(--accent); }
  .act input:focus-visible + span { outline: 2px solid var(--accent); outline-offset: 2px; }
  .act--wanted input:checked + span { background: var(--state-validated); border-color: var(--state-validated-edge); color: var(--ink-on-state); }
  .act--dismissed input:checked + span { background: var(--state-dismissed); border-color: var(--state-dismissed-edge); color: var(--ink-on-state); }
  /* LE CHAMP TIENT DANS SA CARTE : sans box-sizing, ses bordures s'ajoutent aux cent pour cent de largeur et il déborde de quelques pixels — ce qui se voit
     tout de suite sur une grille. */
  .comment { box-sizing: border-box; width: 100%; margin: 8px 0 0; padding: 8px 10px; background: var(--bg); color: var(--ink);
             border: 1px solid var(--line); border-radius: 4px; font: inherit; font-size: .88rem; resize: vertical; }
  .comment:focus { border-color: var(--accent); outline: none; }
  /* LA BARRE DU RELEVÉ RESTE SOUS LE POUCE, et elle n'existe que dans l'artefact : publiée, la page ne peut appeler aucun serveur, et c'est le seul moyen de
     faire sortir les votes de l'appareil. La page servie, elle, enregistre toute seule. */
  .releve { position: fixed; left: 0; right: 0; bottom: 0; display: flex; align-items: center; gap: 12px; padding: 10px var(--gutter);
            background: var(--card); border-top: 1px solid var(--line); }
  .releve-compte { margin: 0; font-family: ui-monospace, monospace; font-size: 12px; color: var(--muted); }
  .releve-copier { padding: 8px 14px; background: var(--bg); color: var(--ink); border: 1px solid var(--accent); border-radius: 4px; font: inherit; font-size: 14px; }
  .releve-texte { flex: 1 1 auto; min-height: 60px; font: inherit; font-size: 12px; }
{$reloadStyles}
</style>

<div class="wrap">
  <h1>La pile</h1>
  <p class="lede measure"><strong>Ce qui attend une réponse de toi, et rien d'autre</strong> — une task que j'ai proposée et qui attend ton accord, ou une
  décision qui t'appartient.{$phraseVote}</p>
  <p class="compte">{$compte}</p>
  <div class="grid">
{$ouverts}  </div>
  <details class="clos">
    <summary>{$titreMien}</summary>
    <ul class="mien">
{$miens}    </ul>
  </details>
</div>
{$releveMarkup}
{$notesScript}
{$scriptVote}
{$releveScript}
{$reloadMarkup}
{$reloadScript}
HTML;

// LE SCRIPT DU VOTE NE PART QUE S'IL Y A DES CARTES À VOTER. Aucune carte, aucun `.acts` ni `.comment` dans le balisage : le script y chercherait des cibles
// absentes, ce qu'un sélecteur ne signale jamais — et `check-page-selectors.php` a levé exactement là-dessus le jour où la page s'est mise à filtrer.
$voteScript = <<<'HTML'
<script>
(function () {
  var SECTION = 'pile';
  var state = {};
  var ready = false;

  function render() {
    Array.prototype.forEach.call(document.querySelectorAll('.acts input'), function (box) {
      var id = box.getAttribute('data-id');
      box.checked = Boolean(state[id] && state[id][box.getAttribute('data-act')]);
    });
    /* LE FORMULAIRE SE RETROUVE TEL QU'IL A ÉTÉ LAISSÉ (opérateur, 2026-08-12 : « le formulaire doit être préservé d'un chargement à l'autre ») : un commentaire
       qu'on retape après chaque rechargement ne s'écrit pas deux fois — on renonce à l'écrire. */
    Array.prototype.forEach.call(document.querySelectorAll('.comment'), function (champ) {
      var id = champ.getAttribute('data-id');
      champ.value = (state[id] && state[id].comment) || '';
    });
    if (window.gatebeastReleve) { window.gatebeastReleve(); }
  }

  /* IL S'ENREGISTRE PENDANT LA FRAPPE, PAS À LA SORTIE DU CHAMP : un rechargement au milieu d'une phrase la perdrait, et c'est exactement le cas que la demande
     nomme. Une courte attente évite d'écrire à chaque touche — assez courte pour qu'aucune phrase ne se perde. */
  var minuteur = null;
  Array.prototype.forEach.call(document.querySelectorAll('.comment'), function (champ) {
    champ.addEventListener('input', function () {
      var id = champ.getAttribute('data-id');
      state[id] = state[id] || {};
      state[id].comment = champ.value;
      if (minuteur) { clearTimeout(minuteur); }
      minuteur = setTimeout(function () {
        retenir(id);
        if (window.gatebeastReleve) { window.gatebeastReleve(); }
      }, 400);
    });
  });

  Array.prototype.forEach.call(document.querySelectorAll('.acts input'), function (box) {
    box.addEventListener('change', function () {
      var id = box.getAttribute('data-id');
      var act = box.getAttribute('data-act');
      state[id] = state[id] || {};
      /* UN VOTE EST L'UN DES DEUX, JAMAIS LES DEUX : « à travailler » et « rejeter » se contredisent, et une carte qui porterait les deux n'apprendrait rien. */
      if (box.checked) {
        Array.prototype.forEach.call(document.querySelectorAll('.acts input[data-id="' + id + '"]'), function (other) {
          if (other !== box) {
            other.checked = false;
            state[id][other.getAttribute('data-act')] = false;
          }
        });
      }
      state[id][act] = box.checked;
      retenir(id);
      if (window.gatebeastReleve) { window.gatebeastReleve(); }
    });
  });

{$storage}
})();
</script>
HTML;

// LE SERVEUR EST LE SEUL ÉCRIVAIN QUAND IL Y EN A UN ; PUBLIÉE, LA PAGE N'APPELLE PERSONNE. Ses votes tiennent alors dans le navigateur, et le relevé est le seul
// canal qui les fait sortir de l'appareil — c'est l'exception écrite à la règle du 2026-08-12 qui a retiré tous les relevés : elle valait pour les pages servies.
$storage = $standalone
    ? <<<'JS'
  var MEMOIRE = 'gatebeast-pile';
  function retenir() {
    try { localStorage.setItem(MEMOIRE, JSON.stringify(state)); } catch (erreur) { /* un cadre peut refuser le stockage : le vote vaut alors pour la visite */ }
  }
  try { state = JSON.parse(localStorage.getItem(MEMOIRE)) || {}; } catch (erreur) { state = {}; }
  ready = true;
  render();
JS
    : <<<'JS'
  function retenir(id) {
    /* RIEN NE S'ÉCRIT AVANT D'AVOIR LU : sans cette garde, le premier rendu repartirait vers le serveur et écraserait ce qui n'est pas encore arrivé. */
    if (!ready || !window.gatebeastNotes) { return; }
    var change = {};
    change[id] = state[id];
    window.gatebeastNotes.save(SECTION, change);
  }
  if (window.gatebeastNotes) {
    window.gatebeastNotes.load(SECTION, function (stored) {
      state = stored || {};
      ready = true;
      render();
    });
  }
JS;

// L'ÉTAT PART DANS LE SCRIPT DU VOTE AVANT QUE CELUI-CI N'ENTRE DANS LA PAGE : `strtr` ne repasse pas sur ce qu'il vient d'écrire, et un `{$storage}` substitué
// en même temps que son enveloppe resterait tel quel dans la page finale.
$voteScript = strtr($voteScript, ['{$storage}' => $storage]);

$page = strtr($page, [
    '{$theme}' => $theme->css('graphite'),
    '{$layout}' => Layout::get()->css(),
    '{$favicon}' => $favicon->tag(),
    '{$scriptVote}' => $open === [] ? '' : $voteScript,
    '{$notesScript}' => $standalone ? '' : Notes::get()->script('/backlog'),
    '{$releveMarkup}' => $standalone ? Survey::get()->markup() : '',
    '{$releveScript}' => $standalone ? Survey::get()->script('La pile — mes votes', ['wanted' => 'à travailler', 'dismissed' => 'REJETÉ']) : '',
    '{$reloadStyles}' => $standalone ? '' : $reload->styles(),
    '{$reloadMarkup}' => $standalone ? '' : $reload->markup(),
    // LE SCRIPT DE RECHARGEMENT PART AVEC SON BALISAGE, JAMAIS SANS : privé de son bouton, il levait sur un élément absent et emportait ce qui suivait. Les trois
    // morceaux — style, balisage, script — se retirent ensemble ou pas du tout.
    '{$reloadScript}' => $standalone ? '' : $reload->script('/backlog'),
    // LA PHRASE DU VOTE NE S'ÉCRIT QUE S'IL Y A QUELQUE CHOSE À VOTER : expliquer un geste qu'aucune carte n'offre fait chercher les boutons qui n'existent pas.
    '{$phraseVote}' => $open === [] ? '' : ' <strong>Chaque carte porte ton vote</strong> : ce que tu veux voir traité, et ce que tu rejettes — une task'
        . ' rejetée sort de la pile. Le vote se retire en recliquant.',
    '{$compte}' => sprintf('%d en attente de toi · %d à moi · php scripts/backlog.php next', count($open), count($mine)),
    // L'ÉTAT VIDE DIT OÙ EST L'ATTENTE, IL NE DIT PAS SEULEMENT QU'ELLE N'EST PAS ICI. Une page qui répond « rien » à qui vient voir ce qu'on lui demande l'a
    // fait se déplacer pour rien : les sprites à juger, eux, attendent bien, et c'est sur l'autre page.
    '{$ouverts}' => $openMarkup !== '' ? $openMarkup
        : "  <p class=\"lede measure\">Rien ne t'attend dans la pile : tu as déjà tranché tout ce qui s'y trouve, et le reste est du travail dû, listé plus bas."
            . " <strong>Ce qui t'attend est ailleurs</strong> : les sprites à juger, sur <a href=\"/sprites\">le suivi des sprites</a>.</p>\n",
    '{$titreMien}' => sprintf('Les %d tasks qui ne t\'attendent pas — du travail dû, déjà décidé', count($mine)),
    '{$miens}' => $mineMarkup,
]);

file_put_contents($outputPath, $page);
printf("%s — %d point(s) en attente de l'opérateur, %d à l'agent, %.1f ko\n", $outputPath, count($open), count($mine), strlen($page) / 1024);
