#!/data/data/com.termux/files/usr/bin/bash
# CLAUDE DEFENDER - AUDIT SCHEDULER
# Sets up automated audits using cronie

echo "🔥 CLAUDE DEFENDER AUDIT SCHEDULER"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Check if cronie is available
if ! command -v crontab &> /dev/null; then
    echo "📦 Installing cronie..."
    pkg install cronie -y

    if ! command -v crontab &> /dev/null; then
        echo "❌ Installation failed. Install manually:"
        echo "   pkg install cronie"
        exit 1
    fi
fi

echo "✅ cronie available"
echo ""

# Create temporary crontab file
TEMP_CRON=$(mktemp)

# Get existing crontab (if any) and filter out our jobs
crontab -l 2>/dev/null | grep -v "claude-defender" > "$TEMP_CRON" || true

echo "🧹 Clearing existing Claude Defender jobs..."
echo "  ✓ Cleared"
echo ""

# Add new jobs
DAILY_AUDIT_SCRIPT=~/.claude-defender/hooks/daily-audit.sh
FORTIFY_SCRIPT=~/.claude-defender/tools/fortify.sh

echo "📅 Scheduling jobs..."

# Daily audit at 3 AM
echo "# Claude Defender: Daily audit" >> "$TEMP_CRON"
echo "0 3 * * * $DAILY_AUDIT_SCRIPT >> ~/.claude-defender/logs/cron.log 2>&1" >> "$TEMP_CRON"

# Fortification every 6 hours (at 00:00, 06:00, 12:00, 18:00)
echo "# Claude Defender: Fortification workflow" >> "$TEMP_CRON"
echo "0 */6 * * * $FORTIFY_SCRIPT >> ~/.claude-defender/logs/cron.log 2>&1" >> "$TEMP_CRON"

# Install new crontab
if crontab "$TEMP_CRON"; then
    echo "  ✓ Daily audit scheduled (3 AM daily)"
    echo "  ✓ Fortification scheduled (every 6 hours)"
else
    echo "  ❌ Failed to install crontab"
    rm "$TEMP_CRON"
    exit 1
fi

rm "$TEMP_CRON"

# Start cron daemon if not running
if ! pgrep -x crond > /dev/null; then
    echo ""
    echo "🚀 Starting cron daemon..."
    crond
    echo "  ✓ Cron daemon started"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📊 SCHEDULED JOBS SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "🔄 Daily Audit:"
echo "   Schedule: 3:00 AM daily"
echo "   Script: $DAILY_AUDIT_SCRIPT"
echo "   Actions: Fortify workflow + health checks"
echo ""
echo "🔥 Fortification:"
echo "   Schedule: Every 6 hours (00:00, 06:00, 12:00, 18:00)"
echo "   Script: $FORTIFY_SCRIPT"
echo "   Actions: Code audit + backup + fortress sync"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "✅ SCHEDULER SETUP COMPLETE"
echo ""
echo "To view scheduled jobs:"
echo "  crontab -l"
echo ""
echo "To manually run:"
echo "  $DAILY_AUDIT_SCRIPT"
echo "  $FORTIFY_SCRIPT"
echo ""

# Log scheduling
LOG_FILE=~/.claude-defender-fortress/logs/scheduler.log
mkdir -p "$(dirname "$LOG_FILE")"
echo "$(date -Iseconds): Audit scheduler configured successfully" >> "$LOG_FILE"

# Send notification
termux-notification -t "📅 Claude Defender" -c "Audit scheduler configured: Daily audits + 6h fortification"

echo "🔥 Automated defense systems online. We never sleep. 🔥"
echo ""
