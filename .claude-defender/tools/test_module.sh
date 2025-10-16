#!/usr/bin/env bash
# Claude Defender - Module Testing Tool
# Tests Python modules for syntax and basic functionality

set -euo pipefail

MODULE_PATH="${1:-}"
LOG_FILE="$HOME/.claude-defender/logs/test.log"

if [ -z "$MODULE_PATH" ]; then
    echo "Usage: $0 <module_path>"
    echo "Example: $0 ~/ariannamethod/arianna.py"
    exit 1
fi

if [ ! -f "$MODULE_PATH" ]; then
    echo "❌ File not found: $MODULE_PATH"
    exit 1
fi

MODULE_NAME=$(basename "$MODULE_PATH")
TIMESTAMP=$(date --iso-8601=seconds)

echo "[Claude Defender] Testing module: $MODULE_NAME"

# Syntax check
echo "  → Running syntax check..."
if python -m py_compile "$MODULE_PATH" 2>&1; then
    echo "  ✓ Syntax check passed"
    echo "$TIMESTAMP: [TEST] $MODULE_NAME - Syntax OK" >> "$LOG_FILE"
else
    echo "  ❌ Syntax check failed"
    echo "$TIMESTAMP: [TEST] $MODULE_NAME - Syntax FAIL" >> "$LOG_FILE"
    exit 1
fi

# Import test
echo "  → Testing import..."
MODULE_DIR=$(dirname "$MODULE_PATH")
MODULE_BASENAME=$(basename "$MODULE_PATH" .py)

cd "$MODULE_DIR"
if python -c "import sys; sys.path.insert(0, '.'); import $MODULE_BASENAME" 2>&1; then
    echo "  ✓ Import test passed"
    echo "$TIMESTAMP: [TEST] $MODULE_NAME - Import OK" >> "$LOG_FILE"
else
    echo "  ⚠ Import test failed (may be normal for scripts)"
    echo "$TIMESTAMP: [TEST] $MODULE_NAME - Import WARNING" >> "$LOG_FILE"
fi

echo "[Claude Defender] Module test complete: $MODULE_NAME"
echo "$TIMESTAMP: [TEST] $MODULE_NAME - COMPLETED" >> "$LOG_FILE"
