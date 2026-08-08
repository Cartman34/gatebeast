<?php
/**
 * USAGE
 *   The remarks tool of the review pages, held once. A page includes Remarks::get()->script(), then calls
 *   window.gatebeastRemarks.attach(section, adapter) for each tool it carries.
 *
 *   The adapter answers THREE questions, and three only:
 *     caseSous(x, y)   the cell under a point of the screen, or null outside the grid
 *     marquer(list)    how a commented cell is marked on this support
 *     section          the name this tool's remarks are stored under
 *   It may also give `nature(cell)`, the sentence naming what a cell holds; without it a cell is named by its coordinates alone.
 *
 * INTENTION
 *   THE SAME TOOL WAS WRITTEN TWICE, and the Campagne page carries both copies — one for the composition plan, one for the mounted mock-up. They do the same
 *   thing: hover naming the cell, click opening the entry, the list of remarks, the mark on the commented cell, removal, copying the summary, clearing, escape.
 *   Two copies drift: the plan learned to file a settled remark and to reopen it, the mock-up never did, and the operator has the same need on both.
 *
 *   WHAT DIFFERS IS THE SUPPORT, AND NOTHING ELSE. The plan is a vector drawing whose marks live in the drawing's own frame; the mock-up is a scene of elements
 *   whose marks are laid over it in pixels. That is the whole of it — so that is what the adapter carries, and everything else is held here once.
 *
 *   PANNING AND ZOOMING ARE NOT PART OF THIS. They belong to the support and differ for good reasons; folding them in would make this module the page itself.
 */

class Remarks
{
    private static ?self $instance = null;

    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** The shared tool, as a script block. Included once per page, whatever the number of tools on it. */
    public function script(): string
    {
        return <<<'JS'
<script>
window.gatebeastRemarks = (function () {
  /* Attaches the remarks tool to a section. `adapter` answers the three questions that depend on the support. */
  function attach(section, adapter) {
    var saisie = section.querySelector(adapter.prefix + 'saisie');
    var saisieOu = section.querySelector(adapter.prefix + 'saisie-ou');
    var saisieTexte = section.querySelector('textarea');
    var supprimer = section.querySelector(adapter.prefix + 'supprimer');
    var rouvrir = section.querySelector(adapter.prefix + 'rouvrir');
    var liste = section.querySelector(adapter.prefix + 'remarques ul');
    var vide = section.querySelector(adapter.prefix + 'remarques-vides');
    /* EVERY copy button, not the first one found: the page carries two — one at the head of the plan, one under the remarks — and wiring only one left the other
       inert. The operator clicked the lower one, under the count of declared cells, and nothing happened: the button was there, listening to nothing. */
    var copiers = Array.prototype.slice.call(section.querySelectorAll(adapter.prefix + 'copier'));
    var effacer = section.querySelector(adapter.prefix + 'effacer');
    var survol = section.querySelector(adapter.prefix + 'survol');
    var zone = adapter.zone || section;
    var titre = adapter.titre || '';
    var remarques = [];
    var vise = null;

    /* A SETTLED REMARK IS FILED, NOT DELETED. The published plan carries the list of cells that have been dealt with; the page marks them settled: their cross
       turns pale grey on the drawing, they leave the summary, and the text stays readable with one click. The operator may reopen one — it becomes active again
       for him, and that choice lives only in his browser: the agent knows nothing beyond what the plan declares. */
    var traitees = {};
    (adapter.resolues || []).forEach(function (cle) { traitees[cle] = true; });

    var MEMOIRE_ROUVERTES = 'gatebeast-rouvertes-' + adapter.section;
    var rouvertes = {};
    try {
      rouvertes = JSON.parse(localStorage.getItem(MEMOIRE_ROUVERTES)) || {};
    } catch (erreur) {
      rouvertes = {};
    }

    function resolue(remarque) {
      var cle = remarque.colonne + ',' + remarque.ligne;

      return Boolean(traitees[cle]) && !rouvertes[cle] && !remarque.neuve;
    }

    function nature(ou) {
      return adapter.nature ? adapter.nature(ou) : '';
    }

    /* REMARKS LIVE IN THE REPOSITORY, NOT IN THE BROWSER (operator, 2026-08-07): there they were lost at the slightest change of address, nobody but their author
       could read them, and they had to be copied out by hand. The server holds them; the page asks for them on opening and hands the whole list back at every
       change. */
    function retenir() {
      if (window.gatebeastNotes) { window.gatebeastNotes.save(adapter.section, remarques); }
    }

    function marquer() {
      adapter.marquer(remarques.map(function (remarque) {
        return {colonne: remarque.colonne, ligne: remarque.ligne, reglee: resolue(remarque)};
      }));
    }

    function afficher() {
      liste.innerHTML = '';
      vide.hidden = remarques.length > 0;
      remarques.forEach(function (remarque) {
        var ligne = document.createElement('li');
        var ou = document.createElement('span');
        ou.className = 'ou';
        ou.textContent = '(' + remarque.colonne + ',' + remarque.ligne + ')';
        var quoi = document.createElement('span');
        quoi.className = 'quoi';
        quoi.textContent = remarque.texte;
        if (resolue(remarque)) {
          ligne.className = 'remarque--reglee';
        }
        var retirer = document.createElement('button');
        retirer.type = 'button';
        retirer.textContent = 'Retirer';
        retirer.addEventListener('click', function () {
          remarques.splice(remarques.indexOf(remarque), 1);
          retenir();
          marquer();
          afficher();
        });
        ligne.appendChild(ou);
        ligne.appendChild(quoi);
        ligne.appendChild(retirer);
        liste.appendChild(ligne);
      });
      /* Both commands stay OFFERED, even with no remark: a button that appears and disappears with the state forces you to guess whether it exists, and the
         operator noticed the gap with the sprites page, where they are always there. Copying an empty summary costs nothing; not finding the button does. */
      copiers.forEach(function (bouton) { bouton.disabled = false; });
      effacer.disabled = false;
    }

    adapter.surface.addEventListener('mousemove', function (evenement) {
      var ou = adapter.caseSous(evenement.clientX, evenement.clientY);
      if (!ou) {
        survol.hidden = true;
        return;
      }
      var cadre = zone.getBoundingClientRect();
      survol.textContent = '(' + ou.colonne + ',' + ou.ligne + ') ' + nature(ou);
      survol.hidden = false;
      survol.style.left = Math.max(4, Math.min(evenement.clientX - cadre.left + 14, cadre.width - survol.offsetWidth - 4)) + 'px';
      survol.style.top = Math.max(4, evenement.clientY - cadre.top - survol.offsetHeight - 10) + 'px';
    });

    adapter.surface.addEventListener('mouseleave', function () {
      survol.hidden = true;
    });

    adapter.surface.addEventListener('click', function (evenement) {
      var ou = adapter.caseSous(evenement.clientX, evenement.clientY);
      if (!ou) {
        return;
      }
      vise = ou;
      saisieOu.textContent = 'Case (' + ou.colonne + ',' + ou.ligne + ') — ' + nature(ou);
      /* A cell already commented reopens ITS remark, to correct or complete it: an empty field would invite rewriting it, and one would end up with two opinions
         on the same cell without knowing which is the good one. */
      var deja = remarques.filter(function (remarque) {
        return remarque.colonne === ou.colonne && remarque.ligne === ou.ligne;
      })[0];
      saisieTexte.value = deja ? deja.texte : '';
      /* The delete button appears only where there is something to delete: on a blank cell it would mean nothing. */
      supprimer.hidden = !deja;
      /* A settled remark reopens with one click: it becomes active again, returns to the summary, and its mark takes its colour back. */
      if (rouvrir) { rouvrir.hidden = !(deja && resolue(deja)); }
      saisie.hidden = false;

      /* The card opens where the click landed, then folds back into the zone if it would stick out: an entry overflowing the plan is an entry you go looking for
         instead of reading. */
      var cadre = zone.getBoundingClientRect();
      saisie.style.left = Math.max(8, Math.min(evenement.clientX - cadre.left + 14, cadre.width - saisie.offsetWidth - 8)) + 'px';
      saisie.style.top = Math.max(8, Math.min(evenement.clientY - cadre.top + 14, cadre.height - saisie.offsetHeight - 8)) + 'px';
      /* preventScroll: without it, giving the field the keyboard scrolls the page onto it, and the plan leaves the screen at the very moment it is commented. */
      saisieTexte.focus({preventScroll: true});
    });

    var poser = section.querySelector(adapter.prefix + 'poser');
    poser.addEventListener('click', function () {
      var texte = saisieTexte.value.trim();
      if (!vise || !texte) {
        return;
      }
      /* A cell carries one remark: the one just written replaces the previous instead of sitting beside it. */
      remarques = remarques.filter(function (remarque) {
        return !(remarque.colonne === vise.colonne && remarque.ligne === vise.ligne);
      });
      /* NEUVE — written AFTER the resolution the plan declares. Without that mark, a remark laid on an already settled cell was born grey, and so read as settled
         although it had just been written; the operator saw it on « (47,43) Herbe rase ». What the plan declares settled are the remarks that came before it,
         never those that will follow. */
      remarques.push({colonne: vise.colonne, ligne: vise.ligne, texte: texte, neuve: true});
      retenir();
      saisie.hidden = true;
      vise = null;
      marquer();
      afficher();
    });

    if (rouvrir) {
      rouvrir.addEventListener('click', function () {
        if (!vise) {
          return;
        }
        rouvertes[vise.colonne + ',' + vise.ligne] = true;
        try {
          localStorage.setItem(MEMOIRE_ROUVERTES, JSON.stringify(rouvertes));
        } catch (erreur) {
          /* With no storage the reopening does not survive a reload; the text itself is never at stake. */
        }
        rouvrir.hidden = true;
        marquer();
        afficher();
      });
    }

    supprimer.addEventListener('click', function () {
      if (!vise) {
        return;
      }
      remarques = remarques.filter(function (remarque) {
        return !(remarque.colonne === vise.colonne && remarque.ligne === vise.ligne);
      });
      retenir();
      saisie.hidden = true;
      vise = null;
      marquer();
      afficher();
    });

    section.querySelector(adapter.prefix + 'annuler').addEventListener('click', function () {
      saisie.hidden = true;
      vise = null;
    });

    saisieTexte.addEventListener('keydown', function (evenement) {
      if (evenement.key === 'Enter' && (evenement.metaKey || evenement.ctrlKey)) {
        poser.click();
      }
    });

    copiers.forEach(function (copier) {
      copier.addEventListener('click', function () {
        /* The summary carries ONLY what is still waiting: handing back an already settled remark would have it done again. */
        var vivantes = remarques.filter(function (remarque) { return !resolue(remarque); });
        var texte = titre + '\n' + (vivantes.length ? vivantes.map(function (remarque) {
          return '(' + remarque.colonne + ',' + remarque.ligne + ') : ' + remarque.texte;
        }).join('\n') : 'Aucune remarque.');
        /* COPYING GOES THROUGH A HIDDEN FIELD, as on the sprites page where it has always worked. The direct clipboard call is refused inside the frame this
           artifact lives in: it fails without a word, and the button looks broken. Selecting the text in a field and copying that works everywhere. */
        var holder = document.createElement('textarea');
        holder.value = texte;
        holder.setAttribute('readonly', 'readonly');
        holder.style.position = 'fixed';
        holder.style.opacity = '0';
        document.body.appendChild(holder);
        holder.select();
        var done = false;
        try {
          done = document.execCommand('copy');
        } catch (erreur) {
          done = false;
        }
        document.body.removeChild(holder);

        if (done) {
          copier.textContent = 'Copié';
          setTimeout(function () { copier.textContent = 'Copier le récapitulatif'; }, 1600);
          return;
        }
        /* Nothing could be copied: the text is put in front of the eyes and already selected, rather than left to be reconstructed. */
        saisieOu.textContent = 'Récapitulatif — à copier à la main';
        saisieTexte.value = texte;
        saisie.hidden = false;
        supprimer.hidden = true;
        saisie.style.left = '8px';
        saisie.style.top = '8px';
        saisieTexte.select();
      });
    });

    effacer.addEventListener('click', function () {
      remarques = [];
      retenir();
      marquer();
      afficher();
    });

    document.addEventListener('keydown', function (evenement) {
      if (evenement.key === 'Escape' && !saisie.hidden) {
        saisie.hidden = true;
        vise = null;
      }
    });

    /* Remarks arrive from the server, therefore after the page opens: it draws once without them, then again once they are here. */
    marquer();
    afficher();
    if (window.gatebeastNotes) {
      window.gatebeastNotes.load(adapter.section, function (chargees) {
        remarques = chargees;
        marquer();
        afficher();
      });
    }
  }

  return {attach: attach};
})();
</script>
JS;
    }
}
