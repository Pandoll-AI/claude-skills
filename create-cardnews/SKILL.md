---
name: create-cardnews
description: Convert Korean or English articles, reports and research into evidence-checked, mobile-readable 1122×1402 card-news carousels. Use for 카드뉴스, 인스타그램 캐러셀, 논문·블로그 카드 요약, metric comparison infographics, or a series of shareable visual slides.
---

# Create Cardnews

Turn an article or report into an editorial **series of image cards**, not a generic summary pasted onto pictures. Preserve factual qualifiers, units, denominators and citations. The default style is **navy / yellow / cream**, mobile portrait **1122×1402**; use `scripts/render_cards.py` to generate clean typography and charts with Pillow.

> **Provenance:** Reconstructed from the previously described `create-cardnews` visual guidelines in November 2026. This is not a copy of the unavailable original ZIP. The renderer is a separate reusable implementation.

## When to trigger

- A user asks for 카드뉴스, Instagram/LinkedIn carousel, multi-card explainer, report/academic-paper visual summary, or visual evidence comparison.
- If an image-editing or design service is preferred, comply with the user's selected tool; do not claim the Pillow renderer is a generative image model.

## Workflow

1. **Read the complete source.** Extract the main argument, factual evidence, opposing findings, qualifications and original citations. Respect the source's publication date.
2. **Build an evidence ledger** for all numbers: source URL, benchmark/task, language, model/version, score, unit, evaluator, protocol and critical caveats. Never merge numbers from incompatible studies in the same ranking chart.
3. **Plan 6–10 cards** by default (up to 20): question/cover → context → evidence → limitations/alternatives → deployment → conclusion. Every card must make one claim, not carry a paragraph of unrelated facts.
4. **Polish the Korean copy as editorial prose.** Prefer natural short sentences. Remove exaggerated superlatives, AI-sounding transitions and unsupported causal claims; preserve technical precision. Separate *observed result*, *author's claim*, *interpretation* and *recommendation*.
5. **Choose layouts** from `cover`, `bullets`, `bars`, `table`, `stats`, `conclusion`. Create an editable UTF-8 JSON deck following `examples/medical-llm/deck.json` and the schema below.
6. **Render** by running `python3 scripts/render_cards.py deck.json --output out/`. Use Korean-capable system fonts; none are bundled. Renderer creates numbered PNGs, `preview_contact_sheet.png` and `manifest.json`.
7. **Inspect every card, not only the contact sheet.** Correct spacing, wrapping, font fallback, graph scale, cut-off captions and incorrect numerical labels. Rewrite overlong cards rather than shrinking body text until illegible.
8. **Deliver** PNGs, editable JSON, source links, and a contact sheet. Include a ZIP if requested. Publish to external sites only when expressly asked.

## Design contract

- Canvas: 1122×1402 px, 2× rasterisation then downsampled.
- Palette: navy `#112747`, yellow `#FFC93B`, cream `#FCF9F3`, blue `#2F70CD`; white content panels.
- Legible hierarchy: strong cover headline, 1 short takeaway per card, readable body text (ideally ≥27 px at full resolution), generous margins; 3–5 items per list card.
- Charts must show metric title, scale and exact numbers; sources must appear on the card or in an accompanying citation slide. Icons can be vector-drawn; avoid relying on colourful emoji as text glyphs.
- Medical and other high-stakes content: research scores are not clinical reliability; mention validation boundaries and important failure modes.

## JSON interface

A deck contains `title`, `source`, `date` and `cards`. Every card has `type`, `title`, optional `label` and `source`; additional fields depend on `type`:

| type | fields |
|---|---|
| `cover` | `subtitle` |
| `bullets` | `intro` (optional), `items: [{"head":"...", "body":"..."}]` (max 5) |
| `bars` | `metric`, `max` (default 100), `bars: [{"name":"...", "value":89.53}]` (max 6), `note` |
| `table` | `headers` (2–3), `rows` (max 6), `note` |
| `stats` | `stats: [{"name":"...", "value":"98%", "detail":"..."}]` (max 4), `note` |
| `conclusion` | `points` (max 4), `note` |

## Run

```bash
python3 -m pip install -r requirements.txt
python3 scripts/render_cards.py examples/medical-llm/deck.json --output output/medical-llm
```

For custom fonts, pass `--font /path/to/Regular.ttf --font-bold /path/to/Bold.ttf`. Supported defaults include Noto Sans CJK (Linux), Apple SD Gothic Neo (macOS), and Malgun Gothic (Windows).

## Non-negotiable accuracy checks

- Do not present cross-study benchmark scores as a head-to-head ranking.
- State numerator/denominator, aggregation, units and protocol when needed to interpret percentages.
- **KTAS “within one level agreement 98%” is not “98% exact accuracy”**; a clinically important one-step under-triage could still be counted as agreement.
- Verify names, dates, model versions, licences and external claims against source evidence. Never fabricate local test results.
- Avoid exporting private patient information or distributing fonts with the repository or archive.