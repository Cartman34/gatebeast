<?php
/**
 * USAGE
 *   Le relevé d'une page PUBLIÉE : `Survey::get()->markup()` pose la barre, `Survey::get()->script()` la fait vivre. Une page servie n'en met aucun des deux.
 *
 * INTENTION
 *   IL N'EXISTE QUE LÀ OÙ IL N'Y A PLUS AUCUN AUTRE CANAL (opérateur, 2026-08-12 : « je n'aurai que le mobile, il faut donc le système de relevé »). Tous les
 *   relevés ont été retirés le matin même, et c'était juste : une page servie écrit ses votes sur le serveur au moment du clic. Une page PUBLIÉE, elle, ne peut
 *   appeler personne — ses votes tiennent dans le navigateur, et le seul moyen de les faire sortir de l'appareil est un texte à coller.
 *
 *   TENU ICI PLUTÔT QUE DANS CHAQUE PAGE : deux pages le portent déjà, et c'est exactement ainsi que la première version s'était retrouvée en trois exemplaires
 *   qui avaient divergé. Ce que la page fournit, c'est la manière de lire SES votes ; le reste — la barre, la copie, le repli quand le presse-papiers refuse —
 *   est le même partout.
 */

class Survey
{
    private static ?self $instance = null;

    /** L'instance du service. C'est la SEULE méthode statique ici, et elle ne fait que ça : tout le travail est d'instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** La barre, en bas de l'écran, où le pouce l'atteint sur un mobile. */
    public function markup(): string
    {
        return <<<'HTML'
<div class="releve">
  <p class="releve-compte" hidden></p>
  <button type="button" class="releve-copier">Copier le relevé</button>
</div>
HTML;
    }

    /**
     * Le relevé, assemblé et copié.
     *
     * LA COPIE PASSE PAR UN CHAMP CACHÉ : l'appel direct au presse-papiers est refusé dans le cadre où vit un artefact, et il échoue SANS RIEN DIRE — le bouton
     * paraît alors cassé. Si même cela échoue, le texte s'affiche tout sélectionné plutôt que d'être perdu.
     *
     * `$title` ouvre le texte collé, et `$mots` traduit chaque acte : ce sont les deux seules choses qui changent d'une page à l'autre.
     *
     * ATTENTION AUX ÉCHAPPEMENTS : CE HEREDOC EST INTERPOLÉ (`<<<JS`, sans quotes), donc PHP y lit les séquences d'échappement. Un `\n` écrit dans une chaîne
     * JavaScript devient un VRAI retour à la ligne au milieu de cette chaîne, le script ne s'analyse plus, et la page perd tout son comportement **sans rien
     * dire** : le bouton reste là et ne fait rien. C'est arrivé le 2026-08-12, sur ce fichier, à la ligne du commentaire. Un saut de ligne destiné au
     * JavaScript s'écrit donc `\\n`.
     */
    public function script(string $title, array $mots): string
    {
        $words = json_encode($mots, JSON_UNESCAPED_UNICODE);
        $heading = json_encode($title, JSON_UNESCAPED_UNICODE);

        return <<<JS
<script>
(function () {
  var barre = document.querySelector('.releve');
  var compte = barre.querySelector('.releve-compte');
  var bouton = barre.querySelector('.releve-copier');
  var MOTS = {$words};

  window.gatebeastReleve = function () {
    var lignes = [];
    Array.prototype.forEach.call(document.querySelectorAll('.acts'), function (bloc) {
      var id = bloc.getAttribute('data-id');
      var choisi = bloc.querySelector('input:checked');
      var carte = bloc.closest('article');
      var champ = carte.querySelector('.comment');
      var mot = (champ && champ.value.trim()) || '';
      /* UNE CARTE SANS VOTE MAIS AVEC UN COMMENTAIRE ENTRE QUAND MÊME : ce qu'il a pris la peine d'écrire est ce qu'il faut me faire parvenir, vote ou pas. */
      if (!choisi && !mot) { return; }
      var nom = carte.querySelector('h2').textContent;
      var ligne = id + ' ' + nom + ' : ' + (choisi ? MOTS[choisi.getAttribute('data-act')] : 'sans vote');
      lignes.push(mot ? ligne + '\\n    — ' + mot : ligne);
    });
    compte.textContent = lignes.length + ' à transmettre';
    compte.hidden = lignes.length === 0;

    return lignes;
  };

  /* TROIS CHEMINS, DU PLUS SÛR AU PLUS RUSTIQUE, ET LE DERNIER NE PEUT PAS ÉCHOUER. Le presse-papiers moderne est celui qui marche sur un mobile ; il n'existe
     qu'en contexte sécurisé et peut être refusé dans un cadre. Le champ caché avec `execCommand` est le vieux chemin, refusé lui aussi selon le cadre. Si les
     deux tombent, le texte s'affiche tout sélectionné : il reste un geste à faire, mais rien n'est perdu — un bouton qui échoue en silence, si. */
  function replier(texte) {
    var visible = barre.querySelector('.releve-texte') || document.createElement('textarea');
    visible.className = 'releve-texte';
    visible.value = texte;
    barre.appendChild(visible);
    visible.select();
  }

  function byTheOldPath(texte) {
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

    return fait;
  }

  function dire(fait, texte) {
    bouton.textContent = fait ? 'Copié' : 'Copie refusée — sélectionne le texte';
    if (!fait) { replier(texte); }
    setTimeout(function () { bouton.textContent = 'Copier le relevé'; }, 2000);
  }

  bouton.addEventListener('click', function () {
    var lignes = window.gatebeastReleve();
    var texte = {$heading} + '\\n' + (lignes.length ? lignes.join('\\n') : 'Aucun vote.');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texte).then(function () {
        dire(true, texte);
      }, function () {
        dire(byTheOldPath(texte), texte);
      });

      return;
    }
    dire(byTheOldPath(texte), texte);
  });

  window.gatebeastReleve();
})();
</script>
JS;
    }
}
