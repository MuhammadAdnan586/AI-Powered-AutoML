"""
AutoML SaaS Platform - Main Application
FastAPI entry point with all routers registered
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.database.connection import create_tables
import logging
import time

logging.basicConfig(
    level=logging.INFO if not settings.APP_DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} [{settings.APP_ENV}]")
    create_tables()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered AutoML SaaS Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field, "message": error["msg"]})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed", "errors": errors},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."},
    )


# --- Module 1: Foundation ---
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.datasets.router import router as datasets_router
from app.dashboard.router import router as dashboard_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(datasets_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


# --- Module 2/3/4: dynamically registered, won't crash app if one fails ---
loaded_modules = []
failed_modules = []

def safe_register(import_path: str, router_attr: str, prefix: str, name: str):
    try:
        module = __import__(import_path, fromlist=[router_attr])
        router_obj = getattr(module, router_attr)
        app.include_router(router_obj, prefix=prefix)
        loaded_modules.append(name)
    except Exception as e:
        failed_modules.append((name, str(e)))
        logger.error(f"Failed to load module '{name}': {e}")


# --- Module 2: AutoML Engine ---
safe_register("app.preprocessing.router", "router", "/api/v1", "Preprocessing")
safe_register("app.feature_engineering.router", "router", "/api/v1", "Feature Engineering")
safe_register("app.automl.router", "router", "/api/v1", "AutoML")
safe_register("app.benchmark.router", "router", "/api/v1", "Benchmark")
safe_register("app.training.routes", "router", "/api/v1", "Training")
safe_register("app.mlflow_tracking.router", "router", "/api/v1", "MLflow Tracking")

# --- Module 3: AI Intelligence ---
safe_register("app.explainability.routes", "router", "/api/v1", "Explainability")
safe_register("app.data_quality.routes", "router", "/api/v1", "Data Quality")
safe_register("app.chatbot.routes", "router", "/api/v1", "Chatbot")
safe_register("app.reports.routes", "router", "/api/v1", "Reports")
safe_register("app.model_registry.routes", "router", "/api/v1", "Model Registry")

# --- Module 4: Production & SaaS ---
safe_register("app.api_generator.routes", "router", "/api/v1", "API Generator")
safe_register("app.retraining.routes", "router", "/api/v1", "Retraining")
safe_register("app.notifications.routes", "router", "/api/v1", "Notifications")
safe_register("app.rbac.routes", "router", "/api/v1", "RBAC")
safe_register("app.monitoring.routes", "router", "/api/v1", "Monitoring")


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "loaded_modules": loaded_modules,
        "failed_modules": [name for name, _ in failed_modules],
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "env": settings.APP_ENV,
        "loaded_modules": loaded_modules,
        "failed_modules": failed_modules,
    }