# markdown-evidence-gif-illustrator

把一篇 Markdown 文章自动做成“可配图、可追溯、可回填”的插图包：
- 找出最值得配图的位置
- 必要时上网检索并做来源朔源（provenance）
- 默认优先高清静态截图（必要时再用 GIF）
- 将图片/GIF 插回克隆后的 Markdown（不改原文）

> 适用于：技术解读、产品分析、教程、新闻拆解等需要“证据可视化”的 Markdown 内容。

---

## 功能亮点

- **原文保护**：默认只在 package 里的 `*.annotated.md` 回填，不修改原始文章
- **来源朔源**：记录 `direct / traced_to_upstream / unresolved`
- **格式策略**：优先 `static_hd_adaptive`，信息装不下再退回 GIF
- **结构化产物**：`matches.yaml`、`sources.md`、`illustration-plan.md`
- **可复用脚本**：从包初始化、匹配构建、截图、回填到配置生成一条链路

---

## 目录结构

```text
.
├── SKILL.md
├── README.md
├── references/
│   ├── workflow.md
│   ├── search-policy.md
│   ├── provenance-rules.md
│   ├── pinchtab-provenance-playbook.md
│   ├── visual-format-policy.md
│   ├── package-layout.md
│   └── markdown-insertion.md
├── scripts/
│   ├── create_article_package.py
│   ├── build_matches.py
│   ├── generate_provenance_queries.py
│   ├── bootstrap_sources_from_matches.py
│   ├── init_source_record.py
│   ├── capture_hd_screenshot.py
│   ├── capture_hd_screenshot.js
│   ├── render_webreel_config.py
│   ├── insert_gifs_into_markdown.py
│   └── redact_asset_filenames.py
└── assets/
    ├── images/
    └── gif/
```

---

## 快速开始

### 1) 创建文章插图包

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/create_article_package.py <article.md>
```

> 默认会脱敏本地绝对路径（如 `/Users/<name>/...`），避免路径泄露到 `illustration-plan.md` 或终端日志。  
> 如你确实需要原始绝对路径，可显式关闭：
>
> ```bash
> python3 .../create_article_package.py <article.md> --no-redact-paths
> ```

将生成：

```text
<article_dir>/<article_stem>__illustration_package/
```

### 2) （可选）从 JSON 构建 `matches.yaml`

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/build_matches.py <matches.json> <matches.yaml>
```

### 3) （需要检索时）生成 provenance 查询 + 初始化来源记录

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/generate_provenance_queries.py \
  ./matches.yaml ./provenance-queries.json

python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/bootstrap_sources_from_matches.py \
  ./matches.yaml ./sources.md
```

### 4) 抓取静态图（默认推荐）

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/capture_hd_screenshot.py \
  --url https://example.com \
  --output ./assets/images/01-example.png \
  --text "target evidence text" \
  --ready-text "target evidence text" \
  --highlight-text "target evidence text"
```

### 5) 回填到 Markdown

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/insert_gifs_into_markdown.py \
  ./article.annotated.md ./matches.yaml
```

### 6) （可选）一键匿名化图片/GIF 文件名

当你要分享 package 给外部协作者，建议执行：

```bash
python3 $HOME/.agents/skills/markdown-evidence-gif-illustrator/scripts/redact_asset_filenames.py \
  ./<article>__illustration_package
```

该命令会把 `assets/images` 和 `assets/gif` 下文件重命名为 `img-001-<hash>.png` / `gif-001-<hash>.gif` 形式，
并自动回写 `matches.yaml`、`sources.md`、`*.annotated.md` 中的引用路径。

---

## 推荐工作流（简版）

1. 创建 package（保留原文）
2. 选锚点（优先高价值解释位）
3. 不足证据才检索
4. 朔源到上游可用来源
5. 默认高清静态图，必要时 GIF
6. 回填 `*.annotated.md`
7. 输出 package 路径与产物清单

详细流程见：`references/workflow.md`

---

## 依赖说明

- Python 3.9+
- Node.js（如需使用 `capture_hd_screenshot.js`）
- 浏览器自动化相关依赖（按你的环境安装）
- 如需检索链路，建议配合 PinchTab / webreel 流程

---

## 隐私与安全建议

- 避免提交任何 API Key / Token / Cookie
- 文档示例路径请使用 `$HOME/...`，不要硬编码本机用户名路径
- `assets/` 建议仅存放可公开图片/GIF，不要放私密截图
- 对外分享前可运行 `scripts/redact_asset_filenames.py` 去标识化文件名并同步更新引用

---

## License

当前仓库未附带许可证文件。如需开源复用，建议补充 `LICENSE`（例如 MIT）。
