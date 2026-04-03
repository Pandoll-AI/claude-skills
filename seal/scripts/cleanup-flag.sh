#!/bin/bash
set -euo pipefail

# Clean up stale flag from previous session
rm -f "$CLAUDE_PROJECT_DIR/.seal-done" 2>/dev/null || true

# Check if gstack is installed
if [ ! -d "$HOME/.claude/skills/gstack" ]; then
  echo '{"systemMessage":"[seal] gstack이 설치되어 있지 않습니다. /review 스킬을 사용하려면 gstack을 설치해주세요: https://github.com/garryslist/gstack"}'
fi

exit 0
