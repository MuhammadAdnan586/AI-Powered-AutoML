"""
Dashboard Charts Service
Generates interactive chart data for the frontend dashboard.
Returns JSON data that can be rendered with Recharts/Chart.js.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional


MODELS_DIR = Path("models")
ARTIFACTS_DIR = Path("artifacts")


class DashboardChartService:
    """
    Prepares chart data for the Module 3 dashboard:
    - Model performance comparison chart
    - Feature importance bar chart
    - Data quality score gauge
    - Training history line chart
    - Correlation heatmap data
    - Class distribution pie chart
    """

    def __init__(self, dataset_id: int):
        self.dataset_id = dataset_id

    def get_benchmark_chart_data(self, benchmark_results: Dict) -> Dict[str, Any]:
        """Prepare bar chart data for model comparison."""
        models = benchmark_results.get("models", [])
        if not models:
            return {}

        return {
            "type": "bar",
            "title": "AutoML Benchmark Leaderboard",
            "data": [
                {
                    "name": m["name"],
                    "score": round(m.get("score", 0) * 100, 2),
                    "training_time": round(m.get("training_time", 0), 2)
                }
                for m in sorted(models, key=lambda x: x.get("score", 0), reverse=True)
            ],
            "xKey": "name",
            "yKeys": ["score"],
            "yLabel": "Score (%)",
            "colors": ["#1a237e", "#283593", "#3949ab", "#5c6bc0", "#7986cb"]
        }

    def get_feature_importance_chart(self, feature_importance: List[Dict]) -> Dict[str, Any]:
        """Prepare horizontal bar chart for feature importance."""
        top10 = sorted(feature_importance, key=lambda x: x["importance"], reverse=True)[:10]
        return {
            "type": "bar",
            "orientation": "horizontal",
            "title": "Top 10 Feature Importance (SHAP)",
            "data": [
                {"feature": f["feature"], "importance": round(f["importance"], 4)}
                for f in top10
            ],
            "xKey": "importance",
            "yKey": "feature",
            "color": "#1b5e20"
        }

    def get_quality_score_gauge(self, quality_score: float, grade: str) -> Dict[str, Any]:
        """Gauge chart data for data quality score."""
        if quality_score >= 75:
            color = "#2e7d32"  # green
        elif quality_score >= 50:
            color = "#f57c00"  # orange
        else:
            color = "#c62828"  # red

        return {
            "type": "gauge",
            "title": "Data Quality Score",
            "value": quality_score,
            "max": 100,
            "grade": grade,
            "color": color,
            "segments": [
                {"from": 0, "to": 45, "color": "#c62828", "label": "Poor"},
                {"from": 45, "to": 60, "color": "#ef6c00", "label": "Average"},
                {"from": 60, "to": 75, "color": "#f9a825", "label": "Good"},
                {"from": 75, "to": 100, "color": "#2e7d32", "label": "Excellent"}
            ]
        }

    def get_class_distribution_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Pie chart for target class distribution."""
        target_col = df.columns[-1]
        if df[target_col].nunique() > 20:
            return {}  # Skip for regression/high cardinality

        counts = df[target_col].value_counts()
        return {
            "type": "pie",
            "title": f"Class Distribution — {target_col}",
            "data": [
                {"name": str(label), "value": int(count)}
                for label, count in counts.items()
            ]
        }

    def get_missing_values_chart(self, missing_info: Dict) -> Dict[str, Any]:
        """Bar chart for missing values per column."""
        columns = missing_info.get("columns", {})
        if not columns:
            return {"type": "bar", "title": "Missing Values", "data": [], "message": "No missing values ✓"}

        return {
            "type": "bar",
            "title": "Missing Values per Column",
            "data": [
                {"column": col, "missing_pct": info["missing_pct"]}
                for col, info in columns.items()
            ],
            "xKey": "column",
            "yKeys": ["missing_pct"],
            "yLabel": "Missing %",
            "color": "#c62828"
        }

    def get_model_metrics_radar(self, benchmark_results: Dict) -> Dict[str, Any]:
        """Radar chart comparing multiple models across metrics."""
        models = benchmark_results.get("models", [])[:5]
        if not models or not models[0].get("all_metrics"):
            return {}

        metric_keys = list(models[0]["all_metrics"].keys())
        return {
            "type": "radar",
            "title": "Model Metrics Comparison",
            "metrics": metric_keys,
            "data": [
                {
                    "model": m["name"],
                    **{k: round(m["all_metrics"].get(k, 0), 4) for k in metric_keys}
                }
                for m in models
            ]
        }

    def get_full_dashboard_data(
        self,
        df: pd.DataFrame,
        quality_report: Dict,
        benchmark_results: Dict,
        feature_importance: Optional[List] = None
    ) -> Dict[str, Any]:
        """Compile all chart data for the dashboard."""
        charts = {
            "benchmark": self.get_benchmark_chart_data(benchmark_results),
            "quality_score": self.get_quality_score_gauge(
                quality_report.get("quality_score", 0),
                quality_report.get("quality_grade", "-")
            ),
            "class_distribution": self.get_class_distribution_chart(df),
            "missing_values": self.get_missing_values_chart(
                quality_report.get("missing_values", {})
            ),
        }

        if feature_importance:
            charts["feature_importance"] = self.get_feature_importance_chart(feature_importance)

        # Summary stats
        charts["summary"] = {
            "total_rows": df.shape[0],
            "total_columns": df.shape[1],
            "quality_score": quality_report.get("quality_score", 0),
            "best_model": benchmark_results.get("best_model", {}).get("name", "-"),
            "best_score": round(benchmark_results.get("best_model", {}).get("score", 0) * 100, 2),
            "total_models_trained": len(benchmark_results.get("models", []))
        }

        return charts
