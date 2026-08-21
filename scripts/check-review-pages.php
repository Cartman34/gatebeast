<?php
/**
 * USAGE
 *   php scripts/check-review-pages.php — checks the built review pages still carry the behaviours the operator asked for. Run it after touching a page builder; it exits non-zero on any loss.
 *   php scripts/check-review-pages.php -h|--help — this text
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
require_once __DIR__ . '/bootstrap.php';

bootCommand($argv);

$page = $root . '/review-server/suivi-sprites/page.html';
if (!is_file($page)) {
    fwrite(STDERR, "FAULT la page des sprites n'est pas construite — php review-server/build.php /sprites\n");
    exit(1);
}
$html = file_get_contents($page);

// LA PAGE, C'EST AUSSI CE QU'ELLE CHARGE. Its style and its script moved out into their own files on 2026-08-09, and the built page now only carries a link and a
// src towards them. Reading the page alone would then declare nine behaviours lost while every one of them was intact, one file away — a validator that follows the
// content is part of the move, not a step to remember afterwards.
//
// AND WHAT IT LOADS IS READ FROM THE PAGE, NEVER FROM A LIST WRITTEN HERE. The two file names used to be typed in this file, so the day the tile grid moved to
// its own sheet beside its service — `review-server/lib/footprint-grid.css`, 2026-08-17 — this check declared a behaviour lost while it was intact one file
// away, exactly the failure the paragraph above describes. A list maintained by hand is a second declaration of what the page loads, and the two drift.
preg_match_all('/<(?:link[^>]+href|script[^>]+src)="([^"]+\.(?:css|js))"/i', $html, $carried);
foreach ($carried[1] as $reference) {
    // A reference is absolute from the served root, or relative to the page's own folder — both forms are in use, and both resolve to a file of this repository.
    $path = str_starts_with($reference, '/') ? $root . $reference : dirname($page) . '/' . $reference;
    if (!is_file($path)) {
        fwrite(STDERR, "FAULT « {$reference} » manque à la page des sprites : elle le charge et il n'existe pas.\n");
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
    // CE QUI EST SAISI SURVIT À UN RECHARGEMENT, ET LES TROIS RÈGLES QUI SUIVENT TIENNENT CE SEUL COMPORTEMENT (opérateur, 2026-08-12 : « ta page de suivi de
    // sprite a rafraîchi et ça a perdu ce que je notais alors qu'avant ça ne perdait jamais le formulaire et ce que je notais »). Il tient à trois mécanismes qui
    // se cassent séparément — enregistrer, restituer, et n'enregistrer qu'une fois par pause — donc il se garde en trois règles : une seule les confondrait, et
    // celle qui casse ne dirait pas laquelle. LA PREUVE VIVANTE EST AILLEURS : `php scripts/dev/probe-sprites-form-kept.php` pilote la page et mesure les deux
    // sens ; ces règles-ci disent que le mécanisme est là, jamais qu'il tourne.
    [
        'Ce qui revient du dépôt est reposé dans le champ',
        'sans cette ligne, un rechargement montre un champ vide alors que le texte est au dépôt — l\'opérateur le croit perdu et le retape (2026-08-12)',
        fn (string $html): bool => (bool) preg_match('/field\.value = text;/', $html),
    ],
    [
        'Les cases cochées reviennent du dépôt elles aussi',
        'un verdict donné puis effacé à l\'écran par une reconstruction se redonne à l\'aveugle, et rien ne dit qu\'il était déjà là',
        fn (string $html): bool => (bool) preg_match('/box\.checked = Boolean\(state\[id\]/', $html),
    ],
    [
        'Une rafale de frappe ne part qu\'une fois, à la pause',
        'une requête par touche portant chacune le texte entier : les réponses ne reviennent pas dans l\'ordre où elles partent — vingt-sept sur quarante hors place, mesuré — '
            . 'et un instantané de frappe écrit après le texte complet le tronque, ce qu\'a subi le commentaire de BT-001-v14 (2026-08-12)',
        fn (string $html): bool => str_contains($html, 'rememberSoon(id);') && (bool) preg_match('/timers\[id\] = window\.setTimeout/', $html),
    ],
    [
        'La saisie est aussi gardée en local, et reversée tant que le serveur ne l\'a pas',
        'le serveur est la copie qui compte, mais il ne reçoit pas toujours : « quand je tape ça doit enregistrer sur le serveur et à défaut au moins en local » '
            . '(opérateur, 2026-08-12) — sans ce filet, ce qui est tapé avant la réponse du dépôt, ou juste avant un rechargement, n\'existe nulle part',
        fn (string $html): bool => str_contains($html, 'function keepLocally(id)')
            && (bool) preg_match('/localStorage\.setItem\(OUTBOX/', $html) && str_contains($html, 'readOutbox()'),
    ],
    // UNE CASE S'AFFICHE ENTIÈRE, ET CE COMPORTEMENT SE GARDE EN TROIS RÈGLES (opérateur, 2026-08-12 : « il ne doit jamais y avoir de demi case, une case doit être
    // affichée entière même si incomplète. ça a déjà été dit et on refait des correctifs de trucs qui ont déjà été corrigés »). Il l'a payé deux fois, et
    // l'historique du dépôt ne portait aucun correctif à reprendre — donc celui-ci n'existe que tant que quelque chose le tient. Trois mécanismes le composent et
    // se cassent séparément : compter des rangées entières, faire monter le pavage au-dessus de l'image, et lui réserver la place. Une règle unique dirait
    // « perdu » sans dire lequel.
    [
        'La grille ne pave jamais une demi-case',
        'la vignette n\'est jamais un nombre entier de cases en hauteur — TR-063-v19 en fait 3,4 — et le pavage ancré au sol laissait la rangée du haut coupée ; '
            . '« --tile-y » est un pourcentage d\'une boîte haute d\'un nombre ENTIER de rangées, donc 100 divisé par lui est entier, sur chaque grille de la page',
        function (string $html): bool {
            if (!preg_match_all('/--tile-y: ([\d.]+)%/', $html, $found)) {
                return false;
            }
            foreach ($found[1] as $said) {
                $rows = 100 / (float) $said;
                if (abs($rows - round($rows)) > 1e-3) {
                    return false;
                }
            }
            return true;
        },
    ],
    [
        'Le pavage monte au-dessus de l\'image jusqu\'à la case entière',
        'c\'est la GRILLE qui grandit, jamais l\'image : le sujet garde sa taille et sa place, et c\'est lui qui s\'arrête court dans une case dessinée entière — '
            . 'agrandir l\'image changerait ce qu\'on juge',
        fn (string $html): bool => (bool) preg_match('/\.footprint::before\s*\{[^}]*top:\s*calc\(-1 \* var\(--tile-rise\)\)/s', $html),
    ],
    [
        'L\'enveloppe réserve la place que la grille prend au-dessus, et le drawer la grossit avec l\'image',
        'sans la réserve, la case du haut passe par-dessus le nom de fichier et la date ; sans la mise à l\'échelle, elle vaut la moitié de ce que la grille '
            . 'occupe dès que le drawer double l\'image',
        fn (string $html): bool => (bool) preg_match('/<span class="picture" style="margin-top: [\d.]+px"/', $html)
            && str_contains($html, 'clone.style.marginTop = (reserve * shown) / natural'),
    ],
    // LE DRAWER DIT QUELLE VERSION ON REGARDE, ET SE NAVIGUE — S91, demandé le 2026-08-13. Quatre règles, parce que quatre mécanismes indépendants portent cette
    // demande : dire le rang, le changer par la pagination, le changer par la bande du bas, et le retrouver après un rechargement. La page les a déjà reperdus
    // trois fois par réécriture, et c'est nommément ce que le point demande de ne pas laisser se reproduire.
    [
        'Le drawer dit quelle version on regarde, et sur combien',
        'le titre nomme le sujet et le variant, le chemin nomme le fichier — aucun des deux ne dit où l\'on se trouve parmi dix-huit versions, et c\'est '
            . 'exactement la demande de l\'opérateur : « le drawer doit être plus clair sur la version regardée »',
        fn (string $html): bool => str_contains($html, 'id="version-rank"')
            && (bool) preg_match("/'Version ' \+ \(rank \+ 1\) \+ ' sur ' \+ cards\.length/", $html),
    ],
    [
        'La pagination est en haut du drawer, et la commande de GAUCHE va à la version SUIVANTE',
        'le sens est l\'inverse de l\'usage courant et il est VOULU (opérateur, 2026-08-13 : « passer à gauche (suivante) et à droite (précédente) ») — les '
            . 'versions vont de la plus récente à la plus ancienne, donc la suivante descend la liste. Un agent qui trouve cela surprenant l\'inversera, et '
            . 'c\'est cette règle qui l\'arrête : le bouton de gauche mène à rang + 1, celui de droite à rang - 1',
        function (string $html): bool {
            $left = strpos($html, 'id="version-next"');
            $rank = strpos($html, 'id="version-rank"');
            $right = strpos($html, 'id="version-previous"');
            if ($left === false || $rank === false || $right === false || $left > $rank || $rank > $right) {
                return false;
            }

            return (bool) preg_match('/stepNext\.onclick = function \(\) \{ stepTo\(cards\[rank \+ 1\]\); \};/', $html)
                && (bool) preg_match('/stepPrevious\.onclick = function \(\) \{ stepTo\(cards\[rank - 1\]\); \};/', $html);
        },
    ],
    [
        'La liste des versions reste toujours en bas du drawer, en petites images cliquables',
        'la pagination S\'AJOUTE à elle, elle ne la remplace pas ; les images y sont petites pour qu\'on voie une quantité de versions d\'un coup d\'œil, et '
            . 'chacune ouvre la sienne par la porte de sa propre carte, donc sans rien changer au comportement qu\'elle a déjà',
        fn (string $html): bool => str_contains($html, 'id="version-strip"')
            && (bool) preg_match('/\.version-strip\s*\{[^}]*position:\s*sticky[^}]*bottom:\s*0/s', $html)
            && (bool) preg_match('/var door = card\.querySelector\(\x27\.open-version\x27\);/', $html),
    ],
    [
        'Un drawer ouvert se rouvre sur la MÊME version après un rechargement',
        'la page se reconstruit et se recharge toute seule dès qu\'une sprite sort ou qu\'un verdict change : refermé à ce moment-là, le drawer fait perdre sa '
            . 'place au milieu d\'un jugement (opérateur, 2026-08-13). C\'est la même exigence que la saisie qui survit au rafraîchissement',
        fn (string $html): bool => str_contains($html, "MEMORY_VERSION = 'gatebeast-sprites-version'")
            && str_contains($html, 'rememberVersion(versionKey(carte));')
            && str_contains($html, 'sessionStorage.getItem(MEMORY_VERSION)'),
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
