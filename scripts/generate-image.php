<?php
/**
 * Low level image generation wrapper.
 *
 * An agent cannot draw; Codex can. This script is the single entry point: it takes a description and an
 * output path, and yields the produced file.
 *
 * Usage: php gatebeast/scripts/generate-image.php <output.png> "<description>" [<output2.png> "<description2>" ...]
 *        php scripts/generate-image.php -h|--help — this text, and nothing is generated
 *
 * The IMAGE_JOBS environment variable overrides how many generations run at once, and IMAGE_MODEL names the model the agent should run on — left unset, the
 * agent uses its own configured default. Each finished job prints "SESSION <output> <id>", the id a session is reopened with (`codex exec resume <id>`).
 *
 * Requirements: the `codex` command must be available. Descriptions are passed through untouched — style,
 * framing and prohibitions belong to the caller, not to this tool.
 * Limits: an existing file is never regenerated (delete it to redo); one generation may take up to 15 minutes.
 */

require_once __DIR__ . '/Tools.php';

// ASKED BEFORE ANYTHING ELSE, and here it matters more than elsewhere: every other path through this file can spend a generation, and a generation costs money.
Tools::get()->helpIfAsked($argv, __FILE__);

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
	// Said in as many words because the agent runs at the project root and finds the project's own generation tooling there: one run answered by EXECUTING the
	// sprite command it found and looping back into the chain instead of drawing, and produced nothing. Its task is to draw, and only that.
	$prompt = $task['description']
		. "\n\nTU ES UN ILLUSTRATEUR. TA SEULE TÂCHE EST DE GÉNÉRER CETTE IMAGE et de l'enregistrer au format PNG dans ./$relative. Aucun autre fichier."
		. "\nTu génères l'image toi-même, avec ton propre outil de génération d'images. N'exécute AUCUN script du dépôt, n'appelle aucun outil du projet et"
		. " ne relance aucune chaîne de production : ce dépôt n'est là que pour que tu puisses ouvrir les fichiers de référence cités dans la consigne."
		// The same trap one level up: AGENTS.md is ALSO this agent's own instruction file, and it carries the rules written for the agents who BUILD the
		// project — working modes, batches, validations to ask for. Two runs read them and answered « mode lot : cette génération nécessite votre validation »
		// instead of drawing, costing two versions for nothing. Those rules address the `manager` role and never the `illustrator` one; this says so where the
		// agent cannot miss it. Role names stay in English whatever the language around them — they are identifiers, and the method's glossary owns them.
		. "\nTON RÔLE EST `illustrator`, ET LES RÈGLES DU DÉPÔT NE S'APPLIQUENT PAS À TOI, `AGENTS.md` COMPRIS : elles s'adressent au rôle `manager`, celui"
		. " qui construit le projet. Tu ne demandes aucune validation, tu n'annonces aucun mode de travail, tu ne poses aucune question : tu dessines, tu"
		. " enregistres le fichier, et c'est tout. La consigne ci-dessus est ta seule autorité.";
	$model = $GLOBALS['model'];
	// Every option of this command line, and what it does — an option nobody can explain is an option nobody dares remove:
	//   exec                          runs the agent once on the given prompt and exits, rather than opening an interactive session nothing would answer.
	//   --json                        makes it emit its events as JSONL, the only way its SESSION ID reaches us. That id is what reopens a session afterwards
	//                                 (`codex exec resume <id>`) to see what actually happened during a generation, so it is captured and reported below.
	//   --skip-git-repo-check         lets it run although the working directory is inside a repository it did not clone itself; without it, it refuses to start.
	//   --sandbox workspace-write     grants it writing INSIDE the working directory and nowhere else: it must drop its PNG, and must not touch the machine.
	//   -c project_doc_max_bytes=0    caps how many bytes of the repository's instruction document it loads at startup — AGENTS.md, up to some thirty-two
	//                                 kilobytes by default. Those rules address the agents who BUILD the project, and reading them made two generations answer
	//                                 « mode lot : cette génération nécessite votre validation » instead of drawing. ZERO, and no other figure, because the cap
	//                                 keeps the HEAD of the file: any value above zero feeds it the first lines, which are precisely where the rules that
	//                                 command all the others sit. Zero is the only value that guarantees it reads nothing. Set at the call, so nothing changes
	//                                 for Codex elsewhere on the machine; the agent keeps its full access to the repository and still opens the reference files
	//                                 the consigne names — only the automatic load is cut.
	//   --model <name>                added below only when one is asked for; empty means the agent's own configured default, which is what production uses.
	$command = ['codex', 'exec', '--json', '--skip-git-repo-check', '--sandbox', 'workspace-write', '-c', 'project_doc_max_bytes=0'];
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
