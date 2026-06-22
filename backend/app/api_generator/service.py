"""
API Generator Service
Handles endpoint creation, key management, and model inference.
"""

import secrets
import time
import pandas as pd
import re
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.api_generator.models import ApiEndpoint
from app.model_registry.registry import ModelRegistry


class ApiGeneratorService:
    def __init__(self, db: Session):
        self.db = db
        self.registry = ModelRegistry()

    # -- Helper --------------------------------------------------------------

    def _make_slug(self, name: str, user_id: int) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        return f"{base}-{user_id}-{secrets.token_hex(4)}"

    def _generate_api_key(self) -> str:
        return secrets.token_urlsafe(32)

    # -- CRUD ------------------------------------------------------------------

    def generate(
        self,
        model_name: str,
        user_id: int,
        endpoint_name: str,
        description: Optional[str],
        model_version: Optional[int] = None,
    ) -> ApiEndpoint:
        # Confirm the model exists in the JSON-based registry
        try:
            _, meta = self.registry.get_model(model_name, model_version)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found in registry")

        endpoint = ApiEndpoint(
            user_id=user_id,
            model_name=model_name,
            model_version=meta["version"],
            endpoint_name=endpoint_name,
            slug=self._make_slug(endpoint_name, user_id),
            description=description,
            api_key=self._generate_api_key(),
        )
        self.db.add(endpoint)
        self.db.commit()
        self.db.refresh(endpoint)
        return endpoint

    def list_endpoints(self, user_id: int) -> List[ApiEndpoint]:
        return self.db.query(ApiEndpoint).filter_by(user_id=user_id).all()

    def get_endpoint(self, endpoint_id: int, user_id: int) -> Optional[ApiEndpoint]:
        return self.db.query(ApiEndpoint).filter_by(id=endpoint_id, user_id=user_id).first()

    def regenerate_key(self, endpoint_id: int, user_id: int) -> str:
        ep = self.get_endpoint(endpoint_id, user_id)
        if not ep:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        ep.api_key = self._generate_api_key()
        self.db.commit()
        return ep.api_key

    def delete_endpoint(self, endpoint_id: int, user_id: int) -> None:
        ep = self.get_endpoint(endpoint_id, user_id)
        if not ep:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        self.db.delete(ep)
        self.db.commit()

    # -- Inference ---------------------------------------------------------------

    def predict(
        self,
        endpoint_slug: str,
        api_key: Optional[str],
        features: Dict[str, Any],
    ) -> Dict[str, Any]:
        ep = self.db.query(ApiEndpoint).filter_by(slug=endpoint_slug, is_active=True).first()
        if not ep:
            raise HTTPException(status_code=404, detail="Endpoint not found or inactive")
        if ep.api_key != api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")

        # Load model from the JSON-based registry
        try:
            model, meta = self.registry.get_model(ep.model_name, ep.model_version)
        except ValueError:
            raise HTTPException(status_code=404, detail="Model artifact not found in registry")

        df = pd.DataFrame([features])
        start = time.perf_counter()
        prediction = model.predict(df).tolist()
        elapsed_ms = (time.perf_counter() - start) * 1000

        probability = None
        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(df).tolist()[0]

        # Update usage stats
        from datetime import datetime
        ep.total_calls += 1
        ep.last_called_at = datetime.utcnow()
        self.db.commit()

        return {
            "prediction": prediction[0],
            "probability": probability,
            "model_name": ep.model_name,
            "endpoint": endpoint_slug,
            "inference_time_ms": round(elapsed_ms, 3),
        }