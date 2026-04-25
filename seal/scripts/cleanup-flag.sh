#!/bin/bash
set -euo pipefail

rm -f "$CLAUDE_PROJECT_DIR/.seal-done" 2>/dev/null || true
exit 0
