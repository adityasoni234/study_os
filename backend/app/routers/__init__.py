"""Auto-discovers every router module. Add a module exporting `router`; don't edit main.py."""

import importlib
import pkgutil

from fastapi import APIRouter


def all_routers() -> list[APIRouter]:
    routers: list[APIRouter] = []
    for mod_info in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
        module = importlib.import_module(f"{__name__}.{mod_info.name}")
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            routers.append(router)
    return routers
