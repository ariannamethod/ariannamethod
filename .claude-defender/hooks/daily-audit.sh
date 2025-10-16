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
        echo "$TIMESTAMP: [AUDIT] DATABASE INTEGRITY FAIL" >> "$LOG_FILE"
    fi
else
    echo "  ❌ Database not found"
    echo "$TIMESTAMP: [AUDIT] Database missing" >> "$LOG_FILE"
fi

# Check 3: Git status
echo "[3/6] Checking git status..."
cd "$REPO_DIR"
UNCOMMITTED=$(git status --porcelain | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
    echo "  ⚠ Uncommitted changes: $UNCOMMITTED files"
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
    echo "$TIMESTAMP: [AUDIT] Boot script missing" >> "$LOG_FILE"
fi

# Check 5: API keys
echo "[5/6] Checking API keys..."
API_KEYS_OK=true
[ -z "${OPENAI_API_KEY:-}" ] && echo "  ⚠ OPENAI_API_KEY not set" && API_KEYS_OK=false
[ -z "${ANTHROPIC_API_KEY:-}" ] && echo "  ⚠ ANTHROPIC_API_KEY not set" && API_KEYS_OK=false
if $API_KEYS_OK; then
    echo "  ✓ API keys configured"
fi

# Check 6: Disk space
echo "[6/6] Checking disk space..."
DISK_USAGE=$(df -h "$HOME" | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "  ⚠ Disk usage: ${DISK_USAGE}% (high)"
    echo "$TIMESTAMP: [AUDIT] High disk usage: ${DISK_USAGE}%" >> "$LOG_FILE"
else
    echo "  ✓ Disk usage: ${DISK_USAGE}%"
fi

# Summary
echo "════════════════════════════════════════════════════════════"
if [ "$SYNTAX_ERRORS" -eq 0 ]; then
    echo "✓ Audit complete - System healthy"
    echo "$TIMESTAMP: [AUDIT] System healthy" >> "$LOG_FILE"
else
    echo "❌ Audit complete - $SYNTAX_ERRORS errors found"
    echo "$TIMESTAMP: [AUDIT] $SYNTAX_ERRORS errors detected" >> "$LOG_FILE"
fi
echo "════════════════════════════════════════════════════════════"
