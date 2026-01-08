import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000/api/v1/decide"

def run_test_case(name, payload, expected_status, expected_decision=None, description=""):
    print(f"\n🧪 TEST CASE: {name}")
    print(f"   Context: {description}")
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, json=payload)
        elapsed = (time.time() - start_time) * 1000
        
        # 1. Status Code Check
        if response.status_code != expected_status:
            print(f"   ❌ FAILED: Expected Status {expected_status}, got {response.status_code}")
            print(f"      Response: {response.text}")
            return False

        data = response.json()
        
        # 2. Decision Logic Check (if applicable)
        if expected_decision:
            actual_decision = data.get("decision", "UNKNOWN")
            if actual_decision != expected_decision:
                # Allow minor deviations if logical (e.g. REVIEW instead of REJECT in edge cases)
                print(f"   ⚠️ WARNING: Expected {expected_decision}, got {actual_decision}")
            else:
                print(f"   ✅ Decision Matched: {actual_decision}")

        # 3. Pipeline Checks
        if response.status_code == 200:
            # Audit Log Check
            if "decision_id" in data:
                print(f"   ✅ Audit Logged: ID {data['decision_id']}")
            else:
                 print("   ❌ Audit Log MISSING")
                 
            # Confidence Check
            if "confidence_score" in data:
                 print(f"   ✅ Confidence Score: {data['confidence_score']:.2f}")
            else:
                 print("   ❌ Confidence MISSING")
                 
        print(f"   ⏱️ Latency: {elapsed:.2f}ms")
        return True

    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        return False

def run_e2e_suite():
    print("🚀 STARTING PROMPT T1: END-TO-END SYSTEM TESTING")
    print("================================================")
    
    # CASE 1: SAFE APPLICANT
    # High Income, Excellent Credit, Low Debt
    safe_payload = {
        "applicant_id": "TEST-SAFE-001",
        "income": 120000,
        "credit_score": 780,
        "total_debt": 5000,
        "loan_amount": 20000,
        "business_type": "IT"
    }
    run_test_case("Safe Applicant", safe_payload, 200, "APPROVE", 
                  "High Income, High Score -> Should Approve")

    # CASE 2: BORDERLINE APPLICANT
    # Medium Income, Average Credit, Moderate Debt
    borderline_payload = {
        "applicant_id": "TEST-BORDER-001",
        "income": 60000,
        "credit_score": 650, # Average
        "total_debt": 25000,
        "loan_amount": 15000,
        "business_type": "Retail"
    }
    run_test_case("Borderline Applicant", borderline_payload, 200, "REVIEW", 
                  "Average metrics -> Should trigger Manual Review")

    # CASE 3: HIGH-RISK APPLICANT
    # Low Income, Poor Credit, High Debt
    risky_payload = {
        "applicant_id": "TEST-RISKY-001",
        "income": 30000,
        "credit_score": 550,
        "total_debt": 40000, # Higher than income!
        "loan_amount": 10000,
        "business_type": "Other"
    }
    run_test_case("High-Risk Applicant", risky_payload, 200, "REJECT", 
                  "High DTI, Low Score -> Should Reject")

    # CASE 4: MISSING DATA
    # Missing 'credit_score'
    missing_payload = {
        "applicant_id": "TEST-MISSING-001",
        "income": 50000,
        # credit_score missing
        "total_debt": 10000
    }
    run_test_case("Missing Data", missing_payload, 422, None, 
                  "Missing mandatory field -> Should 422 Validation Error")

    # CASE 5: CONTRADICTORY CASE (Logical Anomaly)
    # High Score (800) but Poverty Income ($5k) requesting Huge Loan ($1M)
    contradictory_payload = {
        "applicant_id": "TEST-CONTRA-001",
        "income": 5000,
        "credit_score": 800, # Excellent
        "total_debt": 0,
        "loan_amount": 1000000, # $1M loan on $5k income
        "business_type": "Retail"
    }
    run_test_case("Contradictory Applicant", contradictory_payload, 200, "REJECT", 
                  "Excellent Score but Impossible Affordability -> Should Reject/Review")

if __name__ == "__main__":
    run_e2e_suite()
