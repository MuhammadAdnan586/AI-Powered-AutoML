from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class ApiEndpointCreate(BaseModel):
    model_name: str
    model_version: Optional[int] = None
    endpoint_name: str
    description: Optional[str] = None


class ApiEndpointResponse(BaseModel):
    id: int
    model_name: str
    model_version: Optional[int]
    endpoint_name: str
    slug: str
    description: Optional[str]
    api_key: str
    is_active: bool
    total_calls: int
    last_called_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyResponse(BaseModel):
    api_key: str


class PredictionRequest(BaseModel):
    features: Dict[str, Any]


class PredictionResponse(BaseModel):
    prediction: Any
    probability: Optional[List[float]] = None
    model_name: str
    endpoint: str
    inference_time_ms: float