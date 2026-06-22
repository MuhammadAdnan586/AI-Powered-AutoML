# Module 3 – AI Intelligence Layer

Complete implementation of the AI Intelligence Layer for the AutoML SaaS platform.

---

## 📁 Folder Structure

```
module3/
├── explainability/
│   ├── __init__.py
│   ├── shap_service.py        ← SHAP explainer (Tree/Linear/Kernel)
│   └── routes.py              ← /api/explainability/* endpoints
│
├── data_quality/
│   ├── __init__.py
│   ├── analyzer.py            ← Quality score, missing, outliers, correlation
│   └── routes.py              ← /api/data-quality/* endpoints
│
├── chatbot/
│   ├── __init__.py
│   ├── chat_service.py        ← Claude AI chat with dataset context
│   └── routes.py              ← /api/chat/* endpoints
│
├── reports/
│   ├── __init__.py
│   ├── pdf_generator.py       ← Professional PDF with ReportLab
│   ├── excel_exporter.py      ← Multi-sheet Excel with openpyxl
│   └── routes.py              ← /api/reports/* endpoints
│
├── model_registry/
│   ├── __init__.py
│   ├── registry.py            ← Versioned model store
│   └── routes.py              ← /api/model-registry/* endpoints
│
├── dashboard/
│   ├── chart_service.py       ← Chart JSON data for frontend
│   └── routes.py              ← /api/dashboard/* endpoints
│
├── module3_router.py          ← Central router (import this in main.py)
└── requirements_module3.txt   ← All required packages
```

---

## 🔌 Integration (main.py)

```python
from fastapi import FastAPI
from app.module3_router import module3_router

app = FastAPI(title="AutoML SaaS")
app.include_router(module3_router)
```

---

## 🌐 API Endpoints

### 📊 Explainability
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/explainability/explain` | Full SHAP explanation + plots |
| POST | `/api/explainability/feature-importance` | Feature importance ranking |
| GET  | `/api/explainability/plots/{dataset_id}/{model}` | List saved plots |

### 🧹 Data Quality
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/data-quality/report/{dataset_id}` | Full quality report |
| GET | `/api/data-quality/score/{dataset_id}` | Quality score + grade |
| GET | `/api/data-quality/correlation/{dataset_id}` | Correlation matrix |
| GET | `/api/data-quality/missing/{dataset_id}` | Missing values detail |

### 🤖 AI Chat Assistant
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/message` | Send message to AI assistant |
| GET  | `/api/chat/insights/{dataset_id}` | Auto-generate dataset insights |
| GET  | `/api/chat/history/{dataset_id}` | Get conversation history |
| POST | `/api/chat/reset` | Reset conversation |

### 📄 Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reports/generate-pdf` | Generate PDF report |
| POST | `/api/reports/export-excel` | Export Excel workbook |
| GET  | `/api/reports/list` | List all generated reports |
| GET  | `/api/reports/download/{filename}` | Download report file |

### 🗂️ Model Registry
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/model-registry/models` | List all models |
| GET    | `/api/model-registry/models/{name}/versions` | List versions |
| GET    | `/api/model-registry/models/{name}/champion` | Get champion model |
| POST   | `/api/model-registry/promote` | Promote to production |
| POST   | `/api/model-registry/deprecate` | Deprecate version |
| POST   | `/api/model-registry/compare` | Compare two versions |
| DELETE | `/api/model-registry/models/{name}/versions/{v}` | Delete version |

### 📈 Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/data/{dataset_id}` | All chart data |
| GET | `/api/dashboard/benchmark-chart/{dataset_id}` | Benchmark bar chart |
| GET | `/api/dashboard/quality-score/{dataset_id}` | Quality gauge data |

---

## ⚙️ Environment Variables (.env)

```env
ANTHROPIC_API_KEY=your_claude_api_key_here
DATABASE_URL=mysql+mysqlclient://user:pass@localhost/automl_db
SECRET_KEY=your_jwt_secret_key
UPLOADS_DIR=uploads
MODELS_DIR=models
ARTIFACTS_DIR=artifacts
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements_module3.txt
```

---

## 🔄 Module 3 Feature Summary

| Feature | File | Status |
|---------|------|--------|
| SHAP Explainability | `explainability/shap_service.py` | ✅ Complete |
| Feature Importance | `explainability/shap_service.py` | ✅ Complete |
| Data Quality Score | `data_quality/analyzer.py` | ✅ Complete |
| Correlation Analysis | `data_quality/analyzer.py` | ✅ Complete |
| Outlier Detection | `data_quality/analyzer.py` | ✅ Complete |
| AI Chat Assistant | `chatbot/chat_service.py` | ✅ Complete |
| Auto Dataset Insights | `chatbot/chat_service.py` | ✅ Complete |
| PDF Report | `reports/pdf_generator.py` | ✅ Complete |
| Excel Export | `reports/excel_exporter.py` | ✅ Complete |
| Model Versioning | `model_registry/registry.py` | ✅ Complete |
| Champion/Staging | `model_registry/registry.py` | ✅ Complete |
| Dashboard Charts | `dashboard/chart_service.py` | ✅ Complete |
