"""
Test endpoint directly
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class CreditApplication(BaseModel):
    applicant_id: Optional[str] = None
    age: int
    annual_income: float
    total_debt: float
    credit_score: int
    business_type: str = "Other"
    monthly_debt_obligations: Optional[float] = None

@app.post("/test")
def test_endpoint(application: CreditApplication):
    # Auto-generate applicant_id if not provided
    if not application.applicant_id:
        from datetime import datetime
        import uuid
        application.applicant_id = f"APP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    
    # Calculate monthly_debt_obligations if not provided
    if application.monthly_debt_obligations is None:
        application.monthly_debt_obligations = application.total_debt / 12
    
    return {
        "status": "success",
        "applicant_id": application.applicant_id,
        "monthly_debt": application.monthly_debt_obligations
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
