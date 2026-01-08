from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.document_service import document_service
from typing import Optional
import uuid

router = APIRouter()

@router.post("/upload_document")
async def upload_document(
    file: UploadFile = File(...),
    applicant_id: Optional[str] = Form(None),
    document_type: str = Form("bank_statement")
):
    """
    Upload and analyze financial document (PDF/Image).
    Extracts features via OCR + NLP.
    """
    
    # Validate file type
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_FILE_TYPE",
                "message": "Only PDF, PNG, and JPEG files are supported",
                "accepted_types": ["application/pdf", "image/png", "image/jpeg"]
            }
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size (max 10MB)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail={
                "error": "FILE_TOO_LARGE",
                "message": "File size exceeds 10MB limit",
                "max_size_mb": 10,
                "provided_size_mb": round(len(content) / (1024 * 1024), 2)
            }
        )
    
    # Generate document ID
    doc_id = f"DOC-{uuid.uuid4().hex[:8]}"
    
    # Extract features (with mock data for now since pytesseract might not be installed)
    try:
        extraction_result = document_service.extract_from_pdf(content, declared_data={})
        
        if extraction_result.get("status") == "EXTRACTION_FAILED":
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "EXTRACTION_FAILED",
                    "message": extraction_result.get("error", "Could not extract readable text"),
                    "suggestion": "Please upload a clearer scan or digital statement",
                    "extraction_confidence": extraction_result.get("extraction_confidence", 0.0)
                }
            )
        
        return {
            "document_id": doc_id,
            "applicant_id": applicant_id or "UNKNOWN",
            "status": "PROCESSED",
            "extracted_data": {
                "doc_verified_income": extraction_result.get("doc_verified_income", 0),
                "doc_extracted_debts": extraction_result.get("doc_extracted_debts", 0),
                "extraction_confidence": extraction_result.get("extraction_confidence", 0),
                "pages_processed": extraction_result.get("pages_processed", 1)
            },
            "verification": extraction_result.get("verification_flags", {}),
            "raw_text_sample": extraction_result.get("raw_text_sample", "")
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PROCESSING_ERROR",
                "message": str(e)
            }
        )
