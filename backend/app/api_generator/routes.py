"""
Module 4 – No-Code REST API Generator
One-click REST API generation for trained ML models.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.api_generator.service import ApiGeneratorService
from app.api_generator.schemas import (
    ApiEndpointCreate,
    ApiEndpointResponse,
    ApiKeyResponse,
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter(prefix="/api-generator", tags=["API Generator"])


@router.post("/generate", response_model=ApiEndpointResponse)
def generate_api(
    payload: ApiEndpointCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    One-click: generate a REST API endpoint for a trained model.
    Returns endpoint URL + API key.
    """
    service = ApiGeneratorService(db)
    endpoint = service.generate(
        model_name=payload.model_name,
        model_version=payload.model_version,
        user_id=current_user.id,
        endpoint_name=payload.endpoint_name,
        description=payload.description,
    )
    return endpoint


@router.get("/list", response_model=list[ApiEndpointResponse])
def list_endpoints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all API endpoints for the current user."""
    service = ApiGeneratorService(db)
    return service.list_endpoints(user_id=current_user.id)


@router.get("/{endpoint_id}", response_model=ApiEndpointResponse)
def get_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ApiGeneratorService(db)
    ep = service.get_endpoint(endpoint_id, current_user.id)
    if not ep:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return ep


@router.post("/{endpoint_id}/regenerate-key", response_model=ApiKeyResponse)
def regenerate_api_key(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Regenerate API key for a given endpoint."""
    service = ApiGeneratorService(db)
    new_key = service.regenerate_key(endpoint_id, current_user.id)
    return {"api_key": new_key}


@router.delete("/{endpoint_id}")
def delete_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ApiGeneratorService(db)
    service.delete_endpoint(endpoint_id, current_user.id)
    return {"detail": "Endpoint deleted successfully"}


# ── Public prediction endpoint (secured by API key header) ──────────────────

@router.post("/predict/{endpoint_slug}", response_model=PredictionResponse)
def predict(
    endpoint_slug: str,
    payload: PredictionRequest,
    x_api_key: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Public prediction endpoint. Clients pass X-API-Key header.
    No login required – authenticated via API key only.
    """
    service = ApiGeneratorService(db)
    result = service.predict(
        endpoint_slug=endpoint_slug,
        api_key=x_api_key,
        features=payload.features,
    )
    return result
