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

// LA PAGE, C'EST AUSSI CE QU'ELLE CHARGE. Its style and its script moved out into their own files on 2026-08-09, and the built page now only carries a link and a
// src towards them. Reading the page alone would then declare nine behaviours lost while every one of them was intact, one file away — a validator that follows the
// content is part of the move, not a step to remember afterwards.
foreach (['page.css', 'page.js'] as $carried) {
    $path = $root . '/review-server/suivi-sprites/' . $carried;
    if (!is_file($path)) {
        fwrite(STDERR, "FAULT « {$carried} » manque à la page des sprites : elle le charge et il n'existe pas.\n");
        exit(1);
    }
    $html .= "\n" . file_get_contents($path);
}

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
        fn (string $html): bool => (bool) preg_match("/act === 'rework' \|\| act === 'discarded'/", $html),
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
        fn (string $html): bool => str_contains($html, 'chosen.length > 1'),
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
    // LE RELEVÉ À COPIER N'EXISTE PLUS, et sa règle part avec lui (opérateur, 2026-08-11 : « je n'ai pas besoin de la fonctionnalité pour copier le relevé »,
    // puis « normalement, y'a plus de relevé »). Il servait à lui donner un texte à coller dans la conversation ; les verdicts partent maintenant au serveur à la
    // coche, et `php scripts/remarks.php list` en dit autant depuis le fichier. Un contrôle qui garde un comportement supprimé accuse le code d'une perte voulue.
    [
        'Un bouton quitte la comparaison depuis l\'intérieur',
        'sans lui, on en sort en décochant chaque variant un par un, ou en fermant le panneau — donc en perdant le sujet qu\'on juge (opérateur, 2026-08-07)',
        fn (string $html): bool => str_contains($html, 'class="quit-comparison"'),
    ],
    [
        'Ce bouton n\'apparaît que pendant la comparaison, et par la classe de la liste',
        'un affichage recalculé en JavaScript à côté de la classe se désynchronise ; ici la classe « comparison » est la seule source',
        fn (string $html): bool => (bool) preg_match('/\.variants\.comparison \.quit-comparison\s*\{/', $html),
    ],
    [
        'Le marquage des variants supporte un variant sans case à cocher',
        'un variant à produire n\'a pas de case : lire « .checked » sans vérifier levait, et la ligne suivante — celle qui engage la comparaison — n\'était jamais atteinte (2026-08-08)',
        fn (string $html): bool => (bool) preg_match('/var pick = variant\.querySelector\(\x27\.compare\x27\);/', $html),
    ],
    [
        'La fermeture retombe sur le panneau visible quand la pile est vide',
        'la pile vit en mémoire : vidée alors qu\'un panneau est à l\'écran, le bouton de fermeture ne fait plus rien et la page reste bloquée',
        fn (string $html): bool => str_contains($html, "document.querySelector('.fsp:not([hidden])')"),
    ],
];

/**
 * Le préfixe que la page fusionnée pose sur les classes de la maquette montée, pour que les deux outils cessent de se marcher dessus.
 *
 * ÉCRIT UNE FOIS ICI PARCE QUE TROIS RÈGLES LE COMPARENT, et qu'un préfixe recopié dans trois chaînes est un préfixe qu'on changera dans deux. Il valait « mq- »
 * jusqu'au 2026-08-12 — une abréviation française dans du code, ce que l'opérateur a refusé : un symbole de code est anglais, y compris abrégé.
 */
const MOCKUP_PREFIX = 'mockup-';

// LA PAGE CAMPAGNE PORTE DEUX FOIS LE MÊME OUTIL DE REMARQUES — une copie pour le plan de composition, une pour la maquette montée, la seconde préfixée.
// Les faire converger est un remaniement à risque sur une page relue tous les jours, et le premier pas est de FIGER CE QUI DOIT SURVIVRE : sans ce filet, la
// convergence se contrôle à l'œil, et deux comportements repartent — c'est déjà arrivé deux fois sur la page des sprites.
//
// Chaque règle est vérifiée SUR LES DEUX OUTILS, sauf celles qui portent sur le classement des traitées : le plan seul le sait faire aujourd'hui, et la maquette
// doit l'hériter de la convergence. Une règle qui l'exigerait déjà des deux échouerait avant qu'on ait commencé.
$campaign = $root . '/review-server/maquette-campagne/page.html';
if (!is_file($campaign)) {
    fwrite(STDERR, "FAULT la page Campagne n'est pas construite — php review-server/build.php /maquette-campagne\n");
    exit(1);
}
$campaignHtml = file_get_contents($campaign);

/** Un comportement attendu des DEUX outils : la même classe, une fois nue pour le plan, une fois préfixée pour la maquette. */
$onBoth = fn (string $name): callable => fn (string $html): bool =>
    str_contains($html, 'class="' . $name . '"') && str_contains($html, 'class="' . MOCKUP_PREFIX . $name . '"');

$campaignRules = [
    // LA CLASSE TESTÉE ICI ÉTAIT `code`, ET ELLE NE PORTAIT PAS CE COMPORTEMENT (corrigé le 2026-08-11). Le survol est annoncé par l'élément `.survol`, présent
    // des deux côtés ; `code` n'apparaît dans la maquette montée que dans la LISTE DES SUJETS SANS IMAGE. La règle passait donc tant qu'il manquait une image, et
    // elle a crié le jour où il n'en manquait plus — un contrôle qui dépend du contenu au lieu du comportement dit « perdu » sur une page intacte.
    ['Le survol annonce la case sous le curseur', 'sans lui, on pose une remarque sur une case qu\'on croit désigner', $onBoth('survol')],
    ['Un clic ouvre la saisie', 'c\'est le seul geste qui attache une remarque à une case', $onBoth('poser')],
    ['La saisie s\'annule', 'un clic malheureux ne doit pas obliger à écrire pour s\'en sortir', $onBoth('annuler')],
    ['Les remarques posées se listent', 'une remarque qu\'on ne relit pas est une remarque perdue', $onBoth('remarques')],
    // LA COPIE DU RÉCAPITULATIF N'EST PLUS UN COMPORTEMENT, ELLE EST UN INTERDIT (opérateur, 2026-08-12 : « tous les mécanismes avec relevé doivent disparaitre,
    // tout doit être mis sur le serveur »). La règle ne disparaît donc pas : elle se retourne. Sans elle, rien n'empêcherait le bouton de revenir au premier
    // constructeur qui trouverait pratique de « rendre la liste copiable », et personne ne le verrait avant que l'opérateur ne le signale.
    [
        'Aucun relevé ne se copie, sur aucune des deux vues',
        'un bouton de copie est un canal vers la conversation, et tout passe désormais par le serveur',
        fn (string $html): bool => !str_contains($html, 'class="copier"') && !str_contains($html, 'class="' . MOCKUP_PREFIX . 'copier"'),
    ],
    ['Les remarques s\'effacent', 'sans retrait, la liste ne se vide jamais et cesse d\'être lue', $onBoth('effacer')],
    [
        'Les DEUX vues classent une remarque traitée et savent la rouvrir',
        'une remarque dont je me suis occupé qui revient à chaque lecture a coûté cinq redites le 2026-08-06 ; la maquette en a hérité en rejoignant l\'outil commun',
        // LA RÈGLE A ÉTÉ DURCIE LE 2026-08-12, AVEC LA CONVERGENCE : elle n'exigeait la réouverture que du plan, parce que la maquette ne savait pas le faire. Elle
        // le sait, donc la règle l'exige — une règle laissée au niveau de l'ancienne moitié laisserait la capacité se reperdre sans que rien ne le dise.
        fn (string $html): bool => $onBoth('rouvrir')($html) && str_contains($html, 'dataset.resolus'),
    ],
];

$lost = [];
foreach ($rules as [$what, $why, $holds]) {
    if (!$holds($html)) {
        $lost[] = "  PERDU : {$what}\n          {$why}";
    }
}
foreach ($campaignRules as [$what, $why, $holds]) {
    if (!$holds($campaignHtml)) {
        $lost[] = "  PERDU (page Campagne) : {$what}\n          {$why}";
    }
}

if ($lost) {
    fwrite(STDERR, count($lost) . " comportement(s) perdu(s) sur les pages de revue :\n" . implode("\n", $lost) . "\n");
    exit(1);
}

printf("La page des sprites tient ses %d comportements, la page Campagne ses %d.\n", count($rules), count($campaignRules));
