<?php
/**
 * Usage: php review-server/serve.php [port]   — the address it prints is the one to open; `php scripts/stop-review-server.php` closes it at the end of the session.
 *        php review-server/serve.php -h|--help — this text, and no server is started.
 *
 * Intention: one command to start the review, so nobody has to remember the flags of the built-in server, and so the document root cannot be got wrong. THE ROOT IS THE REPOSITORY, not this folder:
 * a review page must be able to reach an image, a plan or a stylesheet where it actually lives, without any of them being copied here or encoded into the page. That is the very constraint that
 * publishing imposed and that serving locally removes.
 *
 * The address is not written here: it is configured in review-server/config.json and handed out by the ReviewServer service, so a port changed there changes everywhere at once.
 *
 * No new tool: `php -S` is PHP's own server, already installed wherever this project runs. Nothing to add on any machine.
 */

require_once __DIR__ . '/bootstrap.php';
require_once dirname(__DIR__) . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

$root = dirname(__DIR__);
$server = ReviewServer::get();
$port = $server->portFrom($argv[1] ?? null);

// THE PORT IS LOOKED AT BEFORE THE SERVER IS CALLED, so that the answer is the one that helps: a server left running by an earlier session is the ordinary case here, and `php -S` only says "Address
// already in use" before dying, which names neither what is holding it nor the command that frees it. Ten and a half hours were lost to exactly that this morning.
if (!$server->portIsFree($port)) {
    throw new RuntimeException("le port {$port} est déjà tenu — « php scripts/stop-review-server.php {$port} » ferme le serveur qui le tient.");
}

$command = sprintf('php -S %s:%d -t %s %s', $server->host(), $port, escapeshellarg($root), escapeshellarg(__DIR__ . '/router.php'));
printf("La revue est servie sur %s/ — Ctrl+C pour l'arrêter.\n", $server->baseUrl($port));
passthru($command, $status);
exit($status);
