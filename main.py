from fastapi import FastAPI
from src.core.variables import origins, REDIS_URL
from src.core.db_pool import DataBasePool
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from scalar_fastapi import get_scalar_api_reference
from src.middlewares.exceptions import ExceptionHandlingMiddleware
from src.middlewares.block_sensitive_path import BlockSensitivePathsMiddleware
from src.api.authentication.views import router as auth_router
from src.api.user.views import router as user_router
from src.api.chatroom.views import router as chatroom_router
from src.api.subscription.views import router as subscription_router
from src.utils.format_response import format_response
from src.webhook.views import router as webhook_router

from src.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await DataBasePool.setup()
    yield
    await DataBasePool.teardown()


app = FastAPI(
    title="Gemini Backend Clone",
    description="Gemini Backend Clone API",
    debug=True,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(ExceptionHandlingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(BlockSensitivePathsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chatroom_router)
app.include_router(subscription_router)
app.include_router(webhook_router)


@app.get("/")
async def root():
    return format_response(
        message="Welcome to Gemini Backend Clone",
        data={"info": "Navigate to '/scalar' to get "},
    )


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
