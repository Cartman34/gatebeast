<?php
/**
 * Low level image generation wrapper.
 *
 * An agent cannot draw; Codex can. This script is the single entry point: it takes a description and an
 * output path, and yields the produced file.
 *
 * Usage: php gatebeast/scripts/generate-image.php <output.png> "<description>" [<output2.png> "<description2>" ...]
 *
 * The IMAGE_JOBS environment variable overrides how many generations run at once.
 *
 * Requirements: the `codex` command must be available. Descriptions are passed through untouched — style,
 * framing and prohibitions belong to the caller, not to this tool.
 * Limits: an existing file is never regenerated (delete it to redo); one generation may take up to 15 minutes.
 */

const DEFAULT_JOBS = 12;
const JOB_TIMEOUT = 900;

$jobs = (int) (getenv('IMAGE_JOBS') ?: DEFAULT_JOBS);
$jobs = max(1, $jobs);

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
	$fileName = basename($output);
	$prompt = $task['description']
		. "\n\nSave the generated image as PNG to ./$fileName in the current directory. No other file.";
	$command = ['codex', 'exec', '--skip-git-repo-check', '--sandbox', 'workspace-write', $prompt];
	$escaped = implode(' ', array_map('escapeshellarg', $command));
	$descriptors = [1 => ['file', '/dev/null', 'w'], 2 => ['file', '/dev/null', 'w']];
	$process = proc_open($escaped, $descriptors, $pipes, realpath($directory));

	return $process === false ? null : ['process' => $process, 'output' => $output, 'startedAt' => time()];
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
