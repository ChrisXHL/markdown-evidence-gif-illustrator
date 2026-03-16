#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """## Source Record: {anchor_id}

- claim_or_visual_need: {claim}
- search_query: {query}
- selected_title: 
- selected_url: 
- source_tier: original
- upstream_source_title: 
- upstream_source_url: 
- provenance_status: unresolved
- why_selected: 
- why_not_other_candidates: 
- usable_for_recording: yes
- uncertainty: 

"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a provenance-oriented source record template to sources.md")
    parser.add_argument("sources", help="Path to sources.md")
    parser.add_argument("--anchor-id", required=True, help="Anchor or match id")
    parser.add_argument("--claim", default="", help="Claim or visual need being traced")
    parser.add_argument("--query", default="", help="Search query used")
    args = parser.parse_args()

    path = Path(args.sources).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("# Sources\n\n", encoding="utf-8")

    with path.open("a", encoding="utf-8") as f:
        f.write(TEMPLATE.format(anchor_id=args.anchor_id, claim=args.claim, query=args.query))

    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
