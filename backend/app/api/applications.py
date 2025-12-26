"""
Application API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models.database import get_db
from ..models.models import Application, ApplicationStatus
from ..schemas.schemas import ApplicationCreate, ApplicationResponse
from ..services.credit_service import credit_service
from datetime import datetime

router = APIRouter(prefix="/api/applications", tags=["applications"])

@router.post("/", response_model=ApplicationResponse, status_code=201)
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """Submit a new loan application"""
    # Generate applicant ID
    last_app = db.query(Application).order_by(Application.id.desc()).first()
    next_id = (last_app.id + 1) if last_app else 1
    applicant_id = f"APP{str(next_id).zfill(6)}"
    
    # Create application
    db_application = Application(
        applicant_id=applicant_id,
        business_type=application.business_type.value,
        years_in_operation=application.years_in_operation,
        annual_revenue=application.annual_revenue,
        monthly_cashflow=application.monthly_cashflow,
        loan_amount_requested=application.loan_amount_requested,
        credit_score=application.credit_score,
        existing_loans=application.existing_loans,
        debt_to_income_ratio=application.debt_to_income_ratio,
        collateral_value=application.collateral_value,
        repayment_history=application.repayment_history.value,
        status=ApplicationStatus.PENDING
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    return db_application

@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all applications with optional filtering"""
    query = db.query(Application)
    
    if status:
        query = query.filter(Application.status == status)
    
    applications = query.offset(skip).limit(limit).all()
    return applications

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific application by ID"""
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application

@router.post("/{application_id}/evaluate")
async def evaluate_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Trigger credit evaluation for an application"""
    # Get application
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status == ApplicationStatus.EVALUATED:
        raise HTTPException(status_code=400, detail="Application already evaluated")
    
    # Prepare data for evaluation
    application_data = {
        'business_type': application.business_type,
        'years_in_operation': application.years_in_operation,
        'annual_revenue': application.annual_revenue,
        'monthly_cashflow': application.monthly_cashflow,
        'loan_amount_requested': application.loan_amount_requested,
        'credit_score': application.credit_score,
        'existing_loans': application.existing_loans,
        'debt_to_income_ratio': application.debt_to_income_ratio,
        'collateral_value': application.collateral_value,
        'repayment_history': application.repayment_history
    }
    
    # Evaluate using credit service
    try:
        evaluation_result = credit_service.evaluate_application(application_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
    
    # Import here to avoid circular import
    from ..models.models import Evaluation
    
    # Create evaluation record
    db_evaluation = Evaluation(
        application_id=application.id,
        risk_score=evaluation_result['risk_score'],
        default_probability=evaluation_result['default_probability'],
        recommendation=evaluation_result['recommendation'],
        confidence_score=evaluation_result['confidence_score'],
        model_version=evaluation_result['model_version'],
        feature_importance=evaluation_result['feature_importance']
    )
    
    # Update application status
    application.status = ApplicationStatus.EVALUATED
    application.updated_at = datetime.utcnow()
    
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    
    return {
        "message": "Evaluation completed successfully",
        "evaluation_id": db_evaluation.id,
        "risk_score": db_evaluation.risk_score,
        "recommendation": db_evaluation.recommendation
    }
