"""
SHAP Explainability Service
Generates SHAP values, feature importance, and explanation plots
"""
import os
import json
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shap
from pathlib import Path
from typing import Optional


ARTIFACTS_DIR = Path("artifacts/explainability")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


class SHAPExplainer:
    """
    Generates SHAP explanations for trained ML models.
    Supports: Tree-based, Linear, and Kernel explainers.
    """

    def __init__(self, model, X_train: pd.DataFrame, model_type: str = "tree"):
        self.model = model
        self.X_train = X_train
        self.model_type = model_type
        self.explainer = None
        self.shap_values = None
        self._init_explainer()

    def _init_explainer(self):
        """Auto-detect and initialize the correct SHAP explainer."""
        try:
            model_name = type(self.model).__name__.lower()
            tree_models = ["randomforest", "gradientboosting", "xgb", "lgbm", "decisiontree", "extratrees"]
            linear_models = ["logisticregression", "linearregression", "ridge", "lasso", "sgd"]

            if any(t in model_name for t in tree_models):
                self.explainer = shap.TreeExplainer(self.model)
            elif any(l in model_name for l in linear_models):
                self.explainer = shap.LinearExplainer(self.model, self.X_train)
            else:
                background = shap.sample(self.X_train, min(100, len(self.X_train)))
                self.explainer = shap.KernelExplainer(self.model.predict, background)
        except Exception as e:
            print(f"[SHAP] Explainer init error: {e}")
            background = shap.sample(self.X_train, min(50, len(self.X_train)))
            self.explainer = shap.KernelExplainer(self.model.predict, background)

    def compute_shap_values(self, X_sample: pd.DataFrame) -> np.ndarray:
        """Compute SHAP values for given samples."""
        self.shap_values = self.explainer.shap_values(X_sample)
        return self.shap_values

    def get_feature_importance(self, X_sample: pd.DataFrame) -> dict:
        """Get mean absolute SHAP values as feature importance."""
        shap_vals = self.compute_shap_values(X_sample)
        if isinstance(shap_vals, list):
            shap_vals = np.abs(shap_vals[1]) if len(shap_vals) > 1 else np.abs(shap_vals[0])
        else:
            shap_vals = np.abs(shap_vals)

        importance = pd.DataFrame({
            "feature": X_sample.columns.tolist(),
            "importance": np.mean(shap_vals, axis=0)
        }).sort_values("importance", ascending=False)

        return importance.to_dict(orient="records")

    def plot_summary(self, X_sample: pd.DataFrame, save_path: str = None) -> str:
        """Generate and save SHAP summary plot."""
        shap_vals = self.compute_shap_values(X_sample)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]

        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_vals, X_sample, show=False, plot_type="bar")
        plt.tight_layout()

        save_path = save_path or str(ARTIFACTS_DIR / "shap_summary.png")
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
        return save_path

    def plot_waterfall(self, X_sample: pd.DataFrame, instance_idx: int = 0, save_path: str = None) -> str:
        """Generate waterfall plot for a single prediction."""
        shap_vals = self.compute_shap_values(X_sample)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]

        plt.figure(figsize=(10, 6))
        shap.plots._waterfall.waterfall_legacy(
            self.explainer.expected_value if not isinstance(self.explainer.expected_value, list)
            else self.explainer.expected_value[1],
            shap_vals[instance_idx],
            X_sample.iloc[instance_idx],
            show=False
        )
        plt.tight_layout()

        save_path = save_path or str(ARTIFACTS_DIR / f"waterfall_{instance_idx}.png")
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
        return save_path

    def plot_force(self, X_sample: pd.DataFrame, instance_idx: int = 0, save_path: str = None) -> str:
        """Generate force plot for a single prediction."""
        shap_vals = self.compute_shap_values(X_sample)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]

        expected = self.explainer.expected_value
        if isinstance(expected, list):
            expected = expected[1]

        shap.initjs()
        force_plot = shap.force_plot(
            expected,
            shap_vals[instance_idx],
            X_sample.iloc[instance_idx],
            show=False
        )
        save_path = save_path or str(ARTIFACTS_DIR / f"force_{instance_idx}.html")
        shap.save_html(save_path, force_plot)
        return save_path

    def get_full_explanation(self, X_sample: pd.DataFrame, dataset_id: int) -> dict:
        """Return complete explainability data for API response."""
        feature_importance = self.get_feature_importance(X_sample)
        summary_plot = self.plot_summary(
            X_sample,
            str(ARTIFACTS_DIR / f"shap_summary_{dataset_id}.png")
        )
        waterfall_plot = self.plot_waterfall(
            X_sample,
            save_path=str(ARTIFACTS_DIR / f"waterfall_{dataset_id}.png")
        )

        return {
            "feature_importance": feature_importance,
            "plots": {
                "summary": summary_plot,
                "waterfall": waterfall_plot,
            },
            "top_features": [f["feature"] for f in feature_importance[:5]],
            "explainer_type": type(self.explainer).__name__
        }
