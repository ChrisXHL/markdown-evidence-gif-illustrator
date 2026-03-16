# Workflow

## Phase 1 — Prepare package
1. Read the Markdown article.
2. Create a sibling package folder beside the article:
   - `<article_stem>__illustration_package/`
3. Clone the article into the package as `<article_stem>.annotated.md`.
4. Create:
   - `assets/images/`
   - `assets/gif/`
   - `illustration-plan.md`
   - `matches.yaml`
   - `sources.md`

Use:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/create_article_package.py <article.md>
```

## Phase 2 — Select illustration anchors
Choose only positions where visuals materially improve understanding:
- abstract concepts
- dense product/UI explanations
- data-heavy claims
- process steps
- comparisons or before/after claims

Prefer at least 5 anchors by default when the article has enough substance.
If the first pass yields fewer than 5 strong anchors, keep searching for secondary-but-still-useful evidence positions until you reach 5, unless the article is genuinely too short or the extra visuals would be repetitive.
Skip trivial decorative image suggestions.
For each selected anchor, default output format should be `static_hd_adaptive`.
Only mark it as `gif` if one frame is unlikely to fit the needed source evidence.

## Phase 3 — Decide whether search is needed
Do **not** search automatically for every paragraph.
Search only when one of these is true:
- the article lacks source links
- the claim needs stronger grounding before choosing a visual
- the visual target is unclear from article text alone
- the best explanatory asset likely lives on an external official page
- the article cites a statement but not its original source

Follow `search-policy.md`.
When search is triggered, prioritize **provenance tracing**:
1. find the most upstream usable source
2. distinguish original source vs relay source
3. record whether tracing is complete, partial, or unresolved
4. use PinchTab execution flow when available

Generate provenance-first query variants:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/generate_provenance_queries.py \
  ./matches.yaml ./provenance-queries.json
```

Bootstrap source records for all anchors:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/bootstrap_sources_from_matches.py \
  ./matches.yaml ./sources.md
```

If needed, initialize a single source record template:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/init_source_record.py \
  ./sources.md --anchor-id anchor-01 --claim "why this paragraph needs a visual"
```

For full search execution guidance, use `pinchtab-provenance-playbook.md`.

## Phase 4 — Build matches
Create structured records for each chosen anchor:
- heading
- quoted_text
- need_image_reason
- visual_type
- preferred_format
- search_query
- source_url
- source_title
- source_tier
- upstream_source_url
- upstream_source_title
- provenance_status
- asset_path
- insertion_mode

Use `matches.yaml` as the source of truth.

## Phase 5 — Capture the visual asset
Default path: capture a **HD static screenshot** from the selected source page.
Use adaptive ratio by default, and only use 16:9 when it does not harm information completeness.
Use GIF only if the source evidence spans multiple screens or requires dynamic reveal.

Before capturing a static screenshot, explicitly verify readiness:
- the target text / selector is visible
- page rendering has stabilized enough for the needed evidence
- the screenshot includes a visible highlight/pointer when the reader needs help locating the key sentence or number

Preferred static capture flow:
1. open page
2. wait for dom + network stabilization when possible
3. wait for target text/selector visibility
4. scroll target into view
5. add visible highlight/pointer to the evidence region
6. prefer subtle marker/underline highlighting for text evidence; reserve box-style highlights for blocks/UI
7. keep screenshots visually clean by default: no on-image text label, no pointer dot, unless the user asks for them
8. keep capture aspect within the package policy range: default near 16:9, expandable only up to 16:16 when needed for completeness
9. capture the focused evidence region with enough context to remain trustworthy
10. if the page is blocked or unreadable, switch to a more usable upstream/source-tier page and document the reason

Decision rule:
- single-frame evidence fits -> static HD image in `assets/images/`
- single-frame evidence fits and 16:9 still preserves key information -> optional `static_hd_16_9`
- single-frame evidence does not fit -> GIF in `assets/gif/`

If GIF recording is required and there is a renderable page target:
1. Render starter config from `matches.yaml`
2. Refine step details for the actual page
3. Validate before recording
4. Record only the selected clips

Starter command:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/render_webreel_config.py \
  ./matches.yaml ./webreel.config.json --url https://example.com
```

Then use the `webreel-recorder` skill workflow:
- scaffold/config edit
- validate
- record

## Phase 6 — Insert visuals into Markdown
Insert after the matching paragraph, not before.
Use relative paths only.
Support two insertion modes:
- `image_only`
- `explanation_and_image` (default)

Use:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/insert_gifs_into_markdown.py \
  ./article.annotated.md ./matches.yaml
```

## Phase 7 — Final delivery
Return:
- package root path
- annotated markdown path
- generated static image and/or GIF paths
- total inserted visual count
- unresolved ambiguity, if any
- sources used, if search happened
