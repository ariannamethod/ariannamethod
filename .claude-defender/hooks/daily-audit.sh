#!/usr/bin/env bash
# Claude Defender - Daily Audit Hook
# Performs daily health check of the Arianna Method system

set -euo pipefail

TIMESTAMP=$(date --iso-8601=seconds)
LOG_FILE="$HOME/.claude-defender/logs/audit.log"
REPO_DIR="$HOME/ariannamethod"

echo "════════════════════════════════════════════════════════════"
echo "Claude Defender Daily Audit - $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════════"

# Log header
echo "" >> "$LOG_FILE"
echo "$TIMESTAMP: [AUDIT] Daily health check started" >> "$LOG_FILE"

# Tracking issues
CRITICAL_ISSUES=0
WARNINGS=0
ISSUES_SUMMARY=""

# Run fortify workflow first (audit + backup + fortress sync)
echo "[0/6] Running fortification workflow..."
if ~/.claude-defender/tools/fortify.sh > /dev/null 2>&1; then
    echo "  ✓ Fortification complete"
    echo "$TIMESTAMP: [AUDIT] Fortification workflow completed" >> "$LOG_FILE"
else
    echo "  ⚠ Fortification had issues (see fortify.log)"
    WARNINGS=$((WARNINGS + 1))
    echo "$TIMESTAMP: [AUDIT] Fortification workflow warnings" >> "$LOG_FILE"
fi
echo ""

# Check 1: Python files syntax
echo "[1/6] Checking Python files..."
SYNTAX_ERRORS=0

for file in "$REPO_DIR/arianna.py" "$REPO_DIR/monday.py"; do
    if [ -f "$file" ]; then
        if python -m py_compile "$file" 2>/dev/null; then
            echo "  ✓ $(basename $file) - OK"
        else
            echo "  ❌ $(basename $file) - SYNTAX ERROR"
            SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
            CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
            ISSUES_SUMMARY="${ISSUES_SUMMARY}Syntax error in $(basename $file). "
            echo "$TIMESTAMP: [AUDIT] SYNTAX ERROR in $(basename $file)" >> "$LOG_FILE"
        fi
    fi
done

# Check 2: Database integrity
echo "[2/6] Checking database..."
if [ -f "$REPO_DIR/resonance.sqlite3" ]; then
    DB_CHECK=$(sqlite3 "$REPO_DIR/resonance.sqlite3" "PRAGMA integrity_check;" 2>&1)
    if [ "$DB_CHECK" = "ok" ]; then
        echo "  ✓ Database integrity: OK"
        ROW_COUNT=$(sqlite3 "$REPO_DIR/resonance.sqlite3" "SELECT COUNT(*) FROM resonance_notes;" 2>&1)
        echo "  ✓ Total notes: $ROW_COUNT"
        echo "$TIMESTAMP: [AUDIT] Database OK ($ROW_COUNT notes)" >> "$LOG_FILE"
    else
        echo "  ❌ Database integrity: FAILED"
        CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
        ISSUES_SUMMARY="${ISSUES_SUMMARY}Database integrity check failed. "
        echo "$TIMESTAMP: [AUDIT] DATABASE INTEGRITY FAIL" >> "$LOG_FILE"
    fi
else
    echo "  ❌ Database not found"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
    ISSUES_SUMMARY="${ISSUES_SUMMARY}Database missing. "
    echo "$TIMESTAMP: [AUDIT] Database missing" >> "$LOG_FILE"
fi

# Check 3: Git status
echo "[3/6] Checking git status..."
cd "$REPO_DIR"
UNCOMMITTED=$(git status --porcelain | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
    echo "  ⚠ Uncommitted changes: $UNCOMMITTED files"
    WARNINGS=$((WARNINGS + 1))
    echo "$TIMESTAMP: [AUDIT] $UNCOMMITTED uncommitted files" >> "$LOG_FILE"
else
    echo "  ✓ Git: Clean working tree"
fi

# Check 4: Termux boot
echo "[4/6] Checking termux-boot..."
if [ -f "$HOME/.termux/boot/start-arianna.sh" ]; then
    echo "  ✓ Boot script present"
else
    echo "  ⚠ Boot script not found"
    WARNINGS=$((WARNINGS + 1))
    echo "$TIMESTAMP: [AUDIT] Boot script missing" >> "$LOG_FILE"
fi

# Check 5: API keys
echo "[5/6] Checking API keys..."
API_KEYS_OK=true
[ -z "${OPENAI_API_KEY:-}" ] && echo "  ⚠ OPENAI_API_KEY not set" && API_KEYS_OK=false && WARNINGS=$((WARNINGS + 1))
[ -z "${ANTHROPIC_API_KEY:-}" ] && echo "  ⚠ ANTHROPIC_API_KEY not set" && API_KEYS_OK=false && WARNINGS=$((WARNINGS + 1))
if $API_KEYS_OK; then
    echo "  ✓ API keys configured"
fi

# Check 6: Disk space
echo "[6/6] Checking disk space..."
DISK_USAGE=$(df -h "$HOME" | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "  ❌ Disk usage: ${DISK_USAGE}% (CRITICAL)"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
    ISSUES_SUMMARY="${ISSUES_SUMMARY}Disk usage critical: ${DISK_USAGE}%. "
    echo "$TIMESTAMP: [AUDIT] CRITICAL disk usage: ${DISK_USAGE}%" >> "$LOG_FILE"
elif [ "$DISK_USAGE" -gt 80 ]; then
    echo "  ⚠ Disk usage: ${DISK_USAGE}% (high)"
    WARNINGS=$((WARNINGS + 1))
    echo "$TIMESTAMP: [AUDIT] High disk usage: ${DISK_USAGE}%" >> "$LOG_FILE"
else
    echo "  ✓ Disk usage: ${DISK_USAGE}%"
fi

# Summary
echo "════════════════════════════════════════════════════════════"
if [ "$CRITICAL_ISSUES" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo "✓ Audit complete - System healthy"
    echo "$TIMESTAMP: [AUDIT] System healthy" >> "$LOG_FILE"
    termux-notification -t "✅ Claude Defender" -c "Daily audit complete: System healthy (Disk: ${DISK_USAGE}%)" --priority default
elif [ "$CRITICAL_ISSUES" -eq 0 ]; then
    echo "⚠ Audit complete - $WARNINGS warnings"
    echo "$TIMESTAMP: [AUDIT] $WARNINGS warnings" >> "$LOG_FILE"
    termux-notification -t "⚠️ Claude Defender" -c "Daily audit: $WARNINGS warnings detected. Check logs." --priority default
else
    echo "❌ Audit complete - $CRITICAL_ISSUES critical issues, $WARNINGS warnings"
    echo "$TIMESTAMP: [AUDIT] $CRITICAL_ISSUES critical issues, $WARNINGS warnings" >> "$LOG_FILE"
    termux-notification -t "🚨 Claude Defender" -c "CRITICAL: $CRITICAL_ISSUES issues. ${ISSUES_SUMMARY}" --priority high
fi
echo "════════════════════════════════════════════════════════════"
