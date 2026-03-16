#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def yaml_quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main() -> int:
    parser = argparse.ArgumentParser(description="Build matches.yaml from a JSON list of illustration anchor records.")
    parser.add_argument("input", help="Path to JSON file containing match records")
    parser.add_argument("output", help="Path to matches.yaml")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input JSON not found: {input_path}")

    records = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise SystemExit("Input JSON must be a list of match objects")

    lines = ["matches:"]
    for record in records:
        lines.append("  - id: " + yaml_quote(str(record.get("id", ""))))
        for key in [
            "heading",
            "quoted_text",
            "need_image_reason",
            "image_type",
            "search_query",
            "source_url",
            "source_title",
            "gif_path",
            "anchor_mode",
            "insertion_mode",
        ]:
            value = record.get(key, "")
            lines.append(f"    {key}: {yaml_quote(str(value))}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
