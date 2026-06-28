<div align="center">

![Header](https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=180&section=header&text=Customer%20Intelligence%20%26%20Revenue%20Optimization&fontSize=30&fontColor=ffffff&fontAlignY=38&desc=Four%20Business%20Questions%20Answered%20Directly%20From%20MySQL&descAlignY=58&descSize=16&descColor=a8d8ea)

[![View Project](https://img.shields.io/badge/🌐%20Run-Locally-0f2027?style=for-the-badge&logoColor=white)](#-quick-start)
[![License](https://img.shields.io/badge/License-MIT-2c5364?style=for-the-badge)](#-license)
[![Stars](https://img.shields.io/github/stars/MuhammadAdnan586/Customer-Intelligence-Revenue-Optimization?style=for-the-badge&color=2c5364&label=Stars)](https://github.com/MuhammadAdnan586/Customer-Intelligence-Revenue-Optimization/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/MuhammadAdnan586/Customer-Intelligence-Revenue-Optimization?style=for-the-badge&color=2c5364&label=Updated)](https://github.com/MuhammadAdnan586/Customer-Intelligence-Revenue-Optimization/commits/main)

</div>

---

### 📌 About the Project

**Customer Intelligence & Revenue Optimization** is a full-stack SQL-driven analytics dashboard that answers four real business questions straight from a MySQL database — **who your best customers are, whether they come back, what they buy together, and where revenue is leaking** — using the Olist Brazilian e-commerce dataset (2016–2018).

> Every number on the dashboard is computed live by a SQL query, not pre-baked — the FastAPI backend queries MySQL on each request and the Next.js frontend renders the result.

---

### 📊 Overview Metrics

| Metric | Value |
|---|---|
| 👥 Total Customers | **96,096** unique buyers |
| 💰 Revenue Analysed | **$15.42M** (delivered orders only) |
| 🧾 Avg Order Value | **$159.86** per delivered order |
| ⚠️ Revenue at Risk | **$270k** (canceled + unavailable) |

---

### ✨ Key Features

**01 · RFM Customer Segmentation**
93,357 customers scored on Recency, Frequency & Monetary value, grouped into actionable segments — *Champions, Loyal Customers, New Customers, At Risk, Need Attention, Lost*.
> 💡 Champions are just 1.1% of customers but spend 2.3x the overall average — the highest-value segment by far.

**02 · Repeat-Purchase & Cohort Retention**
Every delivered customer grouped by purchase frequency to test whether the business retains buyers or only acquires them once.
> 💡 97% of customers never returned — only 3% made a repeat purchase, a clear retention gap.

**03 · Product Affinity — Bought Together**
Multi-item orders broken into category pairs to reveal which products complement each other in a single basket.
> 💡 "cama mesa banho" + "moveis decoracao" appear together 71x more than any other pair — a strong cross-sell signal.

**04 · Revenue Leakage Detection**
Canceled and unavailable orders traced back to product category to size the revenue lost to fulfilment failure.
> 💡 1,234 canceled/unavailable orders cost $269,735.11 — the "cool stuff" category carries the largest single-category loss.

Each module ends with a data-backed **recommendation card**, turning the analysis into an actionable next step instead of just a chart.

---

### 🖼️ Dashboard Preview

| 🏠 Overview | 01 · RFM Customer Segmentation |
|---|---|
| ![Overview](images/overview.jpeg) | ![RFM](images/rfm.jpeg) |

| 02 · Repeat-Purchase & Cohort Retention | 03 · Product Affinity |
|---|---|
| ![Cohort](images/cohort.jpeg) | ![Affinity](images/affinity.jpeg) |

| 04 · Revenue Leakage Detection |
|---|
| ![Leakage](images/leakage.jpeg) |

---

### 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Recharts](https://img.shields.io/badge/Recharts-2c5364?style=flat-square&logoColor=white)

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy + PyMySQL |
| Frontend | Next.js 14 + React 18 |
| Charts | Recharts |
| Styling | Tailwind CSS |
| Icons | Lucide React |
| Database | MySQL 8.0 — Olist e-commerce dataset |

---

### 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/overview` | Header KPIs — customers, revenue, AOV, revenue at risk |
| GET | `/api/rfm` | RFM segment distribution |
| GET | `/api/cohort` | Repeat-purchase / cohort breakdown |
| GET | `/api/affinity` | Top product-category pairs bought together |
| GET | `/api/leakage` | Lost revenue by order status & category |

---

### ⚙️ Quick Start

This project runs as two separate services — **backend** (FastAPI + MySQL) and **frontend** (Next.js) — each in its own terminal.

```bash
# 1. Clone the repo
git clone https://github.com/MuhammadAdnan586/Customer-Intelligence-Revenue-Optimization.git
cd Customer-Intelligence-Revenue-Optimization

# 2. Backend setup
cd backend
python -m venv venv
venv\Scripts\activate          # Windows  |  source venv/bin/activate on macOS/Linux
pip install -r requirements.txt
copy .env.example .env          # then set your MySQL DB_PASSWORD
uvicorn main:app --reload --port 8000

# 3. Frontend setup (new terminal)
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API Docs (Swagger) | http://localhost:8000/docs |

> Full step-by-step setup, including common troubleshooting, is in [`RUN_LOCALLY.md`](RUN_LOCALLY.md).

---

### 📂 Project Structure

```
Customer-Intelligence-Revenue-Optimization/
├── images/
│   ├── overview.jpeg
│   ├── rfm.jpeg
│   ├── cohort.jpeg
│   ├── affinity.jpeg
│   └── leakage.jpeg
├── backend/
│   ├── main.py            # FastAPI app & routes
│   ├── database.py        # SQLAlchemy engine / MySQL connection
│   ├── queries.py         # All SQL: overview, RFM, cohort, affinity, leakage
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── components/
│   │   │   ├── KpiCard.js
│   │   │   ├── RfmSection.js
│   │   │   ├── CohortSection.js
│   │   │   ├── AffinitySection.js
│   │   │   ├── LeakageSection.js
│   │   │   ├── InsightNote.js
│   │   │   └── SectionHeader.js
│   │   ├── page.js
│   │   └── layout.js
│   └── package.json
└── RUN_LOCALLY.md
```

---

### 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the [issues page](https://github.com/MuhammadAdnan586/Customer-Intelligence-Revenue-Optimization/issues) or open a pull request.

---

### 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,50:203a43,100:0f2027&height=100&section=footer)

Made with ❤️ by [**Muhammad Adnan**](https://github.com/MuhammadAdnan586) — Data Scientist | ML Engineer
[LinkedIn](https://www.linkedin.com/in/m-adnan-12a816402) • [Portfolio](https://portfolio-eight-delta-7blam1yft8.vercel.app)

</div>
