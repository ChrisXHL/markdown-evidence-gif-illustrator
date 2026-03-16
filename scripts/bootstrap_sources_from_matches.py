#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def parse_matches(path: Path) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("  - "):
            if current:
                matches.append(current)
            current = {}
            tail = line[4:]
            if ":" in tail:
                key, value = tail.split(":", 1)
                current[key.strip()] = value.strip().strip('"')
        elif current is not None and line.startswith("    ") and ":" in line:
            key, value = line.strip().split(":", 1)
            current[key.strip()] = value.strip().strip('"')
    if current:
        matches.append(current)
    return matches


def section(match: dict[str, str]) -> str:
    anchor_id = match.get("id", "")
    claim = match.get("need_image_reason", "") or match.get("quoted_text", "")
    query = match.get("search_query", "")
    return f"""## Source Record: {anchor_id}

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
    parser = argparse.ArgumentParser(description="Create sources.md source-record stubs from matches.yaml")
    parser.add_argument("matches", help="Path to matches.yaml")
    parser.add_argument("output", help="Path to sources.md")
    args = parser.parse_args()

    matches = parse_matches(Path(args.matches).expanduser().resolve())
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    content = ["# Sources", ""]
    for match in matches:
        content.append(section(match))
    output.write_text("\n".join(content), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
