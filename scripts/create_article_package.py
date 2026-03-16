#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def unique_dir(base: Path) -> Path:
    if not base.exists():
        return base
    index = 2
    while True:
        candidate = base.parent / f"{base.name}-{index}"
        if not candidate.exists():
            return candidate
        index += 1


def display_path(path: Path, *, package_dir: Path | None = None, redact_paths: bool = True) -> str:
    if package_dir is not None:
        try:
            rel = path.relative_to(package_dir)
            return f"./{rel.as_posix()}"
        except ValueError:
            pass

    if not redact_paths:
        return str(path)

    home = Path.home().resolve()
    try:
        rel_home = path.relative_to(home)
        return f"$HOME/{rel_home.as_posix()}"
    except ValueError:
        return f"<redacted:{path.name}>"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a self-contained illustration package beside a Markdown article.")
    parser.add_argument("article", help="Path to the source Markdown article")
    parser.add_argument("--package-dir", help="Optional explicit package directory")
    parser.add_argument("--clone-name", help="Optional cloned markdown filename")
    parser.add_argument(
        "--redact-paths",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Redact absolute local paths in generated files and CLI output (default: on)",
    )
    args = parser.parse_args()

    article = Path(args.article).expanduser().resolve()
    if not article.exists():
        raise SystemExit(f"Article not found: {article}")
    if article.suffix.lower() not in {".md", ".markdown", ".mdx"}:
        raise SystemExit(f"Unsupported article extension: {article.suffix}")

    package_dir = Path(args.package_dir).expanduser().resolve() if args.package_dir else article.parent / f"{article.stem}__illustration_package"
    package_dir = unique_dir(package_dir)
    clone_name = args.clone_name or f"{article.stem}.annotated{article.suffix}"

    (package_dir / "assets" / "gif").mkdir(parents=True, exist_ok=True)
    (package_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
    cloned_article = package_dir / clone_name
    shutil.copy2(article, cloned_article)

    source_article_display = display_path(article, redact_paths=args.redact_paths)
    cloned_article_display = display_path(cloned_article, package_dir=package_dir, redact_paths=args.redact_paths)

    (package_dir / "illustration-plan.md").write_text(
        "# Illustration Plan\n\n"
        "- Status: initialized\n"
        f"- Source article: {source_article_display}\n"
        f"- Cloned article: {cloned_article_display}\n",
        encoding="utf-8",
    )
    (package_dir / "sources.md").write_text("# Sources\n\n", encoding="utf-8")
    (package_dir / "matches.yaml").write_text("matches: []\n", encoding="utf-8")

    print(f"PACKAGE_DIR={display_path(package_dir, redact_paths=args.redact_paths)}")
    print(f"CLONED_ARTICLE={display_path(cloned_article, package_dir=package_dir, redact_paths=args.redact_paths)}")
    print(f"GIF_DIR={display_path(package_dir / 'assets' / 'gif', package_dir=package_dir, redact_paths=args.redact_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
