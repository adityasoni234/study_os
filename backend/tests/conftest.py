"""Shared pytest fixtures for the StudyOS backend.

CRITICAL: the environment is pinned BEFORE any app import — app.config caches
settings at import time. Keep the os.environ lines at the very top.
"""

import os

os.environ["DATABASE_URL"] = "sqlite://"  # in-memory, StaticPool (see app.db.base)
os.environ["AI_MODE"] = "mock"
os.environ.setdefault("APP_ENV", "test")
# The whole suite shares one limiter key (testclient); never rate-limit tests.
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "1000000")

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _database():
    """Create the schema and run idempotent seeds once for the whole session.

    Tolerates partially-built trees (models/seeds still landing from other
    agents) so contract tests keep running during parallel development.
    """
    from app.db.base import SessionLocal, init_db

    try:
        init_db()
    except Exception as exc:  # partial build: models package broken/missing
        print(f"\n[conftest] WARNING: init_db failed ({exc!r}) — tables not created")

    try:
        from app.db.seeds import run_all

        session = SessionLocal()
        try:
            run_all(session)
        finally:
            session.close()
    except Exception as exc:  # partial build: seed modules not landed yet
        print(f"\n[conftest] WARNING: seeds skipped ({exc!r})")

    yield


@pytest.fixture(scope="session")
def client(_database):
    """TestClient over the real app (lifespan runs: sqlite init + seeds, idempotent)."""
    from fastapi.testclient import TestClient

    import app.main as main

    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture()
def db(_database):
    """A plain SQLAlchemy session on the same in-memory database."""
    from app.db.base import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
