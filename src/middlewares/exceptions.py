import logging
import re
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, status
from src.utils.format_response import format_response


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response: Response = await call_next(request)
            return response
        except Exception as exc:
            logging.error("Sorry we found something fishy!🦈 Catching it quick..")
            return format_response(
                message=str(exc) if str(exc) else "Unexpected server error.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
