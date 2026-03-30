# Pandoll AI Claude Skills

## 리포 목적
Pandoll-AI가 제작한 Claude Code 스킬들의 마켓플레이스 레지스트리 + 소스 코드 저장소.
`/plugin marketplace add Pandoll-AI/claude-skills`로 설치 가능.

## 구조

- `.claude-plugin/marketplace.json` — 마켓플레이스 레지스트리 (스킬 목록, 버전, source 정보)
- 각 스킬 폴더 (`coding-score/`, `security-scan/` 등) — 스킬 소스 코드 (SKILL.md + 관련 파일)
- `nanobanana-skill`만 source가 `url`로 외부 리포(`Pandoll-AI/claude-nanobanana-skill`)를 가리킴. 나머지는 `local` source로 이 리포 안에 소스가 있음.

## 등록된 스킬

| 스킬 | 버전 | source | 설명 |
|------|------|--------|------|
| nanobanana-skill | 0.2.4 | url (외부 리포) | Gemini 웹 이미지 생성 + 워터마크 제거 |
| codex-llm-skill | 1.0.0 | local | codex 기반 LLM 커넥터 설치 |
| coding-score | 1.0.0 | local | AI 코드 품질 6영역 평가 |
| security-scan | 1.0.0 | local | 침투 테스트 / 보안 취약점 평가 |
| ui-walkthrough | 1.0.0 | local | UI/UX 감사 + 스크린샷 리포트 |
| wiki-generator | 1.0.0 | local | 시각적 인터랙티브 문서 생성 |
| ontologic-system-design | 1.0.0 | local | 온톨로지 기반 아키텍처 분석 |
| supabase-to-aws | 1.0.0 | local | Supabase ↔ AWS 마이그레이션 자동화 |
| CC-Agents-Native-KMP-App | 1.0.0 | local | **[ARCHIVED]** KMP (Android+iOS) 빌드 에이전트. 오래되어 작동 미보장 |

## 관련 리포 (등록 대상 아님)

- **`~/Projects/codex-nanobanana-skill`** — nanobanana의 codex CLI 변형판. `skills.sh` 등록용 실험 리포이며, 이 마켓플레이스에는 등록하지 않음.
- **`~/Projects/deepcode-claude-skills`** — DeepCode Paper2Code 워크플로우. 내가 만든 스킬이 아니므로 등록하지 않음 (로컬 설치용으로만 사용).
- **`Pandoll-AI/my-claude-plugins`** — (삭제됨) supabase-to-aws 스킬이 있던 리포. 이 리포(`claude-skills`)로 통합 완료 후 삭제함.

## 작업 방식

- 스킬 신규 등록: 스킬 폴더를 이 리포 루트에 추가 → `marketplace.json`의 `plugins` 배열에 항목 추가 → 커밋·푸시
- 스킬 업데이트: 소스 코드 수정 → `marketplace.json` 버전 번호 올리기 → 커밋·푸시
- nanobanana-skill은 별도 리포(`claude-nanobanana-skill`)에서 수정 후 여기서는 버전만 갱신
- 버전은 `marketplace.json`과 각 스킬의 SKILL.md(있는 경우) 양쪽 동기화
- 스킬 폴더에 `.git`이 남아있으면 embedded repo 경고 발생하므로 복사 시 반드시 제거

## 주의사항

- 스킬 폴더 복사 시 `.git` 디렉토리 제거 필수 (embedded git repo 방지)
- `README.md`는 마켓플레이스 설치 안내용 — 스킬 추가 시 테이블도 업데이트할 것
