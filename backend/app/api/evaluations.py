"""
Evaluation API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.models import Evaluation, Application
from ..schemas.schemas import EvaluationResponse, DetailedEvaluationResponse, PredictionExplanation
import json

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])

@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """Get evaluation result by ID"""
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    return evaluation

@router.get("/{evaluation_id}/detailed", response_model=DetailedEvaluationResponse)
async def get_detailed_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed evaluation with application data and explanations"""
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    # Get associated application
    application = evaluation.application
    
    # Parse feature importance
    feature_importance = json.loads(evaluation.feature_importance)
    top_features = [
        PredictionExplanation(**feat) for feat in feature_importance
    ]
    
    return DetailedEvaluationResponse(
        evaluation=evaluation,
        application=application,
        top_features=top_features
    )

@router.get("/application/{application_id}", response_model=EvaluationResponse)
async def get_evaluation_by_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get evaluation for a specific application"""
    evaluation = db.query(Evaluation).filter(
        Evaluation.application_id == application_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=404, 
            detail="No evaluation found for this application"
        )
    
    return evaluation
