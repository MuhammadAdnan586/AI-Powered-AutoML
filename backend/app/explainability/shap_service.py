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
    def __init__(self, model, X_train: pd.DataFrame, model_type: str = "tree"):
        self.model = model
        self.X_train = X_train
        self.model_type = model_type
        self.explainer = None
        self.shap_values = None
        self._cached_X_sample = None
        self._init_explainer()

    def _init_explainer(self):
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

    def _get_scalar_expected_value(self):
        """Get scalar expected value — handles array/list cases."""
        ev = self.explainer.expected_value
        if isinstance(ev, (list, np.ndarray)):
            ev = np.array(ev)
            if ev.ndim == 0:
                return float(ev)
            # For binary classification take index 1, else index 0
            return float(ev[1]) if len(ev) > 1 else float(ev[0])
        return float(ev)

    def _get_shap_values_2d(self, shap_vals):
        """Normalize shap values to 2D array."""
        if isinstance(shap_vals, list):
            # Multi-class: use class 1 for binary, class 0 for others
            shap_vals = shap_vals[1] if len(shap_vals) > 1 else shap_vals[0]

        if isinstance(shap_vals, np.ndarray) and shap_vals.ndim == 3:
            # Shape (samples, features, classes) — take class 1
            shap_vals = shap_vals[:, :, 1]

        return shap_vals

    def compute_shap_values(self, X_sample: pd.DataFrame) -> np.ndarray:
        # Avoid recomputing the same SHAP values multiple times within one
        # explanation request (feature importance + summary plot + waterfall
        # plot all call this with the identical X_sample, which is expensive
        # for KernelExplainer-based models like KNN/SVM).
        if self.shap_values is not None and self._cached_X_sample is X_sample:
            return self.shap_values
        self.shap_values = self.explainer.shap_values(X_sample)
        self._cached_X_sample = X_sample
        return self.shap_values

    def get_feature_importance(self, X_sample: pd.DataFrame) -> dict:
        shap_vals = self.compute_shap_values(X_sample)

        if isinstance(shap_vals, list):
            shap_vals = np.mean([np.abs(sv) for sv in shap_vals], axis=0)
        else:
            shap_vals = np.abs(shap_vals)

        if shap_vals.ndim == 3:
            shap_vals = shap_vals.mean(axis=2)

        if shap_vals.ndim == 1:
            shap_vals = shap_vals.reshape(1, -1)

        mean_importance = np.mean(shap_vals, axis=0).flatten()

        features = X_sample.columns.tolist()
        min_len = min(len(features), len(mean_importance))
        features = features[:min_len]
        mean_importance = mean_importance[:min_len]

        importance = pd.DataFrame({
            "feature": features,
            "importance": mean_importance
        }).sort_values("importance", ascending=False)

        return importance.to_dict(orient="records")

    def plot_summary(self, X_sample: pd.DataFrame, save_path: str = None) -> str:
        shap_vals = self.compute_shap_values(X_sample)
        shap_vals = self._get_shap_values_2d(shap_vals)

        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_vals, X_sample, show=False, plot_type="bar")
        plt.tight_layout()

        save_path = save_path or str(ARTIFACTS_DIR / "shap_summary.png")
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
        return save_path

    def plot_waterfall(self, X_sample: pd.DataFrame, instance_idx: int = 0, save_path: str = None) -> str:
        try:
            shap_vals = self.compute_shap_values(X_sample)
            shap_vals_2d = self._get_shap_values_2d(shap_vals)
            expected_value = self._get_scalar_expected_value()

            plt.figure(figsize=(10, 6))
            shap.plots._waterfall.waterfall_legacy(
                expected_value,
                shap_vals_2d[instance_idx],
                X_sample.iloc[instance_idx],
                show=False
            )
            plt.tight_layout()

            save_path = save_path or str(ARTIFACTS_DIR / f"waterfall_{instance_idx}.png")
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            plt.close()
            return save_path

        except Exception as e:
            print(f"[SHAP] Waterfall plot error: {e}")
            # Fallback: return summary plot path
            return self.plot_summary(X_sample, save_path)

    def plot_force(self, X_sample: pd.DataFrame, instance_idx: int = 0, save_path: str = None) -> str:
        try:
            shap_vals = self.compute_shap_values(X_sample)
            shap_vals_2d = self._get_shap_values_2d(shap_vals)
            expected_value = self._get_scalar_expected_value()

            shap.initjs()
            force_plot = shap.force_plot(
                expected_value,
                shap_vals_2d[instance_idx],
                X_sample.iloc[instance_idx],
                show=False
            )
            save_path = save_path or str(ARTIFACTS_DIR / f"force_{instance_idx}.html")
            shap.save_html(save_path, force_plot)
            return save_path

        except Exception as e:
            print(f"[SHAP] Force plot error: {e}")
            return ""

    def get_full_explanation(self, X_sample: pd.DataFrame, dataset_id: int) -> dict:
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