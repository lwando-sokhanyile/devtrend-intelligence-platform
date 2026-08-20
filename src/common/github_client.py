"""
GitHub API Client
Centralised GitHub API connection used by all collectors.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def get(endpoint, params=None):
    """Makes a GET request to the GitHub API."""
    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers=HEADERS,
        params=params,
        timeout=10
    )
    response.raise_for_status()
    return response.json()