# Provenance Rules

朔源优先级高于普通“找个权威链接”。

## 核心原则
对每个需要外部补强的配图点，优先回答这 4 个问题：
1. 这条信息最早来自哪里？
2. 这个页面是不是原始出处，而不是转述？
3. 如果不是原始出处，是否已经追到更上游来源？
4. 当前证据链是否足以支撑“在这里插这个 GIF/配图”？

## 来源分层
### A. 原始来源（最高优先）
- 官方公告 / 官方文档 / 官方博客
- 论文原文 / 数据发布机构原始页面
- 产品官方页面 / 发布说明 / 演示页面
- 法规、标准、监管原文

### B. 一级转述
- 权威媒体对原始来源的报道
- 行业机构对原始数据的整理
- 专家文章中明确引用原始出处的页面

### C. 二级及以下转述
- 自媒体总结
- 聚合站
- 未标清出处的转载

默认规则：
- 能用 A 就不用 B
- 能追到 A，就不要只停在 B/C
- 如果只能拿到 B/C，必须显式标注“未追到原始出处”

## 朔源动作
每次搜索都优先做：
1. 先找原文 / official / docs / release / paper / report / dataset
2. 再找引用链里的上游链接
3. 检查页面是否直接包含原始截图、原始数据、原始表述
4. 判断该来源更适合“录 GIF”还是只适合“作为证据引用”

## sources.md 必记字段
每条来源至少记录：
- anchor_id
- claim_or_visual_need
- search_query
- selected_title
- selected_url
- source_tier: original | primary_relay | secondary
- upstream_source_title
- upstream_source_url
- provenance_status: direct | traced_to_upstream | unresolved
- why_selected
- why_not_other_candidates
- usable_for_recording: yes | no
- uncertainty

## 何时算“朔源完成”
满足任一：
- 已拿到原始出处页面
- 虽然当前页面不是原始出处，但已经明确追到上游原始链接
- 无法继续上溯，但已清楚标注证据链断点与不确定性

## 冲突处理
如果多个来源说法不同：
- 先比原始来源
- 再比发布时间
- 再比是否直接引用原文/原数据
- 不能消解时，在 `sources.md` 记录冲突，不得静默忽略
