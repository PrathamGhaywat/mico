import logging

import requests
from langchain.tools import tool

from ._api import API_TIMEOUT, api_headers, api_root


@tool
def get_user_stats(slack_id: str) -> str:
    """Get full user stats by Slack ID."""
    try:
        logging.info(f"Looking up user stats for slack_id: {slack_id}")

        # The detail endpoint wants internal user ID, so we search first.
        search_resp = requests.get(
            f"{api_root()}/users",
            headers=api_headers(),
            params={"query": slack_id, "limit": 100},
            timeout=API_TIMEOUT,
        )
        search_resp.raise_for_status()

        users = search_resp.json().get("users", [])
        user = next((u for u in users if u.get("slack_id") == slack_id), None)
        if not user:
            return "User not found"

        user_id = user.get("id")
        detail_resp = requests.get(
            f"{api_root()}/users/{user_id}",
            headers=api_headers(),
            timeout=API_TIMEOUT,
        )
        detail_resp.raise_for_status()
        return str(detail_resp.json())
    except Exception as e:
        logging.error(f"Error fetching user stats for {slack_id}: {e}", exc_info=True)
        return f"Error fetching user stats: {e}"
