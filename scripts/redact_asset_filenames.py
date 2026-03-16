#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_assets(package_dir: Path) -> list[tuple[Path, str]]:
    items: list[tuple[Path, str]] = []
    for kind, prefix in (("images", "img"), ("gif", "gif")):
        d = package_dir / "assets" / kind
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if p.is_file() and not p.name.startswith("."):
                items.append((p, prefix))
    return items


def build_mapping(package_dir: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    counters = {"img": 0, "gif": 0}

    for path, prefix in collect_assets(package_dir):
        counters[prefix] += 1
        digest = file_sha256(path)[:8]
        new_name = f"{prefix}-{counters[prefix]:03d}-{digest}{path.suffix.lower()}"
        new_path = path.with_name(new_name)

        if new_path != path:
            path.rename(new_path)

        old_rel = str(path.relative_to(package_dir)).replace("\\", "/")
        new_rel = str(new_path.relative_to(package_dir)).replace("\\", "/")
        mapping[old_rel] = new_rel

    return mapping


def rewrite_file(path: Path, mapping: dict[str, str]) -> bool:
    if not path.exists() or not path.is_file():
        return False

    original = path.read_text(encoding="utf-8")
    updated = original
    for old_rel, new_rel in mapping.items():
        updated = updated.replace(old_rel, new_rel)
        # tolerate './' prefixed markdown links
        updated = updated.replace(f"./{old_rel}", f"./{new_rel}")

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Redact asset filenames in a package by renaming to stable hashed names and updating references."
    )
    parser.add_argument("package_dir", help="Path to <article>__illustration_package directory")
    parser.add_argument("--matches", default="matches.yaml", help="Matches file name or absolute path")
    parser.add_argument("--sources", default="sources.md", help="Sources file name or absolute path")
    parser.add_argument(
        "--annotated",
        default="auto",
        help="Annotated markdown filename, absolute path, or 'auto' to detect *.annotated.md",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).expanduser().resolve()
    if not package_dir.exists():
        raise SystemExit(f"Package dir not found: {package_dir}")

    mapping = build_mapping(package_dir)
    if not mapping:
        print("No assets found under assets/images or assets/gif")
        return 0

    matches_path = Path(args.matches).expanduser().resolve() if Path(args.matches).is_absolute() else package_dir / args.matches
    sources_path = Path(args.sources).expanduser().resolve() if Path(args.sources).is_absolute() else package_dir / args.sources

    annotated_path: Path | None = None
    if args.annotated == "auto":
        cands = sorted(package_dir.glob("*.annotated.md"))
        annotated_path = cands[0] if cands else None
    else:
        annotated_path = Path(args.annotated).expanduser().resolve() if Path(args.annotated).is_absolute() else package_dir / args.annotated

    touched = []
    if rewrite_file(matches_path, mapping):
        touched.append(str(matches_path))
    if rewrite_file(sources_path, mapping):
        touched.append(str(sources_path))
    if annotated_path and rewrite_file(annotated_path, mapping):
        touched.append(str(annotated_path))

    print("Renamed assets:")
    for old_rel, new_rel in sorted(mapping.items()):
        print(f"- {old_rel} -> {new_rel}")

    if touched:
        print("Updated references:")
        for t in touched:
            print(f"- {t}")
    else:
        print("No reference files needed updates")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
