"""Create the schema and load demo seeds. From backend/: `python -m scripts.dev_db`. Idempotent."""

from app.db import seeds
from app.db.base import SessionLocal, engine, init_db


def main() -> None:
    init_db()
    url = engine.url.render_as_string(hide_password=True)
    print(f"schema: all tables ensured on {engine.dialect.name} ({url})")
    with SessionLocal() as session:
        ran = seeds.run_all(session)
    print(f"seeds: ran {', '.join(ran) if ran else '(no seed modules found)'}")


if __name__ == "__main__":
    main()
