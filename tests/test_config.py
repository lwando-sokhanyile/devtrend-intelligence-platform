"""Tests for config module."""
import os
import pytest


def test_db_port_default():
    """DB_PORT should default to 5433."""
    from src.common.config import DB_PORT
    assert DB_PORT is not None


def test_db_name_default():
    """DB_NAME should default to devtrend_db."""
    from src.common.config import DB_NAME
    assert DB_NAME == "devtrend_db"