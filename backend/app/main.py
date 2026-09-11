"""StudyOS API application factory.

Routers are auto-discovered (app.routers.all_routers) and mounted under /api —
add a router module, never edit this file. Startup: for SQLite the schema is
created in-process (Postgres uses alembic), then idempotent seeds always run.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.base import SessionLocal, engine, init_db
from app.routers import all_routers
from app.utils.errors import register_error_handlers
from app.utils.logging_mw import RequestLoggingMiddleware, setup_logging
from app.utils.ratelimit import RateLimitMiddleware

log = logging.getLogger("studyos")

VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # SQLite dev path: create tables in-process. Postgres runs alembic instead.
    if engine.dialect.name == "sqlite":
        try:
            init_db()
        except Exception as exc:
            log.warning(
                json.dumps({"event": "init_db_failed", "reason": repr(exc)})
            )

    # Seeds are idempotent — always run them; tolerate partially-built trees
    # (e.g. models/seeds not landed yet) so the app still boots.
    try:
        from app.db.seeds import run_all

        session = SessionLocal()
        try:
            ran = run_all(session)
        finally:
            session.close()
        log.info(json.dumps({"event": "seeds_ran", "modules": ran}))
    except Exception as exc:
        log.warning(json.dumps({"event": "seeds_failed", "reason": repr(exc)}))

    log.info(
        json.dumps(
            {
                "event": "startup",
                "appEnv": settings.app_env,
                "aiMode": settings.resolved_ai_mode,
                "db": engine.dialect.name,
                "version": VERSION,
            }
        )
    )
    yield


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="StudyOS API",
        version=VERSION,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url=None,
        lifespan=lifespan,
    )

    register_error_handlers(app)

    # Middleware order (outermost first at runtime): CORS → logging → rate limit.
    # CORS headers therefore reach 429s and error responses; every request —
    # including rate-limited ones — gets a request id and a log line.
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    for router in all_routers():
        app.include_router(router, prefix="/api")

    return app


app = create_app()
