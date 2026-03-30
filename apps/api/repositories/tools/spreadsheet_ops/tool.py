def run(payload: dict) -> dict:
    file_path = str(payload.get("file_path", "")).strip()
    return {
        "ok": True,
        "tool": "spreadsheet_ops",
        "file_path": file_path,
        "changed_cells": 0,
        "warnings": [],
    }
