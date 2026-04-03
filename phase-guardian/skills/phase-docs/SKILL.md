---
name: phase-docs
version: 0.1.0
description: |
  Phase documentation writer. Generates and updates CHANGELOG.md, KNOWLEDGE.md,
  and STRUCTURE.md after meaningful code work. Auto-activated by phase-guardian
  hooks or manually via /wrap command. Maintains ontological knowledge graph
  (entities, relations, actions) and project structure documentation.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
---

# Phase Documentation Guide

이 스킬은 phase-guardian 플러그인의 문서화 엔진입니다. 코드 작업 후 3개의 문서를 생성/업데이트합니다.

## 문서 위치 규칙

- 모노레포가 아닌 경우: 프로젝트 루트에 생성
- 모노레포인 경우: 해당 패키지/모듈 폴더에 생성, 루트에는 요약본

## 1. CHANGELOG.md

Keep a Changelog (https://keepachangelog.com) 포맷 기반.

```markdown
# CHANGELOG

## [YYYY-MM-DD] Phase: {phase 제목}
### Added
- 새로 추가된 기능, 파일, API 등

### Changed
- 기존 기능의 변경사항

### Fixed
- 버그 수정

### Removed
- 삭제된 기능, 파일

### Review
- /review 실행 결과 요약 (이슈 수, 주요 지적사항)
```

**규칙:**
- 최신 항목이 파일 상단
- 기존 내용은 절대 삭제하지 않음, 상단에 추가만
- phase 제목은 작업 내용을 한 줄로 요약
- 각 항목에는 관련 파일 경로를 괄호로 포함: `- JWT 인증 추가 (src/services/auth.ts)`

## 2. KNOWLEDGE.md

온톨로지 기반 지식 그래프. 코드베이스의 엔티티, 관계, 액션을 추적합니다.

```markdown
# KNOWLEDGE
> 마지막 업데이트: YYYY-MM-DD

## Entities
| Entity | Type | Location | Description |
|--------|------|----------|-------------|

Type 분류: Model, Service, Controller, Middleware, Utility, Config, Migration, Test, CLI, API

## Relations
| Subject | Relation | Object | Context |
|---------|----------|--------|---------|

Relation 분류:
- depends_on: 코드 의존성
- triggers: 이벤트/호출 관계
- stored_in: 데이터 저장 위치
- validates: 검증 관계
- extends: 상속/확장
- implements: 인터페이스 구현
- reads_from / writes_to: 데이터 흐름
- authenticated_by: 인증 관계
- cached_in: 캐시 관계
- queued_in: 큐/비동기 처리

## Actions (변경 이력)
| Date | Action | Actor | Target | Detail |
|------|--------|-------|--------|--------|

Action 분류: created, modified, deleted, refactored, fixed, migrated
Actor: 작업 수행자 (Claude, 사용자 이름 등)
```

**규칙:**
- 기존 Entities/Relations 행은 해당 엔티티가 삭제된 경우에만 제거
- 변경된 엔티티는 행을 업데이트
- Actions는 최신 5개만 유지 (오래된 것은 CHANGELOG로 이관)
- Location은 실제 파일 경로 (존재 확인 필수)

## 3. STRUCTURE.md

프로젝트의 실행 구조와 데이터 흐름을 문서화합니다.

```markdown
# STRUCTURE
> 마지막 업데이트: YYYY-MM-DD

## Workflow
주요 실행 흐름을 번호 리스트로 기술.
1. 사용자 요청 → ...
2. ...

## Key Files
| File | Role | Depends On |
|------|------|------------|

Role: 엔트리포인트, 라우터, 컨트롤러, 서비스, 모델, 미들웨어, 설정, 마이그레이션 등

## Database
| Table/Collection | Purpose | Key Relations |
|-----------------|---------|--------------|

Key Relations: FK 관계, 1:N, N:M 등

## API Endpoints
| Method | Path | Handler | Auth | Description |
|--------|------|---------|------|-------------|

## CLI / Scripts
| Command | Purpose |
|---------|---------|

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
```

**규칙:**
- Workflow 섹션은 전체를 다시 작성 (누적이 아님)
- Key Files는 diff에서 변경된 파일 중심으로 업데이트
- Database 섹션은 마이그레이션이 있을 때만 업데이트
- 없는 섹션은 해당 내용이 있을 때만 추가 (빈 테이블 금지)

## 업데이트 절차

1. 기존 파일이 있으면 Read로 읽기
2. git diff로 이번 phase의 변경사항 파악
3. 각 문서를 규칙에 맞게 업데이트
4. 파일이 없으면 새로 생성
5. 변경사항이 없는 문서는 건드리지 않음
