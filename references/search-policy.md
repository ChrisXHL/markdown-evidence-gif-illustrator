# Search Policy

Search is **on-demand**, not mandatory. But once search is needed, **provenance tracing is mandatory**.

## When to search
Search only when it improves precision enough to complete the user goal:
- the article has no useful links
- source credibility is too weak
- a paragraph references a product, concept, workflow, or data point that needs an external visual anchor
- the article mentions something readers should see, but the article does not provide a usable visual
- the article cites a claim, but not the original source behind that claim

## Priority: trace back to the origin
Do not stop at the first seemingly authoritative result.
Prefer the highest-upstream usable source:
1. Original / official / primary source
2. Direct relay that clearly cites the upstream original source
3. Reputable media or expert explainers
4. Community discussion only as fallback, and label it clearly

## Search output requirements
When search occurs, record in `sources.md`:
- query used
- selected source title
- selected source URL
- source tier
- upstream source title/URL if traced
- provenance status: direct / traced_to_upstream / unresolved
- why this source was chosen
- why other candidates were rejected
- any conflicts or uncertainty

Follow `provenance-rules.md` for the full tracing standard.

## Stop conditions
Stop searching when you have enough evidence to:
- justify the illustration anchor
- choose the visual type
- name a concrete source page to record or reference
- explain the provenance status honestly

Do not search broadly once the target is good enough and the evidence chain is explicit.
