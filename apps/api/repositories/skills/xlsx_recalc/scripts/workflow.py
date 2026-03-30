def run(payload: dict) -> dict:
    file_path = str(payload.get("file_path", "")).strip()
    sheet_name = str(payload.get("sheet_name", "")).strip()
    return {
        "ok": True,
        "skill": "xlsx_recalc",
        "file_path": file_path,
        "sheet_name": sheet_name,
        "changed_cells": 0,
        "warnings": [],
        "summary": "XLSX Recalc 技能执行完成（占位实现，待接入真实表格计算）。",
    }
