#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def build_queries(match: dict[str, str]) -> list[str]:
    heading = match.get("heading", "").strip()
    quoted = match.get("quoted_text", "").strip()
    base = match.get("search_query", "").strip() or quoted or heading
    tokens = [t for t in [heading, quoted, base] if t]
    joined = " ".join(dict.fromkeys(tokens))
    variants = [
        f'{joined} official',
        f'{joined} official docs',
        f'{joined} source',
        f'{joined} release notes',
        f'{joined} report OR dataset OR paper',
    ]
    return variants


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate provenance-oriented search queries from matches.yaml")
    parser.add_argument("matches", help="Path to matches.yaml")
    parser.add_argument("output", help="Path to output JSON")
    args = parser.parse_args()

    matches = parse_matches(Path(args.matches).expanduser().resolve())
    payload = []
    for match in matches:
        payload.append(
            {
                "id": match.get("id", ""),
                "quoted_text": match.get("quoted_text", ""),
                "need_image_reason": match.get("need_image_reason", ""),
                "queries": build_queries(match),
            }
        )
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
