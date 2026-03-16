# PinchTab Provenance Playbook

Use this playbook when external search is required and the goal is not only to find a good page, but to **trace back to the most upstream usable source**.

## Step 1 — Start PinchTab safely
Use the bundled helper from `pinchtab-search-assistant`:

```bash
bash $HOME/.agents/skills/pinchtab-search-assistant/scripts/run_pinchtab_safe.sh
```

## Step 2 — Generate provenance-first queries
From `matches.yaml`, generate query variants that bias toward official/original sources:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/generate_provenance_queries.py \
  ./matches.yaml ./provenance-queries.json
```

Default query strategy includes variants like:
- `official`
- `official docs`
- `source`
- `release notes`
- `report OR dataset OR paper`

## Step 3 — Search with a provenance mindset
For each candidate result, ask:
1. Is this the original source?
2. If not, does it cite or link to the original source?
3. Is the upstream source usable for recording?
4. If I stop here, am I leaving an avoidable evidence gap?

## Step 4 — Record source chain
Initialize or bootstrap `sources.md` from matches:

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/bootstrap_sources_from_matches.py \
  ./matches.yaml ./sources.md
```

Then fill each source record with:
- selected page
- source tier
- upstream page
- provenance status
- why selected
- why competing pages were rejected

## Step 5 — Choose the recording target separately from the evidence target
Sometimes the best page for **evidence** is not the best page for **recording**.
Examples:
- A PDF report may be the best original source, but an official summary page may be better for GIF recording.
- A release note may prove the claim, while a product page is better to visually explain the interface.

In that case:
- keep the original source in `sources.md`
- record the visual page in `matches.yaml`
- explain the split explicitly

## Minimum quality bar
- At least 3 candidate sources considered if search is performed
- At least 1 original/official source attempted
- Explicit provenance status for every searched anchor
- Conflicts or unresolved gaps logged, not hidden
