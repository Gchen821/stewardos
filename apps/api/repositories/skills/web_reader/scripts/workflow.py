def run(payload: dict) -> dict:
    url = str(payload.get("url", "")).strip()
    max_chars = int(payload.get("max_chars", 4000))
    return {
        "ok": True,
        "skill": "web_reader",
        "url": url,
        "max_chars": max_chars,
        "content": "",
        "summary": "Web Reader 技能执行完成（占位实现，待接入真实抓取/解析）。",
    }
