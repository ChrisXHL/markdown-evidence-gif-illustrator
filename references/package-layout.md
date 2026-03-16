# Package Layout

Default package layout is created beside the source article:

```text
<article_dir>/
├── source-article.md
└── <article_stem>__illustration_package/
    ├── <article_stem>.annotated.md
    ├── illustration-plan.md
    ├── matches.yaml
    ├── sources.md
    ├── webreel.config.json          # optional
    └── assets/
        ├── images/
        │   ├── 01-<slug>.png
        │   └── 02-<slug>.png
        └── gif/
            ├── 01-<slug>.gif
            └── 02-<slug>.gif
```

## Rules
- Keep the original article untouched.
- Use relative paths inside Markdown.
- Default visual preference is HD static screenshots in `assets/images/`, with adaptive ratio by default.
- Use `assets/gif/` only when one static frame cannot clearly contain the needed source evidence.
- If package folder already exists, create a non-destructive suffix.
- Keep artifact names stable and predictable.
