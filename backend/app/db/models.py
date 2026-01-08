from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Cross-DB compatibility: Use standard JSON for SQLite, JSONB for Postgres
# We'll use a wrapper type if needed, but for now simple JSON works for SQLite.
# In Prod Postgres, usage of JSONB is preferred.

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    applicant_id = Column(String, nullable=False)
    status = Column(String, default="SUBMITTED") # SUBMITTED, SCORED, FINALIZED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    business_type = Column(String, nullable=True)
    
    # Relationships
    features = relationship("ApplicantFeatures", back_populates="application", uselist=False)
    inferences = relationship("ModelInference", back_populates="application")
    decisions = relationship("Decision", back_populates="application")
    reviews = relationship("ManualReview", back_populates="application")

class ApplicantFeatures(Base):
    __tablename__ = "applicant_features"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    
    # Snapshot
    annual_income = Column(Float)
    credit_score = Column(Integer)
    total_debt = Column(Float)
    raw_data = Column(JSON) # JSONB in PG
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    application = relationship("Application", back_populates="features")

class ModelInference(Base):
    __tablename__ = "model_inferences"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    
    model_version = Column(String, nullable=False)
    raw_probability = Column(Float, nullable=False)
    calibrated_pd = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    application = relationship("Application", back_populates="inferences")
    decision = relationship("Decision", back_populates="inference", uselist=False)

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    inference_id = Column(String, ForeignKey("model_inferences.id"), nullable=False)
    
    tier = Column(String, nullable=False) # APPROVE, REVIEW, REJECT
    confidence_score = Column(Float)
    reason_codes = Column(JSON)
    safety_flags = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    application = relationship("Application", back_populates="decisions")
    inference = relationship("ModelInference", back_populates="decision")

class ManualReview(Base):
    __tablename__ = "manual_reviews"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    decision_id = Column(String, ForeignKey("decisions.id"), nullable=True)
    
    original_tier = Column(String)
    final_decision = Column(String)
    justification = Column(Text)
    reviewer_id = Column(String)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    application = relationship("Application", back_populates="reviews")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String)
    entity_id = Column(String)
    action = Column(String)
    actor = Column(String)
    changes = Column(JSON)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
