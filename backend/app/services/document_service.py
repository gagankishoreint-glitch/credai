import re
import io
import statistics
from typing import Dict, Any, Tuple
from fastapi import UploadFile, HTTPException

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

class DocumentService:
    def __init__(self):
        self.MAX_SIZE_MB = 10
        
    async def process_document(self, file: UploadFile) -> Dict[str, Any]:
        """
        Ingest document, validate, extract text, and parse financial metrics.
        Returns dictionary of extracted features.
        """
        # 1. Validation
        if file.content_type not in ["application/pdf", "text/csv"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF or CSV allowed.")
            
        content = await file.read()
        if len(content) > self.MAX_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (>10MB).")
            
        # 2. Extraction
        text = ""
        try:
            if file.content_type == "application/pdf":
                if PdfReader:
                    pdf = PdfReader(io.BytesIO(content))
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                else:
                    return {"error": "PDF Processor unavailable"}
            else:
                # CSV simple decode
                text = content.decode("utf-8")
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Parsing Failed: {str(e)}")
             
        # 3. Financial Parsing (Regex Heuristics)
        # Check if empty (Scanned PDF)
        if len(text.strip()) < 50:
            return {
                "flag": "MANUAL_REVIEW_REQUIRED",
                "reason": "Document appears to be a scanned image or empty."
            }
            
        metrics = self._extract_financials(text)
        return metrics

    def _extract_financials(self, text: str) -> Dict[str, float]:
        """
        Naive Regex Extraction for MVP.
        Searches for lines like "Ending Balance... $5,000.00"
        """
        data = {
            "doc_verified_income": 0.0,
            "doc_derived_cashflow": 0.0,
            "assets_total": 0.0
        }
        
        # Normalize text
        lines = text.split('\n')
        
        deposits = []
        withdrawals = []
        balances = []
        salaries = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Simple Money Match: $1,234.56 or 1234.56
            # Regex captures the last number in the line usually
            matches = re.findall(r'\$?([\d,]+\.\d{2})', line)
            if not matches:
                continue
                
            val = float(matches[-1].replace(',', ''))
            
            if "ending balance" in line_lower:
                balances.append(val)
            elif "deposit" in line_lower or "credit" in line_lower:
                deposits.append(val)
            elif "withdrawal" in line_lower or "debit" in line_lower:
                withdrawals.append(val)
            elif "salary" in line_lower or "payroll" in line_lower:
                salaries.append(val)
                
        # Aggregation Logic
        if balances:
            # Optimistic: Take the max ending balance found (most recent?)
            data["assets_total"] = max(balances)
            
        if salaries:
            # Annualize the detected salary payments (Assuming monthly if count < 12, else sum)
            # Heuristic: If we found < 6 salary checks, assume monthly average * 12
            avg_salary = statistics.mean(salaries)
            data["doc_verified_income"] = avg_salary * 12
        elif deposits:
             # Fallback: Sum of all deposits as income proxy? (Variable)
             # Let's verify sum
             total_dep = sum(deposits)
             # If just one month statement, multiply by 12?
             # Let's assume the doc is ONE MONTH STATEMENT for this MVP.
             data["doc_verified_income"] = total_dep * 12
             
        if deposits and withdrawals:
             net_flow = sum(deposits) - sum(withdrawals)
             data["doc_derived_cashflow"] = net_flow # Monthly Net
             
        return data

document_service = DocumentService()
