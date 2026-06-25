<div align="center">

![Header](https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=180&section=header&text=AI-Powered%20AutoML%20Platform&fontSize=40&fontColor=ffffff&fontAlignY=38&desc=Upload%20%E2%86%92%20Train%20%E2%86%92%20Explain%20%E2%86%92%20Deploy%20%E2%80%94%20No%20Code%20Required&descAlignY=58&descSize=16&descColor=a8d8ea)

[![View Project](https://img.shields.io/badge/🌐%20Deploy-Docker%20Compose-0f2027?style=for-the-badge&logoColor=white)](#%EF%B8%8F-quick-start)
[![License](https://img.shields.io/badge/License-MIT-2c5364?style=for-the-badge)](#-license)
[![Stars](https://img.shields.io/github/stars/MuhammadAdnan586/AI-Powered-AutoML?style=for-the-badge&color=2c5364&label=Stars)](https://github.com/MuhammadAdnan586/AI-Powered-AutoML/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/MuhammadAdnan586/AI-Powered-AutoML?style=for-the-badge&color=2c5364&label=Updated)](https://github.com/MuhammadAdnan586/AI-Powered-AutoML/commits/main)

</div>

---

### 📌 About the Project

**AI-Powered AutoML Platform** is a production-ready, full-stack **Automated Machine Learning SaaS** that lets users upload a dataset, automatically train and compare ML models, understand *why* a model predicted what it did, and deploy a live prediction API — without writing a single line of code.

> Building and deploying ML models normally needs deep technical expertise, weeks of setup, and expensive infrastructure. This platform compresses that entire lifecycle — from raw data to a production API — into minutes.

---

### ✨ Key Features

**🔹 Core AutoML Engine**
- Automated model selection and hyperparameter tuning
- Multi-algorithm benchmarking (Random Forest, XGBoost, Logistic Regression, etc.)
- Feature engineering and data preprocessing pipeline

**🔹 AI Intelligence Layer**
- **SHAP Explainability** — understand why the model made each prediction
- **Data Quality Analyzer** — quality score, outlier detection, correlation matrix
- **AI Chat Assistant** — ask questions about your dataset in natural language
- **Auto PDF & Excel Reports** — one-click professional report generation
- **Model Registry** — versioned model store with champion/staging promotion

**🔹 Production & SaaS Features**
- **No-Code REST API Generator** — one-click API deployment for any trained model
- **Scheduled Retraining** — cron-based automatic model retraining
- **Role-Based Access Control (RBAC)** — admin, user, viewer roles
- **Email & In-App Notifications** — alerts for training completion and anomalies
- **Monitoring & Health Checks** — CPU/RAM/Disk metrics and API usage stats
- **Structured JSON Logging** — production-grade logging middleware
- **Nginx Reverse Proxy + SSL** — secure deployment ready

---

### 🖼️ Screenshots

<table>
  <tr>
    <td align="center" width="50%">
      <b>📊 Dashboard</b><br/><br/>
      <img src="screenshot-dashboard.jpg" width="100%" alt="AutoML Dashboard"/>
    </td>
    <td align="center" width="50%">
      <b>🧹 Preprocessing — Dataset Preview & Quality Report</b><br/><br/>
      <img src="screenshot-preprocessing.jpg" width="100%" alt="Preprocessing and data quality report"/>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <b>🧠 Train Models — Feature-Engineered Dataset Ready</b><br/><br/>
      <img src="screenshot-train.jpg" width="100%" alt="Train models step"/>
    </td>
    <td align="center" width="50%">
      <b>🏆 Results — Best Performing Model</b><br/><br/>
      <img src="screenshot-results.jpg" width="100%" alt="Best performing model results"/>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <b>📋 Model Leaderboard</b><br/><br/>
      <img src="screenshot-leaderboard.jpg" width="100%" alt="Model leaderboard ranking"/>
    </td>
    <td align="center" width="50%">
      <b>🤖 AI Intelligence Layer</b><br/><br/>
      <img src="screenshot-ai-layer.jpg" width="100%" alt="AI Intelligence Layer"/>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <b>⚙️ SaaS & Production — No-Code API Generator</b><br/><br/>
      <img src="screenshot-saas.jpg" width="60%" alt="SaaS and production features"/>
    </td>
  </tr>
</table>

---

### 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-0073C5?style=flat-square&logo=xgboost&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat-square&logo=nginx&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat-square&logo=mlflow&logoColor=white)

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

### ⚙️ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/MuhammadAdnan586/AI-Powered-AutoML.git
cd AI-Powered-AutoML

# 2. Setup environment
cp .env.example .env
# Edit .env with your DB password, SECRET_KEY, ANTHROPIC_API_KEY

# 3. Deploy with Docker
bash scripts/deploy.sh
```

| Service | URL |
|---|---|
| Frontend App | http://localhost |
| API Docs (Swagger) | http://localhost:8000/docs |
| MLflow Tracking | http://localhost:5000 |

---

### 📂 Project Structure
