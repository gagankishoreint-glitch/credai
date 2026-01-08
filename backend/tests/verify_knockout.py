import httpx
import json

def test_knockout():
    url = "http://localhost:8000/api/v1/decide"
    payload = {
        "applicant_id": "TEST_KNOCKOUT_001",
        "age": 35,
        "credit_score": 500, # SHOULD FAIL
        "annual_income": 50000,
        "total_debt": 10000,
        "monthly_debt_obligations": 500,
        "business_type": "Retail"
    }
    
    try:
        response = httpx.post(url, json=payload)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Tier: {data.get('tier')}")
        print(f"Status: {data.get('status')}")
        print(f"Error Message: {data.get('error_message')}")
        
        if data.get('status') == "REJECTED_SAFETY" and "Knockout" in str(data.get('error_message')):
            print("SUCCESS: Low credit score was knocked out.")
        else:
            print("FAILURE: Did not receive expected knockout response.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_knockout()
