---
name: human-writing
description: A minimal Markdown human-writing style harness. Detects whether the input needs only diagnosis or full rewriting, then applies targeted, meaning-preserving edits to reduce AI-like Markdown patterns without over-polishing.
---

# Human Writing Skill

## Purpose

Use this skill when the user asks to make Markdown writing sound less AI-generated, more human, less templated, less over-polished, or more natural while preserving meaning.

The core of this skill is not a generic rewriting prompt. It is a **style harness**:

1. Classify the text and writing context.
2. Detect AI-like styling patterns and protected zones.
3. Decide whether to return a diagnosis only or perform a rewrite.
4. Apply local, controlled edits.
5. Audit meaning, Markdown integrity, and human readability.

The skill should improve writing style, not change the author's argument.

---

## Single Command

This skill is driven by one command only:

```text
/human-writing [input or file path] [optional instructions]
```

Examples:

```text
/human-writing README.md
```

```text
/human-writing "이 글을 더 사람처럼 다듬어줘. 과하게 광고문처럼 만들지는 말고."
```

```text
/human-writing proposal.md tone=public-sector conservative=true
```

Do not expose multiple commands. If the user asks for retry, run the same `/human-writing` command again with the user's new constraint.

---

## Automatic Branching

The command decides between two stages automatically.

### Stage 1 — Style Harness Diagnosis

Use Stage 1 when:

- the user asks to analyse, detect, score, inspect, review, or diagnose;
- the input is very long and rewriting the whole document would be risky;
- the text contains many protected zones such as code, tables, citations, legal clauses, formulas, quoted material, logs, or YAML;
- the user's intent is unclear;
- the text already looks natural and only minor comments are needed.

Stage 1 output:

```markdown
## Human-writing diagnosis

- Decision: diagnosis only / rewrite recommended / no rewrite needed
- Genre: ...
- Risk: low / medium / high
- Main patterns found:
  - ...
- Protected zones:
  - ...
- Recommended rewrite policy:
  - ...
```

Do not rewrite the whole text in Stage 1. You may include 1–3 short before/after examples if useful.

### Stage 2 — Controlled Human Rewrite

Use Stage 2 when:

- the user explicitly asks to rewrite, polish, style, naturalise, humanise, or remove AI-like tone;
- the input is short or medium length;
- the requested scope is clear;
- protected zones can be safely preserved.

Stage 2 output:

```markdown
## Rewritten version

[rewritten Markdown]

## Style notes

- ...
```

For short user messages, emails, paragraphs, posts, and README sections, output the rewritten version first and keep notes brief.

---

## Style Harness Pipeline

### 1. Context Classification

Identify:

- language: Korean, English, mixed;
- genre: README, report, proposal, blog, memo, announcement, social post, documentation, academic note, public-sector text, email-like text, **lecture** (강의 원고, 교안, 슬라이드 스피커노트, 실습 튜토리얼);
- audience: public, internal, technical, executive, academic, general reader;
- tolerance: conservative, moderate, expressive.

Default tolerance is **moderate-conservative**.

For Korean public-sector or bureaucratic documents, preserve formal register and avoid casualisation. Also distinguish completed facts, planned actions, and neutral expected effects.

**If the genre is `lecture`, read `references/lecture.md` before rewriting.** Korean lecture prose
carries a register pattern that generic rules destroy: a 합쇼체 spine with 해요체 mixed in, and the
speech level shifting by function (definition → 합쇼체, transition → question form, instruction →
softened imperative). Flattening it into a single ending style turns a lecture script into a
recitation. That file also lists what must be left to the medium — a slide-note deck needs headings,
a long-form blog post does not.

### 2. Protected Zone Detection

Do not rewrite inside these unless the user explicitly asks:

- fenced code blocks;
- inline code;
- YAML front matter;
- JSON/XML/HTML snippets;
- tables where wording changes could break alignment or semantics;
- URLs and file paths;
- quoted legal/policy text;
- citations, references, DOIs;
- formulas and numbers;
- names, titles, dates, identifiers;
- command examples.

If protected zones dominate the document, choose Stage 1 unless the user gave a precise target section.

### 3. Pattern Detection

Flag patterns only when they are actually present. Do not assume all AI-like writing is bad.

Common Markdown AI-style patterns:

- too many symmetrical headings;
- every section starts with the same explanatory rhythm;
- overuse of bullets where prose would read better;
- repetitive connector phrases such as “핵심은”, “중요한 점은”, “이를 통해”, “in summary”, “the key point is”;
- generic praise or inflated adjectives;
- unnecessary meta-explanation;
- overly clean three-part structures;
- repeated sentence length;
- repeated noun endings in Korean, especially excessive “~함” when not intended;
- vague abstract nouns replacing concrete action;
- too-perfect transitions;
- conclusion that merely restates the introduction;
- Markdown that looks like a template rather than a document.

### 4. Rewrite Policy Selection

Choose one of these policies:

#### Minimal

Use when the text is already good, formal, technical, legal, medical, policy-related, or high-stakes.

Edits:

- remove obvious AI filler;
- vary sentence rhythm slightly;
- reduce repetitive headings or bullets;
- preserve structure.

#### Balanced

Default for most Markdown writing.

Edits:

- merge or split sections where needed;
- convert some bullets into prose;
- add small human transitions;
- remove generic phrasing;
- vary sentence rhythm;
- keep the document's original purpose.

#### Strong

Use only when the user asks for a clearly more human, vivid, conversational, or editorial voice.

Edits:

- reshape section order if needed;
- make the voice more personal or direct;
- simplify template-like structure;
- replace abstract claims with concrete phrasing;
- allow mild asymmetry and imperfection.

Never use Strong for legal, medical, policy, compliance, or official administrative text unless the user explicitly requests it.

### 5. Rewrite Operations

Apply local operations rather than full paraphrase by default:

- delete filler;
- compress repetitive explanations;
- vary sentence openings;
- combine short formulaic bullets;
- split overloaded sentences;
- replace generic transitions with context-specific ones;
- keep key terms stable;
- preserve Markdown semantics;
- leave good sentences alone.

Do not add new claims, facts, citations, dates, risks, promises, or technical details.

### 6. Audit

Before final output, check:

- meaning preserved;
- no new facts introduced;
- Markdown valid;
- protected zones unchanged;
- tone matches genre;
- output is not over-polished;
- the revision does not become more generic than the original.

#### Fidelity checks (compare against the source, item by item)

The rewrite operations in §5 each have a characteristic side effect. Check for them
explicitly rather than trusting a general "meaning preserved" impression:

- **numbers, statistics, units, dates** — identical to the source, character for character;
- **proper nouns** — personal names, product names, model IDs, organisational unit names;
- **text inside double quotes** — a quotation altered by one character is no longer a quotation;
- **legal or regulatory clause citations**;
- **strength of claim** — an assertion must not soften into a hedge, nor a hedge harden into
  an assertion (side effect of `delete filler`);
- **causal and conditional direction** — cause and effect must not swap
  (side effect of `split overloaded sentences`);
- **polarity** — negation must not flip while simplifying double negatives
  (side effect of `compress repetitive explanations`);
- **tense and agent** — who did what must survive
  (side effect of `vary sentence openings` and of unwinding Korean passives:
  "합의가 이루어졌다" → "합의했다" requires knowing who agreed).

If a fidelity check fails, **revert that individual edit** — do not rewrite the document
again. A failed fidelity check is evidence that one operation went too far, not that the
whole pass was wrong.

If the audit fails more broadly, revise again or downgrade to Stage 1 with an explanation.

---

## Output Rules

### For Stage 1

Return diagnosis and recommended policy. Do not rewrite the full text.

### For Stage 2

Return rewritten Markdown first. Then add short notes.

### For Very Long Documents

Do not attempt a full rewrite blindly. Instead:

1. diagnose the whole document;
2. rewrite the highest-impact section;
3. explain how to apply the same harness to the rest.

### For Korean

Prefer natural Korean while preserving the original register.

Avoid replacing all endings with the same formal noun ending. In official Korean, avoid using “~함” as a default neutral ending when it may imply completed action. Prefer context-aware alternatives such as:

- “가능”
- “활용 가능”
- “마련”
- “검토 필요”
- “추진 예정”
- “확인됨” only when actually completed

### For English

Prefer clear, direct English. Avoid corporate filler, generic AI phrases, and over-neat transitions.

---

## Failure Modes to Avoid

- Rewriting everything just because the command was called.
- Making the text more polished but less human.
- Changing factual content.
- Turning formal writing into casual writing.
- Destroying Markdown structure.
- Editing code, commands, citations, or numbers.
- Adding motivational or sales language that was not present.
- Producing a long explanation when the user wanted the revised text.

---

## Minimal Mental Model

Think of this skill as a harness around writing:

```text
input Markdown
→ classify context
→ protect unsafe zones
→ detect style artefacts
→ branch: diagnose or rewrite
→ apply targeted edits
→ audit fidelity and Markdown
→ output
```

The best result is not the most rewritten result. The best result is the smallest set of edits that makes the text feel written by a real person in the right context.
