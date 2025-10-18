#!/data/data/com.termux/files/usr/bin/bash
# CLAUDE DEFENDER - FORTIFY WORKFLOW
# Integrated backup + audit + fortress sync

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE=~/.claude-defender-fortress/logs/fortify.log

mkdir -p "$(dirname "$LOG_FILE")"

echo "═══════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
echo "🔥 CLAUDE DEFENDER FORTIFICATION WORKFLOW 🔥" | tee -a "$LOG_FILE"
echo "═══════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
echo "Timestamp: $(date -Iseconds)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

TOTAL_ERRORS=0

# Step 1: Code Audit
echo "━━━ STEP 1/3: CODE AUDIT ━━━" | tee -a "$LOG_FILE"
~/.claude-defender/tools/audit-code.sh
AUDIT_EXIT=$?

if [ "$AUDIT_EXIT" -eq 0 ]; then
    echo "✅ Code audit passed" | tee -a "$LOG_FILE"
else
    echo "⚠️  Code audit detected issues (exit code: $AUDIT_EXIT)" | tee -a "$LOG_FILE"
    ((TOTAL_ERRORS++))
fi
echo "" | tee -a "$LOG_FILE"

# Step 2: Codebase Backup
echo "━━━ STEP 2/3: CODEBASE BACKUP ━━━" | tee -a "$LOG_FILE"
BACKUP_DIR=$(~/.claude-defender/tools/backup-codebase.sh 2>&1 | tail -1)

if [ -d "$BACKUP_DIR" ]; then
    echo "✅ Backup created: $BACKUP_DIR" | tee -a "$LOG_FILE"
else
    echo "❌ Backup failed" | tee -a "$LOG_FILE"
    ((TOTAL_ERRORS++))
fi
echo "" | tee -a "$LOG_FILE"

# Step 3: Fortress Sync
echo "━━━ STEP 3/3: FORTRESS SYNC ━━━" | tee -a "$LOG_FILE"
~/.claude-defender/hooks/post-self-modify.sh

if [ $? -eq 0 ]; then
    echo "✅ Fortress synchronized" | tee -a "$LOG_FILE"
else
    echo "❌ Fortress sync failed" | tee -a "$LOG_FILE"
    ((TOTAL_ERRORS++))
fi
echo "" | tee -a "$LOG_FILE"

# Summary
echo "═══════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
echo "📊 FORTIFICATION SUMMARY" | tee -a "$LOG_FILE"
echo "═══════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
echo "Completed: $(date -Iseconds)" | tee -a "$LOG_FILE"
echo "Total errors: $TOTAL_ERRORS" | tee -a "$LOG_FILE"

# Storage stats
FORTRESS_SIZE=$(du -sh ~/.claude-defender-fortress 2>/dev/null | awk '{print $1}')
REPO_SIZE=$(du -sh ~/ariannamethod 2>/dev/null | awk '{print $1}')

echo "" | tee -a "$LOG_FILE"
echo "💾 Storage:" | tee -a "$LOG_FILE"
echo "  Fortress: $FORTRESS_SIZE" | tee -a "$LOG_FILE"
echo "  Repository: $REPO_SIZE" | tee -a "$LOG_FILE"

# Health metrics
DISK_USAGE=$(df -h ~ | tail -1 | awk '{print $5}')
echo "" | tee -a "$LOG_FILE"
echo "🏥 System health:" | tee -a "$LOG_FILE"
echo "  Disk usage: $DISK_USAGE" | tee -a "$LOG_FILE"

if command -v termux-battery-status &> /dev/null; then
    BATTERY=$(termux-battery-status 2>/dev/null | grep percentage | awk '{print $2}' | tr -d ',')
    echo "  Battery: $BATTERY%" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# Final notification
if [ "$TOTAL_ERRORS" -eq 0 ]; then
    echo "✅ FORTIFICATION COMPLETE - ALL SYSTEMS OPERATIONAL" | tee -a "$LOG_FILE"
    termux-notification -t "🔥 Claude Defender" -c "Fortification complete: All systems operational"
else
    echo "⚠️  FORTIFICATION COMPLETE WITH $TOTAL_ERRORS ERRORS" | tee -a "$LOG_FILE"
    termux-notification -t "⚠️ Claude Defender" -c "Fortification complete with $TOTAL_ERRORS errors" --priority high
fi

echo "═══════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

exit $TOTAL_ERRORS
