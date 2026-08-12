<?php
/**
 * USAGE
 *   Answer the one question everything around the review has to ask: at which address is it served? Whoever starts it, stops it, or opens one of its pages takes the port and the URL of a route from
 *   here — `ReviewServer::get()->urlFor('/sprites')` — and never writes an address of its own. `portIsFree()` says whether anything is holding it.
 *
 * INTENTION
 *   THE PORT IS A CONFIGURATION OF THE PROJECT, SO THAT IT CHANGES IN ONE PLACE (opérateur, 2026-08-12 : « il faut que le port soit une configuration du projet pour demain le changer facilement »).
 *   It was written out in twelve files — the starter, the closer, ten probes — and each of them was right on its own, which is exactly the shape of the fault: change the port and eleven of the twelve
 *   go on calling an address nobody serves any more, without a word, since a page that fails to load looks like a page that has nothing to show.
 *
 *   THE VALUE IS READ BY `Config`, THE OPERATIONS LIVE HERE. Holding one without the other is what makes copies come back: every caller that has to append a port to a host and a route to a host
 *   writes the same three lines, and they drift. So the service hands out finished URLs, and nobody assembles one.
 *
 *   THE PORT IS PROVED FREE BY BINDING IT, NEVER BY BELIEVING A SIGNAL. `portIsFree()` takes the port and gives it straight back: it is the only answer that cannot be wrong, and it is what lets the
 *   starter say "something is holding it, here is the command that frees it" instead of letting the built-in server die on a bare "Address already in use".
 */

class ReviewServer
{
    private static ?self $instance = null;

    /** The bounds a port has to be within, shared by everything that accepts one — a starting argument as much as the configured value. */
    public const PORT_MINIMUM = 1024;
    public const PORT_MAXIMUM = 65535;

    private string $host;
    private int $port;

    public function __construct()
    {
        $config = Config::get();
        $this->host = (string) $config->value('host');
        $this->port = (int) $config->value('port');
        $this->checkPort($this->port, Config::PATH);
    }

    /** The service instance. This is the ONLY static method here, and it does nothing else: all the work is on the instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** The configured port, and the one a command uses when it is given none. */
    public function port(): int
    {
        return $this->port;
    }

    public function host(): string
    {
        return $this->host;
    }

    /** The root address of the review, no trailing slash: `http://localhost:8080`. */
    public function baseUrl(?int $port = null): string
    {
        return sprintf('http://%s:%d', $this->host, $port ?? $this->port);
    }

    /** The address of one route or one served file: `urlFor('/sprites')`, `urlFor('/var/tmp/sonde.html')`. */
    public function urlFor(string $route, ?int $port = null): string
    {
        if ($route !== '' && !str_starts_with($route, '/')) {
            throw new RuntimeException("la route « {$route} » doit commencer par une barre oblique.");
        }
        return $this->baseUrl($port) . $route;
    }

    /** True when nothing holds the port: it is taken and given straight back, which is the only proof there is. */
    public function portIsFree(?int $port = null): bool
    {
        $socket = @stream_socket_server(sprintf('tcp://%s:%d', $this->host, $port ?? $this->port), $code, $message);
        if ($socket === false) {
            return false;
        }
        fclose($socket);
        return true;
    }

    /**
     * The port a command was given, the configured one when it was given none.
     *
     * WHERE THE ARGUMENT IS READ, ONCE: the starter and the closer both take an optional port, and both used to check its bounds themselves. A rule checked in two places is a rule that will soon be
     * checked in one and a half. An empty argument is no argument — the boundary between a command line and the code is where nothing becomes null.
     */
    public function portFrom(?string $given): int
    {
        if ($given === null || trim($given) === '') {
            return $this->port;
        }
        $port = (int) $given;
        $this->checkPort($port, 'l\'argument de la commande');
        return $port;
    }

    private function checkPort(int $port, string $origin): void
    {
        if ($port < self::PORT_MINIMUM || $port > self::PORT_MAXIMUM) {
            throw new RuntimeException(sprintf('le port doit être compris entre %d et %d, reçu « %d » depuis %s.', self::PORT_MINIMUM, self::PORT_MAXIMUM, $port, $origin));
        }
    }
}
