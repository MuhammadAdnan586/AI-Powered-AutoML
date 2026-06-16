"""
Reports API Routes
Endpoints: generate PDF, export Excel, list reports, download
"""
import pickle
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from app.reports.pdf_generator import PDFReportGenerator
from app.reports.excel_exporter import ExcelExporter
from app.data_quality.analyzer import DataQualityAnalyzer
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/reports", tags=["Reports"])

UPLOADS_DIR = Path("uploads")
MODELS_DIR = Path("models")
REPORTS_DIR = Path("artifacts/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class ReportRequest(BaseModel):
    dataset_id: int
    model_name: Optional[str] = None
    include_shap: bool = True


def load_dataset(dataset_id: int) -> pd.DataFrame:
    for ext in [".csv", ".xlsx"]:
        path = UPLOADS_DIR / f"dataset_{dataset_id}{ext}"
        if path.exists():
            return pd.read_csv(path) if ext == ".csv" else pd.read_excel(path)
    raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")


def load_benchmark_results(dataset_id: int) -> dict:
    path = MODELS_DIR / f"dataset_{dataset_id}" / "benchmark_results.json"
    if path.exists():
        import json
        with open(path) as f:
            return json.load(f)
    return {"models": [], "best_model": {}, "metric": "Score"}


def load_explanation(dataset_id: int, model_name: str) -> dict:
    path = Path("artifacts/explainability") / f"explanation_{dataset_id}_{model_name}.json"
    if path.exists():
        import json
        with open(path) as f:
            return json.load(f)
    return {}


@router.post("/generate-pdf")
async def generate_pdf_report(
    request: ReportRequest,
    current_user=Depends(get_current_user)
):
    """
    Generate a comprehensive PDF report with:
    - Dataset overview, quality score, benchmarks, SHAP analysis.
    Returns download path.
    """
    try:
        df = load_dataset(request.dataset_id)
        quality_report = DataQualityAnalyzer(df, request.dataset_id).analyze()
        benchmark_results = load_benchmark_results(request.dataset_id)

        dataset_info = {
            "id": request.dataset_id,
            "name": f"Dataset #{request.dataset_id}",
            "rows": df.shape[0],
            "columns": df.shape[1],
            "task_type": benchmark_results.get("task_type", "Classification"),
            "target_column": df.columns[-1]
        }

        explanation = None
        if request.include_shap and request.model_name:
            explanation = load_explanation(request.dataset_id, request.model_name)

        generator = PDFReportGenerator()
        pdf_path = generator.generate_report(
            dataset_info=dataset_info,
            quality_report=quality_report,
            benchmark_results=benchmark_results,
            explanation=explanation
        )

        return {
            "status": "success",
            "message": "PDF report generated successfully",
            "file_path": pdf_path,
            "download_url": f"/api/reports/download/{Path(pdf_path).name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/export-excel")
async def export_excel_report(
    request: ReportRequest,
    current_user=Depends(get_current_user)
):
    """
    Export AutoML results to a multi-sheet Excel workbook.
    Returns download path.
    """
    try:
        df = load_dataset(request.dataset_id)
        quality_report = DataQualityAnalyzer(df, request.dataset_id).analyze()
        benchmark_results = load_benchmark_results(request.dataset_id)

        dataset_info = {
            "id": request.dataset_id,
            "name": f"Dataset #{request.dataset_id}",
            "rows": df.shape[0],
            "columns": df.shape[1],
            "task_type": benchmark_results.get("task_type", "Unknown"),
            "target_column": str(df.columns[-1])
        }

        explanation = None
        if request.include_shap and request.model_name:
            explanation = load_explanation(request.dataset_id, request.model_name)

        exporter = ExcelExporter()
        excel_path = exporter.export(
            dataset_info=dataset_info,
            quality_report=quality_report,
            benchmark_results=benchmark_results,
            explanation=explanation
        )

        return {
            "status": "success",
            "message": "Excel report exported successfully",
            "file_path": excel_path,
            "download_url": f"/api/reports/download/{Path(excel_path).name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel export failed: {str(e)}")


@router.get("/list")
async def list_reports(current_user=Depends(get_current_user)):
    """List all generated reports."""
    reports = []
    for f in REPORTS_DIR.iterdir():
        if f.suffix in [".pdf", ".xlsx"]:
            reports.append({
                "filename": f.name,
                "type": "PDF" if f.suffix == ".pdf" else "Excel",
                "size_kb": round(f.stat().st_size / 1024, 1),
                "download_url": f"/api/reports/download/{f.name}"
            })
    return {"reports": sorted(reports, key=lambda x: x["filename"], reverse=True)}


@router.get("/download/{filename}")
async def download_report(filename: str, current_user=Depends(get_current_user)):
    """Download a generated report file."""
    file_path = REPORTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    media_type = "application/pdf" if filename.endswith(".pdf") else \
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(str(file_path), media_type=media_type, filename=filename)
