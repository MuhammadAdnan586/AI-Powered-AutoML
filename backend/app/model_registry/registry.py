"""
Model Registry
Manages model versioning, metadata, and lifecycle.
Supports: save, load, compare, promote, deprecate.
"""
import json
import pickle
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib


REGISTRY_DIR = Path("models/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_INDEX = REGISTRY_DIR / "index.json"


class ModelRegistry:
    """
    Versioned model registry with metadata tracking.
    Each model version stores: model file, metadata, metrics, tags.
    """

    def __init__(self):
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, List[Dict]]:
        if REGISTRY_INDEX.exists():
            with open(REGISTRY_INDEX) as f:
                return json.load(f)
        return {}

    def _save_index(self):
        with open(REGISTRY_INDEX, "w") as f:
            json.dump(self.index, f, indent=2, default=str)

    def _get_next_version(self, model_name: str) -> int:
        if model_name not in self.index:
            return 1
        return max(v["version"] for v in self.index[model_name]) + 1

    def register_model(
        self,
        model_name: str,
        model_object: Any,
        metrics: Dict[str, float],
        dataset_id: int,
        task_type: str,
        feature_names: List[str],
        tags: Optional[Dict[str, str]] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Register a new model version.
        Returns version metadata.
        """
        version = self._get_next_version(model_name)
        model_dir = REGISTRY_DIR / model_name / f"v{version}"
        model_dir.mkdir(parents=True, exist_ok=True)

        # Save model file
        model_path = model_dir / "model.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model_object, f)

        # Compute checksum
        with open(model_path, "rb") as f:
            checksum = hashlib.md5(f.read()).hexdigest()

        metadata = {
            "model_name": model_name,
            "version": version,
            "version_tag": f"v{version}",
            "dataset_id": dataset_id,
            "task_type": task_type,
            "feature_names": feature_names,
            "metrics": metrics,
            "tags": tags or {},
            "description": description,
            "model_path": str(model_path),
            "checksum": checksum,
            "created_at": datetime.now().isoformat(),
            "status": "staging",  # staging | production | deprecated
            "is_champion": False
        }

        # Save metadata
        with open(model_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        # Update index
        if model_name not in self.index:
            self.index[model_name] = []
        self.index[model_name].append(metadata)
        self._save_index()

        return metadata

    def get_model(self, model_name: str, version: Optional[int] = None) -> tuple:
        """
        Load a model. If version is None, loads latest production or latest overall.
        Returns: (model_object, metadata)
        """
        if model_name not in self.index:
            raise ValueError(f"Model '{model_name}' not found in registry")

        versions = self.index[model_name]
        if version:
            meta = next((v for v in versions if v["version"] == version), None)
        else:
            # Try champion first, then latest
            meta = next((v for v in versions if v["is_champion"]), None)
            if not meta:
                meta = max(versions, key=lambda v: v["version"])

        if not meta:
            raise ValueError(f"Version {version} not found for model '{model_name}'")

        with open(meta["model_path"], "rb") as f:
            model = pickle.load(f)

        return model, meta

    def promote_to_production(self, model_name: str, version: int) -> Dict[str, Any]:
        """Promote a model version to production (champion)."""
        if model_name not in self.index:
            raise ValueError(f"Model '{model_name}' not found")

        # Demote existing champion
        for v in self.index[model_name]:
            if v["is_champion"]:
                v["is_champion"] = False
                v["status"] = "deprecated"

        # Promote new version
        target = next((v for v in self.index[model_name] if v["version"] == version), None)
        if not target:
            raise ValueError(f"Version {version} not found")

        target["status"] = "production"
        target["is_champion"] = True
        target["promoted_at"] = datetime.now().isoformat()

        # Update metadata file
        meta_path = Path(target["model_path"]).parent / "metadata.json"
        with open(meta_path, "w") as f:
            json.dump(target, f, indent=2, default=str)

        self._save_index()
        return target

    def deprecate_model(self, model_name: str, version: int) -> Dict[str, Any]:
        """Deprecate a specific model version."""
        if model_name not in self.index:
            raise ValueError(f"Model '{model_name}' not found")

        target = next((v for v in self.index[model_name] if v["version"] == version), None)
        if not target:
            raise ValueError(f"Version {version} not found")

        target["status"] = "deprecated"
        target["is_champion"] = False
        self._save_index()
        return target

    def list_models(self) -> Dict[str, Any]:
        """List all registered models with version counts."""
        result = {}
        for name, versions in self.index.items():
            champion = next((v for v in versions if v["is_champion"]), None)
            result[name] = {
                "total_versions": len(versions),
                "champion_version": champion["version"] if champion else None,
                "latest_version": max(v["version"] for v in versions),
                "versions": versions
            }
        return result

    def compare_versions(self, model_name: str, version1: int, version2: int) -> Dict[str, Any]:
        """Compare metrics between two model versions."""
        if model_name not in self.index:
            raise ValueError(f"Model '{model_name}' not found")

        v1 = next((v for v in self.index[model_name] if v["version"] == version1), None)
        v2 = next((v for v in self.index[model_name] if v["version"] == version2), None)

        if not v1 or not v2:
            raise ValueError("One or both versions not found")

        comparison = {
            "model_name": model_name,
            "version1": {"version": version1, "metrics": v1["metrics"], "created_at": v1["created_at"]},
            "version2": {"version": version2, "metrics": v2["metrics"], "created_at": v2["created_at"]},
            "delta": {}
        }

        all_metrics = set(v1["metrics"].keys()) | set(v2["metrics"].keys())
        for metric in all_metrics:
            val1 = v1["metrics"].get(metric, 0)
            val2 = v2["metrics"].get(metric, 0)
            comparison["delta"][metric] = {
                "v1": val1,
                "v2": val2,
                "change": round(val2 - val1, 4),
                "improved": val2 > val1
            }

        return comparison

    def delete_version(self, model_name: str, version: int) -> bool:
        """Permanently delete a model version."""
        if model_name not in self.index:
            return False

        target = next((v for v in self.index[model_name] if v["version"] == version), None)
        if not target:
            return False

        if target["is_champion"]:
            raise ValueError("Cannot delete champion model. Promote another version first.")

        # Remove files
        model_dir = Path(target["model_path"]).parent
        if model_dir.exists():
            shutil.rmtree(model_dir)

        self.index[model_name] = [v for v in self.index[model_name] if v["version"] != version]
        self._save_index()
        return True
