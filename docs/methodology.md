# Methodology: AI Credit Scoring

## Problem Approach
The project treats credit evaluation as a **binary classification problem** (Default vs. Non-Default) combined with a **probabilistic risk scoring** regression task. The goal is to predict the likelihood of a loan default based on historical applicant data.

## Data Preprocessing

### 1. Feature Engineering
Raw data is transformed into meaningful features for the model:
- **Financial Ratios**:
  - `debt_to_income`: Total monthly debt obligations / Monthly income
  - `loan_to_revenue`: Loan amount / Annual revenue
- **Categorical Encoding**:
  - `business_type`: One-hot encoded (Manufacturing, Trading, Services)
  - `repayment_history`: Ordinal encoding (Poor=0, Average=1, Good=2)

### 2. Normalization
Numerical features (Revenue, Loan Amount) are scaled using **StandardScaler** (Z-score normalization) to ensure the model isn't biased towards larger magnitude numbers.

## Model Selection

We evaluated several algorithms for this task:

| Algorithm | Pros | Cons | Selected? |
|-----------|------|------|-----------|
| **Logistic Regression** | Interpretable, fast | Poor non-linear relationships | No |
| **Random Forest** | Robust to overfitting, handles non-linear data well | Less interpretable than linear models | **Yes** |
| **XGBoost** | High accuracy | Complex tuning required | Future Scope |
| **Neural Networks** | Deep learning capability | Requires massive data | No |

**Selected Model: Random Forest Classifier**
- **Why?**: It offers a great balance between accuracy and robustness. It handles mixed data types (numerical + categorical) well and provides feature importance metrics for explainability.

## Evaluation Metrics

The model is evaluated using:
1. **Accuracy**: Overall correctness of predictions.
2. **Precision**: Accuracy of positive predictions (minimizing false approvals).
3. **Recall (Sensitivity)**: Ability to capture actual defaults (minimizing risk).
4. **F1-Score**: Harmonic mean of Precision and Recall.
5. **ROC-AUC**: Ability to distinguish between classes.

## Decision Logic

The prediction output is mapped to a credit decision:

1. **Risk Score Calculation**:
   `Risk Score = (1 - Probability of Default) * 900`
   *(Scaled to resemble a CIBIL-like score)*

2. **Decision Thresholds**:
   - **Score > 750**: `Approved` (Low Risk)
   - **Score 650 - 750**: `Review` (Medium Risk)
   - **Score < 650**: `Rejected` (High Risk)

3. **Explainability**:
   We use feature importance extraction to identify *why* a decision was made (e.g., "High Debt-to-Income Ratio").
