"""
Model Registry API Routes
Endpoints: list, register, promote, deprecate, compare, delete versions
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.model_registry.registry import ModelRegistry
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/model-registry", tags=["Model Registry"])

registry = ModelRegistry()


class PromoteRequest(BaseModel):
    model_name: str
    version: int


class DeprecateRequest(BaseModel):
    model_name: str
    version: int


class CompareRequest(BaseModel):
    model_name: str
    version1: int
    version2: int


@router.get("/models")
async def list_all_models(current_user=Depends(get_current_user)):
    """List all registered models with version history."""
    try:
        return {"status": "success", "models": registry.list_models()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}/versions")
async def list_model_versions(
    model_name: str,
    current_user=Depends(get_current_user)
):
    """Get all versions for a specific model."""
    models = registry.list_models()
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found in registry")
    return {"model_name": model_name, **models[model_name]}


@router.get("/models/{model_name}/champion")
async def get_champion_model(
    model_name: str,
    current_user=Depends(get_current_user)
):
    """Get the current production (champion) model metadata."""
    try:
        _, meta = registry.get_model(model_name)
        return {"status": "success", "champion": meta}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/promote")
async def promote_model(
    request: PromoteRequest,
    current_user=Depends(get_current_user)
):
    """Promote a model version to production."""
    try:
        result = registry.promote_to_production(request.model_name, request.version)
        return {"status": "success", "message": f"Version {request.version} promoted to production", "model": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deprecate")
async def deprecate_model(
    request: DeprecateRequest,
    current_user=Depends(get_current_user)
):
    """Deprecate a model version."""
    try:
        result = registry.deprecate_model(request.model_name, request.version)
        return {"status": "success", "message": f"Version {request.version} deprecated", "model": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/compare")
async def compare_model_versions(
    request: CompareRequest,
    current_user=Depends(get_current_user)
):
    """Compare metrics between two model versions."""
    try:
        comparison = registry.compare_versions(request.model_name, request.version1, request.version2)
        return {"status": "success", "comparison": comparison}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/models/{model_name}/versions/{version}")
async def delete_model_version(
    model_name: str,
    version: int,
    current_user=Depends(get_current_user)
):
    """Delete a specific model version (cannot delete champion)."""
    try:
        deleted = registry.delete_version(model_name, version)
        if not deleted:
            raise HTTPException(status_code=404, detail="Version not found")
        return {"status": "success", "message": f"Version {version} of '{model_name}' deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
