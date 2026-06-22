"""
Data Quality Analyzer
Generates comprehensive quality report: scores, correlations, missing values,
outliers, distribution analysis, and recommendations.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, List


ARTIFACTS_DIR = Path("artifacts/data_quality")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


class DataQualityAnalyzer:
    """
    Analyzes dataset quality and generates a comprehensive report with score.
    Score range: 0-100 (higher = better quality)
    """

    def __init__(self, df: pd.DataFrame, dataset_id: int):
        self.df = df.copy()
        self.dataset_id = dataset_id
        self.report = {}
        self.score = 0

    def analyze(self) -> Dict[str, Any]:
        """Run all quality checks and return full report."""
        self.report = {
            "dataset_id": self.dataset_id,
            "shape": {"rows": int(self.df.shape[0]), "columns": int(self.df.shape[1])},
            "missing_values": self._check_missing(),
            "duplicates": self._check_duplicates(),
            "data_types": self._analyze_dtypes(),
            "numeric_stats": self._numeric_statistics(),
            "outliers": self._detect_outliers(),
            "correlation": self._correlation_analysis(),
            "class_balance": self._check_class_balance(),
            "quality_score": 0,
            "quality_grade": "",
            "recommendations": []
        }

        self.score = self._compute_quality_score()
        self.report["quality_score"] = self.score
        self.report["quality_grade"] = self._get_grade(self.score)
        self.report["recommendations"] = self._generate_recommendations()

        # Generate plots
        self.report["plots"] = {
            "correlation_heatmap": self._plot_correlation_heatmap(),
            "missing_values_bar": self._plot_missing_values(),
            "distribution_plots": self._plot_distributions()
        }

        return self.report

    def _check_missing(self) -> Dict[str, Any]:
        total_cells = self.df.shape[0] * self.df.shape[1]
        missing_per_col = self.df.isnull().sum()
        missing_pct_per_col = (missing_per_col / self.df.shape[0] * 100).round(2)

        return {
            "total_missing": int(missing_per_col.sum()),
            "missing_percentage": round(missing_per_col.sum() / total_cells * 100, 2),
            "columns": {
                col: {
                    "missing_count": int(missing_per_col[col]),
                    "missing_pct": float(missing_pct_per_col[col])
                }
                for col in self.df.columns if missing_per_col[col] > 0
            }
        }

    def _check_duplicates(self) -> Dict[str, Any]:
        dup_count = int(self.df.duplicated().sum())
        return {
            "total_duplicates": dup_count,
            "duplicate_percentage": round(dup_count / len(self.df) * 100, 2)
        }

    def _analyze_dtypes(self) -> Dict[str, str]:
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}

    def _numeric_statistics(self) -> Dict[str, Any]:
        numeric_cols = self.df.select_dtypes(include=np.number)
        if numeric_cols.empty:
            return {}
        stats = numeric_cols.describe().round(4)
        return stats.to_dict()

    def _detect_outliers(self) -> Dict[str, Any]:
        outlier_info = {}
        numeric_cols = self.df.select_dtypes(include=np.number)

        for col in numeric_cols.columns:
            Q1 = numeric_cols[col].quantile(0.25)
            Q3 = numeric_cols[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = ((numeric_cols[col] < lower) | (numeric_cols[col] > upper)).sum()

            if outliers > 0:
                outlier_info[col] = {
                    "outlier_count": int(outliers),
                    "outlier_pct": round(outliers / len(self.df) * 100, 2),
                    "lower_bound": round(lower, 4),
                    "upper_bound": round(upper, 4)
                }

        return outlier_info

    def _correlation_analysis(self) -> Dict[str, Any]:
        numeric_df = self.df.select_dtypes(include=np.number)
        if numeric_df.shape[1] < 2:
            return {}

        corr_matrix = numeric_df.corr().round(4)
        high_corr_pairs = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                val = corr_matrix.iloc[i, j]
                if abs(val) > 0.8:
                    high_corr_pairs.append({
                        "feature1": corr_matrix.columns[i],
                        "feature2": corr_matrix.columns[j],
                        "correlation": round(float(val), 4)
                    })

        return {
            "matrix": corr_matrix.to_dict(),
            "high_correlation_pairs": high_corr_pairs
        }

    def _check_class_balance(self) -> Dict[str, Any]:
        """Check if last column (assumed target) is balanced."""
        try:
            target = self.df.iloc[:, -1]
            if target.dtype == object or target.nunique() <= 20:
                counts = target.value_counts()
                return {
                    "target_column": str(self.df.columns[-1]),
                    "class_counts": counts.to_dict(),
                    "is_imbalanced": bool((counts.min() / counts.max()) < 0.3)
                }
        except Exception:
            pass
        return {}

    def _compute_quality_score(self) -> float:
        """
        Compute a 0-100 quality score based on:
        - Missing values (30 pts)
        - Duplicates (20 pts)
        - Outliers (20 pts)
        - Data type consistency (15 pts)
        - Class balance (15 pts)
        """
        score = 100.0

        # Deduct for missing values
        missing_pct = self.report["missing_values"]["missing_percentage"]
        score -= min(30, missing_pct * 3)

        # Deduct for duplicates
        dup_pct = self.report["duplicates"]["duplicate_percentage"]
        score -= min(20, dup_pct * 2)

        # Deduct for outliers
        total_outlier_pct = 0
        for col_data in self.report["outliers"].values():
            total_outlier_pct += col_data["outlier_pct"]
        if self.report["outliers"]:
            avg_outlier = total_outlier_pct / len(self.report["outliers"])
            score -= min(20, avg_outlier)

        # Deduct for class imbalance
        if self.report.get("class_balance", {}).get("is_imbalanced"):
            score -= 15

        return max(0, round(score, 1))

    def _get_grade(self, score: float) -> str:
        if score >= 90: return "A (Excellent)"
        elif score >= 75: return "B (Good)"
        elif score >= 60: return "C (Average)"
        elif score >= 45: return "D (Poor)"
        else: return "F (Very Poor)"

    def _generate_recommendations(self) -> List[str]:
        recs = []
        missing_pct = self.report["missing_values"]["missing_percentage"]
        if missing_pct > 20:
            recs.append(f"⚠️ {missing_pct}% missing values detected. Use imputation or remove high-missing columns.")
        elif missing_pct > 5:
            recs.append(f"💡 {missing_pct}% missing values. Consider median/mode imputation.")

        if self.report["duplicates"]["duplicate_percentage"] > 1:
            recs.append("🔁 Remove duplicate rows before training to avoid data leakage.")

        if len(self.report["outliers"]) > 0:
            recs.append(f"📊 Outliers found in {len(self.report['outliers'])} columns. Consider IQR clipping.")

        high_corr = self.report.get("correlation", {}).get("high_correlation_pairs", [])
        if high_corr:
            recs.append(f"🔗 {len(high_corr)} highly correlated feature pairs found. Consider dropping redundant features.")

        if self.report.get("class_balance", {}).get("is_imbalanced"):
            recs.append("⚖️ Class imbalance detected. Use SMOTE or class_weight='balanced'.")

        if not recs:
            recs.append("✅ Dataset looks clean and ready for training!")

        return recs

    def _plot_correlation_heatmap(self) -> str:
        numeric_df = self.df.select_dtypes(include=np.number)
        if numeric_df.shape[1] < 2:
            return ""

        fig, ax = plt.subplots(figsize=(min(12, numeric_df.shape[1] + 2), 8))
        corr = numeric_df.corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
                    square=True, linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
        ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold")
        plt.tight_layout()

        path = str(ARTIFACTS_DIR / f"correlation_heatmap_{self.dataset_id}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path

    def _plot_missing_values(self) -> str:
        missing = self.df.isnull().sum()
        missing = missing[missing > 0]
        if missing.empty:
            return ""

        fig, ax = plt.subplots(figsize=(10, 5))
        missing.sort_values(ascending=False).plot(kind="bar", ax=ax, color="tomato", edgecolor="black")
        ax.set_title("Missing Values per Column", fontsize=13, fontweight="bold")
        ax.set_ylabel("Missing Count")
        ax.set_xlabel("Columns")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        path = str(ARTIFACTS_DIR / f"missing_values_{self.dataset_id}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path

    def _plot_distributions(self) -> str:
        numeric_cols = self.df.select_dtypes(include=np.number).columns[:6]  # Max 6 cols
        if len(numeric_cols) == 0:
            return ""

        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
        axes = np.array(axes).flatten() if n_rows * n_cols > 1 else [axes]

        for i, col in enumerate(numeric_cols):
            axes[i].hist(self.df[col].dropna(), bins=30, color="steelblue", edgecolor="white", alpha=0.8)
            axes[i].set_title(f"Distribution: {col}", fontsize=10)
            axes[i].set_xlabel(col)
            axes[i].set_ylabel("Frequency")

        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.suptitle("Feature Distributions", fontsize=14, fontweight="bold")
        plt.tight_layout()

        path = str(ARTIFACTS_DIR / f"distributions_{self.dataset_id}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path
