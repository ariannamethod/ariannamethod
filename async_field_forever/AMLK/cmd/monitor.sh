#!/usr/bin/env bash
# Tail letsgo logs from the system log directory

set -euo pipefail

LOG_DIR="/arianna_core/log"

if [ ! -d "$LOG_DIR" ]; then
  echo "Log directory $LOG_DIR not found" >&2
  exit 1
fi
# Wait for at least one log file to exist before tailing
shopt -s nullglob
log_files=("$LOG_DIR"/*.log)
while [ ${#log_files[@]} -eq 0 ]; do
  echo "Waiting for logs in $LOG_DIR..."
  sleep 1
  log_files=("$LOG_DIR"/*.log)
done
shopt -u nullglob
tail -f "$LOG_DIR"/*.log
