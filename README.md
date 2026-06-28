<div align="center">

![Header](https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=180&section=header&text=AI-Powered%20AutoML%20SaaS%20Platform&fontSize=30&fontColor=ffffff&fontAlignY=38&desc=Upload%20a%20Dataset.%20Get%20a%20Trained%2C%20Explained%2C%20Deployable%20Model.&descAlignY=58&descSize=16&descColor=a8d8ea)

[![Run Locally](https://img.shields.io/badge/⚙️%20Run-Locally-0f2027?style=for-the-badge&logoColor=white)](#-quick-start)
[![License](https://img.shields.io/badge/License-MIT-2c5364?style=for-the-badge)](#-license)
[![Stars](https://img.shields.io/github/stars/MuhammadAdnan586/AI-Powered-AutoML?style=for-the-badge&color=2c5364&label=Stars)](https://github.com/MuhammadAdnan586/AI-Powered-AutoML/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/MuhammadAdnan586/AI-Powered-AutoML?style=for-the-badge&color=2c5364&label=Updated)](https://github.com/MuhammadAdnan586/AI-Powered-AutoML/commits/main)

</div>

---

### 📌 About the Project

**AI-Powered AutoML** is a full-stack SaaS platform that takes a user from a raw CSV/Excel file to a **trained, benchmarked, explained, and production-ready ML model** — with zero hand-written model code.

> Upload a dataset → the platform profiles it, cleans it, engineers features, trains 7+ algorithms in parallel, picks a winner, explains *why* it works with SHAP, and lets you deploy it as a live REST API — all from the browser.

Built end-to-end across **4 progressive modules**, going from core infrastructure to a genuinely deployable SaaS product (auth, billing-ready RBAC, monitoring, retraining, notifications).

---

### ✨ Key Features

**01 · Foundation & Infrastructure**
JWT authentication, role-based users, dataset upload/versioning (CSV/XLSX), and a live workspace dashboard summarising every dataset and its status.

**02 · AutoML Engine**
Automated preprocessing + feature engineering, then parallel training across **XGBoost, LightGBM, Random Forest, Gradient Boosting, Decision Tree, KNN, Logistic/Linear models**, with automatic best-model selection by score and a side-by-side benchmark view (accuracy, F1, precision, recall).

**03 · AI Intelligence Layer**
- 🔍 **SHAP Explainability** — per-feature impact, force & summary plots for any trained model
- 🧹 **Data Quality Analyzer** — quality score, missing-value map, outlier detection, correlation matrix
- 🤖 **AI Chat Assistant** (Gemini) — ask questions about your dataset in plain English, get auto-generated insights
- 📄 **Reports** — one-click professional PDF (ReportLab) and multi-sheet Excel (openpyxl) export
- 🗂️ **Model Registry** — version every training run, promote a "champion" model to production, compare versions

**04 · Production & SaaS Features**
- 🔌 **No-Code REST API Generator** — turn any trained model into a public, API-key-secured prediction endpoint in one click
- ⏰ **Scheduled Retraining** — cron-based auto-retraining with run logs
- 🔔 **Email + in-app notifications**
- 🛡️ **RBAC**, rate limiting, security headers, structured JSON logging
- 🐳 **Dockerized** full stack with Nginx reverse proxy + SSL-ready config

---

### 🖼️ Platform Preview

| 🏠 Workspace Dashboard | 🧹 Preprocessing & Data Quality |
|---|---|
| <img src="WhatsApp Image 2026-06-25 at 3.00.50 PM.jpeg" width="420"/> | <img src="WhatsApp Image 2026-06-25 at 3.00.50 PM (1).jpeg" width="420"/> |

| ✅ Dataset Ready for Training | 📊 Model Benchmark & Comparison |
|---|---|
| <img src="WhatsApp Image 2026-06-25 at 3.00.50 PM (2).jpeg" width="420"/> | <img src="WhatsApp Image 2026-06-25 at 3.00.51 PM.jpeg" width="420"/> |

| 🏆 Model Leaderboard & Downloads | 🤖 AI Intelligence Layer |
|---|---|
| <img src="WhatsApp Image 2026-06-25 at 3.00.51 PM (1).jpeg" width="420"/> | <img src="WhatsApp Image 2026-06-25 at 3.00.51 PM (2).jpeg" width="420"/> |

| 🔌 SaaS & Production — No-Code API Generator |
|---|
| <img src="WhatsApp Image 2026-06-25 at 3.00.52 PM.jpeg" width="860"/> |

> 💡 Tip: move these screenshots into a `screenshots/` folder with clean filenames (e.g. `dashboard.png`, `benchmark.png`) and update the paths above — GitHub renders them fine either way, but it looks cleaner in the repo file tree.

---

### 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2c5364?style=flat-square&logoColor=white)
![SHAP](https://img.shields.io/badge/SHAP-2c5364?style=flat-square&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini%20API-4285F4?style=flat-square&logo=google&logoColor=white)

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy + Alembic + PyMySQL |
| ML Engine | Scikit-learn, XGBoost, LightGBM, SHAP |
| AI Layer | Google Gemini API (`gemini-2.5-flash`) |
| Frontend | Next.js 14 + React 18 + TypeScript + Tailwind CSS |
| Database | MySQL 8.0 |
| Background Jobs | Celery + Redis + APScheduler |
| Reports | ReportLab (PDF), openpyxl (Excel) |
| Experiment Tracking | MLflow |
| Infra | Docker, Docker Compose, Nginx |
| Auth | JWT (python-jose) + bcrypt |

---

### 📡 API Overview

All routes are versioned under `/api/v1`. Full interactive docs are auto-generated by FastAPI at **`/docs`**.

| Module | Base Path | Examples |
|---|---|---|
| Auth & Users | `/api/v1/auth`, `/api/v1/users` | Register, login, refresh token, profile |
| Datasets | `/api/v1/datasets` | Upload, list, preview, delete |
| Preprocessing & Feature Engineering | `/api/v1/preprocessing`, `/api/v1/feature-engineering` | Cleaning, encoding, scaling, feature generation |
| AutoML & Benchmark | `/api/v1/automl`, `/api/v1/benchmark` | Train, compare models, get best model |
| Explainability | `/api/v1/explainability` | SHAP explanation, feature importance |
| Data Quality | `/api/v1/data-quality` | Quality score, missing values, correlation |
| AI Chat | `/api/v1/chat` | Chat with dataset, auto-insights |
| Reports | `/api/v1/reports` | Generate/download PDF & Excel reports |
| Model Registry | `/api/v1/model-registry` | Versions, champion model, compare |
| API Generator | `/api/v1/api-generator` | Turn a model into a public prediction endpoint |
| Retraining | `/api/v1/retraining` | Cron schedules, manual trigger, logs |
| Notifications | `/api/v1/notifications` | Email + in-app alerts |
| RBAC | `/api/v1/rbac` | Roles & permissions (admin) |
| Monitoring | `/api/v1/monitoring` | Health check, CPU/RAM/disk, API & model stats |

> Module 2/3/4 routers register safely — if one module fails to import, the rest of the API still boots. Check `GET /health` to see `loaded_modules` vs `failed_modules`.

---

### ⚙️ Quick Start

#### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0 running locally
- (Optional) Redis — needed for Celery background jobs
- A free [Gemini API key](https://aistudio.google.com/app/apikey) for the AI Chat Assistant

#### 1. Clone the repo
```bash
git clone https://github.com/MuhammadAdnan586/AI-Powered-AutoML.git
cd AI-Powered-AutoML
```

#### 2. Backend setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows  |  source venv/bin/activate on macOS/Linux
pip install -r requirements.txt

# create a .env file in backend/ — see Environment Variables below
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend setup (new terminal)
```bash
cd frontend-new
npm install
npm run dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

#### Or run everything with Docker
```bash
docker compose up --build
```
This spins up MySQL, the FastAPI backend, the frontend, and Nginx in one go.

---

### 🔑 Environment Variables (`backend/.env`)

```env
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/automl_saas
SECRET_KEY=your_jwt_secret_key
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=your_gemini_api_key_here
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=
SMTP_PASSWORD=
```

---

### 📂 Project Structure

```
AI-Powered-AutoML/
├── backend/
│   ├── app/
│   │   ├── auth/                  # Module 1 — JWT auth
│   │   ├── users/                 # Module 1 — user management
│   │   ├── datasets/               # Module 1 — upload, preview, versioning
│   │   ├── dashboard/               # Module 1 — workspace overview
│   │   ├── preprocessing/           # Module 2 — cleaning pipeline
│   │   ├── feature_engineering/     # Module 2 — feature generation
│   │   ├── automl/                  # Module 2 — multi-model training engine
│   │   ├── benchmark/                # Module 2 — model comparison
│   │   ├── mlflow_tracking/           # Module 2 — experiment tracking
│   │   ├── explainability/            # Module 3 — SHAP
│   │   ├── data_quality/              # Module 3 — quality analyzer
│   │   ├── chatbot/                    # Module 3 — Gemini chat assistant
│   │   ├── reports/                     # Module 3 — PDF/Excel export
│   │   ├── model_registry/               # Module 3 — versioning
│   │   ├── api_generator/                 # Module 4 — no-code API generator
│   │   ├── retraining/                     # Module 4 — scheduled retraining
│   │   ├── notifications/                   # Module 4 — email + in-app alerts
│   │   ├── rbac/                             # Module 4 — roles & permissions
│   │   ├── monitoring/                        # Module 4 — health & metrics
│   │   ├── security/                           # rate limiting, headers
│   │   ├── config/settings.py
│   │   └── main.py                              # FastAPI entry point
│   └── requirements.txt
├── frontend-new/                   # Active frontend — Next.js 14 + TS + Tailwind
│   ├── app/
│   ├── components/
│   └── services/
├── docker/                        # Dockerfiles (backend + frontend)
├── nginx/                          # Reverse proxy config
├── scripts/                        # deploy.sh, setup.sh, init.sql
└── docker-compose.yml
```

---

### 🧭 Module Status

| Module | Description | Status |
|---|---|---|
| 1 · Foundation & Infrastructure | Auth, datasets, dashboard | ✅ Complete |
| 2 · AutoML Engine | Preprocessing, training, benchmarking | ✅ Complete |
| 3 · AI Intelligence Layer | SHAP, data quality, AI chat, reports, registry | ✅ Complete |
| 4 · Production & SaaS Features | API generator, retraining, RBAC, monitoring, Docker | ✅ Complete |

---

### 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the [issues page](https://github.com/MuhammadAdnan586/AI-Powered-AutoML/issues) or open a pull request.

---

### 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,50:203a43,100:0f2027&height=100&section=footer)

Made with ❤️ by [**Muhammad Adnan**](https://github.com/MuhammadAdnan586) — Data Scientist | ML Engineer
[LinkedIn](https://www.linkedin.com/in/m-adnan-12a816402) • [Portfolio](https://portfolio-eight-delta-7blam1yft8.vercel.app)

</div>
