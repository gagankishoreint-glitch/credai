from pydantic import BaseModel
from typing import Optional, List

class CreditApplication(BaseModel):
    # Optional - will be auto-generated if not provided
    applicant_id: Optional[str] = None
    
    # Required core fields
    age: int
    annual_income: float
    total_debt: float
    credit_score: int
    business_type: str = "Other"
    
    # Optional - will be calculated if not provided
    monthly_debt_obligations: Optional[float] = None
    
    # Optional additional fields
    doc_verified_income: Optional[float] = None
    assets_total: Optional[float] = 0.0
    employment_years: Optional[int] = 0
    recent_inquiries: Optional[int] = 0
    delinquency_count: Optional[int] = 0
    payment_history_months: Optional[int] = 0
    credit_utilization: Optional[float] = 0.0
    
    class Config:
        extra = "allow"  # Allow extra fields for Model

class DecisionResponse(BaseModel):
    application_id: str
    decision_id: str
    tier: str
    risk_score: float
    confidence_score: float
    reason_flag: Optional[str] = None
    factors: Optional[List[dict]] = []
    counterfactuals: Optional[List[dict]] = []
    model_version: Optional[str] = None
    status: str  # "SUCCESS", "REJECTED_SAFETY"
    error_message: Optional[str] = None
