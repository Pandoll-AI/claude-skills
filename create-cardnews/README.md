# Create Cardnews — 카드뉴스 제작 스킬

논문·보고서·블로그 글을 **근거 중심의 한국어 카드뉴스**로 만드는 Claude Code 스킬입니다. 긴 문장을 무작정 이미지에 넣는 대신 핵심 메시지를 장별로 구성하고, 정량 성능은 출처·평가 조건을 보존한 채 시각화합니다.

- **기본 규격:** 1122×1402 px, 남색·노랑·크림, PNG 캐러셀
- **산출물:** 장별 PNG, 전체 미리보기, `manifest.json`, 편집 가능한 입력 JSON
- **실행 환경:** Python 3 + Pillow + 시스템 한글 폰트 (웹 API 불필요)
- **레이아웃:** 표지, 목록, 가로 막대그래프, 표, 핵심 수치, 결론

> **중요:** 2026년 11월 의료 LLM 카드뉴스를 만드는 데 사용한 디자인 지침을 바탕으로 다시 구성한 **재구현 스킬**입니다. 과거 원본 ZIP의 코드를 복원한 것이 아닙니다. 예제는 공개 의료 AI 자료를 편집한 것이며 의료기기 성능 검증을 의미하지 않습니다.

## Claude Code 설치

이 프로젝트는 [Pandoll AI Skills 마켓플레이스](https://github.com/Pandoll-AI/claude-skills)에 등록돼 있습니다.

```text
/plugin marketplace add Pandoll-AI/claude-skills
/plugin install create-cardnews@pandoll-ai-skills
```

설치 후: "이 블로그 글로 10장 카드뉴스 만들어줘. 숫자와 출처를 검수해줘."

## 직접 실행

```bash
python3 -m pip install -r requirements.txt
python3 scripts/render_cards.py examples/medical-llm/deck.json --output output/medical-llm
```

`output/medical-llm`에 10장의 PNG와 `preview_contact_sheet.png`, `manifest.json`이 생성됩니다. 새로운 주제는 예제 JSON을 복사해 텍스트와 수치를 수정해 실행합니다.

원본 분석 글: [의료 LLM, 한국어에 강하면 영어에도 강할까](https://blog.pandoll-ai.com/p/58525fa7-f)

## 보안 및 출처

환자 개인정보와 기관 비공개 문서를 공개 저장소에 넣지 마세요. 의료 모델의 시험 점수와 실제 임상 성능은 구분해야 하며, 서로 다른 평가에서 얻은 수치를 같은 순위로 표시하지 않습니다. 한글 폰트는 라이선스 문제를 피하도록 패키지에 넣지 않습니다.