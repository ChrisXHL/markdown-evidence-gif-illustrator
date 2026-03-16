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


def make_insert_block(match: dict[str, str], mode: str) -> str:
    alt = match.get("need_image_reason") or match.get("image_type") or "Illustration GIF"
    gif_path = match.get("gif_path", "")
    reason = match.get("need_image_reason", "")
    if mode == "image_only":
        return f"![{alt}]({gif_path})"
    lines = []
    if reason:
        lines.append(f"> 配图说明：{reason}")
        lines.append("")
    lines.append(f"![{alt}]({gif_path})")
    return "\n".join(lines)


def insert_after_anchor(content: str, anchor: str, block: str) -> tuple[str, bool]:
    if not anchor:
        return content, False
    idx = content.find(anchor)
    if idx == -1:
        return content, False
    insert_at = idx + len(anchor)
    return content[:insert_at] + "\n\n" + block + "\n" + content[insert_at:], True


def main() -> int:
    parser = argparse.ArgumentParser(description="Insert GIF markdown blocks into a cloned Markdown article using matches.yaml.")
    parser.add_argument("article", help="Path to cloned markdown article")
    parser.add_argument("matches", help="Path to matches.yaml")
    parser.add_argument("--mode", choices=["image_only", "explanation_and_image", "auto"], default="auto")
    args = parser.parse_args()

    article_path = Path(args.article).expanduser().resolve()
    matches_path = Path(args.matches).expanduser().resolve()
    if not article_path.exists():
        raise SystemExit(f"Article not found: {article_path}")
    if not matches_path.exists():
        raise SystemExit(f"Matches file not found: {matches_path}")

    content = article_path.read_text(encoding="utf-8")
    updated = content
    results = []
    for match in parse_matches(matches_path):
        anchor = match.get("quoted_text", "")
        insertion_mode = match.get("insertion_mode", "")
        mode = args.mode if args.mode != "auto" else (insertion_mode or "explanation_and_image")
        block = make_insert_block(match, mode)
        updated, ok = insert_after_anchor(updated, anchor, block)
        results.append((match.get("id", "?"), ok, anchor[:60]))

    article_path.write_text(updated, encoding="utf-8")
    for match_id, ok, anchor_preview in results:
        status = "INSERTED" if ok else "NOT_FOUND"
        print(f"{status}\t{match_id}\t{anchor_preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
