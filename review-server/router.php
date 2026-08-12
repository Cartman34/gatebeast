<?php
/**
 * Usage: never called by hand — this is the router handed to PHP's built-in server by serve.php.
 *
 * Intention: give every review page a short, stable address (/parc, /sprites) instead of the path of the file that happens to hold it. A page can then be rebuilt, renamed or split without the
 * address changing — which is the whole point of serving locally rather than publishing: the address stops being a thing to keep.
 *
 * Anything that is not a declared page falls through to the file on disk, from the repository root: that is how a page reaches an image, a stylesheet or a plan without any of them being copied or
 * encoded into it. Returning false hands the request back to the built-in server, which serves the file itself.
 */

$root = dirname(__DIR__);
$here = __DIR__;
$pages = require $here . '/pages.php';
$path = rtrim(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH), '/');

/**
 * Yesterday's addresses, and where they lead today.
 *
 * An address that has been opened once lives outside this repository — in a bookmark, in a message, in the memory of whoever types it. Renaming it with nothing left behind breaks it for everyone
 * except the one who renamed it. The redirect is permanent: the browser remembers the new one and stops asking for the old.
 */
const LEGACY_ROUTES = ['/scene' => '/maquette-campagne'];

if (isset(LEGACY_ROUTES[$path])) {
    header('Location: ' . LEGACY_ROUTES[$path], true, 301);

    return true;
}

/**
 * A page's signature: what changes when the page changes, and nothing else.
 *
 * A built page is signed by its file's date — writing the file IS the change. The home page is written nowhere, so it is signed by its sources: the registry it lists, plus the two files that decide
 * how it is shown.
 *
 * THE DATE OF THE TRACKING DOCUMENT WAS NOT A SIGNATURE, and that was the first attempt: the operator saw the home page announce a new version every time anything at all was written into the
 * tracking document, which happens constantly. The registry has since moved out of it entirely, which settles the matter at its root: the page now watches exactly what it shows.
 */
/**
 * The remarks of a page: read on load, replaced whenever they change.
 *
 * The server is the only writer. A page is a copy on someone's screen, possibly an old one; letting each copy write to the file would have the last reload win and silently drop what was written
 * elsewhere. The page sends its whole list, so a removal is simply a list without it.
 */
if ($path === '/notes') {
    require_once $here . '/bootstrap.php';
    $notes = Notes::get();
    $route = $_GET['page'] ?? '';
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'POST') {
        $notes->save($route, json_decode(file_get_contents('php://input'), true, 512, JSON_THROW_ON_ERROR));
        echo '{"ecrit":true}';

        return true;
    }
    echo json_encode($notes->forRoute($route), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

    return true;
}

/**
 * The rune anchor of one representation, posed from the review page.
 *
 * THE WRITE GOES THROUGH THE TOOL THAT ALREADY OWNS IT, `scripts/set-rune-anchor.py`, and not through a second writer of the referential written here. That tool
 * refuses an unknown path, a subject that is not a creature, a representation without measures and a point outside the image — four refusals this route would
 * otherwise have to repeat, and would repeat slightly differently. Its fault message comes back as it stands, so the page says what the tool said.
 */
if ($path === '/rune-anchor') {
    require_once $here . '/bootstrap.php';
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    $asked = json_decode(file_get_contents('php://input'), true, 512, JSON_THROW_ON_ERROR);
    foreach (['path', 'x', 'y'] as $key) {
        if (!isset($asked[$key])) {
            http_response_code(400);
            echo json_encode(['fault' => "la demande n'a pas de « {$key} »"], JSON_UNESCAPED_UNICODE);

            return true;
        }
    }
    $command = sprintf('python3 %s --path %s --x %s --y %s 2>&1',
        escapeshellarg(dirname($here) . '/scripts/set-rune-anchor.py'),
        escapeshellarg((string) $asked['path']), escapeshellarg((string) round((float) $asked['x'], 1)), escapeshellarg((string) round((float) $asked['y'], 1)));
    exec($command, $lines, $status);
    if ($status !== 0) {
        http_response_code(422);
        echo json_encode(['fault' => implode("\n", $lines)], JSON_UNESCAPED_UNICODE);

        return true;
    }
    echo json_encode(['ecrit' => true, 'dit' => implode("\n", $lines)], JSON_UNESCAPED_UNICODE);

    return true;
}

if ($path === '/version') {
    header('Content-Type: text/plain; charset=utf-8');
    // The answer must never be served from the browser's cache: a signature kept in reserve would say forever that nothing has changed.
    header('Cache-Control: no-store');
    $wanted = $_GET['page'] ?? '';

    if ($wanted === '/') {
        $signature = 0;
        foreach (['/artefacts.json', '/pages.php', '/index.php'] as $source) {
            $signature = max($signature, is_file($here . $source) ? filemtime($here . $source) : 0);
        }
        echo $signature;

        return true;
    }

    foreach ($pages as $page) {
        if ($page['route'] === $wanted) {
            $file = $here . '/' . $page['file'];
            echo is_file($file) ? filemtime($file) : 0;

            return true;
        }
    }

    http_response_code(404);
    echo 'unknown';

    return true;
}

if ($path === '') {
    require $here . '/index.php';

    return true;
}

foreach ($pages as $page) {
    if ($page['route'] !== $path) {
        continue;
    }
    $file = $here . '/' . $page['file'];
    if (!is_file($file)) {
        require_once $here . '/bootstrap.php';
        $reload = Reload::get();
        http_response_code(503);
        header('Content-Type: text/html; charset=utf-8');
        // A page that was never built says so, and says how to build it. A blank screen would send the reader looking for a bug that does not exist. It watches like any other page, so it gives way
        // to the real one the moment the build lands — without that, whoever waited here stayed here.
        printf('<meta charset="utf-8"><style>%s
body { margin: 0; padding: 2rem 1.5rem; background: #17151d; color: #eeecf3; font-family: system-ui, sans-serif; }</style>
<p>La page « %s » n\'est pas encore construite.</p><p>Pour la produire :</p><pre>%s</pre>%s%s',
            $reload->styles(), htmlspecialchars($page['title'], ENT_QUOTES), htmlspecialchars($page['build'], ENT_QUOTES), $reload->markup(), $reload->script($page['route']));

        return true;
    }
    header('Content-Type: text/html; charset=utf-8');
    readfile($file);

    return true;
}

return false;
