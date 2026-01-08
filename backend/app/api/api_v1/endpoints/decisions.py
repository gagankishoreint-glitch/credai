from fastapi import APIRouter, HTTPException, Depends, Body
from app.schemas.decision import CreditApplication, DecisionResponse
from app.services.model_service import model_service
from app.services.policy_engine import policy_engine
from app.services.audit_log import audit_service
from app.services.explainability import xai_service
from app.db.session import get_db
from app.db.models import Application, ApplicantFeatures, ModelInference, Decision, ManualReview
from app.api.deps import get_current_user, RoleChecker, User
from sqlalchemy.orm import Session
import uuid
from pydantic import BaseModel, constr

router = APIRouter()

# Schema for Override
class OverrideRequest(BaseModel):
    decision_id: str
    new_tier: str # "Approve", "Reject"
    justification: constr(min_length=20)

@router.post("/override")
def override_decision(
    request: OverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["underwriter", "admin"]))
):
    """
    Manual Override of an AI Decision.
    Requires 'Underwriter' role and valid justification.
    """
    # 1. Fetch Original Decision
    decision = db.query(Decision).filter(Decision.id == request.decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision ID not found")
        
    # 2. Log Override
    review_record = ManualReview(
        id=str(uuid.uuid4()),
        application_id=decision.application_id,
        decision_id=decision.id,
        original_tier=decision.tier,
        final_decision=request.new_tier,
        justification=request.justification,
        reviewer_id=current_user.username
    )
    
    db.add(review_record)
    
    # Audit Log
    audit_service.log_event("MANUAL_OVERRIDE", {
        "decision_id": request.decision_id,
        "old": decision.tier,
        "new": request.new_tier,
        "actor": current_user.username
    })
    
    db.commit()
    return {"status": "SUCCESS", "message": "Override recorded."}

@router.post("/decide", response_model=DecisionResponse)
def predict_credit_risk(application: CreditApplication):
    """
    Credit decision endpoint with enhanced explainability
    """
    # Auto-generate applicant_id if not provided
    if not application.applicant_id:
        from datetime import datetime
        application.applicant_id = f"APP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    
    # Calculate monthly_debt_obligations if not provided
    if application.monthly_debt_obligations is None:
        application.monthly_debt_obligations = application.total_debt / 12
    
    # Convert to Dict
    data = application.dict()
    
    # Initialize response variables
    decision_tier = "Review"
    confidence = 0.5
    flag = "Processing"
    prob_default = 0.5
    status_msg = "SUCCESS"
    err = None
    model_ver = "ensemble_v1"
    decision_id = str(uuid.uuid4())

    # Safety Check
    try:
        passed, msg = policy_engine.check_safety(data)
        if not passed:
            decision_tier = "Reject"
            status_msg = "REJECTED_SAFETY"
            err = msg
            try:
                audit_service.log_event("SAFETY_BLOCK", {"app_id": application.applicant_id, "reason": msg})
            except:
                pass
    except Exception as safety_error:
        print(f"Safety check error: {safety_error}")
        passed = True
    
    # Risk Scoring & Decision
    if passed:
        try:
            # Model inference
            inference_result = model_service.predict_probability(data)
            prob_default = inference_result.get("calibrated_pd", 0.5)
            model_conf = inference_result.get("confidence_score", 0.5)
            model_ver = inference_result.get("model_version", "ensemble_v1")
            
            # Policy decision
            try:
                decision_tier, confidence, flag = policy_engine.apply_decision_logic(
                    prob_default, 
                    business_type=application.business_type
                )
            except Exception as policy_error:
                print(f"Policy engine error: {policy_error}")
                if prob_default < 0.20:
                    decision_tier, confidence, flag = "Approve", 0.8, "Low Risk"
                elif prob_default > 0.45:
                    decision_tier, confidence, flag = "Reject", 0.8, "High Risk"
                else:
                    decision_tier, confidence, flag = "Review", 0.5, "Gray Zone"
            
            # Enhanced Explainability
            try:
                # Use existing xai_service
                import pandas as pd
                df_input = pd.DataFrame([data])
                
                # Enrich with derived features for XAI if needed (simple heuristic)
                if "utilization_rate" not in df_input.columns:
                     df_input["utilization_rate"] = data.get("credit_utilization", 0)
                
                explanation = xai_service.generate_explanation(df_input, None)
                
                # Log success
                try:
                    audit_service.log_event("DECISION_MADE", {
                        "app_id": application.applicant_id, 
                        "tier": decision_tier,
                        "pd": prob_default
                    })
                except:
                    pass
                
                # Return enhanced response
                return DecisionResponse(
                    application_id=application.applicant_id,
                    decision_id=decision_id,
                    tier=decision_tier,
                    risk_score=prob_default,
                    confidence_score=confidence,
                    reason_flag=flag,
                    factors=explanation.get("top_contributors", []),
                    counterfactuals=[{"action": cf} for cf in explanation.get("counterfactuals", [])],
                    model_version=model_ver,
                    status="SUCCESS",
                    error_message=None
                )
                
            except Exception as enhance_error:
                print(f"Enhancement error (falling back to basic): {enhance_error}")
                # Fallback to basic explanation
                return DecisionResponse(
                    application_id=application.applicant_id,
                    decision_id=decision_id,
                    tier=decision_tier,
                    risk_score=prob_default,
                    confidence_score=confidence,
                    reason_flag=flag,
                    factors=[],
                    counterfactuals=[],
                    model_version=model_ver,
                    status="SUCCESS",
                    error_message=None
                )
            
        except Exception as e:
            print(f"Inference Error: {e}")
            import traceback
            traceback.print_exc()
            return DecisionResponse(
                application_id=application.applicant_id,
                decision_id=decision_id,
                tier="Review",
                risk_score=0.5,
                confidence_score=0.3,
                reason_flag="System Error - Manual Review Required",
                factors=[],
                counterfactuals=[],
                model_version="error_fallback",
                status="ERROR",
                error_message=f"Processing error: {str(e)[:100]}"
            )
    
    # Return response for safety failures
    return DecisionResponse(
        application_id=application.applicant_id,
        decision_id=decision_id,
        tier=decision_tier,
        risk_score=prob_default,
        confidence_score=confidence,
        reason_flag=flag,
        factors=[],
        counterfactuals=[],
        model_version=model_ver,
        status=status_msg,
        error_message=err
    )
