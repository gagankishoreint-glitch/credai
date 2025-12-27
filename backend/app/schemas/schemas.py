"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict
from enum import Enum

class BusinessType(str, Enum):
    MANUFACTURING = "Manufacturing"
    TRADING = "Trading"
    SERVICES = "Services"

class RepaymentHistory(str, Enum):
    GOOD = "Good"
    AVERAGE = "Average"
    POOR = "Poor"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    EVALUATED = "evaluated"

class Recommendation(str, Enum):
    APPROVE = "approve"
    REVIEW = "review"
    REJECT = "reject"

# Application Schemas
class ApplicationCreate(BaseModel):
    business_type: BusinessType
    years_in_operation: int = Field(ge=0, le=100)
    annual_revenue: float = Field(gt=0)
    monthly_cashflow: float
    loan_amount_requested: float = Field(gt=0)
    credit_score: int = Field(ge=300, le=900)
    existing_loans: int = Field(ge=0)
    debt_to_income_ratio: float = Field(ge=0)
    collateral_value: float = Field(ge=0)
    repayment_history: RepaymentHistory
    
    # New optional fields for AI Model (Fallback to defaults if missing)
    gst_turnover: float = Field(default=0.0, ge=0)
    ebitda_margin: float = Field(default=0.1, ge=-1.0, le=1.0)
    net_margin: float = Field(default=0.05, ge=-1.0, le=1.0)
    loan_tenure_months: int = Field(default=36, ge=0)
    loan_purpose: str = "Working Capital"
    promoter_credit_score: int = Field(default=650, ge=300, le=900)
    promoter_exp_years: int = Field(default=5, ge=0)
    collateral_type: str = "None"
    total_debt: float = Field(default=0.0, ge=0)
    existing_emi: float = Field(default=0.0, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_type": "Manufacturing",
                "years_in_operation": 10,
                "annual_revenue": 5000000,
                "monthly_cashflow": 300000,
                "loan_amount_requested": 2000000,
                "credit_score": 720,
                "existing_loans": 2,
                "debt_to_income_ratio": 0.45,
                "collateral_value": 3000000,
                "repayment_history": "Good",
                "loan_tenure_months": 36
            }
        }

class ApplicationResponse(BaseModel):
    id: int
    applicant_id: str
    business_type: str
    years_in_operation: int
    annual_revenue: float
    monthly_cashflow: float
    loan_amount_requested: float
    credit_score: int
    existing_loans: int
    debt_to_income_ratio: float
    collateral_value: float
    repayment_history: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Evaluation Schemas
class EvaluationResponse(BaseModel):
    id: int
    application_id: int
    risk_score: float
    default_probability: float
    recommendation: str
    confidence_score: float
    model_version: str
    evaluated_at: datetime
    
    class Config:
        from_attributes = True

class PredictionExplanation(BaseModel):
    feature: str
    importance: float
    value: float

class DetailedEvaluationResponse(BaseModel):
    evaluation: EvaluationResponse
    application: ApplicationResponse
    top_features: list[PredictionExplanation]
    
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    model_loaded: bool
