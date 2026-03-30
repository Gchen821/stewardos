---
name: Web Reader
description: 参考 helloagents 的 web-reader 技能思路，进行网页正文抽取。
---

# Web Reader

用途：
- 输入 URL，读取网页内容（当前为占位）。
- 输出正文片段和摘要结果。

输入建议：
- `url`：目标网页链接
- `max_chars`：最大提取字符，默认 4000

输出约定：
- `content`：抽取文本
- `summary`：摘要
