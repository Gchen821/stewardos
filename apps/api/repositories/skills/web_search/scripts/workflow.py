def run(payload: dict) -> dict:
    query = str(payload.get("query", "")).strip()
    top_k = int(payload.get("top_k", 5))
    return {
        "ok": True,
        "skill": "web_search",
        "query": query,
        "top_k": top_k,
        "results": [],
        "summary": "Web Search 技能执行完成（占位实现，待接入真实搜索工具）。",
    }
