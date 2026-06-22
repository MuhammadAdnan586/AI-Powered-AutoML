"""
Module 3 – AI Intelligence Layer
Main router integration file.

Register all Module 3 routers in your main FastAPI app:
    from app.module3_router import module3_router
    app.include_router(module3_router)
"""
from fastapi import APIRouter

from app.explainability.routes import router as explainability_router
from app.data_quality.routes import router as data_quality_router
from app.chatbot.routes import router as chatbot_router
from app.reports.routes import router as reports_router
from app.model_registry.routes import router as registry_router
from app.dashboard.routes import router as dashboard_router


# Combine all Module 3 routers under /module3 prefix (optional)
module3_router = APIRouter(tags=["Module 3 – AI Intelligence Layer"])

module3_router.include_router(explainability_router)
module3_router.include_router(data_quality_router)
module3_router.include_router(chatbot_router)
module3_router.include_router(reports_router)
module3_router.include_router(registry_router)
module3_router.include_router(dashboard_router)
