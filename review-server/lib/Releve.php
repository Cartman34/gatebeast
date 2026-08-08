<?php
/**
 * USAGE
 *   Give a review page the ending it always has: the operator ticks and writes, then copies one text to paste back. Used by any page that carries a relevé.
 *
 * INTENTION
 *   The review pages all end the same way: the operator ticks or writes things, then copies one text to paste back into the conversation. That ending was written three times — sprites page, plan,
 *   mock-up — with three copies of the same copy-to-clipboard dance, and only one of them had the fixed button the operator asked for. One module, and every page that carries a relevé gains the same
 *   button, at the same place, with the same behaviour.
 *
 *   THE COPY GOES THROUGH A HIDDEN FIELD, never through the clipboard API: an artifact runs in a frame where the direct call is refused, and it fails SILENTLY — the button looks dead. Selecting text
 *   in a field and copying it works everywhere. When even that is refused, the text is put in front of the operator, already selected, rather than lost.
 *
 *   THE TEXT ITSELF IS FOLDED AWAY by default: it is long, it is read once in a while, and it took the bottom of the page for nothing. The button is what gets used.
 *
 *   The page owns WHAT is copied and this module owns HOW: `window.construireReleve()` returns the text, and everything else — the fixed button, the fold, the states, the failure — lives here.
 */

class Releve
{
    private static ?self $instance = null;

    /** L'instance du service. C'est la SEULE méthode statique ici, et elle ne fait que ça : tout le travail est d'instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    public function styles(): string
    {
        return <<<'CSS'
  .releve { margin-top: 32px; padding: 16px; background: var(--card, #1c211a); border: 1px solid var(--line, #333a2f); border-radius: 4px; }
  .releve-head { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
  .releve-head h2 { margin: 0; font-size: 1.05rem; flex: 1 1 auto; }
  .releve-intro { margin: 10px 0 0; color: var(--muted, #9aa192); }
  .releve-texte { margin: 12px 0 0; padding: 12px; max-height: 40vh; overflow: auto; white-space: pre-wrap;
                  background: var(--bg, #14170f); border: 1px solid var(--line, #333a2f); border-radius: 3px; }
  .releve-texte[hidden] { display: none; }
  .releve-etat { margin: 0; font-size: .85rem; color: var(--muted, #9aa192); }
  /* LE BOUTON FIXE, EN BAS À DROITE : le relevé se copie de n'importe où dans la page, sans avoir à redescendre jusqu'à lui. C'est ce que l'opérateur a demandé, et
     c'est ce qui manquait à deux des trois pages. */
  /* LES BOUTONS PORTENT L'HABILLAGE DU PROJET, ILS NE SONT PLUS NUS. Sans règle à eux, « Copier le relevé » et « Voir le texte » tombaient sur le bouton par défaut du
     navigateur — deux pavés gris au milieu d'une page sombre. L'échelle est celle du constructeur d'origine : chasse fixe, douze pixels, remplissage 6/11, rayon 3. */
  .releve-copier, .releve-deplier, .releve-fixe {
    font-family: ui-monospace, monospace; font-size: 12px; letter-spacing: .04em; padding: 6px 11px;
    background: var(--card, #1c211a); border: 1px solid var(--line, #333a2f); border-radius: 3px; color: var(--ink, inherit); cursor: pointer;
  }
  .releve-copier:hover, .releve-deplier:hover, .releve-fixe:hover { border-color: var(--accent, #8fbf9a); color: var(--accent, #8fbf9a); }
  /* UNE BARRE FIXE PLEINE LARGEUR, PAS UN BOUTON FLOTTANT — c'est ce que posait le constructeur d'origine, et la migration l'avait réduite à son seul bouton (opérateur,
     2026-08-07 : « l'encart fixe en bas… là y'a que le bouton, avant, y'avait un panel dédié »). Elle porte le compte de ce qui est relevé, ce qu'un bouton seul ne dit pas :
     on sait d'un coup d'œil s'il reste quelque chose à copier. */
  .releve-barre {
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 200;
    display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px;
    padding: 9px 18px; background: var(--card, #1c211a); border-top: 1px solid var(--line, #333a2f);
    font-size: 12px;
  }
  .releve-compte { flex: 1 1 auto; margin: 0; font-variant-numeric: tabular-nums; color: var(--muted, #9aa192); }
  .releve-compte strong { color: var(--ink, inherit); font-size: 14px; }
CSS;
    }

    public function markup(string $title, string $intro = 'Rien n\'est envoyé : le bouton copie tout. Le texte lui-même ne s\'affiche que si vous le demandez.'): string
    {
        $title = htmlspecialchars($title, ENT_QUOTES);
        $intro = htmlspecialchars($intro, ENT_QUOTES);

        return <<<HTML
  <section class="releve">
    <div class="releve-head">
      <h2>{$title}</h2>
      <button type="button" class="releve-copier">Copier le relevé</button>
      <button type="button" class="releve-deplier" aria-expanded="false">Voir le texte</button>
      <p class="releve-etat" role="status" aria-live="polite"></p>
    </div>
    <p class="releve-intro">{$intro}</p>
    <pre class="releve-texte" hidden></pre>
  </section>
  <div class="releve-barre">
    <p class="releve-compte" id="releve-compte"></p>
    <button type="button" class="releve-fixe">Copier le relevé</button>
  </div>
HTML;
    }

    public function script(): string
    {
        return <<<'JS'
(function () {
  var texte = document.querySelector('.releve-texte');
  var etat = document.querySelector('.releve-etat');
  var deplier = document.querySelector('.releve-deplier');

  function contenu() {
    return typeof window.construireReleve === 'function' ? window.construireReleve() : '';
  }

  function dire(message) {
    if (etat) { etat.textContent = message; }
    window.setTimeout(function () { if (etat) { etat.textContent = ''; } }, 2400);
  }

  function copier() {
    var value = contenu();
    if (texte) { texte.textContent = value; }
    var holder = document.createElement('textarea');
    holder.value = value;
    holder.setAttribute('readonly', 'readonly');
    holder.style.position = 'fixed';
    holder.style.opacity = '0';
    document.body.appendChild(holder);
    holder.select();
    var done = false;
    try { done = document.execCommand('copy'); } catch (error) { done = false; }
    document.body.removeChild(holder);
    if (done) { dire('Copié'); return; }
    if (texte) {
      texte.hidden = false;
      if (deplier) { deplier.setAttribute('aria-expanded', 'true'); deplier.textContent = 'Masquer le texte'; }
    }
    dire('Copie refusée par le cadre — le texte est ci-dessous, à copier à la main.');
  }

  Array.prototype.forEach.call(document.querySelectorAll('.releve-copier, .releve-fixe'), function (button) {
    button.addEventListener('click', copier);
  });

  /* LE COMPTE SE TIENT À JOUR TOUT SEUL : la barre ne sert à rien si elle n'annonce pas ce qu'il y a à copier. Le relevé se reconstruit à chaque frappe et à chaque clic —
     il tient dans un souffle —, et on n'y lit que son nombre de lignes utiles. */
  var compte = document.getElementById('releve-compte');
  function dire_compte() {
    if (!compte) { return; }
    var utiles = contenu().split('\n').filter(function (ligne) { return ligne.trim().startsWith('- '); }).length;
    compte.textContent = '';
    var chiffre = document.createElement('strong');
    chiffre.textContent = String(utiles);
    compte.appendChild(chiffre);
    compte.appendChild(document.createTextNode(utiles > 1 ? ' points relevés' : ' point relevé'));
  }
  document.addEventListener('input', dire_compte);
  document.addEventListener('change', dire_compte);
  dire_compte();

  if (deplier && texte) {
    deplier.addEventListener('click', function () {
      var show = texte.hidden;
      if (show) { texte.textContent = contenu(); }
      texte.hidden = !show;
      deplier.setAttribute('aria-expanded', show ? 'true' : 'false');
      deplier.textContent = show ? 'Masquer le texte' : 'Voir le texte';
    });
  }
})();
JS;
    }
}
