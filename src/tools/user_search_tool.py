import logging

import requests
from langchain.tools import tool

from ._api import API_TIMEOUT, api_headers, api_root


@tool
def search_users(query: str) -> str:
    """Search users by display name or Slack ID."""
    try:
        # This gives the model a quick roster view when names are fuzzy.
        logging.info(f"Searching users with query: {query}")
        resp = requests.get(
            f"{api_root()}/users",
            headers=api_headers(),
            params={"query": query, "limit": 20},
            timeout=API_TIMEOUT,
        )
        resp.raise_for_status()
        return str(resp.json())
    except Exception as e:
        logging.error(f"Error searching users with query '{query}': {e}", exc_info=True)
        return f"Error searching users: {e}"
