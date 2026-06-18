# app/middleware/error_handler.py

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

import traceback
import logging


logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Centralized application error handling.
    """

    @staticmethod
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation Error",
                "details": exc.errors()
            }
        )

    @staticmethod
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ):

        logger.error(
            traceback.format_exc()
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal Server Error",
                "message": str(exc)
            }
        )