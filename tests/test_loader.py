"""
test_loader.py
Tests for database connection and data loading.
Run with: pytest tests/test_loader.py -v
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


@pytest.fixture
def mock_engine():
    engine = MagicMock()
    conn = MagicMock()
    result = MagicMock()
    result.fetchone.return_value = ("PostgreSQL 17.8 on x86_64",)
    conn.execute.return_value = result
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    engine.connect.return_value = conn
    return engine


def test_get_engine_raises_without_database_url():
    with patch("ingestion.db_connection.DATABASE_URL", None):
        from ingestion.db_connection import get_engine
        with pytest.raises(ValueError, match="DATABASE_URL not found"):
            get_engine()


def test_get_engine_returns_engine_with_valid_url():
    with patch("ingestion.db_connection.DATABASE_URL", "postgresql://user:pass@host/db"):
        with patch("ingestion.db_connection.create_engine") as mock_create:
            mock_create.return_value = MagicMock()
            from ingestion.db_connection import get_engine
            engine = get_engine()
            assert engine is not None
            mock_create.assert_called_once()


def test_connection_returns_true_on_success(mock_engine):
    with patch("ingestion.db_connection.get_engine", return_value=mock_engine):
        from ingestion.db_connection import test_connection
        result = test_connection()
        assert result is True


def test_connection_returns_false_on_failure():
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = OperationalError("connection failed", None, None)
    with patch("ingestion.db_connection.get_engine", return_value=mock_engine):
        from ingestion.db_connection import test_connection
        result = test_connection()
        assert result is False


def test_unique_constraint_prevents_duplicates():
    insert_results = [MagicMock(rowcount=1), MagicMock(rowcount=0)]
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.side_effect = insert_results
    mock_eng = MagicMock()
    mock_eng.connect.return_value = mock_conn
    with mock_eng.connect() as conn:
        first = conn.execute(MagicMock())
        second = conn.execute(MagicMock())
    assert first.rowcount == 1
    assert second.rowcount == 0