"""AppError + global handlers. Raise AppError anywhere; never leak internals."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.utils.envelope import err_body

log = logging.getLogger("studyos")


class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


class NotFound(AppError):
    def __init__(self, what: str = "Resource"):
        super().__init__("NOT_FOUND", f"{what} was not found.", 404)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status, content=err_body(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        fields = sorted(
            {str(e["loc"][-1]) for e in exc.errors() if e.get("loc")} - {"body"}
        )
        message = "Invalid request." + (f" Check: {', '.join(fields)}." if fields else "")
        return JSONResponse(status_code=422, content=err_body("VALIDATION_ERROR", message))

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        log.exception("unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content=err_body("INTERNAL_ERROR", "Something interrupted this request."),
        )
