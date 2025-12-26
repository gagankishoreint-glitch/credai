# AI-Driven Smart Credit Evaluation System

> **Academic Project: Intelligent Financial Decision Support System**

## 📌 Project Overview
The **AI-Driven Smart Credit Evaluation System** is a modern web application designed to automate and enhance the creditworthiness assessment process for business loans. By leveraging Machine Learning techniques, the system analyzes applicant data to generate instant, consistent, and data-driven risk scores, significantly reducing the manual effort required by human underwriters.

**Live Demo:** [https://credit-evaluation-system.vercel.app](https://credit-evaluation-system.vercel.app)

---

## 🚀 Key Features

### Core Functionality
- **Automated Credit Scoring**: ML-based prediction of default probability.
- **Instant Decisioning**: Real-time Approved/Rejected/Review recommendations.
- **Risk Score Generation**: 300-900 credit score simulation.

### Intelligent Tools
- **Loan Comparison Engine**: Side-by-side offer comparison with weighted priority scoring.
- **True Cost Calculator**: Advanced EMI calculator revealing hidden fees and real monthly burden.
- **Document Analyzer**: Intelligent parser for bank statements to extract credit strength signals.
- **Market Benchmarks**: Dashboard showing regional interest rate trends and market stats.

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript | Lightweight, fast, no build complexity |
| **Backend** | Python (FastAPI) | High performance, native async support |
| **ML Engine** | Scikit-learn, Pandas | Robust standard for tabular data ML |
| **Data** | CSV / Synthetic | Flexible, easy to generate and manipulate |
| **Deployment** | Vercel (Frontend), Railway (Backend) | Scalable serverless architecture |

---

## 📂 Project Structure

```bash
credit-evaluation-system/
├── backend/
│   ├── main.py              # FastAPI Application Entry Point
│   ├── model.py             # ML Model & Prediction Logic
│   ├── generate_dataset.py  # Synthetic Data Generator
│   └── data/
│       └── business_credit_data.csv
├── frontend/
│   ├── index.html           # Main Application Form
│   ├── compare.html         # Loan Comparison Tool
│   ├── calculator.html      # EMI Calculator
│   ├── analyzer.html        # Document Analyzer
│   ├── benchmarks.html      # Market Dashboard
│   └── css/                 # Apple-Design System Styles
├── docs/
│   ├── architecture.md      # System Architecture
│   ├── methodology.md       # AI/ML Methodology
│   └── user_manual.md       # usage Guide
└── models/                  # Saved .pkl model files
```

---

## 📊 Dataset Description
The system is trained on a synthetic dataset designed to mimic realistic business credit profiles.
- **Source**: Generated via `backend/generate_dataset.py`
- **Size**: 5,000 Records
- **Key Features**:
  - `annual_revenue` & `monthly_cashflow`
  - `credit_score` & `repayment_history`
  - `debt_to_income_ratio`
  - `years_in_operation`
  - `business_type` (Manufacturing, Trading, Services)

---

## 🔧 Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js (optional, for Vercel CLI)

### 1. Clone Repository
```bash
git clone https://github.com/gagankishoreint-glitch/credit-evaluation-system.git
cd credit-evaluation-system
```

### 2. Backend Setup
```bash
# Install dependencies
pip install fastapi uvicorn pandas scikit-learn numpy

# Generate Dataset
python backend/generate_dataset.py

# Run API Server
python backend/main.py
```
*Server runs at http://localhost:8000*

### 3. Frontend Setup
Simply open `frontend/index.html` in your browser, or serve using:
```bash
npx serve frontend
```

---

## 📈 Future Enhancements
- **Explainable AI Integration**: SHAP/LIME visualization for detailed decision reasoning.
- **OCR Integration**: Tesseract/AWS Textract for real document scanning.
- **Blockchain Ledger**: Immutable record keeping of credit decisions.

---

## 👥 Contributors
- **Gagan Kishore** - Lead Developer & AI Architect

---

*This project was developed as part of the Advanced Credit Intelligence academic curriculum.*
