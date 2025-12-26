# AI-Driven Smart Credit Evaluation System

An intelligent decision-support system for automating business loan credit risk assessment using machine learning.

##  Project Overview

This system automates creditworthiness assessment for business loan applications, reducing decision time and providing data-driven insights to underwriters.

### Features

- **Synthetic Dataset Generation**: 5,000 realistic business loan records
- **ML Models**: Logistic Regression, Random Forest, XGBoost with hyperparameter tuning
- **Explainable AI**: SHAP-based feature importance and prediction explanations
- **RESTful API**: FastAPI backend with automatic API documentation
- **Modern UI**: Premium glassmorphism design with real-time validation
- **Risk Assessment**: 0-100 risk scoring with confidence metrics
- **Decision Support**: Automated approve/review/reject recommendations

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: SQLite (development) / PostgreSQL (production)
- **ML Libraries**: Scikit-learn, XGBoost, SHAP
- **ORM**: SQLAlchemy

### Frontend
- **Core**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Glassmorphism, CSS Grid, Gradients
- **Fonts**: Google Fonts (Inter)

### Machine Learning
- Classification Models: Logistic Regression, Random Forest, XGBoost
- Preprocessing: StandardScaler, LabelEncoder
- Explainability: SHAP (SHapley Additive exPlanations)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd d:\projects\credit-evaluation-system
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Generate synthetic dataset**
   ```bash
   python ml_pipeline/scripts/generate_dataset.py
   ```

4. **Preprocess data**
   ```bash
   python ml_pipeline/scripts/data_preprocessing.py
   ```

5. **Train ML models**
   ```bash
   python ml_pipeline/scripts/model_training.py
   ```

6. **Generate explainability artifacts** (optional)
   ```bash
   python ml_pipeline/scripts/model_explainability.py
   ```

7. **Start the backend server**
   ```bash
   python main.py
   ```
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

8. **Open the frontend**
   - Navigate to `frontend/index.html` in your browser
   - Or use a local server like Live Server in VS Code

### Access Points

- **Frontend**: Open `frontend/index.html`
- **API Documentation**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## 📂 Project Structure

```
credit-evaluation-system/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── applications.py
│   │   │   └── evaluations.py
│   │   ├── models/           # Database models
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── schemas/          # Pydantic schemas
│   │   │   └── schemas.py
│   │   └── services/         # Business logic
│   │       └── credit_service.py
│   ├── ml_pipeline/
│   │   ├── data/             # Generated datasets
│   │   ├── models/           # Trained models
│   │   └── scripts/          # ML scripts
│   │       ├── generate_dataset.py
│   │       ├── data_preprocessing.py
│   │       ├── model_training.py
│   │       └── model_explainability.py
│   ├── main.py               # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── css/
│   │   └── styles.css        # Design system
│   ├── js/
│   │   ├── api.js            # API client
│   │   ├── app.js            # Application form
│   │   └── dashboard.js      # Dashboard logic
│   ├── index.html            # Application form
│   ├── dashboard.html        # Applications list
│   └── evaluation.html       # Results display
└── README.md
```

## 🎯 Usage Workflow

1. **Submit Application**: Fill out the loan application form with business details
2. **Dashboard Review**: View all submitted applications in the dashboard
3. **Trigger Evaluation**: Click "Evaluate" to run AI assessment
4. **View Results**: See risk score, recommendation, and feature importance

## 📊 Dataset Specification

The system uses a synthetic dataset with the following columns:

- `applicant_id`: Unique identifier
- `business_type`: Manufacturing/Trading/Services
- `years_in_operation`: 0-50 years
- `annual_revenue`: Annual revenue in ₹
- `monthly_cashflow`: Average monthly cash flow
- `loan_amount_requested`: Requested loan amount
- `credit_score`: 300-900 credit score
- `existing_loans`: Number of active loans
- `debt_to_income_ratio`: Financial ratio
- `collateral_value`: Asset value
- `repayment_history`: Good/Average/Poor
- `default_flag`: Target variable (0/1)

## 🔍 API Endpoints

### Applications
- `POST /api/applications/` - Submit new application
- `GET /api/applications/` - List all applications
- `GET /api/applications/{id}` - Get specific application
- `POST /api/applications/{id}/evaluate` - Trigger evaluation

### Evaluations
- `GET /api/evaluations/{id}` - Get evaluation result
- `GET /api/evaluations/{id}/detailed` - Get detailed evaluation with explanations
- `GET /api/evaluations/application/{application_id}` - Get evaluation by application

## 🧪 Model Performance

The system trains three models and automatically selects the best performer:
- Logistic Regression (baseline)
- Random Forest (ensemble)
- XGBoost (gradient boosting)

Expected performance: >75% accuracy with ROC-AUC > 0.80

## 📝 Development Notes

- The system uses SQLite for development; configure PostgreSQL for production
- CORS is enabled for all origins in development; restrict in production
- Feature engineering creates additional features for better predictions
- SHAP explainability provides transparency for decision-making

## 🤝 Contributing

This is an academic/demonstration project. For production use:
1. Use real historical loan data
2. Implement proper authentication
3. Add comprehensive testing
4. Set up CI/CD pipeline
5. Configure production database
6. Implement logging and monitoring

## 📄 License

Educational/Academic Project

## 👥 Support

For issues or questions, refer to the project documentation or API docs at `/docs`.
