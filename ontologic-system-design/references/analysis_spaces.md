# 6 분석공간 프레임워크 (6 Analysis Spaces Framework)

온톨로지 기반 시스템 분석의 핵심 도구. 모든 엔티티와 개념을 6개 독립적이면서 상호연결된 위상적 차원으로 분류한다.

> 원리: 확률적 추측("다음 단어 확률?")에서 구조적 이해("개념 간 구조적 관계?")로의 패러다임 전환

---

## 1. 계층 공간 (Hierarchy Space)

**핵심 질문**: "이 개념은 어느 수준에 있는가?"

**경고**: 상위 결론을 하위에 직접 적용하는 것은 왜곡의 핵심 오류.

### 코드 지표
- 패키지/디렉토리 중첩 깊이
- 클래스 상속 계층 (base → concrete)
- 모듈 의존성 방향 (상위 → 하위)
- 추상화 레이어 (interface → implementation)
- 설정의 계층 (global → env → local override)

### 스캔 방법
```
# 디렉토리 깊이 분석
Glob: "src/**/*.py" → 경로 깊이 분포

# 클래스 상속 트리
Grep: "class \w+\(.+\):" → 부모 클래스 추출

# 추상 클래스/인터페이스
Grep: "ABC|Protocol|@abstractmethod|Interface"

# import 방향성
Grep: "^from |^import " → 의존 방향 분석
```

### 일반 패턴
- MVC/MVT 레이어 분리
- 헥사고날 아키텍처 (도메인 ↔ 포트 ↔ 어댑터)
- 클린 아키텍처 (엔티티 → 유스케이스 → 인터페이스 → 프레임워크)

### 안티패턴
- **God Class**: 하나의 클래스가 여러 계층을 관통
- **순환 의존**: 상위↔하위 간 양방향 import
- **계층 누수**: 하위 레이어 세부사항이 상위에 노출
- **무분별한 상속**: 5+ 깊이의 상속 체인

---

## 2. 시간 공간 (Temporal Space)

**핵심 질문**: "언제, 어떤 리듬으로 발생하는가?"

엔티티가 시간 축 위에서 생성·변화·소멸하는 과정을 추적한다.
예: 잠재고객 → 가입 → 활성 → 이탈 → 복귀

### 코드 지표
- 상태 머신 / 상태 전이 (Enum + transition rules)
- 이벤트 소싱 (append-only event log)
- 스케줄러 / cron 작업
- 마이그레이션 파일 (DB schema versioning)
- 타임스탬프 필드 (created_at, updated_at, expires_at)
- 버전 관리 패턴 (v1/v2 API, schema version)
- TTL / 만료 로직

### 스캔 방법
```
# 상태 머신 식별
Grep: "class.*State|status.*enum|WATCH|PENDING|ACTIVE|RESOLVED"

# 이벤트 소싱
Grep: "event_store|append_event|EventLog|emit\(|publish\("

# 스케줄링
Grep: "cron|schedule|interval|tick|periodic|@scheduled"

# 마이그레이션
Glob: "**/migrations/**" 또는 "**/alembic/**"

# 시간 의존성
Grep: "datetime|timestamp|created_at|updated_at|expires|ttl"
```

### 일반 패턴
- 이벤트 드리븐 아키텍처 (Event → Handler → Side Effect)
- Saga 패턴 (분산 트랜잭션의 시간 순서)
- CQRS (Command 시점 ≠ Query 시점)
- 배치 vs 스트림 처리

### 안티패턴
- **숨은 시간 의존성**: 암묵적 실행 순서에 의존
- **레이스 컨디션**: 동시 접근 시 상태 불일치
- **이벤트 순서 미보장**: 순서 의존 로직에 비순서 큐 사용
- **시간 결합**: 모듈 A가 모듈 B의 실행 타이밍에 의존

---

## 3. 재귀 공간 (Recursive Space)

**핵심 질문**: "자기 자신을 어떻게 참조하는가?"

메타인지, 자기 개선, 피드백 루프가 학습과 지능 성장의 기반.
프랙탈 분해와 도메인 온톨로지가 메타 후퇴의 앵커 역할.

### 코드 지표
- 자기 참조 타입 (트리 구조, parent_id → same table)
- 메타프로그래밍 (metaclass, decorator, code generation)
- 규칙이 규칙을 생성하는 구조
- 팩토리 패턴 (팩토리의 팩토리)
- 자기 평가 / 자기 개선 루프
- 재귀적 데이터 구조 (Composite 패턴)
- 스키마가 스키마를 정의 (JSON Schema, OWL)

### 스캔 방법
```
# 자기 참조 관계
Grep: "parent_id|self_ref|ForeignKey.*self|children"

# 메타프로그래밍
Grep: "metaclass|__new__|type\(|exec\(|eval\(|@wraps"

# 코드 생성
Grep: "generate.*code|template.*render|codegen|ast\.parse"

# 자기 평가 루프
Grep: "score|evaluate|intent_score|self_review|feedback_loop"

# 재귀 호출 (단일라인 힌트)
Grep: "return \w+\(" → 함수명과 대조하여 재귀 식별
# 또는 멀티라인 (multiline: true 필요)
Grep: "def (\w+).*\n.*\1\("
```

### 일반 패턴
- Composite 패턴 (트리 구조의 균일 처리)
- Interpreter 패턴 (AST → 재귀 평가)
- 메타-온톨로지 (온톨로지를 만드는 온톨로지)
- Rule-that-generates-rules (규칙 에이전트)

### 안티패턴
- **무한 재귀 위험**: 종료 조건 없는 자기 참조
- **과도한 메타 계층**: 추상화가 너무 깊어 이해 불가
- **메타 후퇴**: 자기 참조가 의미 없는 순환에 빠짐

---

## 4. 구조 공간 (Structural Space)

**핵심 질문**: "개념 간 관계는 무엇인가?"

Leiden 알고리즘의 커뮤니티 탐지, NOMIK의 모듈 간 의존성 구조 발견이 대표적.

### 코드 지표
- 외래 키 / 관계 정의 (ORM relationship)
- import 그래프 (모듈 간 의존성)
- 의존성 주입 (DI container)
- 메시지 패싱 (이벤트 버스, pub/sub)
- 공유 상태 (global state, shared DB)
- API 엔드포인트 연결 (서비스 간 호출)
- 타입 참조 (제네릭, Union, Protocol)

### 스캔 방법
```
# ORM 관계
Grep: "relationship|ForeignKey|ManyToMany|has_many|belongs_to"

# import 그래프
Grep: "^from \w+ import|^import \w+" → 모듈 의존성 맵

# DI / IoC
Grep: "inject|@inject|Container|Provider|Factory"

# 이벤트 버스
Grep: "subscribe|publish|emit|on\(|addEventListener"

# API 호출
Grep: "requests\.|fetch\(|axios\.|httpx\."
```

### 일반 패턴
- Entity-Relationship 모델 (DB 스키마)
- 마이크로서비스 토폴로지
- 이벤트 버스 구독자 맵
- 플러그인 아키텍처 (core ↔ plugin)

### 안티패턴
- **긴밀 결합**: 직접 참조가 추상화 없이 교차
- **숨은 의존성**: import에 나타나지 않는 런타임 의존
- **God Object**: 모든 것과 관계 맺는 중앙 객체
- **순환 참조**: A→B→C→A 의존 사이클

---

## 5. 인과 공간 (Causal Space)

**핵심 질문**: "이것의 원인은 무엇인가?"

원인-결과 사슬 추적. 상관관계와 인과관계를 구분.

### 코드 지표
- 트리거 체인 (이벤트 A → 핸들러 B → 이벤트 C)
- 에러 전파 경로 (exception → catch → re-raise → log)
- Cascade 삭제/업데이트
- 웹훅 체인 (외부 서비스 호출 연쇄)
- 콜백 체인 (then → then → catch)
- 조건부 분기의 영향 범위

### 스캔 방법
```
# 이벤트 핸들러 체인
Grep: "@on_event|def handle_|def on_|EventHandler"

# 에러 전파
Grep: "raise |except.*raise|reraise|propagate"

# Cascade
Grep: "cascade|on_delete|ON DELETE"

# 웹훅
Grep: "webhook|callback_url|notify_url"

# 부수 효과
Grep: "side_effect|after_save|post_commit|signal\."
```

### 일반 패턴
- Command-Event 체인 (CQRS)
- Observer / Pub-Sub 패턴
- Middleware 파이프라인 (request → middleware₁ → ... → response)
- Impact Analysis (변경이 미치는 영향 추적)

### 안티패턴
- **원격 작용 (Action at a distance)**: 먼 곳의 코드가 예기치 않게 영향
- **숨은 부수 효과**: 함수가 명시하지 않은 상태 변경
- **끊어진 인과 체인**: 에러가 삼켜져 원인 추적 불가
- **암묵적 의존**: 환경 변수나 글로벌 상태 의존

---

## 6. 교차 공간 (Cross-Space)

**핵심 질문**: "나머지 5개 공간을 동시에 고려할 때 나타나는 창발적 차원은?"

5개 공간의 교차점에서 **새로운 의미**가 창발한다. 3개 이상 공간에 동시에 걸친 개념이 최고 레버리지 개선 대상.

### 식별 방법
1. 각 엔티티를 5개 공간에서 점수화 (해당 공간 관련도 0~3)
2. 3개 이상 공간에서 점수 ≥ 2인 엔티티 식별
3. 이들이 "교차공간 엔티티" — 시스템의 핵심 허브

### 교차공간 패턴 예시

**모니터링 시스템의 Alert**:
- 계층: 신호 → 경고 → 에스컬레이션 (3단계)
- 시간: WATCH → VERIFYING → ALERT → RESOLVED (상태 전이)
- 재귀: alert가 alert를 트리거 (연쇄 경보)
- 구조: Signal ↔ Case ↔ Report 관계
- 인과: threshold 초과 → 검증 → 확정 → 보고

→ Alert는 5개 공간 모두에 걸친 **최고 레버리지 엔티티**

**Web API의 User**:
- 계층: admin → manager → member (역할 계층)
- 시간: 가입 → 활성 → 휴면 → 탈퇴 (생명주기)
- 구조: User ↔ Order ↔ Product (관계 허브)
- 인과: 로그인 → 권한 확인 → 데이터 접근

→ User는 4개 공간에 걸친 핵심 엔티티

### 가치
- 교차공간 엔티티를 개선하면 시스템 전체에 파급 효과
- 메타-에지(관계 규칙) 정의의 최우선 대상
- 온톨로지 설계의 시작점

---

## 진단 템플릿

| 엔티티 | 계층 (0-3) | 시간 (0-3) | 재귀 (0-3) | 구조 (0-3) | 인과 (0-3) | 교차 점수 | 비고 |
|--------|-----------|-----------|-----------|-----------|-----------|----------|------|
| _예: AlertCase_ | 3 | 3 | 1 | 3 | 3 | **13/15** | 핵심 허브 |
| _예: Config_ | 2 | 1 | 0 | 1 | 0 | 4/15 | 정적 |
| ... | | | | | | | |

**점수 기준**:
- 0: 해당 공간과 무관
- 1: 약한 관련 (단일 속성/동작)
- 2: 중간 관련 (여러 속성/동작)
- 3: 핵심 관련 (해당 공간의 주요 행위자)

**교차 점수 해석**:
- 12-15: 시스템 핵심 허브 → 온톨로지 설계 최우선
- 8-11: 중요 엔티티 → 관계 명시화 필요
- 4-7: 보조 엔티티 → 기본 타입 정의 충분
- 0-3: 유틸리티/헬퍼 → 온톨로지 범위 밖
