"""Seed registry: every module here exporting seed(session) runs via run_all (idempotent)."""

import importlib
import pkgutil

from sqlalchemy.orm import Session


def run_all(session: Session) -> list[str]:
    ran: list[str] = []
    for mod_info in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
        module = importlib.import_module(f"{__name__}.{mod_info.name}")
        seed_fn = getattr(module, "seed", None)
        if callable(seed_fn):
            seed_fn(session)
            ran.append(mod_info.name)
    session.commit()
    return ran
