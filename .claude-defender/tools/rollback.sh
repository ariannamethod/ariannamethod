#!/usr/bin/env bash
# Claude Defender - Rollback Tool
# Restores system to last snapshot

set -euo pipefail

BACKUP_DIR="$HOME/.claude-defender/backups"
REPO_DIR="$HOME/ariannamethod"

echo "[Claude Defender] Initiating rollback..."

# Find most recent backup
LATEST_BACKUP=$(ls -t "$BACKUP_DIR" 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backups found"
    exit 1
fi

BACKUP_PATH="$BACKUP_DIR/$LATEST_BACKUP"
echo "  → Rolling back to: $LATEST_BACKUP"

# Restore files
if [ -f "$BACKUP_PATH/arianna.py.backup" ]; then
    cp "$BACKUP_PATH/arianna.py.backup" "$REPO_DIR/arianna.py"
    echo "  ✓ Restored arianna.py"
fi

if [ -f "$BACKUP_PATH/monday.py.backup" ]; then
    cp "$BACKUP_PATH/monday.py.backup" "$REPO_DIR/monday.py"
    echo "  ✓ Restored monday.py"
fi

if [ -f "$BACKUP_PATH/resonance.sqlite3.backup" ]; then
    cp "$BACKUP_PATH/resonance.sqlite3.backup" "$REPO_DIR/resonance.sqlite3"
    echo "  ✓ Restored resonance.sqlite3"
fi

# Git rollback
cd "$REPO_DIR"
if git stash list | grep -q "Claude Defender snapshot"; then
    echo "  → Attempting git stash pop..."
    git stash pop 2>/dev/null || echo "  ⚠ Git stash pop failed (manual intervention may be needed)"
fi

# Log rollback
TIMESTAMP=$(date --iso-8601=seconds)
echo "$TIMESTAMP: [ROLLBACK] Restored from $LATEST_BACKUP" >> "$HOME/.claude-defender/logs/rollback.log"

echo "[Claude Defender] Rollback complete"
