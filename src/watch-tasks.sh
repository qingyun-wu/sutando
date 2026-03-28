#!/bin/bash
# Watch for new tasks and output a reminder to process ALL files.
# Usage: bash src/watch-tasks.sh (run_in_background: true)
#
# When fswatch detects a change, outputs a reminder message that
# the cron loop will read, ensuring ALL task files get processed.

TASKS_DIR="${1:-$(dirname "$0")/../tasks}"

fswatch -1 "$TASKS_DIR" >/dev/null 2>&1

# Output reminder — this is what the cron loop reads
echo "TASK_DETECTED: Process ALL .txt files in tasks/ before restarting the watcher. Do not process only one."
ls "$TASKS_DIR"/*.txt 2>/dev/null || true
