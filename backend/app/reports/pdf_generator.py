"""
PDF Report Generator
Generates professional PDF reports for ML experiments using ReportLab.
Includes: data quality, model performance, SHAP plots, recommendations.
"""
import io
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


REPORTS_DIR = Path("artifacts/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class PDFReportGenerator:
    """
    Generates comprehensive PDF reports for AutoML experiments.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Define custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=self.styles["Title"],
            fontSize=24,
            textColor=colors.HexColor("#1a237e"),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            parent=self.styles["Heading1"],
            fontSize=14,
            textColor=colors.HexColor("#283593"),
            spaceAfter=8,
            spaceBefore=16,
            borderPad=4
        ))
        self.styles.add(ParagraphStyle(
            name="SubHeader",
            parent=self.styles["Heading2"],
            fontSize=11,
            textColor=colors.HexColor("#37474f"),
            spaceAfter=6,
            spaceBefore=10
        ))
        self.styles.add(ParagraphStyle(
            name="BodySmall",
            parent=self.styles["Normal"],
            fontSize=9,
            spaceAfter=4
        ))
        self.styles.add(ParagraphStyle(
            name="Highlight",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#1b5e20"),
            backColor=colors.HexColor("#e8f5e9"),
            spaceBefore=4,
            spaceAfter=4
        ))

    def generate_report(
        self,
        dataset_info: Dict[str, Any],
        quality_report: Dict[str, Any],
        benchmark_results: Dict[str, Any],
        explanation: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate full PDF report.
        Returns: path to saved PDF file
        """
        if output_path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(REPORTS_DIR / f"automl_report_{dataset_info.get('id', 'x')}_{ts}.pdf")

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        story = []

        # ── Cover Section ──────────────────────────────
        story.append(Spacer(1, 1 * inch))
        story.append(Paragraph("🤖 AutoML Analysis Report", self.styles["ReportTitle"]))
        story.append(Paragraph(
            f"Dataset: <b>{dataset_info.get('name', 'Unknown')}</b>",
            self.styles["Normal"]
        ))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}",
            self.styles["Normal"]
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a237e")))
        story.append(Spacer(1, 0.3 * inch))

        # ── Dataset Overview ───────────────────────────
        story.append(Paragraph("1. Dataset Overview", self.styles["SectionHeader"]))
        overview_data = [
            ["Metric", "Value"],
            ["Dataset Name", dataset_info.get("name", "-")],
            ["Total Rows", str(dataset_info.get("rows", "-"))],
            ["Total Columns", str(dataset_info.get("columns", "-"))],
            ["Task Type", dataset_info.get("task_type", "-")],
            ["Target Column", dataset_info.get("target_column", "-")],
        ]
        story.append(self._create_table(overview_data))
        story.append(Spacer(1, 0.2 * inch))

        # ── Data Quality ───────────────────────────────
        story.append(Paragraph("2. Data Quality Report", self.styles["SectionHeader"]))
        score = quality_report.get("quality_score", 0)
        grade = quality_report.get("quality_grade", "-")
        story.append(Paragraph(
            f"Quality Score: <b>{score}/100</b> — {grade}",
            self.styles["Highlight"]
        ))
        story.append(Spacer(1, 0.1 * inch))

        quality_data = [
            ["Check", "Result"],
            ["Missing Values", f"{quality_report.get('missing_values', {}).get('missing_percentage', 0):.1f}%"],
            ["Duplicate Rows", f"{quality_report.get('duplicates', {}).get('duplicate_percentage', 0):.1f}%"],
            ["Outlier Columns", str(len(quality_report.get("outliers", {})))],
            ["High Correlation Pairs", str(len(quality_report.get("correlation", {}).get("high_correlation_pairs", [])))],
        ]
        story.append(self._create_table(quality_data))

        # Add correlation heatmap if exists
        heatmap = quality_report.get("plots", {}).get("correlation_heatmap", "")
        if heatmap and Path(heatmap).exists():
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("Correlation Heatmap:", self.styles["SubHeader"]))
            story.append(Image(heatmap, width=5 * inch, height=3.5 * inch))

        # Recommendations
        recs = quality_report.get("recommendations", [])
        if recs:
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("Recommendations:", self.styles["SubHeader"]))
            for rec in recs:
                story.append(Paragraph(f"• {rec}", self.styles["BodySmall"]))

        story.append(PageBreak())

        # ── Model Benchmark ────────────────────────────
        story.append(Paragraph("3. AutoML Benchmark Results", self.styles["SectionHeader"]))
        models = benchmark_results.get("models", [])
        best_model = benchmark_results.get("best_model", {})

        if best_model:
            story.append(Paragraph(
                f"🏆 Best Model: <b>{best_model.get('name', '-')}</b> — "
                f"Score: <b>{best_model.get('score', 0):.4f}</b>",
                self.styles["Highlight"]
            ))
            story.append(Spacer(1, 0.1 * inch))

        if models:
            metric_name = benchmark_results.get("metric", "Score")
            bench_data = [["Rank", "Model", metric_name, "Training Time"]]
            for i, m in enumerate(models, 1):
                bench_data.append([
                    str(i),
                    m.get("name", "-"),
                    f"{m.get('score', 0):.4f}",
                    f"{m.get('training_time', 0):.2f}s"
                ])
            story.append(self._create_table(bench_data, header_color="#283593"))
        story.append(Spacer(1, 0.2 * inch))

        # ── Explainability ─────────────────────────────
        if explanation:
            story.append(Paragraph("4. Model Explainability (SHAP)", self.styles["SectionHeader"]))
            features = explanation.get("feature_importance", [])
            if features:
                story.append(Paragraph("Top Feature Importance:", self.styles["SubHeader"]))
                feat_data = [["Rank", "Feature", "SHAP Importance"]]
                for i, f in enumerate(features[:10], 1):
                    feat_data.append([str(i), f["feature"], f"{f['importance']:.4f}"])
                story.append(self._create_table(feat_data))

            shap_plot = explanation.get("plots", {}).get("summary", "")
            if shap_plot and Path(shap_plot).exists():
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph("SHAP Summary Plot:", self.styles["SubHeader"]))
                story.append(Image(shap_plot, width=5 * inch, height=3.5 * inch))

        # ── Footer ─────────────────────────────────────
        story.append(Spacer(1, 0.5 * inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Paragraph(
            "Generated by AI-Powered AutoML Platform",
            ParagraphStyle("Footer", parent=self.styles["Normal"],
                           fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))

        doc.build(story)
        return output_path

    def _create_table(self, data: list, header_color: str = "#1a237e") -> Table:
        """Create a styled table."""
        table = Table(data, hAlign="LEFT")
        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f5f5f5")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e8eaf6")]),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
        table.setStyle(style)
        return table
