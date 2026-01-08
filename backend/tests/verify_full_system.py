import requests
import unittest
import uuid
from app.core.security import create_access_token

BASE_URL = "http://127.0.0.1:8000"

class TestFullSystem(unittest.TestCase):
    def setUp(self):
        # We need a running server. 
        # For this script to work, the user needs to launch 'uvicorn backend.app.main:app'
        # Since I can't easily launch and keep background process in this environment 
        # (run_command allows background but connection might be flaky in test runner),
        # I will use 'TestClient' which simulates the app in-process.
        from fastapi.testclient import TestClient
        from app.main import app
        self.client = TestClient(app)
        
    def test_e2e_flow(self):
        import traceback
        try:
            print("\n--- STARTING E2E VERIFICATION ---")
            
            # 1. AUTHENTICATION (Get Token)
            print("[1] Testing Authentication...")
            login_data = {"username": "underwriter_1", "password": "secret"}
            response = self.client.post("/api/v1/token", data=login_data)
            assert response.status_code == 200, f"Login failed: {response.text}"
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("    -> Token received.")
            
            # 2. DOCUMENT INGESTION
            print("[2] Testing Document Upload...")
            csv_content = "Date,Description,Amount,Balance\n01/01/2026,Salary,5000.00,5000.00\n01/15/2026,Rent,-1500.00,3500.00"
            files = {'file': ('bank_stmt.csv', csv_content, 'text/csv')}
            response = self.client.post("/api/v1/documents/upload", files=files)
            assert response.status_code == 200, f"Upload failed: {response.text}"
            doc_data = response.json()["data"]
            verified_income = doc_data["doc_verified_income"]
            print(f"    -> Extracted Income: ${verified_income}")
            
            # 3. DECISION (AI Inference + XAI)
            print("[3] Testing Decision Engine...")
            app_id = f"TEST_USER_{uuid.uuid4().hex[:8]}"
            payload = {
                "applicant_id": app_id,
                "age": 30,
                "annual_income": 60000, # Reported
                "total_debt": 20000,
                "credit_score": 650, # Marginal
                "business_type": "Retail",
                "monthly_debt_obligations": 1500,
                "doc_verified_income": verified_income, # Use extracted
                "assets_total": 5000
            }
            response = self.client.post("/api/v1/decide", json=payload)
            assert response.status_code == 200, f"Decision failed: {response.text}"
            decision = response.json()
            print(f"    -> AI Decision: {decision['tier']} (Score: {decision['risk_score']:.3f})")
            print(f"    -> Reason Codes: {decision.get('reason_flag')}") 
            
            # 4. OVERRIDE (Security)
            print("[4] Testing Manual Override...")
            from app.db.session import SessionLocal
            from app.db.models import Decision
            db = SessionLocal()
            # Find the ID
            db_decision = db.query(Decision).join(Decision.application).filter(Decision.application.has(applicant_id=app_id)).first()
            if not db_decision:
                 # Debug: list all decisions
                 print("DEBUG: Decisions in DB:")
                 for d in db.query(Decision).all():
                     print(f" - {d.id} for {d.application_id}")
                 raise Exception("Decision not found in DB for applicant " + app_id)

            override_payload = {
                "decision_id": db_decision.id,
                "new_tier": "Approve",
                "justification": "Underwriter manual review: Strong cashflow despite low score."
            }
            
            response = self.client.post("/api/v1/override", json=override_payload, headers=headers)
            assert response.status_code == 200, f"Override failed: {response.text}"
            print("    -> Override Successful.")
            
            # 5. AUDIT VERIFICATION
            from app.db.models import ManualReview
            review = db.query(ManualReview).filter(ManualReview.decision_id == db_decision.id).first()
            assert review is not None
            assert review.reviewer_id == "underwriter_1"
            print("    -> Audit Trail Verified.")
            db.close()
            
            print("\n--- E2E VERIFICATION PASSED ---")
        except Exception:
            traceback.print_exc()
            self.fail("E2E Test Failed")

if __name__ == "__main__":
    unittest.main()
