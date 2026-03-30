---
name: Web Search
description: 参考 helloagents 的 web-search 组织方式，提供网页检索能力。
---

# Web Search

用途：
- 接收自然语言检索请求。
- 调用 `web_query` 工具获取候选结果。
- 返回统一结构给 Agent。

输入建议：
- `query`：检索词
- `top_k`：返回条数，默认 5

输出约定：
- `results[]`：标题、链接、摘要
- `summary`：对结果的短总结
