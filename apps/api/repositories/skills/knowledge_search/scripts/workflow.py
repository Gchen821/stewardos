def run(payload: dict) -> dict:
    query = str(payload.get("query", "")).strip()
    limit = int(payload.get("limit", 5))
    return {
        "ok": True,
        "skill": "knowledge_search",
        "query": query,
        "limit": limit,
        "results": [],
        "summary": "知识检索流程已执行（占位实现）。",
    }
