<?php
/**
 * USAGE
 *   require_once __DIR__ . '/../lib/Theme.php';
 *   $theme = Theme::get();      // l'instance du service, à prendre une fois
 *   echo $theme->css('encre');  // à poser en tête du <style> de la page
 *
 * INTENTION
 *   Un thème est un jeu de variables de couleur, et rien d'autre : il vit dans son propre fichier sous `themes/`, la page inclut celui qu'elle veut, et changer d'habillage ne demande de toucher
 *   aucune page. C'est ce qui permet d'en essayer un sans risquer la mise en page — et d'en garder plusieurs sans que le code ne se ramifie.
 *
 *   Un artefact est un fichier unique : le thème ne peut donc pas être une feuille liée, il est recopié dans la page à la construction. Le fichier reste la source, la copie n'est qu'un transport.
 */

class Theme
{
    private static ?self $instance = null;

    /** L'instance du service. C'est la SEULE méthode statique ici, et elle ne fait que ça : tout le travail est d'instance. */
    public static function get(): self
    {
        return self::$instance ??= new self();
    }

    public function css(string $name = 'encre'): string
    {
        $path = __DIR__ . '/themes/' . preg_replace('/[^a-z-]/', '', $name) . '.css';
        if (!is_file($path)) {
            throw new RuntimeException("FAULT le thème « {$name} » n'existe pas sous review-server/lib/themes/ — une page ne s'habille pas d'un thème inventé.");
        }

        return file_get_contents($path);
    }

    /** Les thèmes disponibles, pour qu'une page puisse les proposer sans les connaître d'avance. */
    public function disponibles(): array
    {
        return array_map(fn (string $path) => basename($path, '.css'), glob(__DIR__ . '/themes/*.css') ?: []);
    }
}
