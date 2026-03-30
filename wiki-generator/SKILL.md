---
name: wiki-generator
description: Generate visual, interactive documentation with diagrams, whiteboards, and editable components. Use when documenting codebases, explaining architecture, creating system diagrams, or building internal team documentation with visual explanations. (project)
---

# Interactive Documentation Generator

## Purpose
Generate concise, visual, educational documentation for codebases. Creates standalone HTML documentation with inline SVG diagrams, styled tables, and clean navigation - viewable with any static server.

## When to Use
- Documenting codebase architecture and design
- Creating system flow diagrams (backend, frontend, data flows)
- Building internal team documentation
- Explaining complex technical concepts visually
- Generating educational documentation for new team members

## Core Principles

### Visual-First Approach
- **MINIMUM 5 visual diagrams** (inline SVG) across documentation
- **MAXIMUM 6 pages total** - be extremely concise
- **MAXIMUM 5K characters per HTML page** - let visuals teach
- Focus on HOW things work, not just WHAT they are

### Documentation Philosophy
- **TEACH, don't describe** - explain WHY and HOW, not just WHAT
- **Write as WE/OUR/US** - first person plural, team teaching team
- **NEVER invent data** - only document what actually exists in the codebase
- **Reference file paths** - connect documentation to actual code files
- **Deep over wide** - prefer nested pages over many siblings

---

## Output Structure

All documentation goes in `/wiki/` at project root:

```
wiki/
├── README.md               # Viewing instructions
├── index.html              # Sidebar layout (Notion-like)
├── styles.css              # Shared styles
├── sidebar-styles.css      # Sidebar-specific styles
├── [project].html          # Main overview page (top tabs)
└── [project]/              # Subpages folder
    ├── architecture.html
    ├── [topic-1].html
    ├── [topic-2].html
    └── ...
```

## Viewing Documentation

```bash
# Start local server
npx serve wiki

# Or Python
cd wiki && python -m http.server 3000
```

Then open:
- **Sidebar view**: `http://localhost:3000` → `index.html` (Notion-like left nav)
- **Simple view**: `http://localhost:3000/[project].html` (top tabs)

Both are **standalone HTML/CSS** - no React/Next.js/Node required.

---

## Two Layout Options

| Layout | Entry | Navigation | Use Case |
|--------|-------|------------|----------|
| **Sidebar** | `index.html` | Left sidebar (256px) | Full documentation browsing |
| **Simple** | `[project].html` | Top tabs | Quick reference, embedding |

---

## File Templates

### 1. README.md
```markdown
# [Project] Wiki

Interactive documentation for the [project] codebase.

## Viewing

\`\`\`bash
npx serve wiki
\`\`\`

Then open:
- Sidebar view: http://localhost:3000
- Simple view: http://localhost:3000/[project].html
```

### 2. styles.css (Shared Styles)
Create with these sections:
- CSS variables (colors, spacing)
- Typography (h1-h6, p, code, blockquote)
- Navigation (top tabs)
- Tables (styled, hover states)
- Cards (grid layout)
- Diagrams (SVG container)
- File trees (monospace)
- Responsive breakpoints
- iframe detection (`.in-iframe` class hides top nav)

### 3. sidebar-styles.css
Create with:
- 256px fixed sidebar
- Notion-like styling (light gray background)
- Hierarchical navigation
- Active state highlighting
- Mobile responsive (slide-out drawer)

### 4. index.html (Sidebar Layout)
Structure:
```html
<body>
  <aside class="sidebar">
    <div class="sidebar-header">[Project]</div>
    <nav class="sidebar-nav">
      <a class="nav-item active" data-page="[project].html">Overview</a>
      <div class="nav-section-title">Documentation</div>
      <a class="nav-item nav-item-nested" data-page="[project]/architecture.html">Architecture</a>
      <!-- More nav items -->
    </nav>
  </aside>
  <main class="main-content">
    <iframe id="content-frame" src="[project].html"></iframe>
  </main>
  <script>/* Navigation handlers */</script>
</body>
```

### 5. Content Pages ([project].html)
Structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Title] - [Project]</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <nav>
    <ul>
      <li><a href="[project].html" class="active">Overview</a></li>
      <li><a href="[project]/architecture.html">Architecture</a></li>
      <!-- More links -->
    </ul>
  </nav>

  <h1>[Title]</h1>
  <p>[Brief description]</p>

  <div class="diagram">
    <svg viewBox="0 0 800 300">
      <!-- Inline SVG diagram -->
    </svg>
    <p class="diagram-caption">[Caption]</p>
  </div>

  <h2>[Section]</h2>
  <table><!-- Data table --></table>

  <!-- More content -->
</body>
</html>
```

---

## Visual Elements

### Inline SVG Diagrams
Use SVG directly in HTML for architecture, flow, and system diagrams:

```html
<div class="diagram">
  <svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg">
    <!-- Boxes -->
    <rect x="50" y="100" width="140" height="80" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
    <text x="120" y="140" text-anchor="middle" font-weight="600" fill="#1e40af">Component</text>

    <!-- Arrows -->
    <defs>
      <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280"/>
      </marker>
    </defs>
    <line x1="190" y1="140" x2="280" y2="140" stroke="#6b7280" stroke-width="2" marker-end="url(#arrow)"/>
  </svg>
  <p class="diagram-caption">System Architecture</p>
</div>
```

**Color palette for boxes:**
- Blue: `fill="#eff6ff" stroke="#3b82f6"` (primary)
- Green: `fill="#f0fdf4" stroke="#22c55e"` (success/agent)
- Yellow: `fill="#fef3c7" stroke="#f59e0b"` (warning/web)
- Purple: `fill="#fae8ff" stroke="#c026d3"` (external/API)
- Gray: `fill="#f3f4f6" stroke="#d1d5db"` (neutral)

### Tables
```html
<table>
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Item</strong></td>
      <td><code>value</code></td>
    </tr>
  </tbody>
</table>
```

### Cards Grid
```html
<div class="grid grid-2">
  <div class="card">
    <div class="card-title">Title</div>
    <p>Description</p>
  </div>
</div>
```

### File Trees
```html
<div class="file-tree">
project/
├── src/
│   ├── index.ts
│   └── utils/
└── package.json
</div>
```

---

## Workflow

### Step 1: Analyze Codebase
1. Explore repository structure
2. Identify top 5-6 key concepts to document
3. Plan visual diagrams for each concept

### Step 2: Create Wiki Structure
```bash
wiki/
├── README.md
├── styles.css
├── sidebar-styles.css
├── index.html
├── [project].html
└── [project]/
    ├── architecture.html
    ├── [topic-1].html
    └── [topic-2].html
```

### Step 3: Create Files in Order
1. `styles.css` - Shared styles first
2. `sidebar-styles.css` - Sidebar styles
3. `[project].html` - Main overview with architecture diagram
4. `[project]/` subpages - One at a time
5. `index.html` - Sidebar layout (references all pages)
6. `README.md` - Viewing instructions

### Step 4: For Each Page
1. Add navigation links
2. Write brief intro paragraph
3. Create inline SVG diagram
4. Add tables/cards for details
5. Reference file paths to code

---

## Critical Rules

1. **MAXIMUM 6 PAGES** - Be selective, combine related topics
2. **MINIMUM 5 SVG DIAGRAMS** - One per major concept
3. **MAXIMUM 5K CHARACTERS PER PAGE** - Let visuals teach
4. **STANDALONE HTML** - No external dependencies, inline SVG
5. **CONSISTENT NAVIGATION** - Same nav on all pages
6. **WRITE AS WE/OUR/US** - First person plural
7. **REFERENCE FILE PATHS** - Connect docs to code

---

## Quick Reference

**Page structure:**
```
<nav> → Top navigation tabs
<h1> → Page title (one per page)
<p> → Brief intro (1-2 sentences)
<div class="diagram"> → SVG diagram
<h2> → Section headings
<table> / <div class="grid"> → Data
<blockquote> → Tips/notes
```

**SVG viewBox:** `viewBox="0 0 800 300"` (width × height)

**Grid classes:** `grid-2` (2 cols), `grid-3` (3 cols)

**Navigation active class:** `class="active"`
