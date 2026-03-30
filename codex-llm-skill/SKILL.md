---
name: codex-llm
description: "Interactive installer that wires a codex-based LLM connector into any project. Replaces or wraps existing LLM API calls (OpenAI, Gemini, etc.) with a codex CLI backend that runs within your subscription quota — zero per-token cost. Supports multi-stage pipelines with per-stage permission tiers (T1 text-only / T2 data-write / T3 full-write), automatic model selection from the latest codex model catalog, and one-env-var switchback to external APIs for production. Trigger: 'llm을 codex를 사용해달라', 'codex로 LLM 연결해줘', 'codex 커넥터 설치', 'use codex for LLM', 'install codex connector'. | 프로젝트에 codex 기반 LLM 커넥터를 대화형으로 설치합니다. 기존 LLM API 호출을 codex CLI로 교체하여 구독 쿼타 내 무비용으로 운용하고, 멀티 스테이지 파이프라인(T1/T2/T3 권한 등급), 최신 모델 자동 선택, 환경변수 한 줄로 prod 외부 API 전환을 지원합니다."
argument-hint: "<project path or description>"
---

# Codex LLM Connector

**EN**: Interactive installer that wires a codex-based LLM connector into any project. During a one-time conversational setup, it analyzes your project, asks which LLM stages you need (e.g., summarize → generate → review), assigns permission tiers and models per stage, then generates config files and connector code. At runtime the installed code handles everything automatically — no further skill involvement. Switch between codex (dev, zero cost) and external APIs (prod) with a single env var.

**KR**: 프로젝트에 codex 기반 LLM 커넥터를 대화형으로 설치하는 스킬입니다. 1회 설치 대화에서 프로젝트를 분석하고, 필요한 LLM 스테이지(예: 요약 → 생성 → 검토)를 파악한 뒤, 스테이지별 권한 등급과 모델을 배정하고, 설정 파일과 커넥터 코드를 생성합니다. 이후 런타임에서는 설치된 코드가 자동으로 처리하며 스킬 개입은 없습니다. 환경변수 한 줄로 codex(dev, 무비용) ↔ 외부 API(prod) 전환.

---

## 1. 핵심 설계 원칙

### 1.1 권한 등급 체계 (Permission Tiers)

LLM 커넥터를 통한 작업은 대부분 **텍스트 입출력**이다. 파일 수정은 예외적 경우이며, 소스 코드 수정은 보안 위험이 높으므로 기본 차단한다.

| 등급 | 이름 | codex 모드 | 허용 범위 |
|------|------|-----------|-----------|
| **T1** | `text-only` | `codex exec` (기본) | stdout 텍스트 응답만. 프롬프트 제약으로 파일 쓰기 차단. **기본값** |
| **T2** | `data-write` | `codex exec --dangerously-bypass-approvals-and-sandbox` | 데이터/문서 파일 생성/수정 허용. 소스 코드 수정 불가 |
| **T3** | `full-write` | `codex exec --dangerously-bypass-approvals-and-sandbox` | 모든 파일 수정 가능. **유저 명시적 승인 필요**. 극히 예외적 |

**T2 소스 코드 차단**: 프롬프트 `[CONSTRAINTS]`에 "소스 코드 파일 수정/생성/삭제 절대 금지" 포함 + 실행 후 git diff로 소스 코드 변경 감지 시 선택적 원복.

### 1.2 멀티 스테이지 파이프라인

유저의 LLM 사용은 1개 이상의 **스테이지**로 구성될 수 있다. 각 스테이지는 독립된 목적, 모델, 권한, 로그를 가진다. 단일 스테이지도 동일 구조로 처리.

**예시: 문서 처리 파이프라인**
```
Stage 1: "summarize" — 문서를 읽고 요약 (T1, mini 모델)
    ↓ stdout 텍스트 전달
Stage 2: "generate"  — 요약 기반으로 새 문서 생성 (T2, 플래그십 모델)
    ↓ 생성된 파일 경로 전달
Stage 3: "review"    — 생성된 문서 품질 검토 (T1, 플래그십 모델)
```

**스테이지 간 데이터 전달**: 이전 스테이지의 stdout을 다음 프롬프트에 삽입하거나, 생성된 파일 경로를 전달.

---

## 2. 모델 선택 기준

### !! 반드시 최신 모델 목록을 먼저 조회할 것 !!

**매 실행 시** https://developers.openai.com/codex/models.md 를 WebFetch로 조회하여 모델 목록과 capability/speed 등급을 확인. 모델명을 절대 하드코딩하지 마세요.

| 용도 | 선택할 모델 특성 | 판단 기준 |
|------|-----------------|-----------|
| 간단한 대화/질문/요약 | 이름에 `mini` 포함 | speed 높고 capability 적절 |
| 빠른 인터랙션 복잡 태스크 | 이름에 `spark` 포함 | speed 최고 (5/5) |
| 코딩 작업 | 이름에 `codex` 포함 (spark 제외) | capability 최고, 코딩 특화 |
| 고급 사고/일반 지식 | 플래그십 모델 (codex/mini/spark 아닌 것) | 최고 추론 능력 |

- `models.json`의 `_fetched_at`이 7일 이상이면 재조회 권장
- WebFetch 실패 시 `codex --help` 또는 CLI에서 모델 목록 확인

---

## 3. 실행 모드

**중요**: 프로그래밍에서 codex를 호출할 때는 반드시 `codex exec` 서브커맨드를 사용합니다. `codex [PROMPT]`는 대화형 CLI이며, `codex exec [PROMPT]`가 비대화형(subprocess 호출용)입니다.

**git 저장소 필수**: `codex exec`는 기본적으로 git 저장소 내부에서만 실행됩니다. git이 초기화되지 않은 프로젝트에서는 `--skip-git-repo-check` 플래그를 추가해야 합니다. 설치 시 Phase 1에서 git 여부를 확인하고, 비-git 프로젝트면 모든 codex exec 호출에 이 플래그를 자동 포함하도록 커넥터를 구성합니다.

### 3.1 T1 text-only (기본)
```bash
codex exec --model <선택된_모델> "질문 내용"
# 비-git 프로젝트인 경우:
codex exec --skip-git-repo-check --model <선택된_모델> "질문 내용"
# 이미지 입력이 필요한 경우:
codex exec --model <선택된_모델> --image <파일경로> "이 이미지를 분석해줘"
```
**대부분의 스테이지는 이 모드로 충분합니다.** 프롬프트 제약으로 파일 수정 차단.

### 3.2 T2 data-write
```bash
codex exec --dangerously-bypass-approvals-and-sandbox --model <선택된_모델> "[CONSTRAINTS]
- 소스 코드 파일 수정/생성/삭제 절대 금지
- 수정 가능 대상: {allowed_extensions} 확장자만
- 작업 범위: {target_dir}/ 이내만
[/CONSTRAINTS]

{실제 프롬프트}"
```
**주의**: `--dangerously-bypass-approvals-and-sandbox`는 확인 없이 실행하므로, 반드시 `[CONSTRAINTS]`로 범위 제한 필수.

### 3.3 T3 full-write (유저 승인 필수)
T2와 동일 명령이나, 소스 코드 제약 없이 `allowed_dirs` 범위 제한 + `.bak` 백업.

### 3.4 Ephemeral (일회성, 세션 미저장)
```bash
codex exec --ephemeral --model <선택된_모델> "..."
```

### 3.5 Resume (이전 세션 이어가기)
```bash
codex exec resume --last "이전 작업에 이어서 ..."
```
같은 스테이지 내 연속 작업은 resume. 스테이지 전환 시 새 세션.

---

## 4. 출력 형식 옵션

| 형식 | 권한 등급 | 프롬프트 예시 |
|------|----------|-------------|
| **Plain text / JSON** | T1 | `"요약해줘"`, `"JSON으로 결과를 줘"` |
| **데이터/문서 파일 생성·수정** | T2 | `"output/result.json으로 저장해줘"` |
| **curl/Telegram 등 전송** | T2 | `"결과를 curl로 API에 POST해줘"` |
| **소스 코드 생성/수정** | T3 | `"src/utils/parser.ts를 생성해줘"` |

---

## 5. 보안 제약 프롬프트

### 5.1 공통 기본 제약 (모든 스테이지)
```
[CONSTRAINTS]
- 프로젝트 루트: {project_root} 이내에서만 작업
- 파일 삭제 금지
- .env, credentials, secrets 파일 읽기/수정 금지
- 파괴적 git 명령 금지
- 시스템 패키지 설치/시스템 디렉토리 접근 금지
- codex를 내부에서 다시 호출하지 마라
```

### 5.2 Tier별 추가 제약
- **T1**: `어떤 파일도 생성/수정/삭제 금지. stdout 텍스트 응답만 허용`
- **T2**: `소스 코드 파일 수정 절대 금지` + `수정 가능: {allowed_extensions}만` + `작업 디렉토리: {allowed_dirs}만` + `설정 파일 수정 금지`
- **T3**: `작업 범위: {allowed_dirs}만` + `수정 전 .bak 백업` + `변경 계획 먼저 출력`

### 5.3 선택적 제약 (필요 시 추가)
인터넷 금지, 외부 API 금지, 의존성 설치 금지, 바이너리 실행 금지, 환경변수 변경 금지, 포트 바인딩 금지, 출력 길이 제한, 민감 데이터 마스킹, 토큰 소모 제한

---

## 6. AGENTS.md 사전 점검

codex는 실행 시 `AGENTS.md`를 자동 읽어들임. **실행 전** 존재 여부 확인, 내용 검토, 충돌 시 유저 알림.

---

## 7. 로깅

### 로그 디렉토리 구조
```
{project_root}/.codex-llm/
├── pipeline.json          # 파이프라인 정의
├── models.json            # 모델 매핑
└── logs/
    ├── {stage_name}/      # 스테이지별 하위 디렉토리
    │   └── YYYY-MM-DD_HHmmss_{run_id}.json
    └── ...
```

### 로그 내용
```json
{
  "run_id": "unique-id",
  "stage": "summarize",
  "tier": "T1",
  "timestamp": "2026-03-23T14:30:00Z",
  "model": "<조회된_모델명>",
  "prompt": "프롬프트 전문",
  "constraints": ["제약 목록"],
  "output": "stdout 또는 생성/수정된 파일 경로",
  "exit_code": 0,
  "duration_seconds": 45
}
```

### 파일 변경 추적 (T2, T3)
1. 실행 전 스냅샷: `git diff --stat` 또는 파일 목록/mtime (비-git)
2. 실행 후 비교, 변경 파일 로그에 기록
3. **T2 위반 시**: 소스 코드 파일만 선택적 원복, 데이터 파일 변경은 유지

---

## 8. 타임아웃 관리

| 작업 유형 | 타임아웃 |
|-----------|---------|
| T1 간단한 질문/답변 | 3분 |
| T1 긴 문서 분석 | 5분 |
| T2/T3 파일 수정 | 10분 |
| 복잡한 멀티스텝/첫 대화 | 제한 없음 (유저 개입 유도) |

타임아웃 초과 시 강제 중단 X → 유저에게 상황 알려 개입 유도.
두리뭉실한 프롬프트는 codex가 탐색에 시간을 소모하므로 첫 대화 시 넉넉히 설정.

---

## 9. 커넥터 설치 워크플로우

### Phase 1: 프로젝트 분석
1. 기존 LLM import/호출 패턴 검색, 입출력 형식 분석
2. `AGENTS.md` 점검
3. 프로젝트 언어/프레임워크 확인
4. **git 저장소 여부 확인** (`.git` 디렉토리 존재) — 없으면 커넥터에 `--skip-git-repo-check` 자동 포함

### Phase 2: 유저에게 스테이지 설계 확인 (AskUserQuestion)

```
1. LLM 스테이지들을 알려주세요 (이름, 목적, 입출력)
2. 각 스테이지의 입력 타입:
   - 텍스트만? → 기본
   - 이미지 포함? → codex exec --image 플래그 사용
   - 오디오/비디오? → T2로 올려서 codex가 도구(ffmpeg 등)로 전처리
   - PDF/문서 파일? → 프롬프트에 파일 경로 명시
3. 각 스테이지 파일 수정 범위 (T1/T2/T3)
4. 기존 LLM API에서 사용 중인 고급 기능:
   - streaming 필요? → codex exec는 미지원, prod API 유지 권장
   - structured output / function calling? → 프롬프트 기반 JSON으로 대체 가능한지
   - temperature / max_tokens 등 세밀한 파라미터 제어? → codex exec는 제한적
5. prod 환경 LLM 계획 (codex만 / 외부 API 유지 / 미정)
```

이 질문에서 codex exec로 대체하기 어려운 기능이 발견되면, 해당 스테이지는 prod 커넥터(OpenAI/Gemini)를 dev에서도 유지하도록 설계합니다. 모든 스테이지를 codex로 강제 전환하지 않습니다.

### Phase 3: 설정 파일 생성

**pipeline.json** — 필수 필드만:
```json
{
  "stages": [
    {
      "name": "summarize",
      "purpose": "문서를 읽고 핵심 요약",
      "tier": "T1",
      "model_type": "chat"
    },
    {
      "name": "generate",
      "purpose": "요약 기반 새 문서 생성",
      "tier": "T2",
      "model_type": "reasoning"
      // 필요 시 추가: allowed_extensions, allowed_dirs, timeout_ms, ephemeral, extra_constraints
    }
  ],
  "prod_connector": "openai"
}
```

**models.json** — WebFetch로 조회하여 생성:
```json
{
  "_fetched_from": "https://developers.openai.com/codex/models.md",
  "_fetched_at": "2026-03-23T14:30:00Z",
  "chat": "<조회된 mini 모델>",
  "fast_complex": "<조회된 spark 모델>",
  "code": "<조회된 codex 모델>",
  "reasoning": "<조회된 플래그십 모델>"
}
```

### Phase 4: 커넥터 구현

프로젝트 언어에 맞게 교체 가능한 LLM 커넥터를 구현합니다. 핵심 구조:

1. **LLMConnector 인터페이스**: `query(prompt, stage) -> str` / `query_json(prompt, schema, stage) -> dict`
2. **구현체**: `CodexConnector` (dev), `OpenAIConnector` / `GeminiConnector` (prod)
3. **StageConfig**: pipeline.json에서 로드, tier에 따라 codex 실행 옵션과 제약 자동 결정
4. **제약 주입 흐름**: `StageConfig.tier` → `_build_constraints()` → `[CONSTRAINTS]` 블록 → 프롬프트에 자동 삽입
5. **T2 사후 검증**: 실행 후 git diff로 소스 코드 변경 감지 → 위반 시 선택적 원복

환경변수로 커넥터 전환:
```env
LLM_CONNECTOR=codex    # codex | openai | gemini
```

### Phase 5: 기존 코드 전환 & 문서화
1. 기존 LLM 호출부를 커넥터 인터페이스로 교체, 각 호출을 스테이지에 매핑
2. 기존 API 키 설정 유지 (prod 전환용)
3. README에 환경 전환 방법, 스테이지 목록, 권한 등급 문서화

---

## 10. 에러 처리

| 상황 | 대응 |
|------|------|
| codex 미설치 | `npm install -g @openai/codex` 안내 |
| 인증 실패 | `codex auth` 실행 안내 |
| 타임아웃 | 유저에게 스테이지명과 상황 알리고 개입 유도 (강제 중단 X) |
| T2 소스 코드 변경 감지 | 소스 파일만 git checkout 원복, 유저 경고, 로그 기록 |
| T3 무승인 사용 시도 | 차단, T3 승인 필요 안내 |
| 모델 미지원 | models.json 재생성 안내 |
| 출력 파싱 실패 | 재시도 1회, 실패 시 plain text 폴백 |

---

## 11. .gitignore 추가

```
# codex-llm
.codex-llm/logs/
*.bak
```
`pipeline.json`과 `models.json`은 프로젝트 설정이므로 git 포함 가능 (유저 확인).
