import logging
import re
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status
from src.utils.format_response import format_response

SENSITIVE_PATTERNS = [
    re.compile(r"\\.\\."),
    re.compile(r"/\\.env($|/)", re.IGNORECASE),
    re.compile(r"/\\.git($|/)", re.IGNORECASE),
    re.compile(r"/\\.htaccess($|/)", re.IGNORECASE),
    re.compile(r"/\\.gitignore($|/)", re.IGNORECASE),
    re.compile(r"wp-admin/?", re.IGNORECASE),
    re.compile(r"wordpress/?", re.IGNORECASE),
    re.compile(r"(?i)/admin/?"),
    re.compile(r"/\\..*"),
]


class BlockSensitivePathsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(path):
                logging.warning(f"Access to sensitive content is forbidden for {path}")
                return format_response(
                    status_code=status.HTTP_403_FORBIDDEN,
                    message="Access to sensitive content is forbidden.",
                )
        return await call_next(request)
