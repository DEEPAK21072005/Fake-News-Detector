from fastapi import Request, status
from fastapi.responses import JSONResponse
from backend.app.core.logging_config import logger


class VeritasException(Exception):
    """Base exception for domain-specific VeritasAI errors."""
    def __init__(self, message: str, status_code: int = 400, details: str = None, suggestion: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details
        self.suggestion = suggestion


async def veritas_exception_handler(request: Request, exc: VeritasException):
    logger.warning(f"Handled VeritasException: {exc.message} (status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "suggestion": exc.suggestion or "Please check your input or adjust settings.",
            "path": request.url.path
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception at {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "An unexpected error occurred during processing.",
            "details": str(exc) if not "password" in str(exc).lower() else "Internal error",
            "suggestion": "Verify system resources or try analyzing plain text.",
            "path": request.url.path
        }
    )
