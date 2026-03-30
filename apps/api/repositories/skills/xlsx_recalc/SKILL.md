---
name: XLSX Recalc
description: 参考 helloagents xlsx 技能，提供 Excel 重算任务入口。
---

# XLSX Recalc

用途：
- 输入本地表格路径和目标 sheet。
- 执行重算/校验逻辑（当前占位）。
- 输出任务结果与统计信息。

输入建议：
- `file_path`：xlsx 文件路径
- `sheet_name`：sheet 名称（可选）

输出约定：
- `changed_cells`：变更单元格数
- `warnings`：异常提示
