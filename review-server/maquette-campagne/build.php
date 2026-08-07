<?php
/**
 * Usage: php review-server/maquette-campagne/build.php
 *
 * Builds review-server/maquette-campagne/page.html — ONE page holding the two views of Maquette Campagne: its composition plan, and the mock-up mounted from it. Two sections, folded or unfolded at will, each
 * remembering its own state from one visit to the next, and each keeping the review tools it already has.
 *
 * Intention: the plan and the mock-up answer the same question — is this scene right? — and the operator was made to open two addresses to ask it. One subject, one page.
 *
 * THE TWO DOCUMENTS ARE MERGED, NOT EMBEDDED. They were first put in embedded documents, to keep their tools from colliding; in an artifact, a script inside an embedded document never runs, and both
 * pages arrived dead — visible, and unusable. A script belongs in the page, as everywhere else in this project. The collision is resolved where it lives: the mock-up's own class names are prefixed,
 * so the two review tools stop reaching for one another's elements while each keeps working exactly as it did.
 */

$root = dirname(__DIR__, 2);
$here = __DIR__;
require_once $root . '/review-server/bootstrap.php';
bootBuild();

// Services are taken here, at the top, once.
$favicon = Favicon::get();
$reload = Reload::get();

$sources = [
    // Both sources are produced WITHOUT a reload notice (empty third argument to their builder): this page is the one that carries it, once, on its own route.
    ['cle' => 'plan', 'titre' => 'Le plan de composition', 'fichier' => "$root/review-server/parc/maquette-campagne-plan.html", 'prefixe' => null,
     'quoi' => 'Ce que la scène déclare, case par case : quel sujet est posé où, et quels bords chaque pièce rejoint. Les raccords y sont vérifiés par calcul.'],
    ['cle' => 'maquette', 'titre' => 'La maquette montée', 'fichier' => "$root/review-server/parc/maquette-campagne-montee.html", 'prefixe' => 'mq-',
     'quoi' => 'Les sprites posées sur leurs cases, à l\'échelle du monde : le sol d\'abord, puis ce qui se dresse dessus.'],
];

// Les noms que les deux pages emploient toutes les deux. Préfixer ceux d'un seul côté suffit à les séparer, et c'est la maquette qui est préfixée — le plan en porte davantage, et moins on touche,
// moins on casse. Les identifiants CSS et les sélecteurs JS passent par la même table, donc rien ne peut être renommé d'un côté seulement.
const PARTAGES = ['plan', 'dessin', 'zone', 'survol', 'saisie', 'saisie-ou', 'saisie-boutons', 'poser', 'supprimer', 'rouvrir', 'annuler', 'remarques',
    'remarques-head', 'remarques-vides', 'copier', 'effacer', 'taille', 'zooms', 'zoom', 'marque', 'ou', 'quoi', 'retirer', 'barre', 'mode', 'wrap',
    'eyebrow', 'lede', 'notes', 'tally', 'source', 'dit', 'rest', 'code', 'number', 'scene', 'scene-cadre', 'scene-piste', 'pose', 'trou', 'manquants',
    'compte', 'remarque--reglee', 'reelle', 'fixe', 'tire'];

/** Le corps d'un document produit : ce qui est entre <div class="wrap"> et la fin, sans son entête ni son titre — la page d'accueil les porte déjà. */
function corps(string $html): string
{
    $start = strpos($html, '<div class="wrap">');
    $end = strrpos($html, '</div>');

    return $start === false ? $html : substr($html, $start, $end - $start + 6);
}

/**
 * Le contenu de toutes les balises d'un nom donné, sans les balises.
 *
 * SANS EXPRESSION RÉGULIÈRE, ET C'EST DÉLIBÉRÉ : la maquette embarque ses sprites en clair dans ses styles, ce qui fait un document de plus d'un mégaoctet, et une
 * expression paresseuse sur un tel texte dépasse la limite de retour arrière du moteur — elle ne rend alors RIEN, sans le dire. La page sortait donc sans un seul
 * style ni une seule image, et se construisait sans erreur. Deux recherches de position font le même travail et ne mentent pas.
 */
function contenus(string $html, string $tag): string
{
    $open = "<{$tag}>";
    $close = "</{$tag}>";
    $parts = [];
    $at = 0;
    while (($start = strpos($html, $open, $at)) !== false) {
        $from = $start + strlen($open);
        $end = strpos($html, $close, $from);
        if ($end === false) {
            break;
        }
        $parts[] = substr($html, $from, $end - $from);
        $at = $end + strlen($close);
    }

    return implode("\n", $parts);
}

/** Renomme les classes partagées d'un document : dans son balisage, dans ses styles et dans ses sélecteurs. Un seul passage, une seule table, aucune moitié de renommage possible. */
function prefixer(string $text, string $prefix): string
{
    foreach (PARTAGES as $name) {
        $text = preg_replace('/(?<=class=")' . preg_quote($name, '/') . '(?=[" ])/', $prefix . $name, $text);
        $text = preg_replace('/(?<=class=")((?:[\w-]+ )*)' . preg_quote($name, '/') . '(?=[" ])/', '$1' . $prefix . $name, $text);
        // A SELECTOR IS RECOGNISED BY WHAT SURROUNDS IT, NOT BY A LIST OF CASES. This line used to enumerate what could follow a name — space, brace, comma, colon, bracket, quote — and one was
        // missing: the DOT of `.pose.s-tr-060`, two classes required on the same element. The element took the new name while its rule kept the old one, so nothing applied any more: the mock-up's
        // sprites were placed, named on hover, and invisible.
        //
        // WHAT PRECEDES MATTERS AS MUCH, and forgetting it broke the zoom buttons: a first fix renamed every `.name` and turned `dataset.zoom` into `dataset.mq-zoom`. A property access is preceded
        // by a name, a closing parenthesis or a bracket; a selector never is. Both ends are stated, and neither is a list to keep up to date.
        $text = preg_replace('/(?<![\w\-\)\]])\.' . preg_quote($name, '/') . '(?![\w-])/', '.' . $prefix . $name, $text);
        $text = str_replace(["classList.toggle('" . $name . "'", 'classList.add(\'' . $name . '\'', 'classList.remove(\'' . $name . '\''],
            ["classList.toggle('" . $prefix . $name . "'", 'classList.add(\'' . $prefix . $name . '\'', 'classList.remove(\'' . $prefix . $name . '\''], $text);
    }

    return $text;
}

$blocks = '';
$allStyles = '';
$allScripts = '';
foreach ($sources as $source) {
    if (!is_file($source['fichier'])) {
        throw new RuntimeException("{$source['fichier']} n'existe pas — construis d'abord le plan et la maquette de la scène");
    }
    $html = file_get_contents($source['fichier']);
    $style = contenus($html, 'style');
    $script = contenus($html, 'script');
    $body = corps($html);
    if ($source['prefixe']) {
        $style = prefixer($style, $source['prefixe']);
        $script = prefixer($script, $source['prefixe']);
        $body = prefixer($body, $source['prefixe']);
    }
    $allStyles .= "\n/* ---- {$source['cle']} ---- */\n" . $style;
    $allScripts .= "\n/* ---- {$source['cle']} ---- */\n" . $script;
    $blocks .= <<<HTML

  <section class="volet" data-cle="{$source['cle']}">
    <button type="button" class="plier" aria-expanded="true">
      <span class="chevron" aria-hidden="true">▾</span>
      <span class="titre">{$source['titre']}</span>
    </button>
    <p class="volet-quoi">{$source['quoi']}</p>
    <div class="volet-corps">{$body}</div>
  </section>

HTML;
}

$page = <<<'HTML'
<title>Maquette Campagne</title>
{$favicon}

<style>
{$styles}

/* ---- la page qui porte les deux ---- */
  /* THIS PAGE HAD NO MARGIN AT ALL and stuck to the edge of the screen, its title clipped (operator, 2026-08-07). It never had one: published, it sat in a frame that gave it some; served as it
     stands, nobody does that for it any more. Its measure is that of its two sources, so the same content keeps its width going from /parc to /maquette-campagne. */
  .page {
    width: min(100%, 1760px);
    margin: 0 auto;
    padding: clamp(1.5rem, 4vw, 3rem) clamp(1rem, 3vw, 2rem) 5rem;
  }
  .page-tete { max-width: 64ch; }
  .page-tete h1 { margin: 0 0 .4rem; }
  .volet { margin-top: 1.2rem; border: 1px solid var(--line, #333a2f); border-radius: 4px; overflow: hidden; }
  .plier {
    display: flex; align-items: center; gap: .6rem; width: 100%; padding: .8rem 1rem;
    background: none; border: 0; border-bottom: 1px solid var(--line, #333a2f); color: inherit; font: inherit; font-weight: 600; text-align: left; cursor: pointer;
  }
  .chevron { display: inline-block; transition: transform .15s; }
  .volet[data-plie="oui"] .chevron { transform: rotate(-90deg); }
  .volet[data-plie="oui"] .plier { border-bottom: 0; }
  .volet-quoi { margin: 0; padding: .8rem 1rem 0; }
  .volet[data-plie="oui"] .volet-quoi,
  .volet[data-plie="oui"] .volet-corps { display: none; }
</style>

<div class="page">
  <header class="page-tete">
    <h1>Maquette Campagne</h1>
    <p>32 × 24 cases, au format de composition du projet. Elle tient en un écran et se rejuge en quelques secondes : c'est là qu'on regarde les pièces et leurs jonctions,
    là où le parc de 64 × 48 sert à l'assemblage final. Les deux vues se replient à volonté, et la page retrouve l'état où tu l'as laissée.</p>
  </header>
{$blocks}
</div>

<script>
{$scripts}

/* ---- le pli des deux sections, retenu d'une visite à l'autre ---- */
(function () {
  var MEMOIRE = 'gatebeast-maquette-campagne-plis';
  var plis = {};
  try { plis = JSON.parse(localStorage.getItem(MEMOIRE)) || {}; } catch (erreur) { plis = {}; }

  document.querySelectorAll('.volet').forEach(function (volet) {
    var cle = volet.dataset.cle;
    var bouton = volet.querySelector('.plier');
    function appliquer(plie) {
      volet.dataset.plie = plie ? 'oui' : 'non';
      bouton.setAttribute('aria-expanded', plie ? 'false' : 'true');
      plis[cle] = plie;
      try { localStorage.setItem(MEMOIRE, JSON.stringify(plis)); } catch (erreur) { /* un cadre peut refuser le stockage : le pli vaut alors pour la visite */ }
    }
    bouton.addEventListener('click', function () { appliquer(volet.dataset.plie !== 'oui'); });
    appliquer(Boolean(plis[cle]));
  });
})();
</script>
{$reloadMarkup}
{$reloadScript}
HTML;

$page = strtr($page, ['{$styles}' => $allStyles . "\n" . $reload->styles(), '{$scripts}' => $allScripts, '{$blocks}' => $blocks,
    '{$favicon}' => $favicon->tag(), '{$reloadMarkup}' => $reload->markup(), '{$reloadScript}' => $reload->script('/maquette-campagne')]);
file_put_contents("$here/page.html", $page);
printf("review-server/maquette-campagne/page.html — %d section(s) fusionnée(s), %.1f Ko\n", count($sources), strlen($page) / 1024);
