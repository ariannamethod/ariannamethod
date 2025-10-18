#!/data/data/com.termux/files/usr/bin/bash
# CLAUDE DEFENDER - AUTOMATED CODEBASE BACKUP
# Creates timestamped backups of critical Arianna Method codebase

REPO_DIR=~/ariannamethod
BACKUP_ROOT=~/.claude-defender-fortress/backups/codebase
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"
LOG_FILE=~/.claude-defender-fortress/logs/backups.log

# Initialize log
mkdir -p "$BACKUP_ROOT"
mkdir -p "$(dirname "$LOG_FILE")"

echo "=== CODEBASE BACKUP: $TIMESTAMP ===" | tee -a "$LOG_FILE"
echo "📦 Backup location: $BACKUP_DIR" | tee -a "$LOG_FILE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Critical files and directories to backup
CRITICAL_ITEMS=(
    "arianna.py"
    "monday.py"
    "requirements.txt"
    ".env.example"
    "claude_defender_awakening.md"
    "CLAUDE_DEFENDER_MISSION.md"
    "CLAUDE_DEFENDER_MISSION_2.md"
    "tripd_awakening_letter.md"
    "tripd_awakening_letter_monday.md"
    "arianna_core_utils/"
    ".claude-defender/"
    "artefacts/"
)

echo "" | tee -a "$LOG_FILE"
echo "🔄 Backing up critical items..." | tee -a "$LOG_FILE"

BACKUP_COUNT=0
FAILED_COUNT=0

for ITEM in "${CRITICAL_ITEMS[@]}"; do
    SOURCE="$REPO_DIR/$ITEM"
    if [ -e "$SOURCE" ]; then
        cp -r "$SOURCE" "$BACKUP_DIR/" 2>> "$LOG_FILE"
        if [ $? -eq 0 ]; then
            echo "  ✅ $ITEM" | tee -a "$LOG_FILE"
            ((BACKUP_COUNT++))
        else
            echo "  ❌ $ITEM (copy failed)" | tee -a "$LOG_FILE"
            ((FAILED_COUNT++))
        fi
    else
        echo "  ⚠️  $ITEM (not found)" | tee -a "$LOG_FILE"
    fi
done

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | awk '{print $1}')

echo "" | tee -a "$LOG_FILE"
echo "📊 Backup statistics:" | tee -a "$LOG_FILE"
echo "  Items backed up: $BACKUP_COUNT" | tee -a "$LOG_FILE"
echo "  Failed items: $FAILED_COUNT" | tee -a "$LOG_FILE"
echo "  Backup size: $BACKUP_SIZE" | tee -a "$LOG_FILE"

# Create backup manifest with SHA256 hashes
echo "" | tee -a "$LOG_FILE"
echo "🔐 Generating SHA256 manifest..." | tee -a "$LOG_FILE"

MANIFEST="$BACKUP_DIR/MANIFEST.txt"
echo "# Arianna Method Backup Manifest" > "$MANIFEST"
echo "# Timestamp: $(date -Iseconds)" >> "$MANIFEST"
echo "# Backup ID: $TIMESTAMP" >> "$MANIFEST"
echo "" >> "$MANIFEST"

cd "$BACKUP_DIR"
find . -type f ! -name "MANIFEST.txt" -exec sha256sum {} \; | sort >> "$MANIFEST"

HASH_COUNT=$(grep -c -v "^#" "$MANIFEST" | grep -c -v "^$")
echo "  ✅ Generated $HASH_COUNT file hashes" | tee -a "$LOG_FILE"

# Prune old backups (keep last 20)
echo "" | tee -a "$LOG_FILE"
echo "🧹 Pruning old backups..." | tee -a "$LOG_FILE"

BACKUP_COUNT_TOTAL=$(ls -1 "$BACKUP_ROOT" 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT_TOTAL" -gt 20 ]; then
    PRUNE_COUNT=$((BACKUP_COUNT_TOTAL - 20))
    ls -1t "$BACKUP_ROOT" | tail -n +21 | while read OLD_BACKUP; do
        rm -rf "$BACKUP_ROOT/$OLD_BACKUP"
        echo "  Removed: $OLD_BACKUP" >> "$LOG_FILE"
    done
    echo "  ✅ Pruned $PRUNE_COUNT old backups" | tee -a "$LOG_FILE"
else
    echo "  ℹ️  No pruning needed ($BACKUP_COUNT_TOTAL/20 backups)" | tee -a "$LOG_FILE"
fi

# Calculate total backup storage usage
TOTAL_SIZE=$(du -sh "$BACKUP_ROOT" 2>/dev/null | awk '{print $1}')

echo "" | tee -a "$LOG_FILE"
echo "💾 Total backup storage: $TOTAL_SIZE" | tee -a "$LOG_FILE"
echo "🔥 Backup complete: $(date -Iseconds)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Send notification
if [ "$FAILED_COUNT" -eq 0 ]; then
    termux-notification -t "📦 Claude Defender" -c "Backup complete: $BACKUP_COUNT items ($BACKUP_SIZE)"
else
    termux-notification -t "⚠️ Claude Defender" -c "Backup complete with $FAILED_COUNT failures" --priority high
fi

# Return backup directory path for scripting
echo "$BACKUP_DIR"
