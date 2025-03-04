import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.views import router
from app.core.dependencies.common import lifespan
from app.api.security.exceptions import rate_limit_exceeded_handler


def create_application() -> FastAPI:
    app = FastAPI(
        title="Dev Talk API - Users",
        description="RESTful API for managing users",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.include_router(router, prefix="/api/v1", tags=["Users"])

    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(HTTPSRedirectMiddleware)

    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,
    )

    app.exception_handler(RateLimitExceeded)(rate_limit_exceeded_handler)

    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )