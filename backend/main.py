"""
AutoML SaaS – FastAPI Application Entry Point
Module 4: Production & SaaS Features
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config.settings import settings
from app.logs_module.logger import setup_logging
from app.logs_module.middleware import RequestLoggingMiddleware
from app.security.middleware import register_security_middleware
from app.scheduler.jobs import start_scheduler, stop_scheduler

# ── Logging (must be first) ───────────────────────────────────────────────────
setup_logging(level="DEBUG" if settings.DEBUG else "INFO")

# ── Lifespan: startup + shutdown ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await start_scheduler()
    yield
    # Shutdown
    await stop_scheduler()


# ── App Factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,   # Hide docs in production
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware (order matters — outermost first) ───────────────────────
    register_security_middleware(app)                    # CORS, rate limit, headers
    app.add_middleware(RequestLoggingMiddleware)         # Request/response logging
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Restrict in production: ["yourdomain.com"]
    )

    # ── Routers ──────────────────────────────────────────────────────────────
    # Module 1 – Foundation (already built)
    from app.auth.routes import router as auth_router
    from app.users.routes import router as users_router
    from app.dashboard.routes import router as dashboard_router
    from app.datasets.routes import router as datasets_router

    # Module 2 – AutoML Engine (already built)
    from app.automl.routes import router as automl_router
    from app.training.routes import router as training_router
    from app.benchmark.routes import router as benchmark_router
    from app.mlflow_tracking.routes import router as mlflow_router

    # Module 3 – AI Intelligence (already built)
    from app.explainability.routes import router as xai_router
    from app.data_quality.routes import router as quality_router
    from app.chatbot.routes import router as chatbot_router
    from app.reports.routes import router as reports_router
    from app.model_registry.routes import router as registry_router

    # ── Module 4 – Production & SaaS Features ──────────────────────────────
    from app.api_generator.routes import router as api_gen_router
    from app.retraining.routes import router as retraining_router
    from app.notifications.routes import router as notifications_router
    from app.rbac.routes import router as rbac_router
    from app.monitoring.routes import router as monitoring_router

    # Register all routers
    for router in [
        auth_router, users_router, dashboard_router, datasets_router,
        automl_router, training_router, benchmark_router, mlflow_router,
        xai_router, quality_router, chatbot_router, reports_router, registry_router,
        api_gen_router, retraining_router, notifications_router, rbac_router, monitoring_router,
    ]:
        app.include_router(router, prefix="/api/v1")

    # ── Health check (public) ────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    def root_health():
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    return app


app = create_app()
