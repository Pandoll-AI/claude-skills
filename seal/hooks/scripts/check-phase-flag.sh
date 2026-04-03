#!/bin/bash
set -euo pipefail

FLAG_FILE="$CLAUDE_PROJECT_DIR/.seal-done"

if [ -f "$FLAG_FILE" ]; then
  # Phase documentation already completed this session — let Claude stop
  echo '{"decision":"approve","reason":"Phase documentation already completed"}'
  rm -f "$FLAG_FILE"
  exit 0
fi

# No flag — defer to the prompt hook for judgment
exit 0
