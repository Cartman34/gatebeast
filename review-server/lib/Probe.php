<?php
/**
 * USAGE
 *   Drive a built review page from a probe: take the page as the server delivers it, graft a script on it, and get back a SERVED address to open — never a
 *   `file://` path. `Probe::get()->page('/sprites')` reads the page, `->serve($html, $script, 'my-probe')` writes the copy and returns its address.
 *
 * INTENTION
 *   A PROBE THAT OPENS ITS COPY FROM THE DISK REPORTS ON A PAGE NOBODY EVER SEES. Since the style and the script of a review page live in their own files, reached
 *   by an ABSOLUTE address, a copy opened as `file://` comes out bare: no style, no script, every button dead, every remark empty. The probe then returns an image
 *   instead of saying « I cannot conclude » — a favourable verdict given without having controlled anything, which is the transparent error this repository
 *   forbids by name. Written under `var/tmp/`, which the server already serves, the copy is of the same origin and everything loads.
 *
 *   AND NO PROBE EVER WRITES, WHICH IS ENFORCED HERE RATHER THAN ASKED OF EACH ONE. Ten empty entries were once dropped into review-server/notes/sprites.json by a
 *   probe that was only measuring — the operator's own verdicts. The muzzle is laid at the TRANSPORT, not on one module: every request that is not a GET is
 *   refused, so a click that ticks a verdict, one that places a rune anchor, and any write invented later are all stopped by the same line. It is grafted BEFORE
 *   the page's own script, because the page can send from its very first moment — it pours back what its local net holds as soon as the repository answers.
 *
 *   THE MUZZLE GOES BEFORE THE FIRST SCRIPT OF THE PAGE, whichever it is — the inline module or the loaded behaviour. Naming one particular tag would tie this
 *   service to the shape of one page, and it serves four.
 */

class Probe
{
    private static ?self $instance = null;

    /** Where a probe's copies are written: the throwaway of the tooling, served by the review server like the rest of the repository. */
    private const YARD = 'var/tmp';

    private string $root;

    private ReviewServer $server;

    public function __construct(?string $root = null)
    {
        $this->root = $root ?? dirname(__DIR__, 2);
        $this->server = ReviewServer::get();
    }

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /**
     * A built page, taken FROM THE SERVER rather than from the disk.
     *
     * Reading the file would give the same bytes; asking the server proves it is up, and a probe that opens a copy while the server is down would otherwise fail
     * later, on the copy, with a message about something else entirely.
     */
    public function page(string $route): string
    {
        $address = $this->server->urlFor($route);
        $held = @file_get_contents($address);
        if ($held === false) {
            throw new RuntimeException("FAULT la revue ne répond pas sur {$address} — lancez php review-server/serve.php.");
        }

        return $held;
    }

    /**
     * Writes a probe copy of `$html` under var/tmp and returns the address the server delivers it at.
     *
     * THE PROBE'S SCRIPT IS APPENDED AT THE VERY END, never injected before `</body>`: a built review page carries no such tag, so a str_replace on it changes
     * nothing at all and the probe reports a clean run over a page it never touched. That is a real fault, met on the first version of two probes here.
     */
    public function serve(string $html, string $script = '', string $name = 'sonde'): string
    {
        $file = preg_replace('/[^a-z0-9-]+/i', '-', $name) . '.html';
        $path = $this->root . '/' . self::YARD . '/' . $file;
        if (!is_dir(dirname($path))) {
            mkdir(dirname($path), 0777, true);
        }
        file_put_contents($path, $this->muzzled($html) . $script);

        return $this->server->urlFor('/' . self::YARD . '/' . $file);
    }

    /**
     * A muzzled copy of whatever one names — a page of the repository, or an address the server already delivers — served under var/tmp.
     *
     * ONE RULE, NO EXCEPTION: a probe never opens the original. A page taken from the disk would come out bare, and even the served page WRITES on its own — the
     * sprites page pours back what its local net holds the moment the repository answers. Looking must stay looking, so what is opened is always a copy that
     * cannot send.
     */
    public function copyOf(string $pathOrAddress, string $name): string
    {
        $isAddress = str_starts_with($pathOrAddress, 'http://') || str_starts_with($pathOrAddress, 'https://');
        if (!$isAddress && !is_file($pathOrAddress)) {
            throw new RuntimeException("FAULT la page « {$pathOrAddress} » n'existe pas.");
        }
        $held = @file_get_contents($pathOrAddress);
        if ($held === false) {
            throw new RuntimeException("FAULT rien à lire sur « {$pathOrAddress} » — si c'est une adresse, lancez php review-server/serve.php.");
        }

        return $this->serve($held, '', $name);
    }

    /** The served address of a file that already lives in the repository — what turns « open this page » into « open it as the operator sees it ». */
    public function addressOf(string $path): string
    {
        $full = realpath($path);
        $inside = realpath($this->root);
        if ($full === false || !str_starts_with($full, $inside . '/')) {
            throw new RuntimeException("FAULT « {$path} » n'est pas un fichier du dépôt — le serveur ne peut pas le servir.");
        }

        return $this->server->urlFor(substr($full, strlen($inside)));
    }

    /**
     * The same page with the muzzle grafted in front of its own script.
     *
     * ITS PLACE IS THE WHOLE POINT: after the page's script it would still stop a click, but not what the page sends of its own accord at load — the sprites page
     * pours back whatever its local net holds the moment the repository answers, and that pour-back is a write.
     */
    private function muzzled(string $html): string
    {
        // BEFORE THE FIRST SCRIPT OF ANY KIND, loaded or inline — never before one particular tag. The remarks module is written inline, the page's behaviour is
        // loaded by `src`, and which of the two comes first is the page's business, not this service's. A page carrying no script at all can write nothing, and
        // the muzzle simply opens the file.
        $at = stripos($html, '<script');

        return $at === false ? $this->muzzle() . $html : substr($html, 0, $at) . $this->muzzle() . substr($html, $at);
    }

    /**
     * The muzzle itself: every request that is not a GET is refused, loudly on the page's console, and counted on `window.__probeWrites` for a probe that wants
     * to assert nothing was attempted.
     *
     * BOTH TRANSPORTS ARE STOPPED, since the pages use both — XMLHttpRequest for the remarks module, fetch for the rune anchor. Refusing at the transport is what
     * makes this hold for a write nobody has written yet.
     */
    public function muzzle(): string
    {
        return <<<'JS'
<script>
(function () {
  window.__probeWrites = [];
  var open = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url) {
    if (String(method).toUpperCase() !== 'GET') {
      window.__probeWrites.push(method + ' ' + url);
      console.log('SONDE — écriture refusée : ' + method + ' ' + url);
      /* The call is turned into a harmless read of the same address: refusing to open at all would throw inside the page's own code and stop the very
         behaviour the probe came to measure. What must not happen is the WRITE, not the gesture. */
      return open.call(this, 'GET', '/version?page=/sonde');
    }

    return open.apply(this, arguments);
  };
  var sent = window.fetch;
  window.fetch = function (address, options) {
    var method = options && options.method ? String(options.method).toUpperCase() : 'GET';
    if (method !== 'GET') {
      window.__probeWrites.push(method + ' ' + address);
      console.log('SONDE — écriture refusée : ' + method + ' ' + address);

      return Promise.resolve(new Response('{"fault":"sonde : écriture refusée"}', {status: 503}));
    }

    return sent.apply(this, arguments);
  };
})();
</script>
JS;
    }
}
