from fastapi import APIRouter, Depends, HTTPException
from ..services.credit_service import credit_service
from ..schemas.schemas import ApplicationCreate, EvaluationResponse
import datetime

router = APIRouter(prefix="/api/predict", tags=["predict"])

@router.post("/", response_model=EvaluationResponse)
async def predict_risk(application: ApplicationCreate):
    """
    Get a risk prediction without saving to the database.
    Used for What-If analysis and real-time simulations.
    """
    try:
        # Convert Pydantic model to dict
        app_data = application.model_dump()
        
        # Evaluate
        result = credit_service.evaluate_application(app_data)
        
        # Return transient response
        return {
            "id": 0, # Dummy ID
            "application_id": 0,
            "risk_score": result['risk_score'],
            "default_probability": result['default_probability'],
            "recommendation": result['recommendation'],
            "confidence_score": result['confidence_score'],
            "model_version": result['model_version'],
            "evaluated_at": datetime.datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
