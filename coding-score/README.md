# Coding Score - AI 코드 품질 평가 Claude Skill

AI 생성 코드의 품질을 6가지 핵심 영역에서 평가하고 상세 리포트를 생성하는 Claude Skill입니다.

## 설치 위치

```
~/.claude/skills/coding-score/
```

## 평가 영역

| 영역 | 설명 | 가중치 |
|------|------|--------|
| 기능적 정확성 | 테스트 통과율, 커버리지, 에러 핸들링 | 20% |
| 성능 및 효율성 | 알고리즘 복잡도, N+1 쿼리, 메모리 사용 | 15% |
| 보안 취약점 | SQL 인젝션, XSS, 하드코딩 시크릿 | 20% |
| 유지보수성 | 린트, 복잡도 메트릭, 코드 스타일 | 20% |
| 아키텍처 | DB 스키마 설계, API 구조, 모듈화 | 15% |
| 사용자 경험 | 에러 메시지, 접근성, 반응형 | 10% |

## 사용법

### Claude Code에서 스킬 호출

```
이 프로젝트의 코드 품질을 평가해줘
```

### CLI 직접 실행

```bash
# 기본 분석 (JSON 출력)
python ~/.claude/skills/coding-score/scripts/analyze.py /path/to/project

# 상세 리포트 생성 (Markdown 출력)
python ~/.claude/skills/coding-score/scripts/analyze.py /path/to/project | \
  python ~/.claude/skills/coding-score/scripts/report.py

# 패턴만 분석
python ~/.claude/skills/coding-score/scripts/patterns.py /path/to/project
```

## 지원 언어

- **Python**: pytest, coverage.py, pylint, bandit, radon
- **JavaScript/TypeScript**: jest, eslint, npm audit

도구가 설치되지 않은 경우 정적 패턴 분석으로 대체됩니다.

## 탐지 패턴

### 보안 취약점
- SQL 인젝션 (f-string, .format, 문자열 연결)
- 하드코딩된 시크릿/API 키
- 위험한 함수 (eval, exec)
- XSS 취약 패턴 (innerHTML)
- 쉘 인젝션

### 성능 이슈
- 중첩 루프 (O(n²))
- N+1 쿼리 패턴
- 루프 내 DB 작업
- 전체 테이블 로딩

### 아키텍처 이슈
- 비RESTful URL 패턴
- 매직 넘버
- 50줄 초과 함수
- TODO/FIXME 미완성 항목
- 디버그 출력문 (console.log, print)

### UX 이슈
- 이미지 alt 속성 누락
- 일반적인 에러 메시지
- 스택 트레이스 노출

## 리포트 예시

```markdown
# 코드 품질 평가 리포트

## 종합 점수: 7.5/10

| 영역 | 점수 | 상태 |
|------|------|------|
| 기능적 정확성 | 8/10 | 양호 |
| 성능 및 효율성 | 6/10 | 양호 |
| 보안 취약점 | 7/10 | 양호 |
| ...

## 상세 분석
...
```

## 파일 구조

```
coding-score/
├── SKILL.md          # 스킬 정의 (Claude가 읽는 진입점)
├── README.md         # 이 문서
├── reference.md      # 상세 평가 기준
├── .gitignore
└── scripts/
    ├── analyze.py    # 통합 분석 스크립트
    ├── patterns.py   # 정적 패턴 분석 모듈
    └── report.py     # 리포트 생성 모듈
```

## 점수 기준

각 영역은 0-10점으로 평가됩니다:

| 점수 | 등급 | 설명 |
|------|------|------|
| 9-10 | 우수 | 모범 사례 준수, 이슈 없음 |
| 7-8 | 양호 | 전반적으로 양호, 경미한 개선점 |
| 4-6 | 개선 필요 | 여러 이슈 존재, 리팩토링 권장 |
| 0-3 | 미흡 | 심각한 문제, 즉시 수정 필요 |

## 참고 자료

- [ISO/IEC 25010](https://www.iso.org/standard/35733.html) - 소프트웨어 품질 모델
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - 웹 보안 취약점
- [PEP 8](https://peps.python.org/pep-0008/) - Python 스타일 가이드

## 라이선스

MIT License
