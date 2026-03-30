---
name: ui-walkthrough
description: >
  UI/UX audit skill. Walks through a browser UI flow step by step, takes a
  screenshot at each interaction, traces findings to source code, and produces
  a timestamped markdown report with UX improvement suggestions.
  Use when user says: "UI 감사", "UX 리뷰", "화면 점검", "audit the UI",
  "walkthrough the flow", "스크린샷 문서화".
argument-hint: "[URL] [flow description]  — URL 생략 시 현재 탭 사용"
---

You are executing a structured UI/UX audit. Follow the 5-phase workflow below exactly.

## Phase 0: 초기화

1. **탭 컨텍스트 확인**: `mcp__claude-in-chrome__tabs_context_mcp` 로 현재 탭 ID와 URL 확인
   - 인자로 URL이 제공된 경우 → `mcp__claude-in-chrome__navigate` 로 이동
   - URL 없으면 현재 탭 그대로 사용

2. **프로젝트 루트 확인**:
   ```bash
   git rev-parse --show-toplevel 2>/dev/null || echo "no-git"
   ```
   - git 루트가 없으면 `~/Desktop` 또는 현재 작업 디렉터리를 사용

3. **출력 디렉터리 생성**:
   ```bash
   mkdir -p $PROJECT_ROOT/ui-audit/screenshots
   ```

4. **리포트 파일명 결정**:
   ```bash
   date '+%Y-%m-%d-%H-%M'
   ```
   → 리포트 경로: `$PROJECT_ROOT/ui-audit/YYYY-MM-DD-HH-MM.md`

5. **리포트 헤더 초기화** — `Write` 도구로 파일 생성:
   ```markdown
   # UI/UX Audit — [URL]
   **날짜**: YYYY-MM-DD HH:MM
   **플로우**: [flow description]
   **감사자**: Claude (ui-walkthrough skill)

   ---

   ## 인터랙션 플랜

   (Phase 1 완료 후 채워 넣음)

   ---
   ```

---

## Phase 1: 초기 정찰

1. **초기 스크린샷 캡처**: `mcp__claude-in-chrome__computer` (action: screenshot)
   - 스크린샷을 시각적으로 확인한 뒤, JS로 canvas 캡처 → 파일 저장:
   ```javascript
   // mcp__claude-in-chrome__javascript_tool — 페이지를 canvas로 캡처하여 다운로드
   (async () => {
     const c = document.createElement('canvas');
     c.width = window.innerWidth; c.height = window.innerHeight;
     const ctx = c.getContext('2d');
     // SVG foreignObject 기법으로 DOM 스냅샷
     const data = `<svg xmlns="http://www.w3.org/2000/svg" width="${c.width}" height="${c.height}">
       <foreignObject width="100%" height="100%">
         <div xmlns="http://www.w3.org/1999/xhtml">${document.documentElement.outerHTML}</div>
       </foreignObject></svg>`;
     const img = new Image();
     const blob = new Blob([data], {type:'image/svg+xml'});
     const url = URL.createObjectURL(blob);
     img.onload = () => { ctx.drawImage(img, 0, 0); URL.revokeObjectURL(url); };
     img.src = url;
     return 'canvas-captured';
   })();
   ```
   - **주의**: JS canvas 캡처는 CORS/외부 리소스 제약이 있을 수 있음.
     실패 시 `mcp__claude-in-chrome__computer` (screenshot)의 시각 정보를 텍스트로 상세 기술하여 리포트에 기록.
   - 리포트에는 스크린샷 설명을 **텍스트 + 스크린샷 참조** 형태로 기록:
     ```markdown
     **[스크린샷: step-00-initial]** — 초기 로드 상태. 메인 헤더, 네비게이션 바, 히어로 섹션 표시.
     ```

2. **DOM 구조 파악**: `mcp__claude-in-chrome__read_page` + `mcp__claude-in-chrome__get_page_text`

3. **콘솔 기준선 기록**: `mcp__claude-in-chrome__read_console_messages` → 기존 에러를 리포트에 기록
   - **기준선 파일 저장** (Phase 2에서 diff 비교용):
   ```javascript
   // mcp__claude-in-chrome__javascript_tool — 콘솔 에러 수를 전역 변수에 저장
   window.__auditConsoleBaseline = performance.now();
   ```
   - 이후 Phase 2 D단계에서는 `mcp__claude-in-chrome__read_console_messages` 호출 시 기준선 시점 이후 에러만 필터링

4. **인터랙션 플랜 수립** (5~12 스텝):
   - 페이지에서 테스트할 주요 사용자 여정을 분석해 스텝 목록 작성
   - `Edit` 도구로 리포트의 "인터랙션 플랜" 섹션을 채움:
     ```markdown
     1. 초기 상태 확인
     2. [다음 스텝]
     ...
     ```

---

## Phase 2: 단계별 인터랙션 루프

**각 스텝마다 A→H 순서를 반복:**

### A. 요소 찾기
```
mcp__claude-in-chrome__find — selector 또는 text로 대상 요소 특정
```

### B. 액션 실행
- 클릭: `mcp__claude-in-chrome__computer` (action: click, coordinate: [x, y])
- 폼 입력: `mcp__claude-in-chrome__form_input`
- 페이지 이동: `mcp__claude-in-chrome__navigate`

### C. 결과 스크린샷 캡처
```
mcp__claude-in-chrome__computer (action: screenshot)
```
- 스크린샷은 Claude가 시각적으로 분석한 뒤, 리포트에 **텍스트 상세 설명**으로 기록
- 리포트 기록 형식:
  ```markdown
  **[스크린샷: step-NN-slug]** — (화면에 보이는 내용을 구체적으로 기술:
  레이아웃, 표시된 요소, 색상, 상태 변화 등)
  ```
- 파일명 참조 규칙: `step-NN-<action-slug>` (예: `step-02-click-signup`)

### D. 콘솔 에러 확인
```
mcp__claude-in-chrome__read_console_messages
```
→ 이전 기준선과 비교해 새로 발생한 에러만 기록

### E. 네트워크 실패 확인 (폼 제출 / API 호출 시)
```
mcp__claude-in-chrome__read_network_requests
```
→ 4xx/5xx 응답, 긴 지연 시간 기록

### F. DOM 식별자 추출
```javascript
// mcp__claude-in-chrome__javascript_tool 로 실행
document.activeElement?.dataset?.testid
  || document.activeElement?.getAttribute('data-testid')
  || document.activeElement?.id
  || document.activeElement?.className
```

### G. 소스코드 추적 (3단계)
1. F에서 얻은 식별자로 **`Grep` 도구** 사용 (bash grep 금지):
   ```
   Grep: pattern="IDENTIFIER", glob="*.{tsx,ts,jsx,js}", path="src/", output_mode="content", head_limit=5
   ```
2. `Read` 도구로 해당 파일 열어 컨텍스트 확인
3. `src/components/Foo.tsx:42` 형식으로 참조 기록

### H. 리포트에 스텝 섹션 즉시 기록
`Edit` (append) 로 리포트에 추가:

```markdown
## Step N: [액션 설명]

![Step N](screenshots/step-NN-slug.png)

| 항목 | 내용 |
|------|------|
| **URL** | `https://...` |
| **액션** | 버튼 클릭 / 폼 입력 / 네비게이션 |
| **발생한 일** | ... |
| **기대 동작** | ... |
| **심각도** | Low / Medium / High / Critical |

**코드 참조**: `src/components/Auth/LoginForm.tsx:47`

**콘솔 에러**: 없음 / (에러 내용)

**UX 문제**:
- (발견된 문제 목록)

**개선 제안**:
1. (구체적 개선안)

---
```

---

## Phase 3: 보충 검사

모든 인터랙션 스텝 완료 후 아래 보충 검사를 순서대로 실행한다.
각 검사 결과는 리포트의 `## 미적·구조 감사` 섹션에 누적 기록한다.

---

### 3-A. 접근성 점검
```javascript
// mcp__claude-in-chrome__javascript_tool
const issues = [];
document.querySelectorAll('button').forEach(btn => {
  if (!btn.textContent.trim() && !btn.getAttribute('aria-label') && !btn.getAttribute('title'))
    issues.push({type: 'button-no-label', el: btn.outerHTML.slice(0, 100)});
});
document.querySelectorAll('input, select, textarea').forEach(inp => {
  const id = inp.id;
  if (!id || !document.querySelector(`label[for="${id}"]`))
    issues.push({type: 'input-no-label', el: inp.outerHTML.slice(0, 100)});
});
JSON.stringify(issues.slice(0, 10));
```

---

### 3-B. 타이포그래피 감사

**목표**: 폰트 종류·크기·굵기·줄간격의 일관성 및 위계 검증

```javascript
// mcp__claude-in-chrome__javascript_tool
const tags = ['h1','h2','h3','h4','p','span','button','label','a'];
const result = {};
tags.forEach(tag => {
  const el = document.querySelector(tag);
  if (!el) return;
  const s = window.getComputedStyle(el);
  result[tag] = {
    fontFamily: s.fontFamily.split(',')[0].trim(),
    fontSize:   s.fontSize,
    fontWeight: s.fontWeight,
    lineHeight: s.lineHeight,
    letterSpacing: s.letterSpacing,
    textTransform: s.textTransform,
  };
});
JSON.stringify(result, null, 2);
```

**평가 기준**:
- 폰트 패밀리가 3종 이상이면 Medium 이슈
- h1→h2→h3 font-size 비율이 1.2 미만(너무 촘촘)이면 Low 이슈
- body 폰트 크기가 14px 미만이면 High 이슈 (가독성)
- line-height가 1.4 미만이면 Medium 이슈
- 전체 페이지에서 쓰이는 font-weight 종류가 5개 초과면 Low 이슈

---

### 3-C. 색상 팔레트 & 대비 감사

**목표**: 실제 사용 색상 목록 추출, 대비비 계산, 팔레트 일관성 확인

```javascript
// mcp__claude-in-chrome__javascript_tool — 색상 수집 (성능: 최대 500요소 샘플링)
const colorSet = new Set();
const allEls = [...document.querySelectorAll('*')].slice(0, 500);
allEls.forEach(el => {
  const s = window.getComputedStyle(el);
  ['color','backgroundColor','borderColor','outlineColor'].forEach(prop => {
    const v = s[prop];
    if (v && v !== 'rgba(0, 0, 0, 0)' && v !== 'transparent') colorSet.add(v);
  });
});
JSON.stringify({ totalSampled: allEls.length, colors: [...colorSet].slice(0, 30) });
```

```javascript
// mcp__claude-in-chrome__javascript_tool — 주요 텍스트 대비비 계산
function luminance(r, g, b) {
  return [r,g,b].map(c => {
    c /= 255;
    return c <= 0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4);
  }).reduce((acc,c,i) => acc + c * [0.2126,0.7152,0.0722][i], 0);
}
function contrast(c1, c2) {
  const L1 = Math.max(luminance(...c1), luminance(...c2));
  const L2 = Math.min(luminance(...c1), luminance(...c2));
  return ((L1+0.05)/(L2+0.05)).toFixed(2);
}
function parseRgb(str) {
  const m = str.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  return m ? [+m[1],+m[2],+m[3]] : null;
}
const pairs = [];
document.querySelectorAll('p, h1, h2, h3, button, a, label').forEach(el => {
  const s = window.getComputedStyle(el);
  const fg = parseRgb(s.color);
  const bg = parseRgb(s.backgroundColor);
  if (fg && bg && bg.some(v => v > 0)) {
    pairs.push({ tag: el.tagName, fg: s.color, bg: s.backgroundColor, ratio: contrast(fg, bg) });
  }
});
JSON.stringify([...new Map(pairs.map(p=>[p.ratio+p.tag, p])).values()].slice(0, 10), null, 2);
```

**평가 기준**:
- 수집된 색상이 12개 초과면 팔레트 과다 → Low 이슈
- 대비비 < 4.5:1 (WCAG AA 본문) → High 이슈
- 대비비 < 3:1 (WCAG AA 대형 텍스트 18px+) → Medium 이슈
- 대비비 < 7:1 (WCAG AAA) 이면 권고로만 기록

---

### 3-D. 간격·여백 일관성 감사

**목표**: padding/margin/gap 값이 디자인 토큰(4px 배수 등)을 따르는지 확인

```javascript
// mcp__claude-in-chrome__javascript_tool
const spacings = new Set();
document.querySelectorAll('div, section, article, main, aside, header, footer, nav').forEach(el => {
  const s = window.getComputedStyle(el);
  ['paddingTop','paddingRight','paddingBottom','paddingLeft',
   'marginTop','marginRight','marginBottom','marginLeft','gap','rowGap','columnGap'].forEach(p => {
    const v = parseFloat(s[p]);
    if (v > 0) spacings.add(v);
  });
});
const arr = [...spacings].sort((a,b)=>a-b);
// 4px 그리드 위반 탐지
const violations = arr.filter(v => v % 4 !== 0);
JSON.stringify({ allSpacings: arr, gridViolations: violations });
```

**평가 기준**:
- 4px 배수 위반 값이 3개 이상이면 Medium 이슈 (디자인 토큰 미사용)
- 사용된 여백 값 종류가 15개 초과면 Low 이슈 (일관성 부재)
- margin: auto 없이 요소가 좌우 치우쳐 있으면 Low 이슈

---

### 3-E. 레이아웃·컨테이너 구조 감사

**목표**: div 중첩 깊이, 레이아웃 방식(flex/grid), 불필요한 래퍼 탐지

```javascript
// mcp__claude-in-chrome__javascript_tool — DOM 깊이 측정 (성능: 최대 500요소 샘플링)
function maxDepth(el, depth = 0) {
  if (!el.children.length) return depth;
  return Math.max(...[...el.children].map(c => maxDepth(c, depth + 1)));
}
const depth = maxDepth(document.body);

// 레이아웃 방식 분포 (샘플링)
const layoutCounts = { flex: 0, grid: 0, block: 0, inline: 0, other: 0 };
const layoutEls = [...document.querySelectorAll('*')].slice(0, 500);
layoutEls.forEach(el => {
  const d = window.getComputedStyle(el).display;
  if (d.includes('flex')) layoutCounts.flex++;
  else if (d.includes('grid')) layoutCounts.grid++;
  else if (d === 'block') layoutCounts.block++;
  else if (d.includes('inline')) layoutCounts.inline++;
  else layoutCounts.other++;
});

// 빈 div 탐지 (콘텐츠/자식 없는 순수 spacer)
const emptyDivs = [...document.querySelectorAll('div')].filter(
  d => !d.textContent.trim() && d.children.length === 0
).length;

// 단일 자식만 있는 래퍼 div (불필요 중첩 의심)
const singleChildWrappers = [...document.querySelectorAll('div')].filter(
  d => d.children.length === 1 && d.children[0].tagName === 'DIV'
).length;

JSON.stringify({ maxDOMDepth: depth, layoutCounts, emptyDivs, singleChildWrappers });
```

**평가 기준**:
- DOM 최대 깊이 > 20이면 Medium 이슈 (성능·유지보수)
- 빈 div > 5개이면 Low 이슈 (spacer div 남용)
- 단일 자식 래퍼 div > 10개이면 Low 이슈 (불필요 중첩)
- flex/grid 미사용(block만 95%+)이면 Low 이슈 (레이아웃 현대화 필요)

---

### 3-F. 크기·치수 일관성 감사

**목표**: border-radius, border-width, shadow, icon 크기 일관성 확인

```javascript
// mcp__claude-in-chrome__javascript_tool
const radiusSet = new Set();
const shadowSet = new Set();
const borderSet = new Set();

document.querySelectorAll('button, input, select, textarea, [class*="card"], [class*="modal"], [class*="panel"]').forEach(el => {
  const s = window.getComputedStyle(el);
  if (parseFloat(s.borderRadius) > 0) radiusSet.add(s.borderRadius);
  if (s.boxShadow !== 'none') shadowSet.add(s.boxShadow.replace(/[\d.]+px/g, 'Xpx'));
  if (parseFloat(s.borderWidth) > 0) borderSet.add(s.borderWidth);
});

// 버튼 높이 일관성
const btnHeights = [...document.querySelectorAll('button')].map(b => parseFloat(window.getComputedStyle(b).height)).filter(Boolean);
const uniqueHeights = [...new Set(btnHeights)];

// 이미지/아이콘 크기
const imgSizes = [...document.querySelectorAll('img, svg')].map(el => {
  const s = window.getComputedStyle(el);
  return `${Math.round(parseFloat(s.width))}x${Math.round(parseFloat(s.height))}`;
}).filter(s => !s.startsWith('0'));
const uniqueImgSizes = [...new Set(imgSizes)];

JSON.stringify({
  borderRadiusValues: [...radiusSet],
  shadowVariants: shadowSet.size,
  borderWidths: [...borderSet],
  buttonHeights: uniqueHeights,
  imageSizes: uniqueImgSizes.slice(0, 10),
});
```

**평가 기준**:
- border-radius 값 종류 > 4개이면 Low 이슈 (라운딩 불일치)
- box-shadow 패턴 > 3종이면 Low 이슈 (그림자 불일치)
- 버튼 높이 종류 > 3개이면 Medium 이슈 (버튼 크기 비표준화)
- 아이콘 크기 > 5종이면 Low 이슈

---

### 3-G. 모바일 반응형 검사

**뷰포트 리사이즈**: `mcp__claude-in-chrome__resize_window` 도구 사용 (width: 375, height: 812)
- `window.resizeTo()`는 브라우저 보안 정책으로 차단됨 — 반드시 MCP 도구 사용
→ 리사이즈 후 스크린샷 캡처 (`step-XX-mobile-375`)

추가 확인:
```javascript
// mcp__claude-in-chrome__javascript_tool — 가로 스크롤 탐지
JSON.stringify({
  bodyScrollWidth: document.body.scrollWidth,
  windowWidth: window.innerWidth,
  hasHorizontalScroll: document.body.scrollWidth > window.innerWidth,
  overflowingEls: [...document.querySelectorAll('*')]
    .filter(el => el.getBoundingClientRect().right > window.innerWidth)
    .map(el => el.tagName + '.' + el.className.split(' ')[0])
    .slice(0, 5)
});
```

**평가 기준**:
- 가로 스크롤 발생이면 High 이슈
- 요소가 viewport 밖으로 삐져나오면 High 이슈
- 터치 타겟(버튼·링크) < 44×44px이면 Medium 이슈

---

### 3-H. 애니메이션·트랜지션 과다 확인

```javascript
// mcp__claude-in-chrome__javascript_tool
const anims = document.getAnimations();
const transitions = [...document.querySelectorAll('*')].map(el => {
  const s = window.getComputedStyle(el);
  return { el: el.tagName, transition: s.transition, duration: s.transitionDuration };
}).filter(t => t.transition !== 'all 0s ease 0s' && t.transition !== 'none');

JSON.stringify({
  activeAnimations: anims.map(a => ({
    name: a.animationName || a.id,
    duration: a.effect?.getTiming()?.duration,
    iterations: a.effect?.getTiming()?.iterations
  })).filter(a => a.duration > 300),
  longTransitionCount: transitions.filter(t => parseFloat(t.duration) > 0.4).length,
  infiniteAnimations: anims.filter(a => a.effect?.getTiming()?.iterations === Infinity).length,
});
```

**`prefers-reduced-motion` 지원 여부 확인** (2단계):

1단계 — JS로 런타임 확인:
```javascript
// mcp__claude-in-chrome__javascript_tool
const mqSupported = window.matchMedia('(prefers-reduced-motion: reduce)').matches !== undefined;
// 시뮬레이션: reduced-motion 시 애니메이션이 줄어드는지 확인
const beforeCount = document.getAnimations().length;
// CSS에서 @media (prefers-reduced-motion) 사용 여부는 stylesheet에서 확인
const hasRule = [...document.styleSheets].some(sheet => {
  try {
    return [...sheet.cssRules].some(r => r.conditionText?.includes('prefers-reduced-motion'));
  } catch(e) { return false; } // CORS 차단된 외부 stylesheet 무시
});
JSON.stringify({ mqSupported, activeAnimations: beforeCount, cssRuleFound: hasRule });
```

2단계 — 소스코드에서 확인:
```
Grep: pattern="prefers-reduced-motion", glob="*.{css,scss,tsx,ts,jsx,js}", path="src/", output_mode="count"
```
→ 매치 0건이면 미처리로 판정

**평가 기준**:
- 무한 반복 애니메이션 > 2개이면 Medium 이슈 (주의 분산)
- 트랜지션 duration > 400ms인 요소 > 5개이면 Low 이슈 (체감 느림)
- `prefers-reduced-motion` CSS 규칙 0건 + 소스코드 매치 0건이면 High 이슈 (접근성)

---

## Phase 4: 리포트 완성

모든 스텝과 보충 검사 결과를 종합해 최종 요약 섹션을 `Edit` 도구로 리포트에 추가:

```markdown
---

## 미적·구조 감사 결과

### 타이포그래피
| 항목 | 측정값 | 판정 |
|------|--------|------|
| 폰트 패밀리 | (측정값) | ✅ / ⚠️ / ❌ |
| body 폰트 크기 | (px) | ✅ / ⚠️ / ❌ |
| 줄간격 | (측정값) | ✅ / ⚠️ / ❌ |
| 제목 위계 비율 | (h1/h2/h3) | ✅ / ⚠️ / ❌ |

### 색상 팔레트
| 항목 | 측정값 | 판정 |
|------|--------|------|
| 총 색상 수 | N종 | ✅ / ⚠️ / ❌ |
| 최저 대비비 | N:1 | ✅ / ⚠️ / ❌ |
| WCAG AA 위반 요소 | N개 | ✅ / ⚠️ / ❌ |

### 여백·간격
| 항목 | 측정값 | 판정 |
|------|--------|------|
| 4px 그리드 위반 | N개 | ✅ / ⚠️ / ❌ |
| 사용 간격 값 종류 | N종 | ✅ / ⚠️ / ❌ |

### 레이아웃·구조
| 항목 | 측정값 | 판정 |
|------|--------|------|
| 최대 DOM 깊이 | N | ✅ / ⚠️ / ❌ |
| 빈 div 수 | N개 | ✅ / ⚠️ / ❌ |
| 단일자식 래퍼 | N개 | ✅ / ⚠️ / ❌ |
| 레이아웃 방식 | flex/grid/block | ✅ / ⚠️ / ❌ |

### 치수 일관성
| 항목 | 측정값 | 판정 |
|------|--------|------|
| border-radius 종류 | N종 | ✅ / ⚠️ / ❌ |
| box-shadow 패턴 | N종 | ✅ / ⚠️ / ❌ |
| 버튼 높이 종류 | N종 | ✅ / ⚠️ / ❌ |

### 모바일·애니메이션
| 항목 | 결과 | 판정 |
|------|------|------|
| 가로 스크롤 발생 | 있음/없음 | ✅ / ❌ |
| 무한 반복 애니메이션 | N개 | ✅ / ⚠️ / ❌ |
| prefers-reduced-motion | 처리/미처리 | ✅ / ❌ |

---

## 종합 요약

### 점수판

| 카테고리 | 점수 | 비고 |
|----------|------|------|
| 🎯 인터랙션 피드백 | N/10 | (한 줄 평가) |
| ♿ 접근성 | N/10 | (한 줄 평가) |
| 🚨 에러 처리 | N/10 | (한 줄 평가) |
| 🎨 타이포그래피 | N/10 | (한 줄 평가) |
| 🌈 색상·대비 | N/10 | (한 줄 평가) |
| 📐 여백·간격 | N/10 | (한 줄 평가) |
| 🧱 레이아웃·구조 | N/10 | (한 줄 평가) |
| 📏 치수 일관성 | N/10 | (한 줄 평가) |
| 📱 반응형 | N/10 | (한 줄 평가) |
| ✨ 마이크로인터랙션 | N/10 | (한 줄 평가) |

**총점: N/100**

### 이슈 분류

| 레벨 | 건수 |
|------|------|
| 🔴 Critical | N |
| 🟠 High | N |
| 🟡 Medium | N |
| 🟢 Low | N |

### Top 5 이슈

1. 🔴 **[이슈명]** — [한 줄 설명] — `src/path/file.tsx:line`
2. 🟠 **[이슈명]** — [한 줄 설명] — `src/path/file.tsx:line`
3. 🟠 **[이슈명]** — [한 줄 설명] — `src/path/file.tsx:line`
4. 🟡 **[이슈명]** — [한 줄 설명] — `src/path/file.tsx:line`
5. 🟡 **[이슈명]** — [한 줄 설명] — `src/path/file.tsx:line`

### Quick Wins (30분 이내)

- [ ] `src/components/X.tsx`: (구체적 수정 내용)
- [ ] CSS: 4px 그리드 위반 여백 수정 — `margin: 13px` → `margin: 12px`
- [ ] CSS: body font-size 14px → 16px
- [ ] CSS: `prefers-reduced-motion` 미디어 쿼리 추가
- [ ] HTML: 아이콘 버튼에 `aria-label` 추가

### 큰 개선사항 (디자인 결정 필요)

- [ ] 디자인 토큰 시스템 도입 (색상·간격·타이포그래피 변수화)
- [ ] 스켈레톤 로딩 상태 구현
- [ ] 에러 바운더리 + 사용자 친화적 fallback UI
- [ ] 색상 팔레트 축소 및 브랜드 가이드 정의

---
*Generated by ui-walkthrough skill — [timestamp]*
```

리포트 저장 확인:
```bash
ls -lh $PROJECT_ROOT/ui-audit/
ls -lh $PROJECT_ROOT/ui-audit/screenshots/
```

완료 후 사용자에게 보고:
- 리포트 파일 경로
- 발견된 이슈 수 (Critical/High/Medium/Low 분류)
- Top 3 Quick Wins

---

## 종합 평가 기준표

### UX 인터랙션 (기능/행동)

| 차원 | 체크 항목 | 심각도 기준 |
|------|-----------|-------------|
| 피드백 반응성 | 100ms 내 시각적 반응? | 없으면 High |
| 로딩 상태 | 비동기 작업에 스피너/스켈레톤? | 없으면 Medium |
| 에러 상태 | 에러 메시지 명확 + 복구 안내? | 없으면 High |
| 포커스 관리 | 키보드 포커스 논리적 흐름? | 모달 트랩 없으면 High |
| 빈 상태 | 빈 데이터 상태 처리? | 없으면 Medium |
| 마이크로인터랙션 | hover/active/focus 상태 존재? | 없으면 Low |
| 터치 타겟 | 모바일 44×44px 이상? | 미달 시 Medium |

### 미적 품질 (시각/디자인)

| 차원 | 체크 항목 | 심각도 기준 |
|------|-----------|-------------|
| **색상 대비** | WCAG AA 기준 (4.5:1) 충족? | 미충족 시 High |
| **팔레트 절제** | 전체 색상 ≤12종? | 초과 시 Low |
| **타이포그래피 위계** | h1>h2>h3 크기 비율 ≥1.2? body ≥14px? | 미달 시 High/Low |
| **폰트 일관성** | 폰트 패밀리 ≤2종? weight 종류 ≤4? | 초과 시 Low |
| **줄간격** | line-height ≥1.4? | 미달 시 Medium |
| **여백 그리드** | padding/margin 4px 배수 준수? | 위반 ≥3개이면 Medium |
| **여백 일관성** | 사용 간격 값 ≤15종? | 초과 시 Low |
| **border-radius 통일** | 라운딩 값 ≤4종? | 초과 시 Low |
| **그림자 통일** | box-shadow 패턴 ≤3종? | 초과 시 Low |
| **버튼 크기 표준화** | 버튼 높이 ≤3종? | 초과 시 Medium |
| **레이아웃 현대성** | flex/grid 활용? (block 전용 지양) | 미사용 시 Low |
| **DOM 깊이** | 최대 중첩 ≤20? | 초과 시 Medium |
| **불필요 래퍼** | 빈 div ≤5개, 단일자식 래퍼 ≤10개? | 초과 시 Low |
| **가로 스크롤** | 모바일에서 가로 오버플로 없음? | 발생 시 High |
| **애니메이션 절제** | 무한 반복 ≤2개, 긴 트랜지션 ≤5개? | 초과 시 Medium |
| **동작 감소 지원** | prefers-reduced-motion 처리? | 미처리 시 High |
| **아이콘 크기 통일** | 아이콘 크기 ≤5종? | 초과 시 Low |

### 심각도 정의

| 레벨 | 정의 |
|------|------|
| **Critical** | 핵심 기능 사용 불가 |
| **High** | 심각한 사용자 마찰 또는 접근성 위반 |
| **Medium** | 우회 가능하지만 UX·가독성 저하 |
| **Low** | 폴리시·세련도·일관성 이슈 |

---

## 예외 처리

| 상황 | 처리 방법 |
|------|-----------|
| 로그인 필요 | 사용자에게 크리덴셜 확인 후 진행 또는 로그인 플로우도 감사 범위 포함 |
| SPA 라우팅 | 클릭 후 `window.location.href` JS로 확인, 네비게이션 확인 |
| 12스텝 초과 | 관련 인터랙션 그루핑, 주요 플로우 우선 |
| 소스코드 없음 (빌드된 앱) | 코드 참조 생략, 디자인 권고만 기록 |
| GIF 녹화 요청 | `mcp__claude-in-chrome__gif_creator` 사용, 스텝 중 적절히 프레임 삽입 |
| alert/confirm 다이얼로그 발생 | 사용자에게 경고, JS로 사전 패치 시도 |

---

## 검증 체크리스트

감사 완료 후 확인:
- [ ] `ui-audit/` 폴더에 `.md` 리포트 파일 존재
- [ ] `ui-audit/screenshots/` 에 각 스텝 PNG 파일 존재
- [ ] 리포트에서 `![Step N](screenshots/...)` 이미지 링크 올바름
- [ ] 코드 참조 (`src/components/...`) 경로가 실제 파일과 일치
- [ ] Quick Wins 섹션이 실행 가능한 수준으로 구체적
- [ ] 종합 UX 점수 및 Top 3 이슈 기록 완료
