<?php
/**
 * Usage: require this file; it returns the review pages the local server serves, and the command that produces each one.
 *
 * Intention: give every page a short address that does not depend on the name of the file holding it, so a page can be rebuilt, renamed or split without the address moving. That is the whole point
 * of serving rather than publishing — the address stops being a thing to keep.
 *
 * 'build' is the exact command that produces 'file', and it is written down because it was written nowhere: the campagne pages are produced by handing a plan and an output path to the park
 * builders, which had to be rediscovered by reading the code. A command nobody can find is a page nobody can rebuild.
 */

return [
    [
        // NI CETTE PAGE NI L'INVENTAIRE NE PORTENT PLUS LE MOT « SUJET » (opérateur, 2026-08-12) : il nommait à la fois les points du projet et les choses du
        // monde, et renommer une seule des deux n'aurait rien réglé — celui qui lit garde le mot en tête et retourne sur l'autre.
        'route' => '/backlog',
        'title' => 'La pile',
        'file' => 'backlog/page.html',
        'build' => 'php review-server/backlog/build.php',
    ],
    [
        // L'INVENTAIRE DIT CE QU'UN SUJET EST, LA PAGE DES SPRITES OÙ EN SONT SES IMAGES : deux questions, deux pages. Demandée par l'opérateur, et perdue une
        // fois avant d'être inscrite (2026-08-12).
        'route' => '/inventory',
        'title' => 'Inventaire du monde',
        'file' => 'inventory/page.html',
        'build' => 'php review-server/inventory/build.php',
    ],
    [
        'route' => '/sprites',
        'title' => 'Suivi des sprites',
        'file' => 'suivi-sprites/page.html',
        'build' => 'php review-server/suivi-sprites/build.php',
    ],
    // ARCHIVED on 2026-08-07 by the operator: the park is no longer maintained — the work is on Maquette Campagne — and both its pages will be restored when wanted. Their builders stay, since the
    // Campagne page is produced by those very builders, and their pages stay on disk. Restoring them is putting these two entries back:
    //   ['route' => '/parc', 'title' => 'Le plan de composition du parc', 'file' => 'parc/page.html', 'build' => 'php review-server/parc/build.php'],
    //   ['route' => '/parc/maquette', 'title' => 'La maquette du parc', 'file' => 'parc/maquette.html', 'build' => 'php review-server/parc/monter.php'],
    [
        'route' => '/maquette-campagne',
        'title' => 'Maquette Campagne',
        'file' => 'maquette-campagne/page.html',
        // The empty third argument says these two are SOURCES, served by no route: they carry no reload notice, which the final page carries once.
        'build' => 'php review-server/parc/build.php assets/maquette/maquette-campagne.json review-server/parc/maquette-campagne-plan.html ""'
            . "\n" . 'php review-server/parc/monter.php assets/maquette/maquette-campagne.json review-server/parc/maquette-campagne-montee.html ""'
            . "\n" . 'php review-server/maquette-campagne/build.php',
    ],
];
