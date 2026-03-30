# Coding Score 상세 평가 기준

## 목차
1. [코드 기능적 정확성](#1-코드-기능적-정확성)
2. [성능 및 효율성](#2-성능-및-효율성)
3. [보안 취약점](#3-보안-취약점)
4. [코드 가독성/유지보수성](#4-코드-가독성유지보수성)
5. [DB 스키마 & API 설계](#5-db-스키마--api-설계)
6. [사용자 경험](#6-사용자-경험)

---

## 1. 코드 기능적 정확성

### 체크리스트
- [ ] 테스트 통과 여부: 모든 단위/통합 테스트 통과
- [ ] 테스트 커버리지: 라인/분기 커버리지 비율
- [ ] 엣지 케이스 처리: null, 0, 빈 배열, 범위 초과
- [ ] 기능 요구사항 충족: TODO/FIXME 미완성 항목 없음
- [ ] 오류 처리: 적절한 예외 처리 및 에러 메시지

### 점수 기준
| 점수 | 기준 |
|------|------|
| 9-10 | 테스트 100% 통과, 커버리지 90%+, 엣지 케이스 완벽 |
| 7-8 | 테스트 80%+ 통과, 커버리지 70%+, 경미한 결함 |
| 4-6 | 테스트 50%+ 통과, 일부 기능 오동작 |
| 0-3 | 테스트 50% 미만, 핵심 기능 실패 |

### 탐지 패턴
```python
# TODO/FIXME 미완성
TODO_PATTERN = r'#\s*(TODO|FIXME|XXX|HACK)'

# 타입 힌트 사용 (Python)
TYPE_HINT_PATTERN = r'def \w+\([^)]*:\s*\w+'

# try-except 에러 핸들링
ERROR_HANDLING_PATTERN = r'try:\s*\n.*\nexcept'
```

---

## 2. 성능 및 효율성

### 체크리스트
- [ ] 알고리즘 복잡도: O(n²) 이상 중첩 루프 없음
- [ ] N+1 쿼리: ORM에서 반복 쿼리 없음
- [ ] 메모리 효율: 대용량 데이터 스트리밍 처리
- [ ] 불필요한 연산: 루프 내 반복 계산 없음
- [ ] 캐싱 활용: 반복 호출 결과 캐싱

### 점수 기준
| 점수 | 기준 |
|------|------|
| 9-10 | 최적 알고리즘, 효율적 자원 사용 |
| 7-8 | 전반적 양호, 약간의 최적화 여지 |
| 4-6 | 성능 이슈 존재, 병목 구간 확인됨 |
| 0-3 | 심각한 성능 문제, 실사용 어려움 |

### 탐지 패턴
```python
# 중첩 루프 (O(n²))
NESTED_LOOP = r'for .+:\s*\n\s+for .+:'

# N+1 쿼리 (Django/SQLAlchemy)
N_PLUS_ONE = r'\.objects\.(get|filter)\(|\.query\.(get|filter)\('

# 루프 내 DB 호출
LOOP_DB_CALL = r'for .+:\s*\n.*\.(save|create|update|delete)\('

# 전체 데이터 로딩
FULL_LOAD = r'\.(all|find)\(\)(?!\s*\[:\d+\])'
```

---

## 3. 보안 취약점

### 체크리스트
- [ ] SQL 인젝션: 파라미터 바인딩 사용
- [ ] XSS: 사용자 입력 이스케이프
- [ ] 하드코딩 시크릿: API 키, 비밀번호 미노출
- [ ] 취약한 함수: eval, exec 미사용
- [ ] 인증/권한: 민감 기능 보호
- [ ] 의존성 취약점: npm audit / pip audit 통과

### 점수 기준
| 점수 | 기준 |
|------|------|
| 9-10 | 취약점 0건, 보안 모범 사례 준수 |
| 7-8 | 심각한 취약점 없음, 경미한 권고사항 |
| 4-6 | 몇몇 취약점 확인, 패치 필요 |
| 0-3 | 중대한 보안 결함, 배포 위험 |

### 탐지 패턴
```python
# SQL 인젝션
SQL_INJECTION = r'f["\'].*(SELECT|INSERT|UPDATE|DELETE).*\{|%s.*%.*\('

# 하드코딩 시크릿
HARDCODED_SECRET = r'(api_key|password|secret|token|key)\s*=\s*["\'][^"\']{8,}["\']'

# 취약 함수
DANGEROUS_FUNC = r'\b(eval|exec|compile|__import__)\s*\('

# XSS (JS)
XSS_PATTERN = r'innerHTML\s*=|document\.write\(|\.html\([^)]*\$'
```

---

## 4. 코드 가독성/유지보수성

### 체크리스트
- [ ] 코딩 표준: PEP8/ESLint 규칙 준수
- [ ] 네이밍 일관성: 명확하고 일관된 명명
- [ ] 함수 길이: 50줄 이하 권장
- [ ] 순환 복잡도: 함수당 10 이하
- [ ] 코드 중복: 중복 블록 최소화
- [ ] 주석 적절성: 필요한 곳에만 명확하게

### 점수 기준
| 점수 | 기준 |
|------|------|
| 9-10 | 린트 에러 0건, 복잡도 모두 권장치 이하 |
| 7-8 | 린트 경고 일부, 전반적으로 양호 |
| 4-6 | 린트 에러 다수, 리팩토링 필요 |
| 0-3 | 스파게티 코드 수준, 전면 개편 필요 |

### 스파게티 코드 지표
| 메트릭 | 경고 기준 | 심각 기준 |
|--------|----------|----------|
| 순환 복잡도 | > 10 | > 20 |
| 함수 길이 (LOC) | > 50 | > 100 |
| 파일 길이 (LOC) | > 300 | > 500 |
| 클래스 결합도 (CBO) | > 10 | > 20 |

---

## 5. DB 스키마 & API 설계

### DB 스키마 체크리스트
- [ ] 기본 키: 모든 테이블에 PK 존재
- [ ] 정규화: 3NF 수준, 중복 최소화
- [ ] 외래 키: 테이블 관계 FK로 명시
- [ ] 인덱스: 조회 빈도 높은 컬럼 인덱싱
- [ ] 데이터 타입: 적절한 타입/크기 선택
- [ ] 제약 조건: UNIQUE, NOT NULL, CHECK 활용

### API 설계 체크리스트
- [ ] RESTful: 명사형 URI, 적절한 HTTP 메서드
- [ ] 상태 코드: 올바른 HTTP 상태 코드 사용
- [ ] 에러 응답: 유용한 오류 메시지 제공
- [ ] 일관성: 응답 형식 통일 (JSON)
- [ ] 버전 관리: API 버전 명시 (/v1/)
- [ ] 문서화: OpenAPI/Swagger 제공

### 점수 기준
| 점수 | 기준 |
|------|------|
| 9-10 | 모범 사례 충실, PK/FK 완비, RESTful |
| 7-8 | 전반적 양호, 작은 개선 여지 |
| 4-6 | 여러 개선점 필요, 비표준 설계 |
| 0-3 | 설계 오류, 전면 검토 필요 |

### 탐지 패턴
```python
# Django 모델 PK 누락 (자동 생성 아닌 경우)
# Flask-SQLAlchemy 모델 분석
MODEL_PATTERN = r'class \w+\(.*Model.*\):'

# REST 엔드포인트
REST_PATTERN = r'@(app|router)\.(get|post|put|patch|delete)\s*\(["\']'

# 비RESTful 패턴 (동사 포함 URL)
NON_REST = r'/(get|create|update|delete|fetch|save)\w*'
```

---

## 6. 사용자 경험

### 체크리스트
- [ ] 에러 메시지: 사용자 친화적, 해결책 제시
- [ ] 로딩 피드백: 진행 상태 표시
- [ ] 접근성: alt 텍스트, aria 속성
- [ ] 반응형: 미디어 쿼리, 유연한 레이아웃
- [ ] 입력 검증: 실시간 피드백

### 점수 기준
| 점수 | 기준 |
|------|------|
| 9-10 | 직관적 UX, 접근성 완비, 만족도 높음 |
| 7-8 | 대체로 양호, 경미한 불편 |
| 4-6 | UX 문제점 존재, 개선 필요 |
| 0-3 | 사용 불편, UX 재설계 필요 |

### 탐지 패턴
```python
# 접근성 (HTML/JSX)
ACCESSIBILITY = r'alt=|aria-|role='

# 반응형
RESPONSIVE = r'@media|flex|grid|min-width|max-width'

# 에러 메시지 품질 (너무 기술적)
TECH_ERROR = r'(Exception|Error|Traceback|stack trace)'
```

---

## 종합 점수 계산

```python
def calculate_total_score(scores: dict) -> float:
    """가중 평균으로 종합 점수 계산"""
    weights = {
        'correctness': 0.20,      # 기능적 정확성
        'performance': 0.15,      # 성능
        'security': 0.20,         # 보안
        'maintainability': 0.20, # 유지보수성
        'architecture': 0.15,    # 아키텍처
        'ux': 0.10               # UX
    }

    total = sum(scores[k] * weights[k] for k in weights)
    return round(total, 1)
```

## 참고 자료

- ISO/IEC 25010: 소프트웨어 제품 품질 모델
- OWASP Top 10: 웹 애플리케이션 보안 취약점
- PEP 8 / Airbnb Style Guide: 코딩 규칙
- Clean Code (Robert C. Martin): 가독성 원칙
