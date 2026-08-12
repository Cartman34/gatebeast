<?php
/**
 * Usage: php review-server/inventory/build.php [sortie.html] — builds the page that lists the subjects of the GAME, served at /inventory.
 *        php review-server/inventory/build.php -h|--help — this text, and nothing is built.
 *
 * Intention: THE OPERATOR HAD ASKED FOR IT AND IT WAS LOST (2026-08-12: « j'avais demandé une page pour recenser les sujets, c'est fait ? »). No page said what a
 * subject IS. `/backlog` carries the open points of the project — it was called `/sujets`, which misled the operator onto it — and `/sprites` speaks of images.
 * Choosing what to produce next means reading a description, and the description lived only in a file nobody opens while looking at a page.
 *
 * TWO DESCRIPTIONS, AND THEY DO NOT SERVE THE SAME PURPOSE. The brief one is composed here from what the referential already holds — type, footprint, cover,
 * height, state of production — and lets a subject be recognised at a glance. The detailed one is quoted VERBATIM from the file the generator itself receives:
 * this page must never become a second wording of a subject, or the two would drift and the one that is read would not be the one that draws.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
require_once $root . '/review-server/lib/Inventory.php';
require_once $root . '/review-server/lib/Thumbnail.php';
require_once $root . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

$outputPath = $argv[1] ?? __DIR__ . '/page.html';
/**
 * L'ARTEFACT EST LA MÊME PAGE SANS SERVEUR, ET C'EST TOUT CE QUI CHANGE (opérateur, 2026-08-12 : « mets la page des sujets à traiter en artefact, je n'aurai que
 * le mobile, il faut donc le système de relevé »). Publiée, la page ne peut ni lire ni écrire sur le serveur de revue : les votes tiennent alors dans le
 * navigateur, et **le relevé revient** — pas partout, ici seulement, parce qu'ici il n'y a plus aucun autre canal. C'est l'exception écrite à la règle du
 * 2026-08-12 qui a fait disparaître tous les relevés : elle valait pour les pages servies, qui ont un serveur.
 */
$standalone = in_array('--artefact', $argv, true);
$inventory = new Inventory($root);
$thumbnails = new Thumbnail($root);
$theme = Theme::get();
$favicon = Favicon::get();
$reload = Reload::get();

/** La taille de la vignette d'un sujet sur cette page : de quoi le reconnaître, pas de quoi le juger — la page des sprites est là pour ça. */
const THUMBNAIL_PIXELS = 96;

function escape(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/**
 * La description détaillée d'un sujet, prise en entier dans son fichier.
 *
 * ELLE N'EST NI COUPÉE NI RÉSUMÉE : c'est le texte exact que reçoit le générateur, et c'est tout l'intérêt de le montrer ici. Un sujet sans fichier de
 * description le DIT — il ne peut alors rien produire du tout, et cette page est le seul endroit où ça se voit d'un coup d'œil.
 */
function description(string $root, string $code): ?string
{
    $path = "$root/assets/descriptions/$code.md";

    return is_file($path) ? trim(file_get_contents($path)) : null;
}

/**
 * Une description rendue en paragraphes, ses replis de fichier refermés.
 *
 * UN RETOUR À LA LIGNE SIMPLE EST UN PLI, PAS UNE COUPURE, et les prendre pour des coupures est le défaut que la première version de cette page a montré : les
 * fichiers de description sont repliés à la largeur du dépôt, si bien que le texte se brisait en plein milieu des phrases, à des endroits que personne n'a
 * choisis. Seule une ligne vide sépare deux paragraphes — c'est la convention du Markdown, et c'est celle que ces fichiers suivent déjà.
 */
function paragraphs(string $text): string
{
    $blocks = preg_split('/\n{2,}/', trim($text));
    $html = '';
    foreach ($blocks as $block) {
        $html .= '<p>' . escape(preg_replace('/\s*\n\s*/', ' ', trim($block))) . "</p>\n";
    }

    return $html;
}

/** Ce qui a été produit pour ce sujet, et ce qui reste dû : le tally des variants qui ont une image courante. */
/** Ce qu'une carte montre de la description : sa première phrase, coupée si elle est longue. */
const TEASER_LIMIT = 190;

/**
 * La barre du relevé, et elle n'existe QUE dans l'artefact.
 *
 * SUR MOBILE IL N'Y A PAS DE SERVEUR, DONC PAS D'AUTRE CANAL (opérateur, 2026-08-12). Les votes tiennent dans le navigateur, et le seul moyen de me les faire
 * parvenir est un texte à coller. La barre reste en bas de l'écran, où le pouce l'atteint, et elle dit le compte : un relevé qu'on croit vide se copie sans qu'on
 * le sache.
 */
const RELEVE_MARKUP = <<<'HTML'
<div class="releve">
  <p class="releve-compte" hidden></p>
  <button type="button" class="releve-copier">Copier le relevé</button>
</div>
HTML;

/**
 * Le relevé, assemblé et copié.
 *
 * LA COPIE PASSE PAR UN CHAMP CACHÉ : l'appel direct au presse-papiers est refusé dans le cadre où vit un artefact, et il échoue SANS RIEN DIRE — le bouton
 * paraît alors cassé. Si même cela échoue, le texte s'affiche tout sélectionné plutôt que d'être perdu.
 */
const RELEVE_SCRIPT = <<<'JS'
<script>
(function () {
  var barre = document.querySelector('.releve');
  var compte = barre.querySelector('.releve-compte');
  var bouton = barre.querySelector('.releve-copier');
  var MOTS = {approved: 'validé', rework: 'à reprendre', discarded: 'écarté'};

  window.gatebeastReleve = function () {
    var lignes = [];
    Array.prototype.forEach.call(document.querySelectorAll('.acts'), function (bloc) {
      var choisi = bloc.querySelector('input:checked');
      if (!choisi) { return; }
      var carte = bloc.closest('.subject');
      var nom = carte.querySelector('h2').textContent;
      lignes.push(bloc.getAttribute('data-id') + ' ' + nom + ' : ' + MOTS[choisi.getAttribute('data-act')]);
    });
    compte.textContent = lignes.length + ' vote(s)';
    compte.hidden = lignes.length === 0;

    return lignes;
  };

  bouton.addEventListener('click', function () {
    var lignes = window.gatebeastReleve();
    var texte = 'Inventaire du monde\n' + (lignes.length ? lignes.join('\n') : 'Aucun vote.');
    var champ = document.createElement('textarea');
    champ.value = texte;
    champ.setAttribute('readonly', 'readonly');
    champ.style.position = 'fixed';
    champ.style.opacity = '0';
    document.body.appendChild(champ);
    champ.select();
    var fait = false;
    try { fait = document.execCommand('copy'); } catch (erreur) { fait = false; }
    document.body.removeChild(champ);
    bouton.textContent = fait ? 'Copié' : 'Copie refusée — sélectionne le texte';
    if (!fait) {
      var visible = document.createElement('textarea');
      visible.className = 'releve-texte';
      visible.value = texte;
      barre.appendChild(visible);
      visible.select();
    }
    setTimeout(function () { bouton.textContent = 'Copier le relevé'; }, 2000);
  });

  window.gatebeastReleve();
})();
</script>
JS;

/**
 * Les trois actes d'un sujet, toujours offerts.
 *
 * ON VOTE SUR LE SUJET, PAS SUR UNE IMAGE, et c'est ce qui distingue cette page de celle des sprites (opérateur, 2026-08-12 : « je ne peux pas évaluer chaque
 * sujet », puis « y'a toujours pas les boutons de vote dessus »). Là-bas on juge un DESSIN — cette version est-elle bonne ? Ici on juge ce que le sujet EST : sa
 * description tient-elle, faut-il la reprendre, ou ce sujet n'a-t-il pas lieu d'être ? Les deux jugements sont rangés séparément, sans quoi valider une
 * description effacerait le verdict d'une image.
 *
 * LES MÊMES MOTS QUE LA PAGE DES SPRITES : `approved`, `rework`, `discarded`. Un second vocabulaire pour un même geste obligerait à traduire d'une page à l'autre.
 */
function acts(string $code): string
{
    $markup = '';
    foreach (['approved' => 'Valider', 'rework' => 'À reprendre', 'discarded' => 'Écarter'] as $key => $label) {
        // DES BOUTONS, PAS DES CASES À COCHER GRISES : la case porte l'état et reste masquée, le libellé devient le bouton. C'est la forme que l'opérateur a
        // demandée sur l'autre page, et deux formes pour un même geste se paient en hésitation à chaque clic.
        $markup .= sprintf('<label class="act act--%s"><input type="checkbox" data-id="%s" data-act="%s"><span>%s</span></label>',
            $key, escape($code), $key, escape($label));
    }

    return $markup;
}

/**
 * La phrase d'accroche d'un sujet : sa première phrase, ramenée à une longueur de carte.
 *
 * COUPÉE, JAMAIS RÉSUMÉE : un résumé serait une seconde rédaction du sujet, et il dériverait de celle qui dessine. La coupe tombe sur un mot entier et se dit
 * par des points de suspension — la description entière est à un pli de là, et c'est elle qui fait foi.
 *
 * ET LA PREMIÈRE PHRASE N'EST PAS TOUJOURS COURTE : celle de l'herbe rase fait six lignes et remplissait la carte à elle seule, ce qui reproduisait en petit le
 * défaut qu'on corrigeait. La limite est donc une longueur, pas une ponctuation.
 */
function teaser(string $detail): string
{
    $flat = trim(preg_replace('/\s*\n\s*/', ' ', $detail));
    $first = explode('. ', $flat)[0];
    if (mb_strlen($first) > TEASER_LIMIT) {
        $cut = mb_substr($first, 0, TEASER_LIMIT);
        $space = mb_strrpos($cut, ' ');

        return rtrim($space === false ? $cut : mb_substr($cut, 0, $space), " ,;:") . '…';
    }

    return rtrim($first, '.') . '.';
}

function production(Inventory $inventory, array $subject): array
{
    $done = 0;
    foreach ($subject['variants'] as $variant) {
        if ($inventory->currentRepresentation($variant) !== null) {
            $done++;
        }
    }

    return [$done, count($subject['variants'])];
}

$cards = '';
$counted = 0;
$missing = [];
$unreadable = [];
foreach ($inventory->subjects() as $code => $subject) {
    $counted++;
    $spread = $inventory->spread($subject);
    [$done, $total] = production($inventory, $subject);
    $main = $inventory->mainVariant($subject) ?? ($subject['variants'][0] ?? null);
    $current = $main ? $inventory->currentRepresentation($main) : null;
    // L'IMAGE ILLISIBLE EST UN FAIT À RAPPORTER, PAS UNE PAGE À FAIRE TOMBER : le service lève, cette page le note et continue — un sujet sans vignette se lit
    // encore par sa description, et c'est elle qu'on vient chercher ici.
    $shot = null;
    if ($current && !empty($current['path'])) {
        try {
            $shot = $thumbnails->shrink($current['path'], THUMBNAIL_PIXELS * $spread['columns']);
        } catch (RuntimeException $fault) {
            $unreadable[] = $code . ' : ' . $fault->getMessage();
        }
    }
    $detail = description($root, $code);
    if ($detail === null) {
        $missing[] = $code;
    }
    // LA BRÈVE SE COMPOSE, ELLE NE S'ÉCRIT PAS (choix de l'agent, 2026-08-12, annoncé à l'opérateur) : aucune donnée ne la porte aujourd'hui, et tout ce qui la
    // ferait tenir en une ligne est déjà déclaré ailleurs. La composer évite d'inventer une seconde source pour un texte qui existerait alors en deux versions.
    // EN PASTILLES PLUTÔT QU'EN PHRASE : quatre faits alignés se comparent d'une carte à l'autre d'un mouvement d'œil, là où une phrase se relit à chaque fois.
    // Les mots affichés restent français, comme la règle le réserve aux textes destinés à l'opérateur — le contrôle de vocabulaire y signale « hauteur », qui est
    // un mot montré, pas un symbole.
    $facts = [
        $subject['type'],
        sprintf('%d × %d au sol', $subject['footprint']['columns'], $subject['footprint']['rows']),
        isset($subject['height']) ? 'hauteur ' . $subject['height'] . ' case' : 'hauteur non déclarée',
        sprintf('%d/%d produit(s)', $done, $total),
    ];
    if (isset($subject['cover'])) {
        $facts[] = sprintf('couvert %d × %d', $subject['cover']['columns'], $subject['cover']['rows']);
    }
    $chips = '';
    foreach ($facts as $fact) {
        // L'ÉTAT DE PRODUCTION SE DISTINGUE DES AUTRES FAITS : c'est le seul qui bouge, et c'est celui qu'on cherche en choisissant quoi produire ensuite.
        $done_all = $done === $total && $total > 0;
        $kind = str_contains($fact, 'produit(s)') ? ($done_all ? ' chip--done' : ' chip--due') : '';
        $chips .= sprintf('<li class="chip%s">%s</li>', $kind, escape($fact));
    }

    // LA PREMIÈRE PHRASE SUFFIT À RECONNAÎTRE UN SUJET, et c'est elle qu'on montre : la description entière imposée sur quinze cartes rend la page illisible et
    // empêche précisément ce qu'on vient y faire — comparer. Elle n'est pas résumée, elle est COUPÉE À SA PREMIÈRE PHRASE : un résumé serait une seconde
    // rédaction, et il dériverait de celle qui dessine.
    $teaser = $detail === null ? '' : teaser($detail);

    $cards .= sprintf(
        '    <article class="subject" id="subject-%s">' . "\n"
        . '      <div class="subject-image">%s</div>' . "\n"
        . '      <p class="subject-head"><span class="subject-code">%s</span><span class="subject-profile">%s</span></p>' . "\n"
        . '      <h2>%s</h2>' . "\n"
        . '      <p class="subject-teaser">%s</p>' . "\n"
        // TOUT LE DÉTAIL EST DERRIÈRE UN SEUL PLI (opérateur, 2026-08-12 : « de base, je ne dois voir qu'un résumé de chaque sujet, je peux cliquer pour dérouler
        // avoir plus de détails si je le souhaite »). Le résumé, c'est l'image, le nom et la première phrase — de quoi reconnaître. Les faits chiffrés et la
        // description entière sont du détail : ils se demandent. Un `details` le fait sans une ligne de script, et l'état de chaque pli appartient à celui qui lit.
        . '      <details class="subject-detail"><summary>Plus de détails</summary><ul class="chips">%s</ul>%s</details>' . "\n"
        // LE VOTE EST EN BAS DE CARTE ET TOUJOURS VISIBLE, PLI OUVERT OU FERMÉ (même message) : c'est le seul geste qu'on vient faire ici, il ne se cherche pas.
        . '      <div class="acts" data-id="%s">%s</div>' . "\n"
        . "    </article>\n",
        escape($code),
        $shot ? sprintf('<img src="%s" width="%d" height="%d" alt="">', $shot[0], $shot[1], $shot[2]) : '<p class="to-produce">À produire</p>',
        escape($code), escape($subject['profile'] ?? ''),
        escape(ucfirst($inventory->label($code))),
        $teaser === '' ? '<em>Aucune description écrite — ce sujet ne peut rien produire.</em>' : escape($teaser),
        $chips,
        $detail === null ? '<p><em>Aucune description écrite.</em></p>' : paragraphs($detail),
        escape($code), acts($code)
    );
}

$page = <<<'HTML'
<title>Inventaire du monde</title>
{$favicon}

<style>
{$theme}
{$layout}
  body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.55 ui-sans-serif, system-ui, sans-serif; }
  h1 { margin: 0 0 6px; font-size: clamp(1.5rem, 1.1rem + 1vw, 2.2rem); letter-spacing: -.01em; }
  .lede { margin: 0 0 10px; color: var(--muted); }
  .tally { margin: 0 0 28px; font-family: ui-monospace, monospace; font-size: .8rem; color: var(--muted); }
  /* LA CARTE EST UNE COLONNE, PAS UNE LIGNE : l'image en haut, le nom, la phrase, les faits, le pli. C'est ce qui permet à la grille d'en poser autant que
     l'écran le permet — une carte en ligne prend toute la largeur quoi qu'il arrive, et quinze d'entre elles font quinze écrans. */
  .subject { display: flex; flex-direction: column; padding: 0 0 14px; background: var(--card); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
  /* L'IMAGE A SA BANDE, ET ELLE GARDE SA HAUTEUR MÊME QUAND ELLE MANQUE : sans elle, les cartes de la même rangée cessent de s'aligner et la grille ondule. */
  .subject-image { display: flex; align-items: center; justify-content: center; height: 168px; background: var(--bg); border-bottom: 1px solid var(--line); }
  .subject-image img { image-rendering: pixelated; max-height: 152px; width: auto; }
  .to-produce { margin: 0; color: var(--muted); font-size: .8rem; }
  .subject h2 { margin: 2px 14px 6px; font-size: 1.1rem; font-weight: 600; }
  .subject-head { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; margin: 12px 14px 0;
                  font-family: ui-monospace, monospace; font-size: 10px; letter-spacing: .03em; color: var(--muted); }
  .subject-code { padding: 2px 7px; background: var(--bg); border: 1px solid var(--line); border-radius: 3px; color: var(--ink); font-weight: 700; }
  .subject-teaser { margin: 0 14px 12px; font-size: .92rem; color: var(--ink); }
  /* LES PASTILLES SE LISENT EN DIAGONALE, d'une carte à l'autre : même ordre, même place, donc l'œil compare sans relire. */
  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin: auto 14px 0; padding: 0; list-style: none; }
  .chip { padding: 3px 9px; background: var(--bg); border: 1px solid var(--line); border-radius: 999px;
          font-family: ui-monospace, monospace; font-size: 11px; color: var(--muted); }
  .chip--done { border-color: var(--state-validated-edge); color: var(--state-validated-edge); }
  .chip--due { border-color: var(--state-rework-edge); color: var(--state-rework-edge); }
  /* LES TROIS ACTES, AU MÊME ENDROIT SUR CHAQUE CARTE : c'est ce qui permet de descendre la grille en jugeant, sans chercher le bouton à chaque sujet. */
  .acts { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 14px 0; }
  .act input { position: absolute; opacity: 0; pointer-events: none; }
  .act span { display: inline-block; padding: 4px 10px; background: var(--bg); border: 1px solid var(--line); border-radius: 4px;
              font-size: 12px; color: var(--muted); cursor: pointer; }
  .act span:hover { border-color: var(--accent); color: var(--accent); }
  .act input:focus-visible + span { outline: 2px solid var(--accent); outline-offset: 2px; }
  /* Un acte retenu prend la couleur de son état, déclarée au thème — jamais un code écrit ici, qui ne suivrait pas un changement d'habillage. */
  .act--approved input:checked + span { background: var(--state-validated); border-color: var(--state-validated-edge); color: var(--ink-on-state); }
  .act--rework input:checked + span { background: var(--state-rework); border-color: var(--state-rework-edge); color: var(--ink-on-state); }
  .act--discarded input:checked + span { background: var(--state-dismissed); border-color: var(--state-dismissed-edge); color: var(--ink-on-state); }
  .subject-detail { margin: 12px 14px 0; font-size: .9rem; }
  .subject-detail summary { cursor: pointer; color: var(--accent); font-size: .82rem; }
  .subject-detail p { margin: 8px 0 0; color: var(--muted); }
  /* LA BARRE DU RELEVÉ RESTE SOUS LE POUCE : sur mobile, un bouton posé en fin de page se cherche après quinze cartes, et c'est le seul geste qui fait sortir les
     votes de l'appareil. Elle ne sert que dans l'artefact — la page servie enregistre toute seule. */
  .releve { position: fixed; left: 0; right: 0; bottom: 0; display: flex; align-items: center; gap: 12px; padding: 10px var(--gutter);
            background: var(--card); border-top: 1px solid var(--line); }
  .releve-compte { margin: 0; font-family: ui-monospace, monospace; font-size: 12px; color: var(--muted); }
  .releve-copier { padding: 8px 14px; background: var(--bg); color: var(--ink); border: 1px solid var(--accent); border-radius: 4px; font: inherit; font-size: 14px; }
  .releve-texte { flex: 1 1 auto; min-height: 60px; font: inherit; font-size: 12px; }
  /* La page garde de la place sous elle : sans quoi la barre couvre la dernière carte, et son vote devient inatteignable. */
  .wrap { padding-bottom: 120px; }
{$reloadStyles}
</style>

<div class="wrap">
  <h1>Inventaire du monde</h1>
  <p class="lede measure">Ce que le monde contient, sujet par sujet : de quoi le reconnaître d'un coup d'œil, et sa description en entier quand on la demande —
  celle-là même qui part au générateur, citée mot pour mot. C'est ici qu'on choisit ce qu'on produit ensuite ; la page des sprites dit où en sont les images.</p>
  <p class="tally">{$tally}</p>
  <div class="grid">
{$subjects}  </div>
</div>
{$notesScript}
<script>
(function () {
  /* LE VOTE VA AU SERVEUR AU MOMENT OÙ IL SE DONNE, ET LE SERVEUR EST LE SEUL ÉCRIVAIN. Une page est une copie sur un écran, possiblement ancienne : laisser
     chaque copie écrire ferait gagner le dernier rechargement. C'est le mécanisme de la page des sprites, repris tel quel — la section diffère, pas le geste. */
  var SECTION = 'sujets';
  var state = {};
  var ready = false;

  function render() {
    Array.prototype.forEach.call(document.querySelectorAll('.acts input'), function (box) {
      var id = box.getAttribute('data-id');
      box.checked = Boolean(state[id] && state[id][box.getAttribute('data-act')]);
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll('.acts input'), function (box) {
    box.addEventListener('change', function () {
      var id = box.getAttribute('data-id');
      var act = box.getAttribute('data-act');
      state[id] = state[id] || {};
      /* UN VOTE EST L'UN DES TROIS, JAMAIS DEUX : un sujet ne peut pas être retenu et écarté à la fois, et une carte qui porterait les deux n'apprendrait rien.
         Ce sont des cases parce que c'est la forme demandée — on déclique pour revenir en arrière — mais elles se comportent comme un choix unique. */
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
{$releveMarkup}
{$releveScript}
{$reloadMarkup}
{$reloadScript}
HTML;

// LE SERVEUR EST LE SEUL ÉCRIVAIN QUAND IL Y EN A UN ; SINON C'EST LE NAVIGATEUR, ET LE RELEVÉ REDEVIENT LE CANAL. Une page publiée ne peut appeler personne :
// ses votes tiennent dans son stockage local, et le bouton de relevé est le seul moyen de me les faire parvenir. C'est la moitié du travail que la version
// servie fait toute seule — et c'est précisément pourquoi le relevé avait disparu partout ailleurs.
$storage = $standalone
    ? <<<'JS'
  var MEMOIRE = 'gatebeast-inventaire';
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

$page = strtr($page, [
    '{$theme}' => $theme->css('graphite'),
    '{$layout}' => Layout::get()->css(),
    // Le module qui parle au serveur : c'est lui qui porte le dialogue, cette page ne fait que lui donner sa section et sa route. L'artefact n'en a pas.
    '{$notesScript}' => $standalone ? '' : Notes::get()->script('/inventory'),
    '{$storage}' => $storage,
    '{$releveMarkup}' => $standalone ? RELEVE_MARKUP : '',
    '{$releveScript}' => $standalone ? RELEVE_SCRIPT : '',
    '{$favicon}' => $favicon->tag(),
    '{$reloadStyles}' => $standalone ? '' : $reload->styles(),
    '{$reloadMarkup}' => $standalone ? '' : $reload->markup(),
    '{$reloadScript}' => $standalone ? '' : $reload->script('/inventory'),
    '{$tally}' => sprintf('%d sujet(s)%s', $counted, $missing ? ' · sans description : ' . implode(', ', $missing) : ''),
    '{$subjects}' => $cards,
]);

file_put_contents($outputPath, $page);
// CE QUI MANQUE REMONTE AU LANCEUR, PAS SEULEMENT DANS LA PAGE : un sujet sans description ne peut rien produire, et celui qui construit la page doit
// l'apprendre de sa sortie — il ne va pas relire le produit fini pour découvrir une anomalie.
printf("%s — %d sujet(s), %.1f ko\n", $outputPath, $counted, strlen($page) / 1024);
if ($missing) {
    fwrite(STDERR, sprintf("SANS DESCRIPTION (%d) : %s\n", count($missing), implode(', ', $missing)));
}
foreach ($unreadable as $said) {
    fwrite(STDERR, "IMAGE ILLISIBLE — {$said}\n");
}
