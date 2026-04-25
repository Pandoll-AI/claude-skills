#!/bin/bash
set -euo pipefail

rm -f "$CLAUDE_PROJECT_DIR/.seal-done" "$CLAUDE_PROJECT_DIR/.seal-warned" 2>/dev/null || true
exit 0
