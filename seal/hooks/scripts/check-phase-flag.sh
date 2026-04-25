#!/bin/bash
set -euo pipefail

FLAG_FILE="$CLAUDE_PROJECT_DIR/.seal-done"

if [ -f "$FLAG_FILE" ]; then
  echo '{"decision":"approve"}'
  rm -f "$FLAG_FILE"
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

changed=$(git status --porcelain 2>/dev/null | awk '{print $NF}')
[ -z "$changed" ] && exit 0

has_code=false
while IFS= read -r file; do
  [ -z "$file" ] && continue
  case "$file" in
    *.md|*.json|*.yaml|*.yml|*.toml|*.lock|.gitignore|.env*|*.txt|LICENSE|CHANGELOG*|README*)
      continue ;;
    *)
      has_code=true
      break ;;
  esac
done <<< "$changed"

if [ "$has_code" = true ]; then
  echo '{"decision":"block","reason":"code changes detected","systemMessage":"[seal] 코드 변경이 감지됐습니다. /wrap 으로 phase를 마무리하세요."}'
fi

exit 0
