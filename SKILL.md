---
name: markdown-evidence-gif-illustrator
description: >
  Analyze a Markdown article, find the exact places where a visual aid would improve clarity,
  search and trace back to the most upstream usable source when the article lacks supporting links,
  prefer HD static source screenshots by default, use adaptive ratio when needed so information is
  not cropped away, fall back to GIF only when one frame cannot fully show the needed evidence,
  and insert those visuals back into a packaged clone of the
  article. Use when user asks for: 为文章配图, 给 markdown 文章插图, 找文章里需要配图的位置,
  截图配图, 高清截图配图, 静态图配图, 16:9 配图, 录 gif 标注文章重点, 自动搜索权威来源补图, 朔源原始出处,
  追溯信息源头, 把图插回 markdown, 文章可视化解释, article illustration from markdown.
  Also trigger when user mentions: markdown article, 配图位置, authority search, provenance,
  source tracing, screenshot, 16:9, webreel, gif annotation, inserted markdown package. Trigger
  even if the user does not explicitly say “skill”.
---

# Markdown Evidence GIF Illustrator

## Overview

Use this skill to turn a Markdown article into a self-contained illustration package: identify the best places for visual explanation, search only when needed, trace claims and visual evidence back to the most upstream usable source, prefer HD static source screenshots by default, use adaptive aspect ratio when needed to preserve complete information, fall back to GIF only when one frame cannot clearly hold the needed evidence, and insert those visuals back into a cloned Markdown file while preserving the original article.

## Workflow

### 1) Prepare the package first
Always start from the source Markdown path.

Create a sibling package folder beside the article and clone the article into it.
Never modify the original article in place by default.

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/create_article_package.py <article.md>
```

Default package root:

```text
<article_dir>/<article_stem>__illustration_package/
```

Key artifacts:
- `<article_stem>.annotated.md`
- `illustration-plan.md`
- `matches.yaml`
- `sources.md`
- `assets/images/`
- `assets/gif/`

### 2) Select only high-value illustration anchors
Pick the paragraphs or sentences where a visual explanation materially improves understanding.

Good candidates:
- abstract concepts
- process explanations
- UI/product walkthrough text
- dense factual or comparison-heavy passages
- paragraphs that would be clearer with a visual pointer or source page

By default, choose **at least 5 positions** when the article has enough substance to support them.
If the first pass yields fewer than 5 high-quality visuals, continue searching for secondary-but-still-useful evidence anchors until you reach 5, unless the article is genuinely too short or evidence would become repetitive.
Do not add decorative visuals just to make the article look busy.
Default visual choice is:
1. HD static screenshot with adaptive ratio
2. HD static screenshot in 16:9 only if it does not lose key information
3. GIF only if a single frame cannot show the needed evidence clearly.

### 3) Search only when needed — but trace to the source when you do
If the article already includes enough reliable context or links, do not search.
If it lacks evidence or visual targets, perform focused search.

The main goal is not just “find a good link”, but **trace back to the most upstream usable source**.
That means:
1. try to find the original / official / primary source first
2. if you land on a relay article, follow its citations upstream
3. explicitly record whether the final selected page is:
   - `direct` (it is the original/primary source)
   - `traced_to_upstream` (you found a relay page and traced it upward)
   - `unresolved` (you could not fully trace to the origin)

Priority order:
1. official pages / docs / blogs / release notes
2. primary data sources / institutions / papers / reports
3. reputable media or expert explainers that clearly cite the upstream source
4. community discussion only as fallback

Recommended execution path when search is needed:
1. generate provenance-first queries from `matches.yaml`
2. bootstrap `sources.md` source records
3. use PinchTab to search and open candidate pages
4. trace upstream links before finalizing the evidence page
5. record source tier + upstream chain + provenance status in `sources.md`

When search is used, record the chosen source, upstream chain, and reason in `sources.md`. See `references/pinchtab-provenance-playbook.md`.

### 4) Build structured match records
For each selected anchor, record:
- heading
- quoted text
- reason this position needs a visual
- visual type
- preferred format (`static_hd_adaptive` by default, `static_hd_16_9` if suitable, `gif` if needed)
- search query used, if any
- chosen source URL and title
- source tier (`original` / `primary_relay` / `secondary`)
- upstream source URL and title, if traced
- provenance status (`direct` / `traced_to_upstream` / `unresolved`)
- target asset path
- insertion mode

Use `matches.yaml` as the source of truth.
If you already have structured JSON, convert it with:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/build_matches.py <matches.json> <matches.yaml>
```

### 5) Prefer HD static capture; use GIF only when needed
For each selected source page, decide format in this order:
1. `static_hd_adaptive`
2. `static_hd_16_9`
3. `gif`

If one screenshot can clearly show the source evidence, use a static image and save it under `assets/images/`.
Do not force 16:9 if it would crop away key information.

Use GIF only when the evidence spans multiple screens or needs scrolling/dynamic reveal.
If GIF recording is required and you have a renderable page target, render a starter config from the matches:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/render_webreel_config.py \
  ./matches.yaml ./webreel.config.json --url https://example.com
```

Then hand off to the `webreel-recorder` workflow:
1. refine steps for the real page
2. validate config
3. record selected GIFs

Important:
- default to HD static screenshots with adaptive ratio when possible
- before any static capture, verify the target page has actually loaded: wait for visible target text/selector, network idle when possible, and fonts/render stabilization
- static screenshots should prefer focused evidence regions over generic full-page captures when that improves readability
- when a key sentence, figure, or claim is the evidence target, visibly mark it in the screenshot with a clear highlight/pointer instead of leaving readers to guess
- highlights should be informative but non-obscuring: prefer subtle marker/underline styles that keep text readable; use heavy red boxes only when the target is a non-text block or UI region
- on-image text labels should be omitted by default unless the user explicitly wants them; the screenshot itself should stay clean
- pointer dots/cursor dots should also be omitted by default; only keep them when the user explicitly wants a stronger visual pointer
- aspect ratio policy: use 16:9 as the default visual baseline; if more vertical space is needed, expand only within the range `16:9` to `16:16` and do not exceed square-equivalent tallness
- if a source page is blocked by a login wall, subscription wall, or social overlay, do not keep a broken screenshot; switch to a more upstream or more usable source and record the reason
- keep GIF clips short when fallback is necessary
- prefer precise highlight/scroll behavior
- validate before recording
- report exact output paths

Recommended static capture command:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/capture_hd_screenshot.py \
  --url https://example.com \
  --output ./assets/images/01-example.png \
  --text "target evidence text" \
  --ready-text "target evidence text" \
  --highlight-text "target evidence text" \
  --highlight-label "关键证据"
```

### 6) Insert visuals back into Markdown
Insert the visual after the target paragraph in the cloned article.
Support both modes:
- `image_only`
- `explanation_and_image` (default)

Use relative paths only.

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/insert_gifs_into_markdown.py \
  ./article.annotated.md ./matches.yaml
```

If anchor matching is ambiguous, stop and verify the anchor instead of inserting into the wrong place.

### 7) Return the package, not just the assets
Final response should report:
- package root path
- annotated Markdown path
- static image and/or GIF file paths
- total inserted visual count
- whether search was used
- provenance status for searched anchors
- any unresolved ambiguity, skipped anchors, or unresolved source-chain gaps

## Outputs

Minimum expected package:

```text
<article_dir>/<article_stem>__illustration_package/
├── <article_stem>.annotated.md
├── illustration-plan.md
├── matches.yaml
├── sources.md
└── assets/
    ├── images/
    │   ├── 01-<slug>.png
    │   └── 02-<slug>.png
    └── gif/
        ├── 01-<slug>.gif
        └── 02-<slug>.gif
```

## Examples

### Example 1

User request:

> 给这篇 Markdown 文章找最需要配图的位置，不够的话自己去搜权威来源，默认做高清静态图，比例按信息完整性来，不够再用 GIF，最后插回文章里，原文别动。

Execution pattern:
1. create package beside article
2. clone original article
3. select at least 5 anchors if the article supports them
4. search only where article evidence is insufficient
5. prefer HD static screenshots first
6. use GIF only for multi-screen or dynamic evidence
7. insert visuals into cloned Markdown
8. return package path and total inserted visual count

### Example 2

User request:

> 这篇文章默认给我做静态图，16:9，不要配图说明，直接用 `![]()`；如果单张图装不下，再退回 GIF，并保留原文件。

Execution pattern:
1. create package
2. prefer static 16:9 visuals
3. fall back to GIF only where single-frame capture is insufficient
4. set insertion mode to `image_only`
5. insert only relative asset links into cloned Markdown
6. return annotated copy path

## Best practices

- Preserve the original Markdown by default.
- Search on demand, not automatically.
- When search happens, prioritize **朔源**: trace to the most upstream usable source instead of stopping at the first decent article.
- Prefer official or primary sources when external evidence is needed.
- Default to **static 16:9 screenshots**.
- Use GIF only when one frame cannot clearly contain the needed source evidence.
- Insert after the target paragraph, not before.
- Use relative paths inside Markdown so the package is portable.
- If no renderable URL/page exists yet, still produce the package and plan first, then request the missing recording target.
- If source evidence conflicts, record the conflict in `sources.md` instead of silently choosing one.
- If the source chain cannot be fully resolved, mark it as `unresolved` rather than pretending certainty.

## References

- `references/workflow.md`
- `references/search-policy.md`
- `references/provenance-rules.md`
- `references/pinchtab-provenance-playbook.md`
- `references/visual-format-policy.md`
- `references/package-layout.md`
- `references/markdown-insertion.md`
