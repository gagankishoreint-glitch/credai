from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_service import document_service

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a bank statement (PDF/CSV) to extract financial Verification Indicators.
    Returns: { "doc_verified_income": float, "assets_total": float, ... }
    """
    try:
        results = await document_service.process_document(file)
        return {"status": "SUCCESS", "data": results}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
