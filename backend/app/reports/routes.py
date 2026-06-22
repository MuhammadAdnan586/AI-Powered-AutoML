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
from sqlalchemy.orm import Session

from app.reports.pdf_generator import PDFReportGenerator
from app.reports.excel_exporter import ExcelExporter
from app.data_quality.analyzer import DataQualityAnalyzer
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.auth.models import User
from app.datasets.models import Dataset, DatasetVersion

router = APIRouter(prefix="/reports", tags=["Reports"])

UPLOADS_DIR = Path("uploads")
MODELS_DIR = Path("models")
REPORTS_DIR = Path("artifacts/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class ReportRequest(BaseModel):
    dataset_id: int
    model_name: Optional[str] = None
    include_shap: bool = True


def load_dataset(dataset_id: int, db: Session, user: User) -> pd.DataFrame:
    """Load dataset CSV/Excel using the active version's file path."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.owner_id == user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    version = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset_id,
        DatasetVersion.is_active == True
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="No active version found for this dataset")

    if version.file_path.endswith(".csv"):
        for encoding in ["utf-8", "latin-1", "windows-1252", "utf-8-sig", "cp1252"]:
            try:
                return pd.read_csv(version.file_path, low_memory=False, encoding=encoding)
            except (UnicodeDecodeError, Exception):
                continue
        raise HTTPException(status_code=500, detail="Could not decode CSV file with any known encoding")
    return pd.read_excel(version.file_path)


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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a comprehensive PDF report with:
    - Dataset overview, quality score, benchmarks, SHAP analysis.
    Returns download path.
    """
    try:
        df = load_dataset(request.dataset_id, db, current_user)
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
            "download_url": f"/api/v1/reports/download/{Path(pdf_path).name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/export-excel")
async def export_excel_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export AutoML results to a multi-sheet Excel workbook.
    Returns download path.
    """
    try:
        df = load_dataset(request.dataset_id, db, current_user)
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
            "download_url": f"/api/v1/reports/download/{Path(excel_path).name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel export failed: {str(e)}")


@router.get("/list")
async def list_reports(current_user: User = Depends(get_current_user)):
    """List all generated reports."""
    reports = []
    for f in REPORTS_DIR.iterdir():
        if f.suffix in [".pdf", ".xlsx"]:
            reports.append({
                "filename": f.name,
                "type": "PDF" if f.suffix == ".pdf" else "Excel",
                "size_kb": round(f.stat().st_size / 1024, 1),
                "download_url": f"/api/v1/reports/download/{f.name}"
            })
    return {"reports": sorted(reports, key=lambda x: x["filename"], reverse=True)}


@router.get("/download/{filename}")
async def download_report(filename: str, current_user: User = Depends(get_current_user)):
    """Download a generated report file."""
    file_path = REPORTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    media_type = "application/pdf" if filename.endswith(".pdf") else \
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(str(file_path), media_type=media_type, filename=filename)