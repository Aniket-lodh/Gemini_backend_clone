import logging
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
                message="Internal server error. please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
