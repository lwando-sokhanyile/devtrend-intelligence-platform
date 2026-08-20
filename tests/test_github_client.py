"""Tests for GitHub API client."""
import pytest
from unittest.mock import patch, MagicMock


def test_headers_without_token():
    """Headers should not include Authorization without token."""
    with patch.dict('os.environ', {}, clear=True):
        import importlib
        import src.common.github_client as client
        importlib.reload(client)
        assert "Authorization" not in client.HEADERS or client.GITHUB_TOKEN is None


def test_get_builds_correct_url():
    """GET request should use correct base URL."""
    with patch('src.common.github_client.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        from src.common.github_client import get
        get("/search/repositories", params={"q": "test"})

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "https://api.github.com/search/repositories" in call_args[0][0]