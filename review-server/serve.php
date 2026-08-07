<?php
/**
 * Usage: php review-server/serve.php [port]   — then open http://localhost:8080/ ; Ctrl+C stops it.
 *
 * Intention: one command to start the review, so nobody has to remember the flags of the built-in server, and so the document root cannot be got wrong. THE ROOT IS THE REPOSITORY, not this folder:
 * a review page must be able to reach an image, a plan or a stylesheet where it actually lives, without any of them being copied here or encoded into the page. That is the very constraint that
 * publishing imposed and that serving locally removes.
 *
 * No new tool: `php -S` is PHP's own server, already installed wherever this project runs. Nothing to add on any machine.
 */

require_once __DIR__ . '/bootstrap.php';
bootBuild();

$root = dirname(__DIR__);
$port = (int) ($argv[1] ?? 8080);
if ($port < 1024 || $port > 65535) {
    throw new RuntimeException("le port doit être compris entre 1024 et 65535, reçu « {$argv[1]} »");
}

$command = sprintf('php -S localhost:%d -t %s %s', $port, escapeshellarg($root), escapeshellarg(__DIR__ . '/router.php'));
printf("La revue est servie sur http://localhost:%d/ — Ctrl+C pour l'arrêter.\n", $port);
passthru($command, $status);
exit($status);
