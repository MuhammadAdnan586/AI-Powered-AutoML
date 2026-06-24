AI-Powered AutoML Platform

A production-ready, full-stack **Automated Machine Learning SaaS platform** that enables users to upload datasets, automatically train and compare ML models, explain predictions, and deploy APIs — all without writing a single line of code.

---

Live Demo
> Deploy with Docker and access at `http://localhost`

---

What Problem Does It Solve?

Building and deploying machine learning models requires deep technical expertise, weeks of setup, and expensive infrastructure. This platform automates the entire ML lifecycle — from raw data to production API — in minutes.

---

Key Features

Core AutoML Engine
- Automated model selection and hyperparameter tuning
- Multi-algorithm benchmarking (Random Forest, XGBoost, Logistic Regression, etc.)
- Feature engineering and data preprocessing pipeline

AI Intelligence Layer (Module 3)
- **SHAP Explainability** — understand why the model made each prediction
- **Data Quality Analyzer** — quality score, outlier detection, correlation matrix
- **AI Chat Assistant** — ask questions about your dataset in natural language
- **Auto PDF & Excel Reports** — one-click professional report generation
- **Model Registry** — versioned model store with champion/staging promotion

Production & SaaS Features (Module 4)
- **No-Code REST API Generator** — one-click API deployment for any trained model
- **Scheduled Retraining** — cron-based automatic model retraining
- **Role-Based Access Control (RBAC)** — admin, user, viewer roles
- **Email & In-App Notifications** — alerts for training completion and anomalies
- **Monitoring & Health Check** — CPU/RAM/Disk metrics and API usage stats
- **Structured JSON Logging** — production-grade logging middleware
- **Nginx Reverse Proxy + SSL** — secure deployment ready

---

Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | Next.js + TypeScript |
| Database | MySQL 8.0 |
| ML Libraries | Scikit-learn, XGBoost, SHAP |
| Containerization | Docker + Docker Compose |
| Reverse Proxy | Nginx |
| Background Jobs | APScheduler |
| Auth | JWT + RBAC |
| Reports | ReportLab (PDF), openpyxl (Excel) |

---

Project Structure

```
AI-Powered-AutoML/
├── backend/              ← FastAPI app
│   └── app/
│       ├── api_generator/      ← No-code REST API generator
│       ├── retraining/         ← Scheduled model retraining
│       ├── notifications/      ← Email + in-app alerts
│       ├── rbac/               ← Role-based access control
│       ├── monitoring/         ← Health checks + metrics
│       └── security/           ← Rate limiting + headers
├── frontend/             ← Next.js UI
├── chatbot/              ← AI chat assistant
├── dashboard/            ← Chart data service
├── data_quality/         ← Data quality analyzer
├── explainability/       ← SHAP explainability
├── model_registry/       ← Versioned model store
├── reports/              ← PDF + Excel generation
├── nginx/                ← Reverse proxy config
├── docker/               ← Dockerfiles
├── scripts/              ← Deploy + DB init scripts
└── docker-compose.yml    ← Full stack orchestration
```

---

Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/MuhammadAdnan586/AI-Powered-AutoML.git
cd AI-Powered-AutoML
```

### 2. Setup environment
```bash
cp .env.example .env
# Edit .env with your DB password, SECRET_KEY, ANTHROPIC_API_KEY
```

### 3. Deploy with Docker
```bash
bash scripts/deploy.sh
```

### 4. Access the platform
| Service | URL |
|---|---|
| Frontend App | http://localhost |
| API Docs (Swagger) | http://localhost:8000/docs |
| MLflow Tracking | http://localhost:5000 |

---

API Example — No-Code Prediction

```python
import requests

# Generate a prediction endpoint for your trained model
r = requests.post(
    "http://localhost:8000/api/v1/api-generator/generate",
    headers={"Authorization": "Bearer <your-jwt-token>"},
    json={"model_id": 5, "endpoint_name": "churn-predictor"}
)
slug = r.json()["slug"]
api_key = r.json()["api_key"]

# Call the public prediction endpoint (no login needed)
prediction = requests.post(
    f"http://localhost:8000/api/v1/api-generator/predict/{slug}",
    headers={"X-API-Key": api_key},
    json={"features": {"age": 35, "tenure": 12, "monthly_charges": 65.5}}
)
print(prediction.json())
# {"prediction": 0, "probability": [0.82, 0.18], "model_name": "XGBoost"}
```

---

Author

**Muhammad Adnan**
Data Scientist | ML Engineer
[LinkedIn](https://www.linkedin.com/in/m-adnan-12a816402) • [Portfolio](https://portfolio-eight-delta-7blam1yft8.vercel.app) • [GitHub](https://github.com/MuhammadAdnan586)
