"""
FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import from app
from app.models.database import engine, Base
from app.api import applications, evaluations
from app.schemas.schemas import HealthCheck

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Driven Smart Credit Evaluation System",
    description="Automated creditworthiness assessment for business loan applications",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(applications.router)
app.include_router(evaluations.router)
from app.api import predict
app.include_router(predict.router)
from app.api import metrics
app.include_router(metrics.router)

@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Driven Smart Credit Evaluation System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """Health check endpoint"""
    from app.services.credit_service import credit_service
    
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        model_loaded=credit_service.model is not None
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
