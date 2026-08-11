(function () {
  /* VERDICTS AND COMMENTS HAVE LEFT THE BROWSER FOR THE REPOSITORY (operator, 2026-08-08: « quand c'est fait, tu supprimes le commentaire »). While they lived in
     local storage the agent could neither read them nor erase them: the operator had to copy them out by hand, and nothing survived — not a change of machine,
     not a cleared browser, not even a renamed key, which happened the same day when the three acts moved to English. The Campagne page had already solved exactly
     this: its remarks are versioned files, and the server is the only writer. Same mechanism here, same module. */
  var SECTION = 'verdicts';
  var MEMORY = 'gatebeast-suivi-sprites';
  var state = {};
  var ready = false;

  /* LOCAL STORAGE NOW SERVES ONE PURPOSE ONLY: handing back what it already holds. The operator has verdicts sitting in it from days past; the switch must take
     them over, not lose them. They are poured over ONLY if the repository holds nothing yet for this page — otherwise an old browser would overwrite a more
     recent judgement made elsewhere. Once poured, the local key is erased: it must never again be a second source. */
  function pourOverOnce() {
    var previous = null;
    try { previous = JSON.parse(localStorage.getItem(MEMORY)); } catch (error) { previous = null; }
    if (!previous || !Object.keys(previous).length) { return false; }
    state = previous;
    window.gatebeastNotes.save(SECTION, state);
    try { localStorage.removeItem(MEMORY); } catch (error) { /* nothing to do: the hand-over has already landed in the repository */ }
    return true;
  }

  /* THE REPOSITORY IS THE ONLY COPY, SO NOTHING IS WRITTEN BEFORE IT HAS BEEN READ: `ready` holds the door. Without that guard the first render — which ticks the
     boxes and fills the fields — would head straight back to the server and overwrite what has not arrived yet.
     BUT THE DOOR USED TO SWALLOW WHAT THE OPERATOR HAD JUST WRITTEN. A remark typed before the server answered was not saved — this returned — and the answer then
     overwrote the field with what the repository held: the text vanished from the screen, with nothing said and nothing kept. A remark must leave when it has been
     DEALT WITH, never at the moment it is written. What is edited during that window is now named here and poured back over the answer, which is the right way
     round: what the operator typed a second ago is more recent than what the file holds. */
  var pending = {};
  function remember(id) {
    if (!ready) {
      if (id) { pending[id] = true; }
      return;
    }
    window.gatebeastNotes.save(SECTION, state);
  }

  /* WHAT ARRIVES FROM THE REPOSITORY IS RENDERED ONTO THE PAGE, AND THAT IS A FUNCTION OF ITS OWN. The first render happens at wiring time, over a still-empty
     state, because the repository answers afterwards; when it answers, everything has to be laid down again — boxes, fields, unfolded zones, filled markers.
     Without that second pass the operator would see a blank page and believe his verdicts lost, while they are right there. */
  function render() {
    Array.prototype.forEach.call(document.querySelectorAll('.acts input'), function (box) {
      var id = box.getAttribute('data-id');
      box.checked = Boolean(state[id] && state[id][box.getAttribute('data-act')]);
    });
    Array.prototype.forEach.call(document.querySelectorAll('.comment'), function (field) {
      var id = field.getAttribute('data-id');
      /* A REMARK THAT HAS BEEN DEALT WITH LEAVES THE INTERFACE, AND IT IS KEPT (operator, 2026-08-11: « une image validée peut avoir une remarque, quand elle est
         traitée, elle est conservée de ton côté mais plus affichée dans l'interface »). It used to be shown struck through and grey, which is still showing it.
         The text stays in the store with its date and its reason — scripts/remarks.php writes the mark, `reopen` puts the remark back on display. */
      var handled = state[id] && state[id].handled;
      var text = (!handled && state[id] && state[id].comment) || '';
      field.value = text;
      /* THE FIELD OF A FILED REMARK IS READ-ONLY, and that is what makes hiding it safe: typing into a box we have just emptied would write the empty text over
         the remark being kept, which is the silent loss this rule exists to prevent. Reopening it is one command away. */
      field.readOnly = Boolean(handled);
      var zone = document.querySelector('.comment-zone[data-more="' + id + '"]');
      var opener = document.querySelector('.open-comment[data-open="' + id + '"]');
      if (zone && text) { zone.hidden = false; }
      if (zone && handled) { zone.hidden = true; }
      if (opener) {
        opener.setAttribute('data-filled', text.trim() ? 'true' : 'false');
        opener.setAttribute('aria-expanded', zone && !zone.hidden ? 'true' : 'false');
      }
      var clearButton = document.querySelector('.clear-comment[data-id="' + id + '"]');
      if (clearButton) { clearButton.hidden = !text.trim(); }
      if (opener) { opener.setAttribute('title', handled ? 'Remarque traitée le ' + handled.date + ' — ' + handled.reason : 'Commentaire'); }
    });
    /* The survey count keeps itself up to date on `change`: it need not know where the state came from, only that it moved. */
    document.dispatchEvent(new Event('change'));
    /* AND THE TILES FOLLOW THE VERDICTS THAT JUST ARRIVED: this runs when the repository answers, so the states shown are those of the stored verdicts and not
       those frozen at build time. */
    refreshStates();
  }

  Array.prototype.forEach.call(document.querySelectorAll('.acts input'), function (box) {
    var id = box.getAttribute('data-id');
    var act = box.getAttribute('data-act');
    box.checked = Boolean(state[id] && state[id][act]);
    box.addEventListener('change', function () {
      state[id] = state[id] || {};
      /* A VERDICT IS ONE OF THE THREE, NEVER TWO (operator, 2026-08-08: « je peux cocher les 3 »). Approve, rework and discard exclude one another: an image cannot
         be accepted and rejected at once, and a survey carrying it in two columns tells its reader nothing. They are checkboxes because that is what the look
         asks for — one unticks to go back — but they behave as a single choice: ticking one unticks the others. */
      if (box.checked) {
        Array.prototype.forEach.call(document.querySelectorAll('.acts input[data-id="' + id + '"]'), function (other) {
          if (other !== box) {
            other.checked = false;
            state[id][other.getAttribute('data-act')] = false;
          }
        });
      }
      state[id][act] = box.checked;
      remember(id);
      /* THE SUBJECT'S STATE IS REMADE AT THE MOMENT OF THE VERDICT, not at the next build: that is the defect the operator reported on 2026-08-11. */
      refreshStates();
      /* REFUSING AN IMAGE MEANS SAYING WHY: ticking « À reprendre » or « Écarter » opens the entry zone and gives it the keyboard. Without the reason the retake
         starts blind again — which is what cost three attempts on the fir tree. « Valider » opens nothing: an agreement has nothing to justify. */
      if (box.checked && (act === 'rework' || act === 'discarded')) {
        var zone = document.querySelector('.comment-zone[data-more="' + id + '"]');
        var opener = document.querySelector('.open-comment[data-open="' + id + '"]');
        if (zone) {
          zone.hidden = false;
          if (opener) { opener.setAttribute('aria-expanded', 'true'); }
          var commentField = zone.querySelector('.comment');
          if (commentField) { commentField.focus({preventScroll: true}); }
        }
      }
    });
  });

  /* THE « + » BUTTON OPENS AND CLOSES THE ENTRY ZONE, and the zone opens by itself when it already carries a comment: a written text that cannot be seen is a text
     lost to whoever reopens the page. */
  Array.prototype.forEach.call(document.querySelectorAll('.open-comment'), function (button) {
    var id = button.getAttribute('data-open');
    var zone = document.querySelector('.comment-zone[data-more="' + id + '"]');
    if (!zone) { return; }
    if (state[id] && state[id].comment && !state[id].handled) { zone.hidden = false; button.setAttribute('aria-expanded', 'true'); }
    button.addEventListener('click', function () {
      zone.hidden = !zone.hidden;
      button.setAttribute('aria-expanded', zone.hidden ? 'false' : 'true');
      if (!zone.hidden) { zone.querySelector('.comment').focus(); }
    });
  });

  Array.prototype.forEach.call(document.querySelectorAll('.comment'), function (field) {
    var id = field.getAttribute('data-id');
    if (state[id] && state[id].comment && !state[id].handled) { field.value = state[id].comment; }
    field.readOnly = Boolean(state[id] && state[id].handled);
    field.addEventListener('input', function () {
      /* A FILED REMARK IS NEVER OVERWRITTEN FROM THE PAGE: its box is read-only and empty, so what would be saved here is the emptiness we put there ourselves. */
      if (state[id] && state[id].handled) { return; }
      state[id] = state[id] || {};
      state[id].comment = field.value;
      remember(id);
    });
  });

  /* LEAVING A COMPARISON WITHOUT LEAVING THE SUBJECT (operator, 2026-08-07): the only way out was to untick each variant one by one, or to close the panel — which
     lost the subject being judged. One button leaves it in a single gesture, and it only shows while the comparison lasts. */
  function leaveComparison(list) {
    Array.prototype.forEach.call(list.querySelectorAll('.compare'), function (box) { box.checked = false; });
    Array.prototype.forEach.call(list.querySelectorAll('.variant'), function (variant) { variant.classList.remove('picked'); });
    list.classList.remove('comparison');
  }

  /* A COMPARISON DOES NOT SURVIVE CLOSING THE SUBJECT: reopening a card must show it whole, not in the state it was left in three subjects ago. A forgotten
     selection makes a subject look as though it had only two variants left. */
  Array.prototype.forEach.call(document.querySelectorAll('.fsp-close'), function (button) {
    button.addEventListener('click', function () {
      var panel = button.closest('.fsp');
      var list = panel ? panel.querySelector('.variants') : null;
      if (list) { leaveComparison(list); }
    });
  });

  /* THE BUTTON THAT LEAVES A COMPARISON FROM THE INSIDE (operator, 2026-08-07). Without it, leaving meant unticking each variant one by one, or closing the panel
     — and so losing the subject being judged. It calls exactly the function the close button already called: one single way out of a comparison, correctable in
     one single place. */
  Array.prototype.forEach.call(document.querySelectorAll('.quit-comparison'), function (button) {
    button.addEventListener('click', function () {
      var list = button.closest('.variants');
      if (list) { leaveComparison(list); }
    });
  });

  /* THE COMPARISON: ticking several variants keeps only those on screen, side by side and larger. Unticking everything returns to the whole list. */
  Array.prototype.forEach.call(document.querySelectorAll('.compare'), function (box) {
    box.addEventListener('change', function () {
      var list = box.closest('.variants');
      var chosen = list.querySelectorAll('.compare:checked');
      /* A VARIANT WITH NO IMAGE HAS NO CHECKBOX, AND THAT IS DELIBERATE — but the loop read `.checked` off the result of querySelector without checking it exists.
         On OB-010, thirteen boxes for twenty variants: on the eighth turn the read threw, the handler stopped there, and the NEXT line — the one that sets the
         `comparison` class — was never reached. So comparison engaged on NO subject carrying a variant still to produce, while the variants were marked all the
         same: two boxes ticked, two `picked` set, and nothing on screen. Found with a probe on 2026-08-08; three readings of the code had missed it. */
      Array.prototype.forEach.call(list.querySelectorAll('.variant'), function (variant) {
        var pick = variant.querySelector('.compare');
        variant.classList.toggle('picked', !!pick && pick.checked);
      });
      /* A COMPARISON ONLY ENGAGES FROM TWO: with a single variant ticked it hid all the others, so the second one's checkbox was no longer there to be ticked. One
         could never compare anything but the first with itself (operator, 2026-08-07). */
      list.classList.toggle('comparison', chosen.length > 1);
    });
  });

  /* CLEARING A COMMENT DOES NOT DESTROY IT: the cleared text is kept, and the button offers to restore it as long as nothing else has been written. The operator
     asked for a lossless solution — clearing in one click must not destroy what has just been written. */
  Array.prototype.forEach.call(document.querySelectorAll('.clear-comment'), function (button) {
    var field = button.parentNode.querySelector('.comment');
    var id = button.getAttribute('data-id');
    var opener = document.querySelector('.open-comment[data-open="' + id + '"]');
    var held = null;
    /* THE CROSS STAYS A CROSS, AND THAT IS THE WHOLE POINT: it carries « × » to clear and « ↺ » to restore, never a word. Writing « Effacer » inside it made it
       lose its place and its shape — that is how the cross asked for three times disappeared twice. It hides when there is nothing to clear. */
    function paint() {
      button.textContent = held === null ? '×' : '↺';
      button.hidden = !field.value.trim() && held === null;
      if (opener) { opener.setAttribute('data-filled', field.value.trim() ? 'true' : 'false'); }
    }
    button.addEventListener('click', function () {
      if (held === null) {
        held = field.value;
        field.value = '';
      } else {
        field.value = held;
        held = null;
      }
      state[id] = state[id] || {};
      state[id].comment = field.value;
      remember(id);
      paint();
    });
    field.addEventListener('input', function () { held = null; paint(); });
    paint();
  });

  /* THE OPENING BUTTON SAYS WHETHER THERE IS A TEXT UNDERNEATH, from the moment the page opens and at every keystroke: without it a folded card gives away nothing
     of what it holds, and one has to unfold them all to find what was written. */
  Array.prototype.forEach.call(document.querySelectorAll('.comment'), function (field) {
    var id = field.getAttribute('data-id');
    var opener = document.querySelector('.open-comment[data-open="' + id + '"]');
    if (!opener) { return; }
    function tell() { opener.setAttribute('data-filled', field.value.trim() ? 'true' : 'false'); }
    field.addEventListener('input', tell);
    tell();
  });

  /* THE FILTERS ACT ON THE GRID: they hide the tiles that are not in the asked-for state, and a section left entirely empty hides with them — a heading that stays
     open over nothing makes one believe there is nothing to see, when all that happened is a filter. */
  /* A SUBJECT'S STATE IS REMADE AS SOON AS A VERDICT CHANGES (operator, 2026-08-11: « Quand j'ai jugé tous les variants d'un sujet, il apparait toujours "À
     juger". Vérifie ça pour toutes les situations, ça doit s'actualiser »). It was computed at build time, from the verdict written in the referential, and the
     page never replayed it: the subject stayed « to judge » until the next build, while its images had just been judged under the reader's eyes.
     THE WORDS AND THE ORDER COME FROM THE TEMPLATE, never retyped here: it is the same rule as at build time — what is owed comes first, and « validated » takes
     EVERY variant. Whatever a page verdict does not say keeps the built state: a variant with no image stays to produce, and a verdict written in the
     referential and never touched here stays what it is. */
  function variantStateNow(article) {
    var built = article.getAttribute('data-state');
    var box = article.querySelector('.acts input');
    if (!box) { return built; }
    var verdict = state[box.getAttribute('data-id')] || {};
    if (verdict.rework) { return window.GATEBEAST_STATE_OWED[0]; }
    if (verdict.discarded) { return window.GATEBEAST_STATE_OWED[1]; }
    if (verdict.approved) { return window.GATEBEAST_STATE_VALIDATED; }
    /* NO VERDICT IN THE PAGE MEANS « I KNOW NOTHING MORE THAN THE BUILD DID » — and certainly not « to judge ». Written after breaking it: an image validated in
       the referential and never touched here fell back to « to judge » on opening, which is the defect just fixed, the other way round. */
    return built;
  }
  function subjectStateNow(panel) {
    var states = Array.prototype.map.call(panel.querySelectorAll('.variant'), variantStateNow);
    if (!states.length) { return window.GATEBEAST_STATE_OWED[2]; }
    for (var rank = 0; rank < window.GATEBEAST_STATE_OWED.length; rank += 1) {
      if (states.indexOf(window.GATEBEAST_STATE_OWED[rank]) >= 0) { return window.GATEBEAST_STATE_OWED[rank]; }
    }
    var everyone = states.every(function (one) { return one === window.GATEBEAST_STATE_VALIDATED; });
    return everyone ? window.GATEBEAST_STATE_VALIDATED : window.GATEBEAST_STATE_TO_JUDGE;
  }
  /* THE FILTER COUNTS FOLLOW THE TILES, or « À juger 9 » would sit above zero tiles left to judge — the filter would then say the opposite of what the grid
     shows, and that is the kind of gap one only notices after being misled by it. */
  function refreshStates() {
    var counts = {};
    Array.prototype.forEach.call(document.querySelectorAll('.tile'), function (tile) {
      var panel = document.getElementById('fsp-' + tile.getAttribute('data-subject'));
      if (!panel) { return; }
      var now = subjectStateNow(panel);
      tile.setAttribute('data-state', now);
      var word = tile.querySelector('.tile-state');
      if (word) { word.textContent = window.GATEBEAST_STATE_LABELS[now] || now; }
      counts[now] = (counts[now] || 0) + 1;
    });
    Array.prototype.forEach.call(document.querySelectorAll('.filter'), function (button) {
      var which = button.getAttribute('data-filter');
      var number = button.querySelector('span');
      if (number && which !== window.GATEBEAST_STATE_ALL) { number.textContent = counts[which] || 0; }
    });
    var pressed = document.querySelector('.filter[aria-pressed="true"]');
    if (pressed) { applyFilter(pressed.getAttribute('data-filter')); }
  }

  /* THE FILTER SAYS WHAT IT LEFT VISIBLE, in the words of the original builder — « 12 sujets affichés », and « tout est affiché » when nothing is filtered out.
     Without it, a filter left on makes the project look as though it held three subjects, and nothing on the page says otherwise. */
  var filterState = document.getElementById('filter-state');
  function tellFilterState() {
    var tiles = document.querySelectorAll('.tile');
    var shown = Array.prototype.filter.call(tiles, function (tile) { return !tile.hidden; }).length;
    var pressed = document.querySelector('.filter[aria-pressed="true"]');
    var everything = !pressed || pressed.getAttribute('data-filter') === window.GATEBEAST_STATE_ALL;
    filterState.textContent = shown + (shown > 1 ? ' sujets affichés' : ' sujet affiché') + (everything ? ' — tout est affiché' : '');
  }
  /* ONE PLACE APPLIES A FILTER, and both the click and the state refresh go through it: a state that changes under an active filter must make its tile appear or
     disappear at once, or the grid shows a subject the filter now excludes. */
  function applyFilter(wanted) {
    Array.prototype.forEach.call(document.querySelectorAll('.filter'), function (other) {
      other.setAttribute('aria-pressed', other.getAttribute('data-filter') === wanted ? 'true' : 'false');
    });
    Array.prototype.forEach.call(document.querySelectorAll('.tile'), function (tile) {
      tile.hidden = wanted !== window.GATEBEAST_STATE_ALL && tile.getAttribute('data-state') !== wanted;
    });
    Array.prototype.forEach.call(document.querySelectorAll('.type'), function (section) {
      var tiles = section.querySelectorAll('.tile');
      var visible = Array.prototype.filter.call(tiles, function (tile) { return !tile.hidden; });
      section.hidden = tiles.length > 0 && visible.length === 0;
    });
    tellFilterState();
  }
  Array.prototype.forEach.call(document.querySelectorAll('.filter'), function (button) {
    button.addEventListener('click', function () { applyFilter(button.getAttribute('data-filter')); });
  });
  tellFilterState();

  /* A TEXT OPENS BESIDE THE IMAGE, in the drawer against the right edge, and copies with one button. It does NOT go through the stack of full-screen panels: it
     covers nothing, so it has nothing to stack, and the escape key must close IT before closing the card being read. */
  var drawerBody = document.getElementById('drawer-body');
  var drawerTitle = document.getElementById('drawer-title');
  var drawerPath = document.getElementById('drawer-path');
  var drawer = document.getElementById('drawer');
  /* THE PATH IS SHOWN IN THE DRAWER, UNDER THE BAR AND ABOVE THE TEXT (operator, 2026-08-11) — never under the button label, never in the title: it belongs to the
     text one is reading, not to the control that opens it. */
  function openDrawer(title, path, content) {
    drawerTitle.textContent = title;
    drawerPath.textContent = path || '';
    drawerPath.hidden = !path;
    drawerBody.textContent = content;
    drawer.hidden = false;
    drawer.scrollTop = 0;
    document.body.classList.add('drawer-open');
  }
  function closeDrawer() {
    drawer.hidden = true;
    document.body.classList.remove('drawer-open');
  }
  Array.prototype.forEach.call(document.querySelectorAll('.open-text'), function (button) {
    button.addEventListener('click', function () {
      var carrier = button.nextElementSibling;
      openDrawer(button.getAttribute('data-title'), button.getAttribute('data-path'), carrier ? carrier.textContent : '');
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll('.drawer-close'), function (button) {
    button.addEventListener('click', closeDrawer);
  });
  document.getElementById('drawer-copy').addEventListener('click', function () {
    var holder = document.createElement('textarea');
    holder.value = drawerBody.textContent;
    holder.setAttribute('readonly', 'readonly');
    holder.style.position = 'fixed';
    holder.style.opacity = '0';
    document.body.appendChild(holder);
    holder.select();
    var done = false;
    try { done = document.execCommand('copy'); } catch (error) { done = false; }
    document.body.removeChild(holder);
    this.textContent = done ? 'Copié' : 'Sélectionne et copie à la main';
    var button = this;
    window.setTimeout(function () { button.textContent = 'Copier'; }, 2000);
  });

  /* A FULL-SCREEN PANEL OPENS OVER ANOTHER, IT DOES NOT REPLACE IT (operator, 2026-08-07). Closing one brings back the one underneath, and so on up to the page.
     Replacing lost the subject being judged as soon as a text was opened: one had to reopen the tile and scroll back down to the variant. */
  var panelStack = [];
  /* THE AUTOMATIC PAGE RELOAD MUST GIVE THE PAGE BACK WHERE IT WAS LEFT, PANELS INCLUDED (operator, 2026-08-08: « ça recharge la page et ça ne me ré-ouvre PAS la
     popin où j'étais »). Scrolling was already restored; the stack of open panels was not, so a rebuild while a subject was being judged sent one back to the whole
     board, to reopen and scroll again. The stack is therefore written at every opening and every closing, in session storage — it belongs to this tab and this
     visit, not to the machine. */
  var MEMORY_STACK = 'gatebeast-sprites-panneaux';
  function rememberStack() {
    try {
      sessionStorage.setItem(MEMORY_STACK, JSON.stringify(panelStack.map(function (popin) { return popin.id; })));
    } catch (error) { /* a frame may refuse storage: the page still works */ }
  }
  function pushPanel(popin) {
    if (!popin) { return; }
    popin.hidden = false;
    popin.scrollTop = 0;
    /* EVERY STACKED PANEL GOES ABOVE THE PREVIOUS ONE, and that is what was missing: they all shared one plane, so the text panel — written BEFORE the subject
       panels in the page — opened BEHIND the one being looked at. The button seemed dead while it was doing its job: a probe showed the panel open, with its
       thousands of characters of text, simply invisible. Three readings of the code had given nothing; one simulated click settled it at once. */
    popin.style.zIndex = String(90 + panelStack.length + 1);
    document.body.style.overflow = 'hidden';
    panelStack.push(popin);
    rememberStack();
  }
  function closePanel() {
    /* THE TEXT BELONGS TO THE OPEN CARD: leaving it behind a closed card would show the prompt of a subject nobody is looking at any more. */
    closeDrawer();
    /* CLOSING HIDES WHAT IS VISIBLE, NOT WHAT THE STACK BELIEVES (operator, 2026-08-08). The stack lives in memory: if it starts empty while a panel is on screen
       — storage cleared under the tab, a partial restore — the close button does nothing any more and the panel NEVER closes, page stuck. So we fall back on what
       the eye can see, which is the only truth at that moment. This is not the normal path: it is the net under the normal path. */
    var top = panelStack.pop();
    if (!top) {
      top = document.querySelector('.fsp:not([hidden])');
      if (top) { top.hidden = true; top.style.zIndex = ''; document.body.style.overflow = ''; rememberStack(); }
      return;
    }
    top.hidden = true;
    top.style.zIndex = '';
    if (!panelStack.length) { document.body.style.overflow = ''; }
    rememberStack();
  }
  /* They reopen in the order they were stacked, otherwise the one underneath would come out on top. A panel that has disappeared from the page — a subject removed
     between two builds — is simply skipped: what no longer exists is not reopened, and the page is not refused over it either. */
  try {
    JSON.parse(sessionStorage.getItem(MEMORY_STACK) || '[]').forEach(function (id) {
      pushPanel(document.getElementById(id));
    });
  } catch (error) { /* storage refused or unreadable: the page simply opens closed */ }
  Array.prototype.forEach.call(document.querySelectorAll('.tile'), function (tile) {
    tile.addEventListener('click', function () {
      pushPanel(document.getElementById('fsp-' + tile.getAttribute('data-subject')));
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll('.fsp-close'), function (button) { button.addEventListener('click', closePanel); });
  /* THE DRAWER CLOSES FIRST: it is opened OVER a card being read, so escape must give the card back, not close it along with the drawer. */
  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') { return; }
    if (!drawer.hidden) { closeDrawer(); return; }
    closePanel();
  });

  /* WHAT THE PAGE PUTS IN THE SURVEY; the module says how it is copied. */
  /* THE REPOSITORY IS READ LAST, ONCE EVERYTHING IS WIRED. If it holds something, it is authoritative. If it holds nothing, what the browser still keeps is poured
     over once, and never touched again. And if the server does not answer — page opened as a file, server stopped — the page stays usable but RECORDS NOTHING:
     better a page that does not remember than a page that pretends to. */
  window.gatebeastNotes.load(SECTION, function (received) {
    var typedBefore = state;
    if (received && Object.keys(received).length) {
      state = received;
    } else {
      pourOverOnce();
    }
    /* WHAT THE OPERATOR WROTE WHILE THE SERVER WAS ANSWERING IS KEPT, AND IT WINS. Only the entries he actually touched are poured back — pouring the whole
       pre-load state over would resurrect what he had cleared elsewhere. */
    var restored = Object.keys(pending);
    restored.forEach(function (id) { state[id] = typedBefore[id]; });
    ready = true;
    pending = {};
    if (restored.length) { remember(); }
    render();
  });

  window.construireReleve = function () {
    var lines = ['SUIVI DES SPRITES — RELEVÉ OPÉRATEUR', new Date().toISOString().slice(0, 10), ''];
    var acts = {approved: 'VALIDÉES', rework: 'À REPRENDRE', discarded: 'ÉCARTÉES'};
    Object.keys(acts).forEach(function (act) {
      var taken = Object.keys(state).filter(function (id) { return state[id] && state[id][act]; });
      if (!taken.length) { return; }
      lines.push(acts[act] + ' (' + taken.length + ')');
      taken.forEach(function (id) { lines.push('  - ' + id); });
      lines.push('');
    });
    /* THE SURVEY CARRIES ONLY WHAT IS STILL DUE: handing back a remark already dealt with would have it done a second time. It stays in the file and on the
       card — filed, not deleted — but it is no longer counted as waiting. */
    var commented = Object.keys(state).filter(function (id) { return state[id] && state[id].comment && !state[id].handled; });
    if (commented.length) {
      lines.push('COMMENTAIRES (' + commented.length + ')');
      commented.forEach(function (id) { lines.push('  - ' + id); lines.push('      ' + state[id].comment); });
    }
    return lines.join('\n');
  };
})();
