"""Application entry point for the unified Recruitment Platform."""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from recruitment_platform.api.router import api_router
from recruitment_platform.config.logging_config import configure_logging
from recruitment_platform.config.settings import get_settings
from recruitment_platform.monitoring.metrics import MetricsMiddleware
from recruitment_platform.monitoring.tracing import setup_tracing
from recruitment_platform.security.middleware import (
    AuthMiddleware,
    InputSanitizationMiddleware,
    RateLimitMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)

settings = get_settings()
configure_logging(settings.log_level, settings.log_format)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_tracing(service_name="recruitment-platform")
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Unified Recruitment Platform - AI-powered recruitment automation",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Security middleware.
    #
    # Starlette PREPENDS on add_middleware(): user_middleware[0] is the
    # OUTERMOST layer, the LAST call ends up innermost.
    #
    # Security headers must appear on EVERY response, including the ones that
    # short-circuit below (401 Auth, 429 RateLimit, 413 InputSanitization).
    # BaseHTTPMiddleware only decorates responses that flow back through it, so
    # relying on add_middleware ordering is fragile: CORS and TrustedHost are
    # registered after this block and therefore sit OUTSIDE the header layer.
    #
    # SecurityHeadersMiddleware is therefore installed last, after CORS and
    # TrustedHost, which makes it the OUTERMOST layer - the only position that
    # guarantees every response, including early rejections, carries headers.
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(InputSanitizationMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted hosts
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    # Added last => outermost. See note above.
    app.add_middleware(SecurityHeadersMiddleware)

    # Include API routes
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Recruitment Platform API", "version": settings.app_version}


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "recruitment-platform"}


def main() -> None:
    """Run the application server."""
    uvicorn.run(
        "recruitment_platform.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers,
    )


if __name__ == "__main__":
    main()
