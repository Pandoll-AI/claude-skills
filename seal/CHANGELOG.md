# CHANGELOG

## [2026-04-25] Phase: hotfix — block decision causes Stop loop

### Fixed
- **무한 루프 버그 수정**: 직전 phase에서 도입한 `decision: "block"`이 Stop 훅에서 무한 루프를 유발하던 문제 해결. Claude Code의 `block`은 "더 할 일이 있어, 멈추지 마"라는 신호인데, systemMessage가 사용자에게 `/wrap` 입력을 요구하는 내용이라 Claude는 할 일이 없어 다시 종료 시도 → 같은 조건에 또 block → 영원히 반복되던 문제. (`seal/hooks/scripts/check-phase-flag.sh`)

### Changed
- Stop 훅이 코드 변경 감지 시 더 이상 `decision: "block"`을 반환하지 않음. 대신 `systemMessage`만 출력해 비-블로킹 알림으로 동작 (`seal/hooks/scripts/check-phase-flag.sh`)
- `.seal-warned` 플래그 도입 — 같은 세션에서 코드 변경이 계속 남아있어도 알림이 1회만 발생하도록 spam 방지 (`seal/hooks/scripts/check-phase-flag.sh`)
- SessionStart cleanup이 `.seal-done`과 `.seal-warned` 둘 다 정리하도록 확장 (`seal/scripts/cleanup-flag.sh`)

### Review
- 6 시나리오 회귀 검증 통과: 변경 없음 / `.md`만 변경 / 코드 변경 시 systemMessage(no block) + warn 플래그 생성 / 동일 세션 재진입 시 무알림 / `.seal-done` 플래그 시 무알림 + 정리 / SessionStart cleanup이 두 플래그 모두 제거.
- cache 디렉터리 핫패치 완료 — 진행 중인 다른 세션이 다음 Stop에서 새 스크립트로 즉시 루프 종료.

## [2026-04-25] Phase: replace LLM Stop hook with bash pre-filter

### Added
- 확장자 기반 코드 변경 감지 pre-filter — `.md/.json/.yaml/.yml/.toml/.lock/.gitignore/.env*/.txt/LICENSE/CHANGELOG*/README*` 제외 (`seal/hooks/scripts/check-phase-flag.sh`)
- 코드 변경 감지 시 bash 단계에서 직접 `block` 결정을 내리는 로직 (`seal/hooks/scripts/check-phase-flag.sh`)

### Changed
- Stop 훅 결정 로직을 bash 단일 스크립트로 통합 — LLM 평가 없이 deterministic 판단 (`seal/hooks/hooks.json`)
- block 시 systemMessage를 6단계 안내문 → `[seal] 코드 변경이 감지됐습니다. /wrap 으로 phase를 마무리하세요.` 한 줄로 축약 (`seal/hooks/scripts/check-phase-flag.sh`)
- approve 경로의 `reason` 필드 제거 — 사용자 화면에 불필요한 내부 상태 노출 차단 (`seal/hooks/scripts/check-phase-flag.sh`)
- `phase-docs` SKILL.md description을 4줄 → 1줄로 압축, system prompt 점유 축소 (`seal/skills/phase-docs/SKILL.md`)
- 플러그인 description을 작업 내용에 맞게 갱신 (`seal/hooks/hooks.json`)

### Removed
- Stop 훅의 `type: prompt` LLM 평가 항목 — approve/block 무관하게 매 Stop마다 약 30줄 평가 프롬프트 + reasoning이 화면에 덤프되던 노이즈 제거 (`seal/hooks/hooks.json`)
- SessionStart의 gstack 미설치 경고 — 미설치 환경에서 매 세션 반복되던 systemMessage 제거 (`seal/scripts/cleanup-flag.sh`)

### Fixed
- Stop 훅이 의미 있는 코드 작업이 아닌 세션(질문/탐색/문서만 수정)에서도 LLM을 호출해 비용·지연·텍스트 덤프를 발생시키던 문제 — bash pre-filter로 LLM 호출 자체를 회피

### Review
- 사용자와 노이즈 원인 분석 → 개선 옵션(A 최소 침습 / B 구조 개선 / C 원칙 재고) 검토 → A+B 통합안 구현. Pre-filter 검증 5 시나리오 통과: 변경 없음 / `.md`만 변경 / 코드 변경 / `.seal-done` 플래그 존재 / non-git 디렉터리. SessionStart cleanup 훅도 별도 검증.
- 동기화 검증 완료: `~/Projects/claude-skills/seal/`, `~/.claude/plugins/marketplaces/.../seal/`, `~/.claude/plugins/cache/.../seal/0.1.0/` 3곳 diff 0.
