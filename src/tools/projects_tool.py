import logging

import requests
from langchain.tools import tool

from ._api import API_TIMEOUT, api_headers, api_root


@tool
def list_projects(query: str = "") -> str:
    """List projects, optionally filtered by a search query."""
    try:
        params: dict[str, str | int] = {"limit": 10}
        if query.strip():
            params["query"] = query.strip()

        # Keeping the payload small makes responses easier for the model to use.
        logging.info(f"Listing projects with params: {params}")
        resp = requests.get(
            f"{api_root()}/projects",
            headers=api_headers(),
            params=params,
            timeout=API_TIMEOUT,
        )
        resp.raise_for_status()
        return str(resp.json())
    except Exception as e:
        logging.error(f"Error listing projects: {e}", exc_info=True)
        return f"Error listing projects: {e}"
