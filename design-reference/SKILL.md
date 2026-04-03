---
name: design-reference
description: 디자인 스타일 카탈로그 & 레퍼런스. 115개 디자인을 키워드로 분류. UI/프론트엔드 작업 시 적합한 디자인 스타일을 매칭하고 제안합니다. "디자인 추천", "어떤 스타일", "design reference", "스타일 찾기" 등의 요청 시 사용하세요.
---

# Design Reference Catalog

유저가 UI/프론트엔드 디자인을 요청할 때, 이 카탈로그에서 키워드 매칭으로 적합한 스타일을 제안한다.

## 사용법

1. 유저 요청에서 키워드를 추출 (예: "dark developer tool" → dark, developer, tool)
2. `+positive` 키워드가 겹치는 디자인을 찾고, `-negative`에 해당하는 건 제외
3. [G] 스타일은 프롬프트를 그대로 적용, [B] 스타일은 `design-md/{brand}/design.md` 파일을 fetch해서 토큰/폰트/수치까지 반영
4. 2-3개 후보를 유저에게 제시하고 선택받기

## 소스

- **[G]** = design-prompts-gallery (https://design-prompts-gallery.vercel.app/) — 60개 generic 스타일 프롬프트
- **[B]** = awesome-design-md (https://github.com/VoltAgent/awesome-design-md/) — 55개 브랜드 디자인 시스템, `design-md/{brand}/design.md`로 접근

## 카탈로그: `name | source | +positive | -negative`

### Dark / Noir / Terminal
- Neural Noir Interface | G | +dark +sophisticated +noir +moody | -bright -colorful -playful
- Midnight Editorial | G | +dark +editorial +typography +elegant | -light -casual -rounded
- Cinematic Noir | G | +film-noir +high-contrast +black +dramatic | -minimal -flat -pastel
- Dark Avant-Garde | G | +experimental +artistic +dark +edgy | -corporate -clean -conservative
- Terminal | G | +monospace +cli +hacker +retro-tech | -modern -gradient -visual
- Red Noir | G | +red +black +dramatic +contrast | -soft -neutral -muted
- Deep Red | G | +red +dramatic +bold +intensity | -subtle -pastel -light
- Linear | B | +dark +indigo +precision +engineering +Inter | -warm -rounded -casual
- Framer | B | +dark +seductive +frosted-glass +GT-Walsheim | -warm -light -minimal
- Composio | B | +pitch-black +cyan +bioluminescent +terminal | -warm -cream -organic
- ClickHouse | B | +black +neon-yellow +aggressive +performance | -soft -warm -elegant
- xAI | B | +dark +brutalist +monospace +zero-decoration | -colorful -rounded -playful
- Sentry | B | +dark-purple +lime-green +irreverent +frosted-glass | -corporate -clean -minimal
- Sanity | B | +dark +coral-red +precision +pill-buttons | -light -casual -warm
- SpaceX | B | +pure-black +cinematic +photography +uppercase +DIN | -cards -grid -colorful
- VoltAgent | B | +carbon-black +emerald-glow +command-terminal | -warm -cream -soft

### Warm / Cream / Editorial
- Bold Editorial | G | +editorial +yellow-accent +magazine +typography | -dark -minimal -tech
- Bold Editorial Design | G | +navy +sage +portfolio +editorial | -neon -dark -aggressive
- Superdesign Editorial Waitlist | G | +magazine +sophisticated +typography | -tech -dark -minimal
- Claude | B | +parchment +terracotta +literary +warm +serif | -dark -neon -tech
- Cursor | B | +cream +orange +gothic-display +warm-craft | -dark -cold -minimal
- Lovable | B | +parchment +humanist +analog +notebook | -dark -sharp -corporate
- PostHog | B | +sage-cream +IBM-Plex +anti-corporate +earthy | -dark -polished -luxury
- Zapier | B | +cream +orange +organized +warm-borders +geometric | -dark -cold -brutalist
- Intercom | B | +off-white +orange +editorial +warm +sharp-radius | -dark -cold -rounded
- Clay | B | +cream +multi-color +playful +artisanal +Roobert | -dark -corporate -sharp
- Warp | B | +warm-black +parchment +terminal-lifestyle | -cold -bright -corporate

### Minimalist / Swiss / Clean
- Swiss Style | G | +swiss +grid +geometric +sans-serif +precision | -decorative -gradient -playful
- Flat Design | G | +flat +minimal +no-depth +clean | -3d -shadow -gradient
- Monochrome | G | +single-color +tonal +restrained | -multi-color -vibrant -gradient
- Clean Fluid | G | +flowing +clean +minimal +geometry | -heavy -dark -complex
- Minimalist Beta Capture | G | +minimal +conversion +focused +simple | -decorative -complex -dark
- Cal | B | +monochrome +shadow-depth +Cal-Sans +Inter | -color -gradient -playful
- Ollama | B | +pure-white +grayscale +SF-Pro-Rounded +radical-minimal | -color -dark -complex
- OpenCode | B | +warm-black +monospace-only +terminal-native | -color -rounded -decorative
- Uber | B | +black-white-binary +pill +bold-geometric +billboard | -gradient -soft -complex

### Glassmorphism / Neumorphism / 3D
- Glassmorphism | G | +frosted-glass +transparency +modern +blur | -flat -opaque -retro
- Glassmorphism Card | G | +glass-card +blur +overlay +depth | -flat -solid -minimal
- Neumorphism | G | +soft-3d +embossed +subtle-shadow | -flat -sharp -high-contrast
- Clay UI | G | +3d-clay +tactile +soft +rounded | -flat -sharp -dark

### Brutalist / Neo-Brutalist
- Brutalist E-commerce | G | +raw +industrial +minimal-ornament +heavy-type | -polished -gradient -soft
- Neo-Brutalism | G | +geometric +bold +contemporary-brutalist | -elegant -soft -subtle

### Retro / Nostalgic
- Bold Retro-Modernism | G | +1970s +geometric +bold-pattern +retro | -minimal -modern -dark
- Win98 | G | +windows98 +skeuomorphic +beveled +retro | -modern -flat -minimal
- News Print | G | +newspaper +column +editorial +vintage | -modern -gradient -dark
- Sketch | G | +hand-drawn +sketchy +informal +organic | -polished -precise -corporate

### Futuristic / Tech / SaaS
- Futuristic SaaS | G | +forward-thinking +tech +futuristic | -retro -traditional -warm
- SaaS Landing Page | G | +developer +clean +professional +technical | -artistic -warm -playful
- Chrome Extension Landing | G | +gray +browser +tech +focused | -colorful -bold -artistic
- Tech Editorial | G | +technical +editorial +modern-typography | -warm -retro -playful
- Synapse | G | +neural +tech +interconnected +network | -organic -warm -traditional
- Cyber Serif | G | +serif +cyberpunk +tech +digital | -organic -warm -traditional
- Vercel | B | +white +near-black +shadow-borders +Geist +philosophical-minimal | -warm -colorful -rounded
- Stripe | B | +white +navy +purple +financial-precision +sohne | -casual -warm -playful
- Hashicorp | B | +dual-mode +enterprise +multi-product +token-system | -playful -organic -artistic

### Nature / Organic
- Nature Inspired | G | +organic +natural +earth-tones +botanical | -tech -dark -sharp
- Organic Modern | G | +organic +flowing +contemporary +soft | -geometric -sharp -grid

### Luxury / Premium
- Luxury | G | +premium +elegant +refined +spacing | -casual -cheap -cluttered
- Architectural Type System | G | +typography +precision +architectural | -casual -playful -colorful
- ElevenLabs | B | +white +stone +Waldenburg-light +whisper-thin +premium | -bold -dark -heavy
- Superhuman | B | +white +deep-purple +lavender +luxury-envelope | -casual -dark -playful
- Apple | B | +white +light-gray +SF-Pro +cinematic +reductive | -busy -dark-first -colorful
- BMW | B | +white +BMW-blue +industrial-precision +zero-radius | -playful -rounded -casual
- Revolut | B | +near-black +white +Aeonik-Pro +billboard-scale +pill | -decorative -warm -soft

### Vibrant / Energetic / Playful
- Neon Velocity Countdown | G | +neon +vibrant +product-launch +energy | -subtle -minimal -traditional
- Kinetic Orange | G | +orange +dynamic +motion +energy | -static -dark -minimal
- Hyper-Saturated Fluid | G | +vibrant +fluid +abstract +saturated | -muted -minimal -structured
- Playful | G | +whimsical +friendly +approachable +fun | -serious -dark -corporate
- Kinetic | G | +motion +dynamic +movement +animated | -static -minimal -traditional
- Bauhaus | G | +geometric +functional +primary-colors +modernist | -decorative -organic -dark
- Replicate | B | +white +orange-red-magenta +festival-poster +massive-type | -subtle -dark -corporate
- Wise | B | +off-white +lime-green +billboard-bold +protest-urgency | -subtle -dark -corporate

### Product / Landing Page
- High Contrast Landing | G | +bold +contrast +high-visibility +conversion | -subtle -muted -soft
- Disruptor Beta Launch | G | +bold +launch +high-contrast +conversion | -subtle -soft -traditional
- Lumina SaaS Landing | G | +yellow +energetic +dynamic +SaaS | -dark -muted -traditional
- Modern Bold | G | +contemporary +bold +strong-contrast | -retro -subtle -minimal

### Industrial / Architectural
- Warm Industrial Gray | G | +industrial +warm +gray +neutral | -vibrant -colorful -playful
- Architectural Blueprint | G | +blueprint +technical-drawing +schematic | -colorful -organic -soft
- Tectonic | G | +geometric +layered +structural +plate-like | -organic -soft -fluid
- Liquid Metal | G | +metallic +reflective +flowing +mercury | -matte -flat -organic

### Digital Wellness / Soft
- Softly Digital Wellness | G | +soft +wellness +mobile +calming | -bold -dark -aggressive
- BabyBites | G | +refined +mobile +elegant +sophisticated | -harsh -dark -aggressive

### Grunge / Collage
- Grunge Collage Motion | G | +distressed +texture +dynamic +raw | -clean -minimal -polished

### Brand-Specific (Additional)
- Airbnb | B | +white +red +warm +card-grid +photography +marketplace | -dark -minimal -tech
- Airtable | B | +white +navy +blue +swiss +enterprise +clean | -dark -playful -artistic
- Cohere | B | +white +blue +purple +enterprise +rounded-cards | -dark -casual -playful
- Coinbase | B | +white +blue +financial +trustworthy +pill-buttons | -playful -warm -artistic
- Expo | B | +off-white +black +Inter +pill +developer-premium | -warm -colorful -playful
- Figma | B | +black-white +vibrant-gradients +figmaSans +gallery | -warm -traditional -corporate
- IBM | B | +white +gray +blue +carbon-design +corporate +8px-grid | -playful -organic -warm
- Kraken | B | +white +purple +professional-crypto +trustworthy | -playful -warm -casual
- Minimax | B | +white +blue +pink +multi-font +app-gallery | -dark -minimal -brutalist
- Mintlify | B | +white +green +Inter +atmospheric +documentation | -dark -bold -aggressive
- Miro | B | +white +pastel +coral +teal +collaborative +Roobert | -dark -sharp -aggressive
- Mistral | B | +golden-amber +warm-luxury +European +zero-radius | -cold -dark -tech
- MongoDB | B | +dark-teal +neon-green +dual-mode +bioluminescent | -warm -cream -soft
- Notion | B | +white +warm-neutral +analog +paper-like +NotionInter | -dark -bold -flashy
- Nvidia | B | +black +green-accent +industrial +precision | -warm -soft -playful
- Pinterest | B | +warm-white +red +olive +rounded +craft-browsing | -dark -sharp -tech
- Raycast | B | +near-black +red +macOS-native +swiss +keyboard | -warm -rounded -casual
- Resend | B | +pure-black +icy-blue +serif-hero +crystalline +gallery | -warm -casual -bright
- RunwayML | B | +black +cool-gray +cinematic +full-bleed +invisible-UI | -warm -cards -colorful
- Spotify | B | +near-black +green +immersive +pill +album-art | -light -corporate -minimal
- Supabase | B | +dark +emerald +developer +pill-CTA +code-editor | -warm -light -playful
- Together.AI | B | +white +pastel-gradient +pink-blue +geometric-modernist | -dark -aggressive -heavy

### Material Design
- Material Design | G | +material +layered +surfaces +elevation | -flat -brutalist -retro
