<?php
/**
 * USAGE
 *   The screen format of the review pages, held once: `Layout::get()->css()` in the page's styles, then `.wrap` around the page, `.measure` around a text meant
 *   to be read, `.grid` around a set of cards. A page declares no width of its own any more.
 *
 * INTENTION
 *   ONE SCREEN FORMAT, AND IT TAKES 4K (operator, 2026-08-12: « standardise le format d'écran responsive acceptant les écrans 4K »). Every page declared its own
 *   width and all of them said 1100 pixels: on a 4K screen, a ribbon in the middle of three thousand eight hundred pixels of nothing. A value copied into five
 *   pages is a value one changes in three.
 *
 *   A PAGE WIDTH IS NOT A READING WIDTH, and confusing the two produces both opposite defects. A wide page is for COMPARING — thumbnails side by side, fifteen
 *   subjects at a glance; a text stops being readable past sixty or so characters, the eye losing its place on the way back. So the container takes the whole
 *   screen and the text keeps its measure inside it.
 *
 *   THE GRID FILLS ITSELF, IT IS NEVER COUNTED. A column count written by hand is right on the screen of whoever wrote it and wrong on every other: the grid
 *   declares the MINIMUM width of a card and lets the browser lay down as many as it can — one on a phone, eight on a 4K, and nobody has anything to decide.
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
