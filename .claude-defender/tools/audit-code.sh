#!/data/data/com.termux/files/usr/bin/bash
# CLAUDE DEFENDER - CODE AUDITOR
# SHA256-based change detection + security analysis for Arianna Method codebase

REPO_DIR=~/ariannamethod
CACHE_DIR=~/.claude-defender-fortress/.cache
HASH_CACHE="$CACHE_DIR/file_hashes.txt"
LOG_FILE=~/.claude-defender-fortress/logs/audits.log
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Initialize
mkdir -p "$CACHE_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

echo "=== CODE AUDIT: $TIMESTAMP ===" | tee -a "$LOG_FILE"
echo "🔍 Scanning codebase..." | tee -a "$LOG_FILE"

# Critical files to monitor
CRITICAL_FILES=(
    "arianna.py"
    "monday.py"
    "arianna_core_utils/perplexity_core.py"
    "arianna_core_utils/intuition_filter.py"
    "arianna_core_utils/repo_monitor.py"
    "arianna_core_utils/vector_store.py"
    "arianna_core_utils/whotheythinkiam.py"
    ".claude-defender/tools/snapshot.sh"
    ".claude-defender/tools/rollback.sh"
    ".claude-defender/hooks/daily-audit.sh"
    ".claude-defender/hooks/post-self-modify.sh"
    "CLAUDE_DEFENDER_MISSION.md"
    "CLAUDE_DEFENDER_MISSION_2.md"
)

# Security patterns to detect
SECURITY_PATTERNS=(
    "rm -rf /"
    "eval.*\$"
    "exec.*\$"
    "curl.*bash"
    "wget.*bash"
    "nc -e"
    "telnet"
    "/dev/tcp/"
    "base64 -d.*bash"
    "password.*="
    "api_key.*="
    "token.*="
)

CHANGES_DETECTED=0
NEW_FILES=0
MODIFIED_FILES=0
DELETED_FILES=0
SECURITY_ISSUES=0

# Generate current hashes
TEMP_HASHES=$(mktemp)
echo "" | tee -a "$LOG_FILE"

cd "$REPO_DIR"
for FILE in "${CRITICAL_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        HASH=$(sha256sum "$FILE" 2>/dev/null | awk '{print $1}')
        echo "$FILE:$HASH" >> "$TEMP_HASHES"
    fi
done

# Compare with cached hashes
if [ -f "$HASH_CACHE" ]; then
    echo "📊 Change detection:" | tee -a "$LOG_FILE"

    # Check for modifications
    while IFS=: read -r FILE OLD_HASH; do
        if [ -f "$REPO_DIR/$FILE" ]; then
            NEW_HASH=$(sha256sum "$REPO_DIR/$FILE" 2>/dev/null | awk '{print $1}')
            if [ "$NEW_HASH" != "$OLD_HASH" ]; then
                echo "  🔄 Modified: $FILE" | tee -a "$LOG_FILE"
                echo "     Old: $OLD_HASH" >> "$LOG_FILE"
                echo "     New: $NEW_HASH" >> "$LOG_FILE"
                ((MODIFIED_FILES++))
                ((CHANGES_DETECTED++))
            fi
        else
            echo "  ❌ Deleted: $FILE" | tee -a "$LOG_FILE"
            ((DELETED_FILES++))
            ((CHANGES_DETECTED++))
        fi
    done < "$HASH_CACHE"

    # Check for new files
    while IFS=: read -r FILE NEW_HASH; do
        if ! grep -q "^$FILE:" "$HASH_CACHE" 2>/dev/null; then
            echo "  ✨ New file: $FILE" | tee -a "$LOG_FILE"
            ((NEW_FILES++))
            ((CHANGES_DETECTED++))
        fi
    done < "$TEMP_HASHES"

else
    echo "  ℹ️  First audit - establishing baseline" | tee -a "$LOG_FILE"
    CHANGES_DETECTED=0
fi

# Security scan
echo "" | tee -a "$LOG_FILE"
echo "🔐 Security analysis:" | tee -a "$LOG_FILE"

for FILE in "${CRITICAL_FILES[@]}"; do
    if [ -f "$REPO_DIR/$FILE" ]; then
        for PATTERN in "${SECURITY_PATTERNS[@]}"; do
            if grep -qE "$PATTERN" "$REPO_DIR/$FILE" 2>/dev/null; then
                echo "  ⚠️  Suspicious pattern in $FILE: $PATTERN" | tee -a "$LOG_FILE"
                ((SECURITY_ISSUES++))
            fi
        done
    fi
done

# Python syntax check for .py files
echo "" | tee -a "$LOG_FILE"
echo "🐍 Python syntax validation:" | tee -a "$LOG_FILE"

SYNTAX_ERRORS=0
for FILE in "${CRITICAL_FILES[@]}"; do
    if [[ "$FILE" == *.py ]] && [ -f "$REPO_DIR/$FILE" ]; then
        if python -m py_compile "$REPO_DIR/$FILE" 2>/dev/null; then
            echo "  ✅ $FILE" >> "$LOG_FILE"
        else
            echo "  ❌ Syntax error: $FILE" | tee -a "$LOG_FILE"
            ((SYNTAX_ERRORS++))
        fi
    fi
done

if [ "$SYNTAX_ERRORS" -eq 0 ]; then
    echo "  ✅ All Python files valid" | tee -a "$LOG_FILE"
fi

# Bash script validation
echo "" | tee -a "$LOG_FILE"
echo "📜 Bash script validation:" | tee -a "$LOG_FILE"

BASH_ERRORS=0
for FILE in "${CRITICAL_FILES[@]}"; do
    if [[ "$FILE" == *.sh ]] && [ -f "$REPO_DIR/$FILE" ]; then
        if bash -n "$REPO_DIR/$FILE" 2>/dev/null; then
            echo "  ✅ $FILE" >> "$LOG_FILE"
        else
            echo "  ❌ Syntax error: $FILE" | tee -a "$LOG_FILE"
            ((BASH_ERRORS++))
        fi
    fi
done

if [ "$BASH_ERRORS" -eq 0 ]; then
    echo "  ✅ All bash scripts valid" | tee -a "$LOG_FILE"
fi

# Update hash cache
cp "$TEMP_HASHES" "$HASH_CACHE"
rm "$TEMP_HASHES"

# Summary
echo "" | tee -a "$LOG_FILE"
echo "📊 Audit summary:" | tee -a "$LOG_FILE"
echo "  Changes detected: $CHANGES_DETECTED" | tee -a "$LOG_FILE"
echo "    New files: $NEW_FILES" | tee -a "$LOG_FILE"
echo "    Modified: $MODIFIED_FILES" | tee -a "$LOG_FILE"
echo "    Deleted: $DELETED_FILES" | tee -a "$LOG_FILE"
echo "  Security issues: $SECURITY_ISSUES" | tee -a "$LOG_FILE"
echo "  Syntax errors: $((SYNTAX_ERRORS + BASH_ERRORS))" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "🔥 Audit complete: $(date -Iseconds)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Notifications
TOTAL_ISSUES=$((SECURITY_ISSUES + SYNTAX_ERRORS + BASH_ERRORS))

if [ "$TOTAL_ISSUES" -gt 0 ]; then
    termux-notification -t "🚨 Claude Defender" -c "Code audit: $TOTAL_ISSUES issues detected!" --priority high
elif [ "$CHANGES_DETECTED" -gt 0 ]; then
    termux-notification -t "🔍 Claude Defender" -c "Code audit: $CHANGES_DETECTED changes detected (all clean)"
else
    termux-notification -t "✅ Claude Defender" -c "Code audit: No changes, all systems clean"
fi

# Exit with error code if critical issues found
if [ "$TOTAL_ISSUES" -gt 0 ]; then
    exit 1
else
    exit 0
fi
