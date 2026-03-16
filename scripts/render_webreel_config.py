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


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a starter webreel config from match anchors.")
    parser.add_argument("matches", help="Path to matches.yaml")
    parser.add_argument("output", help="Path to webreel.config.json")
    parser.add_argument("--url", required=True, help="Target page URL")
    parser.add_argument("--viewport", default="1080x1350", help="Viewport WIDTHxHEIGHT")
    args = parser.parse_args()

    matches_path = Path(args.matches).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    width, height = [int(x) for x in args.viewport.lower().split("x", 1)]

    videos = []
    for index, match in enumerate(parse_matches(matches_path), start=1):
        gif_path = match.get("gif_path") or f"assets/gif/{index:02d}.gif"
        quoted = match.get("quoted_text", "")
        steps = [
            {"action": "goto", "url": args.url},
            {"action": "wait", "ms": 1200},
            {"action": "scrollToText", "text": quoted},
            {"action": "wait", "ms": 600},
            {"action": "highlightText", "text": quoted},
            {"action": "wait", "ms": 900},
        ]
        videos.append(
            {
                "name": match.get("id") or f"spot-{index:02d}",
                "output": gif_path,
                "steps": steps,
            }
        )

    config = {
        "viewport": {"width": width, "height": height},
        "defaultDelay": 300,
        "videos": videos,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
