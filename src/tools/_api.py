import os

API_TIMEOUT = 10


def api_root() -> str:
    base = os.getenv("FLAVORTOWN_BASE_URL", "https://flavortown.hackclub.com").rstrip("/")
    if base.endswith("/api/v1"):
        return base
    return f"{base}/api/v1"


def api_headers() -> dict[str, str]:
    api_key = os.getenv("FLAVORTOWN_API_KEY", "")
    return {"Authorization": f"Bearer {api_key}"}
