import json
import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

METRICS_PATH = "backend/ml_pipeline/metrics.json"

@router.get("/")
async def get_model_metrics():
    """
    Serve the model training metrics and fairness analysis.
    """
    if not os.path.exists(METRICS_PATH):
        raise HTTPException(status_code=404, detail="Metrics file not found. Please train the model first.")
    
    try:
        with open(METRICS_PATH, "r") as f:
            metrics = json.load(f)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading metrics: {str(e)}")
