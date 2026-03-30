def run(payload: dict) -> dict:
    path = str(payload.get("path", "")).strip()
    return {"ok": True, "tool": "file_reader", "path": path, "content": ""}
