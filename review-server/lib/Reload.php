<?php
/**
 * USAGE
 *   Let a served page notice it has been rebuilt and offer to reload itself, so nobody works on a stale version without knowing.
 *
 * INTENTION
 *   A published page reloaded itself whenever it was republished; a locally served page did not, and the operator was left looking at a stale version without knowing it (operator, 2026-08-07). The
 *   lost convenience is given back here, in a gentler form: the page never reloads under one's hands without warning.
 *
 *   HOW IT KNOWS: it asks the server for the signature of its own route, every two seconds. The request carries back a date, never the page — a review page weighs megabytes, and fetching it in a
 *   loop would be absurd. A signature different from the one taken on opening means a rebuild has happened.
 *
 *   WHY A COUNTDOWN AND NOT A PLAIN RELOAD: five seconds are enough to see what is coming and to finish a gesture. Nothing is lost either way — every page saves remarks as they are typed, in the
 *   browser's own storage, and reopens on them. I had claimed otherwise; the operator corrected me, and the code proves him right.
 */

class Reload
{
    private static ?self $instance = null;

    /** The pulse, in milliseconds: how often the page asks for its signature again. */
    private const PULSE = 2000;

    /** The delay before the automatic reload, in seconds — the value the operator asked for. */
    private const DELAY = 5;

    /** The ring's circumference, in drawing units: the radius is fixed by the drawing, the length follows once and for all. */
    private float $ring;

    public function __construct()
    {
        $this->ring = 2 * M_PI * 20;
    }

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    public function styles(): string
    {
        $ring = $this->ring;

        return <<<CSS
  .reload { position: fixed; right: 18px; bottom: 18px; z-index: 200; display: none; align-items: center; gap: 14px; padding: 12px 14px 12px 18px;
            background: #191b1f; border: 1px solid #3a3546; border-radius: 10px; box-shadow: 0 6px 24px rgba(0, 0, 0, .45); color: #e6e4e0;
            font-family: system-ui, sans-serif; font-size: .88rem; }
  .reload[data-open="yes"] { display: flex; }
  .reload-word { margin: 0; max-width: 15rem; line-height: 1.35; }
  .reload-ring { position: relative; width: 46px; height: 46px; flex: none; }
  .reload-ring svg { width: 46px; height: 46px; transform: rotate(-90deg); }
  .reload-ring circle { fill: none; stroke-width: 3; }
  .reload-track { stroke: #3a3546; }
  /* The ring empties over five seconds: it is what tells how much time is left, with no figure to read. */
  .reload-gauge { stroke: #d9a441; stroke-linecap: round; stroke-dasharray: {$ring}; stroke-dashoffset: 0; transition: stroke-dashoffset linear; }
  .reload-button { position: absolute; inset: 8px; border: none; border-radius: 50%; background: #d9a441; color: #191b1f; font: inherit; font-size: .95rem;
                   line-height: 1; cursor: pointer; }
  .reload-button:hover { background: #eab853; }
  .reload-button:focus-visible { outline: 2px solid #e6e4e0; outline-offset: 2px; }
CSS;
    }

    public function markup(): string
    {
        return <<<HTML
<aside class="reload" id="reload" role="status" aria-live="polite">
  <p class="reload-word">Une nouvelle version de cette page est prête.</p>
  <span class="reload-ring">
    <svg viewBox="0 0 46 46" aria-hidden="true"><circle class="reload-track" cx="23" cy="23" r="20"></circle>
      <circle class="reload-gauge" id="reload-gauge" cx="23" cy="23" r="20"></circle></svg>
    <button type="button" class="reload-button" id="reload-button" title="Recharger maintenant" aria-label="Recharger maintenant">↻</button>
  </span>
</aside>
HTML;
    }

    /** The script, route included: the route is what the server knows how to sign, and the browser cannot guess it when the page is served under an address of its own. */
    public function script(string $route): string
    {
        $ring = $this->ring;
        $pulse = self::PULSE;
        $delay = self::DELAY;
        $routeJs = json_encode($route);

        return <<<JS
<script>
(function () {
  var route = {$routeJs};
  var openingSignature = null;
  var announced = false;
  var box = document.getElementById('reload');
  var gauge = document.getElementById('reload-gauge');

  function ask(next) {
    var call = new XMLHttpRequest();
    call.open('GET', '/version?page=' + encodeURIComponent(route), true);
    // A server failure must break NOTHING: the page stays usable as it is, and the pulse resumes on the next beat.
    call.onload = function () { if (call.status === 200) { next(call.responseText); } };
    call.send();
  }

  function announce() {
    announced = true;
    box.setAttribute('data-open', 'yes');
    gauge.style.transitionDuration = '0s';
    gauge.style.strokeDashoffset = '0';
    // The browser must have taken the starting point before the transition starts, otherwise it jumps straight to the end and the ring never animates.
    gauge.getBoundingClientRect();
    gauge.style.transitionDuration = '{$delay}s';
    gauge.style.strokeDashoffset = '{$ring}';
    window.setTimeout(function () { window.location.reload(); }, {$delay} * 1000);
  }

  document.getElementById('reload-button').addEventListener('click', function () { window.location.reload(); });

  /* THE WATCH IS INSTALLED WHATEVER THE FIRST CALL DOES, AND THAT IS THE WHOLE OF THE FIX. It used to be installed INSIDE the first answer, so a page loaded
     while the server was down or restarting never asked again: it stayed open, looking alive, and deaf for the rest of the session. That is what happened to the
     index on 2026-08-12 — « la page index ouverte ne s'est pas rafraîchie » — and no amount of rebuilding could have woken it.
     A FAILED CALL LEAVES THE OPENING SIGNATURE UNKNOWN, and the first one that succeeds becomes it. The page then compares against what it actually saw, rather
     than announcing a change it has no ground to claim. */
  window.setInterval(function () {
    if (announced) { return; }
    ask(function (now) {
      if (openingSignature === null) { openingSignature = now; return; }
      if (now !== openingSignature) { announce(); }
    });
  }, {$pulse});
  ask(function (signature) { if (openingSignature === null) { openingSignature = signature; } });
})();
</script>
JS;
    }
}
