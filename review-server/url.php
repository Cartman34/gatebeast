<?php
/**
 * Usage: php review-server/url.php [route]   — prints the address the review is served at, `/sprites` or any other route appended when one is given.
 *        php review-server/url.php -h|--help — this text.
 *
 * Intention: the address is configuration now, and configuration that can only be read by opening a JSON file is configuration nobody reads — it gets copied into a document instead, and the copy is
 * wrong the day the port changes. This is the command that answers "where is the review?" for a document, for a shell, and for the operator, without anyone opening review-server/config.json.
 *
 * It prints and nothing else: no trailing prose, so the output drops straight into a browser or another command.
 */

require_once __DIR__ . '/bootstrap.php';
require_once dirname(__DIR__) . '/scripts/Tools.php';
bootBuild();

Tools::get()->helpIfAsked($argv, __FILE__);

printf("%s\n", ReviewServer::get()->urlFor($argv[1] ?? '/'));
