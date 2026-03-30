def run(payload: dict) -> dict:
    query = str(payload.get("query", "")).strip()
    return {"ok": True, "tool": "web_query", "query": query, "results": []}
