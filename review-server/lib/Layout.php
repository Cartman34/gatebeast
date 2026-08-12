<?php
/**
 * USAGE
 *   The screen format of the review pages, held once: `Layout::get()->css()` in the page's styles, then `.wrap` around the page, `.measure` around a text meant
 *   to be read, `.grid` around a set of cards. A page declares no width of its own any more.
 *
 * INTENTION
 *   LE FORMAT D'ÉCRAN SE STANDARDISE, ET IL ACCEPTE LE 4K (opérateur, 2026-08-12 : « standardise le format d'écran responsive acceptant les écrans 4K »). Chaque
 *   page déclarait sa propre largeur, et toutes disaient 1100 pixels : sur un écran 4K, un ruban au milieu de trois mille huit cents pixels de vide. Une valeur
 *   recopiée dans cinq pages est une valeur qu'on change dans trois.
 *
 *   UNE LARGEUR DE PAGE N'EST PAS UNE LARGEUR DE LECTURE, et les confondre est ce qui produit les deux défauts opposés. Une page large sert à COMPARER — poser
 *   des vignettes côte à côte, voir quinze sujets d'un coup ; un texte, lui, cesse d'être lisible passé une soixantaine de caractères, et l'œil se perd en
 *   revenant à la ligne. Le conteneur prend donc tout l'écran, et le texte garde sa mesure à l'intérieur.
 *
 *   LA GRILLE SE REMPLIT, ELLE NE SE COMPTE PAS. Un nombre de colonnes écrit à la main est juste sur l'écran de celui qui l'a écrit et faux sur tous les autres :
 *   la grille déclare la largeur MINIMALE d'une carte et laisse le navigateur en poser autant qu'il peut. Sur un portable il en pose une, sur un 4K il en pose
 *   huit, et personne n'a rien à décider.
 */

class Layout
{
    private static ?self $instance = null;

    /** L'instance du service. C'est la SEULE méthode statique ici, et elle ne fait que ça : tout le travail est d'instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    /** Le format, en CSS, à recopier dans la page — un artefact est un fichier unique, le style ne peut pas être une feuille liée. */
    public function css(): string
    {
        return <<<'CSS'
  /* LE FORMAT D'ÉCRAN, TENU UNE FOIS POUR TOUTES LES PAGES (review-server/lib/Layout.php). Une page ne déclare plus ni largeur, ni marge de bord. */
  :root {
    /* La marge de bord suit l'écran : serrée sur un portable, large sur un moniteur, et jamais au-delà de ce qui reste confortable. */
    --gutter: clamp(14px, 2.2vw, 48px);
    /* Le plafond du conteneur. Réglé pour un 4K : 3840 pixels physiques donnent environ 2560 pixels CSS au grossissement habituel, et la page les occupe. */
    --wrap-max: 2560px;
    /* La mesure d'un texte suivi : au-delà, l'œil se perd en revenant à la ligne, quelle que soit la place disponible. */
    --measure: 78ch;
    /* La largeur minimale d'une carte dans une grille. En dessous, la grille en pose une de moins plutôt que de les écraser. */
    --card-min: 320px;
  }
  .wrap { width: min(100% - 2 * var(--gutter), var(--wrap-max)); margin-inline: auto; padding: 24px 0 96px; }
  .measure { max-width: var(--measure); }
  /* `min()` protège le cas étroit : sans lui, une carte de 320 pixels déborde d'un écran de 300 et la page défile de côté. */
  .grid { display: grid; gap: var(--gutter); grid-template-columns: repeat(auto-fill, minmax(min(100%, var(--card-min)), 1fr)); }
CSS;
    }
}
