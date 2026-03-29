import logging

import requests
from langchain.tools import tool

from ._api import API_TIMEOUT, api_headers, api_root


@tool
def fetch_shop_items(_: str = "") -> str:
    """Get a list of shop items, including price (cookies) and stock."""
    try:
        # Handy for spotting API issues quickly when something feels off.
        logging.info("Fetching shop items")
        resp = requests.get(
            f"{api_root()}/store",
            headers=api_headers(),
            timeout=API_TIMEOUT,
        )
        resp.raise_for_status()
        return str(resp.json())
    except Exception as e:
        logging.error(f"Error fetching shop items: {e}", exc_info=True)
        return f"API error: {e}"
