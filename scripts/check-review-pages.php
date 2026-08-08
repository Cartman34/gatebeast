<?php
/**
 * USAGE
 *   php scripts/check-review-pages.php — checks the built review pages still carry the behaviours the operator asked for. Run it after touching a page builder; it exits non-zero on any loss.
 *
 * INTENTION
 *   These behaviours were each asked for, built, then lost again when the page was rewritten — the comment cross three times over, the folded comment field twice in one day. Vigilance is not what
 *   keeps them: an agent rewriting a page cannot miss what it never knew was there. A mechanical check can, and it fails loudly, which is exactly the reasoning the project already applies to its
 *   text-width standard.
 *
 *   IT CHECKS THE BUILT PAGE, NOT THE BUILDER. What matters is what reaches the screen: a rule present in the source but overwritten later, or a button whose markup is right while its style is
 *   gone, both leave the built page wrong — and that is the only file the operator ever sees.
 */

$root = dirname(__DIR__);
$page = $root . '/review-server/suivi-sprites/page.html';
if (!is_file($page)) {
    fwrite(STDERR, "FAULT la page des sprites n'est pas construite — php review-server/build.php /sprites\n");
    exit(1);
}
$html = file_get_contents($page);

// Chaque règle dit CE QUI EST ATTENDU et POURQUOI, pour que celui qui la casse sache ce qu'il vient de retirer plutôt que de la contourner.
$rules = [
    [
        'La zone de commentaire est repliée à l\'ouverture',
        'un champ toujours ouvert prend autant de hauteur que les trois actes réunis, sur chaque carte (opérateur, 2026-08-06 puis 2026-08-07)',
        fn (string $html): bool => (bool) preg_match('/class="mot-zone" data-more="[^"]*" hidden/', $html),
    ],
    [
        'Un bouton ouvre la zone de commentaire',
        'repliée sans bouton, elle serait inatteignable',
        fn (string $html): bool => str_contains($html, 'class="mot-ouvrir"'),
    ],
    [
        'Cocher « À reprendre » ou « Écarter » ouvre la zone',
        'un refus sans motif fait repartir la reprise à l\'aveugle — trois tentatives perdues sur le sapin',
        fn (string $html): bool => (bool) preg_match("/acte === 'reprendre' \|\| acte === 'ecarter'/", $html),
    ],
    [
        'La croix de vidage est une croix, en haut à droite du champ',
        'demandée trois fois par l\'opérateur, perdue deux fois — un mot écrit dedans lui fait perdre sa place et sa forme',
        fn (string $html): bool => str_contains($html, 'class="effacer-mot"')
            && (bool) preg_match('/\.effacer-mot\s*\{[^}]*position:\s*absolute[^}]*top:[^}]*right:/s', $html),
    ],
    [
        'La comparaison n\'engage qu\'à partir de deux variants',
        'engagée dès le premier, elle masque les autres cartes et la case du second n\'est plus là pour être cochée',
        fn (string $html): bool => str_contains($html, 'retenus.length > 1'),
    ],
    [
        'Les actes gardent l\'échelle du constructeur d\'origine',
        'la version PHP avait pris la taille du texte courant, seize pixels, ce qui grossissait toute la carte d\'un tiers',
        fn (string $html): bool => (bool) preg_match('/\.acte span, \.mot-ouvrir\s*\{[^}]*font-size:\s*10px/s', $html),
    ],
    [
        'Les boutons du relevé portent l\'habillage du projet',
        'sans règle à eux, ils tombent sur le bouton par défaut du navigateur — deux pavés gris sur une page sombre',
        fn (string $html): bool => (bool) preg_match('/\.releve-copier, \.releve-deplier, \.releve-fixe\s*\{/', $html),
    ],
];

$lost = [];
foreach ($rules as [$what, $why, $holds]) {
    if (!$holds($html)) {
        $lost[] = "  PERDU : {$what}\n          {$why}";
    }
}

if ($lost) {
    fwrite(STDERR, count($lost) . " comportement(s) perdu(s) sur la page des sprites :\n" . implode("\n", $lost) . "\n");
    exit(1);
}

printf("La page des sprites tient ses %d comportements.\n", count($rules));
