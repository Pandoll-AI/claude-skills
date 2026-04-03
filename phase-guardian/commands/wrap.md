---
name: wrap
description: |
  Phase 마무리 워크플로우를 수동으로 실행합니다. 리뷰 + 문서화 + 커밋을 강제합니다.
  자동 트리거가 놓친 경우나, 작은 수정이지만 문서화가 필요할 때 사용하세요.
---

# /wrap — Phase 마무리

다음 워크플로우를 순서대로 실행하세요.

## Step 1: gstack 확인

```bash
[ -d "$HOME/.claude/skills/gstack" ] && echo "GSTACK_OK" || echo "GSTACK_MISSING"
```

- `GSTACK_OK`: Step 2로 진행
- `GSTACK_MISSING`: 사용자에게 안내:
  "gstack이 설치되어 있지 않습니다. /review를 사용하려면 gstack을 설치해주세요: https://github.com/garryslist/gstack
  gstack 없이 문서화만 진행할까요?"
  - Yes → Step 3으로 건너뜀 (리뷰 스킵)
  - No → 중단

## Step 2: /review 실행

Skill 도구를 사용하여 `review` 스킬을 호출합니다.

```
Skill(skill: "review")
```

리뷰가 완료되면 결과를 기억해두세요. CHANGELOG.md의 Review 섹션에 요약을 포함합니다.

## Step 3: 문서 업데이트

phase-docs 스킬의 규칙에 따라 3개 문서를 업데이트합니다.

1. `git diff HEAD~..HEAD`로 최근 변경사항 파악 (커밋이 없으면 `git diff`로 스테이징 포함)
2. **CHANGELOG.md** 업데이트 — 최상단에 새 phase 항목 추가
3. **KNOWLEDGE.md** 업데이트 — 엔티티/관계/액션 테이블 반영
4. **STRUCTURE.md** 업데이트 — 워크플로우/키파일/DB/API 반영
5. 변경사항이 없는 문서는 건드리지 않음

## Step 4: 커밋 & 푸시

```bash
git add CHANGELOG.md KNOWLEDGE.md STRUCTURE.md
git add -A  # 혹시 빠진 소스 파일이 있으면 포함
git status
```

사용자에게 커밋할 파일 목록을 보여주고 확인을 받은 뒤:

```bash
git commit -m "docs: phase wrap — {이번 phase 한 줄 요약}"
git push
```

## Step 5: 플래그 생성

```bash
touch "$CLAUDE_PROJECT_DIR/.phase-guardian-done"
```

이 플래그는 Stop 훅이 이중으로 문서화를 강제하지 않도록 방지합니다.

## 완료

"Phase wrap 완료. CHANGELOG, KNOWLEDGE, STRUCTURE 업데이트 및 커밋/푸시 완료." 출력.
