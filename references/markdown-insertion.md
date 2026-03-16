# Markdown Insertion Rules

## Default insertion behavior
Insert the visual block **after** the target paragraph or quoted anchor text.
This is safer than inserting before headings or trying to replace content.

## Modes
### 1. `image_only`
```md
![Why this visual helps](assets/images/01-example.png)
```

### 2. `explanation_and_image` (default)
```md
> 配图说明：这一段涉及抽象概念，补充一张高清来源截图帮助读者快速理解对应证据。

![抽象概念来源截图](assets/images/01-example.png)
```

### 3. GIF fallback
```md
> 配图说明：单张图无法完整展示来源证据，因此这里改用 GIF。

![抽象概念来源 GIF](assets/gif/01-example.gif)
```

## Insertion guidance
- Use relative paths only.
- Avoid duplicate insertion on reruns unless intentionally replacing content.
- Keep explanation to one short sentence unless the user asks for more.
- If anchor matching is ambiguous, prefer heading + quoted text verification before insertion.
