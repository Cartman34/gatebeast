<?php
/**
 * USAGE
 *   php scripts/dev/probe-index-refresh.php        opens the index through the server, changes what its signature is taken on, and says whether the reload
 *                                                  banner appears
 *   php scripts/dev/probe-index-refresh.php -h     this text
 *
 * INTENTION
 *   THE INDEX DID NOT OFFER TO RELOAD WHEN A PAGE WAS ADDED (opérateur, 2026-08-12 : « la page index ouverte ne s'est pas rafraîchie »), and reading the code
 *   gave three wrong diagnoses on this family of defect in one evening. This drives the page instead: it asks the server for the signature, touches one of the
 *   three files the signature is taken on, asks again, and says whether the two differ. A banner that never appears because the signature never moves is a
 *   different fault from a banner that appears and is not seen, and only a measurement tells them apart.
 *
 *   IT WRITES NOTHING BUT A TIMESTAMP: `touch` on a versioned file changes no content. Nothing of the operator's is touched.
 */

$root = dirname(__DIR__, 2);
require_once $root . '/review-server/bootstrap.php';
bootBuild();

if (in_array('-h', $argv, true) || in_array('--help', $argv, true)) {
    foreach (array_slice(file(__FILE__, FILE_IGNORE_NEW_LINES), 2, 5) as $line) {
        echo trim(preg_replace('~^\s*\*\s?~', '', $line)), "\n";
    }
    exit(0);
}

$server = ReviewServer::get();
$before = @file_get_contents($server->urlFor('/version?page=/'));
if ($before === false) {
    throw new RuntimeException('FAUTE la route /version ne répond pas — le serveur de revue est-il lancé ?');
}
printf("signature avant : %s\n", trim($before));

// THE THREE FILES THE INDEX TAKES ITS SIGNATURE ON. Touching the registry is the closest thing to what the operator did — he added a page, which rewrites it.
$registry = $root . '/review-server/artefacts.json';
touch($registry);
clearstatcache();
sleep(1);

$after = @file_get_contents($server->urlFor('/version?page=/'));
printf("signature après : %s\n", trim($after));

if (trim($before) === trim($after)) {
    echo "LA SIGNATURE N'A PAS BOUGÉ — le bandeau ne peut pas apparaître, quelle que soit la page ouverte. C'est là qu'est le défaut.\n";
    // UN REFUS NOMME LE GESTE QUI DÉBLOQUE (`S90 refus-avec-solution`) : une sonde qui constate sans dire où regarder fait recommencer le diagnostic.
    echo "  Solution — la signature est calculée par le serveur à partir des fichiers de page : vérifier qu'il relit bien le fichier reconstruit,\n";
    echo "  et non une copie gardée en mémoire. Reconstruire d'abord — « php review-server/build.php <route> » — pour écarter la page périmée.\n";
    exit(1);
}

echo "La signature a bougé : une page ouverte doit proposer de recharger. Si elle ne l'a pas fait, le défaut est dans le script de la page, pas dans la route.\n";
