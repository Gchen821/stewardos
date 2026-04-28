def run(context: dict) -> dict:
    return {
        "asset_type": "agent",
        "asset_code": "reflection",
        "role": "reflection",
        "status": "loaded",
        "summary": "Reflection control asset is loaded from the filesystem repository.",
        "context_keys": sorted(context.keys()),
    }
