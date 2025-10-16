#!/usr/bin/env bash
# Claude Defender - Snapshot Tool
# Creates backup of critical files before changes

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/.claude-defender/backups/$TIMESTAMP"
REPO_DIR="$HOME/ariannamethod"

echo "[Claude Defender] Creating snapshot: $TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup critical files
if [ -f "$REPO_DIR/arianna.py" ]; then
    cp "$REPO_DIR/arianna.py" "$BACKUP_DIR/arianna.py.backup"
    echo "  ✓ Backed up arianna.py"
fi

if [ -f "$REPO_DIR/monday.py" ]; then
    cp "$REPO_DIR/monday.py" "$BACKUP_DIR/monday.py.backup"
    echo "  ✓ Backed up monday.py"
fi

if [ -f "$REPO_DIR/resonance.sqlite3" ]; then
    cp "$REPO_DIR/resonance.sqlite3" "$BACKUP_DIR/resonance.sqlite3.backup"
    echo "  ✓ Backed up resonance.sqlite3"
fi

# Git stash
cd "$REPO_DIR"
if [ -n "$(git status --porcelain)" ]; then
    git stash push -m "Claude Defender snapshot: $TIMESTAMP"
    echo "  ✓ Git stashed changes"
else
    echo "  ⚠ No git changes to stash"
fi

# Log snapshot
echo "$(date --iso-8601=seconds): [SNAPSHOT] Created backup at $BACKUP_DIR" >> "$HOME/.claude-defender/logs/snapshots.log"

echo "[Claude Defender] Snapshot complete: $BACKUP_DIR"
