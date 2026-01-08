from fastapi import APIRouter
from app.schemas.decision import CreditApplication, DecisionResponse
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/test-simple")
def test_simple(application: CreditApplication):
    """Ultra-simple test endpoint"""
    # Auto-generate applicant_id
    if not application.applicant_id:
        application.applicant_id = f"APP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    
    # Calculate monthly_debt
    if application.monthly_debt_obligations is None:
        application.monthly_debt_obligations = application.total_debt / 12
    
    return DecisionResponse(
        application_id=application.applicant_id,
        decision_id=str(uuid.uuid4()),
        tier="Approve",
        risk_score=0.15,
        confidence_score=0.85,
        reason_flag="Test Mode",
        factors=[],
        counterfactuals=[],
        model_version="test_v1",
        status="SUCCESS",
        error_message=None
    )
