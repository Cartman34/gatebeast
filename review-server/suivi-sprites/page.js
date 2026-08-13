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
  /* THE PAGE SENDS THE ENTRY IT CHANGED, NOT EVERYTHING IT KNOWS (2026-08-11, after a morning of verdicts was lost). The server lays what arrives over what it
     holds, key by key, so sending one image's verdict is enough — and sending all of them is how a stale tab used to erase what another had just written. When
     no image is named, everything goes: that is the hand-over of what was typed before the repository answered, and there the whole state IS the change. */
  /* THE LOCAL WRITE COMES FIRST, ET ELLE N'EST JAMAIS SAUTÉE: every path that means to keep something goes through here or through rememberSoon, so the net is
     posed in ONE place instead of at each of the three call sites — one forgotten site is a silent hole, and it is the site nobody thinks about that loses. It is
     posed BEFORE the `ready` guard on purpose: what is typed while the repository has not answered is precisely what the net exists for. */
  function remember(id) {
    if (id) { keepLocally(id); }
    if (!ready) {
      if (id) { pending[id] = true; }
      return;
    }
    /* A SEND THAT IS ABOUT TO HAPPEN IS DROPPED WHEN ONE HAPPENS NOW: the timer would repeat the same entry a moment later, and repeating a send is exactly what
       reopens the race below. */
    if (id && timers[id]) {
      window.clearTimeout(timers[id]);
      delete timers[id];
    }
    var change = {};
    if (id) { change[id] = state[id]; }
    window.gatebeastNotes.save(SECTION, id ? change : state);
  }

  /* ONE SEND PER PAUSE, NOT ONE PER KEYSTROKE — AND IT IS A LOSS OF TEXT, NOT A MATTER OF ECONOMY (operator, 2026-08-12: « ta page de suivi de sprite a rafraîchi
     et ça a perdu ce que je notais »). Every character sent its own request, each carrying THE WHOLE comment as it stood at that instant, and the server lays what
     arrives over what it holds. The answers do not come back in the order they were sent — measured on this very server, twenty-seven of forty out of place — so a
     mid-typing snapshot can be written AFTER the full text and truncate it. That is what the stored comment of BT-001-v14 shows: it stops in the middle of a word.
     A single send once typing rests removes the race instead of narrowing it: two requests for one image are never in flight together, a rest being a hundred times
     the round trip measured here.
     THE REST IS THE ONE THE PILE PAGE ALREADY WAITS, and it is written here because these two pages hold their own; if a third needs it, it moves to the module
     they share rather than being copied a third time. */
  var TYPING_REST = 400;
  var timers = {};

  /* AND IL Y A UNE SECONDE ÉCRITURE, QUI EST UN FILET (operator, 2026-08-12: « normalement quand je tape ça doit enregistrer sur le serveur et à défaut au moins
     en local »). The server is the copy that counts; the browser keeps what the server has NOT received — the keystrokes typed before it answered, those a reload
     cut off, those a stopped server refused. The write itself is taken back from where it worked, `git show fbdd9fd:review-server/suivi-sprites/build.php`,
     function `retenir()`: the same try/catch, and the same reason for it — a frame may refuse storage, and the page must still work with the server alone.
     IT HOLDS WHAT IS OWED, NOT A SECOND COPY OF EVERYTHING. A full mirror of the state would come back at the next load and lay a stale tab's judgement over a
     fresher one — the very loss the server-side merge was written to stop. What is written here is an OUTBOX: the entries touched since the last load, dropped
     one by one as soon as a load shows the server holding the same thing. Its limit, written rather than discovered: an entry the server did receive and which
     was then changed ELSEWHERE reads as not received, so this net would pour the older one back. It waits on a save that tells its caller it has landed. */
  var OUTBOX = 'gatebeast-suivi-sprites-attente';
  function readOutbox() {
    try { return JSON.parse(localStorage.getItem(OUTBOX)) || {}; } catch (error) { return {}; }
  }
  function keepLocally(id) {
    try {
      var held = readOutbox();
      held[id] = state[id];
      localStorage.setItem(OUTBOX, JSON.stringify(held));
    } catch (error) { /* a frame may refuse storage: the page still works, with the server as its only copy */ }
  }
  function setOutbox(held) {
    try { localStorage.setItem(OUTBOX, JSON.stringify(held)); } catch (error) { /* same refusal, same answer */ }
  }
  /* THE SERVER WAITS FOR THE PAUSE, THE BROWSER NEVER DOES: the local write costs nothing and cannot be reordered, so it happens at EVERY keystroke — which is
     what makes the pause safe to wait for. Delaying both would trade one loss for another. */
  function rememberSoon(id) {
    keepLocally(id);
    if (timers[id]) { window.clearTimeout(timers[id]); }
    timers[id] = window.setTimeout(function () {
      delete timers[id];
      remember(id);
    }, TYPING_REST);
  }

  /* WHAT ARRIVES FROM THE REPOSITORY IS RENDERED ONTO THE PAGE, AND THAT IS A FUNCTION OF ITS OWN. The first render happens at wiring time, over a still-empty
     state, because the repository answers afterwards; when it answers, everything has to be laid down again — boxes, fields, unfolded zones, filled markers.
     Without that second pass the operator would see a blank page and believe his verdicts lost, while they are right there. */
  /* A RUNE ANCHOR IS PLACED WITH ONE CLICK, THE WAY A VERDICT IS GIVEN, AND THE SERVER IS THE ONE THAT WRITES. The point is read in the pixels of the DELIVERED
     image, never in those of the screen: the card shows the sprite at another width, and the ratio between the two is carried by the markup. Without that
     conversion, a point placed on the forehead of a fox cub seen large would land on its belly in the file.

     THE PAGE DOES NOT RELOAD ITSELF AFTER THE WRITE: the mark follows the cursor at once, and the file is written by the tool that owns it. A page rebuilding
     itself at every click would lose the reading position in the middle of a judgement.

     THE ANCHOR IS NOW PLACED IN THE DRAWER, NOT ON THE THUMBNAIL, and that follows directly from the click that opens a version (operator, 2026-08-12). Two
     gestures cannot share one click on one element: on the grid, clicking the image opens the version; in the drawer, where it is large, the click places the
     rune — which is in any case the right place to aim at a pixel. The wiring is a function because it serves twice: at page load for whatever is not inside a
     card, and on the CLONE the drawer builds, which carries none of its original's listeners. */
  function wireAnchor(picture) {
    picture.addEventListener('click', function (event) {
      var box = picture.getBoundingClientRect();
      var scale = Number(picture.getAttribute('data-delivered')) / box.width;
      var x = Math.round((event.clientX - box.left) * scale * 10) / 10;
      var y = Math.round((event.clientY - box.top) * scale * 10) / 10;
      fetch('/rune-anchor', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({path: picture.getAttribute('data-anchor-for'), x: x, y: y})
      }).then(function (answer) {
        return answer.json().then(function (said) { return {ok: answer.ok, said: said}; });
      }).then(function (result) {
        /* WHAT FAILS SAYS SO, LOUDLY AND ON THE PAGE: a swallowed refusal would let the mark move on screen while the file received nothing — the transparent
           fault this repository forbids by name. The message is the tool's own, word for word. */
        if (!result.ok) {
          picture.setAttribute('data-anchor-fault', result.said.fault || 'refus sans motif');
          return;
        }
        picture.removeAttribute('data-anchor-fault');
        var mark = picture.querySelector('.rune');
        if (mark) {
          var side = parseFloat(mark.getAttribute('width'));
          mark.style.left = ((x / scale) - side / 2) + 'px';
          mark.style.top = ((y / scale) - side / 2) + 'px';
        }
      });
    });
  }

  /* THE LINE THAT ANNOUNCED AN OLDER VERSION'S COMMENT WENT AWAY WITH ITS REASON (2026-08-12): it existed because only the current version showed notes, so a
     remark written on a reworked version became invisible. Every version now carries its own, on its own card — the older one says it itself, right there.
     Checked before removal: that is what the task asked for. */
  /* WHAT AN EARLIER VERSION SHOWS COMES FROM THE STORE TOO, AND WITHOUT THIS IT SHOWED ALMOST NOTHING: its verdict and its comment are built out of the
     referential, which carries neither — eighteen of the twenty-eight judgements the operator has given bear on an earlier version and live in
     review-server/notes/sprites.json alone, under the path of the image. The card said « Jamais jugée » over each of them.
     WHAT THE STORE DOES NOT NAME KEEPS WHAT WAS BUILT, exactly as variantStateNow does: no verdict ticked here means « I know no more than the build did », not
     « never judged ». A FILED REMARK STILL DOES NOT SHOW ITS TEXT (operator, 2026-08-11): the verdict says what was decided, the text stays kept and unshown. */
  function verdictOf(said) {
    if (said.rework) { return window.GATEBEAST_STATE_OWED[0]; }
    if (said.discarded) { return window.GATEBEAST_STATE_OWED[1]; }
    if (said.approved) { return window.GATEBEAST_STATE_VALIDATED; }

    return null;
  }
  function renderPast() {
    Array.prototype.forEach.call(document.querySelectorAll('.past'), function (block) {
      var said = state[block.getAttribute('data-id')];
      if (!said) { return; }
      var now = verdictOf(said);
      var word = block.querySelector('.verdict');
      if (word && now) {
        word.className = 'verdict verdict--' + now;
        word.textContent = window.GATEBEAST_STATE_LABELS[now] || now;
      }
      var text = said.handled ? '' : (said.comment || '');
      var line = block.querySelector('.past-comment');
      if (!text) {
        if (line) { line.remove(); }

        return;
      }
      if (!line) {
        line = document.createElement('p');
        line.className = 'past-comment';
        block.appendChild(line);
      }
      line.textContent = text;
    });
  }

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
      var text = (state[id] && state[id].comment) || '';
      /* THE TEXT IS PUT BACK IN THE FIELD EVEN WHEN THE REMARK IS FILED, and that is the whole of the fix (operator, 2026-08-11: « je dois pouvoir retrouver les
         commentaires d'une version dans l'interface »). Hiding it had emptied the field as well, so opening the zone showed a blank box: the remark was kept, and
         unreachable from the page. It stays FOLDED — a filed remark is not shown by default, that rule is unchanged — but the « + » now opens onto what was
         written, read-only, with the date and the reason of its filing. Cacher n'est pas ranger. */
      field.value = text;
      /* AND IT IS RESIZED THE MOMENT ITS TEXT ARRIVES: the repository answers after the first render, so a field filled here would keep the height it had when
         it was empty — the remark would be there, and only its first two lines readable. */
      fitComment(field);
      /* THE FIELD OF A FILED REMARK IS READ-ONLY, and that is what makes hiding it safe: typing into a box we have just emptied would write the empty text over
         the remark being kept, which is the silent loss this rule exists to prevent. Reopening it is one command away. */
      field.readOnly = Boolean(handled);
      var zone = document.querySelector('.comment-zone[data-more="' + id + '"]');
      var opener = document.querySelector('.open-comment[data-open="' + id + '"]');
      if (zone && text) { zone.hidden = false; }
      if (zone && handled) { zone.hidden = true; }
      if (opener) {
        opener.setAttribute('data-filled', text.trim() ? 'true' : 'false');
        /* THE OPENER SAYS WHICH OF THE TWO IT CARRIES: a remark still waiting, or one already dealt with. Without it both look alike once folded, and the only way
           to tell them apart is to open each one — which is the round trip this line removes. */
        opener.setAttribute('data-handled', handled ? 'true' : 'false');
        opener.setAttribute('aria-expanded', zone && !zone.hidden ? 'true' : 'false');
      }
      var clearButton = document.querySelector('.clear-comment[data-id="' + id + '"]');
      /* A FILED REMARK OFFERS NO CLEARING: the field is read-only, so the button would write nothing and merely look broken. `remarks.php reopen` puts it back. */
      if (clearButton) { clearButton.hidden = !text.trim() || Boolean(handled); }
      if (opener) { opener.setAttribute('title', handled ? 'Remarque traitée le ' + handled.date + ' — ' + handled.reason : 'Commentaire'); }
    });
    renderPast();
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

  /* A COMMENT FIELD IS AS TALL AS WHAT IT HOLDS: two lines at rest, opening as one types up to FOUR lines, after which it scrolls. Taken back verbatim from the
     original Python builder — `git show fbdd9fd^:artefacts/suivi-sprites/build.py`, function `fitNote` — because it had been lost in a rewrite (operator,
     2026-08-12: « j'avais déjà fait implémenter que cette zone de texte doit grandir quand y'a du contenu… tu as perdu la fonctionnalité en cours de route »).
     THE HEIGHT IS MEASURED HERE RATHER THAN SET IN CSS because it depends on the text once wrapped to the field's own width, which only layout knows. Resetting
     the height to "auto" before reading scrollHeight is what lets a field that has grown come back down when the text is deleted.
     TWO LINES AT REST, FOUR AT MOST. Measured alone, a single line gives a slot too shallow to write in — it reads as a broken input rather than a field, and the
     first wrapped word is already hidden. */
  function fitComment(field) {
    var style = window.getComputedStyle(field);
    var line = parseFloat(style.lineHeight);
    var edges = parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
    var frame = parseFloat(style.paddingTop) + parseFloat(style.paddingBottom) + edges;
    field.style.height = 'auto';
    var floor = Math.round(line * 2 + frame);
    var ceiling = Math.round(line * 4 + frame);
    field.style.height = Math.max(floor, Math.min(field.scrollHeight + edges, ceiling)) + 'px';
  }

  Array.prototype.forEach.call(document.querySelectorAll('.comment'), function (field) {
    var id = field.getAttribute('data-id');
    if (state[id] && state[id].comment) { field.value = state[id].comment; }
    field.readOnly = Boolean(state[id] && state[id].handled);
    fitComment(field);
    field.addEventListener('focus', function () { fitComment(field); });
    field.addEventListener('input', function () {
      fitComment(field);
      /* A FILED REMARK IS NEVER OVERWRITTEN FROM THE PAGE: its box is read-only and empty, so what would be saved here is the emptiness we put there ourselves. */
      if (state[id] && state[id].handled) { return; }
      state[id] = state[id] || {};
      state[id].comment = field.value;
      rememberSoon(id);
    });
    /* AND LEAVING THE FIELD SENDS AT ONCE, WITHOUT WAITING FOR THE REST: the page reloads itself when it is rebuilt, and what is owed to the server must not be
       sitting in a timer at that moment. Clicking a verdict, opening a version, closing the panel — every one of those takes the focus, so the text is safe
       before the gesture that follows it. ONLY WHAT IS OWED GOES: a field one merely passes through has no timer waiting, and sending on every blur would put a
       request on the wire for a text nobody touched. */
    field.addEventListener('blur', function () { if (timers[id]) { remember(id); } });
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
      fitComment(field);
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
    /* THE BUILT STATE IS KEPT APART, BECAUSE `data-state` IS NOW REWRITTEN: it is the fallback used when no verdict is ticked here, and a fallback overwritten
       with the computed value falls back on nothing — unticking a verdict would leave the variant showing the state just removed. */
    if (!article.hasAttribute('data-built')) { article.setAttribute('data-built', article.getAttribute('data-state') || ''); }
    var built = article.getAttribute('data-built');
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
    /* THE STATE WRITTEN ON A VARIANT'S HEAD FOLLOWS THE VERDICT JUST TICKED, like the subject tile's: computed once at build time, it would announce « à juger »
       on a variant validated under the reader's own eyes — the defect reported on 2026-08-11 for subjects, and it would hold here for the same reason. */
    Array.prototype.forEach.call(document.querySelectorAll('.variant'), function (variant) {
      var now = variantStateNow(variant);
      variant.setAttribute('data-state', now);
      var word = variant.querySelector('.variant-state');
      if (word) { word.textContent = window.GATEBEAST_STATE_LABELS[now] || now; }
    });
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
  /* UN DRAWER OUVERT SE ROUVRE À L'IDENTIQUE APRÈS UN RECHARGEMENT (opérateur, 2026-08-13). La page se reconstruit et se recharge toute seule dès qu'une sprite
     est produite ou qu'un verdict change : refermé à ce moment-là, le drawer fait perdre sa place au milieu d'un jugement. « À l'identique » veut dire LA MÊME
     VERSION, pas le même sujet — c'est le chemin de son image qui est retenu, la seule chose qui l'identifie. Même mémoire que la pile des panneaux : la session
     de cet onglet, jamais la machine. */
  var MEMORY_VERSION = 'gatebeast-sprites-version';
  function rememberVersion(key) {
    try { sessionStorage.setItem(MEMORY_VERSION, key || ''); } catch (error) { /* a frame may refuse storage: the page still works */ }
  }
  function closeDrawer() {
    returnVersion();
    drawer.hidden = true;
    paging.hidden = true;
    strip.hidden = true;
    rememberVersion('');
    document.body.classList.remove('drawer-open');
  }
  /* SECTION BUTTONS UNFOLD IN PLACE, THEY NO LONGER OPEN THE DRAWER (operator, 2026-08-12): the drawer now carries A WHOLE VERSION, not a text. A button opening
     a drawer that holds something else forced a step backwards to read the next section. */
  Array.prototype.forEach.call(document.querySelectorAll('.open-text'), function (button) {
    button.addEventListener('click', function () {
      var carrier = button.nextElementSibling;
      var deja = button.nextElementSibling && button.nextElementSibling.nextElementSibling;
      if (deja && deja.classList.contains('text-open')) {
        deja.remove();
        button.setAttribute('aria-expanded', 'false');

        return;
      }
      var bloc = document.createElement('pre');
      bloc.className = 'text-open';
      bloc.textContent = carrier ? carrier.textContent : '';
      button.parentNode.insertBefore(bloc, carrier.nextSibling);
      button.setAttribute('aria-expanded', 'true');
    });
  });

  /* THE DRAWER CARRIES ONE VERSION, AND IT OPENS FROM THAT VERSION ITSELF. Its content is already in the page, folded under the card: it is MOVED, never copied
     — a copy would duplicate the images, which are written out in full in the page, and would double its weight. */
  var drawerHome = null;
  var drawerNode = null;
  var paging = document.getElementById('version-paging');
  var rankSaid = document.getElementById('version-rank');
  var stepNext = document.getElementById('version-next');
  var stepPrevious = document.getElementById('version-previous');
  var strip = document.getElementById('version-strip');
  /* EVERY VERSION OF ONE VARIANT, IN THE ORDER THE PAGE SHOWS THEM: the current one first, then the earlier ones, newest to oldest — which is why « suivante »
     runs down the list and sits on the LEFT.
     WHAT IS ENUMERATED IS THE CARDS, NOT THE `.version-full` NODES, and it is done WHILE EVERYTHING IS HOME — right after returnVersion(), before the new one is
     moved. The earlier versions are folded INSIDE the current version's `.version-full`, which the drawer takes away with them: asked while the drawer holds it,
     the page would answer that this variant has exactly one version, and the rank would be wrong on every card. */
  function versionCards(carte) {
    var variant = carte.closest('.variant');
    if (!variant) { return [carte]; }

    return [variant].concat(Array.prototype.slice.call(variant.querySelectorAll('.previous')));
  }
  /* WHICH VERSION A CARD IS, said by the path of its own image — the same key its verdict and its comment are filed under, so there is one identity and not two.
     The card's own button carries it; only a card with no image at all has none, and such a card opens nothing anyway. */
  function versionKey(carte) {
    var door = carte.querySelector('.open-version');

    return door ? door.getAttribute('data-for') : (carte.getAttribute('data-version') || '');
  }
  /* THE STRIP AT THE BOTTOM: one small image per version, the one being looked at marked. Its images are CLONES taken from the cards, at the size CSS gives them
     — small enough that a quantity of versions is seen at a glance, which is the criterion the operator gave, never a dimension. */
  function fillStrip(cards, rank) {
    strip.textContent = '';
    cards.forEach(function (card, index) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'version-thumb' + (index === rank ? ' version-thumb--current' : '');
      button.setAttribute('data-version', versionKey(card));
      if (index === rank) { button.setAttribute('aria-current', 'true'); }
      var picture = card.querySelector('.picture img');
      if (picture) {
        var small = picture.cloneNode(false);
        small.removeAttribute('width');
        small.removeAttribute('height');
        small.style.marginTop = '';
        button.appendChild(small);
      }
      var mark = document.createElement('span');
      mark.className = 'version-thumb-rank';
      mark.textContent = String(index + 1);
      button.appendChild(mark);
      button.title = 'Version ' + (index + 1) + ' sur ' + cards.length + (index === 0 ? ' — la plus récente' : '');
      /* A VERSION OF THE STRIP S'OUVRE COMME UNE VERSION DE LA LISTE, et par le même chemin : le bouton de sa carte. Rien de son comportement ne change, ce qui
         est la demande — la bande est une seconde porte vers ce qui existe, jamais un second mécanisme. */
      button.addEventListener('click', function () {
        var door = card.querySelector('.open-version');
        openVersion(door || card);
      });
      strip.appendChild(button);
    });
    strip.hidden = cards.length < 1;
  }
  function openVersion(carrier) {
    var carte = carrier.closest('.variant, .previous');
    var full = carte.querySelector('.version-full');
    if (!full) { return; }
    returnVersion();
    /* THE RANK IS TAKEN HERE, everything back in its place and nothing moved yet — see versionCards(). */
    var cards = versionCards(carte);
    var rank = cards.indexOf(carte);
    drawerHome = full.parentNode;
    drawerNode = full;
    /* THE DRAWER SAYS WHAT IT IS SHOWING (operator, 2026-08-12: « quand j'ouvre le drawer, il doit annoncer clairement le nom du sujet et le nom du variant »).
       It announced « La version en entier », which is true of every one of them and names none: opened from a board of fifteen variants, one no longer knew
       which was on screen. Both names are already in the page — the subject at the head of its card, the variant on its own — so they are READ, not recomposed. */
    var panel = carte.closest('.fsp');
    var subjectTitle = panel ? panel.querySelector('.fsp-title') : null;
    var variantHeading = carte.closest('.variant').querySelector('.variant-name');
    /* THE NAME IS READ WITHOUT ITS BADGE: the « principal » mark lives inside the same heading, so taking its whole text gave « Vue principaleprincipal ». Only
       the direct text of the heading is its name; what is nested in it is a label about it. */
    var variantName = '';
    if (variantHeading) {
      Array.prototype.forEach.call(variantHeading.childNodes, function (piece) {
        if (piece.nodeType === 3) { variantName += piece.textContent; }
      });
      variantName = variantName.trim();
    }
    var olderMark = carte.classList.contains('previous') ? ' — version antérieure' : '';
    drawerTitle.textContent = (subjectTitle ? subjectTitle.textContent.trim() : '')
      + (variantName ? ' · ' + variantName : '') + olderMark;
    /* TWO NAMES BECAUSE THEY ARE TWO THINGS — and they shared one, `nom`, declared twice in the same function: the title read the first, the path overwrote it
       with the second on the next line. It worked by order of execution alone, which is the kind of thing that breaks the day a line moves. */
    var fileName = carte.querySelector('.variant-file');
    drawerPath.textContent = fileName ? fileName.textContent : '';
    drawerPath.hidden = !fileName;
    drawerBody.textContent = '';
    /* THE DRAWER IS SHOWN BEFORE ANYTHING IS MEASURED: hidden, it reports a width of zero, and a magnification computed on that would fall back to one for every
       image. */
    drawer.hidden = false;
    /* THE IMAGE IS CLONED WHEN THE DRAWER OPENS, NEVER WRITTEN TWICE INTO THE PAGE: a thumbnail is a file written out in full in the document, and copying it
       took the page from 37 to 71 MB before the build showed it. The clone costs the file nothing; it lives only as long as the drawer. */
    var image = carte.querySelector('.picture');
    if (image) {
      var grande = document.createElement('div');
      grande.className = 'version-image';
      var clone = image.cloneNode(true);
      /* THE MAGNIFICATION IS MEASURED, NOT DECREED: twice for a one-tile sprite, less as soon as it would no longer fit the drawer, never below one — an image
         one has come to look at closely is not shrunk. The available width is taken from the drawer itself, which is already at its size since its style does
         not depend on its content. */
      /* THE IMAGE IS GIVEN A WIDTH IN PIXELS, AND THAT IS THE WHOLE OF IT. Two attempts failed before this one, both for the same reason — a size expressed
         RELATIVE to something that did not move. `width: 200%` measured the image against a wrapper the wrapper took from the image, and `zoom` was read off a
         drawer width that is zero while it is still hidden. An absolute width has no such loop: the wrapper takes the image's size, and the footprint grid,
         which is laid on the wrapper in percentages, follows it exactly.
         TWICE THE THUMBNAIL, BUT NEVER WIDER THAN THE PANEL (operator, 2026-08-12, twice: « si l'image est plus large que le drawer, ça pose souci », then « tu
         n'as pas résolu le problème de sprite très grand »). A sixteen-tile building is therefore shown smaller than twice, and whole. */
      var vignette = clone.querySelector('img');
      if (vignette) {
        var natural = Number(vignette.getAttribute('width')) || vignette.width;
        var tall = Number(vignette.getAttribute('height')) || vignette.height;
        /* BOUNDED ON BOTH SIDES, AND THE RATIO IS NEVER TOUCHED (operator, 2026-08-12: « dans le drawer, les sprites doivent tout de même avoir une taille
           maximum et garder leurs proportions »). Only the WIDTH is set, in pixels; the height follows on its own. A ceiling on the height would have to be
           expressed as a width too — capping both in CSS distorts, since the browser then honours two contradictory sizes. So the height ceiling is converted
           into the width it allows, and the smallest of the three wins: twice the thumbnail, the room across, the room down. */
        var room = drawer.getBoundingClientRect().width - 32;
        var ceiling = window.innerHeight * 0.7;
        var byHeight = tall ? (ceiling * natural) / tall : room;
        var shown = Math.max(1, Math.round(Math.min(natural * 2, room, byHeight)));
        vignette.style.width = shown + 'px';
        vignette.style.height = 'auto';
        vignette.removeAttribute('width');
        vignette.removeAttribute('height');
        /* AND THE ROOM RESERVED ABOVE THE IMAGE IS MAGNIFIED WITH IT. The grid rises out of the image to close its top tile, and the wrapper holds that room in
           a margin the builder writes in pixels, for the thumbnail's size. Left as it is while the image doubles, the reserve would be half of what the grid
           takes and the top tile would climb over the drawer's title. The margin is read off the ORIGINAL card, never off the clone: the clone is the one being
           rewritten, and reading a value one is about to overwrite is how a factor gets applied twice. */
        var reserve = parseFloat(window.getComputedStyle(image).marginTop) || 0;
        clone.style.marginTop = (reserve * shown) / natural + 'px';
      }
      grande.appendChild(clone);
      drawerBody.appendChild(grande);
      /* AND THIS IS THE IMAGE THE RUNE IS PLACED ON: the clone inherits no listener, and this is where one can aim accurately. */
      if (clone.hasAttribute('data-anchor-for')) { wireAnchor(clone); }
    }
    drawerBody.appendChild(full);
    full.hidden = false;
    /* WHAT VERSION IS THIS, OF HOW MANY — the demand itself: « le drawer doit être plus clair sur la version regardée ». The title names the subject and the
       variant, the path names the file; neither says where one stands among eighteen versions. */
    rankSaid.textContent = 'Version ' + (rank + 1) + ' sur ' + cards.length + (rank === 0 ? ' — la plus récente' : '');
    /* GAUCHE MÈNE À LA SUIVANTE, DROITE À LA PRÉCÉDENTE, et les bornes s'éteignent au lieu de disparaître : un bouton qui s'en va déplace l'autre sous le
       curseur, et le clic suivant tombe sur ce qu'on ne visait pas. */
    stepNext.disabled = rank + 1 >= cards.length;
    stepPrevious.disabled = rank < 1;
    stepNext.onclick = function () { stepTo(cards[rank + 1]); };
    stepPrevious.onclick = function () { stepTo(cards[rank - 1]); };
    paging.hidden = cards.length < 2;
    fillStrip(cards, rank);
    rememberVersion(versionKey(carte));
    drawer.hidden = false;
    drawer.scrollTop = 0;
    document.body.classList.add('drawer-open');
  }
  /* Aller d'une version à l'autre, c'est ouvrir l'autre — par sa propre porte, donc avec exactement le comportement qu'elle a déjà. */
  function stepTo(card) {
    if (!card) { return; }
    var door = card.querySelector('.open-version');
    openVersion(door || card);
  }
  /* WHAT WAS MOVED GOES BACK HOME ON CLOSING: left in the drawer, it would be missing from its card, and the next version would open onto nothing. */
  function returnVersion() {
    if (drawerNode && drawerHome) {
      drawerNode.hidden = true;
      drawerHome.appendChild(drawerNode);
    }
    drawerNode = null;
    drawerHome = null;
  }
  Array.prototype.forEach.call(document.querySelectorAll('.open-version'), function (button) {
    button.addEventListener('click', function () { openVersion(button); });
  });
  /* THE IMAGE ITSELF OPENS ITS VERSION (operator, 2026-08-12: « sur la grille, si je clique sur l'image, ça doit aussi ouvrir cette version dans le drawer »).
     That is the gesture one makes without thinking in front of a thumbnail, and until now it meant aiming at the button underneath. The button stays: it names
     what the click does, which an image does not say about itself. */
  Array.prototype.forEach.call(document.querySelectorAll('.variant-image .picture'), function (picture) {
    picture.style.cursor = 'zoom-in';
    picture.addEventListener('click', function () { openVersion(picture); });
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
  /* PUIS LA VERSION QUI ÉTAIT OUVERTE, APRÈS LES PANNEAUX ET JAMAIS AVANT : le drawer s'ouvre PAR-DESSUS le panneau du sujet, donc le panneau doit être là
     d'abord. La version se retrouve par le chemin de son image, comparé attribut à attribut plutôt que glissé dans un sélecteur — un chemin porte des barres et
     des points, et un sélecteur composé à la main est la faute qui ne se voit qu'au premier chemin inhabituel.
     ET SI ELLE ÉTAIT REPLIÉE, LE PLI S'OUVRE AVEC ELLE : une version antérieure vit dans un `details` refermé par la reconstruction, et « à l'identique » vaut
     aussi pour ce qu'il a fallu ouvrir pour l'atteindre. Une version disparue entre deux constructions est simplement passée : ce qui n'existe plus ne se rouvre
     pas, et la page ne se refuse pas pour autant. */
  try {
    var wanted = sessionStorage.getItem(MEMORY_VERSION);
    if (wanted) {
      Array.prototype.some.call(document.querySelectorAll('.open-version'), function (door) {
        if (door.getAttribute('data-for') !== wanted) { return false; }
        var fold = door.closest('details');
        if (fold) { fold.open = true; }
        openVersion(door);

        return true;
      });
    }
  } catch (error) { /* storage refused or unreadable: the drawer simply stays closed */ }
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
    /* AND CE QUE LE FILET LOCAL PORTE EST REVERSÉ ICI, ENTRY BY ENTRY, AND ONLY WHAT THE SERVER DOES NOT ALREADY HOLD (operator, 2026-08-12: « à défaut au moins en
       local »). An entry the server hands back identical HAS landed: it leaves the net. One that differs never arrived — a reload that cut the send, a server that
       was down — so it is laid over what was received, put back on the wire, and KEPT in the net until a load shows it landed. Nothing is dropped on the strength
       of having been sent: a send is not an arrival, and this whole mechanism exists because the difference was paid for. */
    var net = readOutbox();
    var owed = Object.keys(net).filter(function (id) { return JSON.stringify(state[id]) !== JSON.stringify(net[id]); });
    var still = {};
    owed.forEach(function (id) {
      state[id] = net[id];
      still[id] = net[id];
    });
    setOutbox(still);
    owed.forEach(function (id) { remember(id); });
    render();
  });

  /* THE SURVEY TO COPY IS GONE (operator, 2026-08-11: « Si ça enregistre tout seul sur le serveur, je n'ai pas besoin de la fonctionnalité pour copier le
     relevé », then « normalement, y'a plus de relevé »). It existed to hand him a text to paste into the conversation, for want of any other channel: every
     verdict now reaches the repository the moment it is ticked, and the agent reads it there. What it built — the list of what is validated, to rework,
     dismissed and commented — is exactly what `php scripts/remarks.php list` prints, from the file rather than from a screen. */
})();
