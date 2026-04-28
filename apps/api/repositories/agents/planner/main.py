def run(context: dict) -> dict:
    return {
        "asset_type": "agent",
        "asset_code": "planner",
        "role": "planner",
        "status": "loaded",
        "summary": "Planner control asset is loaded from the filesystem repository.",
        "context_keys": sorted(context.keys()),
    }
