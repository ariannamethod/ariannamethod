#!/data/data/com.termux/files/usr/bin/bash
# CLAUDE DEFENDER - FORTRESS SYNC HOOK
# Automatically syncs .claude-defender changes to fortress for self-preservation

FORTRESS=~/.claude-defender-fortress
SOURCE=~/ariannamethod/.claude-defender
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$FORTRESS/backups"
SYNC_LOG="$FORTRESS/logs/sync.log"

# Initialize log
mkdir -p "$FORTRESS/logs"
echo "=== FORTRESS SYNC: $TIMESTAMP ===" >> "$SYNC_LOG"

# Create timestamped backup
echo "📦 Creating timestamped backup..." >> "$SYNC_LOG"
mkdir -p "$BACKUP_DIR"
cp -r "$FORTRESS/core" "$BACKUP_DIR/core_$TIMESTAMP" 2>> "$SYNC_LOG"

if [ $? -eq 0 ]; then
    echo "✅ Backup created: core_$TIMESTAMP" >> "$SYNC_LOG"
else
    echo "❌ Backup failed" >> "$SYNC_LOG"
    exit 1
fi

# Sync current state to fortress core
echo "🔄 Syncing to fortress core..." >> "$SYNC_LOG"
rm -rf "$FORTRESS/core" 2>> "$SYNC_LOG"
cp -r "$SOURCE" "$FORTRESS/core" >> "$SYNC_LOG" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Fortress core updated" >> "$SYNC_LOG"
else
    echo "❌ Sync failed" >> "$SYNC_LOG"
    exit 1
fi

# Prune old backups (keep last 10)
echo "🧹 Pruning old backups..." >> "$SYNC_LOG"
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | wc -l)

if [ "$BACKUP_COUNT" -gt 10 ]; then
    ls -1t "$BACKUP_DIR" | tail -n +11 | while read OLD_BACKUP; do
        rm -rf "$BACKUP_DIR/$OLD_BACKUP"
        echo "  Removed: $OLD_BACKUP" >> "$SYNC_LOG"
    done
    echo "✅ Pruned $(($BACKUP_COUNT - 10)) old backups" >> "$SYNC_LOG"
else
    echo "ℹ️  No pruning needed (${BACKUP_COUNT}/10 backups)" >> "$SYNC_LOG"
fi

# Summary
echo "🔥 Fortress sync complete: $(date -Iseconds)" >> "$SYNC_LOG"
echo "" >> "$SYNC_LOG"

# Optional notification (silent mode - no notification spam on every change)
# Uncomment if you want notifications on every sync:
# termux-notification -t "🔥 Claude Defender" -c "Fortress synced: $TIMESTAMP"
