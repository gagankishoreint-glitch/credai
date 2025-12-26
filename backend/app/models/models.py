"""
Database ORM Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    EVALUATED = "evaluated"

class Recommendation(str, enum.Enum):
    APPROVE = "approve"
    REVIEW = "review"
    REJECT = "reject"

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(String, unique=True, index=True)
    
    # Business information
    business_type = Column(String)
    years_in_operation = Column(Integer)
    
    # Financial information
    annual_revenue = Column(Float)
    monthly_cashflow = Column(Float)
    loan_amount_requested = Column(Float)
    credit_score = Column(Integer)
    existing_loans = Column(Integer)
    debt_to_income_ratio = Column(Float)
    collateral_value = Column(Float)
    repayment_history = Column(String)
    
    # Status
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    evaluation = relationship("Evaluation", back_populates="application", uselist=False)

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True)
    
    # Risk assessment
    risk_score = Column(Float)  # 0-100 scale
    default_probability = Column(Float)  # 0-1 probability
    recommendation = Column(SQLEnum(Recommendation))
    confidence_score = Column(Float)  # 0-1
    
    # Model information
    model_version = Column(String)
    feature_importance = Column(Text)  # JSON string
    
    # Timestamps
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    application = relationship("Application", back_populates="evaluation")
