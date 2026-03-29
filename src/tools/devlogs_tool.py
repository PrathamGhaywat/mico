import logging

import requests
from langchain.tools import tool

from ._api import API_TIMEOUT, api_headers, api_root


@tool
def list_recent_devlogs(limit: int = 5) -> str:
    """Get recent devlogs across all projects."""
    try:
        safe_limit = max(1, min(limit, 20))

        # Clamp limit so we do not accidentally flood the context window.
        logging.info(f"Listing recent devlogs with limit: {safe_limit}")
        resp = requests.get(
            f"{api_root()}/devlogs",
            headers=api_headers(),
            params={"limit": safe_limit},
            timeout=API_TIMEOUT,
        )
        resp.raise_for_status()
        return str(resp.json())
    except Exception as e:
        logging.error(f"Error listing devlogs: {e}", exc_info=True)
        return f"Error listing devlogs: {e}"
