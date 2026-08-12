<?php
/**
 * USAGE
 *   php scripts/stop-review-server.php [port]
 *
 *   Closes the review server left listening on the port — the configured one unless another is given — and says so. Run it before leaving the session: the server does not outlive the session, and a
 *   server left running holds the port, so the next session's `php review-server/serve.php` dies on "Address already in use". Reports and exits 0 when no server is there: nothing to close is no
 *   fault.
 *
 * INTENTION
 *   THE STOPPING GESTURE IS A SCRIPT, NOT A COMMAND TYPED AGAIN (opérateur, 2026-08-12 : « il te faut un script pour le fermer »). The server runs as a background shell of the agent's harness, and
 *   an earlier session's shell is out of reach of the session that comes next: the only remaining door is a signal to the process, which is exactly the kind of gesture the project turns into a named,
 *   reviewable script instead of a hand-typed `kill` whose target is worked out afresh every time — and worked out wrong, on a stale process number, the day someone hurries.
 *
 *   IT VERIFIES THE PORT, IT DOES NOT TRUST THE SIGNAL. A signal that was accepted says nothing about the process having gone: it may ignore it, or take its time. So the proof is the port itself —
 *   the script binds it once the process is gone. Anything short of that would be a success message emitted without checking the success, which is the error this project forbids by name.
 *
 *   In PHP because it is the project's default language for durable tooling, and the process control it needs is in its own POSIX extension.
 *
 * @see review-server/serve.php — the other half of the pair: it starts what this one closes.
 */

/** How long a stopped process is given to actually go, and how often it is looked at, in microseconds. */
const SERVER_GRACE_MICROSECONDS = 5_000_000;
const SERVER_POLL_MICROSECONDS = 200_000;

require_once dirname(__DIR__) . '/review-server/bootstrap.php';
bootBuild();

$server = ReviewServer::get();
$port = $server->portFrom($argv[1] ?? null);

/**
 * The process numbers of the built-in servers listening on that port.
 *
 * MATCHED ON THE ARGUMENTS `serve.php` BUILDS, port included, so a review served on another port is never touched by mistake. The wrapper itself is deliberately not matched: it carries no port on its
 * command line, and it ends by itself the moment the server it waits on is gone.
 *
 * READ FROM /proc RATHER THAN ASKED OF `pgrep`, and that is not a preference: a search whose own pattern is on its own command line matches itself. `pgrep -f "php -S localhost:8080"` duly returned
 * the shell PHP had just spawned to run it, the script signalled a process that had already exited, and it stopped on "No such process" while the real server kept the port. Arguments compared one by
 * one cannot drift like that.
 */
function listeningServers(string $host, int $port): array
{
    $found = [];
    foreach (glob('/proc/[0-9]*/cmdline') as $path) {
        $pid = (int) basename(dirname($path));
        if ($pid === getmypid()) {
            continue;
        }
        // A process may well be gone between the listing and the read: that is expected here, and it means it is not a server we have to close.
        $raw = @file_get_contents($path);
        if ($raw === false) {
            continue;
        }
        $arguments = array_values(array_filter(explode("\0", $raw), static fn (string $part): bool => $part !== ''));
        $flag = array_search('-S', $arguments, true);
        if ($flag !== false && ($arguments[$flag + 1] ?? '') === sprintf('%s:%d', $host, $port)) {
            $found[] = $pid;
        }
    }
    return $found;
}

/** True while the process still exists. Signal 0 checks for it without touching it. */
function stillRunning(int $pid): bool
{
    return posix_kill($pid, 0);
}

$servers = listeningServers($server->host(), $port);
if ($servers === []) {
    // NOT A FAULT, BUT NOT A BLIND "ALL GOOD" EITHER: if no server of ours is there and the port is still held, something else holds it, and that is worth saying out loud.
    if (!$server->portIsFree($port)) {
        throw new RuntimeException("aucun serveur de revue ne tourne sur le port {$port}, et pourtant le port est occupé — regardez ce qui le tient avant de relancer.");
    }
    printf("Aucun serveur de revue sur le port %d — rien à fermer.\n", $port);
    exit(0);
}

foreach ($servers as $pid) {
    if (!posix_kill($pid, SIGTERM)) {
        throw new RuntimeException("le serveur {$pid} n'a pas pu être arrêté : " . posix_strerror(posix_get_last_error()));
    }
}

$waited = 0;
while ($waited < SERVER_GRACE_MICROSECONDS && array_filter($servers, 'stillRunning') !== []) {
    usleep(SERVER_POLL_MICROSECONDS);
    $waited += SERVER_POLL_MICROSECONDS;
}

$stubborn = array_filter($servers, 'stillRunning');
if ($stubborn !== []) {
    throw new RuntimeException(sprintf('le serveur %s ne s\'est pas arrêté en %d secondes — il tient toujours le port %d.',
        implode(', ', $stubborn), (int) (SERVER_GRACE_MICROSECONDS / 1_000_000), $port));
}
if (!$server->portIsFree($port)) {
    throw new RuntimeException("le serveur est arrêté mais le port {$port} reste occupé — la revue ne pourra pas redémarrer dessus.");
}

printf("Serveur de revue fermé (%s) — le port %d est libre.\n", implode(', ', $servers), $port);
exit(0);
