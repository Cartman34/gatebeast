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
        fn (string $html): bool => (bool) preg_match('/class="comment-zone" data-more="[^"]*" hidden/', $html),
    ],
    [
        'Un bouton ouvre la zone de commentaire',
        'repliée sans bouton, elle serait inatteignable',
        fn (string $html): bool => str_contains($html, 'class="open-comment"'),
    ],
    [
        'Cocher « À reprendre » ou « Écarter » ouvre la zone',
        'un refus sans motif fait repartir la reprise à l\'aveugle — trois tentatives perdues sur le sapin',
        fn (string $html): bool => (bool) preg_match("/acte === 'reprendre' \|\| acte === 'ecarter'/", $html),
    ],
    [
        'La croix de vidage est une croix, en haut à droite du champ',
        'demandée trois fois par l\'opérateur, perdue deux fois — un mot écrit dedans lui fait perdre sa place et sa forme',
        fn (string $html): bool => str_contains($html, 'class="clear-comment"')
            && (bool) preg_match('/\.clear-comment\s*\{[^}]*position:\s*absolute[^}]*top:[^}]*right:/s', $html),
    ],
    [
        'La comparaison n\'engage qu\'à partir de deux variants',
        'engagée dès le premier, elle masque les autres cartes et la case du second n\'est plus là pour être cochée',
        fn (string $html): bool => str_contains($html, 'retenus.length > 1'),
    ],
    [
        'Les actes gardent l\'échelle du constructeur d\'origine',
        'la version PHP avait pris la taille du texte courant, seize pixels, ce qui grossissait toute la carte d\'un tiers',
        fn (string $html): bool => (bool) preg_match('/\.act span, \.open-comment\s*\{[^}]*font-size:\s*10px/s', $html),
    ],
    [
        'Un verdict est un seul des trois',
        'valider, à reprendre et écarter s\'excluent — une image acceptée et rejetée à la fois ne dit plus rien au relevé (opérateur, 2026-08-08)',
        fn (string $html): bool => (bool) preg_match('/\.acts input\[data-id="\' \+ id \+ \'"\]/', $html),
    ],
    [
        'Le rechargement automatique de page (RAP) rouvre les panneaux où l\'on était',
        'le défilement était rendu, les panneaux non : une reconstruction pendant qu\'on juge renvoyait à la planche entière (opérateur, 2026-08-08)',
        fn (string $html): bool => str_contains($html, 'gatebeast-sprites-panneaux') && str_contains($html, 'sessionStorage.getItem'),
    ],
    [
        'Les images hors modèle se voient, elles ne sont pas seulement nommées',
        'un nom de fichier ne dit pas si l\'image est un reste, une sonde ou une sprite dont l\'inscription s\'est perdue (opérateur, 2026-08-08)',
        fn (string $html): bool => (bool) preg_match('/<figure class="orphan"><img/', $html),
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
