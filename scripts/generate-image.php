<?php
/**
 * Low level image generation wrapper.
 *
 * An agent cannot draw; Codex can. This script is the single entry point: it takes a description and an
 * output path, and yields the produced file.
 *
 * Usage: php gatebeast/scripts/generate-image.php <output.png> "<description>" [<output2.png> "<description2>" ...]
 *
 * The IMAGE_JOBS environment variable overrides how many generations run at once, and IMAGE_MODEL names the model the agent should run on — left unset, the
 * agent uses its own configured default. Each finished job prints "SESSION <output> <id>", the id a session is reopened with (`codex exec resume <id>`).
 *
 * Requirements: the `codex` command must be available. Descriptions are passed through untouched — style,
 * framing and prohibitions belong to the caller, not to this tool.
 * Limits: an existing file is never regenerated (delete it to redo); one generation may take up to 15 minutes.
 */

const DEFAULT_JOBS = 12;
const JOB_TIMEOUT = 900;
// The generator is an agent working on one subject, and what it did is a TRACE of that run: it is written beside that run's report, under var/generations/
// in the folder mirroring the image's own, and under the same name. Not beside the image — assets/ holds assets, and an event log runs to megabytes. The
// report names this file, so retrieving what happened during a generation costs nothing.
const TRACES = __DIR__ . '/../var/generations';
// The agent always runs from the PROJECT ROOT, never from the folder its image happens to land in. A session belongs to the directory it was launched from
// and is offered nowhere else, so scattering them across assets/poc/sol, assets/poc/cloture and the rest made them unfindable afterwards. From the root,
// every session of the project is listed in one place — and every path a consigne quotes, reference or plan, is reachable from there too.
const PROJECT_ROOT = __DIR__ . '/..';

$jobs = (int) (getenv('IMAGE_JOBS') ?: DEFAULT_JOBS);
$jobs = max(1, $jobs);
// The model the agent runs on. Empty means its own configured default, which is what production uses;
// naming one here is how a generation is tried on another model without touching anyone's config.
$model = (string) (getenv('IMAGE_MODEL') ?: '');
// What is being produced, which is also the folder its traces go to: `sprites` for a sprite, `subjects` for a usage sample.
$traceKind = preg_replace('/[^a-z]/', '', (string) (getenv('IMAGE_TRACE_KIND') ?: 'sprites'));

$arguments = array_slice($argv, 1);
if( count($arguments) < 2 || count($arguments) % 2 !== 0 ) {
	fwrite(STDERR, "Usage: php generate-image.php <output.png> \"<description>\" [...]\n");
	exit(1);
}

$queue = [];
for( $index = 0; $index < count($arguments); $index += 2 ) {
	$queue[] = ['output' => $arguments[$index], 'description' => $arguments[$index + 1]];
}

/**
 * Starts one generation, returning the running job or null when it could not be started.
 */
function startJob(array $task): ?array {
	$output = $task['output'];
	$directory = dirname($output);
	if( !is_dir($directory) && !mkdir($directory, 0775, true) ) {
		fwrite(STDERR, "Cannot create directory: $directory\n");

		return null;
	}
	$root = realpath(PROJECT_ROOT);
	$target = realpath($directory) . '/' . basename($output);
	// Given relative to the root the agent runs in, so it writes exactly where the chain expects the image — it no longer works inside the output folder.
	$relative = str_starts_with($target, $root . '/') ? substr($target, strlen($root) + 1) : $target;
	// Said in as many words because the agent runs at the project root and finds the project's own generation tooling there: one run answered by EXECUTING
	// scripts/generate-sprite-subject.py and looping back into the chain instead of drawing, and produced nothing. Its task is to draw, and only that.
	$prompt = $task['description']
		. "\n\nTU ES UN ILLUSTRATEUR. TA SEULE TÂCHE EST DE GÉNÉRER CETTE IMAGE et de l'enregistrer au format PNG dans ./$relative. Aucun autre fichier."
		. "\nTu génères l'image toi-même, avec ton propre outil de génération d'images. N'exécute AUCUN script du dépôt, n'appelle aucun outil du projet et"
		. " ne relance aucune chaîne de production : ce dépôt n'est là que pour que tu puisses ouvrir les fichiers de référence cités dans la consigne.";
	// --json makes the agent emit its events as JSONL, which is the only way its SESSION ID reaches us. That id is what lets a session be reopened later
	// (`codex exec resume <id>`) to see what actually happened during a generation, so it is captured here and reported to the caller below.
	$model = $GLOBALS['model'];
	$command = ['codex', 'exec', '--json', '--skip-git-repo-check', '--sandbox', 'workspace-write'];
	if( $model !== '' ) {
		array_push($command, '--model', $model);
	}
	$command[] = $prompt;
	$escaped = implode(' ', array_map('escapeshellarg', $command));
	$traceDirectory = TRACES . '/' . $GLOBALS['traceKind'];
	if( !is_dir($traceDirectory) ) {
		mkdir($traceDirectory, 0775, true);
	}
	$log = $traceDirectory . '/' . pathinfo(basename($output), PATHINFO_FILENAME) . '-generateur.jsonl';
	$descriptors = [1 => ['file', $log, 'w'], 2 => ['file', $log, 'a']];
	$process = proc_open($escaped, $descriptors, $pipes, $root);

	return $process === false ? null
		: ['process' => $process, 'output' => $output, 'startedAt' => time(), 'log' => $log];
}

/**
 * Reads the agent's session id out of the events it wrote, or null when none is there.
 *
 * The id is what makes a generation reopenable afterwards, so it is looked for BY KEY rather than by position: the event carrying it has changed shape
 * between versions of the agent, and any of these keys naming a UUID is the same thing under a different name.
 */
function sessionIdOf(string $log): ?string {
	if( !is_file($log) ) {
		return null;
	}
	$pattern = '/"(?:session_id|thread_id|conversation_id|id)"\s*:\s*"([0-9a-fA-F-]{36})"/';

	return preg_match($pattern, (string) file_get_contents($log), $found) ? $found[1] : null;
}

$running = [];
$results = [];

while( $queue || $running ) {
	while( $queue && count($running) < $jobs ) {
		$task = array_shift($queue);
		if( is_file($task['output']) ) {
			$results[$task['output']] = true;
			continue;
		}
		$job = startJob($task);
		if( $job ) {
			$running[] = $job;
		} else {
			$results[$task['output']] = false;
		}
	}
	foreach( $running as $key => $job ) {
		$status = proc_get_status($job['process']);
		$expired = time() - $job['startedAt'] > JOB_TIMEOUT;
		if( $status['running'] && !$expired ) {
			continue;
		}
		if( $expired ) {
			proc_terminate($job['process']);
		}
		proc_close($job['process']);
		unset($running[$key]);
		$results[$job['output']] = is_file($job['output']);
		$session = sessionIdOf($job['log']);
		// Printed for the caller, which puts it in the image's report: without it a generation cannot be reopened, and what the agent did is lost for good.
		echo 'SESSION ' . $job['output'] . ' ' . ($session ?? 'inconnue') . "\n";
	}
	if( $running ) {
		usleep(500000);
	}
}

$failures = 0;
foreach( $results as $path => $succeeded ) {
	echo($succeeded ? "OK $path" : "FAILED $path") . "\n";
	$failures += $succeeded ? 0 : 1;
}
echo $failures === 0 ? "DONE\n" : "DONE WITH $failures FAILURE(S)\n";
exit($failures === 0 ? 0 : 1);
