<?php
/**
 * USAGE
 *   Keep the remarks an operator writes on a review page in the repository instead of in his browser, so they survive and so an agent can read them without being sent them.
 *
 * INTENTION
 *   A remark used to live in the browser's own storage, tied to the address that received it. Three consequences, all paid for: it vanished when the address changed — that happened on 2026-08-06
 *   and the operator lost what he had written; it could not be read by anyone but him, so he had to copy a summary into the conversation by hand; and nothing kept it once he changed machine.
 *
 *   ONE FILE PER PAGE, AND IT IS VERSIONED. What the operator writes is project matter, not browser state: it belongs where the rest of the project lives, with a history. A remark carries what it
 *   is attached to, what it says, when it was written, and whether it has been settled — that last one is what stops a treated remark from coming back at the next reading, which cost five repeated
 *   remarks on 2026-08-06.
 *
 *   THE PAGE NEVER WRITES THE FILE ITSELF: it hands its remarks to the server, which is the only writer. A page is a copy on someone's screen, possibly an old one; letting each copy write would
 *   have the last reload win, and silently drop what was written elsewhere.
 */

class Notes
{
    private static ?self $instance = null;

    private string $directory;

    /**
     * `$directory` is where this instance files, and it is the only thing that changes between one use and another.
     *
     * IT EXISTS BECAUSE THE CRITIQUES OF A TRIAL MUST **NOT** LAND HERE (operator, 2026-08-13: « tes critiques n'ont pas à survivre, tu ne dois garder que les
     * conclusions dans la doc et le code »). They live inside their trial's own folder, under `var/`, and disappear with it — deliberately. What they must NOT
     * have is a durable home: it would be one more history nobody rereads, and it would make the conclusion look as though it lived there rather than at its own
     * foyer. So the destination moves, and the mechanism does not: merging key by key under a lock, with one step back, is what kept a morning of verdicts on
     * 2026-08-11, and a second copy of it written for the workshop page would have to learn that lesson again.
     */
    public function __construct(?string $directory = null)
    {
        $this->directory = $directory ?? dirname(__DIR__) . '/notes';
    }

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** The remarks written on a page, oldest first, or an empty list when the page has never received any. */
    public function forRoute(string $route): array
    {
        $path = $this->pathFor($route);

        return is_file($path) ? json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR) : [];
    }

    /**
     * Lays what a page sends over what the file already holds, entry by entry, and keeps the version it replaces.
     *
     * A PAGE NO LONGER REPLACES THE FILE, IT ADDS TO IT (operator, 2026-08-11: « J'ai mis des commentaires et à reprendre sur tous les PDS mais les commentaires
     * ont disparu, tu as des pertes apparemment »). Each page sent the WHOLE section it knew, so whoever saved last wrote back the state it had read on opening
     * and erased everything written elsewhere in between — two tabs on the review, or a tab and a probe, were enough to lose a morning of verdicts. What arrives
     * is merged key by key: an entry the sender does not mention is left alone, and one it does mention wins, because it is the fresher judgement on that image.
     *
     * A LIST STILL REPLACES ITS LIST. Where a section holds an ordered list rather than entries with keys — the Campagne plan's remarks — there is nothing to
     * merge on: removing the third remark would be indistinguishable from not sending it. Those sections keep the old behaviour, and it is written here rather
     * than discovered.
     *
     * AND THE PREVIOUS VERSION IS KEPT, ONE DEEP. The file was the single copy of a human judgement, overwritten in place with no trace: the loss above could not
     * be repaired, not even from the history, because it had never been committed. `.previous.json` is not a history — it is the one step back that turns an
     * accident into an annoyance.
     *
     * THE WHOLE THING HAPPENS UNDER A LOCK, and merging is exactly why it must. Reading, laying over and writing back are three steps: two saves arriving
     * together would both read the same state and the second would write back a merge that ignores the first — the very loss this method exists to prevent,
     * narrowed to a few milliseconds instead of a browser session. The project's rule asks for the lock at the moment the concurrent write is written, not after
     * the first damage; here the damage came first, and the rule is applied late.
     */
    public function save(string $route, array $notes): void
    {
        if (!is_dir($this->directory)) {
            mkdir($this->directory, 0o775, true);
        }
        $path = $this->pathFor($route);
        // THE LOCK LIVES BESIDE THE FILE, NOT ON IT: locking the file itself would mean opening it for writing before knowing what to write, which truncates it
        // the moment two writers meet. A lock file has no content to lose.
        $gate = fopen($path . '.lock', 'c');
        if ($gate === false || !flock($gate, LOCK_EX)) {
            throw new RuntimeException("FAULT impossible de verrouiller {$path}.lock — rien n'est écrit plutôt qu'écrit à moitié.");
        }
        try {
            $held = is_file($path) ? json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR) : [];
            if ($held) {
                copy($path, $this->previousFor($route));
            }
            foreach ($notes as $section => $sent) {
                $held[$section] = is_array($sent) && !array_is_list($sent) && isset($held[$section]) && is_array($held[$section])
                    ? array_replace($held[$section], $sent)
                    : $sent;
            }
            file_put_contents($path, json_encode($held, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");
        } finally {
            flock($gate, LOCK_UN);
            fclose($gate);
        }
    }

    /** The copy of what a route's file held before the last write — one step back, never a history. */
    private function previousFor(string $route): string
    {
        return preg_replace('/\.json$/', '.previous.json', $this->pathFor($route));
    }

    /**
     * The file a route's remarks live in.
     *
     * The route becomes the file name, with its slashes turned into dashes: `/parc/maquette` gives `parc-maquette.json`. Anything that is not a letter, a digit or a dash is dropped — a name built
     * from something the browser sends must never be able to point outside this folder.
     */
    private function pathFor(string $route): string
    {
        $name = trim(preg_replace('/[^a-z0-9-]+/', '-', strtolower($route)), '-');

        return $this->directory . '/' . ($name === '' ? 'accueil' : $name) . '.json';
    }

    /**
     * The browser side: it loads the remarks of its route, and hands the whole list back whenever it changes. Nothing is kept in the browser — the file is the only copy.
     *
     * EACH REVIEW TOOL HAS ITS OWN SECTION IN THE FILE, and that is not a refinement: the Campagne page carries two of them — the plan and the mounted mock-up — on a single address. Sharing one
     * list would have each tool overwrite the other's remarks at the first change, since each sends the whole list it knows.
     */
    public function script(string $route): string
    {
        $routeJs = json_encode($route);

        return <<<JS
<script>
window.gatebeastNotes = (function () {
  var route = {$routeJs};
  var all = {};

  function load(section, next) {
    var call = new XMLHttpRequest();
    call.open('GET', '/notes?page=' + encodeURIComponent(route), true);
    // A server that cannot be reached leaves the page usable with no remarks rather than dead: what matters is that nothing is invented, never that everything works.
    call.onload = function () {
      all = call.status === 200 ? (JSON.parse(call.responseText) || {}) : {};
      /* AN ARRAY IS NOT A TABLE OF SECTIONS, AND THE DIFFERENCE COST EVERY PAGE ITS FIRST REMARK. A missing or emptied file makes the server answer `[]` — PHP
         encodes an empty array that way, it has no "empty object" type. The module then set its section on an ARRAY: `all['plan'] = …` lands there as a named
         property, and JSON.stringify of an array serialises its indices only. So the remark went back to the server inside a `[]` and vanished, with no error and
         no trace. Invisible until now because the two existing files were never empty; found on 2026-08-08 while wiring up the sprites page, whose file did not
         exist yet. */
      if (Array.isArray(all)) { all = {}; }
      next(all[section] || []);
    };
    call.onerror = function () { next([]); };
    call.send();
  }

  function save(section, notes) {
    /* The same guard as on load: `save` may be called before the load has answered, and it would set its section on the initial array. */
    if (Array.isArray(all) || all === null || typeof all !== 'object') { all = {}; }
    all[section] = notes;
    var call = new XMLHttpRequest();
    call.open('POST', '/notes?page=' + encodeURIComponent(route), true);
    call.setRequestHeader('Content-Type', 'application/json');
    call.send(JSON.stringify(all));
  }

  return {load: load, save: save};
})();
</script>
JS;
    }
}
